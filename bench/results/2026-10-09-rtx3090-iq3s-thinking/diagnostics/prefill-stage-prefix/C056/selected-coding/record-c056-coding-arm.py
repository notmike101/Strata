"""Record a complete fixed-fixture coding baseline, never a quality pass."""
import argparse,csv,hashlib,json,re
from pathlib import Path
a=argparse.ArgumentParser();a.add_argument('arm');a.add_argument('checkpoint');a.add_argument('--next',required=True);args=a.parse_args()
p=Path(__file__).parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking';arm=p/args.arm
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
ident=json.loads((arm/'identity.json').read_text());rows=json.loads((arm/'runs.json').read_text());summary=json.loads((arm/'summary.json').read_text())
assert ident['engine_sha256']=='cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91'
assert ident['fixture_sha256']==hashlib.sha256((p/'goal90-coding-fixture.json').read_bytes()).hexdigest()
assert len(rows)==12 and all(r['completion_tokens']==512 and r['cached_tokens']==0 and r['cache_valid'] for r in rows)
assert len(summary)==2 and all(v['runs']==5 for v in summary.values())
profile=json.loads((p.parent/'coding-best-practices/profile.json').read_text())
requests=list(arm.glob('*.request.json'));assert len(requests)==12
for f in requests:
    payload=json.loads(f.read_text());assert payload['max_tokens']==512
    assert all(payload.get(k)==v for k,v in profile.items()), f
assert 'Cleanup verified: no live Strata' in (p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text()
safe=list(csv.DictReader((arm/'safety.csv').open()));memory={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']};assert min(memory.values())>=16*2**30
result={'summary':summary,'minimum_memory_bytes':memory,'quality_qualified':False,'fixture_sha256':ident['fixture_sha256'],'engine_sha256':ident['engine_sha256']}
d=pub/'diagnostics/coding-refresh'/args.arm
put(d/'audit.json',json.dumps(result,indent=2)+'\n')
for f in ['engine-session.txt','safety.csv','observer.json','observer-audit.json','effective-sampling-modes.json','client-command.json','supervisor.py']:
    put(d/f,(arm/f).read_text(encoding='utf-8'))
put(d/'wrapper.txt',(p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text())
lines=[]
for w,s in summary.items():
    rr=[r for r in rows if r['workload']==w and not r['warmup']]
    lines.append(f"{w}: decode{[r['server_decode_tps'] for r in rr]} => ordinary median{s['server_decode_tps']['median']}; prompt{s['prompt_tps']['median']}, E2E{s['request_e2e_tps']['median']:.6f}, stream{s['stream_total_tps']['median']:.6f}, TTFT{s['ttft_seconds']['median']:.6f}s.")
note=f"## {args.checkpoint} / {args.arm} frozen coding matrix arm\n\n"+'\n\n'.join(lines)+f"\n\nAll12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture{ident['fixture_sha256']}, C056 engine{ident['engine_sha256']}. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.\n\nMinimum physical{memory['physical_available']} and commit{memory['commit_available']}bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.\n\nNext: {args.next}\n"
put(d/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    old=f.read_text(encoding='utf-8');assert '## '+args.checkpoint+' /' not in old;put(f,old+'\n\n'+note)
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint=args.checkpoint,current=args.arm+' complete; not full qualification.',next=[args.next]);put(f,json.dumps(v,indent=2)+'\n')
print(json.dumps(result,indent=2))
