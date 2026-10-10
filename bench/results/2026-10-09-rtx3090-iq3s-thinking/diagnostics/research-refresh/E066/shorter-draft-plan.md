# R047 control / R048 two-token MTP limit

Previous goal turn made progress: E063 corrected preflight defects, R045 measured
and rejected resident-copy storage, and R046 proved the existing rotation path
cannot activate. The retained full-arena configuration remains the control.

2026-10-09 research refresh found main fb58e0dbc8399662c0e47c76578c6e878b14f6cf
and release v0.1.41 unchanged. Open PRs1742/1744 optimize SM86 prefill, not decode.
PR1737 speeds an approximate routing mode with measured distribution/quality
distortion, so it is excluded. PR1741 addresses a two-GPU pipelined wait loop;
the current one-GPU path does not use that service loop. PR1544's singleton
optimization does not execute with retained STRATA_IQ_MT_MIN=1. PR1548 learns a
PCIe fraction from runtime costs; its own report remained below a tuned fixed
fraction and does not establish an improvement over this machine's fixed0.20.
These are unmerged proposals, not a newer release to install. Their external
numbers use different hardware/workloads and are not local speed evidence.

P009's incomplete node trace still identifies wait_flag_ge_kernel, target Q6_K
matrix-vector work and expert fetch/down kernels among the collected costs.
Do not treat those percentages as complete critical-path fractions. P005's
host timing independently showed CPU expert service and GPU-reach wait per
verification window. Six-token MTP in R041 lost speed; two-token MTP has not
been measured in the ledger. The new question is whether shorter draft windows
reduce discarded verification work more than they lose amortization and reuse.

R047 repeats the retained R037 configuration unchanged, with current guards and
observer audit-no-process. R048 changes only --spec4 to --spec2. Existing suffix
policy therefore allows up to four rows instead of six; this is an intrinsic
consequence of the single flag, not a separate hidden setting. Target sampling
and all model weights are untouched. Plain exact-match verification remains in
use, with the target deciding every emitted token. This does not by itself prove
numerical invariance across window shapes or completed-answer quality.

Each arm: fresh process, one excluded warmup and five measured seeds101-105 in
both original short/~3K streaming cache-miss cells,512generated tokens, context
262144, INT8KV/32768GPU cells, CPUF16vision, xhigh, fixed coding sampler,
concurrency1, MTP confidence floor0.70, PCIe fraction0.20 and lag2. Same-order
control/candidate gives the same workload order and expert-cache history policy.
Every run stays in the ordinary median; record all decode/client/prompt metrics,
draft counts, identity, effective sampling env and16GiB physical/commit floors.
Stop the complete process tree after each arm and restore the retained config.

A loser is rejected. A possible winner requires opposite-order repetitions and
the entire frozen random-coding, natural-stop, capability and memory matrix.
No production change follows from a single pair. If tied or losing, use the
captured window/draft counters to decide whether a deeper scheduling change is
justified; do not tune sample parameters or replace the quality gate.
