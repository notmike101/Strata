# R046: existing resident exchange rotation

R045 reduced the pinned expert allocation to 34.55 GiB but lost decode throughput
against the retained full arena. It performed 28,682 exchanges across twelve
requests, with no fallback file reads. The exchanges add GPU-to-host traffic and
an extra host copy. STRATA_EXCHANGE_ROTATE=1 removes the latter by exchanging
buffer ownership, keeping exact expert bytes and their GPU aliases together.
GPU transfer costs remain; this may recover only part of the loss.

Change only that environment key from R045. Keep blocking adaptation, lag2,
MTP4/.70, the target numeric sampler, reasoning, model/quant, 262144 context,
INT8 KV, CPU vision, prompts, seeds, one warmup and five measured runs per cell.
Require explicit activation in startup, the same 8409 GPU cache entries, a
page-locked complement, and no partial residency warning. Save cumulative
rotation, avoided-copy payload and fallback counters. Compare same-seed output
texts with R045 as an additional empirical parity check, without calling text
equality a substitute for the full quality matrix. A loss remains unpromoted.

C027 already passed exact-byte GPU checks in copy, rotation and fallback modes.
This Windows served measurement is still needed; the published Blackwell greedy
single-run example is not evidence for the current sampled model workload.

The supervisor captures the complete engine session before cleanup, with cleanup
in an inner finally so a log write failure cannot bypass process termination.
Snapshot helper versions and the eight-key effective sampling manifest per arm.
