import hashlib,json,re,shutil
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert 'state_bytes_differ=2301127' in (p/'C059-before.txt').read_text()
assert '100% tests passed out of 4' in (p/'C059-ctest.txt').read_text()
assert 'new differing bytes 0, legacy differing bytes 31241' in (p/'C059-boundary.txt').read_text()
detail=(p/'build-cuda86-main/Testing/Temporary/LastTest.log').read_text()
assert detail.count('state_bytes_differ=0 output_bytes_differ=0')==4
exe=root/'engine/strata-cuda133-qfuse-commit-fix.exe'
shutil.copy2(p/'build-cuda86-main/strata.exe',exe)
sha=hashlib.sha256(exe.read_bytes()).hexdigest()
note=f'''## E242 / C059 state fix verified; broad QFUSE remains ineligible

The original source-derived capture/commit probe failed as expected: full QFUSE captured without self-commit, then incorrectly skipped the commit graph, leaving 2,301,127 recurrent-state bytes different from the accepted-state reference. The 64 ordinary GDN fused-output cases passed, showing why output-only checks did not catch this state error.

The narrow correction introduces one shared verify_self_commit policy for both capture and commit. Full QFUSE still uses its commit graph; QFUSEoff, single-token nonbatch enabled commits retain their original path. No kernel arithmetic, quantizer, sampling, configuration, or launcher change. The actual GDN test now covers four policy/output combinations, all with zero recurrent-state and float-output byte differences. CUDA13.3 sm86 build succeeded and all four selected tests passed: verify_parity, qfuse_gdn_test, gr_parity, gdn_parity. These are GDN/kernel checks, not full verifier/conv/KV/session or completed-answer qualification. HIP and SYCL were not built; no upstream review requested.

The independent 8,192-block quantization-boundary diagnostic finds 31,241 differing bytes for the legacy helper versus native Q8_1, and zero for the proposed upstream helper on this corpus. The proposed helper is PRIVATE DIAGNOSTIC code only, not integrated; subnormal/FTZ coverage is still required. Therefore full QFUSE remains disabled and unsafe as a performance candidate. R008/R014 stay in the ledger but cannot qualify a corrected QFUSE path. The fixed engine is archived locally as strata-cuda133-qfuse-commit-fix.exe, SHA256 {sha}; it has no served benchmark or quality result.

Safety reporting correction: E241 specified 16GiB floors, but the direct C059 fixture launches did not record a continuous memory-guard CSV. Only preflight free host memory around112GiB and GPU457MiB were observed; no continuous minimum is claimed. The small synthetic fixtures exited, and no model was loaded. Subsequent screens must use the existing guarded supervisor. This omission does not qualify model memory safety.

User approval of the separate32,768-token completed-answer allowance is retained. Fixed speed tests remain512tokens with identical coding sampling, prompts and seeds. Q015 already uses the approved allowance; do not rerun it merely because approval was delivered again. No new qualifying TPS measurements. C056 remains experimental because its cache matrix regressed; the goal stays active.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>')
    f.write_text('\n'.join(x.rstrip() for x in s.splitlines())+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/qfuse-correctness/C059';put(d/'result.md',note)
for name in ['C059-before.txt','C059-before-build.txt','C059-fixed.txt','C059-fixed-build.txt','C059-ctest.txt','C059-engine-build.txt','C059-boundary.txt','C059-boundary-build.txt','C059-manifest.json','c059-gdn.cpp','c059-policy.inl','c059-boundary.cu','c059-q8-proposed.cuh','build-c059.cmd','build-c059-fixed.cmd','build-c059-engine.cmd','build-c059-boundary.cmd','prepare-c059.py','prepare-c059-boundary.py','close-c059.py']:
    put(d/name,(p/name).read_text())
put(d/'C059-test-detail.txt',detail)
put(d/'fixed-engine.json',json.dumps({'sha256':sha,'file':exe.name,'served_trials':0},indent=2))
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E242 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E242',current='C059 narrow state fix passed CUDA tests; QFUSE remains disabled because independent rounding hazards remain.',next=['Screen shared-expert gate/scale fusion for exact arithmetic before timing; use a guarded standalone fixture.','No promotion until full fixed matrix passes without degradation.'],resume_command='No model resident. Read E241-E242. C059 is a correctness fix only; C056 cache gate remains failed.');s['c059']={'engine_sha256':sha,'cuda_tests_passed':4,'quantization_boundary_legacy_different_bytes':31241,'full_qfuse_qualified':False};put(f,json.dumps(s,indent=2))
f=pub/'README.md';s=f.read_text();a=s.index('Current goal checkpoint');b=s.index('\n\n',a);s=s[:a]+'''Current goal checkpoint (E242): **full goal remains unqualified**. [C059](diagnostics/qfuse-correctness/C059/result.md) fixes a reproduced one-token QFUSE state-commit bug and passes four CUDA test targets. Separate rounding hazards keep full QFUSE disabled. No new served speed claim. C056's closed cache screen still fails non-degradation gates despite passing decode thresholds. Sampling,262144context,IQ3_S and vision remain unchanged. Production launcher unchanged; no benchmark model resident.'''+s[b:];put(f,s)
print('C059 recorded; fixed engine SHA256',sha)
