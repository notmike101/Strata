"""Process adapter checks with actual small child processes, no GPU or downloads."""
import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock

from serve.model_runtimes import BackendError, ChatRuntime, EmbeddingRuntime, ImageRuntime


class Workers(unittest.TestCase):
    def test_chat_response_closes_upstream_even_when_retained(self):
        eof = threading.Event()
        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.end_headers()
                self.wfile.write(b'data: hello\n\n')
                self.wfile.flush()
                self.connection.settimeout(2)
                try:
                    if self.connection.recv(1) == b'':
                        eof.set()
                except OSError:
                    pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        runtime = ChatRuntime([], '.', 'http://127.0.0.1:' + str(server.server_address[1]))
        with runtime.response('/v1/chat/completions', {'stream': True}, {}) as retained:
            self.assertIn(b'hello', next(iter(retained.chunks)))
        self.assertTrue(eof.wait(.5), 'upstream socket remained open after context exit')

    def test_dead_chat_child_is_not_resident(self):
        runtime = ChatRuntime([sys.executable], '.', 'http://127.0.0.1:8082')
        runtime.resident = True
        runtime.proc = type('ExitedProcess', (), {'poll': lambda self: 1})()
        self.assertFalse(runtime.resident)

    def worker(self, source, timeout=2):
        runtime = EmbeddingRuntime([sys.executable, '-u', '-c', source], timeout=timeout)
        self.addCleanup(runtime.close)
        return runtime

    def test_embedding_protocol_and_exit_release(self):
        runtime = self.worker("import sys,json; print('{\"status\":\"ready\"}',flush=True); "
                              "\nfor line in sys.stdin: print(json.dumps({'data':json.loads(line)['input']}),flush=True)")
        runtime.load()
        proc = runtime.proc
        with runtime.response('/v1/embeddings', {'input': 'hello'}, {}) as reply:
            self.assertEqual(json.loads(b''.join(reply.chunks)), {'data': 'hello'})
        runtime.unload()
        self.assertIsNotNone(proc.poll())
        self.assertFalse(runtime.resident)
        self.assertIsNone(runtime.proc)

    def test_timeout_stops_worker_so_stale_replies_cannot_be_reused(self):
        runtime = self.worker("import sys,time; print('{\"status\":\"ready\"}',flush=True); "
                              "\nfor line in sys.stdin: time.sleep(1); print('{\"data\":[]}',flush=True)", timeout=.2)
        runtime.load()
        proc = runtime.proc
        with self.assertRaises(BackendError):
            with runtime.response('/v1/embeddings', {'input': 'hello'}, {}):
                pass
        self.assertFalse(runtime.resident)
        self.assertIsNotNone(proc.poll())

    def test_dead_worker_marks_itself_unloaded_for_retry(self):
        runtime = self.worker("import sys; print('{\"status\":\"ready\"}',flush=True); sys.stdin.readline()")
        runtime.load()
        with self.assertRaises(BackendError):
            with runtime.response('/v1/embeddings', {'input': 'x'}, {}):
                pass
        self.assertFalse(runtime.resident)

    def test_worker_error_preserves_http_status(self):
        runtime = self.worker("import sys; print('{\"status\":\"ready\"}',flush=True); "
                              "\nfor line in sys.stdin: print('{\"error\":\"too many tokens\",\"status\":400}',flush=True)")
        runtime.load()
        with self.assertRaises(BackendError) as error:
            with runtime.response('/v1/embeddings', {'input': 'x'}, {}):
                pass
        self.assertEqual(error.exception.status, 400)

    def test_image_result_and_process_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'weights'
            file.write_bytes(b'fake')
            runtime = ImageRuntime(sys.executable, file, file, file)
            runtime.command = lambda payload, output: [sys.executable, '-c',
                "from pathlib import Path; import sys; Path(sys.argv[1]).write_bytes(b'PNG-result')", str(output)]
            runtime.load()
            with runtime.response('/v1/images/generations', {'prompt': 'x'}, {}) as reply:
                result = json.loads(b''.join(reply.chunks))
            self.assertEqual(base64.b64decode(result['data'][0]['b64_json']), b'PNG-result')
            self.assertIsNone(runtime.proc)
            self.assertFalse(runtime.resident)

    def test_image_prompt_is_one_argument(self):
        runtime = ImageRuntime('sd-cli', 'model', 'vae', 'encoder')
        prompt = 'a drawing; $(whoami) & echo test'
        command = runtime.command({'prompt': prompt}, 'output.png')
        self.assertEqual(command[command.index('-p') + 1], prompt)
        self.assertIn('--diffusion-fa', command)

    def test_image_library_path_is_scoped_to_child(self):
        import os
        original_path = os.environ.get('PATH', '')
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'weights'
            file.write_bytes(b'fake')
            runtime = ImageRuntime(sys.executable, file, file, file, lib_dirs=[folder])
            runtime.command = lambda payload, output: [sys.executable, '-c',
                "import os,sys; from pathlib import Path; Path(sys.argv[1]).write_text(os.environ['PATH'])", str(output)]
            with runtime.response('/v1/images/generations', {'prompt': 'x'}, {}) as reply:
                result = json.loads(b''.join(reply.chunks))
            child_path = base64.b64decode(result['data'][0]['b64_json']).decode()
            self.assertTrue(child_path.startswith(folder + os.pathsep))
            self.assertEqual(os.environ.get('PATH', ''), original_path)


if __name__ == '__main__':
    unittest.main()
