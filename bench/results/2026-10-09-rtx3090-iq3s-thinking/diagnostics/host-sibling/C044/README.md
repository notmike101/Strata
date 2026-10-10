# C044 upstream PR1166 local integration

PR1166 head a71da892150aa6b30cf560c2294c936a0353c5a8 integrated locally, opt-in; only generate.cpp patch context adapted around existing campaign options. Upstream layout test first failed compilation on missing Sibling/host_sibling (red); after integration Windows affinity tests and iq_avx2_parity passed (zero failures). Topology proof: first host0/workers2,4,6,8,10,12,14,16,18; sibling host1/SAME workers; last host18/workers0..16. CUDA13.3.73/sm86 build succeeded. No Linux/HIP/SYCL runtime test, no upstream review/merge request. No claim of IRQ placement or output-quality qualification. Next R078/R079 same-binary first/sibling comparison, no DMA/Clang changes. Candidate engine SHA256 ce7d4ecc250185acd2b14941b66c31a4c71558a0f75f03d53ca85ad11c97355f. Artifacts: diagnostics/host-sibling/C044/.

## Final result: rejected and reverted

| Workload | First decode | Sibling decode | First prompt | Sibling prompt | First E2E | Sibling E2E |
|---|---:|---:|---:|---:|---:|---:|
| Short |87.4|86.3|207.5|205.3|76.0537|76.0412|
| ~3K |84.2|83.4|496.9|497.0|41.9492|41.6896|

All values tok/s, ordinary medians of all five512-token measured requests per
cell; excluded warmup. Startup proves host0 versus host1, nine unchanged workers
2,4,6,8,10,12,14,16,18. Same binary and backend libraries, fixed contract. No
claim that upstream measurements were wrong; the win did not reproduce here.
Both generation medians fell and short prompt also fell, so reject under the
predeclared gate. No second pair or stacking retry. All source restored from
HEAD, both original upstream patch and adapted integration patch retained.
Per-run ranges, MTP, TTFT, stream/E2E, memory and cleanup are in E119/E120 and
served-candidates. Both16GiB floors passed; post-cleanup GPU457MiB.
Production configuration unchanged. No benchmark model left resident.

The build-cuda86-main object directory still contains this rejected integration.
Rebuild restored sources before using it as a current source baseline.
