# C038: share Q8_1 activation across concurrent expert branches

Fixed production contract unchanged. This is an offline eligibility/parity/timing
screen, not a TPS benchmark or production change. The user authorized autonomous
optimization and bounded throwaway probes.

Current verify.cpp publishes the CPU doorbell, forks the shared expert stream,
then independently quantizes the same activation on both branches. Existing
STRATA_VERIFY_QDEDUP excludes sh_fork. Proposed scheduling: quantize once on the
main stream after the doorbell, then record the existing fork event and let both
branches read the same immutable buffer. Shared hidden-state quantization must
still use its separate scratch; join before reuse remains mandatory. QFUSE,
single-token self-commit, routing, cache policy and all arithmetic stay unchanged.

Before any engine edit, compare the two existing quantizers byte for byte for
T=1..8 and bounded finite random/zero/sign-changing inputs. Test a captured
two-stream DAG with actual model shared gate/up weights and identical GEMV
consumers, separate outputs and post-join bitwise comparisons. The routed-side
consumer is a representative dense GEMV, not the whole routed expert pipeline;
timing establishes only local scheduling feasibility.

One excluded warmup and seven alternating rounds of 100 DAGs per graph per cell.
Require every parity check, >=5% geometric mean time reduction, and no cell >3%
slower. One timing process only; failure closes this hypothesis without a served
launch. Success permits an opt-in engine prototype plus integrated correctness
and fresh served controls, not launcher promotion. Fixed allocations <128 MiB;
one global headroom snapshot, no model loaded. Preserve raw results and clean up.

Prefetch eligibility review: existing Foresight admits via cudaEventQuery and
requires extra per-layer slots. docs/DETAILS.md reports regressions on several
cards including dual RTX3090. It is not selected: no new mechanism distinguishes
it from that negative evidence and its timing-dependent residency complicates
reproducibility. C037 already ruled out useful copy-loop arithmetic savings.
