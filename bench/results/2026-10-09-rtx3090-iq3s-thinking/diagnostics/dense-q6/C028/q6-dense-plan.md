# C028: actual dense Q6_K projection geometry

The frozen 90 server_decode_tps contract, model, quantization, numeric sampling,
context and quality gates remain unchanged. This is an isolated kernel diagnostic
under the already authorized performance campaign, not a served qualification run.

P011 groups P009's recorded Q6_K single-column calls by launch shape. The 2560-row
cohort accounts for 157.10 ms across 8000 calls, more than either the full-head or
reduced-vocabulary cohort individually. Other dense cohorts have 512, 640, 6144,
10240 and 12288 rows. These are summed instrumented kernel durations, not exclusive
request critical-path shares. No direct token-rate prediction follows from them.

The actual GGUF directory resolves six dense shapes: input/output 6144/2560 and
2560/{512,640,6144,10240,12288}. C021 only timed the 2560/248320 output head;
its rejected head result does not establish the result for these smaller shapes.

Reuse C021's already parity-tested row-group implementation unchanged. Load the
first actual Q6_K tensor for every dense shape. Compare groups 2, 4 and 8 against
the original one-row kernel using eight activation patterns and odd/full row
counts, finite outputs and output canaries. Preserve the exact per-thread dot
order and reduction order. No precision, weight representation or math changes.

After parity passes, time eleven alternating forward/reverse rounds after one
excluded warmup. Use CUDA graphs of 64 identical kernel calls per sample to reduce
host launch gaps for small shapes; report every CUDA-event value and graph memory.
Baseline and candidate use the same compiler, translation unit and stream. Reuse
CUDA 13.4 only for this paired diagnostic; retained production CUDA 13.3 is unchanged.

Do not modify the production dispatch from this result alone. Reject losers.
Any promising geometry needs actual integrated-source parity, opt-in dispatch,
same-day served AB/BA and the full quality/latency/memory matrix. Two incomplete
coding answers from Q007 still prevent goal qualification. Always reset the device
and verify no live diagnostic, server or model remains afterward.

Other lead rejected without a run: STRATA_STAGE_PIN only serves staging buffers
when the full RAM arena is unavailable. The current arena path does not use those
buffers, and the repository documents IQ3_S corruption in that opt-in path.
