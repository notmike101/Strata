"""Adapters used only by the opt-in gateway; no GPU libraries imported here."""
from __future__ import annotations

import base64
from contextlib import contextmanager
from dataclasses import dataclass
import http.client
import json
import math
import os
from pathlib import Path
import queue
import re
import subprocess
import tempfile
import threading
import time
from urllib.parse import urlsplit

from serve.winjob import contain


class BackendError(RuntimeError):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status


@dataclass
class BackendResponse:
    status: int
    headers: dict
    chunks: object


def validate_embedding(payload):
    inputs = payload.get('input')
    if isinstance(inputs, str):
        inputs = [inputs]
    if (not isinstance(inputs, list) or not 1 <= len(inputs) <= 32
            or any(not isinstance(item, str) or not item.strip() for item in inputs)):
        raise ValueError('input must be a nonempty string or a list of 1 to 32 nonempty strings')
    dimensions = payload.get('dimensions', 2560)
    if type(dimensions) is not int or not 32 <= dimensions <= 2560:
        raise ValueError('dimensions must be an integer between 32 and 2560')
    if payload.get('encoding_format', 'float') not in ('float', 'base64'):
        raise ValueError('encoding_format must be float or base64')
    if 'instruction' in payload and not isinstance(payload['instruction'], str):
        raise ValueError('instruction must be a string')


def validate_chat(payload, path=None):
    if 'stream' in payload and not isinstance(payload['stream'], bool):
        raise ValueError('stream must be a boolean')
    for key in ('temperature', 'top_p', 'min_p', 'presence_penalty', 'frequency_penalty',
                'repetition_penalty'):
        if key in payload and payload[key] is not None and (type(payload[key]) not in (int, float) or not math.isfinite(payload[key])):
            raise ValueError(f'{key} must be a finite number')
    for key in ('top_k', 'max_tokens', 'max_completion_tokens', 'max_output_tokens'):
        if key in payload and payload[key] is not None and type(payload[key]) is not int:
            raise ValueError(f'{key} must be an integer')
    # Reuse the server's pure schema conversion so supported tools/content stay compatible.
    from serve.frontend import anthropic_to_messages, openai_to_messages
    if path == '/v1/chat/completions':
        openai_to_messages(payload)
    elif path in ('/v1/messages', '/v1/messages/count_tokens'):
        anthropic_to_messages(payload)
    elif path == '/v1/responses':
        from serve.responses import input_messages, request_tools
        try:
            input_messages(payload)
            request_tools(payload)
        except Exception as exc:
            raise ValueError(str(exc)) from exc


def validate_image(payload):
    if not isinstance(payload.get('prompt'), str) or not payload['prompt'].strip():
        raise ValueError('prompt must be a nonempty string')
    if len(payload['prompt']) > 16000:
        raise ValueError('prompt must be at most 16000 characters')
    if type(payload.get('n', 1)) is not int or payload.get('n', 1) != 1:
        raise ValueError('this image runtime supports n=1')
    size = payload.get('size', '1024x1024')
    match = re.fullmatch(r'(\d{3,4})x(\d{3,4})', size) if isinstance(size, str) else None
    if not match:
        raise ValueError('size must be WIDTHxHEIGHT')
    width, height = map(int, match.groups())
    if (not 256 <= width <= 2048 or not 256 <= height <= 2048
            or width % 64 or height % 64 or width * height > 1024 * 1024):
        raise ValueError('size must use multiples of 64, dimensions 256..2048, at most 1048576 pixels')
    if payload.get('response_format', 'b64_json') != 'b64_json':
        raise ValueError('this image runtime supports response_format=b64_json')
    steps = payload.get('steps', 20)
    if type(steps) is not int or not 1 <= steps <= 100:
        raise ValueError('steps must be an integer between 1 and 100')
    cfg = payload.get('cfg_scale', 6.0)
    if type(cfg) not in (int, float) or not math.isfinite(cfg) or not 0 <= cfg <= 20:
        raise ValueError('cfg_scale must be a finite number between 0 and 20')
    seed = payload.get('seed', -1)
    if type(seed) is not int or not -1 <= seed <= 2147483647:
        raise ValueError('seed must be an integer between -1 and 2147483647')
    if not isinstance(payload.get('negative_prompt', ''), str):
        raise ValueError('negative_prompt must be a string')


def stop_process(proc, timeout=30):
    """Wait for exit before returning. Leave the owner's handle intact on failure."""
    if proc is None:
        return
    if proc.poll() is None:
        if proc.stdin is not None:
            try:
                proc.stdin.close()
                proc.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                pass
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=timeout)
    else:
        proc.wait()
    if proc.stdin is not None and not proc.stdin.closed:
        proc.stdin.close()


