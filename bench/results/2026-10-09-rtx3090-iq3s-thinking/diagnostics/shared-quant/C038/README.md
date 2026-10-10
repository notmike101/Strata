# C038: shared quantization buffer rejected on byte parity

The offline experiment tested eliminating duplicate activation quantization while
retaining the concurrent routed/shared expert branches. Production currently
calls `quantize_q8_1_rows` for routed experts and `native_quantize_q8_1` for shared
experts. Existing STRATA_VERIFY_QDEDUP is disabled when the shared stream forks.
The proposed candidate quantized once before the existing fork event and let
both branches read that immutable image; separate outputs and the join remained.
No engine, launcher, sampler, model, context or quality-gate change was made.

This was a CUDA13.3.73/sm86 offline DAG screen with actual gate/up weights from
model layers0,23,47 (Q4_K/IQ4_XS, Q5_K/Q5_K, Q4_K/Q5_K), N2560/M640,
T1..8, and zero / bounded random inputs at scales.001,1,100. The two branch
consumers were dense GEMVs, not the complete routed/shared expert pipeline.
Each timing graph held100 DAGs; one excluded warmup plus seven alternating
measured rounds. All raw results and sources are attached. Actual weight bytes
and executables remain private; manifest retains names, sizes and hashes.

The screen passed21 parity cases then stopped with exit4 at layer0/T6/scale.001.
Five completed timing cells are retained as partial, disqualified evidence:
candidate/control ratios.846774,.860435,.890000,.920574,.842430.
These are kernel-DAG timing ratios, not served TPS; they cannot qualify a winner.

A separate correctness-only diagnostic used the exact same deterministic input
sequence and ran both quantizers sequentially on one stream. It found3 mismatching
cases out of96, each one quantized int8 byte:

| Layer | T | Input scale | Byte offset | Routed signed byte | Shared signed byte |
|---:|---:|---:|---:|---:|---:|
| 0 | 6 | .001 | 14433 | -86 | -87 |
| 23 | 8 | 1 | 5435 | -124 | -125 |
| 47 | 4 | 100 | 1791 | 68 | 69 |

Hexadecimal input floats for all three32-value counterexample blocks are saved
in C038-diagnostic.txt. Sequential reproduction rules out stream ordering as the
cause of these mismatches. Build metadata shows --use_fast_math on native_mmvq.cu
but not iq_kernels.cu; both source paths use xi/d and roundf. A division-rounding
difference is consistent with this evidence, but not yet instruction-level proven.
Do not fix this by forcing one quantizer onto both branches: that would change
the baseline arithmetic. Current production does not enable QDEDUP; this is not
evidence of a newly introduced production regression.

The original all-parity gate failed, so the shared-buffer hypothesis is closed.
There was no second timing attempt, integrated build, or served benchmark.
Next distinct mechanism: investigate a dual-output quantization kernel that reads
the input once but preserves both original arithmetic paths and writes separate
byte images. Require these exact counterexamples and broader parity checks before
any timing or integration. Potential DAG savings do not establish a TPS gain.

Prefetch review also closed the existing Foresight path as an experiment choice:
docs/DETAILS.md1447-1456 reports lower medians on several cards and the same result
on dual RTX3090. The implementation admits copies via cudaEventQuery, allocates
extra slots at the expert cache's expense, and adds timing-dependent residency.
No distinct new mechanism justified repeating that path on this host.

The host headroom snapshot exceeded both16GiB floors. Fixed prototype allocations
were below128MiB; memory was not continuously sampled. Both executables exited;
no model was loaded. Cleanup verified no live Strata process and457MiB idle GPU
memory. Production config and executable hashes match the retained baseline.
The90 TPS goal remains active; no new served result or quality qualification.
