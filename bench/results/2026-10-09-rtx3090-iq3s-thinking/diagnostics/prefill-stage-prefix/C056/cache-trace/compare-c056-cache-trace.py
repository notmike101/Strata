import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
names=['P023-cache-trace-control','P024-cache-trace-prefix']
v=[json.loads((p/n/'trace-stages.json').read_text()) for n in names]
ids=[json.loads((p/n/'identity.json').read_text()) for n in names]
assert ids[0]['engine_sha256']==ids[1]['engine_sha256'] and ids[0]['backend_library_sha256']==ids[1]['backend_library_sha256']
files=list((p/names[0]).glob('*.request.json')); assert len(files)==24
assert all(f.read_bytes()==(p/names[1]/f.name).read_bytes() for f in files)
comparison={}
for w in v[0]['summary']:
    comparison[w]={k:{'control':s['median'],'candidate':v[1]['summary'][w][k]['median']} for k,s in v[0]['summary'][w].items()}
    for s in comparison[w].values(): s['difference']=s['candidate']-s['control']
out={'diagnostic_only':True,'qualifying_repetitions_added':0,'same_requests_binary_libraries':True,'arms':names,'cells':comparison}
(p/'c056-cache-trace-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
for w,c in comparison.items():
    print(w)
    print(json.dumps(c,indent=2))
