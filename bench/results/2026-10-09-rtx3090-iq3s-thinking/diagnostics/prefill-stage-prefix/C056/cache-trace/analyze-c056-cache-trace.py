"""Parse existing per-request trace markers; diagnostic statistics only."""
import argparse,collections,hashlib,json,re,statistics,csv
from pathlib import Path
a=argparse.ArgumentParser(); a.add_argument('arm'); a.add_argument('checkpoint'); args=a.parse_args()
p=Path(__file__).parent; d=p/args.arm; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
rows=json.loads((d/'runs.json').read_text()); ident=json.loads((d/'identity.json').read_text())
assert len(rows)==24 and all(r['completion_tokens']==512 and r['cache_valid'] for r in rows)
assert ident['engine_sha256']=='cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91'
cfg=json.loads(json.dumps(ident['config'])); assert cfg['env'].pop('STRATA_TRACE')=='1'
assert cfg==json.loads((p/('R119-prefix-preserve.json' if cfg['env']['STRATA_PREFILL_STAGE_PREFIX']=='1' else 'R118-preserve-control.json')).read_text())
assert ident['configuration_unchanged']
text=(d/'engine-session.txt').read_text(); starts=list(re.finditer(r'^strata trace: request (\d+) (-?\d+)',text,re.M)); assert len(starts)==24
out=[]
for i,(start,r) in enumerate(zip(starts,rows)):
    b=text[start.start():starts[i+1].start() if i+1<len(starts) else len(text)]
    assert int(start[1])==r['prompt_tokens']
    windows=[(int(x),int(y)) for x,y in re.findall(r'^strata trace: window (\d+) (\d+)',b,re.M)]
    reads=[(int(n),kind,float(ms)) for n,kind,ms in re.findall(r'^strata trace: read (\d+) tokens \((batched|windows)\) in ([\d.]+) ms',b,re.M)]
    loans=[(int(n),int(t),float(ms)) for n,t,ms in re.findall(r'^strata trace: lent (\d+) slots for (\d+) tokens in ([\d.]+) ms',b,re.M)]
    refills=[(int(n),int(st),float(ms)) for n,st,ms in re.findall(r'^strata trace: refilled (\d+) slots on (\d+) stage\(s\) in ([\d.]+) ms',b,re.M)]
    assert windows and reads
    entry={'label':r['label'],'workload':r['workload'],'warmup':r['warmup'],'seed':r['seed'],'prompt_tokens':r['prompt_tokens'],'fresh_prompt_tokens':r['fresh_prompt_tokens'],'cached_tokens':r['cached_tokens'],'server_prompt_ms':r['timings']['prompt_ms'],'server_decode_ms':r['timings']['predicted_ms'],'server_decode_tps':r['server_decode_tps'],'request_e2e_tps':r['request_e2e_tps'],'ttft_seconds':r['ttft_seconds'],'windows':windows,'window_width_counts':dict(sorted(collections.Counter(w for pos,w in windows).items())),'window_count':len(windows),'verified_rows':sum(w for pos,w in windows),'mean_ms_per_window':r['timings']['predicted_ms']/len(windows),'read_parts':reads,'loans':loans,'refills':refills,'logical_lent_slots':sum(n for n,t,ms in loans),'physical_refilled_slots':sum(n for n,st,ms in refills),'loan_ms':sum(ms for n,t,ms in loans),'refill_ms':sum(ms for n,st,ms in refills),'batched_read_ms':sum(ms for n,k,ms in reads if k=='batched'),'window_read_ms':sum(ms for n,k,ms in reads if k=='windows'),'draft_offered':r['timings']['draft_n'],'draft_accepted':r['timings']['draft_n_accepted']}
    out.append(entry)
summary={}
for w in sorted({r['workload'] for r in out}):
    g=[r for r in out if r['workload']==w and not r['warmup']]; assert len(g)==5
    summary[w]={k:{'raw':[r[k] for r in g],'median':statistics.median(r[k] for r in g)} for k in ['server_prompt_ms','server_decode_ms','window_count','verified_rows','mean_ms_per_window','logical_lent_slots','physical_refilled_slots','loan_ms','refill_ms','batched_read_ms','window_read_ms','draft_offered','draft_accepted']}
wrapper=(p/(args.arm.split('-')[0]+'-wrapper.txt')).read_text(); assert 'Cleanup verified: no live Strata' in wrapper
assert hashlib.sha256((p.parents[1]/'strata-iq3_s.json').read_bytes()).hexdigest()=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
safe=list(csv.DictReader((d/'safety.csv').open())); floors={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']}; assert min(floors.values())>=16*2**30
result={'authoritative_tps':False,'arm':args.arm,'rows':out,'summary':summary,'memory_floor_bytes':floors,'configuration_verified':True,'cleanup_verified':True}
(d/'trace-stages.json').write_text(json.dumps(result,indent=2)+'\n')
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True); f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
dest=pub/'diagnostics/prefill-stage-prefix/C056/cache-trace'/args.arm
for n in ['trace-stages.json','engine-session.txt','identity.json','safety.csv','supervisor.py','observer.json','observer-audit.json','client-command.json','effective-sampling-modes.json']:
    put(dest/n,(d/n).read_text())
put(dest/'wrapper.txt',wrapper); put(dest/'analyze-c056-cache-trace.py',Path(__file__).read_text())
note=f'## {args.checkpoint} / {args.arm} trace captured\n\n'
for w,s in summary.items():
    note+=w+': medians '+', '.join(f"{k}={v['median']}" for k,v in s.items())+'.\n\n'
note+=f'All24requests retain512tokens and valid new/repeat reuse. Same C056 engine/config plus declared trace switch. Trace timings are diagnostic only, not qualifying repeats. All window positions/widths, prompt pieces, logical loans, physical refills, acceptance and raw timing values retained. Minimum memory bytes{floors};16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.\n'
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## '+args.checkpoint+' /' not in s; put(f,s+'\n\n'+note)
put(dest/'README.md',note)
print(json.dumps({w:{k:v['median'] for k,v in s.items()} for w,s in summary.items()},indent=2))
