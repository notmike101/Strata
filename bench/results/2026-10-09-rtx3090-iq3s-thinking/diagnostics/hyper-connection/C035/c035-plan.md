# C035: bounded lossless HC storage feasibility

Question: can the current model's packed BF16 hyper-connection coefficients be
reconstructed bit for bit from smaller existing Q8_0 source blocks while keeping
the present accumulation tree? Exact model remains GSQ-RCO IQ3_S; no substitution.

Budget and gates, written before inspection of all tensor metadata:
1. One inventory of every HC projection and normalization tensor in both actual
   model shards; resolve each against the current pack index.
2. One full coefficient parity pass for existing source representation versus
   packed representation. If Q8_0 projections exist, independently reconstruct
   their FP32 values and round to BF16 with round-to-nearest-even. Every coefficient
   must match, including zero sign. If the needed Q8 source does not exist, reject
   this hypothesis as inapplicable; do not manufacture a lossy replacement.
3. Only after exact coefficient parity and source eligibility: one CUDA graph
   microbenchmark, T1..8, pending-write and injection on/off, one excluded warmup
   and seven alternating timing rounds. Preserve the old accumulation tree.
   Require bitwise output equality and at least5% lower median HC time for T1,
   with no greater than2% loss at T2..5, before considering integration.

No production source, launcher, sampling, context, quant, vision or memory change.
No server launch during this screen. STRATA_HC_Q8 stays disabled because it changes
weights and reduction order. Reuse existing P009 profiling evidence; no new trace.
Maintain original16GiB physical and commit headroom floors. One failure closes the
screen with evidence, not a repeat. An offline gain is not served TPS or goal proof.
