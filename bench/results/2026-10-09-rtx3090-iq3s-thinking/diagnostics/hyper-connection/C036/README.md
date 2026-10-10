# C036: exact BF16 storage saves bytes but loses GPU time

Hypothesis and finite gates were written in c036-plan.md before the full screen.
The actual BF16 source permits a lossless block format: original sign/mantissa
bits, four-bit exponent offsets and exact BF16 fallback blocks. This is not Q8
quantization. Every one of659,374,080 coefficients across298 target/draft BF16
HC tensors reconstructed bit for bit. Headers/fallbacks included, storage fell
from1,318,748,160 to1,074,217,408 bytes (18.5426%);99.7926% of blocks were eligible.
Original pack/model files were read-only. Norm tensors remained unchanged.

The standalone CUDA13.3 sm86 prototype then compared the existing eight-FMA and
xor reduction tree against the same arithmetic fed by reconstructed BF16 values.
It used the first/middle/last target up-projection in sorted name order, actual
weights, T1..5 and three bounded random input sets. All45 comparisons passed:
1,382,400 finite output floats were bitwise equal. The exact source dot helpers
were copied from fused_gr.cu; no production kernel was modified.

Each timing cell uses200 projection calls per graph, one excluded warmup per
variant and seven alternating measured rounds. All raw rounds are retained;
ordinary medians are below. These are isolated kernel diagnostics, not served TPS.

| Tensor ID | T | Original median us | Packed median us | Packed/original |
|---|---:|---:|---:|---:|
| 0 | 1 | 7.607680 | 11.873280 | 1.560697 |
| 0 | 2 | 10.071041 | 14.612480 | 1.450940 |
| 0 | 3 | 12.071680 | 16.788481 | 1.390733 |
| 0 | 4 | 14.175839 | 18.739199 | 1.321911 |
| 0 | 5 | 14.945281 | 18.938721 | 1.267204 |
| 1 | 1 | 7.055360 | 10.337280 | 1.465167 |
| 1 | 2 | 8.908800 | 12.472320 | 1.400000 |
| 1 | 3 | 10.525921 | 14.136321 | 1.343001 |
| 1 | 4 | 12.260799 | 16.091681 | 1.312450 |
| 1 | 5 | 14.658560 | 18.691999 | 1.275159 |
| 2 | 1 | 51.164162 | 44.917759 | 0.877914 |
| 2 | 2 | 10.525121 | 15.143359 | 1.438782 |
| 2 | 3 | 12.180480 | 16.885759 | 1.386297 |
| 2 | 4 | 14.295040 | 18.953119 | 1.325853 |
| 2 | 5 | 17.638399 | 21.253120 | 1.204935 |

Decision: reject.14/15 cells took20.49-56.07% more GPU time. The first two T1
cells lost46.52-56.07%, failing the required>=5% improvement on every selected
tensor. The last T1 cell has elevated timings and a12.21% apparent gain; it is
retained, not discarded or promoted. Its cause was not investigated because the
other cells already decisively fail the finite retention rule. No repeat, model
launch, integration, launcher change or altered quality gate followed.

The CPU eligibility pass took27.201s, with minimum physical/commit headroom
121,236,983,808/124,016,676,864 bytes. The GPU prototype allocates only three small
tensor representations for one tensor at a time and exits after testing; it is
not a resident model. Tensor copies and executable remain private local scratch;
public evidence contains source, hashes, inventory, parity and all raw timings.

This result rejects this particular per-block exponent decoder. It does not
prove that all lossless storage is slow. A different format needs genuinely new
evidence and a new bounded hypothesis rather than tuning this failed screen.
Next useful direction is measured host/device scheduling or removal of work;
do not repeat closed Q6, device-planning, PCIe or this format without new evidence.
The unchanged90 TPS objective remains unqualified; Q007 still has incomplete
coding answers. Production configuration, model, sampling, context and vision
remain unchanged, and no benchmark model is left resident.
