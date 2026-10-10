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
