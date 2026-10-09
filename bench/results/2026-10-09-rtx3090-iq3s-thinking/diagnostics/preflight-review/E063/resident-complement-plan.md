# R045: resident RAM complement, retained exact-match sampler

2026-10-09. New memory-layout hypothesis after compiler, head-layout and speculative-mode trials failed to establish90tok/s. No production source edit. Only the existing --resident-experts flag is added to the retained R037 configuration; no rejection/Gumbel flags or altered confidence threshold are carried over.

Current mode pins the full46.84GiB expert arena in host RAM while keeping about15.95GiB of those weights duplicated in GPU cache. The resident-complement path keeps the experts absent from GPU in host RAM and exchanges exact expert bytes when cache residency changes. It can reduce pinned footprint and address working set, but adds copy-back/exchange work. It may be slower; this is an unproven memory-layout experiment, not a low-precision model change or a RAM-fit requirement.

Read source src/program/generate.cpp resident setup and docs/DETAILS.md resident mode plus docs/EXCHANGE_ROTATION.md. The initial trial keeps blocking adaptation and the original lag2 policy. Do not enable --adapt-async1: docs explicitly say GPU-versus-CPU admission becomes timing-dependent and loses run-to-run bit-exactness. Rotation is a separate potential candidate after the base complement is measured; do not combine it here.

Before the model trial, run existing exchange_storage_test and file_expert_source_test, including the explicit --rotation-gpu fixture if available, with the retained CUDA13.3 toolchain/runtime. This checks exact byte ownership, mapped aliases, copy/fallback behavior, close/reopen and exchange lifetimes. Do not compile while a benchmark model is resident.

R045 must show 'resident RAM mode' with page-locked storage and expected GPU cache counts in startup. Require the prompt-borrowed experts to fit RAM, report file fallback counters, and reject an unannounced fallback instead of treating it as the planned mode. Keep one excluded warmup and five512-token measured requests in each original short/~3K cell. All target sampling and xhigh parameters, model/quant,262144context,INT8KV,CPUF16vision,concurrency1 and PCIe.20 remain unchanged. Physical and available commit floors remain16GiB. Capture the actual memory reduction and all speed/latency metrics. Full process-tree cleanup is mandatory.

A loss is rejected. A gain only queues repeated controls and the unchanged random-coding/quality/real-use matrix. No launcher promotion occurs here.
