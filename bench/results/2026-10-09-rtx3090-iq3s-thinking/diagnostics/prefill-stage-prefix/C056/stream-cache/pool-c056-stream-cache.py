"""All-run exact-repeat streaming comparison, keeping setup misses separate."""
import json,statistics
from pathlib import Path
p=Path(__file__).parent
names=['R128-stream-cache-control','R129-stream-cache-prefix','R130-stream-cache-prefix-reverse','R131-stream-cache-control-reverse']
ids=[json.loads((p/n/'identity.json').read_text()) for n in names]
assert len({i['engine_sha256'] for i in ids})==len({i['fixture_sha256'] for i in ids})==1
cs=[json.loads(json.dumps(i['config'])) for i in ids]
assert [c['env'].pop('STRATA_PREFILL_STAGE_PREFIX') for c in cs]==['0','1','1','0']
assert all(c==cs[0] for c in cs)
assert all(i['backend_library_sha256']==ids[0]['backend_library_sha256'] for i in ids)
assert all(i['contract']['cache_hits_requested'] and i['contract']['stream'] for i in ids)
assert [i['contract']['workload_order'] for i in ids]==[['short','longer']]*2+[['longer','short']]*2
files=list((p/names[0]).glob('*.request.json')); assert len(files)==24
for f in files:
    assert all((p/n/f.name).read_bytes()==f.read_bytes() for n in names),f.name
rows=[json.loads((p/n/'runs.json').read_text()) for n in names]
assert all(len(rr)==24 and all(r['completion_tokens']==512 and r['cache_valid'] for r in rr) for rr in rows)
out={'arms':names,'engine_sha256':ids[0]['engine_sha256'],'fixture_sha256':ids[0]['fixture_sha256'],'request_bytes_identical':True,'full_goal_pass':False,'promoted':False,'first_requests':{n:rr[0] for n,rr in zip(names,rows)},'cells':{}}
for w in sorted({r['workload'] for r in rows[0]}):
    armrows=[[r for r in rr if r['workload']==w and not r['warmup']] for rr in rows]
    assert all(len(g)==5 and [r['seed'] for r in g]==list(range(101,106)) for g in armrows)
    hit=w.endswith('/hit')
    assert all((r['cached_tokens']>0 if hit else r['cached_tokens']==0) for g in armrows for r in g)
    groups=[armrows[0]+armrows[3],armrows[1]+armrows[2]]
    cell={'exact_repeat_hit':hit,'raw_decode':[[r['server_decode_tps'] for r in g] for g in groups],
          'fresh_cached_counts':[[(r['fresh_prompt_tokens'],r['cached_tokens']) for r in g] for g in groups],'metrics':{},'mtp':[]}
    for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']:
        vals=[[r[k] for r in g] for g in groups]; med=[statistics.median(v) for v in vals]
        cell['metrics'][k]={'control':med[0],'candidate':med[1],'percent_change':100*(med[1]/med[0]-1) if med[0] else None,'ranges':[[min(v),max(v)] for v in vals]}
    for g in groups:
        accepted=sum(r['timings']['draft_n_accepted'] for r in g); offered=sum(r['timings']['draft_n'] for r in g)
        cell['mtp'].append({'accepted':accepted,'offered':offered,'ratio':accepted/offered if offered else None})
    m=cell['metrics']
    cell['decode_target_pass']=m['server_decode_tps']['candidate'] >= (90 if w.startswith('short/') else 85)
    cell['decode_no_degradation']=m['server_decode_tps']['candidate']>=m['server_decode_tps']['control']
    cell['prompt_no_degradation']=m['prompt_tps']['candidate']>=m['prompt_tps']['control']
    cell['e2e_no_degradation']=m['request_e2e_tps']['candidate']>=m['request_e2e_tps']['control']
    cell['latency_no_degradation']=m['request_seconds']['candidate']<=m['request_seconds']['control']
    cell['ttft_no_degradation']=m['ttft_seconds']['candidate']<=m['ttft_seconds']['control']
    out['cells'][w]=cell
(p/'c056-stream-cache-pooled.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
