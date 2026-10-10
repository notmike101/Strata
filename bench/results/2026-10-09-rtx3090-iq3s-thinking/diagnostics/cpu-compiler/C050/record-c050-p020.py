from pathlib import Path
import csv, hashlib, json, math, re, statistics

p=Path('local-setup/target-80'); pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
rows=[]
for m in re.finditer(r'TIMING layer=(\d+) nt=(\d+) jobs=(\d+) repeat=(\d+) variant=(\w+) ms=([\d.]+)',(p/'C050-run/pool.txt').read_text()):
    l,t,j,r,v,ms=m.groups();rows.append(dict(layer=int(l),nt=int(t),jobs=int(j),repeat=int(r),variant=v,ms=float(ms)))
cells=[]
for l,t,j in sorted({(x['layer'],x['nt'],x['jobs']) for x in rows}):
    c=dict(layer=l,nt=t,jobs=j)
    for v in ['msvc','clang']:
        a=[x['ms'] for x in rows if (x['layer'],x['nt'],x['jobs'],x['variant'])==(l,t,j,v)]
        assert len(a)==5;c[v]=dict(raw=a,median=statistics.median(a),minimum=min(a),maximum=max(a))
    c['ratio']=c['clang']['median']/c['msvc']['median'];cells.append(c)
assert len(cells)==96 and len(rows)==960
geo=math.exp(statistics.mean(math.log(c['ratio']) for c in cells));worst=max(c['ratio'] for c in cells)
s=dict(cells=cells,raw_rows=rows,geometric_mean_ratio=geo,worst_cell_ratio=worst,qualifies=geo<=.95 and worst<=1.03,cell_count=len(cells),layers=sorted({c['layer'] for c in cells}),slower_cells=sum(c['ratio']>1 for c in cells),over_three_percent_slower=sum(c['ratio']>1.03 for c in cells))
assert not s['qualifies']
manifest=json.loads((p/'C050-run/manifest.json').read_text()); assert all(x['exit_code']==0 and x['cleanup_complete'] for x in manifest['phases'])
safe=list(csv.DictReader((p/'C050-run/safety.csv').open()))
s['safety']={k:min(int(r[k]) for r in safe) for k in ['physical_available','commit_available']}
assert min(s['safety'].values())>=16*2**30
s['source_commit']='d1a15b1c40d686a66214769943893ad68baf9ec0'
s['decision']='Rejected: fails both predeclared timing gates. No engine integration or served run.'
d=pub/'diagnostics/cpu-compiler/C050';put(d/'summary.json',json.dumps(s,indent=2)+'\n')
for f in ['actual.txt','pool.txt','manifest.json','safety.csv']:
    put(d/f,(p/'C050-run'/f).read_text())
for f in ['c050-actual.cpp','c050-pool.cpp','c050-clang.cpp','c050-msvc.cpp','c050-clang-api.hpp','c050-msvc-api.hpp','build-c050.cmd','C050-build.txt','run-c050.py','memory-guard.py','record-c050-p020.py']:
    put(d/f,(p/f).read_text())
