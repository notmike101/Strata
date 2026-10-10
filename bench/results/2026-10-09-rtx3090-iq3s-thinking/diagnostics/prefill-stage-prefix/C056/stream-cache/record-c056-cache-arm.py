"""Archive a complete new/exact-repeat arm, including any failed cache/length gate."""
import argparse,csv,hashlib,json,re
from pathlib import Path
a=argparse.ArgumentParser(); a.add_argument('arm'); a.add_argument('checkpoint'); a.add_argument('--next',required=True); args=a.parse_args()
p=Path(__file__).parent; root=p.parents[1]; pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'; arm=p/args.arm
ident=json.loads((arm/'identity.json').read_text()); rows=json.loads((arm/'runs.json').read_text()); summary=json.loads((arm/'summary.json').read_text())
assert ident['engine_sha256']=='cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91'
assert ident['fixture_sha256']==hashlib.sha256((p/'goal90-coding-fixture.json').read_bytes()).hexdigest()
assert ident['contract']['cache_hits_requested'] and ident['contract']['max_tokens']==512
assert ident['configuration_unchanged']
mode='stream' if ident['contract']['stream'] else 'nonstream'
expected=json.loads((p/('R119-prefix-preserve.json' if ident['config']['env']['STRATA_PREFILL_STAGE_PREFIX']=='1' else 'R118-preserve-control.json')).read_text())
assert ident['config']==expected
anchor=json.loads((p/'R119-prefix-preserve/identity.json').read_text())
assert ident['backend_library_sha256']==anchor['backend_library_sha256']
assert len(rows)==24 and len(summary)==4 and all(v['runs']==5 for v in summary.values())
profile=json.loads((p.parent/'coding-best-practices/profile.json').read_text())
requests=list(arm.glob('*.request.json')); assert len(requests)==24
for f in requests:
    payload=json.loads(f.read_text()); assert payload['max_tokens']==512 and payload['stream']==(mode=='stream')
    assert all(payload.get(k)==v for k,v in profile.items()),f
for size in ['short','longer']:
    for run in range(6):
        stem=size+'-'+('warmup' if run==0 else f'run-{run}')
        assert (arm/(stem+'-new.request.json')).read_bytes()==(arm/(stem+'-hit.request.json')).read_bytes()
cache_length_ok=all(r['completion_tokens']==512 and r['cache_valid'] and
    (r['cached_tokens']>0 if r['cache_expected']=='hit' else r['cached_tokens']==0) for r in rows)
wrapper=(p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text(); assert 'Cleanup verified: no live Strata' in wrapper
assert hashlib.sha256((root/'strata-iq3_s.json').read_bytes()).hexdigest()=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
safe=list(csv.DictReader((arm/'safety.csv').open())); memory={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']}; assert min(memory.values())>=16*2**30
cache_counts={w:[{'seed':r['seed'],'fresh':r['fresh_prompt_tokens'],'cached':r['cached_tokens'],'total':r['prompt_tokens']} for r in rows if r['workload']==w and not r['warmup']] for w in summary}
result={'arm':args.arm,'mode':mode,'summary':summary,'cache_and_length_pass':cache_length_ok,'cache_counts':cache_counts,'minimum_memory_bytes':memory,'full_qualification':False,'fixture_sha256':ident['fixture_sha256'],'engine_sha256':ident['engine_sha256']}
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/cache-matrix'/args.arm; put(d/'audit.json',json.dumps(result,indent=2)+'\n')
for n in ['engine-session.txt','safety.csv','observer.json','observer-audit.json','effective-sampling-modes.json','client-command.json','supervisor.py']:
    put(d/n,(arm/n).read_text())
put(d/'wrapper.txt',wrapper)
note=f'## {args.checkpoint} / {args.arm} exact-repeat matrix arm\n\n'
for w,s in summary.items():
    g=[r for r in rows if r['workload']==w and not r['warmup']]
    note+=f"{w}: raw decode{[r['server_decode_tps'] for r in g]}, ordinary median{s['server_decode_tps']['median']}; prompt{s['prompt_tps']['median']}, E2E{s['request_e2e_tps']['median']:.6f}, stream={s['stream_total_tps']}, TTFT={s['ttft_seconds']}. Fresh/cached counts{[(r['fresh_prompt_tokens'],r['cached_tokens']) for r in g]}.\n\n"
note+=f"All24request payloads retain fixed profile/512cap, and each new/hit pair is byte-identical. One excluded warmup and five measured runs per cell. Cache/length gate={cache_length_ok}; failures, if any, are retained. Interleaved misses stay separate from the closed pure-miss comparison. Candidate/control config, binary and loaded-library identity checks passed. No completed-answer quality or full goal claim from capped responses.\n\nMinimum physical{memory['physical_available']} and commit{memory['commit_available']}bytes;16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.\n\nNext: {args.next}\n"
put(d/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## '+args.checkpoint+' /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint=args.checkpoint,current=args.arm+f' complete; cache/length gate={cache_length_ok}; full qualification pending.',next=[args.next]); put(f,json.dumps(s,indent=2)+'\n')
print(json.dumps({'arm':args.arm,'cache_and_length_pass':cache_length_ok,'medians':{w:s['server_decode_tps']['median'] for w,s in summary.items()},'minimum_memory_bytes':memory},indent=2))
