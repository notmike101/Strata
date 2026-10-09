# Goal90 research and alternatives

Accessed 2026-10-09. GitHub reads and the release download used the configured bot identity helper. External results motivate tests; none establish a local gain.

| Source | Finding and applicability | Status / next measurement |
| --- | --- | --- |
| [Strata release v0.1.41](https://github.com/Niko1221/Strata/releases/tag/v0.1.41) | Fresh fetch still gives upstream fb58e0db; no newer release to apply. | Verified at goal resumption. |
| [PR1741](https://github.com/Niko1221/Strata/pull/1741) | Avoids repeated device switches in the multi-GPU pipelined service loop. This single-GPU run uses Verifier::run, not that loop. | Not applied; different execution path. |
| [PR1742](https://github.com/Niko1221/Strata/pull/1742) | CUDA SM86 fused-prefill weight-prefetch specialization, Linux RTX3060 measurements. | Unverified locally; prefill-only lead, not a decode fix. |
| [PR1744](https://github.com/Niko1221/Strata/pull/1744) | CUDA SM86 selective two-stage IQ3 fused prefill, Linux RTX3060 measurements. | Unverified locally; do not assume gains transfer to3090. |
| [PR1668](https://github.com/Niko1221/Strata/pull/1668) | Route-tail omission and routing-prior changes explicitly alter outputs. | Excluded by fixed quality contract. |
| [Nsight analysis guide](https://docs.nvidia.com/nsight-systems/AnalysisGuide/index.html) and installed2026.1.3 CLI help | WDDM memory traces expose allocations/migrations but require administrator privileges. Whole-graph CUDA tracing omits per-node activity to reduce overhead. | P006, P007 whole-graph and P008 single-request traces all lost records; none supports whole-run attribution. No elevation or OS setting change. |
| [llama.cpp b11538](https://github.com/ggml-org/llama.cpp/releases/tag/b11538) | Current portable Windows Vulkan binary available. Local llama.cpp source contains Qwen4Exp inference and conversion support; its converter marks MTP export unsupported. Exact runtime/model/feature compatibility still needs testing. | V001 loaded the exact model/context/CPU vision; V002 measured 8.876 median short raw decode tok/s (three runs, no MTP) and was rejected. This is one placement, not an exhaustive Vulkan ceiling. SHA256621ec0ed653ec9d40673be866558d2675eb54907ee4255ecfeb2739f2a6dccf5 matches release digest. Existing llama.cpp installations unchanged. |

Native exact-layout alternative: `native_q6_k_pack` already implements a bitwise-checked packed Q6_K output head and paired timing self-test. The main head is loaded before automatic expert-cache sizing, while the MTP draft copy is later. Extra VRAM must therefore be explicitly accounted for before any full-model experiment. C014 tested actual output-head weights in isolation: bitwise equal but 4-64% slower at the measured widths and 497.3 MiB larger; rejected. A microbenchmark cannot establish a served gain or complete the goal.

The existing CPU scheduling, prefetch, SMT, adaptive-cache and interleaved-row experiments remain rejected as recorded in E021-E036. They are not restarted without new evidence.

Follow-up: P007 whole-graph and P008 one-request/1000ms-flush traces also dropped records. [Current Nsight release notes](https://docs.nvidia.com/nsight-systems/ReleaseNotes/index.html) document a multi-stream/multi-thread buffer-release limitation with this diagnostic and the need for spare GPU memory. Both are hypotheses, not established local causes. Accessed2026-10-09.
