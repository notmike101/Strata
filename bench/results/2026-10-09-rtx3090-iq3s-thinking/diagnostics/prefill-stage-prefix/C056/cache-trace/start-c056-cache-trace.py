import json,hashlib,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
names=['R128-stream-cache-control','R129-stream-cache-prefix','R130-stream-cache-prefix-reverse','R131-stream-cache-control-reverse']
rows={n:json.loads((p/n/'runs.json').read_text()) for n in names}
comparisons=[]
for left,right in [(names[0],names[1]),(names[3],names[2]),(names[0],names[3]),(names[1],names[2])]:
    rr={r['label']:r for r in rows[right]}
    for r in rows[left]:
        label=r['label']; a=(p/left/(label+'.output.txt')).read_bytes(); b=(p/right/(label+'.output.txt')).read_bytes()
        common=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
        comparisons.append(dict(left=left,right=right,label=label,warmup=r['warmup'],workload=r['workload'],output_bytes_equal=a==b,common_prefix_bytes=common,left_bytes=len(a),right_bytes=len(b),left_sha256=hashlib.sha256(a).hexdigest(),right_sha256=hashlib.sha256(b).hexdigest(),left_decode=r['server_decode_tps'],right_decode=rr[label]['server_decode_tps']))
(p/'c056-cache-output-comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
for name,base in [('P023-cache-trace-control','R118-preserve-control'),('P024-cache-trace-prefix','R119-prefix-preserve')]:
    assert not (p/name).exists() and not (p/(name+'.json')).exists()
    cfg=json.loads((p/(base+'.json')).read_text()); cfg['env']['STRATA_TRACE']='1'
    (p/(name+'.json')).write_text(json.dumps(cfg,indent=2)+'\n')
note='''## E232 / C056 cache-path diagnostic pair declared

The prior turn completed R128-R131 and changed the next action by exposing cache-history regressions; it was progress, not an idle wait. Entry HEAD39bea172 is clean except the two known unrelated untracked files. No inference processes; GPU457MiB/0percent. Upstream main remainsfb58e0db, so no new update applies. Existing C056 source/executable retained.

P023-cache-trace-control and P024-cache-trace-prefix copy R118/R119 exactly and add only STRATA_TRACE=1 to both. Execute one control/candidate pair, both short-first, using the existing goal-coding cache-hit client and all24requests (one warmup and five measured new/repeat pairs for each length). Keep all fixed payloads,512output tokens, model, sampler, context, MTP, vision, expert profile and identity/safety guards. These are instrumented diagnostics, not qualifying repetitions and not a reopening of the closed R128-R131 comparison. No source/build or production-launcher change. No process-memory or profiler polling while requests run.

Falsifiable questions: (1) Does prefix-bounded staging actually reduce physically refilled slots and refill time for fresh prompts while retaining the original logical loan? (2) Do repeat hits use only the verifier-window path, with no batched loan/refill? If so, a direct prefix-stage cost cannot explain their prompt regression; preceding generated output and adaptive expert state remain candidates. (3) How do actual window counts/widths and draft acceptance differ alongside decode duration? Existing trace window lines and prompt/read/refill lines can answer these without new logging code. Timings include trace overhead; no instrumented rate may replace a qualifying value.

Offline output comparison of all24labels across both paired configurations and same-configuration opposite-order processes is saved in c056-cache-output-comparison.json. Compare output bytes/hashes only as diagnostic evidence, not a quality score. Same seeds need not produce the same adaptive execution history. After this single pair, analyze stage decomposition and window counts before proposing another optimization. Every failed gate remains recorded; the production launcher stays unchanged and exact cleanup is mandatory.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True); f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/prefill-stage-prefix/C056/cache-trace'; put(d/'plan.md',note); put(d/'c056-cache-output-comparison.json',json.dumps(comparisons,indent=2)+'\n'); put(d/'start-c056-cache-trace.py',Path(__file__).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E232 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E232',current='One C056 cache trace pair declared; diagnostic only, production unchanged.',next=['Run P023 then P024 serially with --goal-coding --cache-hits and audit-no-process.','Analyze prompt/refill/window work without pooling instrumented rates into qualification.']); put(f,json.dumps(s,indent=2)+'\n')
for l,r in [(names[0],names[1]),(names[3],names[2]),(names[0],names[3]),(names[1],names[2])]:
    g=[x for x in comparisons if x['left']==l and x['right']==r]; print(l,r,'equal_outputs',sum(x['output_bytes_equal'] for x in g),'of',len(g))
