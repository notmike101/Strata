from pathlib import Path
import json, statistics, re
p=Path(__file__).parent
arms=['R094-barrier0','R095-barrier64']
if (p/'R096-barrier64/summary.json').exists(): arms+=['R096-barrier64','R097-barrier0']
ident=[json.loads((p/a/'identity.json').read_text(encoding='utf-8')) for a in arms]
control=ident[0]['config']
for a,i in zip(arms,ident):
 assert i['engine_sha256']=='c9508334047d378f2e4f5a7dd128e90064023effb2d12bf884d96520379855b4'
 assert i['backend_library_sha256']==ident[0]['backend_library_sha256']
 c=json.loads(json.dumps(i['config']));ref=json.loads(json.dumps(control))
 for x in [c,ref]:x['env'].pop('STRATA_SERIAL_ADAPT_TOKENS')
 assert c==ref
 for f in (p/arms[0]).glob('*.request.json'):assert f.read_bytes()==(p/a/f.name).read_bytes()
results={}
for mode in ['barrier0','barrier64']:
 rows=[];logs=[]
 for arm in arms:
  if arm.endswith(mode):
   rr=json.loads((p/arm/'runs.json').read_text(encoding='utf-8'))
   assert len(rr)==12 and all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in rr)
   rows+=rr
   trace=(p/arm/'engine-session.txt').read_text(encoding='utf-8')
   bs=re.findall(r'strata serial cache barriers: (\d+) updates, ([\d.]+) ms total',trace)
   if mode=='barrier64': assert len(bs)==12 and all(int(n)==7 for n,_ in bs)
   else:assert not bs
   logs += [{'arm':arm,'updates':int(n),'milliseconds':float(ms)} for n,ms in bs]
 result={'barrier_costs':logs,'workloads':{}}
 for w in ['short','longer']:
  rr=[r for r in rows if not r['warmup'] and r['workload']==w]
  result['workloads'][w]={'runs':len(rr),'metrics':{k:{'median':statistics.median(r[k] for r in rr),'raw':[r[k] for r in rr]} for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds']}}
 results[mode]=result
delta={w:{k:100*(results['barrier64']['workloads'][w]['metrics'][k]['median']/results['barrier0']['workloads'][w]['metrics'][k]['median']-1) for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds']} for w in ['short','longer']}
stop=any(d['server_decode_tps'] < -3 or d['request_e2e_tps'] < -3 or d['prompt_tps'] < -2 for d in delta.values())
result={'arms':arms,'results':results,'percent_change_on_vs_off':delta,'screening_stop':stop,'goal_qualified':False,'quality_qualified':False}
dest=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking/diagnostics/combinations/C048/summary.json')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'percent_change':delta,'screening_stop':stop,'medians':{k:{w:{m:v['median'] for m,v in c['metrics'].items()} for w,c in d['workloads'].items()} for k,d in results.items()}},indent=2))