class ChatRuntime:
    kind = 'chat'

    def __init__(self, command, cwd, base_url, api_key='', env=None, log=None, timeout=600):
        parsed = urlsplit(base_url)
        if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', '::1', 'localhost'):
            raise ValueError('managed chat backend must use loopback HTTP')
        self.command, self.cwd, self.base_url = list(command), cwd, parsed
        self.api_key, self.env, self.timeout = api_key, env or {}, timeout
        self.log = Path(log) if log else None
        self.proc, self.log_file = None, None
        self.resident = False
        self._server_lock = threading.RLock()

    validate = staticmethod(validate_chat)

    @property
    def resident(self):
        return self._resident and self.proc is not None and self.proc.poll() is None

    @resident.setter
    def resident(self, value):
        self._resident = value

    def ensure_server(self):
        with self._server_lock:
            self._ensure_server()

    def _ensure_server(self):
        if self.proc is not None and self.proc.poll() is None:
            return
        if self.proc is not None:
            self.close()
        # Never adopt a server started by somebody else on the private port.
        import socket
        with socket.socket() as probe:
            probe.bind((self.base_url.hostname, self.base_url.port))
        if self.log:
            self.log.parent.mkdir(parents=True, exist_ok=True)
            self.log_file = self.log.open('ab')
        env = {**os.environ, **self.env}
        if self.api_key:
            env['STRATA_API_KEY'] = self.api_key
        self.proc = subprocess.Popen(self.command, cwd=self.cwd, env=env, stdin=subprocess.DEVNULL,
                                     stdout=self.log_file or subprocess.DEVNULL,
                                     stderr=subprocess.STDOUT)
        contain(self.proc)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise BackendError('Strata API failed to start; inspect its local runtime log')
            try:
                with self.response('/health', None, {}) as reply:
                    data = b''.join(reply.chunks)
                    if reply.status == 200 and json.loads(data).get('service') == 'strata':
                        return
            except (OSError, http.client.HTTPException, ValueError):
                pass
            time.sleep(.1)
        raise BackendError('Strata API startup timed out')

    def _control(self, path):
        with self.response(path, {}, {}) as reply:
            result = json.loads(b''.join(reply.chunks))
            if reply.status != 200:
                raise BackendError('Strata model control failed; the backend may still be busy', reply.status)
            return result

    def load(self):
        self.ensure_server()
        result = self._control('/v1/load')
        if not result.get('loaded'):
            raise BackendError('Strata did not confirm the model loaded')
        self.resident = True

    def unload(self):
        if self.proc is not None and self.proc.poll() is None:
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    result = self._control('/v1/unload')
                    break
                except BackendError as exc:
                    if exc.status != 409 or time.monotonic() >= deadline:
                        raise
                    # A disconnected stream may still be cancelling on the private server.
                    time.sleep(.1)
            if result.get('status') not in ('unloaded', 'not loaded') or result.get('loaded'):
                raise BackendError('Strata has not finished unloading; another model will not start')
        self.resident = False

    def close(self):
        self.unload()
        stop_process(self.proc)
        self.proc = None
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    @contextmanager
    def response(self, path, payload, headers):
        conn = http.client.HTTPConnection(self.base_url.hostname, self.base_url.port, timeout=self.timeout)
        forwarded = {key: value for key, value in headers.items()
                     if key.lower() in ('anthropic-version', 'anthropic-beta')}
        if self.api_key:
            forwarded['Authorization'] = 'Bearer ' + self.api_key
        forwarded['Content-Type'] = 'application/json'
        body = json.dumps(payload).encode() if payload is not None else None
        reply = None
        try:
            conn.request('POST' if payload is not None else 'GET', path, body=body, headers=forwarded)
            reply = conn.getresponse()

            def chunks():
                while True:
                    chunk = reply.read1(65536)
                    if not chunk:
                        break
                    yield chunk

            yield BackendResponse(reply.status, dict(reply.getheaders()), chunks())
        finally:
            if reply is not None:
                reply.close()
            conn.close()


