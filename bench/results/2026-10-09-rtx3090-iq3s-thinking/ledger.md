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
