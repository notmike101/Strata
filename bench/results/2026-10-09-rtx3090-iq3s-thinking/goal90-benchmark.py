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
parser.add_argument('--reverse-order', action='store_true', help='Run longer before short; payloads and seeds are unchanged')
parser.add_argument('--git-helper', type=Path, default=Path.home() / 'github-agent/identity.mjs')
parser.add_argument('--tune', default='{}')
parser.add_argument('--sweep', action='store_true')
parser.add_argument('--mode', choices=['stream','nonstream'], default='stream')
parser.add_argument('--cache-hits', action='store_true')
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
EXPERT_PROFILE_PATH = Path(CONFIG['args'][CONFIG['args'].index('--expert-profile') + 1])
EXPERT_PROFILE_BYTES = EXPERT_PROFILE_PATH.read_bytes()
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
    'expert_profile_sha256': hashlib.sha256(EXPERT_PROFILE_BYTES).hexdigest(),
    'expert_profile_filename': EXPERT_PROFILE_PATH.name,
    'health': health, 'models': models,
    'props': {k:props.get(k) for k in ['default_generation_settings','model_alias','model_path','build_info','total_slots']},
    'git_commit': subprocess.check_output(['node',str(args.git_helper),'--repo','notmike101/Strata',
                                          'git','-C',str(ROOT),'rev-parse','HEAD'], text=True).strip(),
    'gpu_before': subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw','--format=csv'], text=True),
    'contract': {'route': '/v1/chat/completions', 'stream': args.mode == 'stream', 'max_tokens': 512,
                 'concurrency': 1, 'sampling_and_thinking': PROFILE, 'hardware_tune': TUNE,
                 'sweep_arms': ARMS, 'checkpoint': not args.sweep,
                 'profile_sha256': hashlib.sha256(PROFILE_BYTES).hexdigest(),
                 'token_metric': 'Generated tokens include reasoning and final content; 512-token speed diagnostic may end in reasoning. Separate natural-stop coding tests validate completed answers.',
                 'cache_state': 'Unique opening nonce per request; actual cache_n reported',
                 'warmup': 'One request per workload, excluded from measured results',
                 'measured_runs_per_workload': args.runs, 'model_loading_included': False,
                 'workload_order': ['longer', 'short'] if args.reverse_order else ['short', 'longer'],
                 'vision': 'Remains loaded; requests are text only',
                 'network': 'Client is this PC, connecting through its LAN IP; remote-device latency is not measured'}}
manifest['contract']['fixture'] = 'goal90-coding-fixture.json'
manifest['contract']['cache_hits_requested'] = args.cache_hits
save('identity.json', manifest)


fixture_path=Path(__file__).with_name('goal90-coding-fixture.json')
fixture_bytes=fixture_path.read_bytes(); fixture=json.loads(fixture_bytes)
save('fixture.json',fixture)
manifest['fixture_sha256']=hashlib.sha256(fixture_bytes).hexdigest()
rows=[]