class EmbeddingRuntime:
    kind = 'embedding'
    validate = staticmethod(validate_embedding)

    def __init__(self, command, cwd=None, env=None, log=None, timeout=600):
        self.command, self.cwd, self.env = list(command), cwd, env or {}
        self.log, self.timeout = Path(log) if log else None, timeout
        self.proc, self.log_file, self.output = None, None, None
        self.resident = False

    def _receive(self):
        try:
            line = self.output.get(timeout=self.timeout)
        except queue.Empty:
            raise BackendError('embedding worker timed out', 504) from None
        if line is None:
            raise BackendError('embedding worker exited; inspect its local runtime log')
        result = json.loads(line)
        if 'error' in result:
            raise BackendError(result['error'], result.get('status', 500))
        return result

    def load(self):
        if self.proc is not None and self.proc.poll() is None and self.resident:
            return
        self.unload()
        if self.log:
            self.log.parent.mkdir(parents=True, exist_ok=True)
            self.log_file = self.log.open('ab')
        self.proc = subprocess.Popen(self.command, cwd=self.cwd, env={**os.environ, **self.env},
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=self.log_file or subprocess.DEVNULL,
                                     text=True, encoding='utf-8', bufsize=1)
        contain(self.proc)
        self.output = queue.Queue()
        proc, output = self.proc, self.output

        def pump():
            try:
                for line in proc.stdout:
                    output.put(line)
            finally:
                output.put(None)
                proc.stdout.close()

        threading.Thread(target=pump, daemon=True).start()
        if self._receive().get('status') != 'ready':
            raise BackendError('embedding worker did not report ready')
        self.resident = True

    def unload(self):
        stop_process(self.proc)
        self.proc = None
        self.resident = False
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    close = unload

    @contextmanager
    def response(self, path, payload, headers):
        if self.proc is None or self.proc.poll() is not None:
            self.unload()
            raise BackendError('embedding worker is not running; unload and retry')
        try:
            self.proc.stdin.write(json.dumps(payload) + '\n')
            self.proc.stdin.flush()
            result = self._receive()
        except BackendError as exc:
            if exc.status >= 500:
                self.unload()
            raise
        except (OSError, ValueError):
            self.unload()
            raise BackendError('embedding worker protocol failed; inspect its local log') from None
        yield BackendResponse(200, {'Content-Type': 'application/json'}, [json.dumps(result).encode()])


class ImageRuntime:
    kind = 'image'
    validate = staticmethod(validate_image)

    def __init__(self, exe, diffusion_model, vae, text_encoder, timeout=1800, extra_args=None, lib_dirs=None):
        self.exe, self.diffusion_model = Path(exe), Path(diffusion_model)
        self.vae, self.text_encoder = Path(vae), Path(text_encoder)
        self.timeout, self.extra_args = timeout, list(extra_args or [])
        self.lib_dirs = list(lib_dirs or [])
        self.proc = None
        self.resident = False

    def load(self):
        for path in (self.exe, self.diffusion_model, self.vae, self.text_encoder):
            if not path.is_file():
                raise BackendError(f'image runtime file is missing: {path.name}')

    def unload(self):
        stop_process(self.proc)
        self.proc = None
        self.resident = False

    close = unload

    def command(self, payload, output):
        width, height = payload.get('size', '1024x1024').split('x')
        return [str(self.exe), '--diffusion-model', str(self.diffusion_model), '--vae', str(self.vae),
                '--llm', str(self.text_encoder), '-p', payload['prompt'],
                '--negative-prompt', payload.get('negative_prompt', ''),
                '--steps', str(payload.get('steps', 20)), '--cfg-scale', str(payload.get('cfg_scale', 6.0)),
                '--sampling-method', 'euler', '--seed', str(payload.get('seed', -1)),
                '-W', width, '-H', height, '--diffusion-fa', '-o', str(output), *self.extra_args]

    @contextmanager
    def response(self, path, payload, headers):
        with tempfile.TemporaryDirectory(prefix='strata-image-') as folder:
            output = Path(folder) / 'image.png'
            log = Path(folder) / 'sd.log'
            try:
                with log.open('wb') as stream:
                    env = dict(os.environ)
                    if self.lib_dirs:
                        env['PATH'] = os.pathsep.join([*map(str, self.lib_dirs), env.get('PATH', '')])
                    self.proc = subprocess.Popen(self.command(payload, output), cwd=self.exe.parent,
                                                 stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                                                 env=env)
                    contain(self.proc)
                    self.resident = True
                    try:
                        code = self.proc.wait(timeout=self.timeout)
                    except subprocess.TimeoutExpired:
                        raise BackendError('image generation timed out', 504) from None
                if code:
                    tail = log.read_text(errors='replace')[-3000:]
                    # Write diagnostics locally, but never echo user prompts in API errors.
                    diagnostics = self.exe.parent / 'last-error.log'
                    diagnostics.write_text(tail, encoding='utf-8')
                    raise BackendError('image generation failed; inspect the image runtime last-error.log')
                if not output.is_file():
                    raise BackendError('image runtime exited without producing a PNG')
                result = {'created': int(time.time()), 'data': [
                    {'b64_json': base64.b64encode(output.read_bytes()).decode('ascii')}]}
            finally:
                self.unload()
            yield BackendResponse(200, {'Content-Type': 'application/json'}, [json.dumps(result).encode()])
