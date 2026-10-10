## E160 / C050 down-only compiler gate rejected; P020 evidence published

Previous turn answering the metric question changed no optimization state; this
continuation revalidated the pending build rather than restarting it. Both fresh
C050 executables existed, compiler processes were absent, and the full build log
ended after successful links. No engine source edits were made.

C050 compares identical current IQ4_NL down code compiled by MSVC19.44 versus
Clang19.1.5, AVX2, precise math, explicit FMA preserved, Clang contraction off.
GU, activation quantization and other down formats use the same current library.
All576 actual-weight complete-pool cases passed bitwise and finite-output checks:
48layers x experts0/173/511 x T1/2/4/8. This is sampled kernel parity, not full
model quality or a served TPS measurement.

Timing used the predeclared predicate down_type20 AND (layer%5==0 OR layer47).
Eight layers qualify:0,5,15,25,35,40,45,47. Layers10,20,30 have another down type
and were excluded by the predicate, not by their measured speed. Thus96cells,
960 measured values (5 alternating pairs each), plus192 warmup values. Each
value averages100 complete-pool calls across64actual experts/layer. T1/2/4/8,
jobs1/3/6,9workers+host0,30tasks. All timings, including slow cells, are retained.

Geometric mean of Clang/MSVC per-cell ordinary-median time ratios:
0.992158989 (0.7841% lower time). Worst ratio1.180074938 (18.0075% slower);
18/96cells slower,3/96over3% slower. The required>=5% aggregate time reduction
AND no cell>3% slower both fail. Reject and close this compiler path; no cherry-
picked subset, extra confirmation, engine integration, server run or promotion.
This does not imply a0.78% served throughput improvement.

Independent global memory guard passed every second. Minimum available physical
119752142848bytes and commit124670394368bytes,
both above16GiB. Exact child exit/cleanup recorded. No model server launched.
Executable hashes and source/build commands accompany all raw results.

Process-inventory correction: CIM again listed the same five old Python PIDs
30352/134612/90924/70108/273856 from the prior E050 investigation. No8080 listener
or model engine was present and GPU memory was457MiB. E050 had already proved
these were exited process objects; the initial commentary calling them wrappers
needed that distinction. Terminate returned0 for those exact validated records;
psutil's live inventory contained only the current diagnostic Python processes.
No evidence of five running models, GPU competition, or a new throughput loss.

P020 allowlisted trace audits, timing statistics, request evidence, safety logs
and scripts are published alongside this result. Raw Nsight/SQLite files stay
private. Trace consistency is not completeness, overlap sums are not removable
latency, and instrumented72.9decode is not a qualifying arm.

Upstream refreshed at2026-10-10 approximately07:07UTC using the bot helper:
main stillfb58e0dbc8399662c0e47c76578c6e878b14f6cf, releasev0.1.41 unchanged.
No stable update to apply. Fresh broader review:
- PR1813 adf979544232c18e6d90b27adf41a5ed4e9b5afe adds exact greedy-window tests,
  not a runtime optimization. Useful test design, not sampled-profile proof.
- PR1713 432702961faba67ae5325444a328ebc6fcde9f26 splits the SYCL verify graph
  around CPU service and pipelines a helper. CUDA is untested upstream. This is
  a distinct scheduling architecture worth examining against the current CUDA
  mapped-buffer/coherence and overlap design; Arc measurements do not transfer.
- PR1426 73b3db6b688f059350d1812ed67efc85bfbbdb30 DFlash currently falls back to
  target-only for sampled requests and loses to MTP in its reported greedy test.
  Not a drop-in candidate under this fixed sampling contract.

Next: examine the CUDA CPU-service/GPU-consumer dependency path and the stepped
verify architecture. Before implementing, establish whether a bounded opt-in
prototype could remove a measured cost without losing current overlap; abandon
it if that mechanism is absent. Do not retry the three closed compiler paths.
Production launcher, context262144, vision and sampling remain unchanged. Goal
active:90short/85long and complete quality/workload matrix still unqualified.
