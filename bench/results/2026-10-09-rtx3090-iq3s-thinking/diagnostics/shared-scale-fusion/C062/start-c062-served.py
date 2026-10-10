import hashlib,json,math,re,shutil,statistics,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert '100% tests passed out of 7' in (p/'C062-ctest-result.txt').read_text()
detail=(p/'build-cuda86-main/Testing/Temporary/LastTest.log').read_text();assert detail.count('PIPELINE T=')==8 and 'SUMMARY cases=320 failed=0' in detail
raw=(p/'C062-result.txt').read_text();rows=[tuple(map(float,x)) for x in re.findall(r'TIMING T=(\d+) round=(-?\d+) candidate=(\d+) us=([\d.e+-]+)',raw)];assert len(rows)==128
cells=[]
for t in range(1,9):
 v=[[x[3] for x in rows if x[0]==t and x[1]>=0 and x[2]==i] for i in (0,1)];assert all(len(x)==7 for x in v);cells.append({'T':t,'control_us':statistics.median(v[0]),'candidate_us':statistics.median(v[1]),'raw':v})
ratio=math.exp(statistics.mean(math.log(c['candidate_us']/c['control_us']) for c in cells));assert ratio<=.95 and all(c['candidate_us']<=c['control_us'] for c in cells)
exe=root/'engine/strata-cuda133-shared-scale.exe';assert not exe.exists();shutil.copy2(p/'build-cuda86-main/strata.exe',exe);sha=hashlib.sha256(exe.read_bytes()).hexdigest()
base=json.loads((p/'R119-prefix-preserve.json').read_text());base['exe']=str(exe)
arms=['R132-shared-scale-control','R133-shared-scale-candidate','R134-shared-scale-candidate-reverse','R135-shared-scale-control-reverse']
for i,name in enumerate(arms):
 assert not (p/(name+'.json')).exists();c=json.loads(json.dumps(base));c['env']['STRATA_SHARED_SCALE_FUSE']='1' if i in (1,2) else '0';(p/(name+'.json')).write_text(json.dumps(c,indent=2)+'\n')
