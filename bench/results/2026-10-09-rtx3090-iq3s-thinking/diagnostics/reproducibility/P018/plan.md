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
