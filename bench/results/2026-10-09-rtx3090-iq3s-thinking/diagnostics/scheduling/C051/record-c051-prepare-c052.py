from pathlib import Path
import hashlib,json,re,subprocess
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
exe=Path('engine/strata-cuda133-usage-guard.exe');sha=hashlib.sha256(exe.read_bytes()).hexdigest()
assert 'PASS accepted-usage' in (p/'C051-mode-green-final.txt').read_text()
d=pub/'diagnostics/scheduling/C051';d.mkdir(parents=True,exist_ok=True)
helper=['node','<USER_HOME>/github-agent/identity.mjs','--repo','notmike101/Strata','git']
patch=subprocess.run(helper+['diff','--','src/program/generate.cpp'],capture_output=True,check=True).stdout.decode()
put(d/'C051-guard.patch',patch)
for name in ['C051-mode-red.txt','C051-mode-red-sentinel.txt','C051-mode-green.txt','C051-mode-green-final.txt','C051-engine-build.txt','C051-final-build.txt','build-c051-final.cmd','record-c051-prepare-c052.py']:
    put(d/name,(p/name).read_text(encoding='utf-8'))
put(d/'test_accepted_usage_modes.py',Path('tools/test_accepted_usage_modes.py').read_text())
note=f'''## E161 / C051 split-window compatibility defect found and guarded

Broader scheduling review followed three closed compiler paths. CUDA mapped()
already uses cudaHostAllocMapped without WriteCombined (verify.cpp:185), unlike
the uncached SYCL path motivating PR1713. Current CUDA GPU resident/PCIe experts
already overlap host CPU work after flagA publication and before flag completion.
A whole-layer drain/CPU-service/relaunch would serialize that work and add host
launches. No measured transferable cost justifies porting Arc's graph segmentation
now. Do not equate its647.7ms waitflag-only trace category with removable work.

Existing --spec-split offers a different supported scheduling architecture:
two token groups interleave pre/post work, allowing CPU experts of one group to
overlap GPU mixer/router work of the other. It increases weight traffic and kernel
launches; source documents an earlier~7% regression on another experiment. No
local campaign comparison found. A bounded same-day screen is more informative
than implementing ungrounded new graph segmentation.

Interaction found BEFORE combining: Verifier::run passes each group's local rows
to pool_multi_cb with no global-row offset. AcceptedUsage::record indexes from
zero on each call. A second group therefore appends routes to first-group rows,
and commit(keep) can count rejected rows as accepted. C046 guard omitted spec_split.
All prior C046-C049/P019/P020 arms used unsplit windows, so this finding does not
invalidate their counters. It does invalidate a prospective combined experiment.

Fix: STRATA_ACCEPTED_USAGE=1 now rejects effective --spec-split at option validation,
with an explicit diagnostic. Default-off and unsplit accepted-usage paths keep
their arithmetic and scheduling. No engine kernel, model bytes, context, sampling
or production launcher change. Full answer-quality equivalence is not claimed.

Regression test tools/test_accepted_usage_modes.py uses absent model paths and
never loads a model. Initial test attempt lacked --ple-gguf and failed too early;
retained as a harness mistake. Corrected test reached the downstream CPU feature
check, proving the missing compatibility guard on the old ac43e898 engine. After
the fix, the unsafe mode returns2 with the new diagnostic. Three controls reach
the no-model sentinel: accepted1/--no-spec-split, accepted0/--spec-split, and
accepted1/--spec-split followed by --no-spec-split (last argument wins).

CUDA13.3 sm86 Release build passed. Token-barrier1.2M oracle steps, accepted-usage
4096 windows, Windows affinity, and IQ AVX2 parity all passed. Final comment-only
rebuild and four CLI controls passed. HIP/SYCL were not built; no upstream review.
Candidate engine SHA256 {sha}; kept separately at
engine/strata-cuda133-usage-guard.exe. Existing production executable unchanged.
No throughput claim for this configuration guard.
'''
put(d/'README.md',note)
plan='''## E162 / C052 finite split-window scheduling screen prepared, not run

Hypothesis: interleaving token groups can hide CPU expert work behind GPU mixer/
router work on this host. Risk: repeated weight reads, smaller batches and more
kernels can outweigh overlap. This is existing --spec-split, not Arc graph-segment
porting. Source's older~7% loss is a warning, not a measurement on this stack.

Same current C051 binary for both arms. A R102 unsplit, B R103 split. Both use
HC-fast1, acceptedusage0, tokenbarrier0 (required by C051), auto prompt share with
MAX1024, DMA0/deviceplan0; lag2,9workers30tasks,PCIe.20,MTP4/.70. Only --spec-split
versus --no-spec-split changes within the pair. Do not compare B directly with
C049 and attribute all differences to scheduling. If promising, correct row-offset
accounting before any future combination with C046/C049; do not bypass the guard.

Exact IQ3_S,262144context,INT8KV/32768resident,CPU F16vision. Fixed thinking profile
temperature1,top_p.95,top_k20,min_p0,presence0,repetition1,frequency0. Identical
original short165/~3K3034 coding payloads,512 generated tokens, concurrency1,
stream/cachemiss,one warmup plus five measured seeds101..105 per workload. All
raw runs retained with ordinary medians, decode/prompt/E2E/stream/TTFT separate.
This is a screen; frozen random coding and full quality matrix remain mandatory.

Finite budget A/B then at most one reversed B/A confirmation if neither decode nor
E2E median loses>3% and neither prompt median loses>2%. Close immediately on these
stop conditions, malformed output, incorrect effective parameters, or memory/
cleanup failure. Pool all10rows/cell if the reverse pair runs; no favorable subset.
No additional split geometry or spec width sweep. Qualifying>90/85 cannot be
claimed from this screen alone. Neither candidate is promoted before full gates.

Before launch inventory exact model/profiler/device users and validate binary/
config identity. Independent16GiB physical/commit floor eachsecond, no per-process
memory polling, no Git/build/GUI/profiler during measured requests. Current
run-c020-arm.py supervisor with --observer audit-no-process; exact whole-tree stop
and production config restore in finally. Runtime proof: exact parsed args plus
successful captured T>=2 windows and source's split_&&T>=2 group selection; retain
any capture on a measured request instead of dropping that seed.
'''
put(pub/'diagnostics/scheduling/C052/plan.md',plan)
for arm,split in [('R102-split0',False),('R103-split1',True),('R104-split1',True),('R105-split0',False)]:
    c=json.loads((p/'R098-conditional0.json').read_text())
    c['exe']=str(exe.resolve());c['env']['STRATA_ACCEPTED_USAGE']='0';c['env']['STRATA_SERIAL_ADAPT_TOKENS']='0'
    c['args']+=[('--spec-split' if split else '--no-spec-split')]
    f=p/(arm+'.json');assert not f.exists();put(f,json.dumps(c,indent=2)+'\n')
