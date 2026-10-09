# R044: confidence threshold after the rejection-mode integration audit

Queued diagnostic, not run or promoted at this checkpoint. Current branch only.

Use R043's audited composition: STRATA_SPEC_PROB=1, STRATA_SPEC_PROB_GATE=top, --suffix-draft0, no lookup chaining. Keep the retained production engine/DLLs, --spec4, original profile, context262144, INT8KV/32768resident, CPUF16vision, PCIe.20 and all thinking/sampling values unchanged.

Change only the hardware draft-confidence floor --spec-min-p0.70 to0.50. This is not the target sampler's min_p, which remains0. It changes how many draft proposals are verified. The gate must depend on the proposal distribution's top probability, never the realized sampled token. C025/C026 document why the latter and draft-dependent lookup mixing are excluded.

New rationale versus rejected T002: T002 used the ordinary exact-match/argmax proposal path. R043 uses the entire proposal distribution and rejection correction, so the probability of accepting a lower-confidence proposal can be materially higher. R043's first longer measured request accepted228/264 drafts, whereas R039's first longer request accepted190/271 under ordinary drafting; those individual examples explain the hypothesis, not a performance claim or controlled acceptance comparison. Use complete all-run R043 acceptance statistics for the actual comparison.

Predicted effect: more accepted tokens per target window can amortize CPU expert work and target weight reads. Counter-risks: extra draft/verification work and lower acceptance at later positions erase any benefit. Five512-token measured seeds101-105 plus one excluded warmup per original short/~3K cell, longer-first. Same live identity checks, no process-memory polling during generation, both16GiB host safety floors, sampled GPU memory, complete tree teardown and restored configuration.

Reject a loss. A promising result only queues a fresh paired repeat and random-coding/full quality matrix. It cannot complete the90tok/s goal by itself. Do not promote any unsafe rejection-sampling combination or change the target sampler to raise acceptance.
