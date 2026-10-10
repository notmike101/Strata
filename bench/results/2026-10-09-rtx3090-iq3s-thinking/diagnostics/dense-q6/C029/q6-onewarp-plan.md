# C029: one physical warp per Q6_K row, exact virtual partials

Question: does replacing a four-warp CTA per Q6_K output row with one physical warp
per row remove enough shared-memory/barrier cost to improve the profiled dense
projections? C028's multiple rows per four-warp CTA lost every dense shape, so
register-interleaving more output rows is closed. This tests a different mapping.

The original kernel assigns Q6 blocks modulo four to four warp accumulators, then
adds warp 1, 2 and 3 into warp 0 in that order before its XOR reduction. The candidate
keeps four independent scalar accumulators per lane, the same per-accumulator block
sequence, original Q6/Q8 dot helpers, ordered final additions and XOR reduction.
One physical warp computes the row without a CTA barrier or shared scratch. Test
2, 4 and 8 independent warps/rows per CTA; row guards must exclude complete warps.
Extra registers, serial work per lane and less memory parallelism may outweigh
the removed synchronization. No bitwise mismatch is acceptable.

Use a standalone CUDA diagnostic, unchanged native reference from the C022 control
library, and extracted original dot/reduction helpers. Record the reference library
and source hashes. First run an intentionally zero-output stub to verify the actual
weight test catches wrong output. Then implement the candidate and require parity
on six actual dense tensors, eight activation patterns, odd and full row counts,
finite values and output canaries. Keep the CUDA 13.4 compiler/math flags matched.

Time exactly as C028: one excluded warmup, eleven alternating order rounds, graph
of 64 identical projections, CUDA-event durations. Save every row. Microbenchmark
time is not server decode or client TPS. No production source/config change yet.
Any winner requires integrated-source verification, default-path preservation,
same-day served control/candidate repeats and the complete fixed quality/workload
matrix before promotion. Sampling, model/quant, context, memory floor and quality
requirements remain unchanged. No benchmark model is left resident.
