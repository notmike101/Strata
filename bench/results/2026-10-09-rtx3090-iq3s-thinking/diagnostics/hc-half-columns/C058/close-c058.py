import csv,hashlib,json,math,re,sqlite3,statistics
from pathlib import Path
p=Path(__file__).parent;pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
raw=(p/'C058-timing.txt').read_text();parity=[x for x in raw.splitlines() if x.startswith('PARITY ')]
assert len(parity)==144 and all('bitwise_equal finite canaries_ok' in x for x in parity)
cells=[]
for line in raw.splitlines():
    if not line.startswith('MEDIAN '):continue
    v={k:float(x) for k,x in re.findall(r'(\w+)=([\d.]+)',line)}
    for candidate,key in [(0,'original_us'),(1,'exact_us')]:
        values=[float(x) for x in re.findall(rf'RAW id={int(v["id"])} T={int(v["T"])} apply={int(v["apply"])} round=\d+ exact={candidate} us=([\d.]+)',raw)]
        assert len(values)==7 and abs(statistics.median(values)-v[key])<1e-5
        v[key+'_rounds']=values
    cells.append(v)
assert len(cells)==48
ratio=math.exp(statistics.mean(math.log(v['exact_us']/v['original_us']) for v in cells))
slower=sum(v['exact_us']>v['original_us'] for v in cells)
result={'id':'C058','parity_cases':144,'timing_cells':48,'geometric_candidate_control_time_ratio':ratio,'slower_cells':slower,'gate_pass':ratio<=.95 and slower==0,'registers_original':107,'registers_candidate':74,'spill_bytes_both':0,'decision':'Reject half-column geometry without integration or served trial.','cells':cells,'raw_label_note':'Inherited exact=1 and exact_us label identifies the half-column candidate; this is NOT exact-T specialization.'}
assert slower==48 and not result['gate_pass']
safe=list(csv.DictReader((p/'C058-safety.csv').open()))
result['minimum_physical_GiB']=min(int(v['physical_available']) for v in safe)/2**30
result['minimum_commit_GiB']=min(int(v['commit_available']) for v in safe)/2**30
(p/'C058-result.json').write_text(json.dumps(result,indent=2)+'\n')
db=p/'P025-decode.sqlite';con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
rows=con.execute('select bytes,copyKind,count(*),sum(end-start)/1e6 from CUPTI_ACTIVITY_KIND_MEMCPY group by bytes,copyKind order by sum(end-start) desc limit 20').fetchall();con.close()
transfer={'source_sha256':hashlib.sha256(db.read_bytes()).hexdigest(),'scope':'Top20 byte-size/copyKind groups over full P025 capture; no environment or pointer values exported; instrumented and overlapping, not complete checkpoint wall time.','columns':['bytes','copyKind','count','summed_ms'],'rows':rows}
(p/'P025-copy-sizes.json').write_text(json.dumps(transfer,indent=2)+'\n')
note=f'''## E240 / C058 rejected; architectural alternatives retained

C058's deliberately empty candidate first failed the complete-output comparison at tensor0/T1/apply0/seed0 (exit4). Implemented one-pass geometry then passed144/144 bitwise, finite-value and inactive-token canary cases. CUDA13.3/sm86 reports74registers versus107 for the reference, zero spills in both. Nevertheless all48 timing cells are slower. All seven alternating rounds per variant and one excluded warmup are retained. Geometric candidate/control duration ratio{ratio:.8f}, or{(ratio-1)*100:.4f}percent higher duration. The predeclared5percent gain/no-slower-cell screen fails. Close without integration, a favorable-width fallback, rerunning or a served trial. Reduced register demand alone did not yield a faster kernel; achieved occupancy/bandwidth counters were not measured and no causal occupancy claim is made. Original production/source/launcher unchanged.

Memory floors: lowest sampled physical{result['minimum_physical_GiB']:.3f}GiB and commit{result['minimum_commit_GiB']:.3f}GiB, both above16GiB. Only small actual-tensor fixtures were loaded; the exact child exited0 and freed allocations. No model server was started by C057/C058. The inherited raw labels exact=1/exact_us mean the C058 half-column candidate, not C057's exact-T algorithm.

Fresh architecture research examined upstream main (unchanged fb58e0db) and open PR1822 at9166e5a16e2df12be57fedd4cf0633a6484a4988, https://github.com/Niko1221/Strata/pull/1822 . It removes gate/up expert gather copies before prompt MMQ by passing an expert-pointer table; down copies remain for the required zero tail. Its reported gain is only one0.7percent prompt measurement on different dual-sm75 hardware, based on0.1.38, not local evidence and not a decode gain. It has not been applied. Existing deferred PR1742/1744 remain prefill-only leads, not new generation evidence. No upstream messages, PRs or reviews were submitted.

Reframe after the two rejected HC probes: stop narrow block/register sweeps. The next bounded question is whether P025's existing prompt gather/copy cost is large enough to justify a locally opt-in version of1822, retaining its padded-down fallback and testing exact rows. If negligible, reject by evidence before building. A prompt improvement alone cannot satisfy failed cached decode gates; the full required matrix and a distinct general-generation mechanism remain necessary. Alternatively investigate shared HC projection reuse/dataflow with hardware counters before proposing precision-changing tensor arithmetic. No lower-precision activation, quant or altered sampler is authorized as a shortcut. The synchronous full-prompt checkpoint proposal remains deferred for its added fresh latency and eviction risk.

C056 R128-R131 remains a closed failed promotion screen, Q015 quality remains scoped to C056, and C057/C058 add no qualifying model runs. Goal stays active. Retain current branch and verified production3457fdfe configuration; no benchmark model resident at publication.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/hc-half-columns/C058';put(d/'result.md',note)
for name in ['C058-timing.txt','C058-manifest.json','C058-safety.csv','C058-build.txt','C058-red-build.txt','C058-red.txt','C058-result.json','prepare-c058.py','implement-c058.py','c058-screen.cu','c058-kernels.inl','build-c058.cmd','run-c058.py','close-c058.py']:
    put(d/name,(p/name).read_text())
put(pub/'diagnostics/profiler/P025/P025-copy-sizes.json',(p/'P025-copy-sizes.json').read_text())
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E240 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E240',current='C057 and C058 rejected: exact parity preserved but timing gates fail. P025 traced current stack; checkpoint extra-copy design deferred.',next=['Inspect existing P025 prompt gather cost and PR1822 applicability before any opt-in build; no decode claim from prefill-only change.','Stop narrow HC geometry sweeps. Seek a distinct dataflow mechanism supported by counters; retain all failed cache gates.','Finish full qualification and promote only a verified non-degrading stack.'],resume_command='No model resident. Same branch perf/rtx3090-thinking-80. Read E236-E240. C057/C058 are closed standalone losers; source unchanged; C056 cc85c6c7 remains experimental.');s['c058']={k:v for k,v in result.items() if k!='cells'};put(f,json.dumps(s,indent=2)+'\n')
f=pub/'README.md';s=f.read_text();start=s.index('Current goal checkpoint');end=s.index('\n\n',start);s=s[:start]+'''Current goal checkpoint (E240): **full goal remains unqualified**. [C057 exact-T specialization](diagnostics/hc-exact-t/C057/result.md) and [C058 smaller-block geometry](diagnostics/hc-half-columns/C058/result.md) preserve bitwise outputs but fail their complete timing screens; neither entered the engine. [P025 current-stack trace](diagnostics/profiler/P025/result.md) is diagnostic only. C056's closed cache screen still fails non-degradation gates despite passing decode thresholds. Sampling,262144context,IQ3_S and vision remain unchanged. Production launcher unchanged; no benchmark model resident.'''+s[end:];put(f,s)
print(json.dumps({k:v for k,v in result.items() if k!='cells'},indent=2))