note=f'''## E160 / C050 down-only compiler gate rejected; P020 evidence published

Previous turn answering the metric question changed no optimization state; this
continuation revalidated the pending build rather than restarting it. Both fresh
C050 executables existed, compiler processes were absent, and the full build log
ended after successful links. No engine source edits were made.

C050 compares identical current IQ4_NL down code compiled by MSVC19.44 versus
Clang19.1.5, AVX2, precise math, explicit FMA preserved, Clang contraction off.
GU, activation quantization and other down formats use the same current library.
All576 actual-weight complete-pool cases passed bitwise and finite-output checks:
48layers x experts0/173/511 x T1/2/4/8. This is sampled kernel parity, not full
model quality or a served TPS measurement.

Timing used the predeclared predicate down_type20 AND (layer%5==0 OR layer47).
Eight layers qualify:0,5,15,25,35,40,45,47. Layers10,20,30 have another down type
and were excluded by the predicate, not by their measured speed. Thus96cells,
960 measured values (5 alternating pairs each), plus192 warmup values. Each
value averages100 complete-pool calls across64actual experts/layer. T1/2/4/8,
jobs1/3/6,9workers+host0,30tasks. All timings, including slow cells, are retained.

Geometric mean of Clang/MSVC per-cell ordinary-median time ratios:
{geo:.9f} (0.7841% lower time). Worst ratio{worst:.9f} (18.0075% slower);
18/96cells slower,3/96over3% slower. The required>=5% aggregate time reduction
AND no cell>3% slower both fail. Reject and close this compiler path; no cherry-
picked subset, extra confirmation, engine integration, server run or promotion.
This does not imply a0.78% served throughput improvement.

Independent global memory guard passed every second. Minimum available physical
{s['safety']['physical_available']}bytes and commit{s['safety']['commit_available']}bytes,
both above16GiB. Exact child exit/cleanup recorded. No model server launched.
Executable hashes and source/build commands accompany all raw results.

Process-inventory correction: CIM again listed the same five old Python PIDs
30352/134612/90924/70108/273856 from the prior E050 investigation. No8080 listener
or model engine was present and GPU memory was457MiB. E050 had already proved
these were exited process objects; the initial commentary calling them wrappers
needed that distinction. Terminate returned0 for those exact validated records;
psutil's live inventory contained only the current diagnostic Python processes.
No evidence of five running models, GPU competition, or a new throughput loss.

P020 allowlisted trace audits, timing statistics, request evidence, safety logs
and scripts are published alongside this result. Raw Nsight/SQLite files stay
private. Trace consistency is not completeness, overlap sums are not removable
latency, and instrumented72.9decode is not a qualifying arm.

Upstream refreshed at2026-10-10 approximately07:07UTC using the bot helper:
main stillfb58e0dbc8399662c0e47c76578c6e878b14f6cf, releasev0.1.41 unchanged.
No stable update to apply. Fresh broader review:
- PR1813 adf979544232c18e6d90b27adf41a5ed4e9b5afe adds exact greedy-window tests,
  not a runtime optimization. Useful test design, not sampled-profile proof.
- PR1713 432702961faba67ae5325444a328ebc6fcde9f26 splits the SYCL verify graph
  around CPU service and pipelines a helper. CUDA is untested upstream. This is
  a distinct scheduling architecture worth examining against the current CUDA
  mapped-buffer/coherence and overlap design; Arc measurements do not transfer.
- PR1426 73b3db6b688f059350d1812ed67efc85bfbbdb30 DFlash currently falls back to
  target-only for sampled requests and loses to MTP in its reported greedy test.
  Not a drop-in candidate under this fixed sampling contract.

Next: examine the CUDA CPU-service/GPU-consumer dependency path and the stepped
verify architecture. Before implementing, establish whether a bounded opt-in
prototype could remove a measured cost without losing current overlap; abandon
it if that mechanism is absent. Do not retry the three closed compiler paths.
Production launcher, context262144, vision and sampling remain unchanged. Goal
active:90short/85long and complete quality/workload matrix still unqualified.
'''
put(d/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    old=f.read_text(encoding='utf-8');assert '## E160 /' not in old;put(f,old+'\n\n'+note)
dp=pub/'diagnostics/profiler/P020'
for f in ['P020-coverage-audit.json','P020-overlap.json','P020-q6-shapes.json','P020-stats_cuda_gpu_kern_sum.csv','P020-stats_cuda_api_sum.csv','P020-export.txt','P020-stats.txt','P020-capture.json','P020-wrapper.txt','prepare-p020.py','profile-p020.ps1','profile-p020.py','run-p020.py','audit-p020-coverage.py','audit-p020-overlap.py','audit-p020-q6-shapes.py']:
    put(dp/f,(p/f).read_text(encoding='utf-8'))
for f in ['safety.csv','cleanup.txt','engine-session.txt','supervisor.py']:
    put(dp/'supervisor'/f,(p/'P020-supervisor'/f).read_text(encoding='utf-8'))
put(dp/'README.md',(pub/'diagnostics/cpu-compiler/C050/plan.md').read_text().split('C050 is a NEW')[0]+'\nRaw trace files stay private; selected audits and timing summaries are included.\n')
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint='E160',current=s['decision'],next=['Inspect stepped verify scheduling against CUDA dependency/overlap evidence before a bounded opt-in prototype.'],resume_command='Read E157-E160 and C050/P020. No model resident. Current source d1a15b1c; build tree C049. All compiler comparison paths closed. Investigate scheduling architecture, not another compiler sweep.',safety='C050 offline parity and timing guard passed; exact children exited. No model server launched; production config unchanged.');put(f,json.dumps(v,indent=2)+'\n')
f=pub/'README.md';v=f.read_text(encoding='utf-8');start=v.index('Current goal checkpoint');end=v.index('\n\n',start);v=v[:start]+'Current goal checkpoint (E160): **90/85 tok/s is not fully qualified**. C050 down-kernel compiler probe passed576 bitwise cases but failed its timing gate: only0.78% geometric-mean time reduction, worst cell18.0% slower. Rejected without engine integration. P020 profiler evidence published; next is a scheduling architecture review. Production unchanged, no benchmark model resident.'+v[end:];put(f,v)
print('Recorded E160, C050 rejected, P020 diagnostic evidence published')
