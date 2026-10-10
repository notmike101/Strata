"""Replay the history preceding the first C047 longer-request divergence."""
from pathlib import Path
source=Path(__file__).with_name('goal90-benchmark.py').read_text(encoding='utf-8')
exec(compile(source.split('for size in (')[0],str(Path(__file__).with_name('goal90-benchmark.py')),'exec'))
manifest['instrumentation']={'authoritative':False,'purpose':'P019 first differing window, fixed80 complete prior request history','window_trace':True,'first_window_logits':True,'payload_source':'R091 exact short warmup+5, longer warmup+first2','fixture_note':'goal90 fixture initialized by helper is not used by these requests'}
save('identity.json',manifest)
labels=['short-warmup']+[f'short-run-{i}' for i in range(1,6)]+['longer-warmup','longer-run-1','longer-run-2']
for label in labels:
    payload=json.loads((Path(__file__).parent/'R091-stack-share80'/f'{label}.request.json').read_text(encoding='utf-8'))
    ask(label,payload,label.split('-')[0],label.endswith('warmup'),'miss')
summary={}
for w in ['short','longer']:
    rr=[r for r in rows if r['workload']==w and not r['warmup']]
    summary[w]={'runs':len(rr),'completion_tokens':[r['completion_tokens'] for r in rr],'prompt_tokens':[r['prompt_tokens'] for r in rr]}
    for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']:
        vv=[r[k] for r in rr];summary[w][k]={'median':statistics.median(vv),'min':min(vv),'max':max(vv)}
save('summary.json',summary)
