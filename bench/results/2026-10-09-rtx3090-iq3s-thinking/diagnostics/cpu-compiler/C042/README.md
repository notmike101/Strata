# C042: Opt-in integrated compiler candidate ready for served validation

Added defaultOFF STRATA_CLANG_IQ3S CMake option and defaultOFF STRATA_IQ3S_CLANG runtime dispatch. Windows/MSVC portable static-runtime builds only, explicit clang-cl path; separate compiler symbols. Only type21 AVX2 GU can switch, VNNI and all other formats retain existing dispatch. Red fixture first failed missing dispatch; green on/off checks passed. Integrated actual-weight576 full pool outputs matched bitwise; existing iq_avx2_parity reports0 failures. CUDA13.3.73/sm86 engine rebuilt, including GPU sources restored after C039. No HIP/SYCL validation or review request. No model/context/sampling/weights changed. R074/R075 will compare runtimeOFF/ON with same binary, fixed TTLCache contract. This remains experimental; no launcher promotion and goal active.

Hardware: RTX3090 24GiB, i9-10900KF10c20t,128GiBDDR4-3200, Windows11 build26200. Exact model: ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF IQ3_S. Actual tensors read locally and never published. Raw all-run logs, source, compile commands and parity evidence attached. Prior C040 losses remain part of the ledger. See fixed goal-90-contract.md for served workload and pending quality/memory/matrix gates.

## Final served outcome: rejected

R074 runtimeOFF versus R075 runtimeON, same binary and fixed parameters:

| Workload | Control decode | Candidate decode | Control prompt | Candidate prompt | Control E2E | Candidate E2E |
|---|---:|---:|---:|---:|---:|---:|
| Short |87.5|87.5|200.0|204.2|76.5906|76.6508|
| ~3K |83.3|82.6|496.2|496.7|41.6844|41.4387|

All values are ordinary medians, tok/s, five measured512-token requests per
cell; one excluded warmup. Raw rows, ranges, stream-total TPS, TTFT, MTP counters
and memory are retained in E112/E113 and the served-candidates directories.
The candidate tied short and lost longer generation, failing the predeclared
no-degradation continuation gate. Do not select the90.1 short peak as success.
The15.1% CPU pool micro gain did not establish a served win. No ABBA/stack retry.

Each arm stopped its exact launcher/server/text/vision process tree. Both
16GiB memory floors passed: minimum physical62,641,897,472bytes and available
commit40,920,264,704bytes across both arms. Post-cleanup GPU457MiB. Retained
production engine SHA6048736d... and config3457fdfe... unchanged.

The source integration was restored from HEAD and its patch archived here.
The build-cuda86-main directory still holds C042 candidate objects: rebuild from
restored sources before using that tree as a source baseline. Saved candidate
executable is diagnostic only. No new compiler dependency in production.
No completed-answer quality claim: these capped thinking runs do not replace
Q007 or the full frozen coding/cold/warm/context/tool/vision matrix. Goal active.
