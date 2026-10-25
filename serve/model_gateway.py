"""Opt-in on-demand API: python -m serve.model_gateway --config model-gateway.local.json."""
from __future__ import annotations

import argparse
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import signal
import threading
from urllib.parse import urlsplit

from serve.model_runtimes import BackendError, ChatRuntime, EmbeddingRuntime, ImageRuntime
from serve.runtime_manager import RuntimeManager

CHAT_PATHS = {'/v1/chat/completions', '/v1/messages', '/v1/messages/count_tokens', '/v1/responses',
              '/v1/vram', '/settings', '/config'}
CONTROL_PATHS = {'/v1/load', '/v1/unload', '/load', '/unload'}
MAX_BODY = 16 * 1024 * 1024
WEB_ROOT = Path(__file__).resolve().parent / 'web'
WEB_FILES = {'/': 'index.html', **{'/web/' + name: name for name in
             ('app.js', 'app.css', 'components.css', 'tokens.css', 'sprite.svg')}}


def reject_nonfinite(value):
    raise ValueError('JSON must not contain NaN or Infinity')


class Gateway:
    def __init__(self, manager, default_model, api_key='', chat_health=None):
        if default_model not in manager.runtimes or manager.runtimes[default_model].kind != 'chat':
            raise ValueError('default_model must name a configured chat runtime')
        self.manager, self.default_model, self.api_key = manager, default_model, api_key
        self.chat_health = dict(chat_health or {})

    def select(self, path, payload):
        kind = ('embedding' if path == '/v1/embeddings' else
                'image' if path == '/v1/images/generations' else 'chat')
        model = payload.get('model', self.default_model)
        if not isinstance(model, str) or model not in self.manager.runtimes:
            raise BackendError('model not found; see /v1/models', 404)
        runtime = self.manager.runtimes[model]
        if path not in CONTROL_PATHS and runtime.kind != kind:
            raise ValueError(f'the requested endpoint requires a {kind} model')
        if path not in CONTROL_PATHS:
            if runtime.kind == 'chat':
                runtime.validate(payload, path)
            else:
                runtime.validate(payload)
        return model


