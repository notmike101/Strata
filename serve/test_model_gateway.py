"""Gateway HTTP integration tests using real sockets and CPU-only fake runtimes."""
from contextlib import contextmanager
import json
import re
import threading
import time
import unittest
import urllib.error
import urllib.request

from serve.runtime_manager import RuntimeManager
try:
    from serve.model_gateway import Gateway, serve_gateway
    from serve.model_runtimes import BackendResponse, validate_embedding, validate_image
except ImportError:
    Gateway = serve_gateway = BackendResponse = validate_embedding = validate_image = None


class FakeRuntime:
    def __init__(self, kind, events):
        self.kind, self.events = kind, events
        self.resident = False
        self.stream_started = threading.Event()
        self.finish_stream = threading.Event()

    def load(self):
        self.events.append(('load', self.kind))
        self.resident = True

    def unload(self):
        self.events.append(('unload', self.kind))
        self.resident = False

    close = unload

    def validate(self, payload, path=None):
        if self.kind == 'chat':
            from serve.model_runtimes import validate_chat
            validate_chat(payload, path)
        if self.kind == 'embedding':
            validate_embedding(payload)
        if self.kind == 'image':
            validate_image(payload)

    @contextmanager
    def response(self, path, payload, headers):
        if payload.get('stream'):
            def chunks():
                self.stream_started.set()
                yield b'data: {"token":"hello"}\n\n'
                self.finish_stream.wait(5)
                yield b'data: [DONE]\n\n'
            yield BackendResponse(200, {'Content-Type': 'text/event-stream'}, chunks())
        else:
            data = {'object': 'list', 'model': payload['model'], 'data': [{'embedding': [1., 0.]}]}
            yield BackendResponse(200, {'Content-Type': 'application/json'}, [json.dumps(data).encode()])


