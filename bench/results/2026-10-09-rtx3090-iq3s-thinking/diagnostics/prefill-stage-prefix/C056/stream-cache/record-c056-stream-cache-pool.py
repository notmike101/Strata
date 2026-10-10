"""Publish the complete streaming cache matrix without hiding failed gates."""
import json,re
from pathlib import Path
p=Path(__file__).parent
pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
v=json.loads((p/'c056-stream-cache-pooled.json').read_text())
assert len(v['arms'])==4 and len(v['cells'])==4
note='''## E230 / C056 four-arm streaming cache comparison

R128 control and R129 candidate ran short-first; R130 candidate and R131 control ran longer-first. Each fresh process ran one excluded new/repeat warmup pair and five measured new/repeat pairs for each prompt length. All 96 requests are retained: 80 measured and 16 warmups. Each repeat request is byte-identical to its preceding new request. All new requests have zero reused tokens, all repeats have positive reuse, and all responses contain 512 completion tokens. Exact model, context, thinking sampler, prompt fixture, seeds, executable and loaded libraries remain fixed; candidate/control differ only in STRATA_PREFILL_STAGE_PREFIX. Ten measured values per configuration/cell are pooled using ordinary medians. First requests are separately retained in the JSON.

The misses in this interleaved matrix are separate from the closed pure-miss R122-R127 comparison because the expert-cache history differs. Hit prompt throughput represents only five fresh tokens, not rereading the entire cached prompt. Server decode, prompt throughput, client end-to-end, stream-total, TTFT and total latency remain separate. The benchmark client runs on this PC through its LAN IP; a separate LAN device was not measured. Model loading and pre-request identity checks are outside request timing.

| Cell | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
'''
failed=[]
for w,c in v['cells'].items():
    assert all(len(g)==10 for g in c['raw_decode'])
    for k,m in c['metrics'].items():
        note+=f"| {w} | {k} | {m['control']:.6f} | {m['candidate']:.6f} | {m['percent_change']:+.3f}% |\n"
    failed += [w+': '+k for k,b in c.items() if (k.endswith('_pass') or k.endswith('_degradation')) and b is False]
note+='\nGate failures: '+('; '.join(failed) if failed else 'none in the pooled observed medians')+'.\n\n'
note+='''Raw per-run values, ranges, actual fresh/reused counts and MTP acceptance are retained in c056-stream-cache-pooled.json and each arm's raw export. No failed value is dropped and these medians do not establish statistical certainty. Each arm passed its independent 16 GiB physical/commit headroom floors and exact process cleanup; production configuration was restored. The engine and production launcher were not changed during this comparison. Q015 remains separate completed-answer quality evidence; capped responses are not substitutes for that check.

Full qualification remains pending. No promotion or goal-completion claim. Continue from the recorded gate outcomes; any repeat must be bounded and declared before its result, not repeated until favorable. Nonstream miss/hit and real-use/near-limit checks still remain. The user-facing timing explanation is preserved in metrics-explained.md at the report root, with a raw R129 example and the client timer boundaries; no timing implementation was changed.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/prefill-stage-prefix/C056/stream-cache'
put(d/'comparison.md',note)
for n in ['c056-stream-cache-pooled.json','pool-c056-stream-cache.py','record-c056-cache-arm.py','record-c056-stream-cache-pool.py','start-c056-stream-cache.py']:
    put(d/n,(p/n).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E230 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text())
s.update(last_checkpoint='E230',current='C056 streaming new/repeat matrix complete; '+str(len(failed))+' pooled gate failures; full qualification pending.',next=['Assess recorded stream-cache gate outcomes before promotion; retain every run.','Complete nonstream miss/hit and real-use/near-limit gates.'],resume_command='No model resident at E230. Stay on perf/rtx3090-thinking-80; exact C056 cc85c6c7 engine and R119 config. Read stream-cache/comparison.md before choosing the next controlled experiment.',safety='R128-R131 exact cleanup and production3457fdfe restoration verified; 16GiB physical/commit floors pass.')
s['c056']['stream_cache']={'arms':v['arms'],'repetitions_per_cell':10,'failed_gates':failed,'full_goal_pass':False}
put(f,json.dumps(s,indent=2)+'\n')
f=pub/'README.md'; s=f.read_text(); start=s.index('Current goal checkpoint'); end=s.index('\n\n',start)
s=s[:start]+f'''Current goal checkpoint (E230): **full goal remains unqualified**. The C056 streaming new/repeat matrix is complete with ten measured values per configuration/cell and {len(failed)} pooled non-degradation/target gate failures; see the [complete comparison](diagnostics/prefill-stage-prefix/C056/stream-cache/comparison.md). The separate selected-coding pure-miss comparison remains92.3short/90.5approximately3K server-decode tok/s across fifteen runs/cell. Original TTL proof remains90.05/88.00 over ten runs/cell, and Q015 completed coding passes5/5 with72checks each. Fixed sampling,512-token speed cap,262144 context and IQ3_S quant remain unchanged. Nonstream and real-use gates remain. No launcher promotion and no benchmark model resident at this checkpoint.'''+s[end:]
put(f,s)
print(json.dumps({'checkpoint':'E230','failed_gates':failed},indent=2))
