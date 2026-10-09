"""Build an execution-cache profile on held-out synthetic coding requests; no weight training."""
import argparse, hashlib, json, time
from pathlib import Path
from urllib.request import Request, urlopen
p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--base-url',required=True); a=p.parse_args()
root=a.root
out=root/'local-setup/target-80/T001-coding-profile-data'; out.mkdir(parents=True,exist_ok=True)
cfg=json.loads((root/'strata-iq3_s.json').read_text())
assert cfg['expert_profile_save'].endswith('T001-learned-profile.bin')
profile=json.loads((root/'local-setup/coding-best-practices/profile.json').read_text())
base=a.base_url.rstrip('/')
health=json.load(urlopen(base+'/health')); assert health['loaded'] and health['model']==cfg['model_name'] and health['max_context']==262144
tasks=[
 'Design a Rust streaming CSV parser with quoted fields and escaped quotes. Explain the state machine and error handling, then implement it with tests.',
 'Implement a TypeScript dependency graph topological sorter that reports cycles with a readable path. Explain correctness and test disconnected components.',
 'Review a PostgreSQL order processing schema. Design an idempotent transaction for inventory reservation under concurrent requests, with SQL and isolation-level analysis.',
 'Implement a C++ bounded producer-consumer queue with graceful shutdown. Discuss ownership, condition variables, exception safety, and tests.',
 'Write Python code for a JSON Pointer evaluator with strict escape handling and informative failures. Explain edge cases and include unit tests.',
 'Design a Go HTTP retry client with deadlines, jitter and idempotency rules. Explain cancellation and implement deterministic tests.',
 'Implement a Java incremental SHA-256 file verifier that reports progress and handles interrupted reads. Explain resource management and tests.',
 'Design a C# command-line configuration loader that merges defaults, a JSON file and environment variables. Validate types and show test cases.'
]
for i,task in enumerate(tasks):
    payload=dict(model=cfg['model_name'],messages=[dict(role='user',content=f'Independent coding-profile preparation item {i}.\n'+task)],max_tokens=512,seed=201+i,**profile)
    start=time.perf_counter()
    response=json.load(urlopen(Request(base+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=900))
    (out/f'item-{i}.json').write_text(json.dumps({'request':payload,'response':response,'wall_seconds':time.perf_counter()-start},indent=2)+'\n')
    print('PROFILE ITEM',i,response['usage'],flush=True)
# Saving occurs before the next request. This unrelated sentinel flushes item7's ranking.
payload=dict(model=cfg['model_name'],messages=[dict(role='user',content='Reply with exactly PROFILE_READY.')],max_tokens=256,seed=209,**profile)
response=json.load(urlopen(Request(base+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=900))
(out/'sentinel.json').write_text(json.dumps({'request':payload,'response':response},indent=2)+'\n')
source=Path(cfg['expert_profile_save']); data=source.read_bytes()
frozen=root/'data/expert-profile-coding-v1.bin'
assert not frozen.exists(), 'Do not overwrite an existing frozen experiment profile'
frozen.write_bytes(data)
(out/'summary.json').write_text(json.dumps({'prepared':True,'training_requests':8,'seeds':list(range(201,209)),
    'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'frozen_profile':frozen.name,
    'note':'Execution-cache placement ranking only. Distinct coding tasks exclude benchmark TTLCache prompts. Freeze before benchmark; saving disabled for measured candidate.'},indent=2)+'\n')
print('FROZEN PROFILE',len(data),hashlib.sha256(data).hexdigest(),flush=True)
