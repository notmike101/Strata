"""Five-seed structured tool round trips with the unchanged thinking sampler."""
import argparse, json, time
from pathlib import Path
from urllib.request import Request, urlopen
p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); p.add_argument('--root',type=Path,required=True); p.add_argument('--base-url',required=True); p.add_argument('--profile',type=Path,required=True); a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
root=a.root
profile=json.loads(a.profile.read_text())
base=a.base_url.rstrip('/')
health=json.load(urlopen(base+'/health'))
tool={'type':'function','function':{'name':'lookup_ticket','description':'Look up the current status of a ticket.',
      'parameters':{'type':'object','properties':{'ticket_id':{'type':'string'}},'required':['ticket_id'],'additionalProperties':False}}}
def ask(label,messages,seed,**extra):
    payload={'model':health['model'],'messages':messages,'max_tokens':2048,'seed':seed,**profile,**extra}
    start=time.perf_counter()
    response=json.load(urlopen(Request(base+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=600))
    (a.out/(label+'.json')).write_text(json.dumps({'request':payload,'response':response,'wall_seconds':time.perf_counter()-start},indent=2)+'\n')
    return response['choices'][0]
for seed in range(101,106):
    messages=[{'role':'user','content':f'Use lookup_ticket to look up ticket TASK-{seed}. After the tool returns, reply with only its status string.'}]
    choice=ask(f'tool-{seed}',messages,seed,tools=[tool],tool_choice={'type':'function','function':{'name':'lookup_ticket'}})
    assert choice['finish_reason']=='tool_calls',choice
    msg=choice['message']; calls=msg['tool_calls']; assert len(calls)==1
    call=calls[0]; assert call['function']['name']=='lookup_ticket'
    assert json.loads(call['function']['arguments'])=={'ticket_id':f'TASK-{seed}'}
    messages += [msg,{'role':'tool','tool_call_id':call['id'],'content':json.dumps({'status':'READY_FOR_REVIEW'})}]
    final=ask(f'result-{seed}',messages,seed,tools=[tool])
    assert final['finish_reason']=='stop' and final['message']['content'].strip()=='READY_FOR_REVIEW',final
    print('PASS structured tool round trip',seed,flush=True)
(a.out/'summary.json').write_text(json.dumps({'passed':True,'seeds':list(range(101,106)),'profile':profile,'note':'Synthetic tool response supplied locally; no external action executed.'},indent=2)+'\n')
