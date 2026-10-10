from pathlib import Path
import json,statistics,re
p=Path(__file__).parent
arms=['R098-conditional0','R099-conditional64']
if (p/'R100-conditional64/summary.json').exists():arms+=['R100-conditional64','R101-conditional0']
ident=[json.loads((p/a/'identity.json').read_text(encoding='utf-8')) for a in arms]
for arm,i in zip(arms,ident):
 assert i['engine_sha256']=='ac43e89822e4febce9a2e3ae93a786eaa705bdc61f04ba28302ee50c64bb87c3'
 assert i['backend_library_sha256']==ident[0]['backend_library_sha256']
 config=json.loads(json.dumps(i['config']));control=json.loads(json.dumps(ident[0]['config']))
 for c in [config,control]:c['env'].pop('STRATA_SERIAL_ADAPT_TOKENS')
 assert config==control
 for f in (p/arms[0]).glob('*.request.json'):assert f.read_bytes()==(p/arm/f.name).read_bytes()
results={}
for mode in ['conditional0','conditional64']:
 rows=[];costs=[];policies=[]
 for arm in arms:
  if not arm.endswith(mode):continue
  rr=json.loads((p/arm/'runs.json').read_text(encoding='utf-8'));assert len(rr)==12
  assert all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in rr)
  rows+=rr
  log=(p/arm/'engine-session.txt').read_text(encoding='utf-8')
  bs=re.findall(r'strata serial cache barriers: (\d+) updates, ([\d.]+) ms total',log)
  ps=[(int(n),int(t)) for n,t in re.findall(r'strata serial cache policy: (\d+) fresh prompt tokens, interval (\d+)',log)]
  if mode=='conditional64':
   assert len(bs)==6 and all(int(n)==7 for n,_ in bs)
   assert len(ps)==12
   for row,(n,t) in zip(rr,ps):assert n==row['prompt_tokens'] and t==(64 if n>=1025 else 0)
  else:assert not bs and not ps
  policies += [{'arm':arm,'fresh_tokens':n,'interval':t} for n,t in ps]
  costs += [{'arm':arm,'updates':int(n),'milliseconds':float(ms)} for n,ms in bs]
 result={'policy_activation':policies,'barrier_costs':costs,'workloads':{}}
 for w in ['short','longer']:
  rr=[r for r in rows if not r['warmup'] and r['workload']==w]
  result['workloads'][w]={'runs':len(rr),'metrics':{k:{'median':statistics.median(r[k] for r in rr),'raw':[r[k] for r in rr]} for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds']}}
 results[mode]=result
delta={w:{k:100*(results['conditional64']['workloads'][w]['metrics'][k]['median']/results['conditional0']['workloads'][w]['metrics'][k]['median']-1) for k in ['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds']} for w in ['short','longer']}
stop=any(d['server_decode_tps'] < -3 or d['request_e2e_tps'] < -3 or d['prompt_tps'] < -2 for d in delta.values())
result={'arms':arms,'results':results,'percent_change_on_vs_off':delta,'screening_stop':stop,'goal_qualified':False,'quality_qualified':False}
dest=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking/diagnostics/combinations/C049/summary.json');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'percent_change':delta,'screening_stop':stop,'medians':{k:{w:{m:v['median'] for m,v in c['metrics'].items()} for w,c in d['workloads'].items()} for k,d in results.items()}},indent=2))