class GatewayHTTP(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Gateway, 'model gateway is not implemented')
        self.events = []
        self.runtimes = {name: FakeRuntime(kind, self.events) for name, kind in
                         [('chat', 'chat'), ('embed', 'embedding'), ('image', 'image')]}
        self.manager = RuntimeManager(self.runtimes)
        self.gateway = Gateway(self.manager, default_model='chat', api_key='test-key')
        self.server = serve_gateway(self.gateway, host='127.0.0.1', port=0)
        self.base = 'http://127.0.0.1:' + str(self.server.server_address[1])

    def tearDown(self):
        if hasattr(self, 'server'):
            self.runtimes['chat'].finish_stream.set()
            self.server.shutdown()
            self.server.server_close()
            self.manager.close()

    def request(self, path, payload=None, key='test-key'):
        headers = {'Content-Type': 'application/json'}
        if key:
            headers['Authorization'] = 'Bearer ' + key
        request = urllib.request.Request(self.base + path,
                                         data=json.dumps(payload).encode() if payload is not None else None,
                                         headers=headers)
        try:
            response = urllib.request.urlopen(request, timeout=10)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.status, json.loads(response.read())

    def test_keyless_gateway_rejects_foreign_host_before_loading(self):
        import http.client
        self.gateway.api_key = ''
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_address[1], timeout=10)
        try:
            conn.request('POST', '/v1/load', body=json.dumps({'model': 'chat'}),
                         headers={'Host': 'attacker.example', 'Origin': 'http://attacker.example',
                                  'Content-Type': 'application/json'})
            response = conn.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            self.assertEqual(self.events, [])
        finally:
            conn.close()
        self.assertEqual(self.request('/v1/load', {'model': 'chat'}, key=None)[0], 200)

    def test_auth_before_loading_and_model_listing_without_loading(self):
        self.assertEqual(self.request('/v1/embeddings', {'model': 'embed', 'input': 'x'}, key=None)[0], 401)
        status, result = self.request('/v1/models')
        self.assertEqual(status, 200)
        self.assertEqual({item['id'] for item in result['data']}, set(self.runtimes))
        self.assertEqual(self.events, [])

    def test_embeddings_switch_away_from_chat(self):
        self.assertEqual(self.request('/v1/chat/completions', {'model': 'chat', 'messages': []})[0], 200)
        status, result = self.request('/v1/embeddings', {'model': 'embed', 'input': ['a', 'b']})
        self.assertEqual(status, 200)
        self.assertEqual(result['model'], 'embed')
        self.assertEqual(self.events, [('load', 'chat'), ('unload', 'chat'), ('load', 'embedding')])

    def test_bad_input_and_wrong_model_kind_do_not_evict_chat(self):
        self.request('/v1/load', {'model': 'chat'})
        before = list(self.events)
        for payload, expected in [({'model': 'embed', 'input': []}, 400),
                                  ({'model': 'chat', 'input': 'a'}, 400),
                                  ({'model': 'unknown', 'input': 'a'}, 404),
                                  ({'model': 'embed', 'input': [123]}, 400)]:
            self.assertEqual(self.request('/v1/embeddings', payload)[0], expected)
        self.assertEqual(self.events, before)

    def test_array_root_and_missing_input_are_rejected(self):
        self.assertEqual(self.request('/v1/embeddings', ['bad'])[0], 400)
        self.assertEqual(self.request('/v1/embeddings', {'model': 'embed'})[0], 400)
        self.assertEqual(self.events, [])

    def test_controls_and_status(self):
        self.assertEqual(self.request('/v1/load', {'model': 'embed'})[0], 200)
        self.assertEqual(self.request('/v1/status')[1]['active_model'], 'embed')
        self.assertEqual(self.request('/v1/unload', {})[0], 200)
        self.assertIsNone(self.request('/v1/status')[1]['active_model'])

    def test_stream_retains_gpu_until_done(self):
        body = json.dumps({'model': 'chat', 'messages': [], 'stream': True}).encode()
        req = urllib.request.Request(self.base + '/v1/chat/completions', data=body,
                                     headers={'Authorization': 'Bearer test-key', 'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=10)
        self.assertEqual(response.readline(), b'data: {"token":"hello"}\n')
        done = []
        thread = threading.Thread(target=lambda: done.append(self.request('/v1/embeddings',
                                      {'model': 'embed', 'input': 'x'})[0]))
        thread.start()
        deadline = time.monotonic() + 2
        while not self.manager.status()['queued']:
            self.assertLess(time.monotonic(), deadline)
            time.sleep(.005)
        self.assertEqual(self.events, [('load', 'chat')])
        self.runtimes['chat'].finish_stream.set()
        self.assertIn(b'[DONE]', response.read())
        response.close()
        thread.join(3)
        self.assertEqual(done, [200])

    def test_external_binding_requires_key(self):
        gateway = Gateway(self.manager, 'chat', api_key='')
        with self.assertRaisesRegex(ValueError, 'API key'):
            serve_gateway(gateway, host='0.0.0.0', port=0)

    def test_web_page_can_open_before_entering_key_without_loading_a_model(self):
        with urllib.request.urlopen(self.base + '/', timeout=5) as reply:
            self.assertEqual(reply.status, 200)
            self.assertIn(b'id="api-key"', reply.read())
        self.assertEqual(self.events, [])

    def test_web_assets_use_the_paths_in_the_unchanged_page(self):
        with urllib.request.urlopen(self.base + '/', timeout=5) as reply:
            html = reply.read().decode()
        paths = re.findall(r'(?:src|href)="(/?web/[^"?#]+)', html)
        self.assertTrue(paths)
        for path in paths:
            with urllib.request.urlopen(self.base + '/' + path.lstrip('/'), timeout=5) as reply:
                self.assertEqual(reply.status, 200)
                self.assertGreater(len(reply.read()), 0)
        self.assertEqual(self.events, [])

    def test_nonfinite_json_is_rejected_before_loading(self):
        status, _ = self.request('/v1/chat/completions', {'model': 'chat', 'temperature': float('nan')})
        self.assertEqual(status, 400)
        self.assertEqual(self.events, [])

    def test_malformed_chat_does_not_evict_embedding(self):
        self.request('/v1/load', {'model': 'embed'})
        before = list(self.events)
        for path, body in [('/v1/chat/completions', {'messages': 'bad'}),
                           ('/v1/chat/completions', {'messages': [], 'temperature': 'bad'}),
                           ('/v1/messages', {'messages': [123]}),
                           ('/v1/responses', {'input': 123})]:
            self.assertEqual(self.request(path, {'model': 'chat', **body})[0], 400)
        self.assertEqual(self.events, before)

    def test_partial_metadata_failure_does_not_append_second_response(self):
        runtime = self.runtimes['chat']
        runtime.ensure_server = lambda: None
        @contextmanager
        def broken_response(*args):
            def chunks():
                yield b'partial body'
                raise OSError('upstream disconnected')
            yield BackendResponse(200, {'Content-Type': 'text/plain'}, chunks())
        runtime.response = broken_response
        req = urllib.request.Request(self.base + '/props', headers={'Authorization': 'Bearer test-key'})
        with urllib.request.urlopen(req, timeout=5) as reply:
            body = reply.read()
        self.assertEqual(body, b'partial body')


class Inputs(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(validate_embedding, 'input validators are not implemented')

    def test_embedding_dimensions_and_encoding(self):
        validate_embedding({'input': 'x', 'dimensions': 32, 'encoding_format': 'base64'})
        for extra in ({'dimensions': True}, {'dimensions': 0}, {'dimensions': 2561},
                      {'encoding_format': 'url'}, {'input': [1]}, {'input': []}):
            with self.assertRaises(ValueError):
                validate_embedding({'input': 'x', **extra})

    def test_image_limits_and_shell_text_is_only_a_prompt(self):
        validate_image({'prompt': 'a drawing; $(echo test)', 'size': '1024x1024'})
        for extra in ({'n': 2}, {'size': '99999x99999'}, {'size': '257x256'},
                      {'steps': 0}, {'steps': True}, {'response_format': 'url'},
                      {'prompt': ''}, {'seed': True}):
            with self.assertRaises(ValueError):
                validate_image({'prompt': 'x', **extra})


if __name__ == '__main__':
    unittest.main()
