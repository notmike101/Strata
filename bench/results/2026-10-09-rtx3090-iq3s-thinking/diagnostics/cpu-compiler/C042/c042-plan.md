# C042: opt-in IQ3_S Clang GU integration and served comparison

C040 blanket replacement is rejected; C041 independent selective gate passed.
Integrate only type21 AVX2 GU under build option STRATA_CLANG_IQ3S (defaultOFF)
and runtime STRATA_IQ3S_CLANG (defaultOFF). Preserve VNNI dispatch, all other
formats, down projections, quantizers, pool scheduling and GPU operations.
Clang19.1.5 /O2 /MT /EHsc /arch:AVX2 /fp:precise -ffp-contract=off,
STRATA_AVXVNNI0. Every renamed public symbol has a separate compiler image.

Dispatch fixture first failed (type21 call absent); on/off must now pass.
Integrated actual-weight pool output must match default bitwise for all48layers,
3experts/layer, T1/2/4/8 (576cases). Run existing parity suite as regression.
Build CUDA13.3.73/sm86, rebuilding GPU sources restored after C039. HIP/SYCL are
not validated. No upstream review or merge requested.

R074 runtimeOFF and R075 runtimeON: same fresh executable, existing fixed
TTLCache short/~3K streaming cache-miss requests, 512tokens, one excluded warmup
and five measured seeds101..105 per workload. Fixed sampling/context/vision,
GR_FAST0, PCIe.20, MTP4/.70, lag2. Independent16GiB physical+commit floors,
audit-no-process telemetry. One resident model, cleanup after each arm.

Retain all results. Continue to reverse-order confirmation only if both decode
medians and prompt processing do not regress; otherwise reject integration.
An apparent winner still needs the frozen random coding prompt and complete
cold/warm/quality/workload matrix. No production promotion on these speed arms.
