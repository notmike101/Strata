# Optimization handoff â€” 2026-10-10

The requested **90 tok/s short and 85 tok/s at roughly 3K input** server-decode targets have been met in repeated measured workloads. Full qualification has not passed. After this handoff, the user explicitly requested deployment: the existing launcher now uses C056. See the [deployment verification and rollback instructions](deployment/C056/README.md).

## Measured target attainment

| C056 workload, streaming and no prompt reuse | Measured runs per length | Short decode tok/s | Roughly 3K decode tok/s | Short / 3K client E2E tok/s |
|---|---:|---:|---:|---:|
| Frozen original TTL coding fixture |10|90.05|88.00|79.19281 /43.02415|
| Frozen selected coding fixture |15|92.30|90.50|81.19105 /43.42885|

These are ordinary medians over every qualifying measured run, not peaks. Separate warmups are excluded. The selected-coding comparison improved observed prompt rates to 216.6 / 513.2 tok/s from 208.8 / 509.9; TTFT was 0.79745 / 6.13374 seconds. The client ran on the model's computer through its LAN address; separate-device LAN latency was not measured. See [original comparison](diagnostics/prefill-stage-prefix/C056/comparison.md), [selected-coding comparison](diagnostics/prefill-stage-prefix/C056/selected-coding/comparison.md) and their raw all-run JSON.

Server decode measures generated tokens, including reasoning, divided by the server generation interval. Request E2E measures completion tokens divided by client request start to complete response, including prompt processing and request overhead. Stream-total ends at the final token; TTFT measures request start to first generated content. A512-token capped reasoning response is timing evidence, not a completed coding answer.

## Completed-answer quality and remaining limits

C056 Q015 passed 5/5 naturally completed topological-order answers, each compiling and passing the same 72 objective cases (360 case executions). The separately approved allowance was 32,768 tokens; actual lengths were 23,770, 11,122, 20,449, 3,356, and 14,812. Corrected checker v2 restores the standard TypeError exception; earlier failures and original checker results remain recorded. This is evidence for this coding task, not universal quality equivalence.

The subsequent C056 exact-repeat streaming matrix failed eight declared non-degradation gates: interleaved short misses and long repeats lost client/decode performance, and short-repeat prompt/TTFT regressed. See [cache comparison](diagnostics/prefill-stage-prefix/C056/stream-cache/comparison.md). Interleaved misses are kept separate from the earlier pure-miss runs. C062 later reached92.80/89.15decode but failed12 non-degradation gates; its integration was removed. Small observed differences are not statistical proof of universal slowdown, but they do not satisfy the fixed acceptance rules.

The candidate still lacks complete nonstream miss/hit qualification, independently defined cold-first-request proof, candidate-specific tools/vision/four reasoning-level/exact-output/cancellation/mixed-history/idle checks, and near-limit recall/memory confirmation. Earlier production checks do not transfer automatically. Configured262144context does not mean90tok/s with a full context: the historical258901-input observation was2.6decode tok/s. No altered sampling, reduced quant/context, discarded slow seed or disabled gate is counted as success.

## Retained setup and reproduction

Production now uses `C:\Strata\strata-iq3_s.json` with `engine/strata-cuda133-prefix-preserve.exe` (SHA256 `cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91`). It exactly matches the measured R119 configuration. The previous format-gather config and launcher are backed up locally. Launch with:

```powershell
& '<USER_HOME>\scripts\Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1'
```

It serves keyless on0.0.0.0:8080 with262144context, exact IQ3_S shards under `C:\models\Qwen3.8-Flash-Next\IQ3_S`, compatible CPU projector `C:\models\Qwen3.8-Flash-Next\mmproj-F16.gguf`, INT8KV/32768resident and remote reasoning controls. Thinking coding sampling remains temperature1,top-p.95,top-k20,min-p0,presence0,repetition1 (frequency0), with MTP4/.70 andPCIe.20 fixed. The launch command now starts the measured C056 setup at the user's explicit request.

C056 benchmark reproduction remains local `local-setup/target-80/R119-prefix-preserve.json`, named engine `engine/strata-cuda133-prefix-preserve.exe`, SHA256cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. Config, fixture, sampler, supervisor, client and per-run identity manifests are retained in the published report. Its opt-ins combine HCfast, committed-row usage, conditional barriers, coupled draft sampling and prefix-bounded temporary KV staging; it is now selected by the launcher but remains incompletely qualified.

C063 checkpoint host-allocation reuse is default-off and unbenchmarked as a model. Its seven-pair copy screen reduced 31.7219 ms to 18.2196 ms with byte validation; eight CUDA regression targets passed. Source and named binary are retained; planned R136â€“R139 have no measurements. See [C063 plan/tests](diagnostics/checkpoint-reuse/C063/integration-and-served-plan.md) and [closeout](diagnostics/checkpoint-reuse/C063/closure.md). No HIP/SYCL validation or served cancellation claim.

## Closeout state

No benchmark model is resident, port 8080 has no listener, and the user-selected optimized config remains in place. GPU usage was 457 MiB / 0% at verification. No new branch. The later E258 user-directed C056 deployment supersedes the earlier no-deployment status. All failed evidence remains published. The goal is still unqualified and has not been marked complete. Further optional optimization should be bounded and justified by a material expected gain; this handoff does not start a new sweep.
