import concurrent.futures,csv,hashlib,importlib.util,json,subprocess,time,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
root=Path('C:/Strata');p=root/'local-setup/target-80';out=p/'deployment-c056';cfg=root/'strata-iq3_s.json'
spec=importlib.util.spec_from_file_location('memory_guard',p/'memory-guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
c=json.loads(cfg.read_text());record=json.loads((out/'deployment.json').read_text());sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(cfg)==record['deployed_config_sha256'] and sha(c['exe'])==record['engine_sha256']
def ps(s):
 r=subprocess.run(['powershell.exe','-NoProfile','-Command',s],capture_output=True,text=True,check=True);return json.loads(r.stdout)
def save(n,v):(out/n).write_text(json.dumps(v,indent=2)+'\n')
processes=ps("ConvertTo-Json -InputObject @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(strata|llama-|nsys|nvcc|cl\\.exe)' -or ($_.Name -match '^python' -and $_.CommandLine -match 'serve.server|goal90-benchmark') } | Select-Object ProcessId,Name)")
existing='--verify-existing' in sys.argv
assert existing or not processes,processes
log=Path(c['log']);offset=log.stat().st_size
safe=(out/'safety.csv').open('w',newline='');writer=csv.writer(safe);writer.writerow(['utc','physical_available','commit_available'])
def check():
 a,b=guard.memory_headroom();writer.writerow([datetime.now(timezone.utc).isoformat(),a,b]);safe.flush();guard.require_headroom(a,b)
def server(action):
 path=out/('server-'+action+'.txt')
 with path.open('w') as f:
  result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'local-setup/optimization-262k/server.ps1'),'-Action',action,'-Tag','deployment-c056'],stdout=f,stderr=subprocess.STDOUT,text=True,check=True)
 result.stdout=path.read_text();result.stderr='';return result
def get(path):
 with urlopen('http://127.0.0.1:8080'+path,timeout=3) as r:return json.load(r)
started=False
try:
 check();started=True
 if not existing:
  r=server('Start');(out/'start.txt').write_text(r.stdout+r.stderr)
 else:
  (out/'start.txt').write_text('Verified existing user-launcher instance after initial wrapper inherited an open output pipe; no second instance launched. Initial wrapper interrupted by exact PID before smoke request. Startup continuous memory monitoring was not obtained; initial safety sample retained.\n')
 t=time.monotonic()
 while True:
  check()
  try:
   health=get('/health')
   if health.get('loaded'):break
  except Exception:pass
  if time.monotonic()-t>600:raise RuntimeError('Startup timeout')
  time.sleep(1)
 models=get('/v1/models');props=get('/props')
 assert health['model']==c['model_name'] and health['max_context']==262144 and health['images']
 assert c['model_name'] in [m['id'] for m in models['data']]
 for key,value in c['sampling'].items():assert props['default_generation_settings']['params']['repeat_penalty' if key=='repetition_penalty' else key]==value,key
 engines=ps("ConvertTo-Json -InputObject @(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'strata*.exe' } | Select-Object ProcessId,Name,ExecutablePath,CommandLine)")
 match=[x for x in engines if x['ExecutablePath'].lower()==c['exe'].lower()];assert len(match)==1
 assert '262144' in match[0]['CommandLine'] and c['args'][c['args'].index('--native')+1].lower() in match[0]['CommandLine'].lower()
 assert len([x for x in engines if x['Name']=='strata-vision.exe'])==1
 listener=ps("Get-NetTCPConnection -LocalPort 8080 -State Listen | Select-Object LocalAddress,OwningProcess | ConvertTo-Json")
 assert listener['LocalAddress']=='0.0.0.0'
 startup=(root/'local-setup/optimization-262k/deployment-c056.stdout.log').read_text(errors='replace') if existing else log.read_bytes()[offset:].decode('utf-8',errors='replace')
 if existing:
  # The server stdout identifies this exact launch; engine markers are in the
  # cumulative engine log's final startup block, bounded after the last banner.
  engine_text=log.read_text(errors='replace')
  marker='strata mtp: coupled draft sampling on (STRATA_SPEC_COUPLED)'
  assert marker in engine_text
  startup=engine_text[engine_text.rfind('strata ',0,engine_text.rfind('prefix-bounded temporary KV staging enabled; full context retained')):]
 for marker in ['prefix-bounded temporary KV staging enabled; full context retained','accepted-row adaptive usage enabled (serial, committed inputs only)','coupled draft sampling on (STRATA_SPEC_COUPLED)','serial cache barrier every 64 accepted input tokens']:assert marker in startup,marker
 save('identity.json',{'engine_sha256':sha(c['exe']),'config_sha256':sha(cfg),'config':c,'engines':engines,'listener':listener,'health':health,'models':models,'props':props})
 payload={'model':c['model_name'],'messages':[{'role':'user','content':'What is 2 + 2? Return only the single digit.'}],'max_tokens':512,'stream':False,'seed':101,**json.loads((root/'local-setup/coding-best-practices/profile.json').read_text())}
 save('smoke.request.json',payload)
 def request():
  req=Request('http://127.0.0.1:8080/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
  with urlopen(req,timeout=120) as r:return json.load(r)
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  future=pool.submit(request)
  while not future.done():
   check();time.sleep(1)
  response=future.result()
 save('smoke.response.json',response)
 choice=response['choices'][0];content=choice['message'].get('content','').strip()
 assert content=='4' and choice['finish_reason']=='stop',(content,choice['finish_reason'])
 save('verification.json',{'passed':True,'checks':['exact C056 binary and R119 config','single text engine plus compatible vision process','keyless API and 0.0.0.0:8080 listener','262144 context and effective unchanged sampler','runtime optimization markers','high-thinking exact-answer smoke request stopped naturally'],'fresh_benchmark':False,'full_goal_qualification':False,'smoke_completion_tokens':response['usage']['completion_tokens'],'utc':datetime.now(timezone.utc).isoformat()})
 print('PASS C056 deployment identity, live defaults, keyless LAN listener, vision process and high-thinking exact-answer smoke',flush=True)
finally:
 if started:
  r=server('Stop');(out/'cleanup.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
 safe.close()
 assert sha(cfg)==record['deployed_config_sha256']
 if log.exists():(out/'engine-session.txt').write_bytes(log.read_bytes()[offset:])