for f in [p/'findings.md',pub/'ledger.md']:
    old=f.read_text(encoding='utf-8');assert '## E161 /' not in old;put(f,old+'\n\n'+note+'\n\n'+plan)
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint='E162',current='C051 compatibility guard built/tested; C052 same-binary split-window screen prepared, not run.',next=['Run guarded R102 control then R103 split-window screen; apply finite stop rule before any reverse confirmation.'],resume_command='Read E161-E162. engine/strata-cuda133-usage-guard.exe SHA256 '+sha+'. C052 config files prepared. Run .venv/Scripts/python.exe local-setup/target-80/run-c020-arm.py local-setup/target-80/R102-split0.json --out local-setup/target-80/R102-split0 --observer audit-no-process > local-setup/target-80/R102-wrapper.txt 2>&1 after fresh preflight. R102-R105 not run yet. Production unchanged; no model resident.');put(f,json.dumps(v,indent=2)+'\n')
f=p/'export-ledger.py';v=f.read_text(encoding='utf-8');idx=v.index('        public_identity["engine_build"] = builds.get(');entry=f"        builds['{sha}'] = {{'kind':'C051 accepted-usage split-window compatibility guard','source_commit':'d4035494','dirty_source':True,'source_patch':'diagnostics/scheduling/C051/C051-guard.patch','cuda':'13.3.73','sm':'86','msvc':'19.44.35228.0'}}\n";assert sha not in v;f.write_text(v[:idx]+entry+v[idx:],encoding='utf-8')
f=pub/'README.md';v=f.read_text(encoding='utf-8');start=v.index('Current goal checkpoint');end=v.index('\n\n',start);v=v[:start]+'Current goal checkpoint (E162): **90/85 tok/s is not fully qualified**. C050 rejected; P020 profiling published. Scheduling review found and fixed an unsupported split-window/accepted-usage combination (C051); CUDA build and regression checks passed. C052 controlled split-window screen prepared but not run. Production unchanged; no benchmark model resident.'+v[end:];put(f,v)
print('E161 guard fix recorded; E162 finite scheduling screen prepared')
