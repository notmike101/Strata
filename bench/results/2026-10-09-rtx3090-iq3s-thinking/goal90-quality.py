"""Use the same identity guards and selected problem with a natural-stop cap."""
from pathlib import Path
source=Path(__file__).with_name('goal90-benchmark.py').read_text(encoding='utf-8')
exec(compile(source.split("for size in (")[0],str(Path(__file__).with_name('goal90-benchmark.py')),'exec'))
assert fixture['selected']=='topological_order'
manifest['contract']['max_tokens']=8192
manifest['contract']['purpose']='Completed-answer quality; excluded from 512-token throughput target'
save('identity.json',manifest)
checks=[]
for seed in range(101,106):
    label=f'coding-{seed}'
    payload=dict(model=CONFIG['model_name'],messages=[dict(role='user',content=f'Validation identifier {seed}. Ignore this identifier.\n'+fixture['task'])],
                 max_tokens=8192,stream=True,seed=seed,**PROFILE)
    ask(label,payload,'quality/coding',False,'miss')
    row=rows[-1]
    outcome={'seed':seed,'finish_reason':row['finish_reason'],'completion_tokens':row['completion_tokens']}
    try:
        assert row['finish_reason']=='stop','Did not stop naturally'
        result=subprocess.run([str(ROOT/'.venv/Scripts/python.exe'),'-I',str(Path(__file__).with_name('check-topological.py')),str(OUT/(label+'.answer.txt'))],
                              text=True,capture_output=True,timeout=5)
        outcome.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,passed=result.returncode==0)
    except Exception as error:outcome.update(passed=False,error=str(error))
    checks.append(outcome); save('checks.json',checks); print('CHECK '+json.dumps(outcome),flush=True)
save('summary.json',dict(passed=all(c['passed'] for c in checks),checks=checks,task=fixture['selected'],sampling=PROFILE))
