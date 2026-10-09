"""Production capability checks; not throughput trials or sampler optimizations."""
import argparse, base64, json, time
from pathlib import Path
from urllib.request import Request, urlopen
p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); p.add_argument('--root',type=Path,required=True); p.add_argument('--base-url',required=True); p.add_argument('--profile',type=Path,required=True); a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
root=a.root
profile=json.loads(a.profile.read_text())
cfg=json.loads((root/'strata-iq3_s.json').read_text())
base=a.base_url.rstrip('/')
def get(path): return json.load(urlopen(base+path,timeout=20))
def post(label,payload):
    start=time.perf_counter()
    r=json.load(urlopen(Request(base+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=900))
    (a.out/(label+'.json')).write_text(json.dumps({'request':payload,'response':r,'wall_seconds':time.perf_counter()-start},indent=2)+'\n')
    assert r['choices'][0]['finish_reason']=='stop', label
    return r['choices'][0]['message']
props,settings,health=get('/props'),get('/settings'),get('/health')
for key in ['temperature','top_p','top_k','min_p','presence_penalty','repetition_penalty','frequency_penalty']:
    assert props['default_generation_settings']['params']['repeat_penalty' if key=='repetition_penalty' else key]==profile[key]
assert settings['defaults']['reasoning_effort']=='high' and settings['defaults']['reasoning_budget_tokens']==0
assert cfg['host']=='0.0.0.0' and health['loaded'] and health['images'] and health['max_context']==262144 and not health['api_key']
model=health['model']; assert model==cfg['model_name']
plain=post('default-thinking',dict(model=model,messages=[dict(role='user',content='Reply with exactly DEFAULTS_OK.')],max_tokens=2048))
assert plain['content'].strip()=='DEFAULTS_OK' and plain.get('reasoning_content')
fixture=json.loads((Path(__file__).resolve().parent.parent/'Q002-service-capabilities/vision.json').read_text())
img=base64.b64decode(fixture['request']['messages'][0]['content'][1]['image_url']['url'].split(',',1)[1])
url='data:image/png;base64,'+base64.b64encode(img).decode()
vision=post('vision',dict(model=model,messages=[dict(role='user',content=[dict(type='text',text='Read the text in this image. Reply only with that text.'),dict(type='image_url',image_url=dict(url=url))])],max_tokens=2048,**profile))
assert all(x in vision['content'].upper() for x in ['STRATA','VISION','42'])
for level in ('xhigh','medium','low','off'):
    params=dict(profile); params['reasoning_effort']=level
    params['chat_template_kwargs']={'enable_thinking':level!='off','preserve_thinking':True}
    msg=post('reasoning-'+level,dict(model=model,messages=[dict(role='user',content='Reply with exactly LEVEL_OK.')],max_tokens=2048,seed=106,**params))
    assert msg['content'].strip()=='LEVEL_OK'
    assert bool(msg.get('reasoning_content'))==(level!='off'), level
    print('PASS reasoning',level,flush=True)
(a.out/'summary.json').write_text(json.dumps({'passed':True,'health':health,'defaults_verified':True,'vision_ocr':True,'reasoning_levels':['xhigh','medium','low','off'],'note':'Capability checks, not comparable throughput benchmarks. Numeric sampling defaults unchanged.'},indent=2)+'\n')
print('PASS LAN/no-key, context, defaults, vision, remote reasoning levels',flush=True)
