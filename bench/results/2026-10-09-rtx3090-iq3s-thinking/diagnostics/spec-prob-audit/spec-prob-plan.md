# R042: exact speculative rejection sampling

Date: 2026-10-09. Current branch, existing implementation; no production source change.

R040 coupled Gumbel did not give a clear overall gain. R041 separately screens a longer MTP window. The next architectural alternative uses the drafter's full sampled distribution instead of only equality with its token guess.

STRATA_SPEC_PROB=1 is already implemented in include/strata/core/spec_prob.hpp, src/core/mtp.cpp and src/kernels/cuda/sampler.cu. The draft uses its own distribution q after its sampling chain. The verifier uses the target's actual post-chain distribution p, accepts a sampled guess d with probability min(1,p(d)/q(d)), and on rejection draws from normalized max(0,p-q). Prompt/suffix guesses without a q-list retain exact-match verification. The target numeric sampler and precision are unchanged. The random-number stream changes, so reproducibility is per explicit mode/seed and identical text versus the control is not claimed.

Reference accessed2026-10-09: https://proceedings.mlr.press/v202/leviathan23a.html. The exact-sampling proof motivates this implementation; finite local tests must verify the code rather than assuming the paper validates it. docs/DETAILS.md reports no reproducible gain on a different RTX3060/IQ3_XXS workload; no general gain is assumed.

C024 prerequisite: build/run existing spec_prob_test (distribution/joint-distribution checks, negative controls, support boundaries) and spec_verify_parity (GPU versus host reference), using CUDA13.3/sm86 and the production DLLs. Keep all failures and full outputs. Do not compile/test while a serving benchmark is active.

If checks pass, R042 changes only STRATA_SPEC_PROB=1 on the retained control; no Gumbel, coupled-only, deeper-window or new compiler/runtime settings are carried over. Keep --spec4, --spec-min-p.70, fixed target temperature1/top_p.95/top_k20/min_p0/presence0/repetition1, unlimited xhigh thinking,262144context,INT8KV,CPUF16vision,PCIe.20. Five512token measured runs and one excluded warmup per short/~3K cell. Collect all raw target/accepted draft counts, latency, prompt rate, memory, identity and whole-tree cleanup.

A gain must survive repeated paired controls, random-coding, natural-stop compilation/tests, streaming/cache/cold matrix, long-context and capability checks. A loss remains recorded and is not installed. If the measured draft counts show that confidence gating prevents useful batching, a later independently labeled draft-threshold experiment may be justified; do not change it inside this arm.
