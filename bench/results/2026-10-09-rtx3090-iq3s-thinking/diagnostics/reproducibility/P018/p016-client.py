"""P016: two exact historical payloads, routing/logit diagnostic only."""
from pathlib import Path
source=Path(__file__).with_name('goal90-benchmark.py').read_text(encoding='utf-8')
exec(compile(source.split('for size in (')[0],str(Path(__file__).with_name('goal90-benchmark.py')),'exec'))
manifest['instrumentation']={'authoritative':False,'purpose':'P016 repeated fresh-process routing and first-window logit comparison; no qualifying speed claim','routing_trace':True,'first_window_logits':True,'payload_source':'R084-usage0-hc0 exact short warmup and run1','fixture_note':'goal90 fixture initialized by helper is not used by these requests'}
save('identity.json',manifest)
for label in ['short-warmup','short-run-1']:
    payload=json.loads((Path(__file__).parent/'R084-usage0-hc0'/f'{label}.request.json').read_text(encoding='utf-8'))
    ask(label,payload,'short',label.endswith('warmup'),'miss')
r=rows[-1]
summary={'short':{'runs':1,'completion_tokens':[r['completion_tokens']],'prompt_tokens':[r['prompt_tokens']]}}
for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']:
    summary['short'][k]={'median':r[k],'min':r[k],'max':r[k]}
save('summary.json',summary)
