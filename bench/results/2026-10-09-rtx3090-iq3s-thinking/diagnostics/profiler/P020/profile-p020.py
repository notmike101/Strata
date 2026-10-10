"""One identified warmup and one complete short capture; diagnostic only."""
from pathlib import Path
source=Path(__file__).with_name('goal90-benchmark.py').read_text(encoding='utf-8')
exec(compile(source.split('for size in (')[0],str(Path(__file__).with_name('goal90-benchmark.py')),'exec'))
nsys=r'C:\Strata\.tools\n5\ProgramFiles64Folder\NVIDIA Corporation\Nsight Systems 2026.5.1\target-windows-x64\nsys.exe'
manifest['instrumentation']={'nsight':'2026.5.1.161 CUDA graph nodes','host_decode_timers':True,'gpu_phase_stamps':False,
 'authoritative':False,'purpose':'P020 exact R099 short payload replay, includes prompt processing; only one measured profile, no TPS qualification.'}
save('identity.json',manifest)
def payload(run):
    label='short-warmup' if run==0 else 'short-run-1'
    return json.loads((Path(__file__).parent/'R099-conditional64'/(label+'.request.json')).read_text(encoding='utf-8'))
ask('short-warmup',payload(0),'short',True,'miss')
subprocess.run([nsys,'start','--session=strata90p020'],check=True)
try:ask('short-run-1',payload(1),'short',False,'miss')
finally:subprocess.run([nsys,'stop','--session=strata90p020'],check=True)
measured=rows[-1]
summary={'short':{'runs':1,'completion_tokens':[measured['completion_tokens']], 'prompt_tokens':[measured['prompt_tokens']]}}
for k in ('server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds'):
    summary['short'][k]={'median':measured[k],'min':measured[k],'max':measured[k]}
save('summary.json',summary)
