import argparse,csv,hashlib,json,re
from pathlib import Path
a=argparse.ArgumentParser();a.add_argument('arm');a.add_argument('checkpoint');args=a.parse_args()
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking';arm=p/args.arm
ident=json.loads((arm/'identity.json').read_text());rows=json.loads((arm/'runs.json').read_text());summary=json.loads((arm/'summary.json').read_text());declared=json.loads((p/'C062-summary.json').read_text())
assert ident['engine_sha256']==declared['engine_sha256'];assert ident['configuration_unchanged'];assert ident['config']==json.loads((p/(args.arm+'.json')).read_text())
assert ident['fixture_sha256']==hashlib.sha256((p/'goal90-coding-fixture.json').read_bytes()).hexdigest()
assert len(rows)==24 and len(summary)==4 and all(v['runs']==5 for v in summary.values())
profile=json.loads((p.parent/'coding-best-practices/profile.json').read_text());requests=list(arm.glob('*.request.json'));assert len(requests)==24
for f in requests:
 payload=json.loads(f.read_text());assert payload['max_tokens']==512 and payload['stream'];assert all(payload.get(k)==v for k,v in profile.items())
for size in ['short','longer']:
 for run in range(6):
  stem=size+'-'+('warmup' if run==0 else f'run-{run}');assert (arm/(stem+'-new.request.json')).read_bytes()==(arm/(stem+'-hit.request.json')).read_bytes()
passed=all(r['completion_tokens']==512 and r['cache_valid'] and (r['cached_tokens']>0 if r['cache_expected']=='hit' else r['cached_tokens']==0) for r in rows)
wrapper=(p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text();assert 'Cleanup verified: no live Strata' in wrapper
assert hashlib.sha256((root/'strata-iq3_s.json').read_bytes()).hexdigest()=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
safe=list(csv.DictReader((arm/'safety.csv').open()));memory={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']};assert min(memory.values())>=16*2**30
marker='shared scale-only fusion captured (CUDA K10 T2..8)';active=marker in (arm/'engine-session.txt').read_text();requested=ident['config']['env']['STRATA_SHARED_SCALE_FUSE']=='1';assert active==requested
result={'arm':args.arm,'summary':summary,'cache_length_pass':passed,'capture_marker':active,'minimum_memory_bytes':memory,'full_qualification':False,'engine_sha256':ident['engine_sha256']}
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>');f.write_text('\n'.join(x.rstrip() for x in s.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/shared-scale-fusion/C062'/args.arm;put(d/'audit.json',json.dumps(result,indent=2))
for name in ['engine-session.txt','safety.csv','observer.json','observer-audit.json','effective-sampling-modes.json','client-command.json','supervisor.py']:put(d/name,(arm/name).read_text())
put(d/'wrapper.txt',wrapper)
note=f'## {args.checkpoint} / {args.arm} complete\n\n'
for w,s in summary.items():
 g=[r for r in rows if r['workload']==w and not r['warmup']];note+=f"{w}: all decode values{[r['server_decode_tps'] for r in g]}, ordinary median{s['server_decode_tps']['median']}; prompt{s['prompt_tps']['median']}; client E2E{s['request_e2e_tps']['median']:.6f}; TTFT{s['ttft_seconds']}; stream-total{s['stream_total_tps']}. Fresh/cached counts{[(r['fresh_prompt_tokens'],r['cached_tokens']) for r in g]}.\n\n"
note+=f'All24 requests retained,20 measured and4 warmups. Cache/512length gate={passed}. Same declared binary/config/fixture and fixed sampler verified. Actual capture marker={active}, matching requested flag. Minimum memory bytes{memory}, both16GiB floors pass. Exact cleanup and production config restoration verified. Capped responses do not replace completed-answer quality. No individual-arm promotion or full-goal claim; complete the declared ABBA sequence and assess all pooled medians.\n'
put(d/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text();assert '## '+args.checkpoint+' /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint=args.checkpoint,current=args.arm+' complete; continue fixed R132-R135 comparison.',next=['Finish predeclared arms once and pool all runs; no launcher changes.']);put(f,json.dumps(s,indent=2))
print(json.dumps({'arm':args.arm,'cache_length_pass':passed,'medians':{w:s['server_decode_tps']['median'] for w,s in summary.items()},'memory':memory},indent=2))
