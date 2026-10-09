# Campaign measurement script. Publication adaptations: root, config and URL are arguments;
# profile filename is sampling.json. Measurement/prompt/seed logic is unchanged. Windows only.
"""Measure the existing Strata API without changing server configuration."""
import argparse
import csv
import hashlib
import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--base-url', required=True)
parser.add_argument('--runs', type=int, default=5)
parser.add_argument('--tune', default='{}')
parser.add_argument('--sweep', action='store_true')
args = parser.parse_args()
PROFILE_PATH = Path(__file__).with_name('sampling.json')
PROFILE_BYTES = PROFILE_PATH.read_bytes()
PROFILE = json.loads(PROFILE_BYTES)
TUNE = json.loads(args.tune)
assert set(TUNE) <= {'pcie_frac', 'spec_min_p'}
ARMS = [('control', {}), ('floor05', {'spec_min_p':0.5}), ('floor09', {'spec_min_p':0.9})] if args.sweep else [('single', TUNE)]
OUT = Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)
ROOT = args.root
CONFIG_PATH = Path(args.config)
CONFIG_BYTES = CONFIG_PATH.read_bytes()
CONFIG = json.loads(CONFIG_BYTES)
EXPECTED_CONTEXT = int(CONFIG['args'][CONFIG['args'].index('--max-context') + 1])
KEY = CONFIG.get('api_key', '')
BASE = args.base_url.rstrip('/')


def save(name, value):
    text = json.dumps(value, indent=2, ensure_ascii=False)
    if KEY:
        text = text.replace(KEY, '<redacted>')
    (OUT / name).write_text(text + '\n', encoding='utf-8')


def ps(code):
    result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', code],
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def get(path):
    headers = {'Authorization': 'Bearer ' + KEY} if KEY else {}
    req = Request(BASE + path, headers=headers)
    with urlopen(req, timeout=20) as response:
        return json.load(response)


def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def listener():
    return ps("$c = Get-NetTCPConnection -State Listen -LocalPort 8080 | Select-Object -First 1; "
              "Get-CimInstance Win32_Process -Filter ('ProcessId=' + $c.OwningProcess) | "
              "Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress")


initial_listener = listener()
assert 'serve.server' in initial_listener['CommandLine']
assert CONFIG_PATH.name in initial_listener['CommandLine']
health = get('/health')
models = get('/v1/models')
props = get('/props')
for key in ['temperature','top_p','top_k','min_p','presence_penalty','repetition_penalty','frequency_penalty']:
    assert CONFIG['sampling'][key] == PROFILE[key], key
    prop_key = 'repeat_penalty' if key == 'repetition_penalty' else key
    assert props['default_generation_settings']['params'][prop_key] == PROFILE[key], key
assert health['model'] == CONFIG['model_name'] and health['loaded']
assert health['max_context'] == EXPECTED_CONTEXT and health['images']
processes = ps("ConvertTo-Json -Compress -InputObject @(Get-CimInstance Win32_Process | "
               "Where-Object { $_.Name -like 'strata*.exe' } | "
               "Select-Object ProcessId,Name,ExecutablePath,CommandLine)")
engines = [p for p in processes if p.get('ExecutablePath') and
           Path(p['ExecutablePath']).resolve() == Path(CONFIG['exe']).resolve()]
assert len(engines) == 1, 'Expected exactly one engine at the configured executable path'
engine = engines[0]
assert Path(engine['ExecutablePath']).resolve() == Path(CONFIG['exe']).resolve()
native = Path(CONFIG['args'][CONFIG['args'].index('--native') + 1])
assert str(EXPECTED_CONTEXT) in engine['CommandLine'] and str(native).lower() in engine['CommandLine'].lower()
libraries = ps(f"(Get-Process -Id {engine['ProcessId']}).Modules | Where-Object {{ "
               "$_.FileName -like '*nvidia*cu13*' -or $_.ModuleName -eq 'nvcuda.dll' } | "
               "Select-Object -ExpandProperty FileName | ConvertTo-Json -Compress")
