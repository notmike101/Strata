import argparse,json,time
from pathlib import Path
from urllib.request import Request,urlopen
p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--request',required=True);a=p.parse_args()
payload=json.loads(Path(a.request).read_text());start=time.perf_counter();first=None;last=None
with urlopen(Request(a.base_url.rstrip('/')+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=900) as response:
 for line in response:
  if not line.startswith(b'data: '):continue
  body=line[6:].strip()
  if body==b'[DONE]':break
  event=json.loads(body)
  if 'error' in event:raise RuntimeError(event['error'])
  delta=event['choices'][0].get('delta',{})
  if delta.get('content') or delta.get('reasoning_content'):
   last=time.perf_counter();first=last if first is None else first
  if event.get('usage'):final=event
end=time.perf_counter();n=final['usage']['completion_tokens']
print(json.dumps(dict(response=final,ttft=first-start,e2e_seconds=end-start,e2e_tps=n/(end-start),stream_total_tps=n/(last-start)),indent=2))
