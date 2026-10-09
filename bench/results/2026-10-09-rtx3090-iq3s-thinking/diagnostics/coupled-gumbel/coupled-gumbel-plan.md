# R040: coupled Gumbel draft candidate, not a promotion

Date: 2026-10-09. Work only in perf/rtx3090-thinking-80. No production source edit.

The retained engine is near 87-89 short and 82-84 longer server decode tok/s. Exact CPU-cache and head-layout prototypes lost in served or device tests. The CUDA13.4 compiler alone did not provide a clear gain. Reassess speculation rather than continue local layout tuning.

Hypothesis: token-keyed random noise shared by the MTP and target lets their sampled picks agree despite differing candidate-list order. More accepted tokens could amortize target verification without changing target probabilities. This implementation already exists, opt-in. T003 tested coupled drafting alone and found no gain; it did not enable Gumbel-max. A different random stream means different text for the same seed; it does not establish quality preservation by itself.

Evidence: docs/DETAILS.md lines113-125 reports a 9% gain on a different AMD host/quant but no clear gain on RTX3060 IQ3_XXS. Treat both as hypothesis support, not a prediction for this computer. Source src/kernels/sampler_parity.cpp includes host/device comparison for the exact numeric profile, 10240-draw softmax frequency comparison, and flag/greedy controls. The coupled_draft_test exercises counter and penalty-history indexing.

Correctness rationale: for fixed target probabilities p_i, taking argmax(log(p_i)+G_i) with independent Gumbel noise is a categorical draw from p. Reusing token-keyed noise in the draft and target can increase equality without changing either marginal; retain only the target-approved prefix. General exact speculation reference: https://proceedings.mlr.press/v202/leviathan23a.html (accessed2026-10-09). The paper is not proof of this implementation. Existing target verification and numerical/backend rounding limitations still apply.

Before inference, build and run sampler_parity, sampler_parity_one_block, sampler_parity_old and coupled_draft_test on CUDA13.3/sm86 with the production libraries. Keep complete failures if any. No compiler or model may be active during served timing.

R040 changes exactly the proposal/coupling mode using STRATA_SPEC_COUPLED=1 plus STRATA_SPEC_GUMBEL=1, on the retained production executable and libraries. Numeric sampler, reasoning, context, KV precision, vision, MTP4/.70, PCIe.20, original short/~3K fixtures, five seeds and512token cap all remain fixed. Collect every run, MTP acceptance, prompt speed, TTFT, client rates and safety. One excluded warmup per cell. Process-memory queries remain outside timed generation. Guard physical and commit headroom independently; clean up entire launcher tree afterward.

If it loses, revert and retain evidence. If it wins, repeat against a fresh unchanged control before random-coding and full quality/memory/real-use gates. No change to the launcher until those pass. The goal remains unqualified while Q007 has incomplete coding answers.

Next independent alternative if needed: six-token MTP windows. Source automatically adds two suffix-draft positions, so --spec6 means a maximum eight-row verifier, not merely the currently allocated six-row verifier. That memory difference must be measured and cannot be hidden by changing context or precision.