if isinstance(libraries, str):
    libraries = [libraries]
shards = []
shard_prefix = native.name.split('-00001-of-')[0]
for path in sorted(native.parent.glob(shard_prefix + '-*.gguf')):
    shards.append({'path': str(path), 'bytes': path.stat().st_size,
                   'sha256_from_setup_verification': path.with_name(path.name + '.done').read_text().strip(),
                   'note': 'Previously fully hashed during this setup; not rehashed by this benchmark.'})
manifest = {
    'utc_started': datetime.now(timezone.utc).isoformat(), 'base_url': BASE,
    'listener': initial_listener, 'engine_processes': processes,
    'engine_sha256': sha(CONFIG['exe']), 'vision_sha256': sha(CONFIG['vision']['exe']),
    'backend_library_sha256': {path: sha(path) for path in libraries},
    'projector_sha256': sha(CONFIG['vision']['mmproj']), 'shards': shards,
    'config': {k:v for k,v in CONFIG.items() if k != 'api_key'},
    'config_sha256': hashlib.sha256(CONFIG_BYTES).hexdigest(),
    'health': health, 'models': models,
    'props': {k:props.get(k) for k in ['default_generation_settings','model_alias','model_path','build_info','total_slots']},
    'git_commit': subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'], text=True).strip(),
    'gpu_before': subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw','--format=csv'], text=True),
    'contract': {'route': '/v1/chat/completions', 'stream': True, 'max_tokens': 512,
                 'concurrency': 1, 'sampling_and_thinking': PROFILE, 'hardware_tune': TUNE,
                 'sweep_arms': ARMS, 'checkpoint': not args.sweep,
                 'profile_sha256': hashlib.sha256(PROFILE_BYTES).hexdigest(),
                 'token_metric': 'Generated tokens include reasoning and final content; 512-token speed diagnostic may end in reasoning. Separate natural-stop coding tests validate completed answers.',
                 'cache_state': 'Unique opening nonce per request; actual cache_n reported',
                 'warmup': 'One request per workload, excluded from measured results',
                 'measured_runs_per_workload': args.runs, 'model_loading_included': False,
                 'vision': 'Remains loaded; requests are text only',
                 'network': 'Client is this PC, connecting through its LAN IP; remote-device latency is not measured'}}
save('identity.json', manifest)

TASK = ('Implement a thread-safe Python TTLCache class using an OrderedDict and a monotonic clock. '
        'Include set, get, delete, clear, len, expiration, capacity eviction, unit tests with an injected fake clock, '
        'and a detailed explanation of thread safety and complexity. Write complete code, then tests, then explain '
        'the design. Do not abbreviate the implementation. Produce a detailed answer of at least 1200 words.')
REFERENCE = '\n'.join(
    f'Existing cache rule {i}: key item_{i:03d} has lifetime {30 + i} seconds and size {64 + i * 3} bytes; '
    'expiration must remove stale entries, and access must update least-recently-used order.'
    for i in range(64))
