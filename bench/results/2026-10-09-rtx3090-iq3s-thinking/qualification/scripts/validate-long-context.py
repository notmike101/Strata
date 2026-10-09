"""Near-limit recall smoke test with the frozen thinking profile; not a speed trial."""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
p.add_argument('--root',type=Path,required=True)
p.add_argument('--base-url',required=True)
p.add_argument('--profile',type=Path,required=True)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
root = a.root
base = a.base_url.rstrip('/')
profile = json.loads(a.profile.read_text())
config_bytes = (root/'strata-iq3_s.json').read_bytes()
health = json.load(urlopen(base+'/health', timeout=20))
assert health['loaded'] and health['max_context'] == 262144

def post(path, body, timeout=120):
    return json.load(urlopen(Request(base+path, data=json.dumps(body).encode(),
                                    headers={'Content-Type': 'application/json'}), timeout=timeout))

codes = ['CEDAR-7421', 'ORBIT-5836', 'MAPLE-9164']
def content(n):
    lines = ['Context qualification Q003. The archive contains three special checkpoint records. '
             'Read the archive, then return the three checkpoint access codes in ALPHA, BETA, GAMMA order. '
             'All ordinary records are irrelevant.\n<archive>']
    needles = {n//10: ('ALPHA', codes[0]), n//2: ('BETA', codes[1]), n*9//10: ('GAMMA', codes[2])}
    for i in range(n):
        if i in needles:
            name, code = needles[i]
            lines.append(f'SPECIAL CHECKPOINT {name}: access code = {code}.')
        lines.append(f'Record {i:06d}: module_{i%997:03d} completed its ordinary review; status stable; '
                     f'checksum {hashlib.sha256(str(i).encode()).hexdigest()[:16]}.')
    lines.append('</archive>\nReturn only the three special checkpoint access codes, separated by commas, '
                 'in ALPHA, BETA, GAMMA order.')
    return '\n'.join(lines)

counts = []
n = 5000
for attempt in range(8):
    prompt = content(n)
    count_body = {'model': health['model'], 'messages': [{'role':'user','content':prompt}],
                  'output_config': {'effort':'high'}}
    tokens = post('/v1/messages/count_tokens', count_body)['input_tokens']
    counts.append({'records': n, 'input_tokens': tokens})
    print('COUNT', n, tokens, flush=True)
    if 258900 <= tokens <= 259100:
        break
    n = max(1, round(n * 259000 / tokens))
else:
    raise RuntimeError('Could not size prompt near 259000 tokens')

payload = {'model': health['model'], 'messages': [{'role':'user','content':prompt}],
           'max_tokens': 2048, 'seed': 101, **profile}
(a.out/'request.json').write_text(json.dumps(payload, indent=2)+'\n')
(a.out/'identity.json').write_text(json.dumps({'utc_started':datetime.now(timezone.utc).isoformat(),
    'health':health, 'counting':counts, 'config_sha256':hashlib.sha256(config_bytes).hexdigest(),
    'profile':profile, 'expected_codes':codes,
    'note':'Single near-limit recall smoke test. Anthropic count estimate; actual OpenAI usage authoritative.'}, indent=2)+'\n')
print('GENERATING near-limit recall', tokens, 'estimated prompt tokens', flush=True)
start = time.perf_counter()
try:
    response = post('/v1/chat/completions', payload, timeout=7200)
    wall = time.perf_counter()-start
    (a.out/'response.json').write_text(json.dumps(response, indent=2)+'\n')
    msg = response['choices'][0]
    answer = msg['message']['content']
    actual = response['usage']['prompt_tokens']
    passed = (msg['finish_reason']=='stop' and all(c in answer for c in codes)
              and actual >= 258000 and actual+response['usage']['completion_tokens'] <= 262144)
    summary = {'passed':passed, 'wall_seconds':wall, 'usage':response['usage'],
               'timings':response.get('timings'), 'answer':answer, 'finish_reason':msg['finish_reason'],
               'config_unchanged':config_bytes==(root/'strata-iq3_s.json').read_bytes(),
               'limitation':'One synthetic recall input; does not establish long-context coding quality or 80 tok/s at depth.'}
    (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary), flush=True)
    assert passed and summary['config_unchanged']
except Exception as exc:
    (a.out/'failure.json').write_text(json.dumps({'error':repr(exc),'wall_seconds':time.perf_counter()-start},indent=2)+'\n')
    raise
