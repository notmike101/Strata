# Device-side resident-group planning: bounded experiment

Hypothesis: the retained CUDA verifier spends material time waiting for the host
and copying expert plans even when every routed expert in a group is already
resident. STRATA_VERIFY_DEVICE_PLAN=1 builds those plans on the GPU and bypasses
host waits for those groups while retaining the host path for mixed groups.

Existing evidence first: P009 contains47,808 wait_flag_ge kernel calls with
795.645 ms summed instrumented duration, plus17,064 plan-copy calls totaling
72.942 ms. These overlapping, instrumented sums are not critical-path fractions.
No resident_plan kernel ran in that trace. No new baseline trace is needed.

Compatibility: current partial8409-slot cache means all_resident_ is false;
one GPU and no pipeline means always_publish_ is false. Foresight swap is off.
The lag2 tier waits for its copy event before publishing host_res and uploading
d_res; this single-stage path does not use in-flight pipeline publication.
The existing CUDA resident_plan parity test passed641 cases with zero failures,
including duplicate routes, variable slot offsets, and nonresident fallback.
No target sampler, model tensor, precision, context or vision setting changes.

Finite budget:
1. One bounded Nsight capture: one excluded warmup and one512-token frozen coding
   request. Prove resident_plan execution and inspect wait/plan calls. This is
   diagnostic only, under the same independent16GiB host-memory floors.
2. One fresh retained-binary control and one candidate: original short/~3K cells,
   one warmup and five measured seeds per cell,512tokens, fixed thinking profile.
3. Continue to one opposite-order pair only if both decode medians improve and
   prompt/client throughput do not fall. If neutral or worse, close the direct
   experiment. A mixed component can receive at most one separately predeclared
   interaction pair when trace evidence identifies a specific compatible partner.

Retention requires repeated served benefit, intact prompt rate and client latency,
then the unchanged full quality/stability/cold-warm/max-context gates. A peak,
profiled rate or isolated kernel saving never qualifies the90 TPS goal.
No source feature is added for this test. Q6 code was retired from shipping source;
its exact archived prototype and all measurements remain available at e564208a.
Production uses the retained format-gather binary, PCIe0.20, lag2 and fixed sampling.
