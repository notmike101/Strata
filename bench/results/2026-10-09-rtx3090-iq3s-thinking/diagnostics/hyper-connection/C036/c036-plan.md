# C036: lossless BF16 exponent-offset storage

Existing evidence: C035 proves the exact HC projection sources are BF16, not Q8.
P009 records252.274ms of gr_up_multi<1,true> and211.968ms of staged down kernels
(overlapping instrumented durations, not exclusive critical-path percentages).
Reducing exact weight bytes is a new hypothesis, not a repeat of source-Q8.

Format: each32 BF16 coefficients uses a52-byte aligned block: a4-byte exponent
base/escape header,16bytes of four-bit exponent offsets, and32bytes holding each
original sign and seven mantissa bits. Blocks with exponent range>15 retain every
original BF16 bit in a64-byte fallback record; the header stores its index with
the high bit set. Zero signs, subnormals, and all exponent values are preserved.
F32 normalization tensors stay unchanged. No arithmetic reduction order changes.

Finite budget:
1. One full offline encode/decode pass over every target and draft BF16 HC tensor.
   Require zero differing bits, >=95% eligible blocks and >=15% aggregate byte
   reduction INCLUDING headers and fallback bytes. Otherwise close immediately.
2. If eligible, one standalone CUDA up-projection prototype using the existing
   reduction tree, actual weights (first/middle/last up projection), T1..5,
   original versus decoded exact coefficients. Require finite bitwise outputs.
   One excluded warmup and seven alternating graph timing rounds; no minima.
   Retain only if T1 ordinary median time improves>=5% on every selected tensor,
   with no >2% loss at T2..5. One failed screen closes the prototype.
3. No integration or model server launch within this screen. A passing prototype
   only warrants a separately bounded all-weight/device test and served design.

No quality, quant, sampling, context, vision, memory-floor or launcher change.
Use the retained CUDA13.3/sm86 toolchain. Keep model tensor data private; publish
only scripts, per-tensor hashes, raw timing, parity and rejection/retention evidence.
