from pathlib import Path
import json,os,subprocess
p=Path(__file__).parent;c=json.loads((p/'R099-conditional64.json').read_text(encoding='utf-8'))
env=os.environ.copy();env.update(c['env']);env['PATH']=';'.join(c['lib_dirs'])+';'+env['PATH']
results=[]
for value in ['-1','1025x','262145','99999999999999999999999999','']:
 e=env.copy();e['STRATA_SERIAL_ADAPT_MIN_PROMPT']=value
 r=subprocess.run([c['exe'],'--serve',*c['args']],env=e,capture_output=True,text=True,timeout=20)
 assert r.returncode==2 and 'STRATA_SERIAL_ADAPT_MIN_PROMPT needs' in r.stderr,(value,r.returncode,r.stderr)
 results.append({'minimum':value,'exit':r.returncode,'stderr':r.stderr})
(p/'C049-rejected-modes.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print('PASS five invalid minimum-fresh-token settings rejected before model load')
