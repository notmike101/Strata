# R041: six-token MTP windows

2026-10-09, current branch; existing engine flag, no production code edit.

Use the retained engine/library stack and R037 control configuration. Change only --spec4 to --spec6. Preserve the target sampler, reasoning, model, quant,262144context,INT8KV,32768resident,CPUF16vision,PCIe.20,min-draft-probability.70 and adaptive lag2. Do not carry coupled/Gumbel flags from R040.

Hypothesis: more accepted draft tokens per target verification could amortize the CPU expert and GPU weight-read costs. Counter-risk: later drafts cost more than the accepted prefix saves, and extra verification buffers reduce VRAM headroom. The source applies the same exact-match target-sample acceptance rule independently at every row. It never emits unverified guesses. The existing GPU multi-token parity tests cover widths through8, but whole-model numerical dispatch may still vary by grouping/cache placement; full coding and capability gates remain mandatory before promotion.

src/program/generate.cpp adds two suffix positions to the MTP cap when suffix drafting is enabled. This trial therefore permits six MTP positions and eight total verification rows, versus four/six in the control. Record startup buffers and peak GPU memory. Stop on allocation failure or either host16GiB floor; do not shrink context or change precision to fit the candidate.

Measure original short/~3K streaming cache misses, five512token runs and one excluded warmup per cell, longer-first to complement R037's short-first control. Keep every seed. Collect MTP accepted/offered, prompt rates, TTFT, E2E and stream rates, memory and complete cleanup proof. A win only queues a repeated pair and random-coding/quality matrix; it does not complete the90tok/s goal.
