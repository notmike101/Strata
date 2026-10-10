"""Declare the next fixed-contract matrix before any inference."""
import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
note='''## E216 / C056 selected-coding matrix and network-description correction

Previous turn was progress: C056 original-workload ABBA, Q015 five-answer quality and commit c2f6195d were completed and pushed. At this entry, tracked checkout is clean, candidate SHA256cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91 and production configuration3457fdfe match, no inference/profiler process is resident, idleGPU457MiB/0percent. Fresh upstream check: mainfb58e0dbc8399662c0e47c76578c6e878b14f6cf, latest releasev0.1.41; no newer update to apply. Goal remains active.

Correction: E213 described client E2E as using a loopback endpoint. Inspection of both frozen clients and their identity manifests shows they actually connect from this PC to its LAN IP. No remote-device network latency is measured. The client timing boundaries, payloads, raw data and all numeric results are unchanged. This correction supersedes the loopback wording; original historical entry is preserved.

Next bounded matrix: R122control/R123candidate short-first, R124candidate/R125control longer-first. Same C056 binary/libraries and configurations copied from R118/R119; only STRATA_PREFILL_STAGE_PREFIX0/1 differs. Use the existing --goal-coding client, fixed random-selected topological_order fixture in short and approximately3K forms, five measured seeds101-105 plus one excluded warmup per workload,512generated tokens, streaming and zero prompt-cache reuse. Preserve all exact request bytes. Compare all ten qualifying measured values per cell with ordinary medians; no deletion or replacement of slow runs. Keep sampling, context262144, INT8KV32768 resident, compatible CPUF16vision, MTP and safety floors unchanged. Full supervisor cleanup and production restoration after each arm. No additional optimization or launcher change during this comparison.

This supplies the selected-coding speed requirement; Q015 already supplies completed-answer tests for the same candidate but cannot replace these512-token measurements. Original-workload R118-R121 results remain separate. After this matrix, stream/nonstream cache-hit and nonstream-miss confirmations plus tools/vision/remote-reasoning/cancellation/mixed-history/near-limit gates are still required. Numeric or quality failure leaves the goal active and prevents promotion.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s),encoding='utf-8',newline='\n')
for name,source in [('R122-coding-control','R118-preserve-control'),('R123-coding-prefix','R119-prefix-preserve'),('R124-coding-prefix-reverse','R119-prefix-preserve'),('R125-coding-control-reverse','R118-preserve-control')]:
    f=p/(name+'.json'); assert not f.exists(); f.write_bytes((p/(source+'.json')).read_bytes())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E216 /' not in s; put(f,s+'\n\n'+note)
put(pub/'diagnostics/prefill-stage-prefix/C056/selected-coding-plan.md',note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E216',current='C056 selected-coding speed ABBA declared; no new speed result yet.',next=['Run R122/R123 short-first and R124/R125 longer-first with --goal-coding.','Retain no-degradation requirements and all remaining stream/nonstream/cache/real-use gates.']); put(f,json.dumps(s,indent=2)+'\n')
print('E216 recorded')
