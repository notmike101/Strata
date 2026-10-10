import csv,json,math,re,statistics
from pathlib import Path
p=Path(__file__).resolve().parent;pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
raw=(p/'C061-result.txt').read_text();assert 'SUMMARY cases=175 failed=0' in raw
rows=[tuple(map(float,x)) for x in re.findall(r'TIMING T=(\d+) round=(-?\d+) candidate=(\d+) us=([\d.e+-]+)',raw)]
assert len(rows)==112
cells=[]
for t in range(2,9):
    values=[[r[3] for r in rows if r[0]==t and r[1]>=0 and r[2]==v] for v in (0,1)]
    assert all(len(a)==7 for a in values)
    cells.append({'tokens':t,'control_us':statistics.median(values[0]),'candidate_us':statistics.median(values[1]),'all_control_us':values[0],'all_candidate_us':values[1]})
ratio=math.exp(statistics.mean(math.log(c['candidate_us']/c['control_us']) for c in cells))
assert ratio<=.95 and all(c['candidate_us']<=c['control_us'] for c in cells)
memory={}
for name in ['C060','C061']:
    safe=list(csv.DictReader((p/f'{name}-safety.csv').open()))
    memory[name]={key:min(int(r[key]) for r in safe)/2**30 for key in ['physical_available','commit_available']}
result={'id':'C061','parity_cases':175,'parity_failed':0,'geometric_candidate_control_duration_ratio':ratio,'microbenchmark_gate_pass':True,'served_tps_claim':False,'cells':cells,'memory_minimum_GiB':memory}
(p/'C061-summary.json').write_text(json.dumps(result,indent=2)+'\n')
note=f'''## E245 / C061 isolated rounding repair passes and saves kernel time

The private explicit-rounded multiply candidate passes all175 complete bitwise/finite/canary cases, including the35 new subnormal-input cases. Unmodified fusion failed105/140 in C060. This supports the multiply/add contraction diagnosis on this NVCC13.3/sm86 build, though instruction disassembly has not independently confirmed the cause.

All seven T2..8 timing cells pass the predeclared screen. Ordinary medians use all seven alternating measured rounds per variant; each has one excluded warmup and200 repetitions per graph. Geometric candidate/control duration ratio is{ratio:.9f}, a{100*(1-ratio):.4f}percent reduction in this isolated operation. Both timings include the same restoration copy. T2 medians are{cells[0]['control_us']:.6f} versus{cells[0]['candidate_us']:.6f}microseconds; T8{cells[-1]['control_us']:.6f} versus{cells[-1]['candidate_us']:.6f}. These are kernel diagnostics, NOT token-generation rates, end-to-end improvement, or evidence that the full goal passed.

Applicability audit: existing LFUSE requires ar_on(), meaning all experts resident. Our83.6GB model on24GiB VRAM does not satisfy this. Simply setting STRATA_LFUSE would not exercise this path. Also, C060/C061 compare against the actual hits-combine API, whereas the staged verifier normally uses native_moe_combine_multi, whose K10 path is vectorized. Both restrictions must be resolved before a served trial. No production/kernel source arithmetic has been modified by C060/C061.

Next controlled design: test a standalone corrected fused VECTOR combine against the actual staged native_moe_combine_multi reference. Preserve K10 first rounded product, ordered FMA accumulation, separately rounded shared multiplication and final addition, including signed-zero/subnormal and cancellation cases. Gate it before integration using the same all-cell screen. If it passes, introduce a default-off scale-only path for the current staged verifier that keeps the existing shared gate GEMV and skips only the sigmoid-scale launch. It must not depend on all-resident mode or import the untested router-aux/pair fusions. Prove activation, same-day served A/B and exact quality before any promotion. C061 by itself does not authorize a launcher change.

Lowest sampled headroom in C060: physical{memory['C060']['physical_available']:.3f}GiB, commit{memory['C060']['commit_available']:.3f}GiB. C061: physical{memory['C061']['physical_available']:.3f}GiB, commit{memory['C061']['commit_available']:.3f}GiB. Both above16GiB, exact fixture children exited; no model loaded. Post-screenGPU457MiB/0percent. Production configuration hash remains3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0. The branch contains only the C059 state-policy correctness change plus tests/report; C061 candidate stays a published reproducible diagnostic. Goal active, no benchmark resident.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>')
    f.write_text('\n'.join(x.rstrip() for x in s.splitlines())+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/shared-scale-fusion/C061';put(d/'result.md',note)
for name in ['C061-result.txt','C061-build.txt','C061-safety.csv','C061-manifest.json','C061-summary.json','prepare-c061.py','c061-screen.cu','c061-candidate.cu','build-c061.cmd','run-c061.py','close-c061.py','c060-scale.inl']:
    put(d/name,(p/name).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E245 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E245',current='C059 CUDA correctness fix; C060 fusion rejected; C061 private rounded-product repair passes175cases and isolated timing gate. No new served result.',next=['Screen corrected vectorized scale/combine against actual staged native_moe_combine_multi, including cancellation/signed-zero/subnormal boundaries.','If exact and faster, integrate default-off scale-only staged-verifier path with existing gate GEMV; do not enable all-resident LFUSE as a substitute.','Retain C056 failed cache screen and full fixed qualification contract.'],resume_command='No model resident. Same branch perf/rtx3090-thinking-80. Read E242-E245. C061 is a microbenchmark lead only; no C062 experiment yet. C059 named engine18baf9e0 has no served qualification.',safety='C060/C061 guarded16GiB, exact children exited; GPU457MiB/0percent. C059 lacked continuous guard CSV; limitation recorded E242.');s['c061']={k:v for k,v in result.items() if k!='cells'};put(f,json.dumps(s,indent=2))
f=pub/'README.md';s=f.read_text();a=s.index('Current goal checkpoint');b=s.index('\n\n',a);s=s[:a]+'''Current goal checkpoint (E245): **full goal remains unqualified**. [C059 state fix](diagnostics/qfuse-correctness/C059/result.md) passes four CUDA test targets. [C061 rounded-product fusion](diagnostics/shared-scale-fusion/C061/result.md) passes175 exact cases and reduces isolated operation duration25.83percent, but needs a staged-verifier implementation and served validation. This is not a TPS gain. Full QFUSE and LFUSE remain disabled. C056's cache screen still fails non-degradation gates. Sampling,262144context,IQ3_S,vision and production launcher unchanged; no benchmark model resident.'''+s[b:];put(f,s)
print(json.dumps({k:v for k,v in result.items() if k!='cells'},indent=2))
