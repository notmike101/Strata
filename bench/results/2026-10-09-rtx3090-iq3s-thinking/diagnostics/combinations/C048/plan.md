## E147 / C048 fixed accepted-token cache boundaries

Previous turn progress: P019 localized a window-shape divergence after identical
first logits and found later requests already differ at first logits. Upstream
main rechecked unchanged fb58e0db, latest v0.1.41. No inference process resident.

Test the PR1779 token-barrier mechanism as a scoped single-GPU serial derivative,
using C046 accepted-row accounting. Default remains off. Require accepted-usage1,
active synchronous cache, one GPU, no helper/peer/pipeline/batch. Preserve PCIe.20:
its transient expert staging is complete when the verifier stream is synchronized,
and cache refill runs only after verifier commit and MTP streams finish. Publish
residency only after the refill stream finishes; report any CUDA wait failure.
Clip the base and chained window to the remaining accepted-input-token interval.
Keep heat/decay/selection rules, numeric kernels, sampling, quant/context unchanged.
Changes are in the existing serial flow, not an imported multi-GPU pipeline.

One interval only:64 from the reference mechanism; no interval sweep. A standalone
boundary oracle exercises random accepted-prefix lengths, nonzero prompt offsets,
base/tail clipping, interval1 and disabled identity. Red compile then green test;
CUDA13.3 sm86 build plus existing accepted usage, affinity and IQ parity tests.
HIP/SYCL unavailable locally; no upstream PR or cross-backend claim.

Finite initial serving comparison: R094 barrier0 then R095 barrier64, same new
binary, fixed80/MAX1024, HC1/accepted1,DMA0/deviceplan0, existing9workers30tasks,
MTP4/.70,INT8KV/32768resident,262144context,CPU F16vision. Exact original TTLCache
short/~3K payloads, one warmup+five measured seeds per cell,512tokens,one request.
16GiB independent physical/commit floors, audit-no-process observer, exact cleanup.
No builds/Git/profiler/GUI/process-memory polls during requests. No trace hooks.
All rows retained; server decode, prompt, E2E, stream total and TTFT separate.

If either decode/E2E cell loses >3% or prompt loses >2%, stop and archive/revert
this candidate. Otherwise one reversed B/A confirmation pair maximum (R096/97).
These screening tolerances allocate experiments, not permission to promote loss.
No production promotion absent all-run medians, frozen coding quality and full
real-use matrix. Diagnostic reproducibility can motivate further investigation
but cannot count as speed qualification. No model left resident at checkpoints.
