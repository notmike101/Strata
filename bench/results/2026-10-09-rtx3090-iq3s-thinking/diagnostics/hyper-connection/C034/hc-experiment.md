# C034: hyper-connection graph screen

P009 attributed 252.274 ms of summed instrumented kernel duration to 20,886
gr_up_multi<1,true> calls (not a critical-path percentage). Existing STRATA_GR_FAST
uses eight lanes per row with the original reduction tree and changes no weights.
CUDA on this RTX3090 defaults off. With HC_SPLIT=2 the norm/down paths stay staged.

The existing eager benchmark passed all 32 parity cells (T1..8, apply/inject on/off),
but its timing reports minima and includes host launch overhead. Preserve it only
as a diagnostic. One graph-replay screen now uses seven alternating-order timing
rounds, one excluded warmup per variant, 200 reads per graph, ordinary medians and
all raw samples. This matches the production graph execution style more closely;
it remains a synthetic kernel diagnostic, never proof of served TPS or quality.

Budget: one graph screen. If dominant T1 cells improve without broad T2..5 losses,
allow one fresh same-binary off/on served pair. Only if both workload medians and
prompt/client rates improve, allow one reversed pair, then fixed full quality
and stability gates. Otherwise close. No new shipping source or launcher change.

NVIDIA graph guidance consulted Oct10 UTC:
https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html
https://developer.nvidia.com/blog/constant-time-launch-for-straight-line-cuda-graphs-and-other-performance-enhancements
These support reducing host launch effects; they do not predict a local speedup.
