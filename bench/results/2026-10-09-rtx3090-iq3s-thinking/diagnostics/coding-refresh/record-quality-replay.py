"""Audit a bounded history-preserving replay, never a full-quality qualification."""
import argparse,csv,hashlib,json,re
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('arm',choices=['Q012-replay-candidate','Q013-replay-production']);parser.add_argument('checkpoint');args=parser.parse_args()
p=Path(__file__).parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking';arm=p/args.arm
source='Q010-expanded-candidate' if args.arm.startswith('Q012') else 'Q011-expanded-production'
expected=json.loads((p/source/'identity.json').read_text());identity=json.loads((arm/'identity.json').read_text())
summary=json.loads((arm/'summary.json').read_text());checks=json.loads((arm/'checks.json').read_text());rows=json.loads((arm/'runs.json').read_text())
assert len(checks)==len(rows)==3 and [r['seed'] for r in checks]==[101,102,103]
assert summary['diagnostic_only'] and not summary['full_quality_qualified'] and summary['focus_seed']==103
assert identity['contract']['max_tokens']==32768 and identity['contract']['diagnostic_only']
for key in ['engine_sha256','vision_sha256','backend_library_sha256','config_sha256','expert_profile_sha256','fixture_sha256']:
    assert identity[key]==expected[key],key
profile=json.loads((p.parent/'coding-best-practices/profile.json').read_text());assert summary['sampling']==profile
payload_checks=[]
for check,row in zip(checks,rows):
    seed=check['seed'];name=f'coding-{seed}.request.json';raw=(arm/name).read_bytes()
    assert raw==(p/source/name).read_bytes(),name
    payload=json.loads(raw);assert payload['max_tokens']==32768 and all(payload.get(k)==v for k,v in profile.items())
    assert row['seed']==seed and row['completion_tokens']==check['completion_tokens']<=32768
    assert row['finish_reason']==check['finish_reason'] and row['cache_valid'] and row['cached_tokens']==0
    if check['passed']:
        assert check['finish_reason']=='stop' and check['returncode']==0
        result=json.loads(check['stdout']);assert result['compiled'] and result['passed'] and result['cases']==72
    payload_checks.append({'seed':seed,'byte_identical_to_original_expanded_suite':True,'request_sha256':hashlib.sha256(raw).hexdigest()})
assert summary['passed']==all(c['passed'] for c in checks)
wrapper=(p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text();assert 'Cleanup verified: no live Strata' in wrapper
assert hashlib.sha256((root/'strata-iq3_s.json').read_bytes()).hexdigest()=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
safe=list(csv.DictReader((arm/'safety.csv').open()));memory={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']};assert min(memory.values())>=16*2**30
result={'arm':args.arm,'source_configuration':source,'diagnostic_only':True,'full_quality_qualified':False,'speed_qualification':False,'passed_count':sum(c['passed'] for c in checks),'checks':checks,'request_identity':payload_checks,'minimum_memory_bytes':memory,'focus_seed_103_completed':checks[-1]['passed'],'prior_failures_preserved':True}
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
dest=pub/'diagnostics/coding-refresh'/args.arm;put(dest/'audit.json',json.dumps(result,indent=2)+'\n')
for name in ['supervisor.py','goal90-quality-replay.py','check-topological.py','engine-session.txt','safety.csv','observer.json','observer-audit.json','effective-sampling-modes.json','client-command.json','client-log.txt','checks.json','summary.json']:
    f=arm/name if (arm/name).exists() else p/name;put(dest/name,f.read_text(encoding='utf-8'))
put(dest/'wrapper.txt',wrapper)
for seed in range(101,104):
    name=f'coding-{seed}.answer.txt';put(dest/name,(arm/name).read_text(encoding='utf-8'))
note=f'## {args.checkpoint} / {args.arm} bounded replay\n\n'
for c in checks:note+=f"Seed{c['seed']}: {c['completion_tokens']}tokens, finish{c['finish_reason']}, passed={c['passed']}; "+(c.get('stdout') or c.get('error','')).strip()+'\n\n'
note+=f"Diagnostic count{result['passed_count']}/3; not full quality qualification. Requests byte-identical to{source}, run101/102/103 in original order from a fresh process. No warmup. Same32768 cap, profile, tests, binaries/libraries/config/model/vision identity. Generated histories may differ; cache tensors are not claimed identical. Prior failures are never replaced.\n\n"
note+=f"Minimum physical{memory['physical_available']} and commit{memory['commit_available']}bytes;16GiB floors pass. Exact cleanup verified; production3457fdfe restored. No promotion.\n"
put(dest/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(encoding='utf-8');assert '## '+args.checkpoint+' /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint=args.checkpoint,current=f"{args.arm} complete: diagnosis{result['passed_count']}/3; original full-quality gate unchanged.",resume_command=f'{args.arm} complete with verified cleanup. No model resident. Inspect current ledger before next arm.');v.setdefault('replay_diagnostics',{})[args.arm]=result['passed_count'];put(f,json.dumps(v,indent=2)+'\n')
print(json.dumps(result,indent=2))
