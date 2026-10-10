"""One identified warmup and one complete short capture; diagnostic only."""
from pathlib import Path
source=Path(__file__).with_name('goal90-benchmark.py').read_text()
exec(compile(source.split('for size in (')[0],str(Path(__file__).with_name('goal90-benchmark.py')),'exec'))
nsys=r'C:\Strata\.tools\n5\ProgramFiles64Folder\NVIDIA Corporation\Nsight Systems 2026.5.1\target-windows-x64\nsys.exe'
manifest['instrumentation']={'nsight':'2026.5.1.161 CUDA graph nodes','host_decode_timers':True,'gpu_phase_stamps':False,
 'authoritative':False,'purpose':'Prove device-side resident-group planning activation; diagnostic, not qualifying throughput.'}
save('identity.json',manifest)
def payload(run):
    label='short-'+('warmup' if run==0 else f'run-{run}')
    nonce=hashlib.sha256(('goal90-'+label+'-stream').encode()).hexdigest()[:24]
    return dict(model=CONFIG['model_name'],messages=[dict(role='user',content=f'Request identifier {nonce}. Ignore this identifier.\n'+fixture['task'])],
                max_tokens=512,stream=True,seed=100+run,**PROFILE)
ask('short-warmup',payload(0),'short',True,'miss')
subprocess.run([nsys,'start','--session=strata90device'],check=True)
try:ask('short-run-1',payload(1),'short',False,'miss')
finally:subprocess.run([nsys,'stop','--session=strata90device'],check=True)
measured=rows[-1]
summary={'short':{'runs':1,'completion_tokens':[measured['completion_tokens']], 'prompt_tokens':[measured['prompt_tokens']]}}
for k in ('server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds'):
    summary['short'][k]={'median':measured[k],'min':measured[k],'max':measured[k]}
save('summary.json',summary)