def serve_gateway(gateway, host='127.0.0.1', port=8080):
    if host not in ('127.0.0.1', '::1', 'localhost') and not gateway.api_key:
        raise ValueError('an API key is required when binding outside loopback')

    from serve.server import LOOPBACK_NAMES, host_allowed

    class Handler(BaseHTTPRequestHandler):
        # Connection-close framing also handles streamed upstream responses without buffering.
        protocol_version = 'HTTP/1.0'

        def setup(self):
            super().setup()
            self.connection.settimeout(120)
            self.response_started = False

        def end_headers(self):
            self.response_started = True
            super().end_headers()

        def parse_request(self):
            if not super().parse_request():
                return False
            if gateway.api_key or host_allowed(self.headers.get('Host'), LOOPBACK_NAMES):
                return True
            self.json(403, {'error': {'message': 'Host is not allowed (DNS rebinding protection)'}})
            return False

        def log_message(self, format, *args):
            pass  # Do not log prompts, authorization, or URL query strings.

        def json(self, status, result):
            body = json.dumps(result, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            if not gateway.api_key:
                return True
            auth = self.headers.get('Authorization', '')
            supplied = auth[7:] if auth.startswith('Bearer ') else self.headers.get('x-api-key', '')
            if hmac.compare_digest(supplied.encode(), gateway.api_key.encode()):
                return True
            self.json(401, {'error': {'message': 'API key required', 'type': 'authentication_error'}})
            return False

        def relay(self, reply):
            self.send_response(reply.status)
            for key, value in reply.headers.items():
                if key.lower() not in ('transfer-encoding', 'connection', 'server', 'date'):
                    self.send_header(key, value)
            self.end_headers()
            for chunk in reply.chunks:
                self.wfile.write(chunk)
                self.wfile.flush()

        def do_GET(self):
            path = urlsplit(self.path).path
            if path in ('/health', '/api/health'):
                self.json(200, {'status': 'ok', 'service': 'strata-model-gateway',
                                **gateway.chat_health,
                                'api_key': bool(gateway.api_key), 'model': gateway.default_model})
                return
            if path in WEB_FILES:
                filename = WEB_FILES[path]
                body = (WEB_ROOT / filename).read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(filename)[0] or 'application/octet-stream')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if not self.authorized():
                return
            if path in ('/v1/models', '/models'):
                self.json(200, {'object': 'list', 'data': [
                    {'id': name, 'object': 'model', 'owned_by': 'local', 'type': runtime.kind}
                    for name, runtime in gateway.manager.runtimes.items()]})
            elif path in ('/v1/status', '/gateway/status'):
                result = gateway.manager.status()
                result['models'] = {name: {'type': runtime.kind, 'loaded': runtime.resident}
                                    for name, runtime in gateway.manager.runtimes.items()}
                self.json(200, result)
            else:
                runtime = gateway.manager.runtimes[gateway.default_model]
                try:
                    runtime.ensure_server()
                    with runtime.response(self.path, None, dict(self.headers)) as reply:
                        self.relay(reply)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                except Exception:
                    if not self.response_started:
                        self.json(502, {'error': {'message': 'chat metadata backend unavailable'}})
                    else:
                        self.close_connection = True

        def do_POST(self):
            if not self.authorized():
                return
            path = urlsplit(self.path).path
            if path not in CHAT_PATHS | CONTROL_PATHS | {'/v1/embeddings', '/v1/images/generations'}:
                self.json(404, {'error': {'message': 'endpoint not found'}})
                return
            if self.headers.get_content_type() != 'application/json':
                self.json(415, {'error': {'message': 'Content-Type must be application/json'}})
                return
            sent = False
            try:
                length = int(self.headers.get('Content-Length', '-1'))
                if not 0 <= length <= MAX_BODY or self.headers.get('Transfer-Encoding'):
                    raise ValueError('a Content-Length between 0 and 16777216 is required')
                payload = json.loads(self.rfile.read(length), parse_constant=reject_nonfinite)
                if not isinstance(payload, dict):
                    raise ValueError('request body must be a JSON object')
                model = gateway.select(path, payload)
                if path in ('/v1/unload', '/unload'):
                    gateway.manager.unload(payload.get('model'))
                    self.json(200, {'status': 'unloaded', **gateway.manager.status()})
                    return
                with gateway.manager.use(model) as runtime:
                    if path in ('/v1/load', '/load'):
                        self.json(200, {'status': 'loaded' if runtime.resident else 'ready',
                                        **gateway.manager.status()})
                        return
                    payload['model'] = model
                    with runtime.response(path, payload, dict(self.headers)) as reply:
                        sent = True
                        self.relay(reply)
            except (BrokenPipeError, ConnectionResetError):
                pass
            except (ValueError, TypeError) as exc:
                if not sent:
                    self.json(400, {'error': {'message': str(exc), 'type': 'invalid_request_error'}})
            except BackendError as exc:
                if not sent:
                    self.json(exc.status, {'error': {'message': str(exc), 'type': 'runtime_error'}})
            except Exception:
                if not sent:
                    self.json(502, {'error': {'message': 'runtime failed; inspect the local runtime log'}})

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def from_config(config):
    api_key = os.environ.get('STRATA_GATEWAY_API_KEY') or config.get('api_key', '')
    runtimes = {}
    for name, item in config['models'].items():
        common = {key: item[key] for key in ('command', 'cwd', 'env', 'log', 'timeout') if key in item}
        if item['type'] == 'chat':
            runtimes[name] = ChatRuntime(base_url=item['base_url'], api_key=api_key, **common)
        elif item['type'] == 'embedding':
            runtimes[name] = EmbeddingRuntime(**common)
        elif item['type'] == 'image':
            runtimes[name] = ImageRuntime(**{key: value for key, value in item.items() if key != 'type'})
        else:
            raise ValueError('unsupported runtime type')
    return Gateway(RuntimeManager(runtimes, idle_seconds=config.get('idle_unload_s', 600)),
                   config['default_model'], api_key=api_key, chat_health=config.get('chat_health'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    gateway = from_config(config)
    server = serve_gateway(gateway, config.get('host', '127.0.0.1'), config.get('port', 8080))
    stopping = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stopping.set())
    print(f"[gateway] listening on {config.get('host', '127.0.0.1')}:{server.server_address[1]}; "
          f"{len(gateway.manager.runtimes)} models available on demand", flush=True)
    try:
        while not stopping.wait(1):
            try:
                gateway.manager.unload_idle()
            except Exception:
                print('[gateway] idle unload failed; retaining runtime ownership and retrying', flush=True)
    finally:
        server.shutdown()
        server.server_close()
        gateway.manager.close()


if __name__ == '__main__':
    main()
