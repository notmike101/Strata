from pathlib import Path
import json, os, subprocess
p=Path(__file__).parent
c=json.loads((p/'R095-barrier64.json').read_text(encoding='utf-8'))
env=os.environ.copy();env.update(c['env']);env['PATH']=';'.join(c['lib_dirs'])+';'+env['PATH']
cases=[('missing accepted usage',{'STRATA_ACCEPTED_USAGE':'0'},[]),
       ('negative',{'STRATA_SERIAL_ADAPT_TOKENS':'-1'},[]),
       ('malformed',{'STRATA_SERIAL_ADAPT_TOKENS':'64x'},[]),
       ('over context',{'STRATA_SERIAL_ADAPT_TOKENS':'262145'},[]),
       ('overflow',{'STRATA_SERIAL_ADAPT_TOKENS':'99999999999999999999999999'},[]),
       ('batch',{},['--batch','1']),('async',{},['--adapt-async','1']),('no pool',{},['--no-pool'])]
results=[]
for label,updates,args in cases:
 e=env.copy();e.update(updates)
 r=subprocess.run([c['exe'],'--serve',*c['args'],*args],env=e,capture_output=True,text=True,timeout=20)
 assert r.returncode==2,(label,r.returncode,r.stderr)
 assert 'STRATA_' in r.stderr,(label,r.stderr)
 results.append({'case':label,'exit':r.returncode,'stderr':r.stderr})
(p/'C048-rejected-modes.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print('PASS eight unsupported/malformed configurations rejected before model loading')
