# Exact CPU expert expansion implementation plan

> For agentic workers: use superpowers:executing-plans inline, task by task, in the existing working branch.

**Goal:** Test whether spending bounded spare RAM on decoded expert codebooks can reduce the native CPU expert critical path without changing any arithmetic or model precision.

**Architecture:** First build an isolated AVX2 probe, using the existing synthetic quantized-expert fixture and actual native row functions as the oracle. Expand each256-value IQ3_XXS,IQ3_S orIQ2_S gate/up block into signed codebook bytes,16 byte scales and the same float block multiplier. Keep the sign operation on activations, original integer lanes, FMA order and reduction. Do not load an expanded cache into the production server until parity, single-core and nine-worker DRAM-streaming measurements justify the additional memory.

**Tech stack:** MSVC17.14, AVX2/FMA, existing ggml and Strata CPU libraries. CPU diagnostic only; no changed CUDA/HIP/SYCL source.

**Spec:** [goal-90-contract.md](goal-90-contract.md). All target sampling, context, quality, memory and real-use constraints remain in force. A kernel speedup alone does not qualify.

## Review focus

- Activation byte-128: reconstruct magnitude and sign separately; moving signs into a signed multiply changes wrapping behavior.
- Zero codebook entries: differing reconstructed sign is harmless only when magnitude is zero; test every encoded block pattern supplied by the fixture.
- Scales, non-finite outputs and tails: preserve float multiplication/FMA order; reject unsupported geometry. Test positive,negative,zero scales and1-8token widths.
- DRAM bandwidth and cache pressure: expanded blocks are288B versus98/110/82B; a hot-L3-only test is insufficient.
- Integration ownership: any eventual bounded cache must outlive all worker jobs, preserve native fallbacks, account for RAM before allocation and avoid new synchronization on misses.

## C015: isolated representation and kernel

Files under the private campaign working directory: cpu-expanded-screen.cpp(test/benchmark),cpu-expanded-kernel.inl(prototype),build-cpu-expanded.cmd(reproducible build). Publish successful or rejected final source and all result files into this report; no production source change in this stage.

- [x] Write a parity test using the existing native synthetic-weight generator and quantized activations; exercise three formats and1-8token widths, normal and extreme activation patterns. Observe the unimplemented candidate fail against native outputs.
- [x] Implement block expansion and a row kernel retaining native integer lanes/FMA order. Compare every gate/up output bit, including SiLU/multiply. Require all cases pass before timing.
- [x] Run five alternating paired native/expanded timings for1/2/3/4tokens with an expert set larger than L3. Retain all samples and preprocessing time/memory. No simultaneous model workload.
- [x] If gains justify integration, repeat with nine workers and representative job sizes as C016 before modifying the engine. Otherwise reject the path.
- [x] Record outcome, update durable next actions and push the evidence on perf/rtx3090-thinking-80. Preserve existing launcher.

## C016: unchanged nine-worker pool with a diagnostic gate/up hook

Create cpu-expanded-pool.cpp and build-cpu-expanded-pool.cmd. Include the existing ExpertPool implementation unchanged in the diagnostic translation unit, substituting only the call to native_gu_rows with an explicitly selected native/expanded wrapper. The wrapper indexes immutable expanded blobs by their original expert pointer; no concurrent cache insertion or allocation. Both paths still use original intermediate quantization,IQ4_NL down rows and scheduling.

- [x] Add a range-kernel parity test through the complete pool: nine workers,30tasks,three formats,1/2/4tokens and1/3/6expert jobs. Observe an unimplemented range writer fail bitwise output parity before implementing it.
- [x] Implement the same expanded row arithmetic for ranges; require complete-expert outputs match at every tested shape.
- [x] Run five alternating paired samples per shape, over a native expert pool larger than L3, with identical affinity and fixed iteration count. Report native and expanded bytes separately and keep all results.
- [x] Only plan engine integration if the complete pool preserves a useful speed advantage. Integration must additionally measure real route hit rate and total RAM; static full expansion is not assumed to fit.

## C017/C018: compact exact nibble representation

Ruling after C016: reject the288B layout for integration;24/27 complete-pool cells regress. Test an alternative138B block before abandoning predecode entirely. The IQ3_S grid has eight magnitudes1,3,...,15; IQ3_XXS has4,12,20,28,36,44,52,62; IQ2_S has8,25,43. A four-bit code therefore represents the original magnitude plus sign exactly for each format. Store256codes in128bytes, the original16-bit block scale, and sixteen four-bit subscale indices in8bytes. No requantization. AVX2 pshufb reconstructs the same signed bytes; preserve sign-on-activation and integer/FMA order.

- [x] C017 parity test first: reuse the independent native oracle; unimplemented output failed640/640 first-case values.
- [x] Implement and pass all48 single-core parity cases; run the same five-pair DRAM benchmark.
- [x] If warranted, repeat the unchanged nine-worker complete-expert C016 matrix as C018 using compact blocks. Require parity and useful gains before any engine/cache integration.
- [x] Publish both losing full-byte and compact alternatives with raw timings; never substitute these kernel rates for served TPS.


## Outcomes and bounded integration plan (C020)

C015 passed parity but its 288-byte representation lost in 24/27 complete-pool C016 cells. Rejected. C017 compact138-byte representation passed48 parity cases; C018 passed27 complete-pool cases. Only IQ3_S consistently improved all nine measured pool shapes (1.21-1.33x). C019 then passed210 actual-weight cases across all ten IQ3_S layers, three sampled experts and seven token widths, including both down formats. These are diagnostic gains, not served throughput.

Integration is scoped to IQ3_S gate/up on AVX2 CPUs using the existing AVX2 arithmetic. Other formats and dispatch modes fall back. Add an explicit immutable cache pointer to ExpertJobMulti; ArenaExpertSource owns and clears storage before its original arena. No process-global pointer registry, asynchronous insertion, request-time allocation, or GPU tensor change. Prefill keeps its current path initially. This also avoids affecting transient/file-backed expert sources.

- [ ] Add production cache interface plus failing tests for disabled/budget/geometry/lifecycle and full-pool bitwise parity, then implement.
- [ ] Require an explicit STRATA_CPU_IQ3S_CACHE_GIB budget; no allocation by default. Validate checked byte arithmetic, physical and commit headroom (at least16GiB), CPU ISA and supported layout before allocating. Build all-or-nothing and report allocation/time or fallback reason. Current exact model requires8.4228515625GiB extra. Cache setup precedes readiness.
- [ ] Preserve all original quantization/down operations and native fallback. Test unsupported formats, cleared/reopened storage, different source instances and NT1-8/ranges. Default source and job pointers stay null.
- [ ] Build CUDA and available CPU tests. HIP/SYCL toolchains are unavailable on this host; do not claim those builds or request upstream review.
- [ ] Run same-day full-model control/candidate with fixed sampler/context/prompts, all samples, startup/RAM telemetry and prompt processing. Reject if gains do not transfer or any quality/stability/memory/prompt gate regresses. Only then extend full qualification matrix.
- [ ] Publish source, commands, binary hashes, failures and results on the current branch. Preserve production launcher until qualification. Stop all benchmark models.


C020 disposition: implementation, memory/ISA/lifecycle unit checks, CPU/CUDA builds, independent review and two-order served comparisons completed(E047/E048). Not promoted. Full source retained as diagnostics/cpu-cache/C020-rejected.patch; active source restored. Actual ArenaExpertSource reopen and extended serving qualification intentionally remain uncompleted for this rejected candidate. The microbenchmark gain did not transfer to a repeatable90tok/s server result.
