import hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
plan=json.loads((p/'C063-summary.json').read_text())
assert all(not (p/name).exists() for name in plan['arms'])
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(root/'strata-iq3_s.json')=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
assert sha(root/'engine/strata-cuda133-checkpoint-reuse.exe')==plan['engine_sha256']
quality=json.loads((p/'Q015-prefix-preserve-quality/summary.json').read_text());assert quality['passed'] and len(quality['checks'])==5
assert all(c['passed'] and c['finish_reason']=='stop' and json.loads(c['stdout'])['cases']==72 for c in quality['checks'])
cfg=json.loads((root/'strata-iq3_s.json').read_text());assert cfg['exe'].endswith('strata-cuda133-format-gather.exe')
files=[root/'strata-iq3_s.json',root/'engine/strata-cuda133-format-gather.exe',root/'engine/strata-cuda133-prefix-preserve.exe',root/'engine/strata-cuda133-checkpoint-reuse.exe',Path('<USER_HOME>/scripts/Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1'),p/'R119-prefix-preserve.json']
inventory={str(f):sha(f) for f in files}
note='''## E257 / bounded closeout; C063 preserved without model benchmarking

The oversight chat relayed the user's request to wrap up soon, then clarified that optional improvements remain authorized when cheap and evidence-backed. No C063 served arm had started. The finite closeout is to retain its completed mechanism test and eight passing CUDA regressions, archive the exact source/build/config evidence, verify cleanup and publish on the existing branch. R136-R139 remain NOT RUN; no inference speed or completed-answer quality is claimed for C063. Starting another96-request comparison for a roughly13.5ms isolated allocation saving is deferred. No new hypothesis, broad matrix, production promotion or deployment was performed.

Cleanup live check: no Strata, llama, Nsight, CUDA compiler or benchmark/server Python process matched the scoped inventory; no8080listener; GPU457MiB and0percent utilization. Production config SHA2563457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0 remains restored. The launcher remains unchanged. These are endpoint snapshots, not peak-memory measurements. The8/8 C063 tests and microbench had their own memory guards; no additional model launch was needed for closure.

C063 stays default-off in source and absent from production config. C059 state correctness fix remains committed; C062's rejected fusion stays removed with its full patch/results retained. The current build directory and named checkpoint-reuse executable now contain C063, unlike the earlier E254 stale-build warning. Exact retained production and experimental file hashes are in closeout-inventory.json. Branch remains perf/rtx3090-thinking-80. The generic goal remains active/unqualified, not marked complete: meeting the measured90/85 throughput thresholds does not erase non-degradation or real-use requirements. Do not automatically interpret the unexecuted R136-R139 plan as authorization for a prolonged repeat campaign after this closeout.

GitHub identity configuration issue: shell git resolved to the ordinary Git executable and gh was not onPATH. Contribution operations used the explicit prescribed GitHub App identity helper; no personal-authentication fallback. No upstream issue, comment, PR, review or merge created.
'''
handoff='''# Optimization handoff â€” 2026-10-10

The requested90tok/s short and85tok/s roughly3K **server-decode** targets have been met in repeated measured workloads. Full qualification has not passed, and the optimized candidate has not replaced the production launcher.

## Measured target attainment

| C056 workload, streaming and no prompt reuse | Measured runs per length | Short decode tok/s | Roughly3K decode tok/s | Short /3K client E2E tok/s |
|---|---:|---:|---:|---:|
| Frozen original TTL coding fixture |10|90.05|88.00|79.19281 /43.02415|
| Frozen selected coding fixture |15|92.30|90.50|81.19105 /43.42885|

These are ordinary medians over every qualifying measured run, not peaks. Separate warmups are excluded. The selected-coding comparison improved observed prompt rates to216.6/513.2tok/s from208.8/509.9; TTFT was0.79745/6.13374seconds. The client ran on the model's computer through itsLAN address; separate-device LAN latency was not measured. See [original comparison](diagnostics/prefill-stage-prefix/C056/comparison.md), [selected-coding comparison](diagnostics/prefill-stage-prefix/C056/selected-coding/comparison.md) and their raw all-runJSON.

Server decode measures generated tokens, including reasoning, divided by the server generation interval. Request E2E measures completion tokens divided by client request start to complete response, including prompt processing and request overhead. Stream-total ends at the final token; TTFT measures request start to first generated content. A512-token capped reasoning response is timing evidence, not a completed coding answer.

## Completed-answer quality and remaining limits

C056 Q015 passed5/5 naturally completed topological-order answers, each compiling and passing the same72 objective cases (360case executions). The separately approved allowance was32768tokens; actual lengths23770,11122,20449,3356,14812. Corrected checkerv2 restores the standard TypeError exception; earlier failures and original checker results remain recorded. This is evidence for this coding task, not universal quality equivalence.

The subsequent C056 exact-repeat streaming matrix failed eight declared non-degradation gates: interleaved short misses and long repeats lost client/decode performance, and short-repeat prompt/TTFT regressed. See [cache comparison](diagnostics/prefill-stage-prefix/C056/stream-cache/comparison.md). Interleaved misses are kept separate from the earlier pure-miss runs. C062 later reached92.80/89.15decode but failed12 non-degradation gates; its integration was removed. Small observed differences are not statistical proof of universal slowdown, but they do not satisfy the fixed acceptance rules.

The candidate still lacks complete nonstream miss/hit qualification, independently defined cold-first-request proof, candidate-specific tools/vision/four reasoning-level/exact-output/cancellation/mixed-history/idle checks, and near-limit recall/memory confirmation. Earlier production checks do not transfer automatically. Configured262144context does not mean90tok/s with a full context: the historical258901-input observation was2.6decode tok/s. No altered sampling, reduced quant/context, discarded slow seed or disabled gate is counted as success.

## Retained setup and reproduction

Production remains `C:\\Strata\\strata-iq3_s.json` using `engine/strata-cuda133-format-gather.exe` (SHA2566048736d7674d8f3c66ce50060f11ca6623df33d3e885030941a6ef9e62f427c). Existing format gather, IQ2_S gather disabled and adaptive lag2 are retained. Launch with:

```powershell
& '<USER_HOME>\\scripts\\Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1'
```

It serves keyless on0.0.0.0:8080 with262144context, exact IQ3_S shards under `C:\\models\\Qwen3.8-Flash-Next\\IQ3_S`, compatible CPU projector `C:\\models\\Qwen3.8-Flash-Next\\mmproj-F16.gguf`, INT8KV/32768resident and remote reasoning controls. Thinking coding sampling remains temperature1,top-p.95,top-k20,min-p0,presence0,repetition1 (frequency0), with MTP4/.70 andPCIe.20 fixed. The launch command starts the retained production setup, not the unpromoted90+candidate.

C056 benchmark reproduction remains local `local-setup/target-80/R119-prefix-preserve.json`, named engine `engine/strata-cuda133-prefix-preserve.exe`, SHA256cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. Config, fixture, sampler, supervisor, client and per-run identity manifests are retained in the published report. Its opt-ins combine HCfast, committed-row usage, conditional barriers, coupled draft sampling and prefix-bounded temporary KV staging; it is experimental, not launcher-qualified.

C063 checkpoint host-allocation reuse is default-off and unbenchmarked as a model. Its seven-pair copy screen reduced31.7219ms to18.2196ms with byte validation; eight CUDA regression targets passed. Source and named binary are retained; planned R136-R139 have no measurements. See [C063 plan/tests](diagnostics/checkpoint-reuse/C063/integration-and-served-plan.md) and [closeout](diagnostics/checkpoint-reuse/C063/closure.md). No HIP/SYCL validation or served cancellation claim.

## Closeout state

No benchmark model is resident, no8080listener, production config restored, GPU457MiB/0percent at verification. No new branch, production promotion or deployment. All failed evidence remains published. The goal is still unqualified and has not been marked complete. Further optional optimization should be bounded and justified by a material expected gain; this handoff does not start a new sweep.
'''
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>');f.write_text('\n'.join(x.rstrip() for x in s.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/checkpoint-reuse/C063';put(d/'closure.md',note)
put(pub/'HANDOFF.md',handoff)
put(d/'closeout-inventory.json',json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'sha256':inventory,'unexecuted_arms':plan['arms'],'no_model_resident':True,'port8080_listening':False,'gpu_memory_mib':457,'production_promoted':False,'goal_complete':False},indent=2))
for name in plan['arms']:put(d/(name+'.json'),(p/(name+'.json')).read_text())
put(d/'close-c063.py',Path(__file__).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text();assert '## E257 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E257',current='Bounded closeout: C056 meets measured90/85targets and Q0155/5; full qualification remains unresolved. C063 tests retained; no served arm started.',next=['No automatic broad matrix or new sweep. Use HANDOFF.md for achieved results and unresolved acceptance gates.'],resume_command='Read HANDOFF.md and E257. No model resident; R136-R139 never started. Production launcher unchanged; C063 default-off and unqualified.');s['c063']['decision']='Retained default-off with8passing CUDA tests; model benchmark deferred at bounded closeout, no promotion.';put(f,json.dumps(s,indent=2))
f=pub/'README.md';s=f.read_text();a=s.index('Current goal checkpoint');b=s.index('\n\n',a);s=s[:a]+'Current goal checkpoint (E257): [bounded closeout and reproducible handoff](HANDOFF.md). C056 measured92.30short/90.50roughly3K server-decode tok/s on the selected coding workload and passed5/5 completed answers, but cache/nonstream/real-use gates prevent full qualification. C063 is regression-tested, default-off and not model-benchmarked. Production launcher unchanged; no benchmark model resident. No full-goal completion claim.'+s[b:];put(f,s)
print('E257 closeout recorded; R136-R139 NOT RUN; production unchanged')
