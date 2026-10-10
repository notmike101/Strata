# C039: dual-output quantization, bounded offline screen

C038 proved a shared byte image unsafe. Inspecting PTX from the current CUDA13.3
objects shows native_quantize_q8_1 uses div.approx.ftz.f32, whereas
quantize_q8_1_rows uses div.rn.f32. The native reduction also flushes subnormals.
Both semantics must survive. One new kernel may load once but writes TWO images,
retaining per-path division, rounding, clamping and reduction behavior. No weight
or sampling changes. No production edit before all offline gates pass.

First run a failing parity fixture using the rejected shared-image mechanism to
prove the counterexamples are exercised. Implement precise dual outputs and
rerun the original96 deterministic C038 cases, plus a larger finite-input
quantization corpus with zero, signed zero, subnormal, rounding-boundary and
clamping inputs. Compare both byte images against existing compiled functions.
Require exact equality of both images and the actual-weight GEMV outputs.

Then ONE timing process: C038's actual gate/up weights from layers0/23/47,
N2560/M640, T1..8, two-stream graph,100 DAGs per graph, one excluded warmup and
seven alternating measured rounds per cell. Require >=5% geometric-mean time
reduction with no cell>3% slower. Failure closes this kernel shape, no retries
for a better median. Timing is an offline scheduling diagnostic, never TPS.

If both gates pass, proceed to an opt-in native engine implementation and
integration tests, followed by same-day served controls under the unchanged
90/85 contract. Preserve current launchers until full qualification. Offline
allocations stay under256MiB, check global16GiB headroom floors and live process
ownership first, leave no model resident, and retain every raw result.
