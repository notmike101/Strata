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
