# Technical experiment ledger

## H000: installation and model change

The initial Unsloth UD-Q4_K_XL setup used the compatible Flash-Next F16 projector after identifying a width mismatch in the originally requested 27B projector. The first model's greedy no-thinking benchmark measured 37.5/32.7 tok/s at short/~3K prompts. The user then selected GSQ-RCO IQ3_S; its first corresponding measurement was 83.7/82.1. This model substitution was explicitly requested and is not an optimization claim at constant quality. The early identity manifests record their original context and arguments.

The deployment subsequently moved to 262,144 maximum context, kept INT8 KV streaming with 32,768 resident cells, GPU vision, and single-user serving. LAN/keyless access was explicitly requested. Setup hashes and the two shard identities were retained. Every later optimization uses IQ3_S and retains those capabilities.

## H001: 262K hardware calibration, before fixed thinking

Question: can the CPU/GPU division and speculation defaults improve this i9-10900KF / RTX 3090 / PCIe 3 x8 combination? Built-in calibration uses greedy sampling and therefore belongs to the historical contract only. Total calibration time: 907 seconds. Full raw sweep values are in historical-calibration.json.

- PCIe fraction tested: 0, .18, .20, .35, .55, .75, .90, 1.0. Initial .18 median 63.55 and .20 64.47; fractions .35 and above were progressively slower, down to about 25 at 1.0. This host benefits from leaving most misses on the CPU.
- Draft-confidence floor tested: .30, .50, .70. Paired confirmation selected .20/.70; ordinary confirmation medians 64.663 -> 66.967, +3.56%.
- CPU workers: nine retained. Six/four/two measured approximately 61.2/54.7/42.8 against 65.2 with nine on the calibration prompts.
- Adaptive cache candidate swap counts 80 and 160 did not clear the >3% promotion threshold. They were not installed.
- Production-path greedy validation: 80.5 -> 84.3 short; 79.5 -> 82.5 longer. Sampled no-thinking validation: 78.0 -> 81.1 short; 75.9 -> 80.6 longer. These numbers do not satisfy the current thinking target.

Validation: five sampled completed coding responses; exact output; unused tool schema; multi-turn instruction; warm cache; image OCR. An initial interval test allowed an ambiguous interpretation of integer adjacency; failed output retained, prompt clarified and then held identical across control and candidate. Retrieval of an exact planted value from 52,542 input tokens passed. No full-window occupancy claim.

Profiler attempts P001/P002 needed correction of an implicit Windows cp1252 tokenizer read; explicit UTF-8 resolved it. P004 captured CUDA graphs, but included startup and vision warmup and aggregated graphs rather than internal nodes. Its ordinary kernel ranking was not used to identify decode hotspots. An additional restart cross-check was blocked by approval review; recorded, not worked around.

Decision: retained only pcie_frac .20 and spec_min_p .70. No model, KV or vision precision change.

## T001: freeze the model-card thinking sampler

User required the same recommended thinking-mode parameters throughout all subsequent optimizations. Set production config sampling and persisted shared defaults. High maps to xhigh; reasoning enabled/preserved, no forced reasoning cutoff. Verified effective API defaults separately from declared config and a plain-client request. Native 262K requires no context extrapolation. Previous non-thinking results were explicitly superseded.

Baseline B001 and final restored B003 each contain five measured seeds per workload after a separate start. Aggregate ten-run medians: short 76.8 (74.3-81.2), longer 72.0 (68.4-73.7); E2E 67.65/38.17. All 512 output tokens and zero prompt-cache tokens.

## T002: interleaved draft-threshold sweep

Mechanism: trade more speculative extension against rejected target verification work. Change only hardware draft floor, not target sampler. Five seeds per arm and length; identical paired prompts; alternating arm order. Disable checkpoints in all arms to prevent cache bias. These diagnostic rates must not be compared directly with checkpoint-enabled production baselines.

Short control .70:75.2, .50:73.9, .90:74.1. Longer .70:70.4, .50:69.9, .90:69.3. Both candidates rejected. Raw request-level acceptance and timing fields retained.

## T003: coupled drafting

Mechanism: draft token guesses use the target sampler's random draw instead of greedy guesses, with the same target distribution. Added --coupled-draft only; fresh process, five measured production requests per workload. Short 76.0 vs matched baseline 77.3 (-1.7%); longer 72.7 vs 72.5 (+0.3%). No material repeatable gain. Flag removed and original configuration restored.

## T004: completed-answer and capability validation

Five interval-merging implementations passed compilation and objective tests with 8192 output allowance and the frozen high-thinking sampler. One seed generated 4674 total tokens, demonstrating why the 512-token speed probe is not a completed-answer test. Exact-output cells with/without tools, natural stopping, long history/latest instruction, cache reuse and vision OCR passed. A final production restart and ordinary request without overrides verified default thinking. Ninety explicit benchmark/quality payloads were audited against the frozen profile.

Per-request reasoning API support was then checked independently for xhigh, medium, low and off. All computed 17*23 correctly; the first three returned reasoning content, off did not. Mapper outputs were asserted, shared defaults remained unchanged. These are capability checks, not substitutes for fixed-thinking performance tests.

## E001: current 80 tok/s campaign, update check and control

User authorized local modifications and required updates first. git fetch found HEAD equal to origin/main at fb58e0d. Installed BUILD.json and latest GitHub release both identify 0.1.41. No Strata update available. Existing local files and credentials preserved. No unrelated driver or package update performed.

Production launcher restarted after validating the port owner and terminating only its process tree. Verified engine/vision exit and VRAM release. B001 five-seed control: short 75.1 (72.1-78.4), E2E66.59; longer71.3 (69.5-73.3), E2E37.96. All output512 and cache0. The current requirement is median >=80 on both existing prompt lengths with no quality or capability reduction, and independent E2E reporting.

## E002 / P001: Nsight graph-node profile

Used Nsight Systems 2026.1.3, CUDA node-level graph tracing, capture started after model readiness. Same production API/payload sampler, GPU vision resident. STRATA_VERIFY_PROFILE enabled for additional GPU stamps. CPU sampling/context switches were unavailable without elevation; CUDA trace completed. Four diagnostic requests (one warmup and one sample per length), never included in uninstrumented medians.

The aggregate kernel table has wait_flag_ge at30.7%, fetch_blobs8.5%, native_q6_k_mmvq6.8%; GPU stamp instrumentation itself is3.4%. CUDA API aggregate includes cudaGraphLaunch40.0%, cudaEventSynchronize25.3%, cudaStreamSynchronize18.4%. These are shares of summed traced durations, not absolute uninstrumented wall-time shares. Kernel counts and every row are published in CSV. The .nsys-rep and SQLite remain local due to size.

Source inspection: GPU-stage instrumentation disables shared-expert side-stream overlap to time phases; it materially perturbs runtime. Detailed stage text also requires STRATA_DECODE_TIMING, which was absent, so no such text was obtained. Do not interpret profiling's 30-50tok/s as production performance. Next test selected CPU coordination placement because the graph waits on host/CPU work.

## E003 / R001: host-core last

Change: add --host-core last, keep nine workers, all model and sampler controls unchanged. Hypothesis: the default coordinating thread on CPU0 competes with Windows GPU interrupts; moving it to logical CPU18 may reduce wait latency. Startup confirmed workers0,2,...,16 and coordinator18. No arithmetic change.

Three measured seeds per length. Short raw63.7,60.7,61.1 (median61.1); longer60.9,56.8,59.5 (median59.5). Large apparent regression against B001; **not promoted**. Checked the new engine's loaded modules for Nsight/CUPTI injection; none found. Profiler session reported shutdown. A fresh original-control run was required before attributing causality.

## E004 / B002: post-profile control repeat and discrepancy

Restored original config and restarted through normal launcher, same sampler and same initial three paired seeds. Short59.5,63.6,62.8 (median62.8); longer61.5,56.9,60.4 (median60.4). Thus most of the B001-to-R001 drop also exists in an unchanged control. R001 vs B001 is confounded; exact cause unresolved. No further performance candidate will be promoted while this discrepancy remains.

During B002: GPU SM clock1995MHz, memory9701MHz, temperature69C, draw234W, P2 under load; approximately417MiB free VRAM and63GiB free physical RAM. These isolated observations do not prove absence of memory-pressure, CPU or scheduling effects. Browser work for authorized fork creation happened during this control and is another possible competing-work confound. Future clean controls must run after browser/publication activity is quiet.

## Publication and continuation

User superseded the initial no-push instruction: create a fork under notmike101 regardless, publish this detailed technical ledger, and push any future Strata code changes there. Publishing is limited to allowlisted synthetic experiment data and technical metadata; local credentials, full process inventories and private machine paths are excluded.

Queued hypotheses, not yet measured: CPU task granularity (--pool-tasks10 vs automatic30); MTP window6 vs4; coupled Gumbel-max drafting with unchanged target sampler; bit-equivalent activation quantization fusion. Stop speculative tuning until the repeated-control discrepancy is resolved. Residency-biased routing, speed projection/control vectors, layer omission, lower target precision, lower reasoning, reduced context and known-corrupt stage pinning are excluded.

Next actions: publish this checkpoint; repeat control in a quiet environment; obtain low-overhead decode timing if necessary; localize the changed cost; then test one supported hypothesis at a time and append every outcome here.

## E005 / B003: quiet repeat after exact profiler-agent cleanup

A subsequent live process inventory found the Nsight agent for session strata80 still present (the session itself was shut down). The earlier local note that the agent had exited was incorrect. Stopped only that verified agent, restarted the unchanged production configuration and ran one warmup plus three measured seeds per workload. No browser actions occurred during measured requests. A separate nvidia-smi logger sampled GPU counters every two seconds; its observed CPU time was 0.03125 seconds during the experiment. No engine tracing flags were set.

Short decode raw62.5,63.1,63.8; median63.1; E2E56.39; TTFT0.995s. Longer raw57.9,58.0,60.3; median58.0; E2E32.17; TTFT7.112s. All six measured runs generated512 tokens with zero cached input. Requests match B001 byte-for-byte for checked short-run-1; generated text differed despite the same seed. A fixed seed does not establish bitwise deterministic inference. First short-run MTP accepted184/252 drafts versus B001176/234, so no claim that acceptance counters are identical.

Profiler-agent cleanup did not restore the initial baseline. An in-flight GPU sample showed2010MHz SM,9701MHz memory,68C,197.63W,23772MiB allocated,94% utilization; CPU performance counter reported132% of3696MHz nominal and74% utility. These are snapshots, not a complete exclusion of CPU scheduling, memory pressure, clock or thermal problems. Preserve the discrepancy rather than cherry-picking B001. The original serving configuration remains active, and no new candidate is promoted. Next technical step is STRATA_DECODE_TIMING-only diagnostics, followed by matched uninstrumented confirmation after the changed cost is isolated.

Publication checkpoint: ledger and allowlisted evidence prepared and verified locally. Fork creation and remote publication remain pending GitHub browser authentication; no successful fork/push is claimed. Public text is normalized to LF before SHA256 generation, while local raw captures retain their original bytes.

## E006 / publication and P002 stage timing

GitHub CLI authentication became available as notmike101. Created public fork notmike101/Strata, verified its parent is Niko1221/Strata, and pushed branch perf/rtx3090-thinking-80 at f77e6e3427d1f4da8c35dc70d793726ff917bc4f. Upstream remains origin; fork is a separate remote. A fresh fetch and release check still found v0.1.41 with no newer upstream source. No model or engine update was available.

P002 changed only STRATA_DECODE_TIMING=1; no CUDA event/node profiler. One excluded warmup and one measured seed per workload. Short75.1 / longer70.0 decode, E2E66.63 /37.57. Diagnostic only, not a promotion or five-seed performance claim. Short measured window averaged19.94ms, verify16.09ms (GPU-reach10.13ms, host5.04ms including CPU4.86ms), draft1.05ms, 1.50 output tokens/window. Longer23.50ms/window, verify18.68ms (GPU-reach10.84ms, host6.94ms including CPU6.74ms), draft1.26ms, 1.65 output tokens/window. Some elapsed time is outside the reported stage subtotals. GPU-reach includes work/synchronization before the host can proceed; it is not purely GPU compute.

The instrumented samples return near the initial baseline, contradicting a permanent software regression. An uninstrumented B004 repeat is required. Engine startup logs also show only216-251MiB CUDA headroom at readiness and117MiB after graph variants in P002. Historical B001 had239MiB, so the warning alone does not prove the cause. Windows GPU paging is a falsifiable memory-pressure hypothesis; reserve1200 vs700MiB will be measured separately. This moves a small set of experts between GPU and CPU without changing weights, routing, precision, sampling, context or vision. CPU/GPU rounding can differ as in the existing cache implementation; completed-answer validation remains required before promotion.

## E007 / B004 uninstrumented recovery control

Restored the original configuration, including removal of STRATA_DECODE_TIMING. Fresh engine, same three seeds. Short raw74.7,73.7,73.7 (median73.7, E2E65.38, TTFT0.902s); longer72.8,70.1,71.4 (median71.4, E2E37.98, TTFT6.340s). The earlier performance range is recovered without a new tuning flag; this falsifies the idea that the source or original configuration permanently regressed. It does not identify the transient slowdown's cause. The warmup remained63.8short /69.5longer and is retained/excluded by the predeclared protocol. B004 is the current paired control. Target80 remains unmet.

Next arm R006 changes only vram-reserve-mib700 to1200. Hypothesis: more CUDA headroom avoids Windows residency pressure and improves consistency; counter-risk: fewer experts resident increases CPU work and lowers throughput. No sampling or capability change. Source documents the same tradeoff on different hardware; that is motivation, not local proof.

## E008 / R006 reserve1200 rejected; R007 CPU vision hypothesis

R006 changed reserve700 to1200MiB only. Short raw70.2,73.3,71.3 (median71.3, E2E63.35), longer67.3,67.4,69.5 (median67.4, E2E36.61). Relative to B00473.7/71.4 this is slower3.3% /5.6%. Extra headroom reached675MiB after capturing another graph variant, but the smaller expert cache raised CPU work. Rejected as a throughput optimization and reserve700 restored in the next arm. This test does not prove that the earlier transient slowdown was paging; it disproves a speed benefit from this reserve increase in the recovered state.

R007 changes only vision.gpu from true to false, preserving the same F16 projector, model shards, image-token cap1024, vision availability, numeric sampling, reasoning and262144context. This deliberately changes the earlier GPU-vision placement contract, not the user's requested vision capability or model precision. The user requested80tok/s without quality loss and did not require the image encoder to run on GPU. GPUProcessMemory measured1,362,653,184 dedicated bytes for the vision process before this arm. Hypothesis: keeping the encoder loaded in system RAM frees about1.3GiB VRAM for more text experts, reducing CPU misses enough to approach80. Counter-risk: slower image encoding; report image latency and correctness separately. No promotion before measured text gain and image checks.

The GPU reference image request (fixed thinking profile, seed106, same synthetic STRATA VISION42 fixture, max_tokens2048) returned the exact text with natural stop in2.538s total,259prompt and45completion tokens, zero cached input. It ran on R006 after throughput measurement and is a capability/latency reference, not a headline speed sample. R007 must repeat the same request from a new engine. All earlier arms keep GPU vision; the per-arm public identity now explicitly records vision execution device and token cap.

## E009 / CPU vision results

short: raw decode [79.2, 80.2, 81.1]; median80.2; E2E70.359; stream-total70.371; TTFT0.913s. longer: raw decode [74.6, 72.9, 72.4]; median72.9; E2E38.886; stream-total38.891; TTFT6.170s. All three seeds per cell generated512tokens with zero cached input; warmups retained separately.

F16 image OCR returned STRATA VISION42 with natural stop,259prompt/42completion tokens, zero input cache,3.752s E2E vs GPU2.538s with45completion tokens. Different completion length is recorded; this is total request latency, not isolated encoder timing. Text short median meets80 in this three-run scan, longer does not. Candidate only, no final promotion. Cache grew from7882 to8409slots (14.95 to15.95GiB), with460MiB CUDA headroom at readiness. GPUProcessMemory confirmed zero dedicated bytes for the CPU vision process. Capability is preserved; image latency tradeoff is explicit.

## E010 / producer activation quantization fusion

short: raw decode [76.8, 82.4, 90.0]; median82.4; E2E73.492; stream-total73.502; TTFT0.786s. longer: raw decode [71.3, 76.1, 75.0]; median75.0; E2E39.550; stream-total39.555; TTFT6.136s. All three seeds per cell generated512tokens with zero cached input; warmups retained separately.

Only STRATA_QFUSE=1 added to R007. Source hypothesis: write Q8_1 activation images in their producing kernels, eliminating separate quantization launches with the same quantized bytes. Per source this also disables one-token self-commit, a possible counter-cost. Median gains vs R007 are2.7%short and2.9%longer, but short spread is wide and the target is unmet on longer. Keep as a provisional candidate requiring paired confirmation and completed-answer checks; no peak90 claim. No source code changed. R010 next tests DF_BRANCH alone against R007; independent mixer side branches can overlap. Its documented Linux NVML-related hang has not been observed upstream on Windows; verify no stalls and ordinary request correctness locally.

## E011 / R010 GPU side branches and R011 blanket gathered CPU path

R010: CPU vision plus STRATA_DF_BRANCH=1 alone. Short80.5median (80.5,79.4,82.0), longer73.1 (73.1,73.7,69.1), E2E70.90/38.93. Relative to R00780.2/72.9, differences are below1%, with a slower long seed. Rejected as an unsupported throughput gain. No stalls observed in the eight requests, including identity/NVML queries, but that small run is not a general stability proof.

Built the existing CPU parity/microbenchmark target with MSVC17.14.36, Release, portableAVX2 and the exact pinned ggml commit3cf03257f219afbe7334045ff7c6a06ac68c627d. Official GitHub source archive SHA256cbe23c594282ead2937abb3f008e51fcec4609d9256652fff42c7cc1c21ea47b. This did not replace the serving engine. C001 default and C002 with STRATA_IQ256_GATHER=1/STRATA_IQ_MT_MIN=1 passed with zero failures: variant rows bitwise equal for1..8tokens, and comparison to ggml within the test's1e-5relative tolerance. Single-token ggml vs multi-token floating accumulation is not bit-identical.

C003 on logicalCPU2,256MiB synthetic expert working set, five repetitions: IQ3_S/IQ4_NL one-token expert median0.665ms through the default engine dispatcher vs0.415ms gathered. This is a single-thread microbenchmark, never a served-TPS claim. R011 tested both switches in the actual release engine with CPU vision: short80.0 (78.7,80.0,80.3), longer73.8 (73.8,73.3,74.5), E2E70.66/39.10. Only a small gain on longer;80not met. No promotion based on the38%microbenchmark reduction.

Model-layout correction: the IQ3_S package is a mixture, not48layers of IQ3_S gate/up weights. native_experts.txt gives(gu_type,down_type): (22,20)x15,(18,20)x14,(21,20)x9,(22,42)x5,(18,42)x3,(21,42)x1,(23,20)x1. In names,20layers of IQ2_S gate/up,17IQ3_XXS,10IQ3_S,1IQ4_XS; down is IQ4_NL or Q2_0. C003's first format alone was insufficient to predict the whole model. C004 measured every remaining actual pair. IQ2_S/IQ4_NL one-token total: scalar0.332ms, gather0.448ms, defaultengine0.395ms; two-token0.401/0.498/0.403. IQ3_XXS/IQ4_NL one-token scalar0.414, gather0.380, engine0.458. Thus forcing gathers on every format cancels part of the IQ3 gains with an IQ2_S regression.

Bounded implementation design: retain the existing global/automatic gather decision by default, and add optional per-format overrides for IQ2_S,IQ3_XXS,IQ3_S. The candidate will gather IQ3 formats but keep IQ2_S scalar, paired with the existing multi-token-from-one setting. No weights, quantization, sampler, context, routing or image-token limit change. Tests must prove format-specific precedence, inheritance when absent/empty, unchanged ISA bits and numerical parity. Work occurs in managed isolated worktree avx2-format-dispatch; the fork already exists. First build an untouched CUDA13.3/sm86 control, preserve its executable, then test the dispatch patch with the same compiler. No revised defaults and no cross-backend performance claim.

## E012 / community reporting audit and clean CUDA build

Reviewed bench/results/COMMUNITY.md and docs/COMMUNITY_BENCHMARKS.md. Added the full all-cell results table with actual/fresh/reused/generated token counts, run count, prompt/decode medians and full ranges, TTFT and total client latency. Published the measurement script (private root/URL parameterized), synthetic request/output artifacts, cumulative verbatim engine timing lines, memory snapshots and explicit trimmed/unmeasured inventory. Added storage and power-limit observations, preparation hashes, and a labeled short/3K index entry. Results branch remains separate from the engine worktree; no upstream PR submitted.

Built untouched engine source fb58e0 (worktree documentation HEAD5f64e18) with CUDA13.3.73, MSVC17.14.36, CMake Release, STRATA_PORTABLE=ON, STRATA_ENABLE_CUDA=ON, CMAKE_CUDA_ARCHITECTURES=86, STRATA_BUILD_TESTS=ON and pinned llama.cpp3cf03257. Preserved control executable SHA25687ed092cacef166254c109c6a8a216182b968d0104f80533ff7a295365cdd232. Existing release executable unchanged. Default CPU parity passed (C005). No engine source edit yet.

B005 identity preflight failed twice before requests: fixed-name strata.exe discovery/singleton JSON, then PowerShell5.1 incompatibility with -AsArray. Corrected to unique configured executable-path matching and ConvertTo-Json -InputObject @(...) without changing request or timing logic. Both failures are retained in failures.json with zero requests, excluded from successful throughput summaries.

B005 first-use excluded short warmup was7.4tok/s and72.847s total; measured short41.5,80.1,79.2 =>median79.2, range41.5-80.1, E2E60.794, TTFT2.057s. Longer76.5,73.0,74.3 =>median74.3, E2E39.316, TTFT6.170s. All measured512tokens, cache0. Early short prefill was also slow (69.8,82.8,108.9tok/s); later long prefill495.3-495.6. Initial description as a persistent build regression was premature: steady requests recovered. Cold JIT/loading is a hypothesis, not established causality. No slow measured run is discarded. B006 repeats the identical build/config in a fresh process before any source patch, to characterize this first-use effect.

## E013 / same-build repeat and opt-in CPU dispatch implementation

B006 repeated B005's identical unchanged CUDA13.3 binary in a fresh process. Short77.5,79.2,79.4 =>median79.2, E2E70.064, TTFT0.869s; longer71.6,73.0,75.1 =>median73.0, E2E38.970, TTFT6.156s. Short prefill recovered to198.6-203.1tok/s; excluded warmup69.7decode. The severe B005 first-use slowdown did not reproduce. No proven compiler throughput improvement over release R00780.2/72.9. B005 slow observations remain in the table. An initial B006 restart hit a transient still-owned port after termination; no request was sent, restart waiting was corrected and the failed attempt is recorded.

Implemented optional per-format gather overrides in isolated branch perf/avx2-format-dispatch, commit2f8f36b, pushed to notmike101/Strata. IQ3_XXS, IQ3_S and IQ2_S accept strict0/1 environment values, invalid/empty/unset inherit the existing per-core/global choice. Only the gather bit changes; VNNI selection is retained. Existing iq256_variant API and default decisions remain. No tensors, routing, sampler, KV or context changes. Candidate executable SHA2566048736d7674d8f3c66ce50060f11ca6623df33d3e885030941a6ef9e62f427c, built from the committed source tree with the identical control toolchain/options.

TDD: C006 compiled against a pass-through implementation and failed exactly six of nine dispatch cases (format overrides), while inheritance controls passed. C007 passed all11 cases after implementation, including invalid-value fallback. C008 passed14/14 dispatch and numerical parity tests. Extended the existing parity test to compare public-dispatch gate/gate-up rows to scalar reference output bit for bit at1..8tokens for every supported format. Default, IQ3S_MT1 and mixed-gather configurations passed. C009 default output matches the preserved untouched control output exactly after removing the six new wrapper-check reporting lines; those new lines also report zero differing rows. Existing ggml relative tolerance remains1e-5. Tests were run outside measured serving requests.

CUDA and CPU paths built on Windows. HIP and SYCL toolchains/devices were not available and were not built or qualified; no cross-backend performance/stability claim or upstream review request. Results remain on their separate report branch. B007 runs the unchanged CUDA control with blanket gather and MT_MIN1; R013 will compare the patched build with only IQ2_S gather overridden to0. This comparison isolates the per-format choice more closely than comparing only against a release binary with different compiler flags. Target80 remains unproven.

## E014 / intermittent slow control, repeated diagnostics, cache-state correction

B007 untouched CUDA13.3 plus blanket gather/MT_MIN1: short78.5,81.5,77.7 =>median78.5; longer71.3,34.9,18.2 =>median34.9. The two severe slow observations are retained. A spot observation during the slowdown showed GPU2010MHz, memory9701MHz,100% utilization,66C,196.98W,697MiB free; CPU performance123% of nominal, available RAM60237MiB, Pages Input/sec0. In a two-second CPU-delta sample the engine consumed4.469CPU-seconds and the largest other process0.078CPU-seconds. These snapshots do not establish absence of GPU migration, scheduling stalls or a hardware problem. Windows shared-GPU-memory counters include the deliberately pinned expert arena and cannot isolate paging.

P003 restarted the identical B007 configuration with only STRATA_DECODE_TIMING=1. Short81.5,77.5,76.6 =>median77.5; longer73.8,71.5,75.8 =>median73.8, all512/cache0. The severe slowdown did not reproduce, so diagnostics did not capture its cause. Long measured windows are approximately21.64-22.86ms, verify17.03-17.89, GPU-reach about10.9-11.1, CPU about5.0-5.7. Treat P003 as instrumented diagnostics, not an optimization winner. R013 now tests the patched mixed-format path without timing flags. Any recovered speed must be compared to normal B006/R011 ranges as well as B007, never claimed as a2x win over the degraded control.

Cache-state correction from source inspection: the startup PROFILE/no-eviction banner describes the cache replacement policy, not the separate adaptive tier. generate.cpp defaults adapt_every4, adapt_swaps96, adapt_decay0.7, adapt_async0, and initializes usage counters when some experts are outside VRAM. Thus current arms adapt residency within and across requests; they start from the same profile after each restart but are not static-residency runs. README corrected. No runtime setting changed by this correction. Earlier interpretation of the banner was incorrect.

Renewed primary-source research: issue616 (https://github.com/Niko1221/Strata/issues/616) reports a much larger isolated gather improvement than served improvement on a different AVX2 laptop; supports treating our kernel microbenchmark as diagnostic only. docs/DETAILS.md and issue781 describe Windows memory-budget effects and the inability of shared-memory counters alone to isolate them. Those are investigation leads, not proof of the cause on this machine. Existing GPU-vision reserve1200 trial was slower overall; CPU-vision memory-margin tests would be distinct experiments.

## E015 / first mixed-format served trial and rejected fusion combination

R013, patched CUDA13.3 build with blanket gather/MT_MIN1 and IQ2_S gather disabled: short 77.7, 79.5, 79.3 tok/s, median 79.3; longer 76.9, 72.2, 77.8, median 76.9. Median E2E 70.059 / 39.948 tok/s; TTFT 0.860 / 6.175 s. Every measured request generated 512 tokens with zero cached input. Compared with normal unchanged-build B006 (79.2 / 73.0), short is tied and longer is +5.3% in this three-seed scan. Because B007 degraded severely, no claimed percentage gain uses B007 as denominator. Candidate remains provisional and below the two-cell 80 tok/s target.

R014 added only STRATA_QFUSE=1 to R013. Short 79.5, 84.7, 80.8, median 80.8; longer 73.4, 71.9, 66.2, median 71.9. E2E 72.013 / 38.674. Although short improved, longer regressed against R013; reject this combination, retain every run. Earlier R008's apparent standalone gain did not transfer reliably to this stack. R015 removes QFUSE and tests only --pool-tasks 10 against R013's automatic 30: same worker count, kernels, model, sampler, and context; only CPU row-task granularity changes.

## E016 / one working branch and contribution identity

User requested one working branch. Merged the tested opt-in CPU source commit 2f8f36b into perf/rtx3090-thinking-80 with merge 98250e0, authored by agent-notmike101[bot], and successfully pushed using the GitHub App identity helper. Deleted perf/avx2-format-dispatch remotely and locally after the merge, archived its clean managed worktree, and verified only the primary checkout remains active. The archive remains recoverable; no needed binaries were inside it. The prepared candidate and untouched control executables remain outside the worktree. The community guide's results-only PR suggestion does not require multiple active development branches; no upstream PR is being submitted.

The new user instructions require the bot identity. Shell discovery still resolved git outside the wrapper directory, so subsequent GitHub reads, commits, merge and pushes use the explicit helper; no personal-credential fallback. The benchmark's workspace revision query now also uses that helper. Previously published commits predate this instruction and retain their existing attribution. Future source rebuilds will use the main checkout in a new build directory rather than the archived source path; recorded historical build outputs and binary hashes remain unchanged.

## E017 / rejected task granularity and delayed adaptive copies

R015 removed QFUSE and changed only --pool-tasks from automatic 30 to 10 against R013. Short 75.4, 78.1, 81.4 tok/s (median 78.1); longer 75.8, 72.0, 70.7 (median 72.0). Reject: this task granularity is slower on the longer workload. Restore automatic 30; keep the nine CPU workers and original host/worker placement.

R016 instead adds only STRATA_ADAPT_LAG=2 to R013. Source generate.cpp waits for the adaptive tier's pending copies two generation windows after scheduling rather than the default one. It retains the synchronization before admitting copied experts, so the CPU/GPU placement decision depends on window count rather than a timing race. Hypothesis: the additional window hides more PCIe copy latency. No expert is skipped, weights and routing remain unchanged, and model/quantization/KV/context/MTP/sampling are frozen. Moving an expert's computation between the existing CPU and GPU kernels can change floating-point rounding; numerical dispatch parity and completed-answer tests are required, not a claim that every sampled output is identical. This is an existing opt-in setting, not another source patch.

R016 short 84.9, 88.9, 86.3 => median 86.3; longer 62.1, 81.1, 82.5 => median 81.1. Median E2E 74.972 / 41.135 tok/s, TTFT 0.923 / 6.166 seconds. One excluded warmup per cell was very slow (14.5 / 15.1 decode), and the first measured longer seed was 62.1. All observations are retained. This first scan meets both median thresholds but is insufficient for promotion because startup variability remains unexplained.

F001 repeats exactly R016 in a fresh process, with five measured seeds 101-105 and one excluded warmup per cell. Short 84.3, 87.9, 88.0, 90.6, 93.7 => median 88.0; longer 83.4, 82.2, 85.4, 82.2, 81.6 => median 82.2. All ten measured runs exceeded 80, each generated 512 tokens with zero prompt reuse. Warmups 81.2 / 78.5 did not reproduce the severe cold stall. Median client E2E 76.427 / 41.409, stream-total 76.442 / 41.412, TTFT 0.902 / 6.168 seconds. These are served decode results with reasoning tokens included, not an 80 tok/s end-to-end claim.

Read-only NVML PCIe/clock/power snapshots were collected late in R016 and during part of F001. R016: 50 samples, 53.09 seconds elapsed, 0.0625 CPU seconds; F001: 131 samples, 139.23 seconds elapsed, 0.015625 CPU seconds. The helper polls NVML's 20 ms PCIe counter snapshots once per second. It is not a continuous trace or per-process attribution. Reported RX values sometimes exceed the expected physical PCIe 3.0 x8 bandwidth, so retain vendor-reported KB/s verbatim and do not interpret them as proven physical throughput or GPU paging. No cause of the intermittent stalls has been established. F001 adds request_started_utc for timestamp alignment only; payload and timing logic are unchanged.

## E018 / finalist behavioral qualification

Q001 on the F001 process: five seeds produced completed Python merge_intervals functions. Every output parsed/compiled and passed five objective cases, including nonadjacent intervals, negative endpoints, empty input, sorted output and input immutability. Ten exact-output tests with and without an unused tool schema passed with natural stop. A 20-turn history followed the latest instruction. Repeated PINE-7319 retrieval passed; the second request reused 65 prompt tokens, recorded separately from cache-zero speed trials. These smoke tests do not establish general coding quality or distributional equivalence.

Q002: declared configuration, live default sampler and observed behavior were checked together. LAN 0.0.0.0:8080, no API key, loaded compatible F16 vision and 262144 maximum context passed. A request without sampler overrides returned the expected answer with thinking. Synthetic image OCR passed. Remote xhigh, medium, low and off requests returned the expected answer, with reasoning present only for the three thinking modes. These are capability checks, not optimization benchmarks; the numeric sampler was unchanged, and all throughput tests retain the fixed high/xhigh thinking contract.

Q003 is a separate near-limit fixed-thinking recall check; F002 will repeat the identical finalist after a process restart with longer-before-short workload order. No throughput claim at 262144 occupied context follows from the short/3K measurements.

Q003 completed: 258901 actual input tokens, zero reused, 162 generated, total 259063. Three synthetic checkpoint codes placed approximately 10%, 50% and 90% into the archive were returned exactly in order; finish_reason=stop. Prompt processing 242651.8 ms (1067.0 tok/s), decode 63087.1 ms (2.6 tok/s), client total 306.267 seconds. Drafts accepted 101/133. Configuration and the frozen high-thinking profile were unchanged. No out-of-memory error occurred. This one request verifies near-limit operation and recall only, not general long-context quality; it explicitly demonstrates that the short-context 80 tok/s result does not extend to a nearly full context. A post-request GPU snapshot reported 23838 MiB used / 485 MiB free; not an inference peak. Stopping the exact service tree before F002 returned usage to 564 MiB / 23759 MiB free. F002 starts a fresh process and reverses only workload order; the same payload bytes, seeds, caps, sampler and engine configuration are retained.

## E019 / identity correction and evidence continuity

At a coordinated Git-write checkpoint after F001/Q001, a separately authorized identity correction changed seven exact prior personal author/committer pairs to agent-notmike101[bot]. It preserved commit trees, messages, timestamps and merge topology; later bot commits changed only parent hashes. Local/fork HEAD changed from 09a6654a0e803ecf728f563e28cac20537db1a5e to 0d2b4f1c0374d990b3877cf72ccb6a9f27a6df01 in place. There was no checkout, reset, clean or runtime/model relocation. The primary checkout and sole working branch remain. Historical identity manifests and ledger entries intentionally retain the commit hashes captured at measurement time; identity-rewrite-commit-map.txt connects them with current history. The candidate source 2f8f36b maps to 1fb2fc6b303423784b6c10a3cb88021d749383df, with the same executable SHA256. Local recovery refs and records are retained.

During qualification export, reopening the already exported Q003 request.json for writing returned Windows OSError22. The file remained readable with the expected 649761 bytes; a temporary copy and atomic replacement succeeded, and the complete export then ran successfully. No model request or benchmark data was changed. This was an evidence-publication file operation failure, not an inference failure; manifest verification remains required before publishing.

## E020 / repeated target result and retained production configuration

F002 restarted the identical finalist through the existing production launcher, with the longer workload first. The same five seeds 101-105, per-cell excluded warmup, 512-token cap, model, engine binary, sampler and configuration were retained. All ten measured request files are byte-identical to F001. Short raw 82.6, 81.4, 86.9, 87.8, 84.4 => median 84.4; longer 85.4, 82.2, 85.4, 86.3, 83.2 => median 85.4. Median client E2E 73.525 / 42.131 tok/s, stream-total 73.540 / 42.138, TTFT 0.919 / 6.160 seconds. Excluded warmups were 84.9 short / 78.1 longer. All measured outputs were 512 tokens with zero prompt reuse. Load-to-health time after launching was 55.509 seconds, separate from request timing. Report files were edited during this run, but no engine source, binary, runtime configuration or sampling file changed; there was no concurrent model request or compiler.

Across both finalist repeats, all 20 measured runs exceeded 80. Ordinary combined medians are 87.35 short / 83.30 longer, ranges 81.4-93.7 / 81.6-86.3. Combined client E2E medians 75.286 / 41.670, stream-total 75.296 / 41.675, TTFT 0.912 / 6.164 seconds. Compared with the same-day original B001 medians 75.1 / 71.3, the complete configuration improves decode by 16.3% / 16.8%. This comparison includes CPU vision placement, the CUDA13.3 local build, opt-in mixed-format gather/MT_MIN1 and adaptive lag2; it does not attribute the total gain to any single change. B006's normal unchanged CUDA13.3/CPU-vision control was 79.2 / 73.0. No percentage claim uses the severely degraded B007 denominator. Preliminary R016 slow observations remain published, so this is not a guarantee of 80 tok/s for every future run or arbitrary input.

Q004 passed five structured lookup_ticket tool-call round trips, seeds101-105: correct function name and JSON ticket_id, tool_calls finish reason, preserved tool-call IDs, synthetic tool result, then the exact requested final answer with natural stop. No external tool action was executed. Q005 repeated service/default-sampling, keyless LAN, F16 OCR and xhigh/medium/low/off checks on the final F002 process; all passed. Q001's five completed coding outputs passed all objective cases. The numerical dispatch tests remain 14/14 from C008; no engine source changed after them. CUDA and CPU were built/tested, HIP and SYCL were not available. Cancellation/retry recovery and a separate remote physical client's network overhead were not qualified.

Retain the finalist in the production config used by the existing user launcher: CPU F16 vision, gathered IQ3 paths with IQ2_S gather disabled, MT_MIN1 and ADAPT_LAG2. No benchmark seed, output cap, profiler flag, alternate sampling or task-granularity override is installed as a production default. Model IQ3_S, context262144, INT8 KV/32768 resident, MTP4/.70, PCIe share.20, one request, LAN0.0.0.0:8080 and keyless access remain. The server remains running because the user requested an operational service. No additional benchmark model is resident. The temporary implementation branch is merged/deleted, its worktree archived, and the only working branch is perf/rtx3090-thinking-80.

The declared short/3K served-decode target is demonstrated in two fresh-process five-seed repeats with opposite workload order. At 258901 input tokens, Q003 instead measured 2.6 decode tok/s while correctly retrieving all three codes. Preserve this substantial context-depth limitation, the CPU-vision latency tradeoff, small VRAM headroom, limited correctness scope and unexplained historical stalls in any summary. These results do not establish universal quality equivalence or 80 tok/s at a nearly full context.

## E021 / new 90 short / 85 longer target, with prompt-read preservation

The user raised the target to90 tok/s short and85 tok/s at approximately3K input, explicitly requiring the same parameters, no quality loss and no prompt-read regression. The promoted F001/F002 configuration is the fallback. New campaign contract: same model/quant, context/KV, CPU vision, sampler/high thinking, request bytes, output cap512, seeds101-105, one request and fresh-process confirmations. MTP4/.70 and PCIe share.20 stay fixed. Judge both server decode and fresh prompt throughput; retain clientE2E/stream-total/TTFT as separate regression metrics. Three-seed scans can reject ideas but cannot complete the target. Small apparent losses within noise are inconclusive and require paired repetition; no automatic5% regression allowance. Preserve all observations, including slow warmups and measured seeds.

A fresh upstream fetch and latest-release API check still returned fb58e0 / v0.1.41; no update was available. No CodeGraph index exists. Same working branch and bot identity helper retained. B008 restarts the unchanged promoted configuration for a five-seed control before any new runtime change. Host snapshot was refreshed locally; private process/network inventory is not published.

First candidate R017 changes only STRATA_ADAPT_LAG2 to3. Source generate.cpp accepts positive integer lags, retains cudaEventSynchronize before admitting copied experts, and skips scheduling a new adaptive round while pending copies exist. Hypothesis: another window of overlap hides additional transfer wait; counter-risk: later residency adoption reduces cache effectiveness. Existing issue764 provides the mechanism on different hardware, not proof of gain on this host. No asynchronous timing-dependent admission, tensor/kernel precision or routing shortcut is introduced. The previously rejected QFUSE/task10 combination is not being recycled without new evidence.

## E022 / fresh control reproduces transient stalls; stage diagnostic

B008 is the unchanged F001/F002 production configuration, not a new optimization. Five short runs:89.2,25.5,18.7,59.9,89.3 => median59.9; longer82.2,74.9,75.9,84.3,76.7 => median76.7. Prompt medians195.8 /495.4, with short range64.1-213.1 and longer493.6-496.2. All runs remain published. The first short warmup73.6 is excluded as predeclared. This reproduces the historical intermittent slowdown without a source or tuning change. Promotion was suspended to collect diagnostics; no gain may be attributed to recovery from these low values.

A snapshot during the slow period reported GPU2010MHz, memory9701MHz,P2,92% utilization,222.67W,67C,466MiB free; available RAM57960MiB, Pages Input/sec0, CPU performance121.05% nominal. These are snapshots, not proof that all resources were unstressed. The read-only NVML logger collected107 samples over113.64s using0.03125CPU seconds, beginning after the slow period had started. Its PCIe counters retain the previously documented interpretation limitation. Exact numerical counters do not establish a paging cause.

P004 restarted the same configuration with only STRATA_DECODE_TIMING=1 added. Short87.0,87.9,84.3,91.0,88.0 => median87.9; longer85.2,87.2,82.9,86.8,82.6 => median85.2. Prompt medians202.1 /495.3; E2E77.137 /42.091. No severe stall reproduced. This is diagnostic, not an optimization winner or a replacement for the failed control record. An example longer window averaged19.84ms: verify17.97, GPU-reach wait11.64, CPU5.18, draft1.36. The final longer sample averaged20.26ms, GPU-reach11.67, CPU5.65. GPU/transfer-side waiting dominates, with remaining CPU work material. No root cause of the transient stalls is established.

R017 proceeds without instrumentation, testing only lag3 against the normal F001/F002/P004 range as well as the full current control. If overlap does not help, R018 will change CPU task granularity only from automatic30 to60, keeping worker count and kernels fixed. Hypothesis: smaller row tasks reduce tail imbalance in the remaining CPU expert work; counter-risk: atomic/task scheduling overhead. The earlier10-task scan lost, so more tasks is a distinct falsifiable scheduling direction rather than a repeated rejected setting.

## E023 / lag3 rejected

R017 short87.8,88.9,75.0 => median87.8; longer81.6,82.0,83.6 => median82.0. Prompt medians198.9 /494.4; E2E76.482 /41.275. Neither new generation target is met, and longer decode does not improve on the normal lag2 range. The0.2% longer prompt-read difference is too small to establish a causal regression on its own, but there is no compensating proven gain. Reject lag3 and restore lag2. R018 tests task60 alone against the promoted stack. If needed, a later host-core-last retest will be explicitly labeled: old R001 was confounded by an equally slow restored control, and the current stack has changed CPU kernels and adaptive lag since then; a recovery will not be attributed to placement.

## E024 / scheduling scans and independent coding-cache preparation

R018 changes only pool-tasks30 to60: short89.1,87.0,88.1 =>88.1; longer86.1,87.0,82.4 =>86.1. Prompt medians196.4 /495.5; E2E76.513 /42.379. This three-seed scan meets the longer generation target but not short90. Its small gain needs paired confirmation; do not promote it yet.

R019 restores task30 and changes only host-core first tolast: short89.7,84.2,88.3 =>88.3; longer86.7,86.1,81.6 =>86.1. Prompt medians195.6 /497.1; E2E76.836 /42.461. Again short90 is unmet, and the short differences from task30 control are small. No claim that this recovers the earlier R001 slowdown; that control was confounded. No candidate has replaced the promoted fallback.

After three marginal/losing scheduling/overlap directions, reassessed expert residency. Upstream issue1348 on a different dual3090/Q4 machine reports significant miss cost and unsuccessful prefetch experiments; its estimates are not local performance evidence. Our P004 still spends roughly5ms/window on CPU experts, so reducing misses is a distinct hypothesis. Existing --expert-profile-save records cache placement rankings without changing model weights. T001 starts from the original profile and processes eight synthetic coding tasks in Rust, TypeScript, SQL, C++, Python JSON Pointer, Go, Java and C#, seeds201-208,512-token caps, the unchanged thinking sampler. None uses the benchmark TTLCache request. Save the resulting ranking after the eighth item with an unrelated sentinel, copy it to a new frozen data file, then disable profile saving for all measured candidate runs. No benchmark answers train the candidate profile.

R020 will change only the startup expert ranking to that frozen file, keeping task30,host-first,lag2 and all quality parameters. Save its exact hash and preparation requests; add a per-request unchanged-profile guard and a per-arm profile hash to the measurement manifest. These identity checks occur outside the timed interval. The experiment tests cache placement, not model fine-tuning or altered routing decisions. Faster benchmark results alone will not establish generality; completed coding/tool/vision tests and prompt-read preservation remain required.

## E025 / frozen profile rejected; GPU branch overlap revisited

T001 produced196632 bytes, SHA256d51bd5bef1f20e7bf9e2732ba0a16dea2b382219bfff6a78f7b2d4bf7da21068. The exact synthetic preparation requests/responses and base64-encoded ranking are retained under profile-preparation. R020 short85.6,91.4,86.0 =>86.0; longer83.5,81.0,23.2 =>81.0. Prompt medians201.2 /495.0; E2E75.264 /41.038. The severe third longer slowdown is retained. This profile did not improve the normal range or meet either target; reject and return to the original ranking. No model weights changed or benchmark prompts leaked into preparation.

R021 returns all baseline execution settings and adds only STRATA_DF_BRANCH=1. This was tied in the old R010 stack; the new motivation is P004's GPU-reach wait dominating after CPU dispatch and lag improvements. Source verify.cpp schedules only independent mixer-input branches on side streams with explicit fork/join dependencies. It does not change arithmetic kernels or sampling. The known Linux/GSP/NVML hang report is not a Windows result, but any hang or regression here disqualifies it. No claim of a benefit before measurement. Other considered flags were not run: GR_DOWN_MAX4 is superseded for this active staged/exact-token path, and the default pool spin timeout is already20ms, much longer than normal inter-layer gaps, so increasing it lacks a demonstrated bottleneck.

## E026 / mixer overlap rejected; combined scheduling scan

R021 short18.7,31.0,85.3 =>median31.0; longer85.9,82.1,83.8 =>83.8. Prompt medians60.8 /495.2; E2E26.575 /41.769. The excluded short warmup was50.0. This reproduces severe short-run stalls and does not improve longer generation; reject DF_BRANCH. The slowdown is not excluded or used as an artificially low gain denominator. Arithmetic kernels and fixed sampling remained unchanged.

R022 combines the two provisional scheduling changes: pool-tasks60 and host-core last, retaining lag2 and the original expert profile. R018 and R019 separately reached86.1 longer but only88.1/88.3 short. This combination tests whether reduced row-task imbalance and host placement compose; no assumption of additive gains. All other model, context, sampler, draft and memory settings are the promoted fallback. Three measured seeds are a rejection screen, not sufficient evidence of target completion.

## E027 / combined scheduling and CPU worker screen

R022 pool-tasks60 plus host-core last: short83.4,88.5,86.1 =>86.1; longer81.6,85.6,84.0 =>84.0. Prompt medians200.3 /497.3; E2E74.306 /41.898. Reject: neither generation threshold, and the separate provisional gains did not compose. R023 returns original scheduling and changes only workers9 to8, explicitly retaining30 tasks instead of allowing the automatic task count to fall to27. Hypothesis: less worker contention or scheduling tail latency; same expert arithmetic and task partition.

After repeated scheduling ties, renewed upstream research through the bot helper. PR1415 adds exact ggml-order singleton AVX2 rows, with a reported2.45% gain on a different i7-12700KF/3060 and older IQ3_XXS stack. Our current MT_MIN1 already uses AVX2 single-token work, so that report is not directly applicable and the patch is not applied. PR1524 concerns four concurrent requests and explicitly claims no single-request speedup; excluded from this fixed one-request campaign. Issue1412 confirms large-page allocation requires SeLockMemoryPrivilege in a fresh logon token and provides no throughput A/B. This host still uses pinned4KiB pages; no sign-out, privilege change or restart performed. References: https://github.com/Niko1221/Strata/pull/1415 , https://github.com/Niko1221/Strata/pull/1524 , https://github.com/Niko1221/Strata/issues/1412 .

## E028 / worker reduction rejected; adaptive frequency hypothesis

R023 workers8/tasks30: short84.6,85.9,85.7 =>85.7; longer83.6,82.6,76.8 =>82.6. Prompt medians193.6 /495.6; E2E74.623 /41.473. Reject: fewer workers did not improve the remaining CPU contribution. Restore nine workers. R024 changes only --adapt-every4 to8, preserving swap budget96, deterministic lag2 and the original startup expert profile. Source generate.cpp runs the adaptive selection/copy thread every specified number of verification windows. Halving its frequency may reduce transfer/coordination overhead, at the risk of additional CPU misses; no expert or tensor computation is omitted.

A separate CPU diagnostic is prepared, not yet run: C010 compares STRATA_IQ_PREFETCH2048(default),0,4096,1024,2048 with the already-built candidate parity executable. It uses256MiB of deterministic synthetic blocks per actual model gate/up format, one pinned physical CPU,1/2-token groups,five repetitions. Hardware prefetch hints do not alter arithmetic. Stop the serving engine before this CPU measurement. The repeated2048 control detects drift; a microbenchmark gain alone cannot qualify a production change.

## E029 / CPU diagnostics rejected and VRAM-margin screen

R024 adapt-every8: short86.6,87.4,89.5 =>87.4; longer85.2,84.9,84.5 =>84.9. Prompt medians201.0 /496.4; E2E76.261 /42.065. Both generation thresholds remain unmet. Restore adapt-every4; this marginal longer result does not justify promoting another execution change.

C010 ran after stopping the serving engine. The first launch was correctly stopped by the process guard while the old engine was still exiting; no measurement ran then. All five subsequent prefetch processes completed. Disabling prefetch was worse. Distances1024/4096 gave mixed small changes within the drift seen between the two2048 controls; retain default2048 and do not extrapolate a served gain.

C011 is a Windows-only diagnostic of the existing ExpertPool, not a production engine patch. It hard-pins the host to the first physical core and compares9 versus18 workers on the other nine cores, verifies affinity, keeps30 tasks, and checks bitwise output equality. Synthetic256MiB streams cover IQ2_S,IQ3_XXS,IQ3_S with IQ4_NL down,1/2 tokens,1/3/6 expert jobs. ABBA9/18/18/9 pools, five passes of200 layer calls each,360 raw timings. All72 initial output checks passed (18 reference sets and54 bitwise comparisons);18 workers were slower in17/18 cells, by0.05-15.66%, and only IQ3_XXS/one-token/three-jobs improved4.69%. Reject SMT without modifying the engine. Initial diagnostic compilation failed on /MD versus the candidate libraries' /MT and missing advapi32; corrected build passed. Failed compiler output was overwritten, disclosed in diagnostics/README.md. This does not affect any inference evidence.

R025 returns the promoted fallback and changes only vram-reserve-mib700 to1100, five measured seeds per cell. Startup has repeatedly warned that the baseline free VRAM is small under WDDM, and historical stalls remain unexplained. The hypothesis is that an additional400MiB requested margin reduces residency pressure; the counter-risk is a smaller expert cache and more CPU work. No paging cause is established and no stability or throughput claim follows from merely requesting the margin. Model, precision, context/KV allocation, sampler, MTP, PCIe fraction, workers, task policy and adaptive timing are unchanged. Reject if it loses throughput; do not trade speed for unproven stability.

## E030 / reserve trial fails; thermal-event diagnostic

R025 requested reserve1100: short86.2,87.6,83.3,86.0,88.3 =>86.2; longer26.4,17.2,12.5,40.7,80.3 =>26.4. Prompt medians200.1 /473.0; E2E75.743 /19.987. Reject. Larger reserve neither demonstrated faster decode nor eliminated severe stalls, and longer prompt-read also fell. During the third longer run, a ten-second OS sample showed no pages input, aggregate disk read latency0.142-0.160ms, disk reads0.13-1.73MB/s, CPU performance120.05-120.70% of nominal. A GPU snapshot showed969MiB free,2010MHz SM,9701MHz memory,94% utilization,215.27W,70C core. These bounded snapshots do not exclude every scheduling/storage/memory issue. Storage reliability/temperature query was unavailable due to CIM access restrictions; no elevation or settings change attempted.

A later snapshot near the end of the fourth/fifth longer transition showed active clock-event mask0x20, documented by NVIDIA as software thermal slowdown (core or memory operating limit). Core temperature alone cannot exclude memory thermal pressure. Direct memory-temperature telemetry returns NVML_ERROR_3 (not supported) on this device/driver. This is an observed event, not yet an attribution for the severe slowdown. Official reference: https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlClocksEventReasons.html .

P005 returns the unchanged reserve700 fallback with only STRATA_DECODE_TIMING=1, ten measured seeds per cell to increase the chance of capturing a stall. A read-only1Hz NVML logger records clocks, power, temperature, PCIe, current clock-event mask, thermal-policy counter and fan speed. Early normal87-89tok/s requests also contain0x20, and automatic fans reach97-100%; therefore the flag alone does not distinguish severe stalls. The thermal duration field has remained constant in the early samples despite flag transitions; retain that inconsistency instead of inferring unmeasured memory temperature. Exact sampler and request template remain frozen; additional seeds106-110 are diagnostic and are not substituted into the five-seed promotion contract.

Prepared but not run: R026 is the exact fallback with both GPU fans at100% for a time-bounded A/B, restoring each prior policy afterward. No clock, voltage or power limit change. Automatic fans already approach100%, so little sustained improvement is expected; this is a falsification of a cooling-ramp hypothesis, not a speed claim. Also inspecting STRATA_TSUM: an existing exact GPU reduction schedule with no extra weight allocation. It requires the native multi-column bitwise parity test on this GPU before served testing; Q6 packed copies would consume roughly700MiB extra and are not being enabled speculatively in this memory-constrained setup.

## E031 / diagnostic outcome, denied fan change, exact GPU reduction

P005 ten-seed diagnostic: short88.0,88.6,87.1,88.4,86.7,86.1,84.9,89.0,89.3,81.9 =>87.55; longer85.7,86.8,85.9,80.1,80.5,85.9,82.4,85.0,87.9,83.0 =>85.35. Prompt medians198.05 /496.45; E2E76.526 /42.209. The severe stall did not reproduce. Normal windows retained roughly10.5-11.7ms GPU-reach wait and3.6-5.7ms CPU contribution. Current thermal-event flags occur at normal speed too; neither those flags nor the larger-margin experiment establishes the stall's cause. NVML logger270 samples/286.40s consumed0.344CPU seconds. The unsupported memory temperature is recorded explicitly. No low measured run from previous arms is removed.

R026 was not run. The first nvmlDeviceSetFanSpeed_v2 call returned NVML_ERROR_NO_PERMISSION (4). No fan policy or speed was changed, and no benchmark request was sent. Both initial policies were automatic. Do not present this as a failed throughput result or a cooling improvement. No elevation or alternate fan-control API was attempted.

C012 compiled the existing mmvq_multi_parity test against the already-built candidate GPU/core libraries and CUDA13.3 runtime, with no engine source change. STRATA_TSUM=0 and1 each passed148480 bitwise comparisons against the single-column reference with zero non-finite outputs; the negative control found63901 finite differences, demonstrating test sensitivity. R027 changes only STRATA_TSUM=1 on the promoted fallback. This existing flag changes the GPU reduction schedule for multi-column dense matvecs, keeping the arithmetic result exact and allocating no new weight copy. Five measured seeds per cell; no promise that a kernel-level change improves served throughput.

Next evidence-backed direction if needed: docs/MMVQ_IL_TABLE.md explicitly describes per-card exact row-layout tuning. The shipped sm86 table compromises between an RTX3060 and RTX5070; this3090 has not been measured by that table. The existing mmvq_il_parity --bench --emit-table measures every row choice and verifies bitwise equality, with a3% per-cell threshold and conservative handling of conflicting shapes. Prepare that diagnostic against the same candidate libraries, stop serving before running it, and test any emitted table through the unchanged service. Do not replace defaults or claim an engine improvement from microbenchmarks alone.

## E032 / reduction rejected; measured per-card matrix layouts

R027 STRATA_TSUM1: short85.0,87.0,90.4,88.4,82.7 =>87.0; longer88.8,84.8,83.0,83.1,82.7 =>83.1. Prompt medians188.4 /496.2; E2E76.367 /41.696. The excluded short warmup was11.5tok/s, retained. No improvement meeting the two targets; remove TSUM. The successful bitwise kernel test does not make this a throughput winner.

C013 follows docs/MMVQ_IL_TABLE.md using the existing mmvq_il_parity source linked against the exact candidate GPU/core libraries, without rebuilding or modifying production kernels. Stop the server, run two full --bench --emit-table sweeps in separate processes. The fixture checks every row choice against plain native_mmvq bit for bit, including finite-output checks; timing streams weight copies beyond L2. Because the upstream emitter compares against the plain kernel, our selector is stricter: retain the shipped table unless a candidate beats the currently selected shipped row choice by at least3% for every measured shape in that class in both sweeps. Unmeasured or inconsistent cells keep the shipped choice. All raw timings and the selection script are retained. Any resulting table is an opt-in environment override, same precision and arithmetic, subject to full served rejection/confirmation gates.

## E033 / exact per-card table selected

C013a andC013b both completed every testedT2-4/rows1,2,4/table comparison with bitwise equality and finite outputs. The fixture times200 kernel calls after200 warm-up calls for each shape/choice, streaming weight copies beyond L2. These are per-call averages, not five-seed served results; substantial between-sweep absolute timing variation remains in the raw logs. The stricter two-sweep selector retained nine changes: Q5_K T3/class1 rows4->2; Q5_K T4/classes1,2 rows1->2; Q6_K T2/class4 plain->rows1; Q6_K T3/class4 rows2->1; Q6_K T4/class1 plain->rows2; IQ4_XS T2/classes2,3 plain->rows2,4; IQ4_XS T4/class1 rows1->2. Worst per-cell candidate/control ratios across all measured shapes and both sweeps range0.800-0.967. No unmeasured class changes.

R028 changes only STRATA_MMVQ_IL_ROWS to the exact selected table, on the original promoted fallback with no TSUM, no extra VRAM copy, no speculative/sampling/context/precision change. Five measured seeds per cell. Full table and selection evidence are in diagnostics/C013-il-selection.json. A positive kernel result does not imply a served improvement; require the declared generation/prompt-read gates and fresh-process confirmations before retention.

## E034 / microbenchmark gain did not transfer; shared-stream screen

R028's first five short requests86.5,89.5,85.8,90.6,85.4 give86.5tok/s median, below90. The kernel-layout improvements did not establish a served gain; do not promote the table. Full longer results remain in raw evidence. A microbenchmark cannot substitute for whole-request throughput.

Final bounded scheduling screen R029: return all promoted baseline settings and change only STRATA_SH_STREAM=0. Source verify.cpp normally forks the shared expert onto a second CUDA stream and joins it per layer. The alternate executes the same arithmetic in the main stream, removing fork/join scheduling but also losing overlap. The existing HIP gain is not NVIDIA evidence; the local hypothesis is that this driver's graph scheduling/VRAM-bandwidth contention may cost more than overlap saves. This is falsifiable in a three-seed rejection screen. If it fails, restore and remeasure the established fallback; no lower-quality or lower-prompt-rate configuration will be installed simply to show a changed result. The90/85 target remains unmet.

## E035 / no accepted improvement; restore the qualified fallback

R028 complete: longer85.4,80.6,83.2,84.7,80.2 =>83.2; short86.5. Prompt medians199.1 /495.6; E2E75.823 /41.685. Reject the nine-cell exact layout override: microbenchmark wins did not transfer to the declared two-cell served target.

R029 shared stream off: short82.2,79.2,83.9 =>82.2; longer79.7,80.8,77.7 =>79.7. Prompt medians198.8 /496.5; E2E72.502 /40.776. Reject: removing shared-expert overlap loses on this GPU. Return to the shipped CUDA stream behavior.

Twelve new runtime candidate configurations were measured in this90/85 follow-up (R017-R025,R027-R029), plus repeated controls/stage diagnostics and CPU/GPU microbenchmarks. None passed the full generation/prompt-read acceptance contract. R026 was a denied hardware-control attempt with no mutation and no throughput result. The target is not declared achieved, and no candidate from this round is promoted. B009 is a fresh five-seed restart of the exact previously qualified F001/F002 fallback with the longer cell first. The unchanged fallback, not any rejected trial, is the intended retained service. Sampling, model/quant,262144 context, INT8 KV/32768 residency, CPU F16 vision, MTP4/.70, PCIe.20, keyless LAN and remote reasoning levels remain unchanged.

The remaining evidence supports GPU/transfer waiting and CPU expert work as material costs but does not establish an immutable hardware ceiling. Intermittent severe stalls also occur in unchanged controls and remain unexplained; thermal-event snapshots, larger VRAM reserve, ordinary disk latency and zero sampled paging do not identify their root cause. Future work should capture a genuinely slow window with stage/scheduling telemetry before more parameter sweeps. Large pages would require an appropriate fresh Windows logon token; no user-right or login changes were made. No quality relaxation, lower context, lower precision, altered sampler, overclock, clock lock or power-limit change is accepted as a shortcut to the goal.

## E036 / restored-state measurement and verification

Follow-up outcome: 90 tok/s short / 85 tok/s at approximately 3K input has not been demonstrated under the full contract. Twelve new runtime candidates and CPU/GPU diagnostics produced no accepted improvement; the exact previously qualified configuration is restored. The final five-seed control measured 85.9 / 83.6 decode tok/s, fresh prompt-read 194.2 / 495.5 tok/s, and client end-to-end 75.31 / 41.80 tok/s (short / longer). See [follow-up-summary.json](follow-up-summary.json), [the fixed contract](contract-90-85.md) and ledger E021 onward. Intermittent severe stalls in earlier unchanged controls remain unresolved; the successful measurements below are retained, not a guarantee of every future run.

Q006 rechecked keyless LAN access, context262144, numeric/default thinking sampling, F16 vision OCR and xhigh/medium/low/off through the normal service; all passed. The loaded engine hash and parsed runtime config match the previous fallback exactly. No additional quality claim is inferred from the synthetic512-token speed probes. The earlier completed coding/tool/history and near-limit recall checks remain the qualification of this unchanged engine/config; the near-limit2.6tok/s result is not replaced by these short/3K numbers. The service remains running. No experimental sampler, profiler, custom layout, TSUM, cache profile, task/worker change, extra reserve or fan policy was retained. The sole working branch remains perf/rtx3090-thinking-80; source/evidence stay on the existing fork, with no upstream PR or merge.

## E037 / explicit persistent 90 tok/s goal

The user requested create_goal without a token budget. get_goal returned null; a new active goal was created for90tok/s server_decode_tps on the exact ISTA-DASLab Flash-Next GSQ-RCO IQ3_S model. See goal-90-contract.md for the frozen matrix and completion rules. The90 target now applies to both short and approximately3K qualifying cells; no threshold reduction is inferred from previous results. Native CUDA remains the only locally qualified backend. No model/quant, sampler, context, quality or prompt-rate concession is authorized.

B010 re-establishes the exact restored control through the production launcher, five seeds per original TTLCache cell, after a fresh process start. It is a baseline, not a new candidate. A separately selected and frozen random coding task will extend the real-use matrix with compilation/tests, cold and exact-repeat cache controls. Keep the original fixtures so prompt choice cannot masquerade as optimization. Recheck upstream before implementation. Investigate the unexplained stalls using existing stage and Nsight evidence; avoid another blind parameter sweep. No benchmark process is to remain resident at handoff under the new user instruction.

## E038 / fresh control stalls; a less intrusive CUDA trace

B010 unchanged control, short seeds101-105: 87.2, 90.0, 21.7, 17.5, 85.9 tok/s, median85.9. Longer: 82.4, 85.0, 85.6, 82.6, 84.8, median84.8. Prompt-read medians77.0 / 495.3; client E2E62.817 / 42.072. Short prompt processing also slowed on the degraded requests. All outputs512, all cache0. No run is removed and no gain will be calculated against the stalled samples alone. These results fail the90 target and expose a stability concern even though the median hides most of the stall cost.

Read-only NVML telemetry was attached late in short-run4 and through the remaining requests: 133 snapshots over140.89s, 0.156 CPU seconds. During its final slow seconds the GPU reported2010MHz SM,9701MHz memory,176-213W and approximately67-73 thousand KB/s PCIe RX; normal decode later used much greater sampled traffic and power. These are20ms device snapshots, not continuous throughput, and cannot assign a stall to a process or prove a bottleneck. A100-sample Windows performance-counter capture showed process dedicated/shared allocations and OS pages-input; mapped pinned expert RAM is expected to appear as shared GPU memory, so its54.6GB allocation is not itself proof of VRAM eviction. Exact counter values and collection timing are retained. No OS/GPU settings changed.

Fresh upstream fetch: origin/main remains fb58e0dbc8399662c0e47c76578c6e878b14f6cf, latest release v0.1.41. Open PR1741 avoids CUDA device switches in the pipelined Verifier::service idle loop; our single-GPU path uses Verifier::run, so do not apply a multi-GPU fix without relevance. PR1742 and1744 concern prefill-only fused-kernel changes on a Linux3060; useful prompt-speed leads, not evidence for this decode target. Approximate route-tail/routing-prior PR1668 explicitly changes output and is excluded.

P006 repeats the unchanged control with host decode timers and Nsight CUDA graph-node tracing, disabling CUDA event tracing and omitting STRATA_VERIFY_PROFILE. This preserves the native shared-expert side-stream path, unlike old P001's GPU phase stamps. Five seeds per original workload, one warmup each; all profiled rates are diagnostic only. Stop the exact service/session afterward and verify no Nsight agent remains before an uninstrumented baseline. WDDM memory tracing requires administrator privileges according to installed Nsight help; no elevation attempted. Official analysis guidance: https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html .

The extra coding problem was selected once, before inference, using recorded seed16098675157555674653 from a fixed list of three tasks: topological_order. Freeze the exact selected prompt, archive and reference tests. The original TTLCache fixtures remain in the target matrix, so a faster coding task cannot replace them.


## E039 / correction: node traces are incomplete, not whole-request profiles

P006 completed twelve API requests, but SQLite diagnostics reveal CUPTI dropped9,233,555 records after failing to allocate buffers. Kernel activity covers5.387-19.723s of a197.306s capture. The trace reports forced flushing, which can insert synchronization. Consequently the42.3 /42.5tok/s profiled medians are instrumentation results, not production regressions or evidence about the uninstrumented17-22tok/s stalls. Summed kernel/API rankings describe only the retained early interval. No kernel optimization is selected from those percentages alone.

A retrospective integrity check found the same problem in P001: 2,954,609 dropped records; kernel activity5.236-23.821s of81.533s. E002 already disclosed GPU-phase instrumentation changing overlap; add incomplete capture as a second limitation. Earlier uninstrumented baseline/candidate timings and objective tests are unaffected. Raw completeness diagnostics, exact record counts, report hashes and the retained aggregates are published. This correction supersedes any reading of those aggregates as complete capture-wide bottleneck shares.

P007 is prepared with whole-graph CUDA tracing instead of per-node tracing, still no GPU phase stamps, CUDA event tracing disabled and host decode timers. The installed Nsight help explicitly states whole-graph tracing reduces overhead by omitting node events. Require zero dropped records and trace coverage spanning the measured requests before interpreting its chronology. Its measurements remain diagnostic and cannot complete the goal.

B011 reloaded the unchanged production configuration after exact profiler-agent cleanup. It measures the selected topological-order problem, short and archived-context forms, five miss/hit pairs plus one warmup pair per size. The cache-hit requests are exact payload repeats; the engine must report positive reuse. Completed coding answers use an independent8192-token quality allowance. A72-case topological checker passed a correct implementation and rejected a sorted-list implementation that fails cycle handling; generated answers have not yet been qualified.

Architectural alternative queued for a bounded offline probe C014: the existing exact packed Q6_K output-head layout on actual model weights. Unlike toggling many host parameters, this changes weight access layout for a large dense projection. First measure bitwise parity and paired head timings without a serving model. Only if the gain is material consider a production candidate, accounting for the extra head/draft VRAM and cache displacement. The existing implementation allocates a second copy, so no low-memory launch or quality promise is inferred. No production source change yet.


## E040 / coding/cache baseline and failed completion gate

B011 used the unchanged engine/config, no profiler modules loaded, selected topological_order task, five seeds101-105 per cell. Short cache-miss decode87.6,91.4,94.2,90.9,89.8 =>90.9; short exact-repeat hit91.7,90.7,93.3,92.9,95.6 =>92.9. Approximately3.1K miss92.6,87.6,90.4,89.9,85.6 =>89.9; hit85.6,86.3,90.6,84.9,86.0 =>86.0. Every request generated512 tokens; every declared miss had zero reused tokens and every declared hit had positive reuse (all but five prompt tokens). Miss prompt-read medians199.3 /510.1; miss E2E79.227 /43.176; hit E2E91.478 /84.815. This is a baseline on an additional fixed prompt, not an optimization gain or a replacement for TTLCache results. The required90 medians are not met in all cells.

Q007 natural-stop coding gate used the same selected problem and thinking sampler with a separate8192-token allowance. Seeds101 and105 exhausted8192 tokens in reasoning without a final function: failures, retained. Seeds102/103/104 stopped after4121/4415/8079 generated tokens, compiled, and each passed72 objective cases (including duplicate edges, missing endpoints, cycles, isolated nodes, lexicographic order and input immutability). Thus3/5 passed and the qualification gate fails. The512-token speed probes remain partial reasoning, not compiled-answer evidence. No sampler, reasoning budget, prompt or cap is changed retrospectively to relabel these failures as passes. This does not identify an arithmetic regression; it bounds the unchanged model's completion behavior under this finite allowance.

No production configuration is promoted. Goal remains active. P007 whole-graph profiling now runs on a fresh exact control, with automatic cleanup of its own named profiler agent. C014 isolated packed-head parity/timing follows only after the serving model exits. Nonstream matrix and exact-model portable Vulkan comparison remain pending.


## E041 / reject packed head; whole-graph capture remains incomplete

Correction to the live interpretation of B010 Windows counters: their100 samples cover20:10:28.439-20:12:08.538UTC, after short-run4 ended around20:10:21.36UTC. Pages Input/sec ranged0-5541.92; it was not always zero. They cannot exclude paging/eviction during the slow request. Process dedicated/shared allocations were constant at24,492,236,800 /54,587,858,944bytes; these allocation counters do not measure residency transitions. Late NVML samples overlap the stall but do not attribute its cause. Retain all telemetry and this limitation.

P007 reduced event volume with whole-graph tracing, but CUPTI still dropped1,434,033records after buffer-allocation failures. Graph records cover6.584-20.240seconds of136.683seconds; kernel records5.320-20.197. This is another incomplete early interval, despite all twelve HTTP requests completing. Profiled median decode80.6 /78.2 and prompt128.4 /494.2 are diagnostic only. Renamed the mistakenly named local folder P007-node-profile to P007-graph-profile to match the actual graph trace command, retaining every request. Published trace-completeness counts, hashes and partial aggregate tables. Exact service and its named Nsight agent exited; no profiler remained before the next diagnostic.

C014 loaded only the actual Q6_K output head248320x2560 and tested existing STRATA_Q6_PACKED against the native GGUF layout. Outputs were bitwise equal for1-4columns. Eleven paired samples per timed shape gave native/packed median microseconds: one column599.0/984.3, two823.1/858.3, four1196.0/1617.9. Packed costs4.3%-64.3% more time plus497.3MiB; reject it, no full-model candidate or launcher change. This isolated exactness test is not a complete model-quality gate or served TPS. The first wrapper attempt incorrectly treated routine native stderr as a PowerShell error; the wrapper was corrected to redirect stdout/stderr through Start-Process, then the complete test passed parity and failed performance. All final timings and their ranges are retained. The model allocation was released afterward.

Next architectural comparison: portable llama.cpp b11538 Vulkan recognizes the RTX3090 and exposes CPU MoE placement plus an expert GPU cache. Exact GGUF metadata identifies qwen4exp,48blocks,512experts,2560embedding and262144context. First establish whether this build loads that architecture and compatible vision with the full configured context; record raw target decode separately if native MTP is unavailable. It cannot qualify merely by loading or by changing the fixed sampler. Native CUDA remains the retained backend.


## E042 / bounded profile limitation; CPU architectural experiment

P008 captured only one fixed short coding request after one excluded warmup, with graph-node tracing and1000ms CUDA flushing. It still dropped344,406CUPTI records. Kernel coverage1.183-9.777s versus11.289s capture; measured HTTP interval10.058s. Its56.1decode tok/s is instrumentation overhead, not a production measurement. The warmup also ran with the injection library loaded and is not an uninstrumented control. No aggregate percentage from P008 is treated as a complete critical-path share.

NVIDIA's current Nsight release notes explicitly list unreleased CUDA event buffers for applications using several streams from several threads, with the same allocation-failure diagnostic; they also warn CUDA tracing requires spare device memory. These are possible explanations, not a locally proven root cause. The1000ms flush experiment did not fix completeness. Source: https://docs.nvidia.com/nsight-systems/ReleaseNotes/index.html accessed2026-10-09. Do not keep repeating a full multi-request trace with this failing setup. A bounded whole-graph interval or targeted kernel/pool probe is the next diagnostic path. Exact service and named profiler agent were removed afterward.

C015 design is recorded in cpu-expanded-plan.md. Hypothesis: predecoding CPU-resident gate/up codebooks trades spare RAM and preprocessing for fewer AVX2 lookup/sign/scale instructions. It does not change quantization. A288-byte expanded block stores signed grid bytes,16scale bytes and the same float multiplier, versus98/110/82-byte IQ3_XXS/IQ3_S/IQ2_S blocks. Keep the original activation sign operation (including byte-128), integer accumulation lanes, FMA sequence, SiLU and reduction. The first gate is bitwise equality for normal and extreme activations at1-8tokens, followed by five alternating paired timings over a DRAM-sized expert pool and then nine-worker validation if warranted. No production cache allocation or source change yet.

Ruling: execute the bounded prototype inline on the existing working branch; no new worktree/branch. This follows the user's one-branch requirement and autonomous optimization authorization. The existing native source is an oracle, not modified by the diagnostic. A microbenchmark win alone cannot authorize promotion; memory, pool contention, integration parity and the full fixed matrix remain necessary.


## E043 / Vulkan compatibility and rejected raw-target placement

Portable llama.cpp b11538 (79e2e74eb,Clang20.1.8) loaded qwen4exp, the exact two IQ3_S shards and compatible CPU F16 projector with262144context and one slot. V001 became ready in46.857s and exited cleanly. V002 used the same backend with CPU MoE plus6144MiB expert cache,GPU layers99,9threads,Q8_0K/V,full context,thinking on/unlimited/high,preserved thinking and the unchanged numeric coding sampler. API names were translated explicitly: Strata repetition_penalty1 -> llama repeat_penalty1; Strata reasoning_budget_tokens0 -> llama CLI reasoning-budget-1. Original B011 request prompts and seeds retained. No MTP and no assertion that llama Q8_0KV is byte-equivalent to Strata INT8. This is a diagnostic comparison, not a qualification arm.

The first V002 launch failed immediately because this build rejects --verbose-prompt; that attempt is retained and the unsupported diagnostic flag was removed. The successful launch recorded props/model identity and actual requests. Warmup:166prompt/512generated,8.094raw target decode,3.298prompt tok/s,113.475s total. Short seeds101-103 all generated512 with zero cache reuse: decode8.876,8.689,8.957 =>8.876median; prompt17.515median; E2E7.617; TTFT9.652s. These are raw target rates, not served-MTP rates and not a native/Vulkan matched-distribution quality result.

Ruling: reject this placement after the complete three-run short cell rather than spending the remaining longer matrix on an order-of-magnitude loser. A supervisor checked that all three runs had512tokens and all rates<15, then stopped only the exact recorded executable/PID on18081. The already-started longer warmup disconnected and is explicitly incomplete. The generic runner's final loaded:false field records that deliberate interruption; capability-before-stop.json preserves the successful load. No failed or partial longer request is counted. This does not prove an upper bound for Vulkan or exhaust its placement/compiler/speculation options. Production launcher remains native CUDA.

## E044 / full-byte CPU expansion fails under nine workers

C015 first observed the stub fail640/640 gate/up values, then all48 parity cases passed after implementation. Three formats(IQ3_XXS,IQ3_S,IQ2_S),1-8tokens,normal and extreme activations including byte-128 and negative/zero activation scales; unchanged integer lane and FMA ordering. Five alternating pairs per timed shape(1/2/3/4tokens) over~64MiB compressed GU weights gave1.17-1.80x single-core gate/up speedups. Full raw timings and preprocessing bytes/time are retained. This is synthetic diagnostic evidence, not actual-model or served quality.

C016 reused the actual nine-worker,30-task ExpertPool implementation with only its GU call redirected to the prototype; original intermediate quantization and IQ4_NL down rows remained. The stubbed range writer first failed2560 outputs. Implemented ranges then passed all27 complete-expert parity cells(three formats,1/2/4tokens,1/3/6jobs). Five alternating pairs per cell and a> L3 expert pool:288-byte expansion was slower in24/27cells. Only the IQ3_S four-token shapes gained0.5-3.7%. Reject this representation. Added memory traffic is a plausible explanation for the lost single-core benefit; no memory-bandwidth counter measured that cause directly.

## E045 / compact exact nibble cache is promising only for IQ3_S

C017 stores the same signed codebook values in four-bit codes, retaining original half block scale and exact subscale indices:138B per256weights versus98/110/82B native and288B from C015. Each format has at most16 signed values, so this is lossless repacking, not a lower-quality quant. AVX2 byte shuffles recover identical grid/sign/scale vectors. The initial stub failed640/640 values; implemented kernel passed48 cases. Single-core speedups1.18-1.70x across all tested shapes, with five paired samples each.

C018 repeated the unchanged nine-worker complete-expert matrix:27/27parity cells pass. IQ3_S improves every measured cell by1.21-1.33x. IQ3_XXS and IQ2_S have mixed wins/losses, so they are excluded from the next server candidate. The native model layout has ten IQ3_S GU layers(17,21,25,27,28,29,35,40,44,45); expanding every expert of just those layers would require8.4228515625GiB additional RAM, computed from512experts x1280rows x10blocks x138B x10layers. This is a capacity calculation, not measured live allocation. One of those layers has Q2_0 down weights; this prototype measured IQ4_NL down only, so actual-weight/down-type validation is still required.

No production source/configuration was changed or promoted. Next:actual GGUF-weight parity, bounded cache allocation/lifetime design and default-path parity, then same-day paired live benchmarks with the frozen sampler/context. A21-33%pool improvement across only ten layers does not imply the whole model gains that much or reaches90tok/s.

B012's first non-streaming warmup returned legitimate null final content with512reasoning tokens. The collector tried to join None and failed after saving the raw response/timings. Preserve that attempt; replace null content/reasoning with empty text only for extraction, replay the saved response successfully, and restart from a fresh unchanged service. No sample or model parameters changed, and no incomplete attempt is counted as a completed arm.


## E046 / non-streaming control and actual-weight compact-cache parity

B012 completed after the collector-only null-content fix, from a fresh exact retained service, longer workload first. One excluded miss/hit warmup pair per size and five measured seeds101-105 per cell. Short miss decode88.5,90.0,88.0,93.0,90.0 =>90.0; short hits91.4,96.3,88.9,87.9,92.4 =>91.4. Longer misses89.7,90.2,91.0,89.3,90.9 =>90.2; longer hits89.0,86.6,87.1,88.1,88.7 =>88.1. Miss prompt medians199.8 /509.2; E2E78.616 /43.219(short/longer). Hit E2E90.114 /86.904. All generated512; declared misses reused0 and hits reused all but5prompt tokens. Nonstream TTFT/stream-total remain null. This unchanged control does not complete the target: one cache-hit cell is below90, other required streaming/TTL cells and Q007 completion gate still fail, and two independent qualifying confirmations are absent. Exact service stopped afterward.

C019 tested the compact IQ3_S prototype on actual GGUF weight slices, with no server resident. All ten IQ3_S GU layers, experts0/173/511 in each, and widths1/2/3/4/5/6/8:210 full-expert cases,2,227,200 compared float values, all bitwise equal and finite. Both native IQ4_NL and Q2_0 down types are covered. The unchanged nine-worker pool performs original intermediate quantization/down rows. Raw tensor values are not published; only source, fixture selection, outcomes and binary hash. This proves the sampled primitive outputs, not every expert, whole-model quality, cache lifetime, memory use or a served speedup.

The goal remains active. Production engine/configuration are still the previously qualified fallback. Next implementation candidate: bounded opt-in compact CPU cache for IQ3_S GU only, with explicit RAM accounting, eager preparation before readiness, immutable worker-visible pointers and cleanup tied to its source arena. Default-disabled behavior must retain exact outputs. Integration must pass lifecycle/parity checks and full paired server benchmarks before promotion; the known Q007 finite-cap completion failures remain disclosed and unresolved.


## E047 / bounded compact IQ3_S integration, first served pair

C020 implements an opt-in exact IQ3_S gate/up cache owned by ArenaExpertSource. STRATA_CPU_IQ3S_CACHE_GIB is an integer allocation budget; unset leaves the existing native path. The cache stores138-byte blocks, original fp16 scale bits, exact four-bit signed grid indices and original subscales. It changes neither model quantization nor GPU weights. Startup validates canonical native geometry and checked byte bounds, budget, physical RAM and available commit with16GiB left over. Unknown commit, unsupported ISA/dispatch, shared arenas, allocation failure or unsupported geometry fall back explicitly. Linux currently lacks commit reporting and therefore falls back. Only the ten IQ3_S GU layers qualify; other quant types and prefill retain their existing paths. Immutable per-job pointers avoid a global registry or allocation during requests. Clear precedes original arena teardown.

TDD: the stub failed at valid-cache-load as intended. Production integration passed budget/RAM/commit/unknown-commit/overflow/bounds/reopen/multiple-owner tests, eight extreme-activation/range cases and16 complete-pool parity cases; CPU-only tests passed with MT_MIN1 and2. The integrated actual-weight implementation again passed210cases and2,227,200float comparisons, including IQ4_NL and Q2_0 down weights. CUDA build and16 selected CTests passed. CPU-only native-on build/tests and native-off link/run smoke passed. Native-off stubs, unsupported-CPU test skipping and unknown-commit refusal were fixed following independent static review. Review found no remaining Windows benchmark blocker; actual ArenaExpertSource close/reopen and full served quality/stability remain promotion gates. HIP/SYCL toolchains unavailable, not built. The first CMake test build failed for missing private ggml-common include; corrected target include path and rebuilt. The initial manual test build used an absent build path; corrected before the intended red test. All failed logs retained.

R030/R031 use the same new CUDA13.3/sm86 binary, fixed sampler, original TTLCache prompts, context262144/INT8, CPU F16 vision, MTP4/min-p0.70 and existing runtime tuning. The only arm setting difference is compact budget9GiB. Each fresh process runs one excluded warmup and five512-token measured seeds per short/3K cell. R030 cache-off medians86.7/85.6decode,197.3/496.1prompt,76.226/42.258E2E. R031 cache-on medians86.0/83.2decode,196.3/494.6prompt,75.264/41.609E2E. This first pair is a regression, not a promoted improvement. Paired request JSON is identical; sampled output texts differ, so kernel parity does not substitute for a completed-answer quality test. All raw seeds are retained.

R031 confirmed cache ready with9,043,968,000bytes(8.4228515625GiB),10.516s expansion,35.247s load versus25.154s R030 load. One-second resource snapshots began before launch and continue through cleanup: system RAM/commit, summed engine RSS/private bytes, GPU used/free, paging, clock/power/temperature. System-wide Pages Input/sec is not engine paging attribution; sampled extrema are not exact peaks. Reverse-order candidate/control repeat pending to judge small differences. Both completed services stopped, retained production config restored, launcher unchanged. Goal active,90unqualified and Q007 completion failures unresolved.


## E048 / compact-cache reverse repeat, rejection and newer tools

Reverse-order R032(cache on) and R033(cache off), longer first, completed all five measured512-token seeds per size plus excluded warmups. R032 medians85.9short/82.8longer decode;197.9/495.9prompt;74.879/41.537E2E. R033 medians86.8/44.9decode;202.3/495.1prompt;75.851/29.182E2E. R033 longer includes44.9,16.9 and another major slow run; every seed remains in the ordinary median. R033 recovered to normal short speeds. This repeats the previously observed intermittent control stalls; it is not valid to discard them or attribute the apparent longer aggregate win to the compact cache. Numeric sampler and request JSON remain fixed. Source build, same-binary A/B, uninstrumented GPU execution; the common lightweight one-second resource observer is disclosed separately from Nsight-injected diagnostics.

R033's first measured longer request began21:27:30.332UTC, ran17.545s, and had a system-wide Pages Input/sec sample22,492.94 at21:27:40.437. This overlaps the slowdown, unlike the older B010 counter capture. It does not identify the engine as the source or prove CPU paging/VRAM eviction caused it. GPU free allocation snapshots stayed about513MiB; that is allocation evidence, not proof of WDDM residency. RAM and commit remained well above the16GiB floor; detailed all-sample CSVs and observed extrema are attached. No OOM. Monitors sampled through cleanup; exact process inventories after the arms show no model/profiler resident and nvidia-smi returned568MiB used.

Ruling: reject C020 for promotion. Both enabled short medians are slightly below their controls and neither enabled size reaches90. The first clean pair loses in both cells; the second longer comparison is confounded by control stalls. No repeated server gain offsets8.42GiB additional RAM and about10s expansion. Startup readiness was25.154/35.247/65.537/55.348s forR030/R031/R032/R033; the latter starts selected unbuffered expert reads, so the extra30s must not all be attributed to compact expansion. Preserve all failures and the unresolved stall. Full natural-stop quality and ArenaExpertSource reopen promotion work was deliberately not pursued for this loser; kernel/cache tests alone do not certify whole-model quality.

The complete experiment source is preserved as C020-rejected.patch againstb1eea8a5; git apply --check passes after restoring production source. The three newly created source files were moved to the local rejected-source archive. No additional branch was created. Runtime config restored to the qualified format-gather engine; launcher unchanged. Source/runtime compact changes are no longer active.

Fresh official vendor research found newer tooling than this campaign's installed CUDA13.3.73/Systems2026.1.3. The live CUDA download page resolves to13.4.2(Update1), superseding the search snippet's13.4.1; official redistrib_13.4.2.json is dated2026-09-16. Systems2026.5.1 is available and lists improved CUPTI flushing at cudaProfilerStop. This does not prove the local record loss is fixed. Before another kernel change: install verified vendor development/profiling components side-by-side, run minimal backend/profiler checks, and re-establish the same fixed baseline if the compiled/runtime path changes. No driver replacement, reboot, privilege change or global launcher switch. Download/install status is tracked in the next checkpoint.

Next architectural lead, not implemented: Q6_K head row grouping without extra packed weight storage. Native one-column head launches one128-thread CTA per vocabulary row. Test2/4/8rows per CTA retaining each row's existing per-thread block order and lane0 reduction/store. The incomplete P008 trace suggests the head is worth a bounded diagnostic, not a whole-run bottleneck proof. Unlike rejected C014 this changes launch/work grouping only, uses original Q6_K weights and adds no weight buffer. Require actual-weight bitwise parity and repeated alternating CUDA-event timings before any serving test. Investigate control stalls with the updated profiler and complete trace validation; no claim that this kernel lead fixes stalls.


## E049 / verified side-by-side development and profiling update

Applied official CUDA13.4.2 redistributables side-by-side, verifying every archive's published SHA256 and byte size. nvcc reports13.4.92. CUDA smoke compiled forsm86 using MSVC17.14.36 and passed32 launches/128 exact float values. cudaRuntimeGetVersion and cudaDriverGetVersion both return13030; record these API values separately from the compiler/package version. This verifies a minimal backend, not a full Strata13.4 build or a throughput improvement. Previous toolchain and production launcher remain available.

Nsight Systems2026.5.1.161 MSI SHA256379c0a15a9cf7b8028081073fdd1d9798b9aaa618fb46c6a01785b69ed01d5f2, NVIDIA Authenticode signature valid. Initial administrative extraction exited1603/Error1304 at a261-character filename. Repeating administrative extraction into C:/Strata/.tools/n5 succeeded(exit0), with no global installation, policy/driver change or reboot. CLI version confirmed. The CUDA smoke trace contains exactly32 kernel records and no dropped-record diagnostic; larger Strata capture completeness still must be checked. Raw MSI logs withheld because they contain private machine/user properties; the relevant error and disposition are recorded here.

Nsight Compute package2026.3.1.2 CLI reports2026.3.1.0(build38829034). It launches the smoke executable, but profiling returns ERR_NVGPUCTRPERM: performance-counter access is restricted. No permission or driver policy changed. Use available Systems CUDA timelines and CUDA-event timings; do not claim Compute metrics were collected.

C020 production-source restoration and all four served arms remain retained. No benchmark model resident after these tool checks. Goal active,90tok/s and Q007 quality gates remain unqualified. Next: re-capture one unchanged production request with updated Systems, verify trace completeness, then decide whether the next controlled test should address residency stalls or Q6_K launch grouping.


## E050 / user-reported launcher leaks: confirmed, corrected and regression tested

The user observed multiple Strata instances. Expanded inspection found five live PowerShell launcher processes from10:22,15:13,15:31,15:40 and17:19 local time, plus their venv-python records and console hosts. No live Strata engine, vision engine or8080 listener was present at that inspection. The five launcher/console groups used740.047MiB sampled working set and1465.316MiB private commit in aggregate. WMI continued to enumerate five Python PIDs; direct Windows GetExitCodeProcess subsequently returned exit code1 for every Python record, not STILL_ACTIVE259. They were terminated process objects, not five active models. Do not infer GPU competition or a throughput penalty from this cleanup defect alone.

Root cause: the campaign's local server.ps1 Stop action killed only the port-owning Python child and descendants. On Windows the launcher chain contains an outer PowerShell plus a venv Python launcher above that listener. Stop left those ancestors behind; after the listener disappeared, later Stop calls did nothing. Prior no-engine/no-port checks were insufficient to establish complete process cleanup. This is a campaign-harness defect, not evidence of a model quality change. All five validated launcher trees were explicitly terminated; exact PID, command line and creation time were checked before termination. Normal desktop GPU usage remains; no unrelated processes were stopped.

Fix: Stop now discovers exact configured launcher/server and workspace engine identities, validates an existing listener, selects the highest matched ancestor, rechecks creation time/command line, terminates that tree, and verifies no live launcher/server/engine/vision processes remain. Start refuses leftover live launcher/server instances even with no listening port. Exited WMI records are checked against live Process state. A regression fixture failed against the previous helper with 'orphan launcher with no listener was left running', then passed orphan/no-listener cleanup, nested venv/listener root cleanup and unrelated-listener refusal. Original helper, corrected helper, red/green logs and test script are attached. R034 is the live retained-configuration lifecycle check; it must finish cleanup before another launch. No model-code, sampler, launcher defaults or context changes.

The completed P009 request used the new Systems2026.5.1 profiler and unchanged retained engine/config: one excluded warmup plus one512-token diagnostic,69.8server_decode_tps,61.516request_e2e_tps,1.026sTTFT. These instrumented rates are not qualification evidence.759910kernel records span1.345-9.615s of9.715s capture, but diagnostics still warn that not all CUDA events might have been collected. No explicit dropped-record count appeared; trace completeness remains unproven. CUDA performance-counter permission remains unavailable. All raw P009 evidence is preserved.

Source inspection resolved the misleading startup 'Q5_K head' message: generate.cpp hardcodes that label, while NativeHead::load uses the tensor's actual GGUF type and original bytes; the actual-weight diagnostic verified output.weight is Q6_K,2560x248320. No head quantization was changed. The Q6_K kernel lead remains valid as a bounded diagnostic, not a proven whole-request bottleneck.


## E051 / real cleanup-cycle verification; stalls and memory guard correction

R034 used the unchanged retained engine, same original TTL coding requests, numeric sampler,262144context,INT8KV,MTP4,one request,one warmup per size and five measured512-token seeds per size. Short ordinary median83.8server_decode_tps(range75.7-89.6),200.0prompt tok/s,73.247request_e2e_tps,0.867sTTFT. Longer median18.8decode(range6.9-82.3),474.4prompt,15.207E2E,6.562sTTFT. All slow runs remain. The long warmup was11.7decode; measured18.8,6.9,15.1,82.3,80.3. No performance winner and no90qualification. This control proves the prior leftover launcher shells are not necessary for the stalls; it does not identify their cause.

Live process inspection during R034 found exactly one verified launcher tree: PowerShell541640 -> venv Python145004 -> serving Python705020 -> vision663444 and text engine300184. Finally cleanup terminated that complete tree, including console host328624, and verified zero live Strata launcher/server/engine/vision processes. A separate post-cycle Stop check agreed; nvidia-smi585MiB used,0%GPU. This is the live regression test for E050. No benchmark model remains resident.

Resource observation: minimum available physical RAM31,149,924,352bytes(29.011GiB); available commit8,614,846,464bytes(8.023GiB), with25samples below the16GiB contract floor. Maximum Pages Input/sec173869.068(system-wide, not engine attribution). Engine RSS/private values were roughly stable while total available RAM/commit changed sharply; a spot top-process inventory found no second large model/process. This does not prove WDDM migration. GPU allocation/free values do not establish residency. R034 fails the memory qualification condition independently of its speed result.

The existing supervisor only aborted for available physical RAM<16GiB. Corrected it to check both physical RAM and available commit before launch, after readiness and every second during requests, failing closed on read errors. A boundary test first failed on low commit despite ample physical RAM, then passed independent physical/commit floors including zero and exactly16GiB. No contract relaxation, quality-gate change or launcher-default change.

The resource observer itself consumed63.578CPU-seconds over353.329wall seconds, versus0.375/160.446,R030;0.453/171.469,R031;0.422/200.728,R032;14.797/233.530,R033. Therefore 'lightweight observer' is not established for the slow arms. Observer API blocking/cost could be a symptom or contributor. Before another compiler/kernel comparison, isolate NVML/PDH/process-enumeration costs and compare a safely guarded control without that observer, keeping request/sampling/model/context unchanged. Preserve the instrumented arms and do not silently exclude them from earlier reports. Further kernel work is deferred until measurement interference is understood.


## E052 / isolate monitoring cost; safe abort of reproduced stalls

R035 removed the NVML/PDH/psutil observer, preserving a one-second GlobalMemoryStatusEx physical/commit safety guard through model loading and requests. No model/config/request/seed/sampler change. One excluded warmup plus five measured512-token runs per size. Ordinary medians89.2short/82.1longer server_decode_tps;202.1/496.9prompt tok/s. No severe stall. Minimum available physical64,100,835,328bytes and commit42,511,769,600bytes. Full tree cleanup verified. This is a safe control result below the goal, not proof that monitoring caused earlier stalls and not a production optimization.

The observer audit timed its API groups individually. Without a loaded model, process enumeration plus memory queries took about2.15ms median, while other groups were sub-millisecond. R036 repeated the same workload with the full observer and per-group timers. The short five-run cell completed. Longer measured runs1/2 were13.5/18.0decode tok/s; longer-run3 was deliberately interrupted by the guard at22:47:11.314UTC, available commit17,007,628,288bytes below17,179,869,184(16GiB). Available physical41,077,157,888bytes. All completed raw runs and the interrupted request are retained. The incomplete longer cell has no qualifying median and is not exported as a completed arm. The exact launcher, two Python layers, text engine and vision tree were stopped and GPU usage returned585MiB.

R036 audit: process-enumeration/memory group max2779.7615ms wall and2281.25ms CPU per poll;25.828CPU seconds total,50calls above100ms. Other group maxima: NVML memory2.4685ms, global memory0.8152ms, PDH paging1.0679ms, clocks0.5029ms, power0.3192ms, temperature0.0907ms, clock reasons0.1296ms. This narrows the costly observer activity to the process group but does not yet distinguish enumeration from GetProcessMemoryInfo or prove the call caused memory pressure. A post-model idle audit returned about2.15ms for the process group. psutil7.2.2 source maps memory_info to PROCESS_MEMORY_COUNTERS with a slower permission-error fallback; no permission-error attribution has been demonstrated.

R037 is the controlled follow-up: the same monitored workload with only process enumeration/memory queries omitted, retaining NVML,PDH and physical/commit safety. Its result is pending. Source changes so far are benchmark supervision/observation only. The supervisor now records its source per arm and forcibly stops its own observer if it does not exit within10seconds after model cleanup. No new engine/launcher defaults. The Q6_K row-grouping plan is recorded but queued behind this audit and the unchanged-source CUDA13.4 build.

Relevant primary API reference: https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo . It documents returned process counters and required query rights, not a performance guarantee or explanation for this local slowdown. NVIDIA's NVML documentation describes WDDM-managed memory; allocation snapshots alone still do not establish residency transitions.


## E053 / retain low-cost monitoring; proceed to compiler comparison

R037 omitted only the process-enumeration/memory-query group from the timed observer. NVML memory, clocks, power, temperature and clock reasons; PDH paging; and the independent physical/commit guard remained active. Same retained engine, model, context, vision, MTP, request JSON, five seeds and 512-token cap as R035/R036. It completed both five-run cells and both excluded warmups: ordinary decode medians 87.5 short / 83.9 longer tok/s; prompt medians 198.8 / 496.5 tok/s. No severe stall or memory-floor breach. Minimum available physical RAM 64,349,507,584 bytes and commit 42,742,296,576 bytes. All remaining timed observer calls together consumed 0.015625 CPU seconds; the maximum individual wall time was 0.4551 ms. Full launcher/server/model/vision cleanup passed.

Interpretation: the slow process-query group is avoidable monitoring overhead and is associated with the reproduced stalls. R035 (safety guard only) and R037 (all other observer groups) were stable; R036 with process queries stalled and was safely aborted. This narrows the problem but does not distinguish process enumeration from a particular memory API, nor prove a driver mechanism. Earlier stalls without this observer are still retained. No claim that all historical instability is solved. Process memory queries will be kept outside timed generation; system memory and GPU telemetry remain available, and missing per-process peak measurements will be stated. Repeat this measurement policy during subsequent paired trials.

The unchanged-source CUDA 13.4.92 control build C022 is now underway in its own build directory, using sm86, portable Release, MSVC and the existing pinned ggml source. This is a toolchain candidate, not a launcher promotion. The retained CUDA 13.3 executable remains unchanged. After build checks, compare it under the stable measurement policy and record actual loaded libraries separately from the compiler version. The C021 row-grouping harness has been written with a deliberately incorrect stub; it has not yet been compiled or claimed correct. No production kernel source changed.


## E054 / updated compiler built; exact row-grouping candidate rejected

C022 built unchanged retained source with CUDA13.4.92, MSVC19.44.35228.0, sm86, portable Release and the existing pinned ggml source. Engine SHA256 ee908fc32b1a7d86ad349785d533086cfcacdf5df7886342d1d955ef54be494c, 52,241,920 bytes. All15 selected CPU dispatch/parity tests passed. The initial GPU test command referenced native_mmvq_multi, whose optional bench source is absent in this checkout; that command failed and is retained. Corrected selection built and passed all4 applicable GPU tests: mmvq_multi_parity, native_multi_parity, kv_stream_parity and verify_batch_parity. This covers tested matrix formats including Q6_K, routing/combining, KV streaming and batched verification; it is not full served quality qualification. Test PATH prioritizes the same existing production CUDA DLL directory; compiler and runtime identities remain separate.

C021 standalone actual-head test first failed with its deliberately wrong candidate stub (reference00000000 versus ffffffff on the first zero-input row). Implemented2/4/8rows per128-thread CTA with the original per-row block stride, DP4A/FMA/reduction sequence and lane-zero result. It passed168cases and6,021,840finite bitwise float comparisons, including odd output tails and unchanged guard values. Original Q6_K head bytes521,472,000; no weight repacking or extra weight buffer. This is a sampled parity proof for the prototype, not a whole-model quality result.

Timing: one excluded warmup per variant,11rounds,16calls per timed CUDA-event interval, alternating forward/reverse variant order. Every raw timing is retained. Ordinary median milliseconds per full head:

- 1 row(s)/CTA: 0.604220 ms, range 0.585714-0.609784; speedup 1.0000x versus original.

- 2 row(s)/CTA: 0.649920 ms, range 0.616064-0.657786; speedup 0.9297x versus original.

- 4 row(s)/CTA: 0.727340 ms, range 0.679040-0.741888; speedup 0.8307x versus original.

- 8 row(s)/CTA: 1.065906 ms, range 1.033856-1.073216; speedup 0.5669x versus original.

All grouped variants were slower. Reject C021; do not integrate, rerun serving or promote this kernel. Prototype, red/green logs, build flags and all event timings are archived. Production kernel source and launcher remain unchanged. GPU memory returned585MiB used after the diagnostic.

R038 is now comparing the unchanged-source CUDA13.4 engine under the same fixed served workload, changing only executable/toolchain and preserving existing runtime library paths. No process-memory queries during generation; remaining telemetry and both16GiB safety guards remain. Its result is pending. Q007 and the full90tok/s matrix remain unqualified.


## E055 / compiler-only CUDA 13.4 served comparison does not justify promotion

R038 completed both original TTLCache streaming cache-miss cells, in longer-then-short order: one excluded warmup and five measured seeds 101-105 per cell, exactly 512 generated tokens per measured request. Fixed sampler, high/xhigh reasoning, 262144 context, INT8 KV, CPU F16 vision, MTP4/min-p0.70 and PCIe fraction0.20 were preserved. Only executable/compiler changed relative to the retained configuration. Loaded cuBLAS, cuBLASLt and NVIDIA driver DLL hashes exactly match R037; this is not a runtime-library trial.

| Workload | Server decode median (range), tok/s | Prompt median, tok/s | Request E2E median, tok/s | Stream total median, tok/s | TTFT median, s |
|---|---:|---:|---:|---:|---:|
| Short | 86.5 (83.7-88.8) | 205.6 | 75.5981 | 75.6114 | 0.8433 |
| Approximately 3K | 84.2 (82.8-85.0) | 495.7 | 41.8972 | 41.9003 | 6.1647 |

Same-day retained controls R035 and R037 produced short/longer decode medians 89.2/82.1 and 87.5/83.9, respectively. The new compiler is within this mixed range and does not meet 90 in either cell. No severe stalls occurred. This does not establish a reproducible performance winner, nor does it replace the random-coding, quality or real-use gates. Q007 remains 3/5 completed coding answers passing their tests and 2/5 capped without a final answer.

Minimum available physical memory 64,233,795,584 bytes; minimum available commit 42,596,917,248 bytes. Peak sampled GPU use 25,260,417,024 bytes. Both 16 GiB floors passed. Observer total CPU time 0.000 ms; maximum individual observer call 0.4519 ms. Per-process peak memory was deliberately not queried during requests. Full launcher, server, engine and vision tree cleanup passed; a subsequent idle check read 585 MiB GPU used. Original configuration was restored.

Disposition: compiler candidate unpromoted; production launcher unchanged. Next, isolate the newly downloaded CUDA runtime libraries using the same CUDA13.4 executable, with library-name-based identity capture and an explicit configured-directory guard. If that also lacks a clear gain, leave the retained compiler/runtime stack in place and move to broader serving/scheduling alternatives. All raw measured seeds and failed arms remain public evidence.


## E056 / newer CUDA libraries fail to improve the served workload

R039 held the R038 CUDA13.4 executable constant and changed only lib_dirs to the side-by-side CUDA13.4.2 SDK directory. Module capture now matches CUDA DLL names independently of installation path and refuses a non-driver CUDA library outside the configured directories. Live identity confirmed new cuBLAS/cuBLASLt binaries and unchanged nvcuda driver. This avoids attributing a compiler build to runtime libraries it did not load.

Loaded library SHA256:

- cublas64_13.dll: `60bbba8868290311e9c1657b2193ddec667744eb555ff843f87acb7c039f9efa`.

- cublasLt64_13.dll: `cad63434448e7141629e240ea093ad596a7ef6a0f67b468ba9bc1df6e1eeee33`.

- nvcuda.dll: `3fe38dc3b7eb45f4c364d87df01dbf1c224c5ffd96b542cea8c0dca215330b84`.

Original TTLCache streaming cache misses, one excluded warmup plus five seeds per cell, 512 generated tokens each, longer then short. Same fixed thinking profile, context, precision, MTP and vision.

| Workload | Server decode median (range), tok/s | Prompt median, tok/s | Request E2E median, tok/s | Stream total median, tok/s | TTFT median, s |
|---|---:|---:|---:|---:|---:|
| Short | 87.4 (84.2-90.1) | 201.6 | 76.3132 | 76.3240 | 0.8588 |
| Approximately 3K | 80.5 (70.3-85.2) | 496.4 | 41.0086 | 41.0118 | 6.1523 |

The longer median is lower than R038's84.2 and the retained R037's83.9. One90.1 short seed is not goal evidence. All slower seeds remain included. Do not promote this runtime stack; compiler and runtime candidates remain available for development, while the launcher keeps the retained CUDA13.3 engine and original runtime libraries. No quality win or full-matrix qualification is claimed.

Minimum available physical RAM 62,318,350,336 bytes and commit 41,375,252,480 bytes; sampled GPU peak 25,283,485,696 bytes. Both16GiB host safety floors passed. Full launcher/server/text/vision process cleanup passed, followed by585MiB idle GPU use. Original configuration restored.

Next larger alternative R040 is the existing opt-in coupled Gumbel draft implementation, after sampler/host-reference and distribution checks. Its exact numeric sampling remains fixed, but its random stream changes; it is diagnostic until full correctness/quality gates pass. T003's losing coupled-only arm remains recorded and is not being relabeled. Plan and rationale are in diagnostics/coupled-gumbel/coupled-gumbel-plan.md.


## E057 / coupled Gumbel sampler checks pass; served trial started

C023 built the existing sampler_parity and coupled_draft_test targets using CUDA13.3.73/sm86 Release and the production runtime libraries. All four selected tests passed: sampler_parity, sampler_parity_one_block, sampler_parity_old and coupled_draft_test. Each sampler implementation reported zero failures, including Gumbel GPU/host-reference parity for48draws across three chains (one is exactly temperature1/top_k20/top_p.95/min_p0), and total variation0.0098 over10240categorical draws against the expected softmax. Flag controls confirmed a different sampled random stream and unchanged greedy behavior. These are finite implementation checks, not a claim of universal coding-quality equivalence.

Source selection, counter/history arithmetic, and the exact-match target verifier support a distribution-preserving diagnostic. No probability threshold is used to accept an unverified token. The numerical thinking sampler stays identical. Retain per-arm reproducibility with explicit engine, flags and seed; do not claim identical text to the inverse-CDF stream for the same seed. There is no production source edit, quantization change, reduced context or reasoning restriction.

R040 is running on the retained production engine/library stack with only STRATA_SPEC_COUPLED=1 and STRATA_SPEC_GUMBEL=1 added. Both original five-seed512-token cells are required; sampler tests alone cannot promote it. If throughput improves, complete paired repeated controls and the random-coding/full quality matrix before changing the launcher.


## E058 / R040-coupled-gumbel

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.9 (85.6-89.7) | 205.4 | 76.1232 | 76.1376 | 0.8606 | 876/1107 (79.13%) |
| longer | 85.1 (80.2-87.0) | 496.2 | 42.1124 | 42.1187 | 6.1566 | 985/1251 (78.74%) |

Minimum available physical RAM 63,815,675,904 bytes; available commit 42,119,364,608 bytes. Sampled GPU peak 25,258,319,872 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

R040 coupled Gumbel completed at86.9/85.1 short/longer decode tok/s. The mixed difference versus R03787.5/83.9 does not establish a repeatable overall gain or meet90. Keep it unpromoted; all five seeds remain included.

Next: R041 tests --spec6 alone on the retained control, with exact-match target verification and additional GPU buffers explicitly measured.


## E059 / R041-spec6

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.5 (84.6-88.5) | 199.6 | 74.7996 | 74.8136 | 0.8811 | 904/1236 (73.14%) |
| longer | 81.5 (80.2-85.4) | 496.3 | 41.2792 | 41.2822 | 6.1481 | 1043/1480 (70.47%) |

Minimum available physical RAM 64,107,753,472 bytes; available commit 42,449,571,840 bytes. Sampled GPU peak 25,298,165,760 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

R041 six-token MTP windows finished below90 in both cells and lost throughput versus the retained control. The larger window did not justify its cost; reject and retain --spec4. No quality or prompt-rate concession was made.

Next: C024 tests exact speculative rejection sampling before an independently labeled R042 trial; keep target sampling fixed.


## E060 / rejection-sampling integration audit finds two distribution biases

C024 passed the existing spec_prob_test (72 cases, including two-million-trial distribution cases, joint distributions, support boundaries and deliberately wrong negative controls) and spec_verify_parity (1,296 GPU rows, zero mismatches). These tests exercise the rejection rule in isolation. They do not test the surrounding draft-confidence gate or proposal-source selection. The earlier plan's implication that these tests alone would establish the served mode's target distribution was too strong.

While R042 was preparing, source audit found that spec_draft_merge_kernel writes the probability of the sampled draft token by default (spec_gate_pick), then generate.cpp allows that draft into verification only when its probability exceeds --spec-min-p. Selecting the rejection-sampling path using the realized draft changes the conditional proposal distribution, while the verifier still receives the original q. The plain-sampling fallback does not cancel this bias.

Readable counterexample: p=(0.5,0.5), q=(0.75,0.25), confidence floor0.70. Only draft A enters rejection sampling. Its accepted contribution to A is0.75*(0.5/0.75)=0.5; when B is discarded, plain p sampling adds0.25*0.5=0.125. Thus final P(A)=0.625, not0.5. C025 uses the real host spec_verify_row/spec_sample and spec_gate_pick, plus the served gate rule. One million draws observed0.623935/0.376065, total variation0.123935; a second asymmetric case also failed. Ungated and always-closed controls passed. With existing STRATA_SPEC_PROB_GATE=top, all four cases passed (maximum observed total variation0.000722). This is a synthetic integration counterexample, not a measured percentage of bias on the selected model.

A second source-dependent selection exists in generate.cpp: suffix lookup is considered only when its first token equals the MTP's sampled draft; suffix windows then use plain exact-match target sampling instead of q-based rejection. C026 isolates this rule with the same p/q and a policy choosing the matching suffix. Observed target A frequency0.373727 instead of0.5 (analytical0.375). Disabling suffix choice produced0.500338; a draft-independent always-lookup control produced0.500074. The retained ordinary exact-match mode and R040's shared-draw coupled mode are different algorithms; these counterexamples specifically invalidate the audited probabilistic-rejection composition.

R042 was stopped immediately during its excluded warmup. No measured result or successful speed summary exists; partial request/SSE, failure, memory and complete cleanup evidence are retained. ConnectionResetError is the intentional termination, not an unexplained model crash. The previous production configuration was restored and idle GPU memory returned585MiB. This optional mode was never promoted.

A benchmark preflight guard now rejects STRATA_SPEC_PROB unless distribution-top gating is explicit, suffix drafting is disabled, and lookup chaining is absent/zero. Five focused tests first failed three rejection cases with a no-op guard, then all passed. The supervisor checks before model launch. Production engine source and launcher are unchanged.

Next diagnostic R043 may use the existing rejection algorithm only with STRATA_SPEC_PROB=1, STRATA_SPEC_PROB_GATE=top and --suffix-draft0, on the retained engine/libraries and four-token MTP. These settings remove the two demonstrated draft-dependent selection paths while preserving the target numeric sampler, model, context and reasoning. Disabling lookup can reduce speed for repeated text; it is a candidate cost to measure, not a quality concession or a promoted setting. Full random-coding, capability, memory, repeated speed and prompt/client non-regression gates remain required. No upstream issue or message was sent; this evidence is published only to the authorized fork.


## E061 / R043-spec-prob-top-no-suffix

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.3 (85.0-87.8) | 200.9 | 74.7275 | 74.7376 | 0.8665 | 914/1206 (75.79%) |
| longer | 85.1 (81.8-86.1) | 496.0 | 42.1726 | 42.1772 | 6.1517 | 1008/1320 (76.36%) |

Minimum available physical RAM 64,181,604,352 bytes; available commit 42,612,404,224 bytes. Sampled GPU peak 25,220,571,136 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

R043 audited rejection-mode composition reached85.3/85.1 short/longer server decode tok/s. Neither cell meets90, and short speed is lower than the retained control. Keep it unpromoted; the production launcher retains ordinary exact-match drafting.

Next: R044 is queued: change only the audited proposal-distribution confidence floor from0.70 to0.50, leaving target min_p0 and every thinking parameter fixed. See spec-prob-threshold-plan.md; repeat and qualify only a measured winner.


E061 checkpoint supplement: the preflight guard also matches the engine's boolean environment semantics (any nonempty value except exact string0). Four enabled-value subcases first failed, then the six-test suite passed after correction. These current guard sources and red/green outputs are archived separately from E060's five-test version. The complete all-run MTP counts for R037/R040/R041/R043 are retained in diagnostics/spec-prob-audit/all-run-acceptance-comparison.json; no acceptance claim depends on a selected fast seed. Higher acceptance alone is not evidence of higher served throughput.

The read-only GitHub search used the required bot helper. The open issue search for STRATA_SPEC_PROB returned1447; the open speculative-PR search returned existing pipeline, batch, benchmark and kernel work. No issue, comment or upstream pull request was created. This fork report does not claim to have exhaustively searched every discussion or to be an upstream-reviewed bug fix.

Final checkpoint cleanup again verified zero live Strata launcher/server/text/vision processes. GPU use585MiB, free23738MiB, utilization0%. The production configuration is byte-identical to the saved pre-trial version. No failed compiler/runtime/draft experiment is installed. The goal remains active, with its full quality and repeated-workload conditions unmet.


## E062 / R044-spec-prob-top-floor05

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 82.6 (74.4-93.9) | 203.5 | 72.2176 | 72.2264 | 0.8648 | 1123/1775 (63.27%) |
| longer | 84.5 (81.6-87.4) | 496.3 | 42.0126 | 42.0178 | 6.1585 | 1217/1919 (63.42%) |

Minimum available physical RAM 63,070,449,664 bytes; available commit 41,725,988,864 bytes. Sampled GPU peak 25,205,891,072 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

R044 lower draft-confidence floor finished at82.6/84.5 short/longer decode tok/s, versus R04385.3/85.1. Reject the threshold change; the93.9 short peak does not replace the all-run median. No candidate is promoted.

Next: Independent review of the rejection-mode audit is pending. In parallel, prepare R045 resident-complement memory layout with the retained ordinary sampler, after byte-ownership and GPU-alias tests.


## E063 / Independent sampling audit review and preflight corrections

The independent source review confirmed the two E060 integration counterexamples. It found no further concrete conditioning or counter-domain defect in the explicitly configured R043/R044 serial path. This is source review of the inspected path, not finite-precision distribution proof, completed coding quality, or performance qualification. The review also confirmed that old/one-block sampler modes can silently use exact-match verification while startup still announces probabilistic drafting; a startup label alone is insufficient evidence of actual rejection verification.

The review found two defects in the benchmark preflight, both reproduced before correction. First, serve/server.py inherits os.environ and then overlays stringified config entries; the guard inspected config entries only. The guard now checks the effective inherited environment with the same overlay. Ten tests passed after the inheritance correction, including inherited enablement, explicit disablement and gate overrides. Second, the engine parses repeated CLI flags from left to right, with the final value winning; the guard used the first. It now validates the final occurrence and refuses a missing value. Twelve tests passed after that correction. A manifest privacy test brought the suite to thirteen.

A follow-up review found the Windows case-insensitive environment edge. The guard now refuses noncanonical spellings of the eight recognized sampling-mode keys on Windows, including differently-cased collisions, rather than guessing child duplicate-key precedence. All three new subcases first failed; the final fourteen-test suite passed. The original E060/E061 archived guards remain historical evidence and are superseded by E063. The final Windows-case correction is covered by tests; the independent review had verified the preceding corrections and identified this additional case.

The supervisor now snapshots the effective sampling-mode allowlist and helper source before preparation. It never publishes the full environment. The keys are STRATA_SPEC_PROB, STRATA_SPEC_PROB_GATE, STRATA_SPEC_MIN_TEMP, STRATA_SPEC_PROB_DT, STRATA_SPEC_GUMBEL, STRATA_SPEC_COUPLED, STRATA_OLD_SAMPLER and STRATA_SAMPLER_ONE_BLOCK; null means absent. R043/R044 config files explicitly set PROB/top and have no duplicate relevant arguments, so the two original defects do not directly invalidate their explicit configuration. Their prior parent environment was not captured with this new manifest; absence of other inherited modes cannot be proven retrospectively. Future trials carry the allowlist.

C027 independently passed the existing exchange_storage_test and file_expert_source_test CTest fixtures under CUDA13.3, then the explicit GPU fixture completed 64 exact-byte exchanges each for pinned copy, pinned rotation and pageable fallback. No serving model was resident during the build/tests. These small ownership/alias/lifetime tests support trying the existing resident-complement path; they do not establish full-model speed or answer quality. Compilation warnings are preserved in the raw log. HIP/SYCL execution and Compute Sanitizer were not run in C027.

R045 adds only --resident-experts to the retained R037 configuration. Its startup guard requires page-locked resident storage, all 8409 control cache entries, and no reported partial-RAM/prompt-lending fallback. Four focused guard tests passed after the failing placeholder version. R045 snapshotted the thirteen-test sampling guard before the Windows-case correction landed; its canonical config keys and all-null saved effective sampling-mode manifest have no case ambiguity. The final guard is used for subsequent trials. No target sampling parameter or production launcher setting changed.


## E064 / R045-resident-complement

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 75.3 (74.8-77.6) | 200.9 | 66.8598 | 66.8707 | 0.8772 | 824/1097 (75.11%) |
| longer | 67.2 (66.0-72.1) | 515.9 | 37.8599 | 37.8626 | 5.9255 | 982/1322 (74.28%) |

Minimum available physical RAM 41,651,535,872 bytes; available commit 53,762,297,856 bytes. Sampled GPU peak 25,224,896,512 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

The resident complement reduced pinned expert storage from46.84 to34.55GiB but lost throughput:75.3/67.2 short/longer server decode tok/s, versus R03787.5/83.9. All12 requests including warmups recorded zero fallback blob reads;28682 expert exchanges occurred. The smaller allocation did not translate to a speed gain. Reject this copy-based resident mode; no promotion.

Next: Measure R046 with only exchange-buffer rotation enabled on top of R045, after a startup activation guard. This existing byte-preserving path removes the extra host copy but retains the GPU transfers; keep the same sampling, all-run benchmark and cleanup.


## E065 / R046 resident rotation refused before measurement

R046 changed only STRATA_EXCHANGE_ROTATE=1 from R045. Startup retained 34.55 GiB of page-locked resident expert storage and 8409 GPU cache entries, but explicitly reported: `exchange rotation unavailable; retaining copy path: requires equal-size expert blocks and a fully mapped/pinned RAM complement`. The source eligibility check in FileExpertSource::reserve_exchanges requires uniform layer blob sizes as well as fully pinned, mapped, nonpartial storage. This requested mode is not available on the current layout through the existing flag.

The new activation guard rejected the arm before any warmup or measured API request. There is no throughput result, no successful summary and no claim that rotation improved or lost speed on this model. Its failed-startup record, exact supervisor/helpers, config, engine log, memory and complete cleanup output are retained separately from successful arms. The five-test resident guard suite passed, including a previously failing test that requires explicit rotation activation.

The cleanup finally stopped the launcher root and every descendant, and the previous production config hash returned to 3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0. GPU memory returned to 553 MiB. No benchmark model remains resident. The full engine session is now captured in a nested try/finally, so a log-write failure cannot skip the stop call; restoration of configuration and observer shutdown remain in the outer finally.

The memory-layout branch of the experiment queue is closed for the existing implementations: R045 saves expert RAM but loses decode speed, and R046 cannot activate rotation. Generalizing ownership rotation to mixed block sizes would be new engine work and would still retain the extra GPU-to-host transfers; it is not an established path to 90 tok/s. No source change or production promotion is justified by these results alone.

Next: refresh current upstream and profiler evidence for a different single-GPU scheduling or kernel theory on the retained full arena. Do not retry the losing threshold, compiler/runtime, head layout, CPU repack or resident-copy arms without new evidence. The existing --pipeline-windows option is specifically a two-GPU layer-split path and is not an applicable one-GPU knob. Windows large pages still require a user-right/session change; no such change has been made. The fixed numeric sampling and every quality/workload gate remain in force; the goal stays active and unqualified, including Q007's two incomplete answers.


## E066 / Current upstream and profiler reassessment

The previous goal turn was progress: resident-copy throughput was measured and rejected, rotation was refused before measurement, and preflight corrections were tested. Fresh read-only GitHub queries again found main fb58e0dbc8399662c0e47c76578c6e878b14f6cf and latest release v0.1.41 unchanged. No newer stable Strata release is waiting to apply. Reviewed current PR1742/1744 (SM86 prefill),1741 (pipelined service early exit),1737 (approximate routing kernel),1544 (exact CPU singleton) and1548 (dynamic PCIe balance). URLs, exact PR heads and applicability limits are retained in diagnostics/research-refresh/E066/sources.json. Nothing was posted upstream or imported blindly.

Approximate resident routing remains excluded despite the attractive reported speed: that mode changes expert selection and the source report measured output-distribution/quality distortion. The SM86 prefill proposals make no decode claim; the singleton proposal's dispatch does not run under the retained multi-token minimum of1. The current one-GPU verifier calls run(), not the pipelined service() addressed by1741. Dynamic PCIe fitting is a potential architectural lead, but its existing evidence is below a manually tuned fraction on the reported machine and does not establish a win against this control.

Rechecked P009 collected kernel/API statistics and P005 host decode timing. The incomplete Nsight trace remains diagnostic, not a complete critical-path partition or speed proof. CPU service plus GPU-reach/transfer wait remain material. Six-token drafting lost in R041; two-token drafting has not been measured. R047 is a fresh unchanged control, then R048 changes only --spec4 to2 on the same retained engine/libraries. The existing suffix policy consequently permits at most four rather than six rows. Every target sampler, context, precision, thinking and quality requirement remains fixed. The detailed hypothesis and rejection/promotion rules are recorded before the experiment.


## E067 / R047-fresh-control

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.1 (84.5-93.2) | 204.0 | 76.5356 | 76.5499 | 0.8632 | 863/1139 (75.77%) |
| longer | 80.9 (78.6-83.8) | 495.8 | 41.1061 | 41.1115 | 6.1567 | 906/1248 (72.60%) |

Minimum available physical RAM 64,167,477,248 bytes; available commit 42,260,922,368 bytes. Sampled GPU peak 25,222,799,360 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Fresh unchanged control:87.1 short and80.9 longer server decode tok/s. The complete seed ranges are84.5-93.2 and78.6-83.8; a93.2 peak is not qualification. This is a current paired reference for R048, not a new promoted configuration or a replacement for earlier controls.

Next: Run R048 with only the MTP depth reduced from4 to2; every target sampling, model, context and quality condition is unchanged.


## E068 / R048-spec2

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.5 (82.6-87.0) | 206.1 | 75.0765 | 75.0951 | 0.8489 | 701/897 (78.15%) |
| longer | 80.8 (76.8-82.1) | 496.5 | 41.0873 | 41.0913 | 6.1494 | 825/1038 (79.48%) |

Minimum available physical RAM 64,197,320,704 bytes; available commit 42,335,342,592 bytes. Sampled GPU peak 25,187,147,776 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Two-token MTP finished at85.5/80.8 short/longer server decode tok/s, versus the fresh R047 control87.1/80.9. Short E2E also fell. Reject this smaller-window candidate; the target90 threshold was not met and the marginal prompt increase does not offset decode/client regression. Four-token MTP remains the retained configuration.

Next: Audit P009 trace coverage offline, then select a different kernel or scheduling intervention from verified stage costs rather than repeating losing draft limits.


## E069 / P010 retrospective P009 coverage audit; balance theory

Terminology correction: the P009 warning alone does not establish that kernels were lost. A [version-matched NVIDIA forum explanation](https://forums.developer.nvidia.com/t/nsight-systems-2026-5-1-produced-112-collected-100-warning-despite-complete-coverage-of-32-kernels/384749) says its separate probe emitted the warning because of a forced flush. That probe used Linux and ordinary launches, so its conclusion does not automatically transfer to this Windows graph trace. P009 coverage was unproven; calling it definitely incomplete based only on the warning was too strong. The [official guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html) also distinguishes graph-level from more costly node tracing. No instrumented rate becomes a qualification result.

The read-only SQLite audit found 759,910 kernel records, all with positive intervals. All 996 graph-launch API keys match graph kernel activity keys, in both directions. Across fourteen graph identities, every repeated launch contains the same node multiset as that graph's first observed launch, with no duplicate node IDs within a launch. All 12,628 direct kernel keys match launch APIs. The other 65 launch APIs sit inside one stream-capture interval; 65 graph nodes were created there, and their original IDs exactly match the nodes executed by graph41. Thus those calls are graph construction, not 65 unexplained missing kernel executions. All recorded launch API return values were zero.

This reconciles recorded launches and graph cohorts internally. It does not independently enumerate every node expected by the application, prove all memory-transfer records present, or detect a uniformly absent API/activity pair. The producer855077 and collected804251 totals represent different categories/phases and cannot be treated as a dropped-kernel count. A second process reported zero produced events and no collected CUDA events; those diagnostics remain separately identified by global PID. The audit records the database hash, queries and detailed counts. Raw capture metadata can contain inherited environment values, so only an explicit nonprivate metadata allowlist is exported; the SQLite/NSYS artifacts remain local.

The first ad-hoc correlation query was stopped after an unindexed correlated join ran slowly; the saved audit uses sets and linear scans and completed in about two seconds without a model resident. This analysis never ran alongside a measured request.

R048 accounting supplement: reducing --spec4 to2 also reduced maximum suffix window/buffer size. With automatic cache sizing, startup loaded8412 GPU experts instead of R047's8409 (both rounded15.95GiB). This is a recorded consequence of the flag, not an independently fixed cache amount. The smaller-window arm still lost decode/client speed and remains rejected.

The next controlled test R049 retains four-token MTP and changes PCIe fraction0.20 to0.10. Original calibration predated the retained CPU-dispatch improvements, so the old share need not be optimal for the faster CPU path. Source assigns a rounded integer fraction of distinct missed experts to the GPU; the candidate keeps all expert computations and weights. Source proof and the predeclared workload/rejection rules are in pcie-after-cpu-plan.md. R047 and R049 startup both show8409 GPU experts. A lower transfer count alone is not a win, and changed CPU/GPU rounding still requires the full quality gate before any promotion.


## E070 / R049-pcie010

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.6 (86.1-89.7) | 200.5 | 75.9130 | 75.9269 | 0.8658 | 849/1128 (75.27%) |
| longer | 85.3 (81.9-87.1) | 497.1 | 42.2071 | 42.2127 | 6.1415 | 930/1240 (75.00%) |

Minimum available physical RAM 64,216,748,032 bytes; available commit 42,317,918,208 bytes. Sampled GPU peak 25,224,896,512 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

PCIe fraction0.10 finished at86.6/85.3 short/longer server decode tok/s, versus fresh control87.1/80.9. Longer improved in this pair, but short decode/E2E and prompt median were slightly lower. The result is mixed and below90 in both cells; no promotion. Preserve all runs and repeat in the opposite arm/workload order before deciding whether the apparent longer gain is reproducible.

Next: R050 repeats PCIe0.10 with longer-first workload order, then R051 repeats the unchanged PCIe0.20 control with longer-first order, completing an AB/BA comparison. No benchmark model resident between arms.


## E071 / R050-pcie010-reverse

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.3 (84.5-88.0) | 202.3 | 76.7701 | 76.7805 | 0.8478 | 863/1100 (78.45%) |
| longer | 85.1 (80.5-86.5) | 496.2 | 42.1489 | 42.1520 | 6.1579 | 1026/1337 (76.74%) |

Minimum available physical RAM 64,239,681,536 bytes; available commit 42,343,604,224 bytes. Sampled GPU peak 25,216,507,904 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

The opposite-workload-order PCIe0.10 repeat reached87.3/85.1 short/longer server decode tok/s. The candidate repeats remain below90. Keep this result unpromoted until the opposite-order0.20 control completes; the first control pair alone cannot establish the apparent longer-input gain.

Next: Run R051 unchanged0.20 control in longer-first order, then compare ordinary pooled medians over all ten measured runs per setting and workload, preserving each fresh-process result.


## E072 / R051-control-reverse

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.8 (86.5-88.4) | 201.9 | 76.8112 | 76.8261 | 0.8574 | 916/1168 (78.42%) |
| longer | 82.3 (78.3-86.6) | 496.4 | 41.4649 | 41.4680 | 6.1575 | 960/1330 (72.18%) |

Minimum available physical RAM 64,174,030,848 bytes; available commit 42,262,347,776 bytes. Sampled GPU peak 25,216,507,904 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

The unchanged PCIe 0.20 control in longer-first order reached 87.8/82.3 short/longer server decode tok/s. The four-arm PCIe AB/BA comparison is complete; neither setting reaches 90 in both workloads. Preserve individual-process results and compare all ten measured runs per setting before any conclusion.

Next: Compute the complete R047/R049/R050/R051 AB/BA comparison, keep the retained production setting, and inspect the profiled Q6 single-column shape distribution before choosing a new kernel theory.


## E073 / PCIe 0.20 versus 0.10, complete AB/BA

The predeclared four fresh processes are complete: R047 control, R049 candidate,
R050 candidate with longer-first order, R051 control with longer-first order.
Each contains one excluded warmup plus five measured seeds per workload. All ten
measured rows per setting/workload enter the ordinary median below. Every matched
request JSON is byte-identical across all four arms, including benchmark identifier,
seed, sampling, reasoning, prompt, streaming and output cap. All measured requests
generated 512 tokens with zero cached prompt tokens. Engine and loaded-library
hashes match; normalized configurations differ only in PCIe fraction.

| Workload / setting | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short / 0.20 | 87.30 (84.5-93.2) | 202.95 | 76.62434 | 76.64000 | 0.85977 | 1779/2307 |
| short / 0.10 | 86.85 (84.5-89.7) | 201.50 | 75.99213 | 76.00865 | 0.85682 | 1712/2228 |
| longer / 0.20 | 82.20 (78.3-86.6) | 496.15 | 41.42366 | 41.42733 | 6.15712 | 1866/2578 |
| longer / 0.10 | 85.20 (80.5-87.1) | 496.80 | 42.17801 | 42.18236 | 6.14922 | 1956/2577 |

PCIe 0.10 changes short decode by -0.52%, prompt throughput by -0.71%, and
request E2E throughput by -0.83%. Longer decode improves by 3.65%, prompt by
0.13%, and E2E by 1.82%. Short process medians are 87.1/87.8 for control and
86.6/87.3 for candidate; longer process medians are 80.9/82.3 and 85.3/85.1.
These small samples establish a mixed observed result, not a confidence interval
or a universal causal improvement. The ten rows repeat five seeds across two
processes, and the fixed TTLCache prompt does not represent every coding task.

Decision: unpromoted. The apparent longer-input gain survives workload-order
reversal, but short decode/client/prompt medians decrease and neither setting
meets the complete 90 tok/s contract. Keep production PCIe 0.20. A pooled median
does not override a failing per-process qualification cell. Q007 still has two
incomplete coding answers, and these arms did not repeat the full random-coding,
cold/cache-hit/nonstream/long-context/tool/vision matrix.

All four arms passed the independent 16 GiB physical/commit floors and full-tree
cleanup. Post-comparison independent cleanup again found no live launcher, server,
text engine or vision process; port 8080 was closed, GPU memory 553 MiB and the
production config SHA256 was 3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0.

Next: P011 breaks down the existing Q6 single-column trace by projection shape.
C028 will test the already parity-checked row grouping on actual smaller dense
tensors, where C021 did not measure timing. No server or model is launched for the
offline audit; the isolated kernel diagnostic releases all allocations afterward.


## E074 / C028 dense Q6_K projection diagnostic

P011's read-only geometry audit finds the Q6_K cohort with 2560 output rows
accounts for 157.10 ms in 8000 recorded calls. The full-head and reduced-vocabulary
cohorts account for 120.48 and 137.18 ms respectively; 10240-row projections add
118.41 ms. These are summed instrumented durations, not exclusive critical-path
shares. GGUF metadata resolves the six dense shapes tested below. C021 timed only
the output head, so C028 reuses its unchanged row grouping on actual dense tensors.

Each diagnostic passed 1008 cases and 1,558,608 finite, bitwise-equal float
comparisons on six actual tensors, eight activation patterns, seven odd/full row
counts and three candidates, with output canaries intact. Timing uses one uncaptured
priming call and one captured warmup per variant (both excluded), then eleven
alternating forward/reverse rounds, a graph of 64 repeated
projections per sample, and CUDA events. All raw rows are archived. Neither this
synthetic activation test nor kernel timing qualifies output quality or served TPS.
In the raw CSV, label 1 means the unchanged four-warps-per-row reference, not a
one-warp CTA. Candidate labels 2/4/8 name the row or warp grouping under test.

| Actual tensor | Input/output | Reference median, us | rows_per_cta=2, us | =4, us | =8, us |
|---|---:|---:|---:|---:|---:|
| blk.0.attn_qkv.weight | 2560/10240 | 27.038 | 29.788 | 33.632 | 45.408 |
| blk.0.ssm_out.weight | 6144/2560 | 16.800 | 17.888 | 24.432 | 24.304 |
| blk.1.attn_gate.weight | 2560/6144 | 17.306 | 19.744 | 21.536 | 32.688 |
| blk.2.ffn_up_shexp.weight | 2560/640 | 3.325 | 3.904 | 5.104 | 7.520 |
| blk.3.attn_k.weight | 2560/512 | 3.232 | 3.824 | 5.136 | 7.408 |
| blk.31.attn_q.weight | 2560/12288 | 31.760 | 35.294 | 39.824 | 55.248 |

Decision: reject all dense row-group candidates. Every candidate median is slower; no production source, config or launcher changes. Next: test one physical warp per row with the original ordered virtual partials (C029).


## E075 / C029 dense Q6_K projection diagnostic

This tests a different mapping: one physical warp computes each row while
retaining four virtual partial sums, the original modulo-four block order, Q6/Q8
dot helpers, ordered partial additions and XOR reduction. Removing shared memory
and the CTA barrier increases work/register demand per lane. The deliberately
zero-output RED stub failed on pattern 1, one output row, group 2: reference
0x3e0a7c9a versus 0x00000000. The implemented candidate then passed every parity
case. The production native reference links from the unchanged C022 library.

Each diagnostic passed 1008 cases and 1,558,608 finite, bitwise-equal float
comparisons on six actual tensors, eight activation patterns, seven odd/full row
counts and three candidates, with output canaries intact. Timing uses one uncaptured
priming call and one captured warmup per variant (both excluded), then eleven
alternating forward/reverse rounds, a graph of 64 repeated
projections per sample, and CUDA events. All raw rows are archived. Neither this
synthetic activation test nor kernel timing qualifies output quality or served TPS.
In the raw CSV, label 1 means the unchanged four-warps-per-row reference, not a
one-warp CTA. Candidate labels 2/4/8 name the row or warp grouping under test.

| Actual tensor | Input/output | Reference median, us | warps_per_cta=2, us | =4, us | =8, us |
|---|---:|---:|---:|---:|---:|
| blk.0.attn_qkv.weight | 2560/10240 | 27.360 | 27.840 | 27.104 | 27.404 |
| blk.0.ssm_out.weight | 6144/2560 | 16.652 | 18.286 | 18.160 | 18.160 |
| blk.1.attn_gate.weight | 2560/6144 | 17.328 | 18.748 | 17.328 | 17.600 |
| blk.2.ffn_up_shexp.weight | 2560/640 | 3.311 | 4.352 | 4.416 | 4.444 |
| blk.3.attn_k.weight | 2560/512 | 3.248 | 4.384 | 4.496 | 4.267 |
| blk.31.attn_q.weight | 2560/12288 | 32.592 | 33.424 | 33.675 | 34.160 |

Decision: reject as a general or served candidate. Five shapes tie or lose; the
10240-row four-warp CTA improves only 0.94% in this small diagnostic (27.360 to
27.104 us). That tiny isolated difference does not establish a repeatable service
gain or justify another full-model run. No production dispatch was modified.

Both diagnostics release allocations and reset the device. GPU memory returned
to 553 MiB and no model/server was resident. Device-wide allocated memory during
the small diagnostics was approximately 1.31-1.34 billion bytes, including context
and other processes; it is not the standalone graph size. CUDA 13.4 is only the
paired diagnostic compiler, not a promoted production toolchain change.

The Q6 mapping branch is closed for now. Next architectural question: can a
deterministic, workload-aware CPU/GPU missed-expert assignment retain the short
behavior of PCIe 0.20 and longer behavior of 0.10? Inspect the upstream balance
controller and current schedule dependencies before any code change; reject
timing-dependent quality shortcuts. The fixed 90 TPS matrix, Q007 coding failures,
prompt/client-rate preservation and safe memory gates remain in force.


## E076 / R052-pcie000

Same retained production engine and loaded library hashes as R037. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.7 (84.4-90.1) | 196.0 | 74.7886 | 74.8024 | 0.8834 | 879/1130 (77.79%) |
| longer | 84.0 (80.7-87.8) | 495.0 | 41.8174 | 41.8219 | 6.1676 | 951/1289 (73.78%) |

Minimum available physical RAM 63,746,965,504 bytes; available commit 42,041,077,760 bytes. Sampled GPU peak 25,109,200,896 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Zero PCIe share reached 85.7/84.0 short/longer server decode tok/s. Compared with same-order R051 control 87.8/82.3, short decode, prompt throughput and client rate fell; reject this setting as a stack component. All 8409 GPU-cache slots remained present. Production stays at PCIe 0.20.

Next: Confirm the narrow C029 2560/10240 four-warp-CTA component with the retained CUDA 13.3 toolchain, all 22 actual tensors of that shape and three fresh processes each. Preserve small verified gains for interaction testing rather than requiring any component to reach 90 alone.


## E077 / C030 small-component confirmation and interaction plan

User steering explicitly calls for combining below-target improvements while
checking their interactions. A component does not need to reach 90 tok/s alone.
Ruling: reopen only C029's 2560/10240 group-4 case, which won 10/11 initial paired
rounds, rather than discard it because its isolated gain is small. The general
Q6 mapping remains rejected; the narrow case required confirmation first.

C030 uses the retained CUDA 13.3.73 compiler and unchanged reference library on
all 22 actual Q6_K tensors of that shape. Three fresh processes per tensor retain
eleven alternating timing rounds each, excluding both priming and graph warmup.
The middle pass reverses tensor order. All 66 process medians favor the preselected
group-4 candidate: median candidate/reference time ratio 0.985704, range
0.956067-0.997541. That is about 1.43% less kernel time at the median process ratio,
not an estimate of whole-request throughput. Every tensor's 33 timing values,
every process median, and alternative group measurements remain in the raw files.

All 11,088 parity cases and 32,486,256 finite float comparisons were bitwise equal,
with output canaries intact. The kernel keeps the original quantization, per-lane
four-part accumulation order and reduction. No target sampler runs in this test.
Each process resets the CUDA device; GPU memory returned to451MiB, with no server
or benchmark model resident. The desktop's idle allocation was lower than the
earlier553MiB baseline; R052 nevertheless retained8409 cache slots.

Decision: verified kernel component, pending integrated-source and served checks.
Add a CUDA-only opt-in for exactly the measured single-column shape; defaults and
other shapes retain original dispatch. C031 first captured the old native graph
and failed the requested activation check (onewarp0, expected1), then the code was
added. The first build command used a nonexistent CMake path and failed before
compiling; the corrected command uses the established .venv CMake. These command
and test failures are retained. Build and integrated parity checks are in progress.

The factorial stack plan preserves A (retained stack), A+B, A+C and A+B+C, then
reverses order in fresh processes. It measures interaction instead of adding
percentages. R052's zero PCIe share is not a component because it regressed short,
prompt and client metrics. PCIe0.10 remains mixed, not promoted. Every served test
retains the fixed model, quant,262144 context, thinking sampling and quality gates.


## E078 / C031-C032 integrated Q6 opt-in; R053 memory stop

The narrow CUDA-only STRATA_Q6_ONEWARP=1 component is now implemented for
single-column Q6_K projections with input width2560 and output width10240.
Four physical warps own four rows. Each lane retains four virtual partials and
the original ordered combination and warp reduction. Unset, zero and all other
shapes retain the original dispatch. No sampling, precision or model change.

C031 graph inspection failed against the unchanged library before implementation,
then passed against the new library. Independent review found no blocking issue;
its requested additional wrong-input/correct-output shape2304/10240 now passes,
alongside eligible, wrong-output, both-wrong and multicolumn shapes. All five
dispatch cases passed with the flag absent, zero and one. Both existing CUDA
MMVQ parity suites passed (2/2). CUDA13.3.73 Release sm_86 was built; HIP/SYCL
execution is unavailable and is not claimed. The initial nonexistent CMake-path
failure and the corrected build command remain archived.

C032 links the actual integrated native entry against an independent copy of the
original reference. Both flag modes across all22 actual tensors passed2,464 cases
and7,219,168 finite bitwise float comparisons, including odd/full row counts and
eight activation patterns. Output canaries passed. All44 subprocesses exited and
GPU usage returned to451MiB. The first PowerShell runner invocation had a string
interpolation parse error before execution; it was corrected before these checks.
These are kernel-correctness results, not served TPS or coding-answer proof.

R053 attempted the rebuilt binary with the opt-in disabled, preserving the
retained configuration. It produced no completed warmup or measured run. The
independent memory guard stopped it at physical headroom39,973,257,216 bytes and
commit headroom16,785,092,608 bytes, below the16GiB commit floor. All launcher,
server, engine and vision processes were stopped; the production config was
restored byte-for-byte and GPU returned to451MiB. No TPS is assigned to this arm.

Startup cache8409, prefill8192, ring384 and borrowed-cache2315 match R051. The
R053 starting commit headroom was about8.28GB lower than R051; the subsequent
growth remains unexplained. The retained executable is therefore being rerun
under current host conditions before attributing this to the code or enabling
the new dispatch. Safety floors remain unchanged. Production is not promoted.
The small component remains a candidate for stacking, subject to the same
sampling, quality, memory and workload contract. Goal90 remains active.


## E079 / R055 retained-engine memory failure; R056 diagnostic repeat

R055 repeats the retained production executable and fixed profile under current
host conditions. Its memory guard also stopped the arm: physical headroom
40,795,901,952 bytes and commit16,578,236,416 bytes, below the16GiB floor.
There is no complete qualifying summary. All completed and interrupted request
payloads, raw SSE, outputs and timing rows remain archived, including longer
runs at13.3 and13.6 server decode tok/s. These failures are not dropped in favor
of a successful repeat. The failure therefore is not unique to the Q6 rebuild.

R056 adds a diagnostic-only early-stop hook below32GiB commit headroom, at which
point it would capture process private/RSS attribution once and then stop. The
hook never triggered; no process-memory query ran during generation. The fixed
original requests, sampling,512-token cap and five measured seeds were retained.
All ten measured requests completed. Ordinary medians: short86.8 and longer84.2
server_decode_tps; prompt200.9/496.2; request_e2e75.8817/41.9018; TTFT0.8742/6.1570s.
The longer69.5 tok/s run remains included (range69.5-86.3). This diagnostic is
not a promotion or proof that the intermittent memory failure is resolved.
Minimum physical/commit headroom61,737,230,336/39,387,676,672 bytes passed both
original16GiB floors. Raw all-run statistics and the modified supervisor are saved.

Both arms completed full launcher-tree cleanup and restored the production config
SHA2563457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0.
Direct Computer Use inspection after cleanup found Task Manager on Performance /
Memory. It was not showing a Strata details row; that observation does not prove
or rule out observer interference. No Task Manager setting was changed. UI capture
raised the subsequent idle GPU sample to773MiB from451MiB, so another idle check
is required before any comparison. Screenshots and unrelated app details are not
published. Attribution of the intermittent commit growth remains unresolved.

Next: repeat the rebuilt disabled control with the normal observer and the same
payloads. Do not infer a code regression from R053 alone, and do not silently
exclude R055 or its slow rows. Enable the exact Q6 component only after a stable
control; evaluate combinations as measured interactions, not summed percentages.
Goal90 remains active, fixed thinking sampling and all quality gates unchanged.


## E080 / R057-q6-disabled-retry

Explicitly verified candidate engine SHA256 1dfeecd9869c266e82961426026e14c82ff822e0e004898959a900925ea57cf4; loaded library hashes match R056-memory-attribution. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 83.5 (80.2-93.4) | 189.9 | 72.6606 | 72.6703 | 0.9268 | 887/1179 (75.23%) |
| longer | 82.6 (79.6-84.4) | 497.7 | 41.5393 | 41.5423 | 6.1465 | 988/1303 (75.83%) |

Minimum available physical RAM 62,133,624,832 bytes; available commit 39,957,852,160 bytes. Sampled GPU peak 25,380,110,336 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Rebuilt disabled control completed at83.5/82.6 short/longer server decode tok/s. The intermittent memory stop did not reproduce; this does not erase R053 or R055. All8409 cache slots retained. No promotion.

Next: Complete same-binary enabled comparison and reverse-order confirmation before judging the small component.


## E081 / R054-q6-enabled

Same engine and loaded library hashes as R057-q6-disabled-retry. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 84.5 (83.6-86.2) | 193.9 | 73.9178 | 73.9352 | 0.9107 | 877/1171 (74.89%) |
| longer | 81.5 (75.8-84.2) | 496.8 | 40.7532 | 40.7574 | 6.1539 | 986/1336 (73.80%) |

Minimum available physical RAM 61,753,532,416 bytes; available commit 39,369,736,192 bytes. Sampled GPU peak 25,408,487,424 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Same-binary Q6 opt-in changed short decode83.5 to84.5 and longer82.6 to81.5 tok/s. Requests were byte-identical, only STRATA_Q6_ONEWARP changed,8409 cache slots retained. Mixed first pair, not a verified served gain; retain for reverse-order confirmation rather than adding isolated percentages.

Next: Run enabled then disabled in fresh processes with longer-first workload order, preserving all runs and fixed sampling.


## E082 / R058-q6-enabled-reverse

Same engine and loaded library hashes as R057-q6-disabled-retry. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 84.7 (83.3-89.7) | 188.4 | 73.8539 | 73.8712 | 0.9239 | 938/1238 (75.77%) |
| longer | 80.9 (76.6-85.2) | 497.9 | 41.0989 | 41.1625 | 6.1458 | 960/1330 (72.18%) |

Minimum available physical RAM 62,375,604,224 bytes; available commit 40,273,682,432 bytes. Sampled GPU peak 25,371,656,192 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Enabled reverse-order repeat completed84.7/80.9 short/longer server decode tok/s. All8409 cache slots retained; no memory stop. Q6 remains unpromoted.

Next: Complete the paired disabled reverse-order comparison, then evaluate the predeclared PCIe0.10 interaction.


## E083 / R059-q6-disabled-reverse

Same engine and loaded library hashes as R057-q6-disabled-retry. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.0 (83.7-88.3) | 197.0 | 74.3307 | 74.3445 | 0.8920 | 859/1141 (75.28%) |
| longer | 83.7 (80.7-84.7) | 496.1 | 41.7360 | 41.7404 | 6.1610 | 924/1241 (74.46%) |

Minimum available physical RAM 62,262,190,080 bytes; available commit 40,038,105,088 bytes. Sampled GPU peak 25,345,077,248 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Disabled reverse-order repeat completed85.0/83.7 short/longer server decode tok/s. Across AB/BA, ordinary ten-run medians off84.75/82.70 versus on84.60/81.20 show no verified served gain. Keep Q6 disabled in production. The standalone kernel gain is not a served-speed claim.

Next: Measure the same binary at PCIe0.10 with Q6 disabled and enabled; accept only a combination that removes regressions across all metrics.


## E084 / Q6 AB/BA result and conditional interaction test

Ten measured rows per workload/flag, all retained: off84.75/82.70 versus
on84.60/81.20 short/longer ordinary median server_decode_tps. Short prompt
195.80 versus193.35, longer496.25 versus497.15. Client E2E73.9670/41.5853
versus73.8859/40.9434. The small kernel win did not establish a served gain at
PCIe0.20; the production switch remains off. No peak or selected seed is promoted.

Test the predeclared interaction with PCIe0.10 because its previous longer gain
came with a slight short regression. Both components are conditional candidates,
not independent production winners. The new plan fixes A/B/C/D configurations,
all-run medians, request equality and fresh-process opposite-order checks. A
combination must remove regressions, not merely beat one losing component.

Repository hygiene:18,451 local generated build/download/diagnostic files were
still visible to Git as untracked scratch. Added only /local-setup/ and /.tools/
to the local .git/info/exclude; git check-ignore verified both. No files were
deleted. Scrubbed public bench/results evidence remains tracked and published.
This reduces irrelevant workspace scanning; it is not proof of the cause of
R053/R055 memory growth and is not reported as a model throughput improvement.
The four completed Q6 served arms had no memory stop. Goal90 remains active.


## E085 / R060-q6off-pcie010

Same engine and loaded library hashes as R057-q6-disabled-retry. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.0 (84.9-90.2) | 207.8 | 76.3433 | 76.3579 | 0.8493 | 792/1075 (73.67%) |
| longer | 81.8 (73.4-86.0) | 495.3 | 41.3312 | 41.3342 | 6.1738 | 916/1283 (71.40%) |

Minimum available physical RAM 61,906,137,088 bytes; available commit 39,734,501,376 bytes. Sampled GPU peak 25,291,358,208 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Factorial C: Q6 off and PCIe0.10 completed87.0/81.8 short/longer server decode tok/s; all8409 cache slots retained. Conditional candidate only, not promoted.

Next: Complete D and the predeclared D/C reverse-order pair before computing interaction.


## E086 / R061-q6on-pcie010

Same engine and loaded library hashes as R060-q6off-pcie010. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.1 (86.2-88.1) | 203.5 | 76.1571 | 76.1709 | 0.8683 | 864/1122 (77.01%) |
| longer | 81.0 (79.6-83.8) | 495.8 | 41.1120 | 41.1152 | 6.1658 | 929/1291 (71.96%) |

Minimum available physical RAM 62,423,752,704 bytes; available commit 40,322,920,448 bytes. Sampled GPU peak 25,279,496,192 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Factorial D: adding Q6 toPCIe0.10 changed short87.0 to87.1 and longer81.8 to81.0 tok/s. Short prompt and client throughput also fell. No useful first-pair synergy; no promotion.

Next: Finish R062/R063 opposite-order confirmation, retain all rows, then close or retain this combination based on the complete matrix.


## E087 / R062-q6on-pcie010-reverse

Same engine and loaded library hashes as R061-q6on-pcie010. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.9 (85.3-89.4) | 203.3 | 76.6546 | 76.6695 | 0.8724 | 833/1057 (78.81%) |
| longer | 84.0 (82.1-85.3) | 495.8 | 41.8085 | 41.8128 | 6.1648 | 1041/1379 (75.49%) |

Minimum available physical RAM 62,351,650,816 bytes; available commit 40,301,572,096 bytes. Sampled GPU peak 25,261,015,040 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Combined reverse-order repeat completed87.9/84.0 short/longer server decode tok/s with safe memory and full cleanup. This process median alone does not qualify or prove an interaction.

Next: Record the final C control and calculate the entire fixed factorial matrix.


## E088 / R063-q6off-pcie010-reverse

Same engine and loaded library hashes as R060-q6off-pcie010. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.9 (84.9-91.8) | 201.1 | 75.4871 | 75.5018 | 0.8508 | 841/1088 (77.30%) |
| longer | 84.4 (80.8-86.6) | 495.4 | 41.9538 | 41.9584 | 6.1717 | 1037/1347 (76.99%) |

Minimum available physical RAM 62,783,791,104 bytes; available commit 40,855,494,656 bytes. Sampled GPU peak 25,253,347,328 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Final PCIe0.10 Q6-disabled reverse-order control completed; retain all five seeds per workload and compare against every matching enabled row. No candidate is promoted by this record.

Next: Calculate the four-configuration interaction with all ten measured rows per workload/configuration; refresh upstream and move to the next scheduling theory if the stack does not pass.


## E089 / complete Q6 and PCIe interaction matrix

Every cell below contains ten measured runs from two fresh processes, each with
one excluded warmup and five measured seeds. All measured requests generated 512
tokens with zero reused prompt tokens. Input JSON is byte-identical by label.
The binary, loaded CUDA libraries, GGUF shards, projector, expert profile,
262,144 context, INT8 KV, vision and thinking sampling match. Every arm retained
8,409 GPU cache slots. Only the named Q6 flag and PCIe share differ.

These are ordinary medians of every measured row, not averages of process medians.
Per-process summaries, ranges and every raw value are in factorial.json. A/B and
C/D are separate AB/BA blocks; temporal drift is a limitation of this matrix.
The earlier memory failures remain in the ledger and are not hidden by this table.

| Setting | Q6 | PCIe share | Workload | Decode tok/s | Prompt tok/s | E2E tok/s | Stream tok/s | TTFT s |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| A | 0 | 0.20 | short | 84.75 | 195.80 | 73.9670 | 73.9834 | 0.8942 |
| A | 0 | 0.20 | longer | 82.70 | 496.25 | 41.5853 | 41.5884 | 6.1490 |
| B | 1 | 0.20 | short | 84.60 | 193.35 | 73.8859 | 73.9032 | 0.9127 |
| B | 1 | 0.20 | longer | 81.20 | 497.15 | 40.9434 | 40.9772 | 6.1479 |
| C | 0 | 0.10 | short | 86.60 | 204.80 | 75.9383 | 75.9526 | 0.8501 |
| C | 0 | 0.10 | longer | 83.20 | 495.35 | 41.6315 | 41.6363 | 6.1728 |
| D | 1 | 0.10 | short | 87.50 | 203.40 | 76.4059 | 76.4202 | 0.8699 |
| D | 1 | 0.10 | longer | 82.85 | 495.80 | 41.5816 | 41.5852 | 6.1653 |

The combination does not reach the target. Compared with PCIe 0.10 alone,
Q6 improves the pooled short decode median but lowers the longer decode median.
It is therefore not a verified improvement across both workloads. Its exact
kernel speedup is real within C030's microbenchmark, but cannot be promoted as a
served-speed win. Production retains its previous engine and settings. All eight
arms completed full-tree cleanup and passed the original host-memory floors.
Full coding, cold/warm, tools, vision and maximum-context qualification is not
claimed. Q007's incomplete coding answers remain an unresolved quality gate.

The arithmetic interaction is retained in factorial.json as (D-C)-(B-A), in each
metric's own units. A positive interaction does not imply that D beats C, reaches
90 tok/s, or meets the prompt/client no-regression requirement.

Next: close this Q6/PCIe combination as unpromoted; refresh upstream and test the existing device-side resident-group planning path only after its parity and activation checks. Fixed thinking sampling and goal90 remain unchanged.


## E090 / retire Q6 shipping code; resident-planner activation proven

The completed interaction matrix did not establish an across-workload Q6 benefit.
Removed only the new Q6 kernel/dispatch and its shipping test; git diff against
745b5e38 confirms native_mmvq.cu returned to the prior source. The archived source,
all tests and prototype commit e564208a remain available for reproduction. The
retained production executable was never overwritten or promoted to this candidate.

Refreshed upstream through the required GitHub App helper: main remains
fb58e0dbc8399662c0e47c76578c6e878b14f6cf and latest release remains v0.1.41,
published2026-10-08T12:14:59Z. No update was available to apply.

New hypothesis and finite budget are in diagnostics/device-plan/P012/device-plan-experiment.md.
Existing P009 trace supplied the wait/copy evidence; no new baseline trace was
collected. The existing CUDA resident_plan parity suite passed641 cases with zero
failures. Source inspection confirmed partial-cache, single-stage eligibility,
foresight disabled, and lag2 event completion before residency publication.

P012 then captured one excluded warmup and one complete512-token frozen random
coding request with STRATA_VERIFY_DEVICE_PLAN=1 on the retained6048736d engine.
Nsight recorded16,032 resident_plan kernels (none in P009), proving execution.
Their summed instrumented duration was33.592ms;48,096 wait_flag_ge_or calls summed
726.911ms. These are overlapping instrumented sums, not critical-path percentages
or served improvements. The profiled request reported68.4 server decode tok/s;
it is explicitly nonqualifying. Profiling reduced cache capacity to8,394 slots
versus8,409 in ordinary runs, another reason not to compare profiled TPS directly.

Independent physical/commit headroom stayed above59,917,492,224/36,158,709,760 bytes.
The wrapper and outer supervisor cleaned the whole model tree and restored the
production config. The redundant outer Nsight shutdown reported a closed connection
after the inner shutdown had already completed; the nested finally still executed
and verified model cleanup. Idle GPU returned to581MiB. No benchmark model remains.

Next is one unprofiled off/on pair, five measured seeds after one warmup per short
and ~3K workload. Another reversed pair is conditional on promising served decode,
prompt rate and client latency. No endless repeats of this hypothesis. The fixed
model, quant,262144 context, vision, thinking profile and every quality gate remain.


## E091 / R064-deviceplan-control

Same engine and loaded library hashes as R056-memory-attribution. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.5 (86.9-88.9) | 206.0 | 76.8105 | 76.8245 | 0.8486 | 812/1079 (75.25%) |
| longer | 84.3 (82.9-84.5) | 497.0 | 41.9748 | 41.9795 | 6.1479 | 915/1228 (74.51%) |

Minimum available physical RAM 62,691,651,584 bytes; available commit 40,731,168,768 bytes. Sampled GPU peak 25,264,357,376 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Fresh retained-binary device-plan control; short 87.5 and longer 84.3 server_decode_tps. Fixed sampling and context, five measured seeds per workload. Full quality matrix remains incomplete.

Next: Compare predeclared R065 device-plan enabled arm.


## E092 / R065-deviceplan-enabled

Same engine and loaded library hashes as R064-deviceplan-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 84.3 (81.1-86.4) | 206.1 | 73.6851 | 73.6951 | 0.8374 | 851/1135 (74.98%) |
| longer | 78.5 (78.1-81.7) | 496.1 | 40.4569 | 40.4623 | 6.1658 | 911/1276 (71.39%) |

Minimum available physical RAM 62,584,963,072 bytes; available commit 40,618,774,528 bytes. Sampled GPU peak 25,273,040,896 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Reject STRATA_VERIFY_DEVICE_PLAN=1: short median 84.3 versus 87.5 control; longer 78.5 versus 84.3. Activation proven in P012 but served throughput regressed. Finite experiment budget closes this hypothesis; no repeat or promotion.

Next: Investigate hyper-connection kernels using existing P009 trace; preserve production configuration and fixed quality gates.


## E093 / C034 hyper-connection fast-path screening

Existing P009 shows20,886 gr_up_multi<1,true> calls totaling252.274ms instrumented
kernel duration, not a critical-path percentage. Existing STRATA_GR_FAST=1 uses
eight lanes per row and preserves the reduction tree. CUDA defaults off here.
No shipping source change is needed; staged HC norm/down remain selected.

The upstream eager benchmark passed32/32 bitwise comparisons but reports minima;
its timings are diagnostic only. A local graph-replay adaptation then passed all
32 comparisons (T1..8, pending-write on/off, injection on/off). Seven alternating
timing rounds after one excluded warmup,200 reads per graph, all raw samples saved.
T1 fast/control median-time ratios were0.934376,0.936346,0.927058,0.923352.
T2..4 with no pending write lost1.1-3.4%; corresponding pending-write cells won
5.6-6.7%. T5..8 all improved. These are synthetic kernel timings, not served TPS.
The mixed multi-token result and dominant T1 improvement justify one off/on pair;
no promotion and no claim that quality or the90 TPS contract is satisfied.

Budget: R066 fresh retained-binary control and R067 STRATA_GR_FAST=1, otherwise
identical fixed sampling/context/vision, five seeds per short/~3K cell. Only an
across-workload served benefit with intact prompt/client rates permits a reversed
pair. Otherwise close. Numerical screening does not replace full coding quality.
Evidence: diagnostics/hyper-connection/C034. NVIDIA graph guidance links in plan.


## E094 / R066-grfast-control

Same engine and loaded library hashes as R064-deviceplan-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.9 (82.6-88.3) | 201.4 | 75.8938 | 75.9039 | 0.8634 | 843/1140 (73.95%) |
| longer | 82.7 (80.3-85.8) | 495.7 | 41.5126 | 41.5168 | 6.1668 | 862/1180 (73.05%) |

Minimum available physical RAM 62,547,136,512 bytes; available commit 40,615,669,760 bytes. Sampled GPU peak 25,263,800,320 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Fresh control for STRATA_GR_FAST; short 86.9, longer 82.7 server_decode_tps. No production change.

Next: Compare R067 with exactly one environment flag changed.


## E095 / R067-grfast-enabled

Same engine and loaded library hashes as R066-grfast-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.7 (86.5-89.2) | 204.2 | 77.2461 | 77.2577 | 0.8504 | 886/1157 (76.58%) |
| longer | 83.1 (80.6-86.1) | 496.1 | 41.6313 | 41.6370 | 6.1699 | 875/1215 (72.02%) |

Minimum available physical RAM 62,655,672,320 bytes; available commit 40,728,608,768 bytes. Sampled GPU peak 25,270,124,544 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Promising first pair: short 88.7 versus 86.9, longer 83.1 versus 82.7; prompt and client median rates also improve. Longer TTFT increases slightly. Below target and not promoted; reverse order confirmation required.

Next: R068 enabled then R069 disabled, both longer-first; full quality gates remain mandatory.


## E096 / R068-grfast-enabled-reverse

Same engine and loaded library hashes as R066-grfast-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.4 (85.2-88.2) | 191.8 | 75.5408 | 75.5544 | 0.9040 | 797/1040 (76.63%) |
| longer | 84.3 (82.9-85.0) | 496.2 | 41.9354 | 41.9413 | 6.1635 | 979/1361 (71.93%) |

Minimum available physical RAM 62,614,597,632 bytes; available commit 40,662,786,048 bytes. Sampled GPU peak 25,258,721,280 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Reverse-order fast-path repeat: short 86.4, longer 84.3 server_decode_tps. Short prompt 191.8 tok/s; this run alone does not prove no regression. No promotion.

Next: Pool both enabled processes against both controls without removing slow seeds.


## E097 / R069-grfast-control-reverse

Same engine and loaded library hashes as R066-grfast-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 84.5 (83.6-90.5) | 199.3 | 73.9941 | 74.0035 | 0.8777 | 850/1137 (74.76%) |
| longer | 83.5 (81.5-86.5) | 495.8 | 41.7202 | 41.7235 | 6.1678 | 919/1263 (72.76%) |

Minimum available physical RAM 62,591,614,976 bytes; available commit 40,653,860,864 bytes. Sampled GPU peak 25,257,934,848 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Reverse-order control: short 84.5, longer 83.5 server_decode_tps; full cleanup and safety gates passed. Compare complete ABBA raw rows.

Next: Close bounded fast-path experiment using all-run medians and prompt/client metrics.


## E098 / HC fast ABBA and bounded PCIe interaction

Four fresh processes, one excluded warmup and five measured seeds per workload
per process. The second pair reverses both arm and workload order. Each table
cell is the ordinary median of all ten measured512-token requests, with zero
cached prompt tokens. Request JSON, binary, libraries, model shards, projector,
expert profile and all config except STRATA_GR_FAST match. Cache8409 in all arms.
The script asserts those properties; abba.json preserves every value and process
summary. Hardware, runtime and fixed262144-context thinking profile are unchanged.

| Setting | Workload | Decode tok/s | Prompt tok/s | E2E tok/s | Stream tok/s | TTFT s |
|---|---|---:|---:|---:|---:|---:|
| off | short | 85.00 | 200.35 | 74.4052 | 74.4213 | 0.8716 |
| off | longer | 83.10 | 495.75 | 41.6164 | 41.6201 | 6.1673 |
| on | short | 87.30 | 202.75 | 76.4360 | 76.4482 | 0.8696 |
| on | longer | 83.15 | 496.15 | 41.6442 | 41.6494 | 6.1664 |

Short decode improved2.71%; the longer result is effectively tied (+0.06%).
Both individual paired short and longer decode medians increased, but the second
enabled process had slower short prompt processing. Pooled prompt/client medians
do not regress. Retain as a combination candidate, not a promoted configuration.
This does not meet90 TPS or the full quality/stability/workload matrix. Q007's
two incomplete coding answers remain unresolved. Synthetic bitwise parity is
necessary evidence for unchanged arithmetic, not a substitute for coding quality.
All four arms passed both16GiB memory floors and complete process-tree cleanup.

## Next bounded interaction

E073 found PCIe share0.10 improved longer decode82.2 to85.2 but slightly lowered
short decode87.3 to86.85. Fast HC now improves short and ties longer. Hypothesis:
their different costs (GPU HC arithmetic vs missed-expert transfer/CPU division)
may complement each other. They also share GPU scheduling and host waits, so
additivity is explicitly unproven. No sampler, precision or context change.

Budget: one fresh R070 fast=1/PCIe0.20 control and R071 fast=1/PCIe0.10 candidate,
same fixed short/~3K requests, warmup+five measured seeds each. Only if both
decode medians improve and prompt/client rates do not fall, permit one reversed
pair. Otherwise close this combination. No more repetitions to chase a peak.
Any retention still requires activation and full fixed quality/matrix checks.


## E099 / R070-grfast-pcie020

Same engine and loaded library hashes as R067-grfast-enabled. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.1 (84.8-88.1) | 202.2 | 75.3052 | 75.3182 | 0.8710 | 803/1068 (75.19%) |
| longer | 83.1 (81.5-88.1) | 496.0 | 41.6311 | 41.6351 | 6.1623 | 987/1299 (75.98%) |

Minimum available physical RAM 62,272,811,008 bytes; available commit 39,816,007,680 bytes. Sampled GPU peak 25,270,976,512 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Fresh fast-kernel PCIe0.20 control: short 86.1, longer 83.1 server_decode_tps. Same retained executable and fixed profile. All rows preserved.

Next: Compare R071 lower PCIe share under the predeclared no-regression rule.


## E100 / R071-grfast-pcie010

Same engine and loaded library hashes as R070-grfast-pcie020. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.9 (84.5-90.7) | 205.8 | 75.4163 | 75.4302 | 0.8525 | 928/1210 (76.69%) |
| longer | 82.9 (81.7-84.4) | 496.1 | 41.6246 | 41.6289 | 6.1594 | 950/1272 (74.69%) |

Minimum available physical RAM 62,643,515,392 bytes; available commit 40,750,952,448 bytes. Sampled GPU peak 25,270,648,832 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Reject combination: short 85.9 versus 86.1 control, longer 82.9 versus 83.1. Longer client rate also slightly lower. A 90.7 short peak does not qualify. Finite budget closes this interaction; no reversed pair, no promotion.

Next: Archive completed comparisons; larger dataflow alternatives need a new explicit theory and finite budget. Fixed contract and production launcher retained.


## E101 / HC and PCIe interaction closed; next architecture screen

R070/R071 preserve byte-identical request JSON and exact binary, loaded libraries,
GGUF, projector and expert-profile identities; configs differ only in PCIe share.
With HC fast enabled, lowering share0.20 to0.10 changed short decode86.1 to85.9,
longer83.1 to82.9; longer E2E41.6311 to41.6246. This fails the predeclared rule.
Close this interaction without another pair. Peak90.7 is not a qualifying result.
Production launcher and config remain unchanged; full cleanup verified after both
arms. Production config SHA256 is3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0.
Idle GPU after cleanup589MiB. No benchmark model remains resident.

The earlier predeclared four-process HC ABBA comparison remains available in
diagnostics/hyper-connection/abba.json. Include R070 as well when describing the
candidate's cumulative results: all-fast020-runs.json contains all15 measured
rows per workload across R067/R068/R070, not a selected fast subset.

All15 fast/PCIe0.20 short rows: decode median86.50, prompt202.30, E2E75.7012, stream75.7241 tok/s; TTFT0.8710s.

All15 fast/PCIe0.20 longer rows: decode median83.10, prompt496.10, E2E41.6313, stream41.6370 tok/s; TTFT6.1632s.

Remaining architecture hypothesis, not implemented or benchmarked: compress the
BF16 HC projection storage losslessly relative to current packed weights using
the source Q8_0 blocks, reconstruct the exact BF16-rounded coefficients on load,
and preserve the current accumulation tree. P009's HC projection read costs make
bandwidth reduction a plausible mechanism. The existing STRATA_HC_Q8 is NOT this
candidate: fused_gr.cu explicitly changes both weights and reduction order, and
native_dense.cpp adds another allocation without releasing the packed weights.
Do not enable it as a shortcut or call it quality-neutral. A new candidate needs
all-actual-tensor reconstruction parity, graph microbenchmark and finite budget
before any integration or served test. No source or runtime change for this idea.

Q007 still has3/5 compiled/tested answers and2/5 incomplete answers. The full90
TPS contract is not qualified. Keep the objective unchanged. The goal tool still
reported a preexisting blocked status at this turn's entry; the user explicitly
resumed work, but the available update_goal interface cannot set active. No
completion or threshold change was made. The durable campaign retains active
optimization intent and this exact resume checkpoint.


## E102 / C035 exact HC source screen

The exact GSQ-RCO IQ3_S target has no Q8_0 hyper-connection source tensors.
All387 target HC tensors were enumerated across both actual GGUF shards and
matched to the live configuration's pack index:290BF16 and97F32 tensors.
Every one of640,624,640 coefficients was compared across1,283,235,840 packed
bytes, with zero mismatching bytes. Per-tensor source/packed/reconstructed
SHA256, shapes, types, byte sizes and counts are preserved in C035-result.json.

The draft model was separately checked:11HC tensors,19,773,440 coefficients,
zero Q8 source tensors and zero mismatching bytes. BF16 values are unchanged;
F32 normalization follows the existing packer's FP32 source+1 transform.
C035-draft-result.json records the exact method and hashes for every tensor.

This disproves the prerequisite of E101's proposed source-Q8 storage strategy.
The source comment about Q8 projections applies to other model variants; it
does not describe this resolved GSQ-RCO artifact. No new quantization, model
substitution or output-changing STRATA_HC_Q8 path was used. The finite plan
closed at its eligibility gate: no CUDA microbenchmark, source integration,
server launch or TPS claim. No repeat is warranted for the same artifacts.

The target comparison took12.392s. Minimum physical/commit headroom during it
was120,180,817,920/123,979,243,520 bytes, above both16GiB floors. Only tensor
metadata and HC coefficients were read; no full model allocation. The initial
WMI enumeration included stale Python process records, but live-process cleanup
verification found no live Strata launcher, server, engine or vision process.
Initial GPU usage523MiB. Production config hash and all quality requirements
remain unchanged. The90 TPS objective is still unqualified, not completed.

Next: reframe around the actual BF16 source representation or measured host/
device scheduling costs. A lossless format would require its own demonstrated
compression and exact reconstruction, not assumed source Q8 blocks. Do not
repeat Q6, device-planning or lower-PCIe combinations already closed in ledger.


## E103 / C036 lossless BF16 block format

Hypothesis and finite gates were written in c036-plan.md before the full screen.
The actual BF16 source permits a lossless block format: original sign/mantissa
bits, four-bit exponent offsets and exact BF16 fallback blocks. This is not Q8
quantization. Every one of659,374,080 coefficients across298 target/draft BF16
HC tensors reconstructed bit for bit. Headers/fallbacks included, storage fell
from1,318,748,160 to1,074,217,408 bytes (18.5426%);99.7926% of blocks were eligible.
Original pack/model files were read-only. Norm tensors remained unchanged.

The standalone CUDA13.3 sm86 prototype then compared the existing eight-FMA and
xor reduction tree against the same arithmetic fed by reconstructed BF16 values.
It used the first/middle/last target up-projection in sorted name order, actual
weights, T1..5 and three bounded random input sets. All45 comparisons passed:
1,382,400 finite output floats were bitwise equal. The exact source dot helpers
were copied from fused_gr.cu; no production kernel was modified.

Each timing cell uses200 projection calls per graph, one excluded warmup per
variant and seven alternating measured rounds. All raw rounds are retained;
ordinary medians are below. These are isolated kernel diagnostics, not served TPS.

| Tensor ID | T | Original median us | Packed median us | Packed/original |
|---|---:|---:|---:|---:|
| 0 | 1 | 7.607680 | 11.873280 | 1.560697 |
| 0 | 2 | 10.071041 | 14.612480 | 1.450940 |
| 0 | 3 | 12.071680 | 16.788481 | 1.390733 |
| 0 | 4 | 14.175839 | 18.739199 | 1.321911 |
| 0 | 5 | 14.945281 | 18.938721 | 1.267204 |
| 1 | 1 | 7.055360 | 10.337280 | 1.465167 |
| 1 | 2 | 8.908800 | 12.472320 | 1.400000 |
| 1 | 3 | 10.525921 | 14.136321 | 1.343001 |
| 1 | 4 | 12.260799 | 16.091681 | 1.312450 |
| 1 | 5 | 14.658560 | 18.691999 | 1.275159 |
| 2 | 1 | 51.164162 | 44.917759 | 0.877914 |
| 2 | 2 | 10.525121 | 15.143359 | 1.438782 |
| 2 | 3 | 12.180480 | 16.885759 | 1.386297 |
| 2 | 4 | 14.295040 | 18.953119 | 1.325853 |
| 2 | 5 | 17.638399 | 21.253120 | 1.204935 |

Decision: reject.14/15 cells took20.49-56.07% more GPU time. The first two T1
cells lost46.52-56.07%, failing the required>=5% improvement on every selected
tensor. The last T1 cell has elevated timings and a12.21% apparent gain; it is
retained, not discarded or promoted. Its cause was not investigated because the
other cells already decisively fail the finite retention rule. No repeat, model
launch, integration, launcher change or altered quality gate followed.

The CPU eligibility pass took27.201s, with minimum physical/commit headroom
121,236,983,808/124,016,676,864 bytes. The GPU prototype allocates only three small
tensor representations for one tensor at a time and exits after testing; it is
not a resident model. Tensor copies and executable remain private local scratch;
public evidence contains source, hashes, inventory, parity and all raw timings.

This result rejects this particular per-block exponent decoder. It does not
prove that all lossless storage is slow. A different format needs genuinely new
evidence and a new bounded hypothesis rather than tuning this failed screen.
Next useful direction is measured host/device scheduling or removal of work;
do not repeat closed Q6, device-planning, PCIe or this format without new evidence.
The unchanged90 TPS objective remains unqualified; Q007 still has incomplete
coding answers. Production configuration, model, sampling, context and vision
remain unchanged, and no benchmark model is left resident.


## E104 / C037 expert-fetch scheduling screen

The predeclared offline screen replaced per-vector64-bit division with per-block
blob/stripe assignment. Both paths retain384 blocks,256 threads and identical
16-byte copies. P009 established the kernel's presence; instrumented duration
was not interpreted as a critical-path percentage. Current upstream main remains
fb58e0dbc8399662c0e47c76578c6e878b14f6cf; no update was available.

All140 parity/guard cases passed across seven actual model blob sizes, counts
0,1,2,3,4,5,7,8,16,64 and both paths. A total3,131,392,000
copied bytes were verified against pinned host input, including source-pointer
permutation and untouched destination prefix/tail guards. Data patterns are
synthetic; exact copy parity is independent of tensor arithmetic.

CUDA13.3.73/sm86 graph timing used32 copies per graph, one excluded warmup per
variant and seven alternating measured rounds. Ordinary medians and every raw
round are retained. Nonempty geometric mean candidate/control ratio0.999604
fails the required<=0.95; cell range0.979664..1.021740.
Maximum empty-call penalty0.224000us. Reject without another run or integration.
The unchanged copier's measured payload bandwidth median was
6.440GB/s (decimal), range6.211..6.466.
This supports a bandwidth-bound interpretation for this isolated transfer screen,
not a proof of the whole engine's bottleneck or physical TPS ceiling.

| Blob bytes | Count | Original us | Candidate us | Ratio |
|---:|---:|---:|---:|---:|
| 1510400 | 0 | 1.433000 | 1.376000 | 0.960223 |
| 1510400 | 1 | 234.303996 | 234.043002 | 0.998886 |
| 1510400 | 2 | 468.032002 | 467.005014 | 0.997806 |
| 1510400 | 4 | 935.711980 | 938.015997 | 1.002462 |
| 1510400 | 8 | 1872.128010 | 1880.473971 | 1.004458 |
| 1715200 | 0 | 2.272000 | 2.227000 | 0.980194 |
| 1715200 | 1 | 267.866999 | 267.520010 | 0.998705 |
| 1715200 | 2 | 531.418979 | 529.247999 | 0.995915 |
| 1715200 | 4 | 1068.639994 | 1083.423972 | 1.013834 |
| 1715200 | 8 | 2122.047901 | 2168.181896 | 1.021740 |
| 1868800 | 0 | 2.272000 | 2.240000 | 0.985915 |
| 1868800 | 1 | 290.847987 | 291.359007 | 1.001757 |
| 1868800 | 2 | 590.080023 | 578.079998 | 0.979664 |
| 1868800 | 4 | 1171.607018 | 1157.248020 | 0.987744 |
| 1868800 | 8 | 2355.360031 | 2355.999947 | 1.000272 |
| 1971200 | 0 | 1.888000 | 2.039000 | 1.079979 |
| 1971200 | 1 | 307.289988 | 307.608008 | 1.001035 |
| 1971200 | 2 | 610.656023 | 611.168027 | 1.000838 |
| 1971200 | 4 | 1224.279046 | 1223.423958 | 0.999302 |
| 1971200 | 8 | 2538.877010 | 2510.047913 | 0.988645 |
| 2176000 | 0 | 1.504000 | 1.728000 | 1.148936 |
| 2176000 | 1 | 338.164002 | 337.433010 | 0.997838 |
| 2176000 | 2 | 674.965978 | 674.399018 | 0.999160 |
| 2176000 | 4 | 1349.753976 | 1351.552010 | 1.001332 |
| 2176000 | 8 | 2727.072001 | 2696.928024 | 0.988946 |
| 2329600 | 0 | 1.459000 | 1.408000 | 0.965045 |
| 2329600 | 1 | 360.960007 | 360.222012 | 0.997955 |
| 2329600 | 2 | 723.551989 | 721.271992 | 0.996849 |
| 2329600 | 4 | 1448.384047 | 1445.119977 | 0.997746 |
| 2329600 | 8 | 2906.719923 | 2917.632103 | 1.003754 |
| 2662400 | 0 | 1.472000 | 1.404000 | 0.953804 |
| 2662400 | 1 | 411.872000 | 411.552012 | 0.999223 |
| 2662400 | 2 | 824.703991 | 829.501987 | 1.005818 |
| 2662400 | 4 | 1651.826978 | 1648.733974 | 0.998128 |
| 2662400 | 8 | 3310.688019 | 3343.647957 | 1.009956 |


Memory was checked with one global snapshot, not continuous monitoring:
physical120,894,988,288 and
commit124,079,091,712 bytes available, above
the original16GiB floors. Fixed host/device allocations were below0.5GiB each.
The process exited successfully and no model server was launched. No production
source, launcher, quality gate, sampling, context, vision or model changes.

Next direction: reduce transfers through a separately justified residency or
prefetch architecture, rather than reworking this already bandwidth-limited copy
loop. Prior lower-PCIe-share, device-plan and cache-profile failures remain binding
evidence; do not repeat them without a distinct new mechanism. Full90 TPS and
coding quality qualification remain unmet. The goal tool now reports active.


## E105 / C038 concurrent shared-quantization screen

The offline experiment tested eliminating duplicate activation quantization while
retaining the concurrent routed/shared expert branches. Production currently
calls `quantize_q8_1_rows` for routed experts and `native_quantize_q8_1` for shared
experts. Existing STRATA_VERIFY_QDEDUP is disabled when the shared stream forks.
The proposed candidate quantized once before the existing fork event and let
both branches read that immutable image; separate outputs and the join remained.
No engine, launcher, sampler, model, context or quality-gate change was made.

This was a CUDA13.3.73/sm86 offline DAG screen with actual gate/up weights from
model layers0,23,47 (Q4_K/IQ4_XS, Q5_K/Q5_K, Q4_K/Q5_K), N2560/M640,
T1..8, and zero / bounded random inputs at scales.001,1,100. The two branch
consumers were dense GEMVs, not the complete routed/shared expert pipeline.
Each timing graph held100 DAGs; one excluded warmup plus seven alternating
measured rounds. All raw results and sources are attached. Actual weight bytes
and executables remain private; manifest retains names, sizes and hashes.

The screen passed21 parity cases then stopped with exit4 at layer0/T6/scale.001.
Five completed timing cells are retained as partial, disqualified evidence:
candidate/control ratios.846774,.860435,.890000,.920574,.842430.
These are kernel-DAG timing ratios, not served TPS; they cannot qualify a winner.

A separate correctness-only diagnostic used the exact same deterministic input
sequence and ran both quantizers sequentially on one stream. It found3 mismatching
cases out of96, each one quantized int8 byte:

| Layer | T | Input scale | Byte offset | Routed signed byte | Shared signed byte |
|---:|---:|---:|---:|---:|---:|
| 0 | 6 | .001 | 14433 | -86 | -87 |
| 23 | 8 | 1 | 5435 | -124 | -125 |
| 47 | 4 | 100 | 1791 | 68 | 69 |

Hexadecimal input floats for all three32-value counterexample blocks are saved
in C038-diagnostic.txt. Sequential reproduction rules out stream ordering as the
cause of these mismatches. Build metadata shows --use_fast_math on native_mmvq.cu
but not iq_kernels.cu; both source paths use xi/d and roundf. A division-rounding
difference is consistent with this evidence, but not yet instruction-level proven.
Do not fix this by forcing one quantizer onto both branches: that would change
the baseline arithmetic. Current production does not enable QDEDUP; this is not
evidence of a newly introduced production regression.

The original all-parity gate failed, so the shared-buffer hypothesis is closed.
There was no second timing attempt, integrated build, or served benchmark.
Next distinct mechanism: investigate a dual-output quantization kernel that reads
the input once but preserves both original arithmetic paths and writes separate
byte images. Require these exact counterexamples and broader parity checks before
any timing or integration. Potential DAG savings do not establish a TPS gain.

Prefetch review also closed the existing Foresight path as an experiment choice:
docs/DETAILS.md1447-1456 reports lower medians on several cards and the same result
on dual RTX3090. The implementation admits copies via cudaEventQuery, allocates
extra slots at the expert cache's expense, and adds timing-dependent residency.
No distinct new mechanism justified repeating that path on this host.

The host headroom snapshot exceeded both16GiB floors. Fixed prototype allocations
were below128MiB; memory was not continuously sampled. Both executables exited;
no model was loaded. Cleanup verified no live Strata process and457MiB idle GPU
memory. Production config and executable hashes match the retained baseline.
The90 TPS goal remains active; no new served result or quality qualification.


## E106 / C039 exact dual-output quantization

C038's counterexamples prompted inspection of the current CUDA13.3 object PTX.
The native quantizer uses div.approx.ftz.f32 and FTZ reduction operations; the
routed quantizer uses div.rn.f32 and retains subnormal arithmetic. Both extracted
PTX entry points are attached. The new prototype reads an input once, computes
both original arithmetic paths, and writes distinct36-byte Q8_1 blocks. It does
not exchange their images, change weights, sampling, context or expert selection.

The regression fixture first reproduced the known failure with a shared-image
stub. The dual-output implementation then passed all96 C038 actual-weight DAG
cases, including all three original counterexamples. An additional4096-case
corpus compared47,185,920 finite input values and106,168,320 output bytes, with
untouched prefix/tail guards. It includes signed zero, subnormals, the first normal
exponent, mixed finite exponents and values that exercise FP16-scale/sum clamping.
These tests passed again against the integrated production API, independently of
the prototype definition. CUDA13.3.73/sm86; no HIP or SYCL build was performed.

The predeclared single timing process used actual layer0/23/47 shared gate/up
weights, N2560/M640, T1..8, two concurrent GEMV consumers,100 DAGs per graph,
one excluded warmup and seven alternating measured rounds per cell. Every raw
round is attached. Ordinary cell medians gave a geometric mean candidate/control
time ratio0.934193051, range0.868036..0.967430.
That is about6.58% less time in this isolated DAG. It is not served
TPS or proof of whole-engine benefit. The >=5% aggregate/no>3% regression gate
passed, permitting an opt-in engine experiment.

Integration was guarded by STRATA_DUAL_Q8=1 (defaultoff), CUDA, native expert
layout, a late shared-stream fork, no preexisting QFUSE image, and G==1. The
single-group condition avoids overwriting shared scratch while another group is
still executing. The CPU doorbell remains before the new kernel; the existing
fork event follows it. The shared expert receives its fast image and retains its
own hidden-state scratch; routed experts retain their precise image. Existing
join ordering remains before the next layer. A one-time capture log proved
activation at T4 in R073. Default/off remains the original quantization path.

The integration patch, regression source, build commands/logs and binary hashes
are archived. Upstream main remained fb58e0dbc8399662c0e47c76578c6e878b14f6cf;
no update was available. The test binary SHA256 is
ca6551bc7fcd095032c082408378adf91c476a48d48e7e223988c0d4c06beefc.

R072/R073 used the SAME candidate binary with only STRATA_DUAL_Q8 changed0->1,
GR_FAST0, and the retained production numerical/settings contract. Every arm
used fresh process state, one excluded warmup and five measured seeds101..105
per original short/~3K cache-miss workload,512 tokens, one request at a time.
R072 control decode medians87.4/81.2; R073 candidate85.7/80.8 tok/s.
Prompt medians201.2/496.1 vs205.5/497.1; request-E2E76.4100/41.1743 vs
75.3068/41.1098 tok/s. Detailed ranges, TTFT, stream TPS, MTP and memory are
recorded in E107/E108. Both decode medians fell, so reject without another pair
or stacking it with GR_FAST. There is no qualifying90 TPS result.

All12 output-text pairs differ, and the request's cache-miss nonce also differs;
these served files are not an exact-input bitwise comparison. The512-token
speed runs are capped thinking continuations, not completed-answer quality
qualification. Full coding/workload qualification remains unresolved as before.

The source edits were restored byte-for-byte from the pre-experiment checkpoint
and the experimental regression test was archived then removed from tools/.
The retained executable/config hashes remain6048736d... and3457fdfe....
Both benchmark launcher trees stopped cleanly; idle GPU457MiB, no model resident.
The build-cuda86-main object directory still holds this candidate and must be
rebuilt from restored sources before calling it a new baseline build.

Next: reassess CPU expert execution/code generation against the existing host
timings and exact mixed-format inventory. Do not repeat shared-quant scheduling,
Q6 one-warp, Foresight, device planning or lower-PCIe combinations absent a new
mechanism. Current production settings remain unchanged; the goal stays active.


## E107 / R072-dualq-off

Explicitly verified candidate engine SHA256 ca6551bc7fcd095032c082408378adf91c476a48d48e7e223988c0d4c06beefc; loaded library hashes match R070-grfast-pcie020. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.4 (85.0-90.1) | 201.2 | 76.4100 | 76.4235 | 0.8509 | 877/1137 (77.13%) |
| longer | 81.2 (79.3-85.8) | 496.1 | 41.1743 | 41.1774 | 6.1606 | 961/1359 (70.71%) |

Minimum available physical RAM 62,731,513,856 bytes; available commit 40,977,375,232 bytes. Sampled GPU peak 25,130,110,976 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Fresh default-off control for C039 candidate binary; GR_FAST0, PCIe.20. All measured rows retained. Source/build patch is archived under C039; this is not a launcher promotion.

Next: Compare only STRATA_DUAL_Q8=1 in R073 using the same binary and fixed contract.


## E108 / R073-dualq-on

Same engine and loaded library hashes as R072-dualq-off. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.7 (83.7-88.5) | 205.5 | 75.3068 | 75.3253 | 0.8487 | 862/1162 (74.18%) |
| longer | 80.8 (79.9-83.6) | 497.1 | 41.1098 | 41.1129 | 6.1436 | 876/1248 (70.19%) |

Minimum available physical RAM 62,705,815,552 bytes; available commit 40,997,621,760 bytes. Sampled GPU peak 25,117,528,064 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Reject dual-output quantization: short decode85.7 versus87.4, longer80.8 versus81.2 tok/s. Prompt processing improved slightly but both generation medians fell. Activation at T4 confirmed. Production source restored; original launcher/executable untouched.

Next: Reassess CPU expert code generation against existing traces and actual mixed formats. Closed GPU scheduling paths are not to be repeated without a new mechanism.


## E109 / C040 Blanket Clang GU rejected

Clang19.1.5 replaced GU code generation across IQ3_XXS/IQ3_S/IQ2_S while retaining MSVC pool/down/quantization. All576 actual-weight pool-output cases (48layers, experts0/173/511, T1/2/4/8) matched bitwise. Synthetic large-weight pool timing:27cells, nine workers plus host0,30tasks, T1/2/4, jobs1/3/6; one warmup and five alternating rounds of100calls. Geomean candidate/control time .9484517 but worst1.1166899. Predeclared no-cell>3% regression gate FAILED. Blanket replacement rejected. All failed cells retained; no served speed claim.

Artifacts: diagnostics/cpu-compiler/C040/README.md


## E110 / C041 Selective IQ3_S Clang GU passed independent offline gate

A distinct format-selective hypothesis follows the blanket failure. Fresh MSVC19.44.35228.0 and Clang19.1.5 copies of the SAME iq_avx2.cpp coexist with renamed symbols. Clang flags /O2 /MT /EHsc /arch:AVX2 /fp:precise /clang:-ffp-contract=off, STRATA_AVXVNNI0. Explicit FMA intrinsics retained; no reassociation/fast math. All576 actual-weight full-pool outputs matched bitwise. Independent timing used ten actual IQ3_S layers and64experts/layer ((29+17*i)%512), beyond L3; T1/2/4, jobs1/3/6, nineworkers+host0,30tasks, one warmup+five alternating100call rounds:90cells. All90 parity checks passed. Geomean time ratio .8492428922, minimum .7299289867, maximum1.0100528315. PASS >=5% geomean gain/no cell>3% slower. About15.1% less CPU pool time is NOT served token generation improvement. Other formats/down projections retain MSVC.

Artifacts: diagnostics/cpu-compiler/C041/README.md


## E111 / C042 Opt-in integrated compiler candidate ready for served validation

Added defaultOFF STRATA_CLANG_IQ3S CMake option and defaultOFF STRATA_IQ3S_CLANG runtime dispatch. Windows/MSVC portable static-runtime builds only, explicit clang-cl path; separate compiler symbols. Only type21 AVX2 GU can switch, VNNI and all other formats retain existing dispatch. Red fixture first failed missing dispatch; green on/off checks passed. Integrated actual-weight576 full pool outputs matched bitwise; existing iq_avx2_parity reports0 failures. CUDA13.3.73/sm86 engine rebuilt, including GPU sources restored after C039. No HIP/SYCL validation or review request. No model/context/sampling/weights changed. R074/R075 will compare runtimeOFF/ON with same binary, fixed TTLCache contract. This remains experimental; no launcher promotion and goal active.

Artifacts: diagnostics/cpu-compiler/C042/README.md


## E112 / R074-clang-off

Explicitly verified candidate engine SHA256 8b39f7c08733abcf4fbe3b4cc76f7599e7b928b34eb1361d1f4d05d51bb50e3d; loaded library hashes match R072-dualq-off. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.5 (85.0-89.0) | 200.0 | 76.5906 | 76.6010 | 0.8650 | 924/1257 (73.51%) |
| longer | 83.3 (82.0-84.0) | 496.2 | 41.6844 | 41.6915 | 6.1595 | 935/1278 (73.16%) |

Minimum available physical RAM 62,641,897,472 bytes; available commit 40,920,264,704 bytes. Sampled GPU peak 25,130,110,976 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C042 same-binary compiler runtimeOFF control: decode87.5/83.3; prompt200.0/496.2. R075 will isolate the IQ3_S GU compiler. No promotion or quality qualification.

Next: Evaluate R075 runtimeON against this control and reject any regression.


## E113 / R075-clang-on

Same engine and loaded library hashes as R074-clang-off. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.5 (82.9-90.1) | 204.2 | 76.6508 | 76.6620 | 0.8541 | 870/1182 (73.60%) |
| longer | 82.6 (80.6-85.9) | 496.7 | 41.4387 | 41.4416 | 6.1518 | 961/1325 (72.53%) |

Minimum available physical RAM 62,644,117,504 bytes; available commit 40,929,189,888 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C042 rejected: runtimeON decode87.5/82.6 versus87.5/83.3 control; short tie and longer regression. Prompt204.2/496.7 versus200.0/496.2. The15.1% independent CPU pool gain did not transfer to served generation. No repeat or stacking retry. Production source restored; retained launcher unchanged.

Next: Reassess critical-path overlap before another kernel edit; isolated pool/kernel gains have repeatedly failed to improve served generation. Keep all closed paths closed absent a new mechanism.


## E114 / P013 overlap audit

Offline interval-union audit of existing P009, no model launched. Recorded CUDA activity spans8271.267ms:6691.268ms with any recorded kernel/memcpy/memset and1579.998ms without recorded activity. Memcpy-only-category time768.870ms; wait-flag-only642.708ms; Q6MMVQ-family-only944.558ms. These are temporal categories, NOT dependency critical paths, removable latency, or proof of idle hardware/CPU stalls. P010 coverage limits remain. Pinned H2D:3973calls,8,041,226,240bytes,1295.604ms summed. Existing adaptive copy submission is a distinct candidate; kernel sum reductions alone have not consistently improved served TPS. Raw NSYS/SQLite remain private; only allowlisted interval summaries exported. Artifacts: diagnostics/profiler/P013/.


## E115 / C043 existing batch-transfer correctness

Existing DMA batch byte/event-order test passed63cases with allocated pinned memory and63cases with Windows registered memory on CUDA13.3.73/sm86. This is transfer correctness, not generation quality. Aggregate diagnostic timing for registered48x2MiB: submission .3348ms individual vs .0431ms batch; total15.6793ms vs15.6212ms. Raw repeat times are absent from this upstream test, so no all-run campaign speed claim. R076 runtimeOFF control was allowed to finish when the user prioritized upstream PR review. R077 runtimeON has NOT run; candidate and activation remain unmeasured. No production change. Artifacts: diagnostics/dma-batch/C043/.


## E116 / R076-dma-off

Same engine and loaded library hashes as R037-observer-no-process. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.6 (85.1-88.7) | 202.1 | 76.4687 | 76.4797 | 0.8717 | 843/1088 (77.48%) |
| longer | 84.9 (80.5-86.7) | 495.4 | 42.0905 | 42.0963 | 6.1622 | 974/1277 (76.27%) |

Minimum available physical RAM 62,620,717,056 bytes; available commit 40,869,150,720 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Fresh retained-engine control, explicit STRATA_DMA_BATCH0: decode87.6/84.9, prompt202.1/495.4. R077 not run: user requested upstream PR review during this arm; in-flight measurement finished undisturbed, then exact cleanup. No candidate comparison or promotion.

Next: Prioritize finite upstream PR compatibility review; keep C043 runtimeON unmeasured.


## E117 / P014 upstream review

Verified origin **Niko1221/Strata**, main `fb58e0dbc8399662c0e47c76578c6e878b14f6cf` unchanged. Fork is notmike101/Strata; working branch remains perf/rtx3090-thinking-80. Screened158unique open titles across the newest100 plus targeted searches,30merged listings, and14full metadata/diff sets. This is a bounded review, not a claim to audit every open PR.

- [#1779](https://github.com/Niko1221/Strata/pull/1779) at `f3727b2464321a35c4638491d75bcda1d4ecbb9c`: Excluded: explicitly requires distinct-GPU layer split; this host has one GPU. Includes dependencies1656/1674; no partial import.
- [#1744](https://github.com/Niko1221/Strata/pull/1744) at `0701e617b93c8ea37984d2121ce3b1447f0c4e81`: Compatible SM86 prefill lead, deferred: changes fused prompt path only; no decode claim; separate enable/build flags required.
- [#1742](https://github.com/Niko1221/Strata/pull/1742) at `fab43d049ebb57a2cdac25ca34de7dcb089f4993`: Compatible SM86 prefill lead, deferred: modest reported prompt gain, no decode change; do not combine with1744 blindly.
- [#1741](https://github.com/Niko1221/Strata/pull/1741) at `462a79df354d9597be6de521043f2ec3e55f7f34`: Excluded from this workload: changes Verifier::service used by pipelined windows; current one-GPU serial path uses run(). Rechecked prior E066 finding.
- [#1737](https://github.com/Niko1221/Strata/pull/1737) at `72070620821a26677c4fff85c5f3813362407fc4`: Excluded: optimizes resident-routing substitutions; enabling that policy changes expert selection, violating fixed quality contract.
- [#1720](https://github.com/Niko1221/Strata/pull/1720) at `17a16c689ea5e9c45a6b73b060c150e6ab6065b5`: Deferred prefill-only Q8_0 dequant optimization; review actual dense tensor/call-site eligibility before importing.
- [#1368](https://github.com/Niko1221/Strata/pull/1368) at `d27059967d942562c8d303c013d0c6af4fef45d1`: Promising prompt-read preservation candidate: exact per-token quantize/scatter, new symbols absent locally. Deferred behind decode candidate; distinct from rejected C038 native-vs-routed sharing.
- [#1548](https://github.com/Niko1221/Strata/pull/1548) at `a513394c4768f1d0fa13957e79b171b0fcc51c32`: Deferred architectural candidate: dynamic fitted PCIe allocation requires removing fixed pcie-frac; reported below manually tuned share. Timing-derived placement needs reproducibility design before testing.
- [#1544](https://github.com/Niko1221/Strata/pull/1544) at `9d0614f43757f8ffcd1f90b2647d4d0d31200d32`: Inactive under retained IQ_MT_MIN1: exact singleton gate is nt<mt_min. Do not change arithmetic dispatch to make benchmark benefit appear.
- [#1525](https://github.com/Niko1221/Strata/pull/1525) at `f048d15594c62335b9fa7c350ecf4d07b749d30d`: Promising prompt-only fusion/dequant candidate; new symbols absent locally. No decode claim; validate exact arithmetic independently and do not stack with1720 before conflict review.
- [#1418](https://github.com/Niko1221/Strata/pull/1418) at `8cae814e6e819736e47c95f3b5e8b056c7528c0f`: Closed mechanism overlap: multi-row activation reuse, unre-based against current interleaved kernels; related C021/C030 work already failed. No new integration without distinct applicable shapes.
- [#1095](https://github.com/Niko1221/Strata/pull/1095) at `af52a5e847c0cbb81d7b3cd94ed0bb49b9e15b0b`: Excluded as written: compile-gated experimental pre75 device; RTX3090 is sm86. Reported gain only KV gather micro, not end-to-end.
- [#1125](https://github.com/Niko1221/Strata/pull/1125) at `6dd03c47bc09afd9546a71fc54bc52186cc2c3b9`: Already implemented locally: q8k_quant_avx2 and native_quant_act/h default runtime gate present; do not reimport open PR merely because GitHub says open.
- [#1166](https://github.com/Niko1221/Strata/pull/1166) at `a71da892150aa6b30cf560c2294c936a0353c5a8`: Selected: absent HostCore::Sibling; opt-in host LP1 on physical core0, workers2/4/...18 unchanged. Distinct from rejected host-last LP18. No numerical or sampling change; upstream speed/IRQ claims not assumed true here.

Chosen action: integrate1166 locally as an opt-in, run the upstream topology test and CPU regressions, then same-binary first/sibling fixed served comparison. Source adaptation only where current generate.cpp contains additional options. Preserve original patch/hash and current integration patch. No imported performance number is accepted as this host's measurement. Default production launcher unchanged. C043 batchDMA runtime test is on hold, not silently combined.


## E118 / C044 PR1166 integration

PR1166 head a71da892150aa6b30cf560c2294c936a0353c5a8 integrated locally, opt-in; only generate.cpp patch context adapted around existing campaign options. Upstream layout test first failed compilation on missing Sibling/host_sibling (red); after integration Windows affinity tests and iq_avx2_parity passed (zero failures). Topology proof: first host0/workers2,4,6,8,10,12,14,16,18; sibling host1/SAME workers; last host18/workers0..16. CUDA13.3.73/sm86 build succeeded. No Linux/HIP/SYCL runtime test, no upstream review/merge request. No claim of IRQ placement or output-quality qualification. Next R078/R079 same-binary first/sibling comparison, no DMA/Clang changes. Candidate engine SHA256 ce7d4ecc250185acd2b14941b66c31a4c71558a0f75f03d53ca85ad11c97355f. Artifacts: diagnostics/host-sibling/C044/.


## E119 / R078-host-first

Explicitly verified candidate engine SHA256 ce7d4ecc250185acd2b14941b66c31a4c71558a0f75f03d53ca85ad11c97355f; loaded library hashes match R076-dma-off. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.4 (85.8-88.8) | 207.5 | 76.0537 | 76.0675 | 0.8356 | 824/1085 (75.94%) |
| longer | 84.2 (79.6-86.1) | 496.9 | 41.9492 | 41.9539 | 6.1521 | 931/1252 (74.36%) |

Minimum available physical RAM 62,653,054,976 bytes; available commit 40,921,882,624 bytes. Sampled GPU peak 25,119,625,216 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C044 PR1166 same-binary first-core control: decode87.4/84.2, prompt207.5/496.9. No performance/quality promotion.

Next: Compare R079 sibling against this same-binary control.


## E120 / R079-host-sibling

Same engine and loaded library hashes as R078-host-first. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.3 (85.4-90.1) | 205.3 | 76.0412 | 76.0607 | 0.8534 | 830/1074 (77.28%) |
| longer | 83.4 (80.2-85.2) | 497.0 | 41.6896 | 41.6927 | 6.1486 | 917/1244 (73.71%) |

Minimum available physical RAM 62,612,475,904 bytes; available commit 40,870,113,280 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C044 PR1166 rejected: sibling decode86.3/83.4 versus87.4/84.2 control; both generation medians fell. Prompt205.3/497.0 versus207.5/496.9; short prompt also fell. Startup proves hostLP1 with unchanged workers. No repeat or stack retry; upstream integration reverted and patch retained. Production launcher unchanged.

Next: Use P014 finite review to select exact prompt-only PR1368 or1525 with independent parity and same-day served checks; no unsupported decode promise. C043 batched-transfer runtime remains unmeasured, held for upstream priority.


## E121 / P015 batch API activation and request-identity correction

P015 traced80cudaMemcpyBatchAsync_v13000 calls, all return0, on retained engine6048736d... with DMA1. Independent16GiB physical/commit guards passed; exact cleanup and config restoration passed. This diagnostic is not qualifying TPS. Raw profiler trace stays private.

Correction to E106/C039: the earlier statement that the cache-miss nonce differed across R072/R073 was wrong. Re-reading all12saved request JSON pairs shows byte-for-byte identity; R074/R075 and R078/R079 also have12/12identical payloads. Different output text cannot be explained by changed request nonces. Exact input does not by itself establish deterministic output arithmetic; generated-text differences remain preserved and unexplained here. No quality equivalence or90TPS conclusion follows.

## E122 / C045 cumulative combination plan

The user explicitly prioritized combining smaller complementary improvements.
This replaces C043's isolated no-regression continuation rule for the NEW combined
configuration; it does not erase prior losses or relax final qualification.

## Inventory

| Status | Change / exact reference | Bottleneck and compatibility | Known interactions |
|---|---|---|---|
| Production retained | CPU F16 vision, CUDA13.3 engine6048736d..., gathered IQ3/MT_MIN1 with IQ2_S gather0, adaptive lag2; F001/F002 full20rows medians87.35/83.30 vs B006 normal CUDA13.3 CPU-vision79.2/73.0 | Frees text VRAM, CPU expert decode, copy overlap; fixed model/context/INT8KV/sampling | This is an already combined stack, not additive attribution. Q007/full90 qualification pending. |
| Implemented, unpromoted | HC-fast STRATA_GR_FAST1; R067/R068 vs R066/R069, same6048736d... binary, PCIe.20/deviceplan0; all10/cell87.30/83.15 vs85.0/83.10 | GPU hyper-connection read arithmetic; C03432bitwise cases; short gain, longer tie | Include R070 too: all15enabled .20 rows86.5/83.1. HC-fast+PCIe.10 R071 lost against R070; that combination remains closed. |
| Implemented, not yet served-tested | Batch transfers STRATA_DMA_BATCH1; C043126byte/event-order checks; P01580successful CUDA batch calls | Fewer CPU submissions/driver calls for adaptive copies; preserves immutable bytes, destinations, stream/event ordering and lag2; no added tensor buffer | Complements GPU HC work but shares PCIe/scheduling. No measured combined gain yet; no sum of percentages. |
| Rolled back, conditional future interaction | IQ3_S-only Clang C042;576actual-weight parity;90offline pool cells15.1%less time; R07587.5/82.6 vs R07487.5/83.3 | CPU GU; isolated short tie/long loss | A faster GPU could expose CPU work currently hidden by overlap. This is a possible DISTINCT interaction, not an automatic reuse. Not in this matrix; requires profiling evidence before a bounded new stack test. |
| Rolled back | PR1166 host sibling C044; R07986.3/83.4 vs R07887.4/84.2 | Host scheduling; correct topology, both decode losses | No current evidence to justify stacking it. |
| Closed | Dual-Q8 C039, Q6onewarp, device planner, PCIe.10+HC-fast, compact CPU cache, lag3/tasks/SMT/residency variants | Each has archived parity, activation and/or served failure | Do not launch a blind powerset or repeat closed combinations. Reopening requires a distinct mechanism/evidence. |
| Compatible upstream reserve | PR1368 quantize/scatter; PR1525 exact prompt fusions/dequant | Prompt processing only; absent locally | Could complement a decode winner and protect read rate; no claim these alone reach90decode. No integration in current matrix. |

## Finite comparison budget and exact next combination

A=HC0/DMA0 (R080), B=HC1/DMA0 (R081), D=HC1/DMA1 (R082),
C=HC0/DMA1 (R083), in that order. The next COMBINATION is D, HC-fast plus batch
adaptive transfers on the already retained production stack. Four fresh process
arms; each one excluded warmup and five measured seeds101..105 for BOTH original
short/~3K cache-miss tasks,512generated tokens, concurrency1. Forty measured
requests plus eight warmups. Same binary6048736d..., backend libraries, model,
262144context, CPU F16vision, INT8KV/32768resident, MTP4/.70, PCIe.20, lag2,
workers9 and tasks30. Fixed coding thinking sampling1/.95/20/0/0/1. Explicit
GR_FAST and DMA_BATCH flags are the only factors; no speculative quality flags.
No other builds/profiling/Git/GUI/process-memory polling during timed requests.
Identity every request;16GiB physical AND commit floors; exact cleanup each arm.

P015 proved batch API activation before this matrix. Prior C034/E098 establishes
HC-fast arithmetic/dispatch; the same executable is used. Check every saved
request byte-for-byte across four arms, every cap/cache count, and all memory
logs. Preserve all results, including R076's earlier control separately.

Primary assessment is D versus A under the full contract. Report B/C as
components and D-B/C-A interactions; do not reject D merely because B or C is
below90 or loses an isolated metric. No selective seeds or favorable medians.
A candidate may remain an unpromoted stack component below target.

Continuation budget: at most ONE reversed D/A pair (20more measured requests),
if D improves either decode median by>=1% while the other decode, prompt and
client medians are no worse than1% versus A. This1% is ONLY a screening allowance
for confirmation, not permission for final degradation. If clearly worse, stop
this combination; if within noise with no>=1%gain, classify inconclusive and
keep data, no extra timing sweep. A confirmed stack can remain experimental
below90. Final promotion still requires90short/85~3K ordinary repeated medians,
no demonstrated prompt/read/quality/stability regression, frozen random coding
and complete cold/warm/cache/tool/vision/max-context matrix. Q007 still pending.



## E123 / R080-hc0-dma0

Same engine and loaded library hashes as R076-dma-off. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.2 (83.3-93.7) | 204.4 | 77.0436 | 77.0577 | 0.8458 | 893/1105 (80.81%) |
| longer | 85.1 (83.3-87.8) | 495.8 | 42.1234 | 42.1280 | 6.1662 | 1019/1337 (76.22%) |

Minimum available physical RAM 62,608,982,016 bytes; available commit 40,933,240,832 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C045 factorial A, HC0/DMA0: fresh same-day baseline88.2/85.1 decode. Component/stack decisions await all four planned arms.

Next: Evaluate B, D and C using the finite C045 plan; no isolated gate overrides the combined-stack test.


## E124 / R081-hc1-dma0

Same engine and loaded library hashes as R080-hc0-dma0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 86.5 (84.9-87.9) | 211.2 | 76.0918 | 76.1070 | 0.8332 | 839/1123 (74.71%) |
| longer | 85.7 (81.6-88.2) | 496.0 | 42.2565 | 42.2597 | 6.1587 | 1086/1404 (77.35%) |

Minimum available physical RAM 62,126,764,032 bytes; available commit 40,043,798,528 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C045 factorial B, HC1/DMA0:86.5/85.7 decode. Short lower, longer higher than A. Preserve as a component observation; proceed to combined D regardless of isolated short loss.

Next: Complete D=HC1/DMA1 and C=HC0/DMA1 before the stack decision.


## E125 / R082-hc1-dma1

Same engine and loaded library hashes as R080-hc0-dma0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.9 (85.8-90.4) | 208.5 | 77.2826 | 77.2968 | 0.8348 | 867/1112 (77.97%) |
| longer | 82.5 (80.3-86.4) | 496.8 | 41.5286 | 41.5317 | 6.1445 | 892/1204 (74.09%) |

Minimum available physical RAM 62,571,765,760 bytes; available commit 40,903,426,048 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C045 factorial D, HC1/DMA1:88.9/82.5 decode versus A88.2/85.1. Short+0.79%, longer-3.06%; prompt208.5/496.8 versus204.4/495.8. This combined configuration fails final no-degradation and the predeclared confirmation trigger. Do not infer additive gains.

Next: Complete batching-only C to retain the full interaction matrix; no reversed D/A pair under this result.


## E126 / R083-hc0-dma1

Same engine and loaded library hashes as R080-hc0-dma0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.2 (84.8-87.1) | 206.6 | 75.4300 | 75.4450 | 0.8511 | 803/1082 (74.21%) |
| longer | 82.7 (82.2-86.7) | 495.5 | 41.5731 | 41.5764 | 6.1680 | 937/1241 (75.50%) |

Minimum available physical RAM 62,572,130,304 bytes; available commit 40,924,909,568 bytes. Sampled GPU peak 25,123,819,520 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C045 factorial C, HC0/DMA1:85.2/82.7 decode versus A88.2/85.1. Full matrix completed; D recovers short speed versus C but not longer. Both16GiB floors and exact cleanup passed. Production unchanged; no reverse pair or matrix rerun.

Next: Record C045 interaction evidence and retain useful unpromoted components. Investigate an upstream-derived architecture that reduces transfer quantity rather than resubmitting the same copies.


## E127 / C045 completed combination assessment

All four arms completed: one excluded warmup plus five measured seeds per short/~3K workload, 40 measured requests total. All 36 cross-arm request-file comparisons are byte-identical. Engine/library hashes match; config differs only in HC-fast and batch-transfer flags. All 48 requests including warmups generated512tokens with zero prompt-cache tokens. E123-E126 preserve ranges, TTFT, stream/E2E, MTP, memory and cleanup.

| Arm | HC-fast | Batch transfers | Short server_decode_tps | ~3K server_decode_tps | Short/~3K prompt tok/s |
|---|---:|---:|---:|---:|---|
| R080 A | 0 | 0 | 88.2 | 85.1 | 204.4 / 495.8 |
| R081 B | 1 | 0 | 86.5 | 85.7 | 211.2 / 496.0 |
| R082 D | 1 | 1 | 88.9 | 82.5 | 208.5 / 496.8 |
| R083 C | 0 | 1 | 85.2 | 82.7 | 206.6 / 495.5 |

D versus A: short+0.79%, longer-3.06%; E2E77.2826/41.5286 versus77.0436/42.1234. The combined stack fails the finite confirmation trigger and final no-degradation contract. No reversed pair is run. Descriptive HC effects are B-A=-1.7/+0.6 tok/s with DMAoff versus D-C=+3.7/-0.2 with DMAon. These medians demonstrate interaction/noise, not an additive or causal estimate. No arm independently qualifies90/85 and full quality. Preserve HC-fast as an unpromoted component for a distinct justified combination. This specific DMA combination is closed. Production remains unchanged; all exact launcher trees stopped.

Next hypothesis: exclude rejected speculative rows from adaptive cache heat, reducing transfer quantity rather than copy submission overhead. Inspect and test a scoped single-GPU serial-serve derivation of PR1779; do not import its multi-GPU pipeline. Keep all numeric computation, model, sampling, MTP, context and cache precision unchanged. Any runtime placement rounding still needs quality validation.


## E128 / C046 prelaunch plan

# C046: committed-row cache heat and HC-fast

Hypothesis: current serial verify dispatch counts rejected draft rows in adaptive
expert heat. Keeping only committed input rows may improve cache placement and
reduce misses/transfers; HC-fast addresses independent GPU arithmetic. P013 proves
transfers occur, not that their whole interval is removable. Inspired by the
accepted-usage portion of upstreamPR1779 headf3727b2464321a35c4638491d75bcda1d4ecbb9c;
no multi-GPU pipeline code is imported. This is a new cache policy, not a repeat
of C045 copy-submission batching or prior adapt-every/lag sweeps.

Implementation: opt-in STRATA_ACCEPTED_USAGE=1 for single-GPU serial serve with
synchronous adaptive cache. Record routed expert indices per verify input row;
temporarily suppress eager usage accounting with RAII restoration; count rows
0..a before the existing adaptation point, matching ver.commit(a+1). Preserve
duplicate ID counts and invalid ID handling. Discard rejected rows. Final-window
counts follow committed input rows even if output cap/EOS prevents emitting all
outputs; no change to the existing commit/emission policy. Empty/default flag
keeps the original accounting. Unsupported batch/pipeline/async/peer/helper/
all-resident modes reject opt-in. Prompt path, model bytes, expert routing,
computation, KV, sampling, MTP depth/threshold, PCIe fraction and adapt schedule
remain unchanged. Placement may change CPU/GPU rounding; this is NOT an assertion
of identical generated text or automatic quality parity.

Correctness gate: first reproduce missing-helper test failure, then pass scalar
oracle checks over all accepted prefixes, invalid IDs, duplicate IDs, repeated
windows, exception restoration, and4096 random48-layer512-expert windows. Build
CUDA13.3/sm86 engine and run existing IQ AVX2 parity and topology tests. HIP/SYCL
toolchains unavailable; not built, no upstream review/merge request. Verify
active startup message and actual retained/routed counters in each enabled arm.

Finite served budget: four fresh arms A=usage0/HC0 R084, B=usage1/HC0 R085,
D=usage1/HC1 R086, C=usage0/HC1 R087, in A/B/D/C order. SAME newly built engine
for every arm; DMA0/deviceplan0. One excluded warmup plus five seeds101..105 per
short and ~3K cell,512tokens,cachemiss,concurrency1. Forty measured requests.
Fixed262144context,INT8KV/32768resident,CPU F16vision,thinking high->xhigh unlimited,
temperature1/top_p.95/top_k20/min_p0/presence0/repetition1, MTP4/.70, PCIe.20,
lag2,9workers30tasks. Identity per request; independent16GiB physical AND commit
floors; audit-no-process; no competing builds/profilers/GUI/Git during timings.
Exact cleanup and config restore after each arm. Assert byte-identical payloads.

Assess D against A, B/C retained as component/interactions. Maximum ONE reversed
D/A pair (20more measured requests) if either decode median improves>=1% and
neither other decode/prompt/E2E median falls>1%. This is a continuation screen,
not final permission for degradation. Otherwise stop this combination. No
component must individually reach90 or win every isolated metric. Retain useful
unpromoted components with evidence. Full promotion requires90/85 repeated
ordinary medians, fixed random coding with completed tested answer, and all
cold/warm/cache/tool/vision/maxcontext/quality/stability checks; Q007 is unresolved.
No peak/microbenchmark/short-only success qualifies. Retained production stays
unchanged until all requirements pass. No model resident at handoff.



## E129 / R084-usage0-hc0

Explicitly verified candidate engine SHA256 8057ab78c4129fc250ed668f5acd738a6b9cd2381b2d089467bd24f72f770ab2; loaded library hashes match R080-hc0-dma0. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.9 (82.2-88.9) | 203.5 | 76.6375 | 76.6595 | 0.8410 | 816/1097 (74.38%) |
| longer | 81.7 (79.9-82.8) | 496.6 | 41.3400 | 41.3444 | 6.1522 | 955/1328 (71.91%) |

Minimum available physical RAM 62,468,005,888 bytes; available commit 40,772,149,248 bytes. Sampled GPU peak 25,123,819,520 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C046 A new-binary control:87.9/81.7 decode; production unchanged. Full matrix pending.

Next: Run B usage-only, then D combined and C HC-only per finite C046 plan.


## E130 / R085-usage1-hc0

Same engine and loaded library hashes as R084-usage0-hc0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.5 (85.8-89.3) | 206.0 | 77.1226 | 77.1385 | 0.8402 | 904/1214 (74.46%) |
| longer | 82.8 (80.8-86.3) | 496.0 | 41.5491 | 41.5523 | 6.1624 | 990/1278 (77.46%) |

Minimum available physical RAM 62,477,889,536 bytes; available commit 40,765,911,040 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C046 B usage-only:87.5/82.8 decode versus87.9/81.7 control. Activation proved12requests:2950080 retained of3310560 routed entries. Short slightly lower, longer higher; component evidence only.

Next: Run D usage1/HC1 then C usage0/HC1; judge combined stack against A.


## E131 / R086-usage1-hc1

Same engine and loaded library hashes as R084-usage0-hc0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.6 (84.6-90.8) | 203.6 | 76.8049 | 76.8157 | 0.8630 | 899/1197 (75.10%) |
| longer | 82.7 (80.2-85.6) | 497.1 | 41.6162 | 41.6217 | 6.1357 | 928/1289 (71.99%) |

Minimum available physical RAM 62,532,505,600 bytes; available commit 40,852,852,736 bytes. Sampled GPU peak 25,123,819,520 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C046 D combined:87.6/82.7 decode versus87.9/81.7. Long+1.22%, short-0.34%, prompt203.6/497.1 and E2E76.8049/41.6162 do not regress. Finite reverse confirmation trigger passes; no promotion.

Next: Complete C HC-only, then the single permitted reversed D/A pair; pool all measured rows.


## E132 / R087-usage0-hc1

Same engine and loaded library hashes as R084-usage0-hc0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.4 (85.1-91.1) | 201.8 | 77.3560 | 77.3665 | 0.8457 | 919/1217 (75.51%) |
| longer | 84.2 (78.8-86.3) | 496.5 | 41.8582 | 41.8640 | 6.1560 | 942/1267 (74.35%) |

Minimum available physical RAM 62,578,327,552 bytes; available commit 40,881,319,936 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C046 C HC-only:88.4/84.2 decode; full initial factorial complete. D87.6/82.7 is slower than C but passes the predeclared D-versus-A confirmation screen. No additive gain or promotion claimed.

Next: Execute exactly one reversed D/A pair, R088/R089, then assess all10rows per cell; no additional sweep.


## E133 / R088-usage1-hc1-confirm

Same engine and loaded library hashes as R084-usage0-hc0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.3 (83.9-93.9) | 203.8 | 76.4968 | 76.5116 | 0.8541 | 965/1262 (76.47%) |
| longer | 84.1 (81.3-86.2) | 495.4 | 41.8563 | 41.8594 | 6.1681 | 981/1305 (75.17%) |

Minimum available physical RAM 62,522,593,280 bytes; available commit 40,876,900,352 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C046 D confirmation:87.3/84.1 decode. Full10short D runs median87.45 remains below90. Long confirmation stronger than initial82.7; final A repeat required for pooled assessment.

Next: Finish R089 A control; pool both five-run passes and close finite C046 matrix.


## E134 / R089-usage0-hc0-confirm

Same engine and loaded library hashes as R084-usage0-hc0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.4 (83.0-88.1) | 201.0 | 76.6129 | 76.6271 | 0.8495 | 891/1159 (76.88%) |
| longer | 81.0 (80.0-84.8) | 496.8 | 41.1770 | 41.1806 | 6.1374 | 917/1253 (73.18%) |

Minimum available physical RAM 62,528,049,152 bytes; available commit 40,896,790,528 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C046 A confirmation:87.4/81.0 decode. Finite six-arm matrix complete, all guards and exact cleanup passed. Assess pooled A/D ordinary medians and keep unpromoted component evidence.

Next: Publish C046 full matrix, activation, tests and code; inspect output-path variability before further controlled combinations.


## E135 / C046 full confirmation and retained experimental component

Sixty measured512-token requests across six fresh-process arms, plus twelve excluded warmups. Fixed numeric sampling and262144context. All60 cross-arm request-file comparisons are byte-identical; same engine8057ab78... and backend libraries, only accepted-usage and HC flags differ. All measured/warmup responses have512tokens and zero cache reuse. Each arm passed independent16GiB physical/commit guards and exact cleanup.

| Group | Measured runs per workload | Short / ~3K server_decode_tps | Short / ~3K prompt tok/s | Short / ~3K request_e2e_tps |
|---|---:|---|---|---|
| A control R084+R089 | 10 | 87.40 / 81.50 | 202.25 / 496.80 | 76.6252 / 41.2801 |
| D combined R086+R088 | 10 | 87.45 / 83.30 | 203.70 / 496.40 | 76.6509 / 41.7356 |
| B accepted-usage only R085 | 5 | 87.50 / 82.80 | 206.00 / 496.00 | 77.1226 / 41.5491 |
| C HC only R087 | 5 | 88.40 / 84.20 | 201.80 / 496.50 | 77.3560 / 41.8582 |

D versus A: short+0.057%, longer+2.209%; prompt+0.717%/-0.081%; request E2E+0.033%/+1.103%. Short TTFT0.85642s versus0.84527s; longer6.16156s versus6.14619s. This is a longer-input signal with unchanged short decode, small prompt/TTFT differences and incomplete quality; not a verified no-degradation winner. The HC-only five-run arm was faster than D, so additive/causal benefit is not established. No extra repetition is authorized by the exhausted finite plan. Both targets remain unmet.

Keep accepted-row accounting disabled by default as an experimental component with tests and reproducible source; production launcher/executable/config remain unchanged. Same model bytes, routing, computation, sampling and precision; cache placement can alter CPU/GPU rounding, so full quality remains required. The meaningful longer-input result is preserved for justified future combinations, not discarded solely for missing90. Do not blindly repeat this matrix.

Runtime activation: all12requests in each of R085/R086/R088 logged positive retained/routed counts with rejected rows excluded; full counts in summary.json. This proves accounting activation, not fewer copied bytes. Tests cover all prefix lengths, invalid/duplicate IDs, reset, exception restoration and4096 random48-layer512-expert windows. Post-matrix test strengthening explicitly covers T1..8 and is registered in CMake with assertions enabled in Release. Existing IQ AVX2 parity reports0failures; Windows affinity test passes. CUDA13.3sm86 built; HIP/SYCL not built and no upstream review/merge requested.

Follow-up P016 read-only reproducibility audit: R084/R089 have identical payloads/config/binary but all12output texts differ; common prefixes range57..506characters (warmup included), not a tokenizer-level divergence measurement. Positive seeds are forwarded in serve/server.py:959-961, parsed in generate.cpp, and Verifier::run draws Philox(seed,position). Source also feeds measured round times into DraftPolicy::observe, while CPU/GPU expert arithmetic can round differently (documented at the adaptation barrier). Those are plausible contributors, NOT proof of root cause. Do not change the sampling contract or blame a different nonce. Next bounded diagnostic should isolate the first differing routing/window/logit state using identical fresh-process requests, preserving production and all safety guards.


## E136 / P016 finite first-divergence diagnostic

Previous turn was progress: completed C046 six-arm combination and confirmation,
retained disabled experimental component and published08602c45. Current goal
remains90/85 with full quality/matrix unresolved. No model resident at entry.

Two fresh processes, P016-A and P016-B, same C0468057ab78... engine with both
accepted-usage and HC disabled (the exact repeated control that showed divergent
outputs). Each sends the saved R084 short warmup seed100 and short-run1 seed101,
byte-identical512-token streaming payloads, unchanged thinking coding parameters,
262144context, INT8KV/32768resident, CPU F16vision and9workers/30tasks. Sole
instrumentation: existing --dump-routing and STRATA_DUMP_FIRST_LOGITS. Output
paths differ per leg; no new engine code or sampling modification. Four requests
total, one warmup+one diagnostic per leg. NO throughput qualification from these
instrumented one-run cells. No further legs without new evidence and written plan.

Compare complete first-window logits (248320F32values/request), routed expert IDs,
window sizes inferred from per-layer trace records, and generated text prefixes.
Preserve truncated final routing record if abrupt server cleanup leaves one;
never mistake a truncated tail for an early divergence. Trace records have no
explicit request boundary; identify fresh T1/layer0 patterns cautiously, compare
chronological prefix without inventing positions. First divergence localization
does not establish its root cause. Existing source shows seed forwarding and
Philox(seed,position); timing-based draft policy plus placement/shape rounding are
hypotheses. No claim of altered seed or changed nonce. Independent16GiB physical
AND commit guards and exact cleanup/config restoration per leg. Raw binary
traces/logits stay private; publish hashes and parsed aggregate diagnostics only.


## E137 / P016 result and P017 causal control

P016 two fresh identical-config processes completed with exact cleanup. Both
requests have248320finite F32 first-window logits. Warmup: all248320values differ,
maxabs0.718124/meanabs0.101710. Run1: all248320differ,maxabs0.983901/meanabs0.157924.
Argmax1596matches in both cases. Output common prefixes57/44characters. Both
startup profiles/cache sizes match (8409experts,2315borrowed prefill slots).
Routing traces parse completely,54960/55200records; raw first divergence at record26,
layer6, a swapped ordering of the final2expert IDs. However the trace starts with
T4capture/warmup work and lacks explicit request boundaries: this record is NOT
assigned to an actual generated-token position. First-window logit divergence
is the reliable localization, before decode adaptation can be its sole cause.

Source evidence: prefill.cpp:2986-3040 updates CPU share/gate from measured GPU/CPU
layer timing; line3083 selects that share. CPU/GPU arithmetic differs by documented
implementation. This supports but does not yet prove a causal hypothesis.

P017 bounded control: two fresh legs A/B, two exact saved R084 requests each
(shortwarmup100/run1seed101),512tokens. Same8057ab78... binary/context/model/KV/
vision/sampling, accepted-usage0/HC0/DMA0. Add only STRATA_PREFILL_CPU_SHARE=0;
retain existing routing/first-logit instrumentation with leg-specific paths.
Four diagnostic requests total, no throughput qualification or production
promotion. Compare first-logit bit identity and text, alongside original P016.
If first logits still differ, CPU-share timing is not a sufficient explanation;
investigate earlier prompt state rather than more blind performance sweeps.
If logits stabilize, retain as localized evidence; do not infer all decode
reproducibility or quality. GPU-only prompt processing is NOT a candidate winner
without the unchanged no-prompt-rate-degradation and complete quality gates.
Independent16GiB physical/commit guards and exact cleanup/config restoration.
No third pair in this plan. Raw binaries private, summaries/hashes publishable.


## E138 / P017 localization and P018 share measurement

P017 two independent fresh-process runs with CPU prompt sharing disabled produced
bit-identical first-window logits for both saved requests (all248320F32values),
AND byte-identical entire512-token generated outputs (2391/2446characters).
P016 auto-sharing had all logits different and divergent texts. Together with
the timing-based share/gate code, this demonstrates the auto prompt placement as
a source of variation in this pair; not a claim of deterministic output for all
models/workloads. Startup model/cache/profile, seeds and numeric sampling match.
GPU-only prompt processing has diagnostic run1read81.0/81.1tok/s versus P016
206.9/204.7. It is rejected as a production optimization under no-read-degradation.

P018 is ONE new diagnostic process, original warmup100/run1seed101 only. Existing
STRATA_DBG_CPU_GATE output is extended with the existing chosen cpu_share and
measured CPU/GPU milliseconds per expert. Only that opt-in fprintf changes; no
arithmetic/selection code modified, no sampling/model/context changes. Build
CUDA13.3sm86 and verify debug format before launch. No HIP/SYCL build/review.
Use C046 combined stack (accepted usage1,HC1,DMA0) because the next candidate
will complement it. No routing/logit dump necessary; four earlier raw traces
already localize the issue. Independent16GiB physical/commit floors, no competing
model and exact cleanup/config restore. One warmup+one diagnostic request, no
speed qualification. Extract all share readings, exclude explicitly uncalibrated
initial values, choose ONE fixed fraction rounded to0.05 from the observed median
(clamp0.05..0.90), then benchmark it with CPU_SHARE_MAX1024 explicitly fixed so
the ~3K prompt path is not unintentionally changed by an explicit share flag.
No arbitrary multi-fraction sweep; further tests need results and a written plan.


## E139 / P018 measured share and C047 cumulative fixed-share plan

P018 completed and cleaned up.90calibrated readings, CPU share median0.7870875,
range0.759230..0.813005. Predeclared rounding selects exactly0.80. No fraction
sweep. Debug-only engine5d43a376...; all readings and source patch retained.
The diagnostic printf extension is removed from working source after capture;
C047 uses the previously tested8057ab78... engine, no debug/routing/logit hooks.

C047 immediate control is C046's EXACT combined stack: HC-fast1, accepted-row
accounting1,DMA0/deviceplan0, CUDA13.3,IQ3_S,262144context, INT8KV/32768resident,
CPU F16vision,MTP4/.70,PCIe.20,lag2,9workers30tasks. Only added performance factor
is fixed CPU prompt share0.80 versus auto (unset). BOTH arms explicitly set
STRATA_PREFILL_CPU_SHARE_MAX=1024 to keep the ~3K prompt path unchanged. Numeric
sampling remains thinking high/xhigh unlimited,1/.95/20/0/0/1,frequency0. This
preserves the user-prioritized complementary stack and isolates the new setting.

Budget: Aauto R090, Bfixed80 R091, Bfixed80 R092, Aauto R093. Each fresh process,
one excluded warmup+5measured seeds101..105 for BOTH original short/~3K tasks,
512tokens,cachemiss,concurrency1.40measured requests,8warmups maximum. No profiling,
builds,Git,GUI or process-memory polling during timing; audit-no-process and
independent16GiBphysical/commit floors. Exact cleanup and config restoration.
If B first pass has any prompt median worse>2% or decode/E2E worse>3%, stop this
candidate without confirmation (diagnostic-only stability does not waive loss).
Otherwise complete the single reversed B/A confirmation pair. No additional
pair/sweep. Pool all10qualifying rows per workload/cell with ordinary medians.

Compare exact payload and output hashes for B/B and A/A, MTP offered/accepted,
cache counters, prompt/decode/client/stream/TTFT and memory. Identical output is
reproducibility evidence, not a quality proof; fixed-share determinism is not
assumed from GPU-only P017. No90/85claim without frozen random coding and full
quality/cold-warm/tool/vision/maxcontext matrix. A smaller reproducible gain may
remain an unpromoted component. Final no-degradation contract is unchanged;
screening tolerances only decide whether to spend confirmation requests.


## E140 / R090-stack-auto

Same engine and loaded library hashes as R086-usage1-hc1. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.6 (83.9-91.2) | 205.9 | 78.8948 | 78.9101 | 0.8558 | 888/1162 (76.42%) |
| longer | 85.1 (84.2-87.1) | 495.6 | 42.1018 | 42.1075 | 6.1707 | 979/1295 (75.60%) |

Minimum available physical RAM 62,488,645,632 bytes; available commit 40,813,428,736 bytes. Sampled GPU peak 25,130,110,976 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C047 immediate auto-sharing control:90.6/85.1 decode over5runs/cell, prompt205.9/495.6. This isolated arm clears numeric thresholds but earlier identical-stack results are lower and full quality/matrix are unresolved; not goal qualification.

Next: Measure fixed80 sharing on identical HC-fast+accepted-row stack; apply finite stop/confirmation rule.


## E141 / R091-stack-share80

Same engine and loaded library hashes as R090-stack-auto. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.4 (85.2-93.0) | 219.7 | 77.9088 | 77.9204 | 0.8052 | 873/1122 (77.81%) |
| longer | 83.0 (80.9-86.5) | 496.0 | 41.5991 | 41.6050 | 6.1583 | 893/1218 (73.32%) |

Minimum available physical RAM 62,568,460,288 bytes; available commit 40,969,015,296 bytes. Sampled GPU peak 25,111,236,608 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C047 fixed80 first pass:88.4/83.0 decode versus90.6/85.1 auto. Prompt219.7/496.0 versus205.9/495.6; E2E77.9088/41.5991. Decode losses2.43%/2.47% remain within predeclared3% continuation bounds; do not promote.

Next: Complete exactly one reversed fixed80/auto pair R092/R093 and compare all12output files plus all10measured rows per cell.


## E142 / R092-stack-share80

Same engine and loaded library hashes as R090-stack-auto. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.9 (84.6-92.5) | 218.2 | 77.7094 | 77.7220 | 0.8144 | 873/1122 (77.81%) |
| longer | 84.2 (82.6-90.1) | 496.7 | 41.9516 | 41.9581 | 6.1593 | 1085/1415 (76.68%) |

Minimum available physical RAM 62,568,718,336 bytes; available commit 40,950,386,688 bytes. Sampled GPU peak 25,111,236,608 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C047 fixed80 repeat:87.9/84.2 decode, prompt218.2/496.7. Eight of12outputs exactly match R091: all6short, longer warmup/run1; longer run2 diverges and following outputs differ. Reproducibility improved but incomplete; no promotion.

Next: Complete final R093 automatic-sharing control, pool all10rows/cell, preserve hashes and acceptance.


## E143 / R093-stack-auto

Same engine and loaded library hashes as R090-stack-auto. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.2 (86.3-91.2) | 206.2 | 77.2246 | 77.2397 | 0.8543 | 1002/1282 (78.16%) |
| longer | 83.7 (83.1-84.5) | 496.7 | 41.8051 | 41.8095 | 6.1473 | 895/1233 (72.59%) |

Minimum available physical RAM 62,561,058,816 bytes; available commit 40,943,771,648 bytes. Sampled GPU peak 25,130,110,976 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C047 final auto control:88.2/83.7 decode. Full C047 pooled auto90.00/84.35 versus fixed80 88.15/83.95; fixed prompt improves but decode/E2E decline. Neither full goal nor final no-degradation passes.

Next: Close finite C047, preserve measured prompt/reproducibility component and all raw data; diagnose later divergence before any justified reopening of exact kernels.


## E144 / C047 complete comparison and reproducibility evidence

The finite four-arm ABBA comparison completed: 40 measured requests plus eight
excluded warmups. Every measured request generated 512 tokens with zero cached
prompt tokens. All 36 cross-arm payload-file comparisons are byte-identical.
Same engine 8057ab78..., libraries, model, vision, context and sampling. The sole
factor is fixed 80% CPU prompt share versus auto on the same HC-fast plus
committed-row-accounting stack; both have CPU_SHARE_MAX=1024.

| All 10 runs per workload | Auto short / ~3K | Fixed80 short / ~3K |
|---|---|---|
| server_decode_tps | 90.00 / 84.35 | 88.15 / 83.95 |
| Prompt tok/s | 206.05 / 495.95 | 218.55 / 496.40 |
| request_e2e_tps | 78.5048 / 41.9447 | 77.8091 / 41.8843 |
| stream_total_tps | 78.5225 / 41.9485 | 77.8212 / 41.8881 |
| TTFT seconds | 0.85517 / 6.16258 | 0.80599 / 6.15881 |

Fixed80 changes short/~3K decode by -2.06%/-0.47%, prompt by +6.07%/+0.091%,
and client E2E by -0.89%/-0.14%. It is not a no-degradation winner and is NOT
promoted. The faster prompt path and improved repeatability remain useful
experimental evidence for a distinct future combination. No extra fraction or
repeat is run. Auto's isolated R090 passed both numeric thresholds, but the
paired pooled ~3K median does not. Including the two earlier same-binary C046
HC1/accepted1 auto passes (R086/R088; implicit rather than explicit identical
1024-token sharing limit), all 20 runs per workload give 88.2 / 84.0 decode.
That broader history is not discarded to present a favorable 90 short result.
Full random-coding quality and real-use matrix remain unresolved; goal active.

Output reproducibility: auto 0/12 byte-identical output pairs; fixed80 8/12.
All six fixed short outputs and the longer warmup/run1 match, with identical
draft offered/accepted counts. Longer run2 first diverges; later outputs also
differ. Fixed80 removes the demonstrated prompt-placement variation in these
short requests, but is not full serving determinism or a correctness proof.
P016/P017 separately show first-token logits differing under auto versus fully
identical logits AND text in two fresh GPU-only prompt controls. GPU-only prompt
read around81 tok/s is rejected for production. P018's 90 measured calibrated
share readings selected80% by the predeclared rounding rule, not a sweep.

All four performance arms and five diagnostic processes passed independent
16 GiB available-physical AND commit guards and exact launcher/server/text/vision
cleanup. Per-process memory was not polled during generation. Production config
and executable hashes remain3457fdfe... /6048736d...; idle GPU457MiB. Diagnostic
prefill log extension was archived and removed, with no retained source change.
No benchmark model remains resident.

Next investigation: residual variation can propagate through timing-based
suffix-window selection into cache adaptation scheduled by window count. This
is a hypothesis, not a diagnosis from the final aggregate counts. Inspect the
first differing longer window before fixing anything. PR1779's accepted-token
cache barriers are a larger architectural alternative to the current accepted-
row heat alone; its published implementation waits at fixed token boundaries
and must be separately adapted/tested for single-GPU serial serving. Do not
reuse prior losing intervals or kernels without distinct new mechanism/evidence.


## E145 / P019 first differing longer-window diagnostic

Previous goal turn was progress: P016/P017 localized automatic prompt placement
as a variation source; P018 measured its actual share; C047 retained a6.07%short
prompt improvement as experimental but rejected promotion due decode/E2E loss.
Current goal still90/85 and full quality; no inference process at entry.

P019 replays the exact history through C047's first observed differing request:
shortwarmup+5measured payloads, longerwarmup+run1+run2,9requests per fresh process.
Two legs A/B,18diagnostic512-token requests maximum. Same8057ab78... binary,
fixed80 share/MAX1024,HC1/accepted1,DMA0/deviceplan0,262144context,CPU F16vision,
INT8KV/32768resident,MTP4/.70,PCIe.20,lag2,9workers30tasks. Numeric thinking coding
sampling unchanged. Only hooks: existing STRATA_TRACE request/window position/T
stderr lines and STRATA_DUMP_FIRST_LOGITS, no routing dump or source modification.
Capture every first-window logit file and full text; align trace windows by the
existing request marker. No speed qualification: tracing perturbs timing and
the later cell has only2nonwarmup requests. No third pair if divergence fails
to reproduce. Independent16GiB physical/commit guards, exact cleanup and config
restoration; no concurrent model/profiler/build. Raw logit binaries private.

Compare each request's first logits, sequence of(position,T), draft acceptance
and text. If logits match but window shapes first diverge, timing-driven draft
selection remains implicated; if first logits differ, prior cache/request state
must be examined. Neither alone proves cache scheduling is the sole cause.
The source adaptation schedule uses every4windows, while accepted-row heat alone
does not fix those boundaries. PR1779's accepted-token boundaries are a distinct
architectural candidate: fixed token positions, clipped windows, synchronous
publish after copies; not imported wholesale from its multi-GPU pipeline.
Do not change sampling, quantization or quality gates to obtain equal output.


## E146 / P019 window divergence reproduced; bounded diagnostic closed

Two fresh processes replayed the exact nine R091 requests in order, with
512 generated tokens each and zero cached prompt tokens. Same 8057ab78 engine,
backend library hashes, fixed CPU share .80/MAX1024, HC1, accepted usage1 and
unchanged sampling/context/model/vision; only the logit dump destination differs.
All eighteen requests completed. This is instrumentation evidence, not a
qualifying throughput comparison; neither tracing nor its timings is promoted.

The first three requests (short warmup, short runs1/2) have identical first
logits, full output, window sequences and offered/accepted draft counts. Each
first-logit snapshot contains248320 finite F32 values. Short run3 also starts
with bit-identical logits, but its window sequence first differs at zero-based
index347: absolute position644 has T4 in A and T2 in B. A has374 windows and
198/138 offered/accepted drafts; B has373 windows and197/139. Full output differs.
Thus the first observed divergence occurs earlier than C047's longer run2.
This supersedes any interpretation that fixed80 guarantees short reproducibility;
C047's six matching short pairs remain valid observations for those runs only.

The subsequent short run4 already has different first logits (maximum absolute
difference1.12157655); short run5 .97195768; longer warmup .78262842; longer run1
.80348349; longer run2 .82470608. Every subsequent full output differs. Across
all nine requests, first logits match4/9, full outputs and windows match3/9.
Exact raw hashes and per-request first differing window positions are in
summary.json; complete request-aligned position/T sequences in window-traces.json.
Raw binary logits stay private. Every request payload matches R091 byte-for-byte.

Interpretation: equal initial logits do not guarantee equal subsequent decoding.
The observed T4/T2 split is consistent with the existing timing-dependent draft
policy, and later-request initial differences are consistent with carried cache
state. We have not captured every intermediate logit/token or residency map, so
this does not prove the window policy caused the first text difference, nor
that cache adaptation is the sole source. Tracing itself can perturb timing.
The finite two-process budget is closed; no third repeat is needed.

Next architectural hypothesis: adaptation every four variable-length windows
can create different cache publication positions. A separately designed
accepted-token-boundary scheduler could hold placement stable within fixed token
blocks, clip speculative windows to boundaries, and fence cache publication.
PR1779 is a reference, but its multi-GPU implementation cannot be imported
unchanged into this single-GPU serial path. Before implementation, establish a
finite test plan, preserve .20 PCIe/sampling/quality, prove copy ordering and
default-off behavior, and measure its synchronization cost. No such code or
production setting was changed by P019. This is a candidate, not a verified fix.

Memory safety: minimum available physical/commit bytes A62252527616/40998223872,
B62169985024/40726831104, both above the independent16GiB floors. Exact supervisor
cleanup verified no remaining Strata launcher/server/engine/vision processes.
Production config restored to SHA2563457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0;
GPU memory returned to457MiB. No benchmark model remains resident.

The90/85 server_decode_tps goal and full quality/workload matrix remain active
and unqualified. C047 remains unpromoted: its automatic-share pooled short/3K
decode90.00/84.35 versus fixed80 88.15/83.95. End-to-end metrics remain separate
and include prompt processing plus generation and API completion overhead.


## E147 / C048 fixed accepted-token cache boundaries

Previous turn progress: P019 localized a window-shape divergence after identical
first logits and found later requests already differ at first logits. Upstream
main rechecked unchanged fb58e0db, latest v0.1.41. No inference process resident.

Test the PR1779 token-barrier mechanism as a scoped single-GPU serial derivative,
using C046 accepted-row accounting. Default remains off. Require accepted-usage1,
active synchronous cache, one GPU, no helper/peer/pipeline/batch. Preserve PCIe.20:
its transient expert staging is complete when the verifier stream is synchronized,
and cache refill runs only after verifier commit and MTP streams finish. Publish
residency only after the refill stream finishes; report any CUDA wait failure.
Clip the base and chained window to the remaining accepted-input-token interval.
Keep heat/decay/selection rules, numeric kernels, sampling, quant/context unchanged.
Changes are in the existing serial flow, not an imported multi-GPU pipeline.

One interval only:64 from the reference mechanism; no interval sweep. A standalone
boundary oracle exercises random accepted-prefix lengths, nonzero prompt offsets,
base/tail clipping, interval1 and disabled identity. Red compile then green test;
CUDA13.3 sm86 build plus existing accepted usage, affinity and IQ parity tests.
HIP/SYCL unavailable locally; no upstream PR or cross-backend claim.

Finite initial serving comparison: R094 barrier0 then R095 barrier64, same new
binary, fixed80/MAX1024, HC1/accepted1,DMA0/deviceplan0, existing9workers30tasks,
MTP4/.70,INT8KV/32768resident,262144context,CPU F16vision. Exact original TTLCache
short/~3K payloads, one warmup+five measured seeds per cell,512tokens,one request.
16GiB independent physical/commit floors, audit-no-process observer, exact cleanup.
No builds/Git/profiler/GUI/process-memory polls during requests. No trace hooks.
All rows retained; server decode, prompt, E2E, stream total and TTFT separate.

If either decode/E2E cell loses >3% or prompt loses >2%, stop and archive/revert
this candidate. Otherwise one reversed B/A confirmation pair maximum (R096/97).
These screening tolerances allocate experiments, not permission to promote loss.
No production promotion absent all-run medians, frozen coding quality and full
real-use matrix. Diagnostic reproducibility can motivate further investigation
but cannot count as speed qualification. No model left resident at checkpoints.


## E148 / R094-barrier0

Explicitly verified candidate engine SHA256 c9508334047d378f2e4f5a7dd128e90064023effb2d12bf884d96520379855b4; loaded library hashes match R091-stack-share80. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.7 (85.4-93.1) | 217.7 | 78.2182 | 78.2301 | 0.8013 | 873/1122 (77.81%) |
| longer | 84.4 (82.9-85.7) | 496.2 | 41.9663 | 41.9713 | 6.1638 | 1045/1394 (74.96%) |

Minimum available physical RAM 62,577,848,320 bytes; available commit 40,870,330,368 bytes. Sampled GPU peak 25,111,236,608 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C048 same-day feature-off control: short88.7 and longer84.4 server decode. New binary, fixed80 prompt sharing, HC1 and accepted usage1; no goal or full-quality qualification.

Next: Evaluate R095 barrier64 under the predeclared stop rule.


## E149 / R095-barrier64

Same engine and loaded library hashes as R094-barrier0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 85.2 (79.9-90.2) | 226.7 | 75.6242 | 75.6342 | 0.7736 | 812/1084 (74.91%) |
| longer | 89.6 (83.4-90.0) | 497.7 | 43.2796 | 43.2843 | 6.1346 | 1064/1410 (75.46%) |

Minimum available physical RAM 62,509,596,672 bytes; available commit 40,775,720,960 bytes. Sampled GPU peak 25,111,236,608 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C048 fails the predeclared no-confirmation screen: short85.2 versus88.7 decode (-3.95%), E2E75.6242 versus78.2182 (-3.32%). Longer89.6 versus84.4 decode (+6.16%), E2E43.2796 versus41.9663 (+3.13%). All12 requests show seven cache barriers. Mixed workload response; not promoted and no reverse pair.

Next: Archive and revert C048; use the longer-input gain to form a distinct path-specific hypothesis before another experiment.


## E150 / C048 rejected globally; longer-input mechanism retained as a hypothesis

Previous goal turn was progress: P019 localized a window divergence. This turn
built and measured the distinct accepted-token boundary architecture. Upstream
main remains fb58e0dbc8399662c0e47c76578c6e878b14f6cf, release v0.1.41.
Reference: https://github.com/Niko1221/Strata/pull/1779 at
f3727b2464321a35c4638491d75bcda1d4ecbb9c. Only the single-GPU serial token-boundary
mechanism was implemented; no multi-GPU pipeline or sampling change was imported.

Candidate SHA256 c9508334047d378f2e4f5a7dd128e90064023effb2d12bf884d96520379855b4,
CUDA13.3 sm86, source dd0555b5 plus archived patch and two new source files.
Default-off STRATA_SERIAL_ADAPT_TOKENS; enabled value64 requires C046 accepted
usage and its restricted synchronous single-GPU serving route. Base and chained
windows clip to the boundary. The verifier commit/stream and MTP stream finish
before adaptation; the refill stream finishes before publishing cache residency.
PCIe fraction stays .20. New scheduling and placement may change numerical
rounding/output, so unchanged numeric kernels are not a full quality proof.

Validation: missing-header red compilation, then1.2M randomized accepted-prefix
steps passed across intervals1/2/3/7/64/257, disabled identity and clipping/error
cases. Registered CMake test, accepted usage oracle, Windows worker/host affinity,
IQ AVX2 parity all passed; CUDA engine built. Eight unsupported/malformed configs
rejected before loading. HIP/SYCL not built; no upstream review requested.

Both served arms used the same binary/libraries and12 byte-identical requests.
One warmup+five measured seeds per short/~3K cell, all512tokens/cachemiss, fixed80
CPU prompt share/MAX1024, HC1/accepted1,DMA0/deviceplan0. Numeric thinking coding
sampling1/.95/20/0/0/1 remained fixed,262144context,INT8KV/32768resident,CPU F16vision.

| Metric | Control short / ~3K | Barrier64 short / ~3K |
|---|---:|---:|
| server_decode_tps | 88.7 / 84.4 | 85.2 / 89.6 |
| prompt_tps | 217.7 / 496.2 | 226.7 / 497.7 |
| request_e2e_tps | 78.2182 / 41.9663 | 75.6242 / 43.2796 |
| stream_total_tps | 78.2301 / 41.9713 | 75.6342 / 43.2843 |
| TTFT seconds | .80133 / 6.16382 | .77358 / 6.13455 |

Raw decode, seeds101..105:
- R094 short90.2,88.7,85.4,93.1,87.4; longer82.9,84.4,85.7,85.4,83.1.
- R095 short79.9,82.1,85.2,87.6,90.2; longer85.4,89.6,83.4,89.8,90.0.

Short decode -3.946% and E2E -3.316% cross the written loss-stop rule. Therefore
no R096/R097 confirmation pair, no promotion. Longer decode +6.161% and E2E
+3.129% are promising single-pass observations, not confirmed wins or goal proof.
Do not discard the short regression or reinterpret the overall candidate as a win.
All12 enabled requests executed seven barriers; total barrier time median
214.314ms/request, range212.924..216.111ms.
Counts prove activation. Time includes selection, stream fences, copies and
publication; it is not an isolated copy benchmark or removable-time estimate.
Measured draft acceptance short873/1122 control versus812/1084 candidate;
longer1045/1394 versus1064/1410. Text/acceptance can change throughput.

All24 requests passed independent16GiB physical/commit guards and exact process
cleanup. Lowest available physical/commit62509596672/40775720960 bytes. GPU peak
25111236608bytes sampled, no process-memory polling during requests. Final GPU
457MiB, production config hash3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0.
Production launcher/binary unchanged. Source is restored after archiving the
candidate patch/tests/build evidence; build tree and saved candidate binary still
contain C048, so do not mistake them for a rebuilt retained control.

Next distinct hypothesis: the short-path regression may reflect insufficient
cache adaptation early in request history, whereas longer prompts prepare a more
useful cache. The candidate short sequence rises79.9 to90.2, but seeds differ,
so this trend alone does not prove warm-cache causality. The natural existing
prompt-placement boundary is1024tokens (short CPU/GPU sharing versus longer
GPU prefill). A separately planned long-path-only barrier experiment could keep
the original short policy and test the larger-input benefit without assuming
the policies compose: earlier short requests change later cache state. Keep
the interval64 and sampling fixed, compare against the same stack, and include
boundary-neighbor/random-coding checks before any promotion. This is C049's
potential mechanism, not permission to bypass C048's stop or cherry-pick rows.

Goal90/85 and full quality/cold-warm/workload qualification remain active and
unmet. Q007's two incomplete natural-stop coding answers remain unresolved.


## E151 / C049 longer-prefill-only cache barriers

Previous goal turn was progress: C048 global barriers rejected for short decode
-3.95%, while ~3K decode improved6.16%. Candidate source was archived and restored.
C049 is a distinct policy-composition experiment, not a rerun of that failed arm.
Reuse its tested64-token boundary mechanism only after a request freshly reads
at least1025 prompt tokens. Prefill consumes all but the final prompt token, and
the existing CPU-sharing limit is chunks below1024. Thus this threshold follows
the existing prompt-path boundary, not the specific3034-token fixture. Cached
long contexts with short fresh suffixes retain window-based adaptation. Rejected
draft rows still do not count; synchronization and64-token interval stay fixed.

Default off. Gate tests cover fresh1/1024/1025/262144, configured interval0,
minimum0 and cached-suffix semantics. Preserve CUDA/math/model/quant/sampling,
262144context,INT8KV/32768resident,CPU F16vision,MTP4/.70,PCIe.20,lag2,HC1 and
acceptedusage1,DMA0/deviceplan0,9workers30tasks. Both arms use auto prompt share
with explicitMAX1024: fixed80 was not a promoted performance win. This differs
from C048 in both arms; only the barrier option differs within this new pair.

Bounded comparison A R098 control0, B R099 conditional64; each fresh process,
one warmup+five measured seeds101..105 per original short/~3K cell,512tokens,
streaming/cachemiss/concurrency1. Byte-identical payloads; no arithmetic or
sampling change. If any decode/E2E median loses>3% or prompt median loses>2%,
close without confirmation. Otherwise one reverse B R100/A R101 pair maximum;
pool all10rows/cell ordinary medians. No threshold or interval sweep. Since short
requests run before long ones, repeated short results also test the new binary's
inactive branch; mixed history in the reverse workload order remains a later
gate, not an implied guarantee. R096/97 remain unused closed-C048 reservations.

16GiB physical/commit floors, no per-process polling during requests, no builds/
Git/GUI/profiler concurrently. Exact process-tree cleanup/config restore eacharm.
Require runtime log proof short interval0 and long interval64, seven updates per
512-token longer request. If retained, test boundary-neighbor workloads, cache
hits, fresh cold and random coding before promotion. Full quality/workload gates
unchanged;512-token throughput screens do not prove compilable answer quality.


## E152 / R098-conditional0

Explicitly verified candidate engine SHA256 ac43e89822e4febce9a2e3ae93a786eaa705bdc61f04ba28302ee50c64bb87c3; loaded library hashes match R090-stack-auto. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.0 (86.3-91.8) | 206.8 | 78.4740 | 78.4961 | 0.8248 | 824/1102 (74.77%) |
| longer | 83.8 (82.1-87.8) | 497.3 | 41.9150 | 41.9207 | 6.1381 | 955/1313 (72.73%) |

Minimum available physical RAM 62,593,171,456 bytes; available commit 40,871,514,112 bytes. Sampled GPU peak 25,130,110,976 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C049 same-day automatic-share control: short90.0 and longer83.8 server decode; E2E78.4740/41.9150. New conditional-policy binary with feature0. Not full goal or quality qualification.

Next: Compare R099 and apply written confirmation rule.


## E153 / R099-conditional64

Same engine and loaded library hashes as R098-conditional0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.5 (88.0-90.0) | 210.3 | 77.4039 | 77.4145 | 0.8336 | 849/1156 (73.44%) |
| longer | 87.8 (81.0-93.6) | 497.1 | 42.8233 | 42.8265 | 6.1423 | 1113/1391 (80.01%) |

Minimum available physical RAM 62,521,552,896 bytes; available commit 40,808,697,856 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C049 first candidate pass: short88.5 (-1.67%) and longer87.8 (+4.77%) decode; E2E77.4039 (-1.36%) /42.8233 (+2.17%). Gate proven inactive on all6 short requests and active with7 updates on all6 longer requests. First longer measured request includes a five-token graph capture; retained without exclusion. Screening permits the one reversed pair; no confirmed win or promotion.

Next: R100 candidate then R101 control, same request order; pool all10 seeds per cell afterward.


## E154 / R100-conditional64

Same engine and loaded library hashes as R098-conditional0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.1 (85.7-92.1) | 211.7 | 78.6941 | 78.7053 | 0.8330 | 890/1150 (77.39%) |
| longer | 84.2 (82.8-86.4) | 497.6 | 41.9768 | 41.9800 | 6.1387 | 871/1212 (71.86%) |

Minimum available physical RAM 62,548,140,032 bytes; available commit 40,841,080,832 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C049 confirmation candidate90.1/84.2 decode, E2E78.6941/41.9768. The larger first-pass longer gain did not repeat; every seed remains included. Gate and cleanup passed; no promotion.

Next: Pool with final R101 control and R098/R099; no extra confirmation pair.


## E155 / R101-conditional0

Same engine and loaded library hashes as R098-conditional0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.8 (87.6-91.7) | 199.4 | 78.0203 | 78.0359 | 0.8650 | 928/1229 (75.51%) |
| longer | 82.7 (79.0-84.2) | 496.7 | 41.5619 | 41.5650 | 6.1480 | 915/1245 (73.49%) |

Minimum available physical RAM 62,592,548,864 bytes; available commit 40,893,767,680 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C049 final same-binary control completed. Complete10-row pooled medians: control89.4/82.9 versus conditional89.1/85.0 server decode; E2E78.2471/41.6374 versus78.0490/42.1705. Longer gain2.53%, short loss0.34%; no no-degradation or goal qualification. Finite four-arm comparison closed.

Next: Record full comparison and retain default-off experimental component; profile remaining short-input cost before selecting another change.


## E156 / C049 complete four-arm comparison; experimental component only

Same-binary ABBA R098/R099/R100/R101 completed,10 measured rows per workload/cell
(40 measured+8 warmups total). All512tokens, cachemiss, exact payload equality,
fixed thinking coding sampling1/.95/20/0/0/1,frequency0. Context262144, INT8KV with
32768 resident, CPU F16vision, MTP4/.70,PCIe.20,9workers30tasks,HC1/acceptedusage1,
auto prompt sharing/MAX1024,DMA0/deviceplan0. No slow seed or graph capture removed.

| All-run ordinary median | Control | Conditional64 | Change |
|---|---:|---:|---:|
| Short server_decode_tps |89.4|89.1|-0.336%|
| ~3K server_decode_tps |82.9|85.0|+2.533%|
| Short prompt_tps |206.35|211.00|+2.253%|
| ~3K prompt_tps |497.05|497.25|+0.040%|
| Short request_e2e_tps |78.24714|78.04901|-0.253%|
| ~3K request_e2e_tps |41.63743|42.17055|+1.280%|
| Short stream_total_tps |78.26603|78.05986|-0.263%|
| ~3K stream_total_tps |41.64120|42.17379|+1.279%|
| Short TTFT seconds |.852411|.833291|-2.243%|
| ~3K TTFT seconds |6.140930|6.141785|+0.014%|

Individual pass decode short/~3K: A90.0/83.8, B88.5/87.8, B90.1/84.2,
A88.8/82.7. Every individual result and raw seed order is retained in E152-E155
and summary.json. The larger first-pass longer gain did not repeat at the same
size. R099 longer run1 includes a captured5-token graph; retained. Its longer
draft acceptance80.01% versus R09872.73% also shows that output/draft behavior
contributes to served speed. No isolated kernel-speed claim follows.

The candidate's longer median reaches85.0 in this screen, but short89.1 misses90,
and short decode/E2E point estimates are below control. Therefore no no-degradation
qualification, no production promotion, no target completion. The complete finite
comparison is closed; no extra repeats to seek a favorable median. Retain the
default-off code as an experimental component for future justified combinations.
It is not a verified overall winner. Same-day control is essential: earlier
same-stack historical controls were sometimes faster; do not pool different
binary histories or present the2.533% as a universal gain.

Runtime proof: all12 enabled-arm short requests logged interval0; all12 longer
requests logged interval64 and seven completed barriers each. Policy uses fresh
prompt tokens n-resume, so long cached conversations with short suffixes retain
ordinary window adaptation. Threshold1025 is anchored to1024 prefill tokens plus
the last prompt token consumed in decode. This request-level rule is a proxy:
checkpoint splits can still make smaller prefill chunks. Boundary-neighbor,
cache-hit and reversed workload-history validation remain required.

Barrier time median214.684ms across12 longer requests,
range210.816..216.275; includes selection/copies/fences/publication,
not removable latency. Full-output byte matches across passes: control
0/12, conditional0/12.
No determinism or answer-quality claim follows from the scheduling policy.

Implementation/build: SHA256ac43e89822e4febce9a2e3ae93a786eaa705bdc61f04ba28302ee50c64bb87c3,
source cacdcd35 plus C049-integration.patch/new header+test. CUDA13.3 sm86 passed;
the registered boundary test,1.2M accepted-prefix oracle steps, accepted-usage
oracle, Windows affinity and IQ AVX2 parity passed. New fresh-count boundary tests
failed before implementation, then passed. Five malformed minimum settings were
rejected before load. Prior C048 routing/config restrictions remain. HIP/SYCL not
built; no upstream review requested. Default-off helper leaves base/tail windows
unchanged in tests; actual default-output byte equivalence is not established
under the preexisting automatic-placement nondeterminism. Full quality is pending.

Use only for further controlled experiments: STRATA_ACCEPTED_USAGE=1,
STRATA_SERIAL_ADAPT_TOKENS=64, STRATA_SERIAL_ADAPT_MIN_PROMPT=1025. Unset/0 token
interval keeps ordinary window-based adaptation. A minimum0 enables the rejected
global policy from C048; it is not recommended. Requires one-GPU serial serving
and active synchronous cache; unsupported helper/peer/batch/pipeline routes fail.
Production config and launcher keep these experimental options off.

All four supervisors passed16GiB physical/commit floors and exact launcher/server/
engine/vision cleanup. Minimum available physical/commit62521552896/40808697856
bytes; maximum sampled GPU25130110976bytes. No process-memory polling during
requests. Production config restored3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0;
idleGPU457MiB. No benchmark model resident. Windows powercfg read-only check shows
High performance scheme8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c already active; no
power-setting mutation or prospective gain claimed.

Next: refresh short-decode profiling on the cumulative native stack before
selecting another kernel/configuration change. Prior P009/P013 traces predate HC1,
accepted usage and this experiment. Reuse profile-goal90-new.ps1 / profile-one-
request-new.py only after inspecting their identity/config/cleanup guards; trace
one warmup plus one measured diagnostic request, never count it as qualifying TPS.
Use dependency/overlap evidence, not summed overlapping durations as saved time.
Full frozen random-coding, cold/warm/cache-hit/vision/tools/reasoning/cancel/max-
context matrix remains required. Q007 two incomplete coding answers unresolved.
Goal remains active and unqualified; no safe experiment is currently blocked.


## E157 / P020 refreshed cumulative-stack short-request profile

Previous goal turn was progress: C049 four-arm comparison finished, source and
ledger pushed d1a15b1c. Candidate89.1/85.0 versus89.4/82.9 control; no promotion.
Refresh profiler evidence before another change. Existing P009/P013 predate HC1
and accepted-usage accounting. Do not infer the remaining bottleneck from them.

One fresh process, exact R099 short warmup(seed100) and short-run1(seed101)
payloads,512tokens each, streaming/cachemiss, frozen thinking coding profile,
IQ3_S/262144/INT8KV/CPU F16vision. Current engineac43e898,HC1/accepted1,auto prompt
share/MAX1024,conditional64/minfresh1025 (inactive for this165-token request),
DMA0/deviceplan0,MTP4/.70,PCIe.20,9workers30tasks. Only host decode timers added.
Nsight Systems2026.5.1 graph-node software trace, CUDA events disabled,1s flush,
CPU sampling/context-switch tracing disabled. Start after warmup, stop after the
entire measured request. Capture includes prompt processing; never label total
GPU sums as decode-only. No GPU phase stamps or source changes.

Finite budget one capture. Independent16GiB physical/commit guard eachsecond,
preflight process inventory, identity-checked requests, exact profile-session and
launcher/model/vision cleanup and production config restore in finally. No other
model/build/profiler/GUI or process-memory polling during generation. Raw nsys-rep
and SQLite stay private; export only selected stats and diagnostics. Audit record
consistency before conclusions; absence of records is not proof of GPU idle.
Overlapping kernel/copy sums and interval unions are not a dependency critical
path or removable latency. Instrumented TPS is diagnostic, never qualification.


## E158 / P020 findings and E159 / C050 IQ4_NL down compiler probe

P020 completed one warmup and one profiled512-token exact R099 short request.
Software graph-node tracing slowed served decode to72.9 and E2E64.7341tok/s;
diagnostic only, never a qualifying performance value. Capture includes827ms
prompt processing plus7018.8ms decode. Host decode timers:311windows,22.57ms per
window, verify20.79 (GPU-reach wait10.44, host6.02: plan.08, activationquant.10,
jobs.01, CPUexpertwork5.81), commit/emit.18, draft1.24. These instrumented timers
identify CPU expert work as a larger host target than planning, not a guaranteed
critical-path saving or precise uninstrumented fraction.

Trace audit:720399kernel records,991 graph launch API/activity matches,12543direct
launches/activity matches; zero invalid intervals, nonzero launch returns or
unmatched launches. Cohort node sets stable. Nsight still warns not all CUDA
events may be collected; producer/collector counts differ by category and are not
a dropped-kernel count. Internal reconciliation does not prove completeness.
Whole-request recorded activity span7848.909ms, any6768.548, no recorded1080.362.
Only-category-active:Q6MMVQ855.068ms, memcpy762.882ms, waitflag647.689ms. These
overlap categories are not dependency critical paths, removable time or proof
of idle hardware. Raw SQLite/nsys metadata remains private. Exact cleanup passed,
GPU457MiB and config3457fdfe... restored. Capture budget closed.

C050 is a NEW compiler target: IQ4_NL down projection(type20), not C042's IQ3_S
gate/up retry. C040/C041/C042 deliberately kept down projections on MSVC. Compile
the identical current iq_avx2.cpp as separately renamed MSVC and Clang19.1.5
images, AVX2 only, precise math, Clang FP contraction off; explicit FMA intrinsics
unchanged. Only the test pool's type20 down dispatch differs; GU, quantization and
all other formats remain identical. No production source/runtime edits yet.

Proof gate: all576 actual-weight full-pool outputs across48layers,experts0/173/511,
T1/2/4/8 must match bitwise and be finite. Then one finite timing probe: eligible
type20 layers0/5/10/15/20/25/30/35/40/45/47,64 actual experts/layer with prior fixed
(29+17*i)%512 selection (beyond L3),T1/2/4/8,jobs1/3/6,9workers+host0,30tasks,
one warmup and five alternating paired100-call rounds per cell. All cells retained.
Require at least5% geometric-mean whole-pool time gain and no cell over3% slower
before any engine integration. Otherwise close this compiler path without served
runs. This is an offline primitive probe, not TPS or full answer-quality proof.
Independent16GiB physical/commit guards, no model server or concurrent build during
timing. Sampling/model/context contract is untouched; no weight files exported.


## E160 / C050 down-only compiler gate rejected; P020 evidence published

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
0.992158989 (0.7841% lower time). Worst ratio1.180074938 (18.0075% slower);
18/96cells slower,3/96over3% slower. The required>=5% aggregate time reduction
AND no cell>3% slower both fail. Reject and close this compiler path; no cherry-
picked subset, extra confirmation, engine integration, server run or promotion.
This does not imply a0.78% served throughput improvement.

Independent global memory guard passed every second. Minimum available physical
119752142848bytes and commit124670394368bytes,
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


## E161 / C051 split-window compatibility defect found and guarded

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
Candidate engine SHA256 0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd; kept separately at
engine/strata-cuda133-usage-guard.exe. Existing production executable unchanged.
No throughput claim for this configuration guard.


## E162 / C052 finite split-window scheduling screen prepared, not run

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


## E163 / R102-split0

Explicitly verified candidate engine SHA256 0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd; loaded library hashes match R037-observer-no-process. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.5 (85.5-96.7) | 212.2 | 78.6265 | 78.6376 | 0.8185 | 951/1256 (75.72%) |
| longer | 84.5 (81.8-86.4) | 494.7 | 41.9826 | 41.9868 | 6.1831 | 960/1305 (73.56%) |

Minimum available physical RAM 62,485,311,488 bytes; available commit 41,676,505,088 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C052 same-day unsplit control completed: short90.5 and longer84.5 decode. This is a screen, not target qualification. HC1, acceptedusage0, barrier0; only split scheduling differs in upcoming candidate.

Next: Run R103 split scheduling with identical remaining settings, then apply the E162 stop rule.


## E164 / R103-split1

Same engine and loaded library hashes as R102-split0. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 79.0 (78.3-81.0) | 204.9 | 69.8017 | 69.8164 | 0.8619 | 850/1111 (76.51%) |
| longer | 78.3 (76.3-78.7) | 494.9 | 40.3146 | 40.3191 | 6.1667 | 948/1260 (75.24%) |

Minimum available physical RAM 62,413,287,424 bytes; available commit 41,514,856,448 bytes. Sampled GPU peak 25,199,316,992 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C052 rejected: split scheduling short79.0/longer78.3 versus90.5/84.5 control; decode and E2E regression gates fail, short prompt also falls3.44%. No R104/R105 confirmation. Complete predeclared workload set retained.

Next: Close C052 and inspect request-conditional accepted-usage composition using the existing fresh1025 boundary; production unchanged.


## E165 / C052 complete, split-window scheduling rejected

Previous goal turn was progress: C050 closed, C051 guard fixed and pushed49db7853.
This turn completed same-binary C052 A/B with one warmup and five measured runs
per short/~3K workload, exact twelve request payloads byte-identical. Every
request512tokens/cachemiss; C051 engine0dea69dc, HC1, acceptedusage0, barrier0,
fixed model/context/vision/sampling. Sole arm change: --no-spec-split/--spec-split.

| Ordinary five-run median | Unsplit | Split | Change |
|---|---:|---:|---:|
| Short server_decode_tps |90.5|79.0|-12.707%|
| ~3K server_decode_tps |84.5|78.3|-7.337%|
| Short prompt_tps |212.2|204.9|-3.440%|
| ~3K prompt_tps |494.7|494.9|+0.040%|
| Short request_e2e_tps |78.62648|69.80172|-11.224%|
| ~3K request_e2e_tps |41.98263|40.31463|-3.973%|
| Short stream_total_tps |78.63763|69.81643|-11.218%|
| ~3K stream_total_tps |41.98680|40.31906|-3.972%|
| Short TTFT seconds |.818503|.861862|+5.297%|
| ~3K TTFT seconds |6.183140|6.166672|-0.266%|

Control short91.3,87.5,90.5,85.5,96.7; longer83.3,84.5,81.8,86.4,85.8.
Split short79.0,81.0,78.6,79.2,78.3; longer78.3,76.4,76.3,78.4,78.7.
No slower seed or first graph capture removed. Short failure was noticed after
the longer set had begun; completed that already-planned set for evidence and
ran no extra confirmation. R104/R105 reservations unused. Reject; no promotion.
The control90.5 short is not full90/85 qualification (long84.5, quality pending).

Actual codepath evidence: live identity records exact split flags, engine hash,
and captured multiple-token windows. generate.cpp passes spec_split to set_split;
record_window chooses two groups when split_ and T>=2. Source is same in both.
No timing-instrumentation flags. Full output quality remains unqualified; these
truncated throughput samples do not establish compilable coding answers.

Independent16GiB floor passed: minimum physical62413287424 and
commit41514856448bytes. All exact launcher/server/engine/vision trees
stopped; config3457fdfe restored, idleGPU457MiB. No process-memory polling during
requests. Production unchanged. The scheduling path is closed without a split
geometry sweep or speculative-accounting combination.


## E166 / C053 request-conditional cache-accounting composition

Distinct combination hypothesis: C049 enabled accepted-row accounting even on
short requests where its token barrier was inactive. Its paired short89.1 versus
89.4 control did not qualify; C052's HC-only control90.5/84.5 shows useful short
performance without accepted-row accounting, but is NOT a same-day causal proof
against C049. Test that distinction on one binary, not pooled historical arms.

Add default-off STRATA_ACCEPTED_USAGE_BARRIER_ONLY=1. Requires acceptedusage1 and
configured positive barrier interval; malformed values reject before loading.
Effective accepted-row accounting is active only when this request has a positive
barrier interval. The existing minfresh1025 threshold is retained, not tuned to
seeds. Thus the combined experimental policy applies after longer fresh prompts;
short or small cached suffixes retain ordinary all-row accounting and window
adaptation. Minimum0 remains the old all-request mode. No sampling, routing,
weights, quantization or context change. Cache placement can affect CPU/GPU
rounding; no byte-identical whole-model output or quality claim follows.

Test first: enabled/disabled and gated/ungated predicates, inactive/positive
request intervals, alternating request policy with independent accepted/all-row
accounting oracles; malformed/dependency CLI configurations, C051 split rejection.
CUDA build and existing accepted-usage/token-barrier tests. HIP/SYCL unavailable.

Then finite same-binary ABBA: R106 control barrier-only0, R107 candidate1. Both
HC1,acceptedusage1,conditional64/minfresh1025,auto shareMAX1024,DMA0/deviceplan0,
lag2,9workers30tasks,MTP4/.70,PCIe.20. Unsplit only. Exact IQ3_S262144 INT8KV/
32768resident CPUF16vision. Numeric thinking1/.95/20/0/0/1,frequency0 unchanged.
Same original short/~3K requests,512tokens,cachemiss,stream/concurrency1,onewarmup
and five measured seeds101..105 each. If any decode/E2E median falls>3% or prompt
falls>2%, close without confirmation. Else exactly one reversed R108B/R109A pair,
ordinary all10medians per cell, no further threshold or interval sweep. Require
runtime proof of short ordinary accounting and long accepted accounting/barriers.
If retained, reverse-workload history, boundary/cache-hit tests and full frozen
random coding/quality/cold-warm/vision/tools/reasoning/cancel/maxcontext gates
remain. No promotion from screening metrics.16GiB guards and exact cleanup apply.


## E167 / C053 implementation gates passed; finite comparison started

Implemented default-off STRATA_ACCEPTED_USAGE_BARRIER_ONLY with strict0/1 parser,
acceptedusage1 and positive configured interval requirements. Request flag derives
from the already resolved TokenBarrier interval; it gates capture, commit and
usage reporting together. Startup cache eligibility and C051 split rejection are
unchanged. Logs explicitly report fresh-token count, active policy and option.

New helper/boundary/alternating-request oracle tests failed to compile before the
helper existed, then passed. New CLI test reached the downstream no-model sentinel
on the old C051 binary (missing gate), then passed all11 configuration cases on
C053:4split controls,5invalid barrier-only/dependency cases,2allowed policy cases.
No test loaded model weights. CUDA13.3 sm86 Release, accepted-usage4096-window
oracle, token-barrier1.2M steps, Windows affinity and IQ AVX2 parity passed.
HIP/SYCL not built; no upstream review or full quality claim.

C053 engine SHA256 a5f344775873de8f9d1567dc153beb2736a1ce526571aca7eaff1d285dc1e4c8,
engine/strata-cuda133-barrier-usage.exe. Four configs prepared, only option0/1 differs.
R106 control started under independent16GiB guards after no-inference inventory,
GPU457MiB, verified production config3457fdfe. No other model/build/profiler runs.
All candidate source remains opt-in, no production launcher modification.


## E168 / R106-usage-all

Explicitly verified candidate engine SHA256 a5f344775873de8f9d1567dc153beb2736a1ce526571aca7eaff1d285dc1e4c8; loaded library hashes match R037-observer-no-process. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 89.9 (86.9-92.9) | 207.0 | 78.7990 | 78.8154 | 0.8389 | 930/1183 (78.61%) |
| longer | 84.8 (83.5-90.5) | 495.7 | 42.0352 | 42.0384 | 6.1634 | 965/1331 (72.50%) |

Minimum available physical RAM 62,495,952,896 bytes; available commit 41,703,223,296 bytes. Sampled GPU peak 25,121,722,368 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C053 same-binary all-request accepted-usage control; conditional barrier64/minfresh1025. Full five-seed sets completed. Not a qualification or a comparison with historical binaries.

Next: Run R107 barrier-only accounting on identical binary and requests; apply E166 finite gates.


## E169 / R107-usage-barrier

Same engine and loaded library hashes as R106-usage-all. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.8 (88.0-89.8) | 206.6 | 77.6272 | 77.6379 | 0.8414 | 842/1089 (77.32%) |
| longer | 86.9 (79.9-89.8) | 495.2 | 42.4579 | 42.4612 | 6.1705 | 984/1335 (73.71%) |

Minimum available physical RAM 62,496,063,488 bytes; available commit 41,699,950,592 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C053 initial pair: candidate88.8/86.9 versus89.9/84.8 control. Short decode -1.22%, longer +2.48%; neither decode/E2E exceeds3% regression nor prompt2%, so execute the single predeclared reversed pair. Not a winner or target qualification.

Next: Run exactly R108 candidate then R109 control; pool all ten measured rows per workload/cell and close C053.


## E170 / R108-usage-barrier

Same engine and loaded library hashes as R106-usage-all. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.8 (88.2-89.8) | 209.3 | 77.5645 | 77.5760 | 0.8261 | 851/1174 (72.49%) |
| longer | 86.0 (85.1-88.6) | 495.3 | 42.2664 | 42.2697 | 6.1676 | 920/1257 (73.19%) |

Minimum available physical RAM 62,432,530,432 bytes; available commit 41,622,216,704 bytes. Sampled GPU peak 25,123,819,520 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C053 reverse candidate completed88.8/86.0 decode; second candidate short median repeats88.8. No selection of favorable longer seeds. Final reverse control is required before pooled decision.

Next: Run R109 all-request accounting control, then pool all ten measured rows per cell and close C053.


## E171 / R109-usage-all

Same engine and loaded library hashes as R106-usage-all. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.2 (86.8-91.5) | 201.8 | 78.9291 | 78.9405 | 0.8449 | 895/1167 (76.69%) |
| longer | 90.0 (83.2-94.3) | 495.5 | 43.2729 | 43.2774 | 6.1598 | 1057/1371 (77.10%) |

Minimum available physical RAM 62,421,921,792 bytes; available commit 41,652,064,256 bytes. Sampled GPU peak 25,125,916,672 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C053 final reverse control completed. Four-arm finite comparison finished; pool all ten measured rows per workload/configuration. No extra repeats.

Next: Compute C053 all-run medians, activation proof, request equality, memory/cleanup and decide source disposition.


## E172 / C053 closed and rejected; goal-threshold correction

Four-arm ABBA completed: R106A89.9/84.8, R107B88.8/86.9,
R108B88.8/86.0, R109A90.2/90.0 short/~3K decode medians. All48requests
were512tokens/cachemiss, exact twelve payloads equal across all four processes.
Warmups excluded, all ten measured rows per workload/configuration retained.
Same a5f34477 engine; only STRATA_ACCEPTED_USAGE_BARRIER_ONLY0/1 differs.

| Ordinary all-ten-run median | All-request accounting | Barrier-only accounting | Change |
|---|---:|---:|---:|
| short server_decode_tps |90.050000|88.800000|-1.388%|
| short prompt_tps |206.950000|207.950000|+0.483%|
| short request_e2e_tps |78.864052|77.595824|-1.608%|
| short stream_total_tps |78.877924|77.606974|-1.611%|
| short ttft_seconds |0.842238|0.833783|-1.004%|
| short request_seconds |6.492189|6.598294|+1.634%|
| longer server_decode_tps |86.650000|86.050000|-0.692%|
| longer prompt_tps |495.600000|495.250000|-0.071%|
| longer request_e2e_tps |42.471709|42.298843|-0.407%|
| longer stream_total_tps |42.475400|42.302017|-0.408%|
| longer ttft_seconds |6.160471|6.169093|+0.140%|
| longer request_seconds |12.056357|12.104357|+0.398%|

The candidate fails no-degradation: pooled decode and E2E are lower in both
workloads. Short88.8 misses90; longer86.05 misses90. Reject, archive patch/tests/
build evidence, and restore the four changed source files to49db7853. C051's
split/accounting incompatibility guard remains. Production launcher/config/engine
remain unchanged. No extra repetitions or threshold sweep. The C053 a5f34477
binary remains a diagnostic artifact; build-cuda86-main contains its objects until
a future rebuild. Do not silently call it current clean-source code after restore.

Runtime proof: all24control requests used accepted accounting; both candidate
processes logged active0 on all12short requests and active1 on all12longer
requests. Every longer request logged seven64-token barrier updates. Therefore
the failed result is not an inactive-setting/fallback explanation. Longer results
can change despite identical longer policy because prior short requests change
cache history. Output/draft behavior also varies; no isolated kernel gain inferred.

Safety: minimum available physical62421921792
and commit41622216704bytes;16GiB floor passed
through all48requests. Exact launcher/server/engine/vision cleanup passed each arm,
config3457fdfe restored, GPU457MiB idle. No benchmark model resident.

THRESHOLD CORRECTION: goal-90-contract.md established90tok/s in BOTH short and~3K
qualifying speed cells. Several later progress/ledger summaries, including recent
90/85 wording, accidentally repeated the earlier pre-goal85longer target. They do
not amend the fixed goal contract. Keep historical numbers; interpret completion
against90/90 and every quality, stability, memory and workload gate. This correction
restores the existing contract, not a new threshold or a relaxation. The saved
contract file itself is unchanged. Current summaries will explicitly say90/90.

The C053 control's90.05/86.65screen medians therefore do NOT meet the goal. The
short margin is only0.05tok/s, long is below90, and frozen random coding/full quality
remain unqualified. C052's90.5/84.5 control was also unqualified. No speed or quality
promotion follows from any of these control observations.

Next: stop selecting from the TTLCache screen alone. Measure the retained native
HC1/acceptedusage1/conditional64/minfresh1025 stack on the already-frozen random
medium coding fixture with unchanged512token speed and8192token separate quality
checks. Use the clean-source C051 engine0dea69dc, same numeric thinking profile,
context/vision, independent memory guards and exact cleanup. That is a NEW measured
baseline on that fixture, not a reuse of a5f34477's90.05result. Preserve Q007's two
incomplete answers as failures; establish whether they persist on this stack before
another sampled-drafting combination. Goal remains active; no blocker declared.


## E173 / frozen coding baseline and completion-quality refresh

Previous goal turn was progress: six full served arms completed, C052/C053 rejected,
C053 source restored and ledger pushed7e4f5d7a. The fixed goal is90tok/s in both
short and~3K cells; no threshold or sampling change in this refresh.

Use existing randomly selected topological_order fixture SHA25616fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5,
unchanged task/reference, seeds101..105,512output tokens, one warmup per short/
longer streaming cache-miss cell. Two fresh processes R110 short-first/R111
longer-first. Native C051 engine0dea69dc, HC1/accepted1/conditional64/minfresh1025,
IQ3_S262144 INT8KV/32768resident CPUF16vision, MTP4/.70,PCIe.20,lag2,9workers30tasks,
auto prompt shareMAX1024,DMA0/deviceplan0. Numeric thinking1/.95/20/0/0/1 and
frequency0, unlimited reasoning unchanged. No coupled/probabilistic sampler flags.
This is an additional fixed-workload baseline, not an optimization gain against
historical B011 or proof that every cold/cache-hit/nonstream cell passes.

Then Q008 uses the same original quality payloads from Q007, five seeds101..105,
separate8192-token natural-stop allowance and72objective tests per final function.
Do not substitute those throughput values for512-token speed results. Preserve
incomplete answers as failures, keep the cap and prompt fixed. No new variant or
parameter sweep during these checks. Q0073/5 remains historical failed evidence.

Preflight no inference/compiler/profiler, GPU457MiB, config3457fdfe restored.
Independent16GiB physical/commit guard eachsecond, no process-memory polling,
exact launcher/server/model/vision cleanup and config restoration per process.
R110 started; its live exec handle was91599. Do not start a second server.


## E174 / R110-random-native frozen coding baseline

longer/stream/new: decode[88.2, 90.2, 88.3, 89.0, 90.3] => ordinary median89.0; prompt510.2, E2E42.960721, stream42.965072, TTFT6.180677s.

short/stream/new: decode[92.2, 95.0, 98.1, 90.9, 92.7] => ordinary median92.7; prompt214.0, E2E81.283776, stream81.305735, TTFT0.807274s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C051 engine0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Full matrix and quality remain required.

Minimum physical62218043392 and commit41268506624bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Run R111 in reversed workload order, then Q008 complete-answer quality under unchanged profile.


## E175 / R111-random-native-reverse frozen coding baseline

longer/stream/new: decode[78.1, 84.2, 91.5, 90.9, 89.7] => ordinary median89.7; prompt509.0, E2E43.154368, stream43.157858, TTFT6.182458s.

short/stream/new: decode[93.5, 93.7, 95.2, 94.1, 91.2] => ordinary median93.7; prompt210.4, E2E81.998981, stream82.014900, TTFT0.824625s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C051 engine0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Full matrix and quality remain required.

Minimum physical62384869376 and commit41575317504bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Pool both coding arms and run Q008 complete-answer quality under unchanged profile and corrected 90 short / 85 long thresholds.


## E176 / user threshold correction and paired coding baseline

The user correction relayed through oversight at2026-10-10 07:51UTC sets90 server_decode_tps short and85 at approximately3K input. This supersedes E172 and the previous90-both contract interpretation. Updated goal-90-contract.md, goal-90-state.json, README current summary and explicit threshold checks in diagnostics/coding-refresh/paired-summary.json. Goal tool remains active; its90 headline remains the short target and its API cannot edit objective text. Historical logs, failures and recording scripts are preserved, not rewritten or rerun. Sampling, context, quality, memory, workload matrix and promotion requirements are unchanged.

short/stream/new: all10 decode values[92.2, 95.0, 98.1, 90.9, 92.7, 93.5, 93.7, 95.2, 94.1, 91.2]; ordinary median93.6; E2E median81.641379; prompt median211.45. Numeric speed threshold met; not full qualification.

longer/stream/new: all10 decode values[88.2, 90.2, 88.3, 89.0, 90.3, 78.1, 84.2, 91.5, 90.9, 89.7]; ordinary median89.35; E2E median43.057545; prompt median509.35. Numeric speed threshold met; not full qualification.

Both fresh-process confirmations complete; exact server cleanup verified. No benchmark model resident. Next Q008 completed-answer tests without modifying the fixed profile or8192-token quality allowance.


## E177 / Q008 completed-answer quality refresh started

Previous goal turn made progress: R111 finished, both coding baselines were pooled, user targets reconciled to90 short /85 longer, and all evidence was validated and pushed asd055dc26. No numeric profile or quality condition changed.

Q008 uses byte-identical R110 configuration (C0510dea69dc engine; HC1/accepted1/conditional64/minfresh1025), original goal90-quality.py, unchanged topological fixture, seeds101-105, max8192 and natural-stop plus72 objective tests per answer. There is no speed qualification from this quality run and no additional quality warmup. Original Q007 failures remain. Added only a private supervisor --goal-quality selector to run the existing quality client under the same16GiB global physical/commit guard, timeout and exact-tree cleanup. Mutually exclusive workload selectors reject mixed modes. Both helper scripts compile; production configuration3457fdfe and idleGPU457MiB were verified before start. Supervisor rejects concurrent inference/build/profiler processes.

Live session57761; outputQ008-goal-coding, wrapperQ008-wrapper.txt. Inspect that handle before any other model launch. No Git/build/profiler/process-memory polling during requests. Next: verify all five request payloads againstQ007, preserve every outcome, inspect final answers and guard/cleanup evidence before deciding further work.


## E178 / Q008 completed-answer quality results

Seed101: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed102: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed103: 6600tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed104: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed105: 8192tokens, finishlength, passed=False; Did not stop naturally

Quality pass count1/5. Every request exactly matchesQ007, including numeric profile, thinking, seed, task and8192 cap. All actual cache counts are zero. Every passing answer stopped naturally, compiled and passed72 objective tests. All failures retained. These variable-length answers are excluded from512-token target statistics. No quality warmup; inherited manifest warmup wording is corrected in this audit.

Minimum physical62487044096 and commit41671241728bytes; both16GiB floors pass. Supervisor exact cleanup verified and production config3457fdfe restored. Native experimental C051 stack remains unpromoted.

Next: Run identical Q009 quality suite on production control to separate inherent8192-token incompletion from candidate regressions before more tuning.


## E179 / Q009 same-day production quality control

Q008 passed1/5 versus historical Q0073/5, with seeds101/102/104/105 incomplete at8192 and no final answer. Historical comparison alone does not establish cause. Run Q009 immediately on the restored production configuration3457fdfe, format-gather engine6048736d, identical quality client, prompts, seeds, profile, vision, context and8192 cap. Only engine and environment differ fromQ008; explicit diff archived. No speed claim from variable-length quality answers. All five seeds retained regardless of prior failure. Same guarded supervisor and exact cleanup apply. No production changes.


## E180 / Q009 completed-answer quality results

Seed101: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed102: 5211tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed103: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed104: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed105: 8192tokens, finishlength, passed=False; Did not stop naturally

Quality pass count1/5. Every request exactly matchesQ007, including numeric profile, thinking, seed, task and8192 cap. All actual cache counts are zero. Every passing answer stopped naturally, compiled and passed72 objective tests. All failures retained. These variable-length answers are excluded from512-token target statistics. No quality warmup; inherited manifest warmup wording is corrected in this audit.

Minimum physical62260240384 and commit41414959104bytes; both16GiB floors pass. Supervisor exact cleanup verified and production config3457fdfe restored. Production control quality measured; experimental stack remains unpromoted.

Next: Compare Q009 production with Q008 candidate outcomes and isolate the component affecting completion; do not promote the quality-failing stack.


## E181 / paired quality interpretation and unchanged contract

Q008 candidate1/5 and same-day Q009 production1/5. Q008 seed103 completed6600tokens; Q009 seed102 completed5211tokens; each compiled and passed72 objective tests. Other four responses in each suite exhausted8192 during reasoning without final answer. All ten request payloads matchQ007 exactly. Original Q0073/5 remains retained. Q007/Q009 engine, vision, loaded backend libraries, configuration, expert-profile and fixture hashes all match; outcome variation therefore exists even for the same recorded production identity. Different cache/scheduling state and floating-point execution paths remain hypotheses, not established causes. Fixed seeds do not promise identical full text here. Source inspection confirms serve/server.py forwards positive integer seeds and generate.cpp initializes req_sp.seed from the request and resets counter0. No code fix was made on speculative attribution.

Both configurations fail the existing completed-answer gate. The current data do not establish a candidate-specific quality regression, nor do equal pass counts prove quality equivalence. The512-token medians93.6 short/89.35 longer remain narrow speed-cell results, not goal completion. Variable-length quality decode ranges77.6-82.6 candidate and77.9-81.2 production are separate diagnostics, not the512-token metric. Production launcher remains unchanged; all benchmark trees stopped; GPU457MiB/0percent after each suite. Both global16GiB memory floors passed.

Rechecked the user-specified model card on2026-10-10: https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF#best-practices . It keeps the prescribed thinking sampler and advises ample generation length for reasoning. Our8192 completion-quality cap is a frozen test limit, not that model-card recommendation. Asked the user whether to raise only this separate quality allowance to32768;512-token speed requests, prompts, seeds, sampler, context and objective tests would stay fixed. No answer yet and no cap change applied. This approval is required by the user's fixed-contract instruction, not an inferred skill restriction. All failures remain historical evidence whatever the decision.

Next independent optimization work: audit the existing distribution-preserving coupled-Gumbel path with the retained HC/accepted-cache stack, then a bounded same-binary control/candidate comparison if integration is sound. Earlier R040 coupling alone86.9/85.1 versus R03787.5/83.9 was mixed, not a winner; the new hypothesis is a measured interaction with GPU/cache improvements, not assumed additive gains. Preserve every numeric sampling parameter and exact-match target verification; biased probability/suffix paths stay excluded. A new random stream requires its own fixed-arm reproducibility and completed-answer checks before promotion. No new inference run has started.


## E182 / C054 coupled drafting plus HC/cache combination

Previous turn made progress: complete Q008/Q009 quality evidence changed interpretation and was pushedf523264f. Goal remains active with corrected90short/85long thresholds. Quality cap8192 unchanged; user choice about32768 remains pending. Current authoritative cleanup logs and idleGPU457MiB verified before tests. No production source or configuration edit.

Hypothesis: R040 coupling's longer-context gain may combine with HC latency hiding and accepted-row cache accounting. Coupling changes draft/target agreement, HC changes GPU execution, accepted usage changes expert placement; interactions can help or hurt, so no addition of isolated speedups is assumed. Existing R040 mixed result stays closed as a stand-alone configuration. This is a distinct combined stack compared on one C0510dea69dc executable.

Integration audit: generate.cpp clips the verify window at token barriers before AcceptedUsage.begin(T), captures rows only around ver.run, clears the pointer before MTP draft execution, and commits exactly the a+1 target-verified input prefix. Target verification uses exact equality; STRATA_SPEC_PROB is explicitly0, so known biased probability/suffix composition is excluded. Coupled counters use absolute sequence positions and copy the unchanged per-request sampler. HC selection does not alter this acceptance logic. Gumbel draws preserve the intended categorical distribution subject to finite implementation checks; they change the seeded text stream and are not claimed byte-identical to inverse-CDF sampling.

Ran fresh build/checks for sampler_parity, sampler_parity_one_block, sampler_parity_old, coupled_draft_test, accepted_usage_test and token_barrier_test:6/6 pass. Sampler tests include the fixed numeric chain, GPU/host Gumbel checks and empirical distribution checks; host tests cover counters/history/prefixes/boundaries. These do not establish complete model quality. Buildtree strata.exe remains archived C053 and is NOT used; served engine is explicit C051 file0dea69dc. Private supervisor now verifies requested coupled-startup marker before timed requests.

Pre-registered comparison: R112 A0/0, R113 B1/1 for STRATA_SPEC_COUPLED/STRATA_SPEC_GUMBEL. HC1, accepted1, conditional64/minfresh1025, lag2, PCIe.20, MTP4/.70, modelIQ3_S,262144context,INT8KV and CPUF16vision fixed. Both arms explicitly set probability/old/one-block sampler flags0. Original TTLCache short/~3K streaming cache misses, same requests/seeds101-105,512tokens,1warmup+5measured each. No other model/profiler/build runs during inference;16GiB global floors and exact tree cleanup.

Finite screen: if candidate loses more than3percent in either server-decode or E2E median, or either prompt-rate median, stop after the first pair. Otherwise complete R114 B then R115 A with reverse workload order and pool all ten rows per cell. This3percent is only a screening stop, never a promotion regression allowance. Full target/no-degradation and all quality/matrix gates remain required. At most four arms; no repeated search for a favorable median. Archive every warmup, slow seed, output, MTP acceptance and resource record.


## E183 / R112-coupled-stack-control

Explicitly verified candidate engine SHA256 0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd; loaded library hashes match R099-conditional64. This is a new-binary control comparison, not a same-binary claim. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.7 (87.4-91.2) | 210.0 | 77.9408 | 77.9522 | 0.8345 | 805/1088 (73.99%) |
| longer | 86.7 (82.2-88.1) | 496.5 | 42.5708 | 42.5741 | 6.1520 | 978/1290 (75.81%) |

Minimum available physical RAM 62,292,963,328 bytes; available commit 41,396,244,480 bytes. Sampled GPU peak 25,130,110,976 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C054 feature-off control88.7 short/86.7 longer; no coupled candidate measured yet. Quality evaluation takes priority after user approval of a separate32768-token allowance.

Next: Q010 candidate and Q011 production complete-answer suites at32768;512-token speed protocol unchanged. R113 remains queued, not run.


## E184 / approved expanded quality allowance, Q010 and Q011

Direct user answer in this thread approves raising only the separate completed-answer quality allowance to32768. The oversight relay conveys the same approval. Updated goal-90-contract.md from8192 to32768 with historical-preservation clause; added goal90-quality-expanded.py instead of altering the original8192 client. Every payload must equal its originalQ007 payload after changing only max_tokens. Existing checker check-topological.py and its72cases are unchanged. Five seeds101-105, original task, numeric sampler, reasoning settings, model, context, vision and memory floors remain fixed.512-token speed requests unchanged.

Private supervisor adds --goal-quality-expanded selecting the new client and a7200s whole-suite safety timeout, allowing five longer answers while preserving1s16GiB physical/commit checks and exact final cleanup. Legacy client/timeout remains available unchanged. Q010-expanded-candidate uses exactQ008 config; Q011-expanded-production uses exactQ009 config. Both have distinct output paths, no quality warmup, and no speed-target claim from variable-length answers. New manifest explicitly corrects quality warmup wording.

R112 completed before this change and exact cleanup passed. C054 candidateR113/R114/R115 not started; bounded combination remains queued while matched completed-answer quality takes priority. R112 control88.7/86.7 is retained, not a combined optimization result. No model resident at the preparation checkpoint. Next: runQ010, audit natural completion and tests, cleanup; then matchedQ011. Record any cap failures and never relabel Q007/Q008/Q009.


## E185 / Q010-expanded-candidate approved expanded quality

Seed101: 15491tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed102: 6210tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed103: 32768tokens, finishlength, passed=False; Did not stop naturally

Seed104: 2254tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed105: 7939tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Pass count4/5 with user-approved32768 cap. All five requests equal the originalQ007 requests except max_tokens. Configuration, executable, libraries, expert profile, fixture and vision hashes matchQ008-goal-coding. Natural-stop passing answers compile and pass72tests each. Zero prompt reuse. Legacy8192 failures remain unchanged. Variable-length quality answers do not satisfy the512-token speed target.

Minimum physical62516215808 and commit41714528256bytes;16GiB floors pass. Exact cleanup verified and production3457fdfe restored. No promotion; other workload, stability and real-use requirements remain.


## E186 / Q011-expanded-production approved expanded quality

Seed101: 9087tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed102: 3740tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed103: 3417tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed104: 5742tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed105: 7482tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Pass count5/5 with user-approved32768 cap. All five requests equal the originalQ007 requests except max_tokens. Configuration, executable, libraries, expert profile, fixture and vision hashes matchQ009-production-quality. Natural-stop passing answers compile and pass72tests each. Zero prompt reuse. Legacy8192 failures remain unchanged. Variable-length quality answers do not satisfy the512-token speed target.

Minimum physical62270132224 and commit41084174336bytes;16GiB floors pass. Exact cleanup verified and production3457fdfe restored. No promotion; other workload, stability and real-use requirements remain.


## E187 / approved expanded quality comparison closes

Q010 candidate4/5 versus matched Q011 production5/5 at the user-approved32768 completed-answer allowance. All five request files are byte-identical between arms, and equalQ007 after changing only max_tokens. Profile, seeds, task, checker and72 test cases remain unchanged. Production's successful answers were reviewed as coherent implementations; finite test coverage is not a claim of universal model quality.

| Seed | Candidate tokens | Candidate outcome | Production tokens | Production outcome |
|---|---:|---|---:|---|
|101|15491|natural stop;72tests pass|9087|natural stop;72tests pass|
|102|6210|natural stop;72tests pass|3740|natural stop;72tests pass|
|103|32768|cap reached; no final answer|3417|natural stop;72tests pass|
|104|2254|natural stop;72tests pass|5742|natural stop;72tests pass|
|105|7939|natural stop;72tests pass|7482|natural stop;72tests pass|

Candidate seed103 exhausted32768 while production seed103 finished3417 and passed. Candidate is ineligible for promotion under the fixed all-five condition. This one pair does not identify a causal component or prove a general distributional quality regression. Do not rerun the unchanged candidate until a favorable pass count appears. Preserve all Q007/Q008/Q0098192 failures and Q01032768 failure. No source/runtime/launcher change was promoted. Both exact trees stopped, production config3457fdfe restored, idleGPU457MiB/0percent. Both host16GiB floors passed.

Long-answer throughput is diagnostic only, not the512-token target. Q010 selected coding speed medians from earlier R110/R11193.6/89.35 remain separate. Original-workload R112 control88.7/86.7 is below the short90 target, so full performance qualification also remains incomplete. Q011's5/5 quality applies to production6048736d configuration only; it cannot be transferred to C051 HC/accepted1 stack.

C054 state: integration6/6 checks pass, R112 control completed, R113/R114/R115 were never started after quality took priority. Keep that proposed combination queued; no combined winner exists. Next controlled diagnosis: same C051 executable and HC1, disable accepted-row accounting and its dependent barriers for a complete five-seed32768 quality suite. All quality inputs are148 fresh tokens, below the1025 barrier threshold, so barriers were inactive in Q010; the changed active mechanism is accepted-row accounting. This is a component-isolation test, not a new sampling profile or a retry of the same configuration. Inspect dependency guards before preparing it. After quality is resolved, prioritize the outstanding unchanged nonstream/cache-hit, mixed-history and real-use matrix before additional speed searches.

Changes implementing approval: goal-90-contract.md quality allowance; new goal90-quality-expanded.py (legacy client preserved); private supervisor expanded-client selector and7200s whole-suite timeout with original per-second memory guards; record-expanded-quality.py validates exact request equivalence except approved cap and preserves natural-stop/72-test scoring. Checker check-topological.py unchanged.512-token benchmark client unchanged. The generated final functions are published separately from their reasoning for inspection.


## E188 / reproduce completion failure before component ablation

Refined the next step after review: a single Q010/Q011 pair cannot identify which component caused the seed103 difference. Before the broad ablation proposed inE187, do one bounded fresh-process matched replay of seeds101,102,103 in that order on candidate and production. Preserve the preceding requests rather than extracting seed103 in isolation: adaptive cache/tuner history matters. Same32768 allowance, request bytes, numeric profile, reasoning, model/context/vision and72-test checker. Label replay as a three-request diagnosis, not a replacement for the five-answer quality gate. At most one candidate/control pair; retain a non-reproduction and do not keep repeating until a desired outcome. Only follow with a one-component ablation if evidence supports it; respected accepted-usage/barrier dependency remains mandatory.

No replay started. Both model trees remain cleaned up. C054 speed candidate still queued. The expanded allowance is approved and already applied; no user decision remains pending. Next authoritatively inspect process state, then prepare distinct Q012/Q013 diagnostic paths after confirming they are unused.

Publication check: an atomic replacement of an existing P018 identity export returned transient Windows AccessDenied once; both files had ordinary Archive attributes. Re-running the unchanged exporter succeeded. No experiment was rerun and no measurement was discarded. Final inventory/hash validation is required before push.

Publication validation also caught the private LAN literal in the newly copied audit-helper source before any push. Sanitized that public copy; executable private helper and all measurements unchanged.


## E189 / bounded completion-replay pair prepared

Previous turn made progress: expanded matched Q0104/5 vsQ0115/5 completed, code outputs reviewed, cleanup verified, user-approved contract change and evidence pushed55daf8c1. Fresh upstream GitHub API check still finds mainfb58e0dbc8399662c0e47c76578c6e878b14f6cf and releasev0.1.41 published2026-10-08; no new Strata update to apply. Current checkout has only the two known unrelated untracked files; neither is read or staged.

One diagnostic pair only: Q012-replay-candidate uses byte-identical Q010 config; Q013-replay-production uses byte-identical Q011 config. Fresh process per arm, no warmup, requests101,102,103 in original order. Each request exactly matches its expanded-suite counterpart. This preserves preceding request history and lets the adaptive cache evolve normally; it does not promise identical hidden cache tensors when generated text varies. Focus is whether seed103 incompletion reproduces.32768cap, numerical thinking profile,72-case checker, model/context/vision and16GiB physical/commit floors fixed.

New private goal90-quality-replay.py changes only the original expanded client's loop bound and diagnostic metadata/workload label. Summary explicitly says diagnostic_only and full_quality_qualified false even if all three pass. Private guarded supervisor selects this client with --goal-quality-replay and a5400s whole-suite timeout. Original five-seed and512-token clients unchanged. No code/runtime modification or speculative flag change is being tested. Snapshot guards reject concurrent inference/profiler/build processes; full-tree cleanup before the next arm.

Finite outcome rule: run each configuration once. Preserve both a reproduction and a non-reproduction; do not repeat until a preferred result. An ablation follows only with supporting evidence. This diagnosis never overwrites Q010's failed five-answer gate or substitutes three answers for five. C054 R113/R114/R115 remain queued, not started. Next: Q012 thenQ013, compare complete prefix outcomes and seed103, then choose the next safe action from evidence.


## E190 / Q012-replay-candidate bounded replay

Seed101: 5172tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed102: 7054tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed103: 4628tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Diagnostic count3/3; not full quality qualification. Requests byte-identical toQ010-expanded-candidate, run101/102/103 in original order from a fresh process. No warmup. Same32768 cap, profile, tests, binaries/libraries/config/model/vision identity. Generated histories may differ; cache tensors are not claimed identical. Prior failures are never replaced.

Minimum physical62469341184 and commit41708654592bytes;16GiB floors pass. Exact cleanup verified; production3457fdfe restored. No promotion.


## E191 / Q013-replay-production bounded replay

Seed101: 8244tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed102: 8207tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed103: 13008tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Diagnostic count3/3; not full quality qualification. Requests byte-identical toQ011-expanded-production, run101/102/103 in original order from a fresh process. No warmup. Same32768 cap, profile, tests, binaries/libraries/config/model/vision identity. Generated histories may differ; cache tensors are not claimed identical. Prior failures are never replaced.

Minimum physical62526005248 and commit41694203904bytes;16GiB floors pass. Exact cleanup verified; production3457fdfe restored. No promotion.


## E192 / bounded replay closes; no causal component identified

The immediately preceding user-question response explained metrics and made no optimization progress. This continuation authoritatively polled live session32540, completed its audit, and ran the already registered production replay serially. No run was restarted because an observation expired.

Q012 did not reproduce the candidate seed103 cap failure. Three requests in the original101/102/103 order all completed and passed72tests. Q013 provides the matched production replay below. Request files are byte-identical between arms and to the corresponding expanded suite. Fresh process per arm; no warmup; fixed32768 allowance and unchanged numerical thinking profile, checker, model, context and vision. Prior generated text and hidden adaptive-cache state need not be identical even with the same request seeds.

| Seed | Candidate tokens / outcome | Production tokens / outcome |
|---|---|---|
| 101 | 5172 / stop / pass=True | 8244 / stop / pass=True |
| 102 | 7054 / stop / pass=True | 8207 / stop / pass=True |
| 103 | 4628 / stop / pass=True | 13008 / stop / pass=True |

This ends the one-pair diagnosis. Do not rerun the unchanged configuration until a favorable result appears, and do not attribute the earlier cap failure to HC or accepted-row accounting without causal evidence. Q010 remains4/5 and ineligible for promotion; Q011 remains5/5 for production only. Three passing diagnostic answers never replace the full five-answer gate. All earlier failures and generated answers remain published. Fixed512-token speed measurements are separate.

Qualification assessment before another speed test:

- Retained production has Q011 five completed answers passing all72tests, but is not certified to meet the new90/85 speed goal. Its previous real-use checks remain historical evidence.
- Experimental C051 HC/accepted-usage/conditional-barrier stack has R110/R111 selected-coding streaming medians93.6/89.35, but original-workload R112 short88.7 is below90. Its Q010 quality gate failed4/5. These are two independent blockers to promotion.
- Current experimental stack still lacks two qualifying confirmations of selected-coding nonstream misses and exact-repeat hits in both modes, plus refreshed mixed-history, tools, vision, reasoning controls, cancellation, idle and near-limit checks. No old production result certifies this stack.
- Q012 is diagnostic evidence only and does not clear any missing full-quality or workload gate. A broad component ablation is unsupported by this non-reproduction.

Next: resume the already preregistered C054 combination screen, R113 coupled/Gumbel drafting on the unchanged HC/accepted-usage/conditional-barrier stack versus R112. This is an explicitly new candidate, not continued qualification of the failed unchanged candidate. The bounded speed screen comes before a costly full matrix because the existing candidate is already ineligible and below the original-workload short target. This tests a new composition of existing mechanisms, not a quality retry or promotion. Numeric sampling and all fixed workload settings remain unchanged. If either decode/E2E/prompt median loses more than3percent, reject after the first pair; otherwise finish the bounded reverse-order R114/R115 comparison and pool every measured row. New seeded streams require their own full quality and real-use gates before any promotion. No production launcher changes.


## E193 / R113-coupled-stack

Same engine and loaded library hashes as R112-coupled-stack-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.0 (87.7-91.6) | 206.6 | 78.5023 | 78.5139 | 0.8545 | 850/1097 (77.48%) |
| longer | 86.0 (81.7-89.8) | 496.4 | 42.3687 | 42.3719 | 6.1528 | 880/1194 (73.70%) |

Minimum available physical RAM 62,540,607,488 bytes; available commit 41,750,736,896 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

First C054 pair mixed: candidate90.0/86.0 versus control88.7/86.7 decode. Short prompt median206.6 versus210.0; all pre-registered screen losses less than3percent. Neither a winner nor full qualification. Original Q010 quality failure remains.

Next: Complete bounded reverse-order R114 candidate then R115 control and pool all ten rows per cell; no further unchanged retries.


## E194 / R114-coupled-stack-reverse

Same engine and loaded library hashes as R112-coupled-stack-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 90.3 (86.1-91.5) | 200.2 | 78.3273 | 78.3423 | 0.8679 | 860/1097 (78.40%) |
| longer | 88.3 (83.4-91.4) | 496.5 | 42.9287 | 42.9328 | 6.1492 | 1047/1333 (78.54%) |

Minimum available physical RAM 62,498,480,128 bytes; available commit 41,779,806,208 bytes. Sampled GPU peak 25,117,528,064 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C054 second candidate arm completed in reverse workload order. Preserve all rows; final decision deferred until registered reverse control R115 completes and both ten-run sets are pooled. No promotion or full-quality qualification.

Next: Run R115 reverse-order control once; close C054 using complete ordinary medians and no-degradation contract.


## E195 / R115-coupled-stack-control-reverse

Same engine and loaded library hashes as R112-coupled-stack-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 87.7 (87.6-92.4) | 209.0 | 77.1613 | 77.1814 | 0.8422 | 858/1141 (75.20%) |
| longer | 84.7 (81.6-92.4) | 495.8 | 42.0414 | 42.0447 | 6.1545 | 974/1294 (75.27%) |

Minimum available physical RAM 62,472,945,664 bytes; available commit 41,714,196,480 bytes. Sampled GPU peak 25,115,430,912 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

C054 registered ABBA sequence complete. Final reverse-order control retained without dropping slow seeds; evaluate complete pooled comparison next. No promotion or full-quality qualification.

Next: Compute all ten-run ordinary medians, prompt/E2E differences, preserve quality uncertainty and publish bounded C054 result.


## E196 / C054 complete ABBA: numeric thresholds reached, no-degradation unproven

Same C051 engine0dea69dc and loaded libraries, modelIQ3_S,262144context,INT8KV, compatible CPUF16vision, serial requests, MTP4/minp.70 and fixed thinking numeric profile. ControlR112/R115 has coupled/Gumbel0/0; candidateR113/R114 has1/1. Other configuration fields match exactly. All measured request bytes match control, seeds101-105,512completion tokens and zero cache reuse. One excluded warmup per cell per fresh process, two opposite workload orders, ten measured rows per cell per configuration. The comparison script verifies these conditions. No cherry-picked seed, peak or upper median.

| Workload | Configuration | Decode median | Prompt median | E2E median | Stream-total median | TTFT median seconds |
|---|---|---:|---:|---:|---:|---:|
| short | control | 88.55 | 209.35 | 77.56124 | 77.57229 | 0.838461 |
| short | candidate | 90.15 | 205.30 | 78.41483 | 78.42810 | 0.856666 |
| longer | control | 86.55 | 496.00 | 42.45596 | 42.46041 | 6.153906 |
| longer | candidate | 87.15 | 496.45 | 42.64870 | 42.65235 | 6.150953 |

All raw decode values in arm order, each arm in seed101-105 order:

- short control: [91.2, 88.7, 88.4, 91.2, 87.4, 87.6, 87.6, 87.7, 92.4, 90.0]; accepted/offered 1663/2229.
- short candidate: [90.9, 91.6, 90.0, 87.7, 88.9, 88.8, 91.5, 90.3, 86.1, 90.7]; accepted/offered 1710/2194.
- longer control: [82.2, 86.7, 88.1, 86.5, 88.1, 81.6, 92.4, 84.2, 86.6, 84.7]; accepted/offered 1952/2584.
- longer candidate: [81.7, 89.7, 84.5, 86.0, 89.8, 83.4, 90.2, 84.7, 88.3, 91.4]; accepted/offered 1927/2527.

Candidate ordinary decode medians90.15short/87.15long reach the corrected numerical90/85 thresholds in these original TTLCache streaming miss cells only. Both candidate five-run arms also reach the corresponding thresholds individually. Pooled short decode+1.81percent and E2E+1.10percent; longer decode+0.69percent and E2E+0.45percent. These modest gains need the remaining workload/quality evidence and are not a global goal-completion claim.

Short prompt processing209.35 to205.30tok/s is -1.93percent; TTFT0.838461 to0.856666seconds rises0.018205seconds. Longer prompt496.00 to496.45tok/s. The preregistered3percent stop threshold was only a screening rule, never permission to accept a regression. The user's no-prompt-degradation requirement is NOT proven. This finite ABBA screen is closed; do not keep repeating it until the prompt difference disappears. Preserve this mixed result and investigate the prompt/cache interaction through separately specified evidence. Coupled/Gumbel changes the seeded text stream; finite target-distribution checks are archived, not a claim of byte-identical output or a full model-quality guarantee.

Quality status: Q010's prior HC/accepted-usage candidate remains4/5 under32768, and its three-request replay does not erase the failure. C054 is a distinct combined configuration with no completed five-answer quality suite yet. Q011 production5/5 cannot be transferred to it. Neither quality nor any missing real-use gate is waived. No production launcher or source change promoted. All four exact launcher trees cleaned up and original production config3457fdfe restored. Physical/commit16GiB floors passed; observed GPU memory returned457MiB and utilization0percent after R115.

Next bounded step: one five-seed32768 complete-answer suite for C054 (Q014-coupled-quality), unchanged checker, tasks and numeric profile. Do not retry it until passing. If it fails, preserve and reject promotion. If it passes, proceed to the outstanding selected-coding/nonstream/cache-hit and real-use cells with matched production controls; quantify prompt behavior in those cells rather than treating the present1.93percent loss as allowed. No further blind C054 TTLCache repetitions. Keep the goal active and leave production unchanged until every gate passes.


## E197 / Q014 full quality check for the combined candidate

Previous goal turn made progress: bounded quality replay closed without reproducing the prior cap failure; C054 ABBA completed with ten measured runs per cell, ordinary decode90.15short/87.15long, and short prompt processing-1.93percent. All evidence pushedbb0f1292433d388c4ea9948d7c73c0d8a9dcb719. No full qualification or promotion. Entry checks find no live Strata/llama/profiler process, GPU457MiB/0percent, only the two known unrelated untracked files, and unusedQ014 output path.

Q014-coupled-quality config is byte-identical to R113/R114 (SHA2561e46c2180bec01c26573d8fcc194cf746f2f1f2ebd4bf64b7063fe748cbeb2e1); engine remains0dea69dc. One fresh process, fixed original five seeds101-105, no quality warmup, approved32768 completion allowance, unchanged topological_order fixture and72-case checker. Same numerical thinking profile, context262144, IQ3_S, INT8KV, compatible CPUF16vision, and full safety/identity guards. Coupled/Gumbel execution changes seeded streams but not the numerical sampling parameters; its finite distribution checks are not substituted for model quality.

Run the complete five answers once. Record every outcome and preserve Q0104/5 and all earlier failures. No retry-until-pass. A pass qualifies this coding check only; it does not clear short-prompt non-degradation, the missing full speed matrix or real-use gates. Failure prevents promotion. No engine code or production launcher change. Exact process cleanup and production configuration restoration are mandatory.


## E198 / prompt slowdown source audit, no causal fix yet

While Q014 runs, read-only source inspection narrows the1.93percent short-prompt regression theory. No build, profiler, process-memory polling, Git operation or second inference workload ran during generation. Repository has no.codegraph directory, so ordinary source search is used.

src/program/generate.cpp starts r0 at9147 before prompt-cache/session handling. It records prompt_ms at9985 after the input is read and lent expert slots are refilled, before the first generation window. The serial short-read window path at9573-9578 disables head sampling while consuming known prompt tokens. Therefore direct target Gumbel sampling in the first generation window is outside the prompt interval and is not itself an established explanation for reduced prompt_tps. The metric also includes session/cache handling and refill work; it is not a pure transformer-prefill kernel metric.

Existing STRATA_TRACE instrumentation reports individual read-part/window durations at9944-9948 and refill counts/duration at9656-9676. A later matched trace can separate these contributions without modifying the production code or redefining the benchmark timer. Possible mechanism: changed generated token histories alter adaptive expert residency before the next uncached prompt. This is a hypothesis, not a proven cause. CPU scheduling or other unmeasured effects remain possible.

Conditional next diagnosis if Q014 passes: use one bounded matched trace pair on original fixed short prompts, preserving warmup and request order, same512 output cap and numeric profile; add only STRATA_TRACE=1 to both arms, label all instrumented timing diagnostic, and preserve every output. Compare prompt read versus refill times and counts. Do not promote from tracing or run unchanged uninstrumented repetitions until the regression disappears. Do not suppress sampling/head work, alter sampler parameters or cache policy based only on this hypothesis. Full coding and real-use qualification remains required.


## E199 / Q014-coupled-quality approved expanded quality

Seed101: 7748tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed102: 14847tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed103: 16435tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed104: 7830tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed105: 12225tokens, finishstop, passed=False; original checker v1 raised NameError because TypeError was unavailable. Original stderr is retained in checks.json; the separate E200 evaluation corrects the checker environment.

Pass count4/5 with user-approved32768 cap. All five requests equal the originalQ007 requests except max_tokens. Configuration, executable, libraries, expert profile and vision hashes matchR113-coupled-stack; fixture hash matchesQ011. Natural-stop passing answers compile and pass72tests each. Zero prompt reuse. Legacy8192 failures remain unchanged. Variable-length quality answers do not satisfy the512-token speed target.

Minimum physical62226292736 and commit41426882560bytes;16GiB floors pass. Exact cleanup verified and production3457fdfe restored. No promotion; other workload, stability and real-use requirements remain.


## E200 / checker execution-environment defect: preserve original result, recheck all frozen answers

Q014 generated all five answers to natural stop:7748,14847,16435,7830,12225tokens. Original v1 checker reported4/5. Seed105 correctly raises ValueError for a missing endpoint inside a try with an except TypeError clause. In ordinary Python, the ValueError propagates because it is not a TypeError. The checker omitted the standard TypeError builtin, so evaluating the exception handler instead raised NameError. The task only prohibited imports; it did not prohibit built-in exception classes. This is an execution-environment defect, not evidence of an incorrect topological ordering.

Preserved check-topological.py and all original checks.json, stdout/stderr, answers, requests, cap failures and E1994/5. A regression against the frozen seed105 answer fails v1 with the exact NameError. New check-topological-v2.py differs by one addition to the allowed builtin list: TypeError. The AST restrictions,72 test cases, reference function, random seed904001, natural-stop requirement, timeout, expected exceptions, input immutability checks and score threshold are byte-identical. No imports/eval/open or other capabilities were enabled. Valid-answer regression passes v2; four deliberately incorrect/unsafe answers remain rejected. The same frozen answer passes all72 tests using ordinary Python builtins as a separate diagnostic.

Rechecked every stored answer in Q007-Q014 under v1 and v2, with ordinary-Python parity for naturally completed answers. No inference requests or new seed selection.36answers total; all v1 outcomes reproduced. Only Q014seed105 changes. Counts v1 to v2: Q0073/5 to3/5; Q0081/5 to1/5; Q0091/5 to1/5; Q0104/5 to4/5; Q0115/5 to5/5; Q0123/3 to3/3; Q0133/3 to3/3; Q0144/5 to5/5. All output-cap failures remain failures. Original and corrected records coexist with checker/answer hashes and per-answer stdout/stderr.

Q014's five frozen final functions were reviewed as coherent topological-order implementations and each passes the unchanged72-case objective suite under corrected standard exception semantics. This qualifies only the completed-answer coding gate for C054, not universal quality or the full goal. Numeric thinking sampler, prompts, seeds,512speed requests and approved32768quality allowance unchanged. Future quality runs must use v2 consistently for controls and candidates, retaining the checker hash. This repairs evaluation fidelity; it does not lower the quality standard. Short-prompt slowdown and the missing real-use/speed cells remain open. Exact cleanup passed; no benchmark model resident at this checkpoint.


## E201 / paired prompt tracing, diagnostic only

After Q014 coding answers pass the unchanged objective cases under the corrected Python exception environment, investigate C054's measured short-prompt slowdown. P021-prompt-trace-control copies R112 and P022-prompt-trace-coupled copies R113; the sole addition to each is STRATA_TRACE=1. Full original TTLCache benchmark is retained to avoid changing its client: short then longer, one warmup and five measured requests each, seeds101-105,512tokens, numeric profile unchanged. This includes the planned short-prompt trace plus the corresponding longer workload. One fresh process per arm and one pair only. Both output paths were unused at preparation.

Trace code already exists in the verified engine; no source/build change. Read-part/window and refill timing lines will localize prompt interval costs. All timings from these arms are instrumented diagnostic results, not extra qualifying repetitions, and must not be pooled into R112-R115 or used to hide the prior1.93percent loss. Preserve cache-hit counts, every slow seed, generated output and original server/client metrics. Compare same request indices and explicitly disclose that preceding generated tokens and adaptive cache state can differ.

Guarded supervisor remains active: exact identity,16GiB physical/commit floors, one model tree, no process-memory polling during requests, mandatory cleanup and configuration restoration. Q014 natural-stop outputs are frozen and are not regenerated. Production launcher remains unchanged. Next: inspect trace decomposition, then act on an evidenced bottleneck or proceed to missing workload gates; do not invent a causal fix from aggregate noise.


## E202 / P021-prompt-trace-control

Same engine and loaded library hashes as R112-coupled-stack-control. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.8 (86.4-96.2) | 212.8 | 78.0714 | 78.0858 | 0.8112 | 819/1088 (75.28%) |
| longer | 88.1 (86.6-90.4) | 495.2 | 42.8422 | 42.8464 | 6.1617 | 947/1278 (74.10%) |

Minimum available physical RAM 62,440,603,648 bytes; available commit 41,681,256,448 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Instrumented prompt-stage diagnostic with STRATA_TRACE=1. These timing rows are not qualifying speed repetitions and cannot be pooled into C054 ABBA. Read/refill decomposition pending matched P022; no promotion.

Next: Run P022 matched coupled trace once, then compare prompt-stage timings and counts.


## E203 / P022-prompt-trace-coupled

Same engine and loaded library hashes as R113-coupled-stack. Config diff is archived. Fixed numeric sampling, high/xhigh reasoning, model/quant, vision, context262144 and INT8KV retained. Original TTLCache streaming cache-miss workloads; one excluded warmup and five measured seeds101-105 per cell,512tokens per measured run. No slow seed excluded.

| Workload | Decode median (range), tok/s | Prompt median, tok/s | E2E median, tok/s | Stream total median, tok/s | TTFT median, s | Draft accepted/offered |
|---|---:|---:|---:|---:|---:|---:|
| short | 88.9 (87.1-91.0) | 209.7 | 77.8145 | 77.8260 | 0.8436 | 833/1074 (77.56%) |
| longer | 87.6 (80.8-88.5) | 495.5 | 42.6936 | 42.6977 | 6.1602 | 1024/1291 (79.32%) |

Minimum available physical RAM 62,161,031,168 bytes; available commit 40,959,152,128 bytes. Sampled GPU peak 25,128,013,824 bytes. Both16GiB host floors passed. Per-process peak memory not sampled. Full launcher/server/text/vision cleanup passed and previous config restored.

Matched instrumented prompt-stage diagnostic complete. STRATA_TRACE=1 timings are excluded from qualifying medians. Q014 corrected v2 coding quality5/5, original v1 failure preserved; full goal remains unqualified.

Next: Analyze both traces stage by stage; keep C054 speed medians and observed prompt regression unchanged.


## E204 / prompt trace localization and current qualification checkpoint

One instrumented matched pairP021/P022 completed, each original short/longer workloads with one warmup+five measured seeds,512tokens, fixed numeric sampler, exact model/context/vision and same C051 engine. Each differs from its corresponding C054 arm only by STRATA_TRACE=1; request bytes match. Parser validates12 request boundaries, all prompt-token counts and read-token totals, no cache reuse and512completion tokens. Trace timing is diagnostic only, excluded from qualifying C054 medians.

| Workload | Arm | Prompt total ms | Batched read ms | Tail windows ms | Refill ms | Refilled slots | Other prompt ms |
|---|---|---:|---:|---:|---:|---:|---:|
| short | P021 | 775.4 | 594.8 | 45.1 | 99.0 | 311 | 38.3 |
| longer | P021 | 6124.8 | 5622.4 | 44.7 | 419.1 | 1318 | 38.2 |
| short | P022 | 801.0 | 609.5 | 50.8 | 99.0 | 311 | 38.4 |
| longer | P022 | 6123.1 | 5618.4 | 46.8 | 419.2 | 1318 | 38.2 |

Medians of separate stages need not sum to the median total. Other time is computed per request after subtracting traced read/refill/lend durations; it includes checkpoint/session work and timing/trace overhead, not an attributed bottleneck. Short candidate batched-read median is14.7ms higher and tail-window median5.7ms higher; refill is99.0ms for both with311slots. Longer refill419.1/419.2ms and1318slots is essentially unchanged. This localizes the observed difference to computation rather than more refill bytes; it does not prove cache composition, CPU sharing or Gumbel as the cause. Prompt throughput212.8control/209.7candidate also differs in this instrumented pair, but these values cannot replace the original209.35/205.30 or erase the measured1.93percent loss.

Code investigation: generate.cpp request_chunk rounds each prompt buffer capacity up to256tokens, and lend uses Prefill::bytes_needed for that capacity. Current short main reads160-163tokens while borrowing buffers for256; the four-token tail uses verifier windows. A bounded next feasibility check is to calculate the exact scratch/loan reduction for a smaller short-request capacity and audit all alignment/relayout/kernel requirements. Do not assume it is safe or faster: capacity may affect kernel layout or routing placement. Keep defaults byte-identical, require an opt-in if implemented, and retain the full quality/speed contract. This is a new structural hypothesis motivated by measured work, not a rerun of C054 until favorable. No C055 engine code, build or speed arm exists yet.

Q014 corrected coding gate5/5 is supported by frozen-output tests, standard-Python diagnostic parity, and the one-builtin TypeError repair. Original v1 score4/5 is preserved alongside v2; all36 stored answers were rechecked and only Q014seed105 changes. Legacy cap failures remain failures. Future quality client goal90-quality-expanded-v2.py is a separately versioned copy selecting the v2 checker, recording its hash, saving its source and asserting it cannot change during a run. Private supervisor adds explicit --goal-quality-expanded-v2 with the same7200s timeout and memory/cleanup guards. Original clients/checker remain available unchanged. New helper syntax checks pass; no additional model generation for this correction.

The goal remains unqualified: C054 numeric original streaming-miss medians90.15/87.15 meet90/85, but short-prompt non-degradation is unproven; selected-coding speed, nonstream/cache-hit confirmations and real-use gates remain missing for this combination. No source or launcher promotion. P021/P022 exact trees cleaned up, production config3457fdfe restored, idleGPU457MiB/0percent. Both16GiB physical/commit floors passed. Next: quantify short-buffer opportunity before implementation, then test only an evidence-backed change or complete missing workload gates; never waive the prompt-loss condition.
