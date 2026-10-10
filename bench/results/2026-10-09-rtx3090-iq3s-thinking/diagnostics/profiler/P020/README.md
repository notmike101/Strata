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


Raw trace files stay private; selected audits and timing summaries are included.
