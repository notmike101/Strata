import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
note='''## E225 / C056 streaming exact-repeat cache matrix declaration

Previous turn was progress: the selected-coding pure streaming-miss comparison closed at15measured runs per configuration/cell, with92.3/90.5candidate decode and improved paired prompt/E2E medians; report pushed at a443246d. Entry checks confirm that commit, clean tracked checkout, candidate enginecc85c6c7, production configuration3457fdfe, no resident inference/profiler process and idleGPU457MiB/0percent. Upstream main remainsfb58e0; no new source update to apply. Goal remains active.

Next bounded matrix: R128control/R129candidate short-first, then R130candidate/R131control longer-first. Configurations copied exactly from R118/R119 and the same cc85c6c7 binary/libraries; only prefix staging0/1 differs. Use existing --goal-coding --cache-hits in stream mode. For each frozen coding workload, run one excluded new/hit warmup pair and five measured new/hit pairs with seeds101-105. The hit repeats its immediately preceding payload byte-for-byte. Require every new request to have cache_n0, every hit to have positive actual cache_n, and every response512completion tokens. Record actual fresh/reused token counts, decode, prompt processing, stream-total, E2E, TTFT, latency, acceptance and memory separately.

The new requests in this interleaved sequence have different expert-cache history from the closed pure-miss matrix. Keep them as their own cells and never add them to R122-R127 medians. The exact-repeat hit cells are the missing qualification. Compare all ten measured runs per cell/configuration across the opposite-order confirmations using ordinary medians; no discarded slow seeds. Preserve sampler,262144 context, quant/KV, MTP, compatible CPUF16 vision, single concurrency and16GiB physical/commit floors. Each arm must clean up its full process tree and restore production before the next starts.

No engine or launcher change. Q015 completed-answer5/5 remains separate from these capped speed responses. Nonstream and real-use/near-limit requirements remain pending; no full goal completion or promotion from this matrix alone.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s),encoding='utf-8',newline='\n')
for name,source in [('R128-stream-cache-control','R118-preserve-control'),('R129-stream-cache-prefix','R119-prefix-preserve'),('R130-stream-cache-prefix-reverse','R119-prefix-preserve'),('R131-stream-cache-control-reverse','R118-preserve-control')]:
    f=p/(name+'.json'); assert not f.exists(); f.write_bytes((p/(source+'.json')).read_bytes())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E225 /' not in s; put(f,s+'\n\n'+note)
put(pub/'diagnostics/prefill-stage-prefix/C056/stream-cache/plan.md',note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E225',current='C056 streaming exact-repeat cache matrix declared; no new cache-hit measurement yet.',next=['Complete R128-R131 with --goal-coding --cache-hits, opposite workload order confirmations.','Verify actual positive prompt reuse and every512-token result; keep interleaved misses separate from the closed pure-miss matrix.']); put(f,json.dumps(s,indent=2)+'\n')
print('E225 recorded')
