"""Selected-coding ABBA: preserve the complete seed set and request identity."""
import json,statistics
from pathlib import Path
p=Path(__file__).parent
names=['R122-coding-control','R123-coding-prefix','R124-coding-prefix-reverse','R125-coding-control-reverse']
ids=[json.loads((p/a/'identity.json').read_text()) for a in names]
assert len({i['engine_sha256'] for i in ids})==1
assert len({i['fixture_sha256'] for i in ids})==1
cs=[json.loads(json.dumps(i['config'])) for i in ids]
assert [c['env'].pop('STRATA_PREFILL_STAGE_PREFIX') for c in cs]==['0','1','1','0']
assert all(c==cs[0] for c in cs)
assert all(i['backend_library_sha256']==ids[0]['backend_library_sha256'] for i in ids)
assert [i['contract']['workload_order'] for i in ids]==[['short','longer']]*2+[['longer','short']]*2
requests=list((p/names[0]).glob('*.request.json')); assert len(requests)==12
for f in requests:
    assert all((p/a/f.name).read_bytes()==f.read_bytes() for a in names),f.name
rows=[json.loads((p/a/'runs.json').read_text()) for a in names]
out={'arms':names,'engine_sha256':ids[0]['engine_sha256'],'fixture_sha256':ids[0]['fixture_sha256'],'request_bytes_identical':True,'full_goal_pass':False,'promoted':False,'cells':{}}
for size in ['short','longer']:
    w=size+'/stream/new'
    armrows=[[r for r in rr if r['workload']==w and not r['warmup']] for rr in rows]
    assert all(len(g)==5 and [r['seed'] for r in g]==list(range(101,106)) and all(r['completion_tokens']==512 and r['cached_tokens']==0 and r['cache_valid'] for r in g) for g in armrows)
    groups=[armrows[0]+armrows[3],armrows[1]+armrows[2]]
    c={'raw_decode':[[r['server_decode_tps'] for r in g] for g in groups],'metrics':{},'mtp':[]}
    for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']:
        vals=[[r[k] for r in g] for g in groups]; med=[statistics.median(v) for v in vals]
        c['metrics'][k]={'control':med[0],'candidate':med[1],'percent_change':100*(med[1]/med[0]-1),'ranges':[[min(v),max(v)] for v in vals]}
    for g in groups:
        accepted=sum(r['timings']['draft_n_accepted'] for r in g); offered=sum(r['timings']['draft_n'] for r in g)
        c['mtp'].append({'accepted':accepted,'offered':offered,'ratio':accepted/offered})
    c['decode_target_pass']=c['metrics']['server_decode_tps']['candidate'] >= (90 if size=='short' else 85)
    c['prompt_no_degradation']=c['metrics']['prompt_tps']['candidate']>=c['metrics']['prompt_tps']['control']
    c['e2e_no_degradation']=c['metrics']['request_e2e_tps']['candidate']>=c['metrics']['request_e2e_tps']['control']
    out['cells'][w]=c
(p/'c056-coding-pooled.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
