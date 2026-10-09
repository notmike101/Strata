import argparse, ast, json, re, time, statistics
from pathlib import Path
from urllib.request import Request, urlopen
p=argparse.ArgumentParser(); p.add_argument('--out',required=True); p.add_argument('--root',type=Path,required=True); p.add_argument('--base-url',required=True); p.add_argument('--profile',type=Path,required=True); a=p.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
cfg=json.loads((a.root/'strata-iq3_s.json').read_text())
PROFILE=json.loads(a.profile.read_text())
base=a.base_url.rstrip('/')
health=json.load(urlopen(base+'/health')); assert health['model']==cfg['model_name'] and health['max_context']==262144 and health['images'] and not health['api_key']
def ask(label,messages,cap=8192,seed=101,**extra):
    payload=dict(model=cfg['model_name'],messages=messages,max_tokens=cap,seed=seed,**PROFILE,**extra)
    (out/(label+'.request.json')).write_text(json.dumps(payload,indent=2))
    start=time.perf_counter()
    response=json.load(urlopen(Request(base+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=1800))
    (out/(label+'.response.json')).write_text(json.dumps(dict(response=response,wall_seconds=time.perf_counter()-start),indent=2))
    print(label,response['choices'][0]['finish_reason'],response.get('timings'),flush=True)
    assert response['choices'][0]['finish_reason']=='stop',response
    return response['choices'][0]['message']['content'].strip()
def user(s): return [dict(role='user',content=s)]
results=[]
for seed in range(101,106):
    text=ask(f'code-{seed}',user('Write only Python code for merge_intervals(intervals): merge a list of closed integer intervals, including equal endpoints. Merge only when next_start <= current_end, never bridge a gap of 1; return a sorted list of tuples. Do not mutate the input. Empty input returns []. Include no imports, tests, annotations, or explanation.'),seed=seed)
    blocks=re.findall(r'```(?:python)?\s*([\s\S]*?)```',text)
    code=blocks[0] if blocks else text
    tree=ast.parse(code)
    assert all(isinstance(x,ast.FunctionDef) for x in tree.body),code
    assert not any(isinstance(x,(ast.Import,ast.ImportFrom)) or isinstance(x,ast.Attribute) and x.attr.startswith('_') or isinstance(x,ast.Name) and x.id.startswith('__') for x in ast.walk(tree))
    ns={'__builtins__':{k:v for k,v in vars(__import__('builtins')).items() if k in ['sorted','list','tuple','len','min','max','range','enumerate','zip','reversed','int','float','set']}}
    exec(compile(tree,'generated','exec'),ns)
    fn=ns['merge_intervals']
    for inp, expected in [([],[]),([(3,5),(1,3)],[(1,5)]),([(1,10),(2,4)],[(1,10)]),([(5,7),(1,2),(8,9)],[(1,2),(5,7),(8,9)]),([(-3,-1),(-2,4),(6,6)], [(-3,4),(6,6)])]:
        original=list(inp); got=fn(inp); assert got==expected,(got,expected); assert inp==original
    results.append(dict(seed=seed,code_pass=True))
    for tools in [False,True]:
        extra={'tools':[{'type':'function','function':{'name':'get_weather','description':'Get weather','parameters':{'type':'object','properties':{}}}}]} if tools else {}
        answer=ask(f'exact-{seed}-{tools}',user('Reply with exactly CALIBRATION_OK and nothing else. Do not use any tools.'),2048,seed,**extra)
        assert answer=='CALIBRATION_OK',answer
history=[]
for i in range(20):
    history += [dict(role='user',content=f'Archive item {i}: blue widgets were counted.'),dict(role='assistant',content='Recorded.')]
history += user('Ignore the archived item counts. Reply with exactly LATEST_OK.')
assert ask('history',history,2048)=='LATEST_OK'
for repeat in range(2):
    assert ask(f'cache-{repeat}',user('The reference code is PINE-7319. Reply with only that code.'),2048)=='PINE-7319'
(out/'summary.json').write_text(json.dumps(dict(passed=True,code_tests=results,health=health),indent=2))
print('PASS sampled coding, exact output with/without tools, natural stop, multi-turn history, repeated prompt',flush=True)
