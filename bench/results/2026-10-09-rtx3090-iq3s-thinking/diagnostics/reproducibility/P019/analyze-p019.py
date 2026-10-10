"""Compare the bounded P019 pair; binary logits remain private."""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np

base = Path(__file__).parent
out = Path('bench/results/2026-10-09-rtx3090-iq3s-thinking/diagnostics/reproducibility/P019')
def sha(b): return hashlib.sha256(b).hexdigest()
def trace(arm):
    requests = []
    for kind, x, y in re.findall(r'strata trace: (request|window) (\d+) (\d+)', (base/arm/'engine-session.txt').read_text(encoding='utf-8')):
        if kind == 'request': requests.append({'marker': [int(x), int(y)], 'windows': []})
        elif requests: requests[-1]['windows'].append([int(x), int(y)])
    return requests

arms = ['P019-A', 'P019-B']
identities=[json.loads((base/a/'identity.json').read_text(encoding='utf-8')) for a in arms]
assert identities[0]['engine_sha256']==identities[1]['engine_sha256']=='8057ab78c4129fc250ed668f5acd738a6b9cd2381b2d089467bd24f72f770ab2'
assert identities[0]['backend_library_sha256']==identities[1]['backend_library_sha256']
configs=[json.loads(json.dumps(x['config'])) for x in identities]
for c in configs: c['env'].pop('STRATA_DUMP_FIRST_LOGITS')
assert configs[0]==configs[1]
runs = [json.loads((base/a/'runs.json').read_text(encoding='utf-8')) for a in arms]
traces = [trace(a) for a in arms]
assert all(len(x)==9 for x in runs+traces)
result = {'diagnostic_only': True, 'throughput_qualification': False, 'requests': [], 'arms': {}}
for a, rows in zip(arms, runs):
    assert 'Cleanup verified: no live Strata' in (base/(a+'-wrapper.txt')).read_text(encoding='utf-8')
    assert all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in rows)
    safety=list(csv.DictReader((base/a/'safety.csv').open(encoding='utf-8')))
    floors={k:min(int(r[k]) for r in safety) for k in ['physical_available','commit_available']}
    assert min(floors.values()) >= 16*1024**3
    result['arms'][a]={'requests':len(rows),'minimum_available_bytes':floors,'cleanup_verified':True}
for i,(a,b) in enumerate(zip(*runs)):
    assert a['label']==b['label']
    label=a['label']
    payloads=[(base/x/(label+'.request.json')).read_bytes() for x in arms]
    assert payloads[0]==payloads[1]==(base/'R091-stack-share80'/(label+'.request.json')).read_bytes()
    blobs=[(base/(x+'-logits.'+str(i))).read_bytes() for x in arms]
    logits=[np.frombuffer(x,dtype='<f4') for x in blobs]
    assert all(len(x)==248320 and np.isfinite(x).all() for x in logits)
    text=[(base/x/(label+'.output.txt')).read_bytes() for x in arms]
    windows=[x[i]['windows'] for x in traces]
    first=next((j for j,(x,y) in enumerate(zip(*windows)) if x!=y),None)
    if first is None and len(windows[0])!=len(windows[1]): first=min(map(len,windows))
    result['requests'].append({'label':label,'payload_identical_to_R091':True,'logit_sha256':list(map(sha,blobs)),
        'logits_bit_identical':blobs[0]==blobs[1],'logits_max_abs_difference':float(np.max(np.abs(logits[0]-logits[1]))),
        'output_sha256':list(map(sha,text)),'output_identical':text[0]==text[1],
        'window_counts':list(map(len,windows)), 'first_differing_window_index_zero_based':first,
        'first_differing_windows':None if first is None else [w[first] if first<len(w) else None for w in windows],
        'draft_offered':[r['timings']['draft_n'] for r in [a,b]], 'draft_accepted':[r['timings']['draft_n_accepted'] for r in [a,b]]})
out.mkdir(parents=True,exist_ok=True)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(out/'window-traces.json').write_text(json.dumps(dict(zip(arms,traces)),indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
