"""One fixed new/repeat pair after identical warmups; diagnostic only."""
from pathlib import Path
source=Path(__file__).with_name('goal90-benchmark.py').read_text(encoding='utf-8')
exec(compile(source.split('for size in (')[0],str(Path(__file__).with_name('goal90-benchmark.py')),'exec'))
nsys=r'C:\Strata\.tools\n5\ProgramFiles64Folder\NVIDIA Corporation\Nsight Systems 2026.5.1\target-windows-x64\nsys.exe'
manifest['instrumentation']={'nsight':'2026.5.1.161 CUDA graph nodes','host_decode_timers':True,'gpu_phase_stamps':False,'authoritative':False,'purpose':'P025 exact R129 short warmup new/hit then measured new/hit; complete two-request capture, not throughput qualification.'}
save('identity.json',manifest)
assert manifest['engine_sha256']=='cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91'
anchor=json.loads((Path(__file__).parent/'R129-stream-cache-prefix/identity.json').read_text())
assert manifest['backend_library_sha256']==anchor['backend_library_sha256']
expected=json.loads(json.dumps(CONFIG)); assert expected['env'].pop('STRATA_DECODE_TIMING')=='1'
assert expected==anchor['config']
def send(label,warmup):
    payload=json.loads((Path(__file__).parent/'R129-stream-cache-prefix'/(label+'.request.json')).read_text(encoding='utf-8'))
    kind='hit' if label.endswith('-hit') else 'new'
    ask(label,payload,'short/stream/'+kind,warmup,'hit' if kind=='hit' else 'miss')
send('short-warmup-new',True); send('short-warmup-hit',True)
subprocess.run([nsys,'start','--session=strata90p025'],check=True)
try:
    send('short-run-1-new',False)
    send('short-run-1-hit',False)
finally:subprocess.run([nsys,'stop','--session=strata90p025'],check=True)
summary={}
for r in rows:
    assert r['completion_tokens']==512 and r['cache_valid']
    if r['warmup']:continue
    cell={'runs':1,'completion_tokens':[512],'prompt_tokens':[r['prompt_tokens']]}
    for k in ('server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds'):
        cell[k]={'median':r[k],'min':r[k],'max':r[k]}
    summary[r['workload']]=cell
save('summary.json',summary)
