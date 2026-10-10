import json,re
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
v=json.loads((p/'c062-stream-cache-pooled.json').read_text());assert len(v['arms'])==4 and len(v['cells'])==4
failed=[];note='''## E252 / C062 complete served cache screen

R132 control and R133 candidate ran short-first; R134 candidate and R135 control ran longer-first. Same executable and exact C056 stack, only STRATA_SHARED_SCALE_FUSE0/1 differs. All96 requests retained:80 measured,16 warmups,10 measured values per config/cell. Each new/hit request pair is byte-identical. All new prompts have zero reuse, repeats have positive reuse, and every response produced512completion tokens. Capture markers prove the candidate branch was captured; controls have none. Each arm passed the16GiB physical/commit guard and exact cleanup, with production config restored. Fixed sampling,262144context,IQ3_S,vision,MTP4/.70,PCIe.20 unchanged.

These interleaved new/hit results remain separate from the earlier pure-miss matrix. Hit prompt speed concerns only five fresh tokens, not the entire cached prefix. Loading and identity checks precede request timing. Client runs on thisPC through itsLAN address, not a remote client. Ordinary medians use every measured value; no selection or repeat-until-favorable. First requests are separately retained as warmups, not cold qualification.

| Cell | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
'''
for w,c in v['cells'].items():
 assert all(len(g)==10 for g in c['raw_decode'])
 for k,m in c['metrics'].items():note+=f"| {w} | {k} | {m['control']:.6f} | {m['candidate']:.6f} | {m['percent_change']:+.3f}% |\n"
 failed.extend(w+': '+k for k,b in c.items() if (k.endswith('_pass') or k.endswith('_degradation')) and b is False)
note+='\nFailed declared gates: '+('; '.join(failed) if failed else 'none')+'.\n\n'
if failed:
 note+='The mechanism fails the declared all-cell non-degradation/target screen. Do not promote or run expanded quality as if it were a winner. Preserve the evidence and assess whether a distinct, profiler-supported correction exists; do not rerun the unchanged arm hoping for favorable medians. The standalone24.32percent operation-duration gain does not establish a served improvement.\n\n'
else:
 note+='This narrow served comparison passes its measured gates and permits further qualification. It does not resolve the older C056 regression against its earlier control, nor establish completed-answer quality, nonstream behavior, full real-use/near-limit safety or cold startup performance. Those gates remain before promotion.\n\n'
note+='Raw per-run values/ranges, MTP accepted/offered tokens, client times and prompt counts remain attached. These observed medians are not a statistical certainty claim. Goal remains active, launcher unchanged and no benchmark model resident.\n'
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>');f.write_text('\n'.join(x.rstrip() for x in s.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/shared-scale-fusion/C062';put(d/'served-comparison.md',note)
for name in ['c062-stream-cache-pooled.json','pool-c062-stream-cache.py','record-c062-arm.py','record-c062-pool.py','prepare-c062-pool.py']:put(d/name,(p/name).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text();assert '## E252 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E252',current='C062 served cache screen complete; '+str(len(failed))+' failed declared gates; no promotion.',next=['Assess complete C062 evidence; no unchanged rerun or full-goal claim.'],resume_command='No model resident. Same branch. Read E246-E252 and C062/served-comparison.md.');s['c062']['served_cache']={'arms':v['arms'],'failed_gates':failed,'full_goal_pass':False};put(f,json.dumps(s,indent=2))
print(json.dumps({'failed_gates':failed,'cells':{w:c['metrics']['server_decode_tps'] for w,c in v['cells'].items()}},indent=2))
