import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
v=json.loads((p/'c056-stream-cache-pooled.json').read_text())
assert not v['cells']['short/stream/new']['decode_no_degradation']
note='''## E231 / C056 cache matrix retained as a failed promotion screen

Close the four-arm R128-R131 comparison without an additional repeat pair. Every candidate cell exceeds its 90-short/85-longer decode threshold, but that is insufficient under the no-degradation contract. Short interleaved misses: control93.95 versus candidate91.15 server-decode tok/s (-2.980%); client E2E80.922679 versus80.163395 (-0.938%). Longer repeat hits: control91.45 versus candidate90.55 decode (-0.984%); E2E90.282037 versus89.448428 (-0.923%). Short repeat hits improve decode93.10 to93.75, but fresh-prompt rate76.95 to74.50 (-3.184%) and TTFT98.388 to102.914ms fail their gates. The five freshly processed tokens make that prompt rate sensitive to small durations; this is an explanation of scale, not permission to erase or waive the failure. Longer interleaved misses improve every reported median. All sixteen warmups and eighty measured requests remain in the public record.

The short-miss aggregate MTP acceptance ratio changed from2025/2577 (78.580%) to1896/2506 (75.658%). This is a plausible contributor, not a causal finding. Longer-hit acceptance improved from1998/2607 (76.640%) to1939/2491 (77.840%) while decode slowed, so acceptance ratio alone cannot explain all results. Equal request bytes and seeds do not prove equal generated sequences or identical CPU/GPU routing; cached history and adaptive execution must be investigated. Engine logs preserve real served draft/suffix and accepted-usage counts. Do not label these served values raw-target kernel throughput.

No candidate promotion and no production-launcher edit. Prior pure-miss and Q015 quality successes remain valid within their own workloads; they do not override this failed workload screen. The cache matrix is closed rather than rerun until favorable. Next, inspect the existing per-request output/draft/routing evidence and obtain a bounded diagnostic of short new/repeat prefill/refill and subsequent decode work before proposing a code change. Keep diagnostic instrumentation separate from qualifying rates. The goal remains active; nonstream and real-use/near-limit gates remain outstanding after a candidate passes this screen. Exact process cleanup,16GiB memory floors and restored production configuration were verified for every arm.

The user's timing question is documented in metrics-explained.md: request timing excludes model load and preflight, includes prompt and served generation, and uses this PC's LAN address. The illustrative measured R129 seed103 longer miss has512completion tokens,5743.0ms server decode (89.2tok/s),11858.5512ms complete client request (43.175595tok/s), and6137.5134ms TTFT. This individual example is not used as a qualification statistic.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E231 /' not in s; put(f,s+'\n\n'+note)
d=pub/'diagnostics/prefill-stage-prefix/C056/stream-cache'
put(d/'decision.md',note); put(d/'close-c056-cache-screen.py',Path(__file__).read_text())
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E231',current='C056 cache matrix closed: target medians pass but non-degradation screen fails. Do not promote or repeat this comparison until favorable.',next=['Inspect per-request outputs, MTP counts and routing/cache history; separate observed acceptance changes from causal claims.','Run a bounded stage/refill/decode diagnostic if existing evidence cannot explain the mixed regressions; retain all data and fixed sampler.','After a revised candidate passes this screen, finish nonstream and real-use/near-limit gates.'],resume_command='No model resident. Stay on perf/rtx3090-thinking-80. Read C056/stream-cache/decision.md. C056 cc85c6c7 is experimental and failed cache-matrix promotion; do not alter production launcher.'); s['c056']['status']='experimental; failed streaming cache non-degradation screen; not promoted'; put(f,json.dumps(s,indent=2)+'\n')
f=pub/'README.md'; s=f.read_text().replace('Current goal checkpoint (E230)','Current goal checkpoint (E231)'); s=s.replace('The C056 streaming new/repeat matrix is complete','The C056 streaming new/repeat matrix is closed without promotion'); put(f,s)
print('E231 recorded; failed screen closed, diagnostic next, no promotion')