runner=(p/'run-c020-arm.py').read_text()
spot="        print('COMPLETE',a.out,flush=True)"
check='''        if candidate.get('env',{}).get('STRATA_SHARED_SCALE_FUSE') == '1':
            session=engine_log.read_bytes()[log_offset:]
            if b'shared scale-only fusion captured (CUDA K10 T2..8)' not in session:
                raise RuntimeError('Requested scale-only path was not captured; arm invalid')
'''
assert runner.count(spot)==1;runner=runner.replace(spot,check+spot);(p/'run-c062-arm.py').write_text(runner)
diff=subprocess.check_output(['node',r'<USER_HOME>/github-agent/identity.mjs','--repo','notmike101/Strata','git','diff','--','CMakeLists.txt','src/core/verify.cpp','src/kernels/cuda/native_moe.cu','src/kernels/cuda/shared_expert.cu','include/strata/kernels/native_moe.hpp','include/strata/kernels/shared_expert.hpp'],cwd=root,text=True)
result={'id':'C062','engine_sha256':sha,'micro_geometric_duration_ratio':ratio,'micro_cells':cells,'parity_cases':320,'pipeline_cases':8,'cuda_test_targets':7,'arms':arms,'full_goal_qualified':False}
(p/'C062-summary.json').write_text(json.dumps(result,indent=2)+'\n')
note=f'''## E247 / C062 integration verified; fixed served ABBA screen declared

C062 unrounded vector epilogue failed180/320 cases. The explicit-rounded version passed320/320 and all eight timing cells, geometric duration ratio{ratio:.9f} ({100*(1-ratio):.4f}percent lower duration). Raw seven-round medians and every row are retained. The integration negative control then failed all eight actual shared_expert_multi pipeline cases because bit4 had no scale-deferral implementation. After implementing it, those8/8 pipeline cases and320/320 epilogue cases pass. All seven selected CUDA test targets passed. These fixtures use synthetic Q8_0 projection weights for dataflow, not a substitute for the production model's quantized-layer quality gate.

The new STRATA_SHARED_SCALE_FUSE option is default-off and CUDA-only. It applies only to staged, nonbatch verifier windows T2..8, K10 aligned rows, native BF16 gate, no remote helper and LFUSEoff. The existing gate GEMV computes its raw logit; bit4 defers only the sigmoid-scale step into a new vector combine with explicit rounded products. CPU/PCIe expert rows, reduction FMA order, gate calculation, quantizers and sampler are retained. T1 keeps its old production path. The previous ungated kernels remain untouched. HIP/SYCL not built or qualified; no upstream review requested.

Fresh executable strata-cuda133-shared-scale.exe SHA256 {sha}. C059 correctness fix is common to both arms; QFUSE remains off. The served screen uses this SAME executable for both, exact C056 prefix-preserve stack with only STRATA_SHARED_SCALE_FUSE0/1 changing. This isolates the new mechanism; C056's earlier regression against its older control is NOT erased and must still be resolved before promotion.

Declared sequence: R132 control short-first, R133 candidate short-first, R134 candidate longer-first, R135 control longer-first. Four fresh processes; each runs one warmup new/repeat pair and five measured new/repeat pairs per prompt length. Total96 requests,80 measured,16 warmups;10 values per config/cell. Frozen random coding prompt, roughly3K padded variant, byte-identical repeat payloads, seeds101..105,512 generated tokens, stream mode, one concurrent request,262144context,IQ3_S,INT8KV,CPUvision unchanged. Thinking sampler1/.95/20/min-p0/presence0/repetition1, MTP4/.70,PCIe.20 unchanged. Client samePC via LAN IP, not remote-network latency.

Retain server decode, fresh prompt rate/count, TTFT, E2E, stream-total, total latency, accepted/drafted tokens, memory and all failures separately. Pool ordinary all-run medians. Require90short/85long server decode in each process and pooled; no pooled prompt/decode/client-rate regression or latency increase versus same-day control. New/hit cache identity and512length must pass. No rerun-until-favorable. Warmup first-request rows remain separately recorded, not cold qualification. If the mechanism fails, do not run expensive completed-answer/full real-use qualification or change launchers.

The supervisor additionally rejects a candidate arm without the actual graph-capture marker after all requests.16GiB physical/commit floor every second; audit observer excludes process-memory polling; exact child cleanup and production config restoration per arm. This is a revised code stack, permitting a new declared cache comparison; prior C056 failures remain published.
'''
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>');f.write_text('\n'.join(x.rstrip() for x in s.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/shared-scale-fusion/C062';put(d/'integration-and-served-plan.md',note);put(d/'source.patch.json',json.dumps({'patch':diff},indent=2));put(d/'tests/shared_scale_fusion.cu',(root/'tests/shared_scale_fusion.cu').read_text());put(d/'C062-test-detail.txt',detail)
for name in ['C062-red-result.txt','C062-red-build.txt','C062-red-safety.csv','C062-red-manifest.json','C062-result.txt','C062-build.txt','C062-safety.csv','C062-manifest.json','C062-integration-red-result.txt','C062-integration-red-build.txt','C062-integration-red-safety.csv','C062-integration-red-manifest.json','C062-ctest-result.txt','C062-ctest-safety.csv','C062-ctest-manifest.json','C062-engine-build.txt','C062-summary.json','prepare-c062.py','prepare-c062-integration.py','prepare-c062-ctest.py','implement-c062.py','start-c062-served.py','c062-red-candidate.cu','c062-candidate.cu','c062-screen.cu','c062-integration-red.cu','c060-scale.inl','build-c062.cmd','build-c062-engine.cmd','build-c062-integration-red.cmd','run-c062.py','run-c062-red.py','run-c062-integration-red.py','run-c062-ctest.py','run-c062-arm.py']:
 put(d/name,(p/name).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text();assert '## E247 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E247',current='C062 integrated and CUDA tests passed; R132-R135 controlled served cache screen declared, not yet run.',next=['Run the predeclared R132-R135 sequence once; preserve all outcomes.'],resume_command='Follow the live run-c062-arm process/session. Never restart based only on timeout. C062 executable hash in C062-summary.json; no launcher promotion.');s['c062']=result;put(f,json.dumps(s,indent=2)+'\n')
print('C062 served arms declared; engine',sha)
