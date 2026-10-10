"""Record approved 32768-token quality suites; never count them as speed runs."""
import argparse,csv,hashlib,json,re
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('arm',choices=['Q015-prefix-preserve-quality']);parser.add_argument('checkpoint');args=parser.parse_args()
p=Path(__file__).parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking';arm=p/args.arm
source='R119-prefix-preserve'
expected=json.loads((p/source/'identity.json').read_text());identity=json.loads((arm/'identity.json').read_text())
summary=json.loads((arm/'summary.json').read_text());checks=json.loads((arm/'checks.json').read_text());rows=json.loads((arm/'runs.json').read_text())
assert len(checks)==len(rows)==5 and [r['seed'] for r in checks]==list(range(101,106))
assert identity['contract']['max_tokens']==32768
assert identity['contract']['quality_checker_sha256']==hashlib.sha256((arm/'check-topological-v2.py').read_bytes()).hexdigest()
assert (arm/'check-topological-v2.py').read_bytes()==(p/'check-topological-v2.py').read_bytes()
assert identity['contract']['warmup']=='No quality warmup; all five seeds assessed'
for key in ['engine_sha256','vision_sha256','backend_library_sha256','config_sha256','expert_profile_sha256']:
    assert identity[key]==expected[key],key
assert identity['fixture_sha256']==json.loads((p/'Q011-expanded-production'/'identity.json').read_text())['fixture_sha256']
assert identity['config']['env']['STRATA_SPEC_COUPLED']=='1' and identity['config']['env']['STRATA_SPEC_GUMBEL']=='1'
assert identity['config']['env']['STRATA_SPEC_PROB']=='0'
profile=json.loads((p.parent/'coding-best-practices/profile.json').read_text());assert summary['sampling']==profile
payload_checks=[]
for check,row in zip(checks,rows):
    seed=check['seed'];name=f'coding-{seed}.request.json'
    payload=json.loads((arm/name).read_text());original=json.loads((p/'Q007-goal-coding'/name).read_text());assert original['max_tokens']==8192
    original['max_tokens']=32768;assert payload==original
    assert all(payload.get(k)==v for k,v in profile.items())
    assert row['seed']==seed and row['completion_tokens']==check['completion_tokens']<=32768
    assert row['finish_reason']==check['finish_reason'] and row['cache_valid'] and row['cached_tokens']==0
    if check['passed']:
        assert check['finish_reason']=='stop' and check['returncode']==0
        result=json.loads(check['stdout']);assert result['compiled'] and result['passed'] and result['cases']==72
        assert (arm/f'coding-{seed}.answer.txt').read_text(encoding='utf-8').strip()
    payload_checks.append({'seed':seed,'matches_original_except_approved_cap':True,'request_sha256':hashlib.sha256((arm/name).read_bytes()).hexdigest()})
assert summary['passed']==all(c['passed'] for c in checks)
wrapper=(p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text();assert 'Cleanup verified: no live Strata' in wrapper
assert hashlib.sha256((root/'strata-iq3_s.json').read_bytes()).hexdigest()=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
safe=list(csv.DictReader((arm/'safety.csv').open()));memory={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']};assert min(memory.values())>=16*2**30
result={'arm':args.arm,'source_configuration':source,'quality_passed':summary['passed'],'passed_count':sum(c['passed'] for c in checks),'checks':checks,'request_identity':payload_checks,'minimum_memory_bytes':memory,'speed_qualification':False,'quality_cap':32768,'legacy_failures_preserved':True}
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
dest=pub/'diagnostics/coding-refresh'/args.arm;put(dest/'audit.json',json.dumps(result,indent=2)+'\n')
for name in ['supervisor.py','goal90-quality-expanded-v2.py','check-topological-v2.py','engine-session.txt','safety.csv','observer.json','observer-audit.json','effective-sampling-modes.json','client-command.json','client-log.txt','checks.json','summary.json']:
    f=arm/name if (arm/name).exists() else p/name;put(dest/name,f.read_text(encoding='utf-8'))
put(dest/'wrapper.txt',wrapper)
for seed in range(101,106):
    name=f'coding-{seed}.answer.txt';put(dest/name,(arm/name).read_text(encoding='utf-8'))
note=f'## {args.checkpoint} / {args.arm} approved expanded quality\n\n'
for c in checks:note+=f"Seed{c['seed']}: {c['completion_tokens']}tokens, finish{c['finish_reason']}, passed={c['passed']}; "+(c.get('stdout') or c.get('error') or c.get('stderr','')).strip()+'\n\n'
note+=f"Pass count{result['passed_count']}/5 with user-approved32768 cap. All five requests equal the originalQ007 requests except max_tokens. Configuration, executable, libraries, expert profile and vision hashes match{source}; fixture hash matchesQ011. Natural-stop passing answers compile and pass72tests each. Zero prompt reuse. Legacy8192 failures remain unchanged. Variable-length quality answers do not satisfy the512-token speed target.\n\n"
note+=f"Minimum physical{memory['physical_available']} and commit{memory['commit_available']}bytes;16GiB floors pass. Exact cleanup verified and production3457fdfe restored. No promotion; other workload, stability and real-use requirements remain.\n"
put(dest/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(encoding='utf-8');assert '## '+args.checkpoint+' /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint=args.checkpoint,current=f"{args.arm} complete: expanded quality{result['passed_count']}/5; no full goal qualification.",resume_command=f'{args.arm} complete with verified cleanup. No model resident. Inspect current ledger before next arm.');v.setdefault('expanded_quality_results',{})[args.arm]=result['passed_count'];put(f,json.dumps(v,indent=2)+'\n')
print(json.dumps(result,indent=2))
