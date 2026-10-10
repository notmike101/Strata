"""Freeze all-run ABBA comparison, with identical request bytes across arms."""
import json, statistics
from pathlib import Path
p=Path(__file__).parent
names=['R118-preserve-control','R119-prefix-preserve','R120-prefix-preserve-reverse','R121-preserve-control-reverse']
ids=[json.loads((p/a/'identity.json').read_text()) for a in names]
assert len({i['engine_sha256'] for i in ids})==1
configs=[json.loads(json.dumps(i['config'])) for i in ids]
assert [c['env'].pop('STRATA_PREFILL_STAGE_PREFIX') for c in configs]==['0','1','1','0']
assert all(c==configs[0] for c in configs)
assert all(i['backend_library_sha256']==ids[0]['backend_library_sha256'] for i in ids)
requests=list((p/names[0]).glob('*.request.json')); assert len(requests)==12
for f in requests:
    assert all((p/a/f.name).read_bytes()==f.read_bytes() for a in names),f.name
rows=[json.loads((p/a/'runs.json').read_text()) for a in names]
out={'arms':names,'engine_sha256':ids[0]['engine_sha256'],'request_bytes_identical':True,'promoted':False,'full_goal_pass':False,'cells':{}}
for w in ['short','longer']:
    arm_rows=[[r for r in rr if r['workload']==w and not r['warmup']] for rr in rows]
    assert all(len(g)==5 and all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in g) for g in arm_rows)
    groups=[arm_rows[0]+arm_rows[3],arm_rows[1]+arm_rows[2]]
    cell={'raw_decode':[[r['server_decode_tps'] for r in g] for g in groups],'metrics':{}}
    for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']:
        values=[[r[k] for r in g] for g in groups]; med=[statistics.median(v) for v in values]
        cell['metrics'][k]={'control':med[0],'candidate':med[1],'percent_change':100*(med[1]/med[0]-1),'ranges':[[min(v),max(v)] for v in values]}
    cell['decode_target_pass']=cell['metrics']['server_decode_tps']['candidate'] >= (90 if w=='short' else 85)
    cell['prompt_no_degradation']=cell['metrics']['prompt_tps']['candidate']>=cell['metrics']['prompt_tps']['control']
    cell['e2e_no_degradation']=cell['metrics']['request_e2e_tps']['candidate']>=cell['metrics']['request_e2e_tps']['control']
    out['cells'][w]=cell
(p/'c056-pooled.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
