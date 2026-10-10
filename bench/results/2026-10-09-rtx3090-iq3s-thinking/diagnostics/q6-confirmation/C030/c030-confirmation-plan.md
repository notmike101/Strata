# C030: confirm the narrow Q6 component for stacking

Use the retained CUDA 13.3 compiler and unchanged build-cuda86 native reference
library to compile the C029 parity/timing harness. Preserve candidate source and
math. Run all 22 actual Q6_K tensors of shape 2560 input x 10240 output, three
fresh processes each, including all original eight patterns and canaries. Each
process retains eleven alternating timing rounds, excluding the uncaptured priming
call and captured graph warmup. Use the existing group-4 candidate as the preselected
choice; do not choose a different winner per tensor after looking at timing.

This checks whether the first CUDA 13.4 result transfers to the production compiler
and other actual weights. Require bitwise correctness for every case, and compare
all 33 timing rows per tensor to reference. Also retain every per-process median.
No claim of served throughput follows from this diagnostic. If the preselected
group-4 variant consistently wins without a material losing tensor/process,
integrate only that shape behind an opt-in switch and measure it alone and with
other promising components against the retained production stack. Otherwise park
it with the measured evidence; small size alone is not the rejection reason.

R052 PCIe zero regressed short/client/prompt metrics, so it is not a component to
combine. PCIe 0.10 remains mixed. The retained build is unchanged, and all fixed
sampling, quality and workload gates remain in force for later served trials.