rows = []
for workload in ['short', 'longer']:
    for run, arm_name, arm_tune in [(r,name,tune) for r in range(args.runs+1) for name,tune in (ARMS if r%2==0 else ARMS[::-1])]:
        base_label = f'{workload}-' + ('warmup' if run == 0 else f'run-{run}')
        label = base_label + ('-'+arm_name if args.sweep else '')
        workload_key = workload + ('/'+arm_name if args.sweep else '')
        current = listener()
        assert current['ProcessId'] == initial_listener['ProcessId'], 'Server identity changed'
        assert CONFIG_PATH.read_bytes() == CONFIG_BYTES, 'Server config changed'
        assert PROFILE_PATH.read_bytes() == PROFILE_BYTES, 'Frozen sampling contract changed'
        h = get('/health')
        assert h['model'] == CONFIG['model_name'] and h['loaded']
        nonce = hashlib.sha256((('sweep-' if args.sweep else '')+base_label).encode()).hexdigest()[:24]
        prompt = f'Benchmark identifier {nonce}. Ignore this identifier.\n'
        if workload == 'longer':
            prompt += 'Read these existing design requirements before implementing the cache:\n' + REFERENCE + '\n'
        prompt += TASK
        payload = {'model': CONFIG['model_name'], 'messages': [{'role':'user','content':prompt}],
                   'max_tokens':512, 'stream':True, **PROFILE, 'seed':100+run}
        if arm_tune:
            payload['strata_tune'] = arm_tune
        if args.sweep:
            payload['strata_checkpoint'] = False
        save(label + '.request.json', payload)
        print(f'START {label}', flush=True)
        headers = {'Content-Type':'application/json'}
        if KEY:
            headers['Authorization'] = 'Bearer ' + KEY
        req = Request(BASE + '/v1/chat/completions', data=json.dumps(payload).encode(), headers=headers)
        started = time.perf_counter()
        first = last_token = None
        chunks = []
        final = None
        with urlopen(req, timeout=900) as response, (OUT / (label + '.sse')).open('wb') as raw:
            for line in response:
                raw.write(line)
                if not line.startswith(b'data: '):
                    continue
                body = line[6:].strip()
                if body == b'[DONE]':
                    break
                event = json.loads(body)
                if 'error' in event:
                    raise RuntimeError(event['error'])
                delta = event['choices'][0].get('delta', {})
                piece = delta.get('content') or delta.get('reasoning_content')
                if piece:
                    now = time.perf_counter()
                    first = now if first is None else first
                    last_token = now
                    chunks.append(piece)
                if event.get('usage'):
                    final = event
        ended = time.perf_counter()
        assert final and first and final.get('timings'), 'Missing measured timing fields'
        t = final['timings']
        n = final['usage']['completion_tokens']
        row = {'label':label, 'workload':workload_key, 'warmup':run == 0,
               'prompt_tokens':final['usage']['prompt_tokens'], 'fresh_prompt_tokens':t['prompt_n'],
               'cached_tokens':t['cache_n'], 'completion_tokens':n,
               'server_decode_tps':t['predicted_per_second'], 'prompt_tps':t['prompt_per_second'],
               'ttft_seconds':first-started, 'request_seconds':ended-started,
               'request_e2e_tps':n/(ended-started), 'stream_total_tps':n/(last_token-started),
               'finish_reason':final['choices'][0]['finish_reason'], 'timings':t}
        rows.append(row)
        save('runs.json', rows)
        (OUT / (label + '.output.txt')).write_text(''.join(chunks), encoding='utf-8')
        print(json.dumps({k:v for k,v in row.items() if k != 'timings'}), flush=True)

summary = {}
for workload in sorted(set(r['workload'] for r in rows)):
    measured = [r for r in rows if r['workload'] == workload and not r['warmup']]
    summary[workload] = {'runs':len(measured), 'prompt_tokens':[r['prompt_tokens'] for r in measured],
                         'completion_tokens':[r['completion_tokens'] for r in measured]}
    for metric in ['server_decode_tps','prompt_tps','ttft_seconds','request_seconds','request_e2e_tps','stream_total_tps']:
        values = [r[metric] for r in measured]
        summary[workload][metric] = {'median':statistics.median(values), 'min':min(values), 'max':max(values)}
assert CONFIG_PATH.read_bytes() == CONFIG_BYTES
save('summary.json', summary)
manifest['gpu_after'] = subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw','--format=csv'], text=True)
manifest['configuration_unchanged'] = True
save('identity.json', manifest)
columns = [k for k in rows[0] if k != 'timings']
with (OUT / 'runs.csv').open('w',newline='',encoding='utf-8') as target:
    writer = csv.DictWriter(target,fieldnames=columns)
    writer.writeheader()
    writer.writerows({k:r[k] for k in columns} for r in rows)
print('SUMMARY ' + json.dumps(summary), flush=True)