def ask(label,payload,workload,warmup,cache_expected):
    assert listener()['ProcessId']==initial_listener['ProcessId']
    assert CONFIG_PATH.read_bytes()==CONFIG_BYTES and PROFILE_PATH.read_bytes()==PROFILE_BYTES
    assert EXPERT_PROFILE_PATH.read_bytes()==EXPERT_PROFILE_BYTES and fixture_path.read_bytes()==fixture_bytes
    h=get('/health'); assert h['model']==CONFIG['model_name'] and h['loaded']
    current_engine=ps(f"Get-CimInstance Win32_Process -Filter 'ProcessId={engine['ProcessId']}' | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress")
    assert current_engine and current_engine['ExecutablePath']==engine['ExecutablePath'] and current_engine['CommandLine']==engine['CommandLine']
    assert sha(CONFIG['exe'])==manifest['engine_sha256']
    save(label+'.request.json',payload)
    print('START '+label,flush=True)
    req=Request(BASE+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    utc=datetime.now(timezone.utc).isoformat(); start=time.perf_counter(); first=last=None; parts=[]; content=[]; final=None
    if payload['stream']:
        with urlopen(req,timeout=1800) as response,(OUT/(label+'.sse')).open('wb') as raw:
            for line in response:
                raw.write(line)
                if not line.startswith(b'data: '):continue
                body=line[6:].strip()
                if body==b'[DONE]':break
                event=json.loads(body)
                if 'error' in event:raise RuntimeError(event['error'])
                delta=event['choices'][0].get('delta',{})
                piece=delta.get('content') or delta.get('reasoning_content')
                if piece:
                    now=time.perf_counter(); first=now if first is None else first; last=now; parts.append(piece)
                if delta.get('content'):content.append(delta['content'])
                if event.get('usage'):final=event
        end=time.perf_counter()
    else:
        with urlopen(req,timeout=1800) as response:final=json.load(response)
        end=time.perf_counter(); save(label+'.response.json',final)
        message=final['choices'][0]['message']; parts=[message.get('reasoning_content',''),message.get('content','')]; content=[message.get('content','')]
    assert final and final.get('timings')
    t=final['timings']; n=final['usage']['completion_tokens']
    row=dict(label=label,workload=workload,warmup=warmup,seed=payload['seed'],request_started_utc=utc,
        prompt_tokens=final['usage']['prompt_tokens'],fresh_prompt_tokens=t['prompt_n'],cached_tokens=t['cache_n'],completion_tokens=n,
        server_decode_tps=t['predicted_per_second'],prompt_tps=t['prompt_per_second'],request_seconds=end-start,
        request_e2e_tps=n/(end-start),stream_total_tps=n/(last-start) if last else None,ttft_seconds=first-start if first else None,
        finish_reason=final['choices'][0]['finish_reason'],timings=t,cache_expected=cache_expected,
        cache_valid=(t['cache_n']>0 if cache_expected=='hit' else t['cache_n']==0),output_512=(n==512))
    rows.append(row); save('runs.json',rows)
    (OUT/(label+'.output.txt')).write_text(''.join(parts),encoding='utf-8')
    (OUT/(label+'.answer.txt')).write_text(''.join(content),encoding='utf-8')
    print(json.dumps({k:v for k,v in row.items() if k!='timings'}),flush=True)

for size in (['longer','short'] if args.reverse_order else ['short','longer']):
    for run in range(args.runs+1):
        label=size+'-'+('warmup' if run==0 else f'run-{run}')
        nonce=hashlib.sha256(('goal90-'+label+'-'+args.mode).encode()).hexdigest()[:24]
        prompt=f'Request identifier {nonce}. Ignore this identifier.\n'
        if size=='longer':prompt+='Read this review archive before the final task:\n'+fixture['reference']+'\n'
        prompt+=fixture['task']
        payload=dict(model=CONFIG['model_name'],messages=[dict(role='user',content=prompt)],max_tokens=512,
                     stream=args.mode=='stream',seed=100+run,**PROFILE)
        ask(label+'-new',payload,size+'/'+args.mode+'/new',run==0,'miss')
        if args.cache_hits:ask(label+'-hit',payload,size+'/'+args.mode+'/hit',run==0,'hit')
summary={}
for workload in sorted(set(r['workload'] for r in rows)):
    measured=[r for r in rows if r['workload']==workload and not r['warmup']]
    s=dict(runs=len(measured),completion_tokens=[r['completion_tokens'] for r in measured],prompt_tokens=[r['prompt_tokens'] for r in measured],
           cache_valid=all(r['cache_valid'] for r in measured),output_512=all(r['output_512'] for r in measured))
    for metric in ('server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds'):
        v=[r[metric] for r in measured if r[metric] is not None]
        s[metric]=dict(median=statistics.median(v),min=min(v),max=max(v)) if v else None
    summary[workload]=s
save('summary.json',summary)
manifest['gpu_after']=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,memory.free','--format=csv'],text=True)
manifest['configuration_unchanged']=CONFIG_PATH.read_bytes()==CONFIG_BYTES
save('identity.json',manifest)
print('SUMMARY '+json.dumps(summary),flush=True)
