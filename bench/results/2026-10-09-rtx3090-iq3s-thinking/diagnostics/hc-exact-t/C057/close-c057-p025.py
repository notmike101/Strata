"""Close the predeclared screen and archive allowlisted diagnostics."""
import csv, hashlib, json, math, re, statistics
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
raw=(p/'C057-timing.txt').read_text(); parity=[x for x in raw.splitlines() if x.startswith('PARITY ')]
assert len(parity)==72 and all('bitwise_equal finite canaries_ok' in x for x in parity)
cells=[]
for line in raw.splitlines():
    if not line.startswith('MEDIAN '): continue
    v={k:float(x) for k,x in re.findall(r'(\w+)=([\d.]+)',line)}
    # Recompute each ordinary median from all seven raw rounds.
    for exact,key in [(0,'original_us'),(1,'exact_us')]:
        values=[float(x) for x in re.findall(rf'RAW id={int(v["id"])} T={int(v["T"])} apply={int(v["apply"])} round=\d+ exact={exact} us=([\d.]+)',raw)]
        assert len(values)==7 and abs(statistics.median(values)-v[key])<1e-5
        v[key+'_rounds']=values
    cells.append(v)
assert len(cells)==24
ratio=math.exp(statistics.mean(math.log(c['exact_us']/c['original_us']) for c in cells))
slower=sum(c['exact_us']>c['original_us'] for c in cells)
result={'id':'C057','parity_cases':len(parity),'timing_cells':len(cells),'measured_rounds_per_variant_per_cell':7,'excluded_warmups':1,'geometric_candidate_control_time_ratio':ratio,'slower_cells':slower,'gate_pass':ratio<=0.95 and slower==0,'cells':cells,'decision':'Reject broad exact-T specialization; no engine integration or served trial.'}
assert not result['gate_pass']
(p/'C057-result.json').write_text(json.dumps(result,indent=2)+'\n')
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
note=f'''## E238 / C057 rejected; current P025 trace preserved

C057 passed all72 complete-output bitwise, finite-value and inactive-token canary checks. Its final PASS line denotes correctness only. Across all24 timing cells, the geometric candidate/control duration ratio is{ratio:.8f}: candidate time is{(ratio-1)*100:.4f}percent higher. {slower}/24 individual medians are slower. Each median uses all seven alternating measured rounds after one excluded warmup,200calls per graph; the analysis independently recomputed these medians from the raw lines. The declared at-least5percent time improvement/no-slower-cell gate fails. Close without integration, another repeat, favorable-cell selection or a served trial. Actual BF16 weights, arithmetic/reduction order and all model quality controls were unchanged; this is not a model-throughput result. Only small tensor fixtures were resident, the standalone process exited0, and all recorded physical/commit memory floors remained above16GiB.

P025 allowlisted graph/API coverage, overlap, Q6 geometry, timing tables, host engine log, synthetic request evidence and safety/cleanup records are archived. The capture is one measured new/repeat pair after two excluded warmups, NOT five measured repetitions despite the inherited wrapper's --runs5 argument; the dedicated client sends exactly four saved R129 payloads and records one measured request per cell. All512tokens and cache-state checks passed. Nsight software-node instrumentation changes throughput: its77.8/76.2decode values must not enter qualification pools or replace R128-R131. Not-all-events-collected warning remains; matching graph cohorts do not prove completeness. Whole-capture sums include both prompts and the inter-request gap, can overlap, and are not removable or decode-critical-path time. Raw SQLite/nsys-rep and actual model fixtures remain private. Final helper files are authoritative; prepare-p025.py is a historical partial generator, followed by the archived final client/guard additions.

The full goal remains active and the existing C056 cache-screen regressions remain recorded. No production engine, source, sampler, launcher or model changes. Next examine checkpoint transfer/retention costs before any exact-prompt checkpoint prototype: preserving the existing turn checkpoint is mandatory, and an extra synchronous running-state copy could worsen fresh latency. This is a cost investigation, not approval to hide fresh-request work or redefine prompt throughput.
'''
d=pub/'diagnostics/hc-exact-t/C057'; put(d/'result.md',note)
for name in ['C057-timing.txt','C057-manifest.json','C057-safety.csv','C057-build.txt','C057-result.json','prepare-c057.py','c057-screen.cu','c057-kernels.inl','build-c057.cmd','run-c057.py','close-c057-p025.py']:
    put(d/name,(p/name).read_text())
dp=pub/'diagnostics/profiler/P025'
for name in ['P025-coverage-audit.json','P025-overlap.json','P025-q6-shapes.json','P025-stats_cuda_gpu_kern_sum.csv','P025-stats_cuda_api_sum.csv','P025-export.txt','P025-stats.txt','P025-capture.json','P025-wrapper.txt','prepare-p025.py','profile-p025.ps1','profile-p025.py','run-p025.py','audit-p025-coverage.py','audit-p025-overlap.py','audit-p025-q6-shapes.py']:
    put(dp/name,(p/name).read_text())
for name in ['engine-session.txt','safety.csv','cleanup.txt','supervisor.py','effective-sampling-modes.json']:
    put(dp/'supervisor'/name,(p/'P025-supervisor'/name).read_text())
put(dp/'result.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E238 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E238',current='C057 exact-T specialization rejected: parity72/72,23/24 timing cells slower; P025 trace archived.',next=['Inspect exact-repeat checkpoint transfer and retention costs; require a fresh-latency-safe design before implementing.','All C056 cache regressions and remaining nonstream/real-use gates remain.'],resume_command='No model resident. Stay on perf/rtx3090-thinking-80. C057 closed without integration. Read E235-E238; C056 remains unpromoted.'); s['c057']={k:v for k,v in result.items() if k!='cells'}; put(f,json.dumps(s,indent=2)+'\n')
f=pub/'README.md'; s=f.read_text(); start=s.index('Current goal checkpoint'); end=s.index('\n\n',start); s=s[:start]+'''Current goal checkpoint (E238): **full goal remains unqualified**. [C057 fixed-size HC kernel](diagnostics/hc-exact-t/C057/result.md) passes72bitwise checks but is4.18percent slower across24timing cells; rejected without engine integration. [P025 current-stack profile](diagnostics/profiler/P025/result.md) is diagnostic only. C056's closed cache screen still fails non-degradation gates, despite decode thresholds passing. Sampling,262144context,IQ3_S and vision remain unchanged. Production launcher unchanged; no benchmark model resident.'''+s[end:]; put(f,s)
print(json.dumps({k:v for k,v in result.items() if k!='cells'},indent=2))
