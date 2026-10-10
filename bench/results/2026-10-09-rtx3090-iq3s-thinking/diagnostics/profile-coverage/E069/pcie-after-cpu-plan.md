# R049: revisit CPU/PCIe balance after the CPU dispatch improvements

Current paired control R047: 87.1/80.9 short/~3K server decode tok/s, unchanged
four-token MTP. R048's smaller window lost speed and is rejected.

The original calibration chose PCIe fraction0.20 on the earlier engine/profile,
before the retained gathered CPU dispatch and format-specific IQ2_S exception.
It measured0,0.18,0.20,0.35,0.55,0.75,0.90,1.0;0.10 was not measured. Later
source changes materially improved CPU expert service. A share chosen before
that improvement is a hypothesis for the current stack, not a permanent optimum.

Source src/core/expert_source.cpp builds distinct missed experts and assigns
floor(nmiss*pcie_num/256) of the last misses to the GPU. generate.cpp rounds the
requested fraction to pcie_num. Moving0.20 (51/256) to0.10 (26/256) can avoid
PCIe transfers for modest miss groups while asking the faster CPU kernels to
compute those same expert weights. It does not omit experts or change routing.
GPU/CPU floating rounding can differ, so a speed gain still needs the existing
full quality and reproducibility matrix.

P005 host timing and the internally consistent portions of P009 show material
GPU-reach/transfer wait and CPU service. This gives a falsifiable balance theory:
less PCIe work could reduce total window time, or CPU service could grow enough
to lose. Do not count saved transfers alone as an optimization win.

R049 changes only --pcie-frac0.20 to0.10 relative to R047. Keep the model/quant,
262144 context, INT8KV/32768 resident, MTP4/.70, lag2, CPUF16vision, xhigh and
all fixed numeric target sampling. Same original short/~3K requests, one warmup
and five measured512-token seeds per cell, one request at a time. Retain every
run, both16GiB host memory floors, GPU telemetry and full-tree cleanup.

Compare ordinary all-run medians and client/prompt metrics against R047 and
historical retained controls. An apparent winner needs an opposite-order fresh
control/candidate repeat before any random-coding/full-matrix promotion work.
An ambiguous small change is not a win. No production launcher change yet.
