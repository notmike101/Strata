"""Re-evaluate every stored answer in the quality series; never regenerate/select."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

p = Path(__file__).parent
old = (p/'check-topological.py').read_bytes()
new = (p/'check-topological-v2.py').read_bytes()
assert old.replace(b"'set','ValueError','any'", b"'set','ValueError','TypeError','any'") == new
arms = ['Q007-goal-coding', 'Q008-goal-coding', 'Q009-production-quality', 'Q010-expanded-candidate', 'Q011-expanded-production', 'Q012-replay-candidate', 'Q013-replay-production', 'Q014-coupled-quality']
result = {'checker_v1_sha256':hashlib.sha256(old).hexdigest(), 'checker_v2_sha256':hashlib.sha256(new).hexdigest(), 'only_change':'Expose standard TypeError builtin; exact tests, AST restrictions, reference, seed, and scoring unchanged', 'new_inference_requests':0, 'arms':{}}
for arm in arms:
    checks = json.loads((p/arm/'checks.json').read_text())
    rows = []
    for c in checks:
        answer = p/arm/f"coding-{c['seed']}.answer.txt"
        r = dict(seed=c['seed'], finish_reason=c['finish_reason'], completion_tokens=c['completion_tokens'], original_passed=c['passed'], answer_sha256=hashlib.sha256(answer.read_bytes()).hexdigest())
        if c['finish_reason'] != 'stop':
            r.update(corrected_passed=False, reason='Natural-stop requirement still fails; no checker revision can clear output-cap failures')
        else:
            for key, checker in [('v1', 'check-topological.py'), ('v2', 'check-topological-v2.py'), ('normal_python_diagnostic', 'check-topological-normal-python-diagnostic.py')]:
                run = subprocess.run([sys.executable, '-I', str(p/checker), str(answer)], text=True, capture_output=True, timeout=5)
                r[key] = dict(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr)
                if run.returncode == 0:
                    assert json.loads(run.stdout) == {'passed':True, 'compiled':True, 'cases':72, 'test_seed':904001}
            assert (r['v1']['returncode']==0) == c['passed'], (arm,c['seed'])
            assert r['v2']['returncode'] == r['normal_python_diagnostic']['returncode'], (arm,c['seed'])
            r['corrected_passed'] = r['v2']['returncode']==0
        rows.append(r)
    result['arms'][arm] = {'original_passed_count':sum(r['original_passed'] for r in rows),'corrected_passed_count':sum(r['corrected_passed'] for r in rows),'count':len(rows),'rows':rows}
assert result['arms']['Q014-coupled-quality']['corrected_passed_count']==5
(p/'checker-v2-recheck.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({name:{k:v for k,v in info.items() if k!='rows'} for name,info in result['arms'].items()},indent=2))
