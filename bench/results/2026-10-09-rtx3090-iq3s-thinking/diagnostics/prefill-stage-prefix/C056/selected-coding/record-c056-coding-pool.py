import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
v=json.loads((p/'c056-coding-pooled.json').read_text())
note='''## E221 / selected-coding ABBA and bounded ambiguity repeat

The predeclared R122control/R123candidate short-first and R124candidate/R125control longer-first matrix completed: same binary/libraries, exact fixture, configs differing only by prefix-stage0/1, all12payload files byte-identical across arms. Every response512tokens with zero cache reuse; one excluded warmup and five measured seeds101-105 per cell per arm. All forty measured runs retained, including the slow81.8 values. Ordinary ten-run medians:

| Workload | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
'''
for w,c in v['cells'].items():
    for k,m in c['metrics'].items():
        note+=f"| {w} | {k} | {m['control']:.5f} | {m['candidate']:.5f} | {m['percent_change']:+.3f}% |\n"
note+='''
Both named decode targets are met, as are the measured prompt and client-E2E comparisons. However short server decode is92.20candidate versus92.30control, a0.10tok/s decrease, not an improvement. The first pair also had small E2E decreases, while the pooled E2E medians improved. Preserve this ambiguity and do not turn it into a general no-degradation claim. Decode ranges overlap widely; no statistical certainty is asserted.

Bounded next action, declared before more inference: one additional unchanged matched pair, R126control then R127candidate, both short-first, same frozen payloads/seeds. This repeats the order that showed the first-pair loss. Include every earlier and additional measured run in final ordinary fifteen-run medians per configuration/cell. Close this comparison after this pair; do not keep rerunning it until favorable. No seed exclusion, changing prompt, sampling, context, allowance or quality checker. If uncertainty or a regression remains, retain it as unproven and investigate a new mechanism instead of promoting on a selected subset.

Q0155/5 completed-answer quality and original TTL matrix remain separate. Stream/nonstream cache-hit and nonstream-miss confirmations plus real-use/near-limit gates are still missing for C056. Full goal remains active and unqualified. All four arms passed16GiB physical/commit guards and exact cleanup; production configuration restored after each. No launcher changes.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/prefill-stage-prefix/C056/selected-coding'; put(d/'first-comparison.md',note)
for n in ['c056-coding-pooled.json','pool-c056-coding.py','record-c056-coding-arm.py','start-c056-coding.py']:
    put(d/n,(p/n).read_text())
for name,source in [('R126-coding-control-confirm','R122-coding-control'),('R127-coding-prefix-confirm','R123-coding-prefix')]:
    f=p/(name+'.json'); assert not f.exists(); f.write_bytes((p/(source+'.json')).read_bytes())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E221 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E221',current='C056 selected-coding targets and prompt/E2E medians pass; short decode92.20 versus92.30 leaves no-degradation ambiguous.',next=['Exactly one additional short-first matched pair R126/R127; pool all fifteen measured runs per cell.','Close this comparison after the pair. Preserve any remaining regression or uncertainty; no repeat-until-pass.']); put(f,json.dumps(s,indent=2)+'\n')
print('E221 recorded')
