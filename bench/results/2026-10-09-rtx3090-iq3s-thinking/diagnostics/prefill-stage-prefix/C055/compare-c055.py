"""Same-binary fixed-contract first-pair screen; never declares promotion."""
import json, statistics
from pathlib import Path
p=Path(__file__).parent
arms=['R116-prefix-control','R117-prefix-stage']
ids=[json.loads((p/a/'identity.json').read_text()) for a in arms]
assert ids[0]['engine_sha256']==ids[1]['engine_sha256']
assert ids[0]['backend_library_sha256']==ids[1]['backend_library_sha256']
c=[json.loads(json.dumps(i['config'])) for i in ids]
assert [i['env'].pop('STRATA_PREFILL_STAGE_PREFIX') for i in c]==['0','1']
assert c[0]==c[1]
rr=[json.loads((p/a/'runs.json').read_text()) for a in arms]
result={'arms':arms,'engine_sha256':ids[0]['engine_sha256'],'promoted':False,'full_goal_pass':False,'cells':{}}
for w in ['short','longer']:
    gs=[[r for r in rows if r['workload']==w and not r['warmup']] for rows in rr]
    assert all(len(g)==5 and all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in g) for g in gs)
    metrics={}
    for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']:
        med=[statistics.median(r[k] for r in g) for g in gs]
        metrics[k]={'control':med[0],'candidate':med[1],'percent_change':100*(med[1]/med[0]-1)}
    result['cells'][w]={'metrics':metrics,'raw_decode':[[r['server_decode_tps'] for r in g] for g in gs]}
out=p/'c055-first-pair.json'; out.write_text(json.dumps(result,indent=2)+'\n')
print(out.read_text())
