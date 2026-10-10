# C039: exact dual-output quantization passed micro gates, lost served comparison

C038's counterexamples prompted inspection of the current CUDA13.3 object PTX.
The native quantizer uses div.approx.ftz.f32 and FTZ reduction operations; the
routed quantizer uses div.rn.f32 and retains subnormal arithmetic. Both extracted
PTX entry points are attached. The new prototype reads an input once, computes
both original arithmetic paths, and writes distinct36-byte Q8_1 blocks. It does
not exchange their images, change weights, sampling, context or expert selection.

The regression fixture first reproduced the known failure with a shared-image
stub. The dual-output implementation then passed all96 C038 actual-weight DAG
cases, including all three original counterexamples. An additional4096-case
corpus compared47,185,920 finite input values and106,168,320 output bytes, with
untouched prefix/tail guards. It includes signed zero, subnormals, the first normal
exponent, mixed finite exponents and values that exercise FP16-scale/sum clamping.
These tests passed again against the integrated production API, independently of
the prototype definition. CUDA13.3.73/sm86; no HIP or SYCL build was performed.

The predeclared single timing process used actual layer0/23/47 shared gate/up
weights, N2560/M640, T1..8, two concurrent GEMV consumers,100 DAGs per graph,
one excluded warmup and seven alternating measured rounds per cell. Every raw
round is attached. Ordinary cell medians gave a geometric mean candidate/control
time ratio0.934193051, range0.868036..0.967430.
That is about6.58% less time in this isolated DAG. It is not served
TPS or proof of whole-engine benefit. The >=5% aggregate/no>3% regression gate
passed, permitting an opt-in engine experiment.

Integration was guarded by STRATA_DUAL_Q8=1 (defaultoff), CUDA, native expert
layout, a late shared-stream fork, no preexisting QFUSE image, and G==1. The
single-group condition avoids overwriting shared scratch while another group is
still executing. The CPU doorbell remains before the new kernel; the existing
fork event follows it. The shared expert receives its fast image and retains its
own hidden-state scratch; routed experts retain their precise image. Existing
join ordering remains before the next layer. A one-time capture log proved
activation at T4 in R073. Default/off remains the original quantization path.

The integration patch, regression source, build commands/logs and binary hashes
are archived. Upstream main remained fb58e0dbc8399662c0e47c76578c6e878b14f6cf;
no update was available. The test binary SHA256 is
ca6551bc7fcd095032c082408378adf91c476a48d48e7e223988c0d4c06beefc.

R072/R073 used the SAME candidate binary with only STRATA_DUAL_Q8 changed0->1,
GR_FAST0, and the retained production numerical/settings contract. Every arm
used fresh process state, one excluded warmup and five measured seeds101..105
per original short/~3K cache-miss workload,512 tokens, one request at a time.
R072 control decode medians87.4/81.2; R073 candidate85.7/80.8 tok/s.
Prompt medians201.2/496.1 vs205.5/497.1; request-E2E76.4100/41.1743 vs
75.3068/41.1098 tok/s. Detailed ranges, TTFT, stream TPS, MTP and memory are
recorded in E107/E108. Both decode medians fell, so reject without another pair
or stacking it with GR_FAST. There is no qualifying90 TPS result.

Correction E121: all12 request payloads are byte-identical while all12 output texts differ.
The earlier nonce explanation was wrong; the cause remains unresolved. The512-token
speed runs are capped thinking continuations, not completed-answer quality
qualification. Full coding/workload qualification remains unresolved as before.

The source edits were restored byte-for-byte from the pre-experiment checkpoint
and the experimental regression test was archived then removed from tools/.
The retained executable/config hashes remain6048736d... and3457fdfe....
Both benchmark launcher trees stopped cleanly; idle GPU457MiB, no model resident.
The build-cuda86-main object directory still holds this candidate and must be
rebuilt from restored sources before calling it a new baseline build.

Next: reassess CPU expert execution/code generation against the existing host
timings and exact mixed-format inventory. Do not repeat shared-quant scheduling,
Q6 one-warp, Foresight, device planning or lower-PCIe combinations absent a new
mechanism. Current production settings remain unchanged; the goal stays active.
