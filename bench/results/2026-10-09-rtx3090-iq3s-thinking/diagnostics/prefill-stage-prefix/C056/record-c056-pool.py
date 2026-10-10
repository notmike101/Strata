import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
v=json.loads((p/'c056-pooled.json').read_text())
assert all(c['decode_target_pass'] and c['prompt_no_degradation'] and c['e2e_no_degradation'] for c in v['cells'].values())
note='''## E213 / C056 complete original-workload ABBA timing result

R118control/R119candidate short-first, then R120candidate/R121control longer-first completed with fresh processes. Exact engine SHA256cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91 and loaded libraries match; configs differ only by STRATA_PREFILL_STAGE_PREFIX0/1. Every one of the12request payload files is byte-identical across all four arms. One excluded warmup and five measured512-token cache-miss requests per cell per arm. Ordinary pooled medians below include all ten measured values, including the slower second control. No selective deletion, substitution or favorable-subset median.

| Workload | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
'''
for w,c in v['cells'].items():
    for k,m in c['metrics'].items():
        note+=f"| {w} | {k} | {m['control']:.5f} | {m['candidate']:.5f} | {m['percent_change']:+.3f}% |\n"
note+='''
Both candidate fresh-process decode medians meet their cell thresholds: R11990.1/89.5 and R12090.0/88.0. Pooled90.05short/88.0longer meets90/85. Short prompt221.2versus205.55 and longer499.35versus495.5 also pass the no-degradation comparison; E2E79.19281/43.02415versus77.72713/42.32524 passes. Margin above90 is small; this is finite workload evidence, not a universal speed guarantee or statistical certainty. The control's drift is retained and disclosed. Server decode is not real-world TPS. Client E2E runs on the server PC's loopback endpoint, not the remote LAN harness. Thinking tokens count toward512. Cold process loading and first warmup are recorded separately, excluded from these warm medians.

All four safety floors and exact launcher/server/text/vision cleanup passed; production config3457fdfe restored after each. No model remained at the end of R121. The original C055 mixed screen is preserved and not pooled with this revised mechanism. Bounds/refill unit tests and CUDA13.3sm86 build pass; HIP/SYCL are not built or validated. Original shared-header method signatures are retained through overloads for the separate SYCL implementation. No production launcher promotion.

Next Q015 evaluates the frozen selected coding fixture with seeds101-105, natural-stop answers, approved32768cap and corrected-v2 checker hash, same72objective cases and numeric thinking sampler. The512-token speed contract is unchanged. Remaining required selected-coding speed, nonstream/repeated-prefix, tools, vision, reasoning-levels, cancellation, mixed history and near-limit memory checks still apply to C056 itself; historical configurations cannot satisfy them. Goal remains active and unqualified as a whole.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s),encoding='utf-8',newline='\n')
d=pub/'diagnostics/prefill-stage-prefix/C056'; put(d/'comparison.md',note)
for n in ['pool-c056.py','compare-c056.py','c056-first-pair.json','c056-pooled.json','c056-source.patch']:
    raw=(p/n).read_bytes(); put(d/n,raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8'))
for n in ['include/strata/prefill/stage_bounds.hpp','tools/test_prefill_stage_bounds.cpp']:
    put(d/Path(n).name,Path(n).read_text())
for n in ['c055-footprint-fake.cpp','c055-footprint-fake.csv']:
    put(pub/'diagnostics/prefill-stage-prefix/C055'/n,(p/n).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E213 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E213',current='C056 original-workload ABBA meets decode90.05/88.00 plus prompt and E2E non-degradation; full goal remains unqualified.',next=['Q015 five-answer32768 quality with frozen corrected-v2 checker.','Complete selected-coding speed and all remaining real-use/context gates before promotion.']); put(f,json.dumps(s,indent=2)+'\n')
f=pub/'README.md'; s=f.read_text(); start=s.index('Current goal checkpoint'); end=s.index('\n\n',start); s=s[:start]+'''Current goal checkpoint (E213): **full goal remains unqualified**. C056 reaches pooled90.05short/88.00approximately3K server-decode tok/s across ten measured runs per cell, with unchanged512-token thinking requests. Paired prompt throughput improves7.61percent/0.78percent and client E2E improves1.89percent/1.65percent. All four arms and identical request bytes are retained. The candidate avoids reloading untouched cache slots while preserving original prompt expert placement. Completed-answer quality and remaining workload/real-use gates are still required; no launcher promotion. See [full comparison and caveats](diagnostics/prefill-stage-prefix/C056/comparison.md).'''+s[end:]; put(f,s)
print('E213 recorded')
