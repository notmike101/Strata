# R052: no primary PCIe missed-expert work after CPU gather improvements

Hypothesis: P009's GPU stage costs plus E073's repeatable longer-workload gain from
reducing PCIe fraction 0.20 to 0.10 suggest the GPU/link side is over-assigned for
some windows after the retained CPU gather improvements. Test the other endpoint,
0.00, using the current faster CPU implementation. The old zero-share calibration
predates those CPU improvements and cannot settle this experiment.

Change only --pcie-frac from 0.20 to 0.00 in the retained production configuration.
All missed experts still execute using their original CPU kernels and weights;
cached experts stay on GPU. The fixed thinking profile, model/quant, context,
INT8 KV, vision, concurrency and request payloads stay identical. Record any
automatic GPU-cache or graph-buffer consequence; do not hide it as fixed capacity.

Use the latest same-day unchanged R051 control, longer-first order, one excluded
warmup plus five measured 512-token seeds per workload. No process queries during
requests. Full identity check, GPU telemetry, independent 16 GiB RAM/commit guard
and finally-based whole-tree cleanup remain active. Stop this direction if decode
or prompt/client metrics regress. If it wins, repeat with a fresh control in the
opposite order and run random coding plus the full quality/memory matrix before
promoting anything. No altered sampling or target-number change.

This is the next concrete scheduling test before implementing a new controller.
Upstream PR 1548's runtime fit changes decisions based on measured timings; it is
not a deterministic production candidate without further correctness analysis.
