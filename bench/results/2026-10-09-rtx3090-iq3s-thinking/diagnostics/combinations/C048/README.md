## E150 / C048 rejected globally; longer-input mechanism retained as a hypothesis

Previous goal turn was progress: P019 localized a window divergence. This turn
built and measured the distinct accepted-token boundary architecture. Upstream
main remains fb58e0dbc8399662c0e47c76578c6e878b14f6cf, release v0.1.41.
Reference: https://github.com/Niko1221/Strata/pull/1779 at
f3727b2464321a35c4638491d75bcda1d4ecbb9c. Only the single-GPU serial token-boundary
mechanism was implemented; no multi-GPU pipeline or sampling change was imported.

Candidate SHA256 c9508334047d378f2e4f5a7dd128e90064023effb2d12bf884d96520379855b4,
CUDA13.3 sm86, source dd0555b5 plus archived patch and two new source files.
Default-off STRATA_SERIAL_ADAPT_TOKENS; enabled value64 requires C046 accepted
usage and its restricted synchronous single-GPU serving route. Base and chained
windows clip to the boundary. The verifier commit/stream and MTP stream finish
before adaptation; the refill stream finishes before publishing cache residency.
PCIe fraction stays .20. New scheduling and placement may change numerical
rounding/output, so unchanged numeric kernels are not a full quality proof.

Validation: missing-header red compilation, then1.2M randomized accepted-prefix
steps passed across intervals1/2/3/7/64/257, disabled identity and clipping/error
cases. Registered CMake test, accepted usage oracle, Windows worker/host affinity,
IQ AVX2 parity all passed; CUDA engine built. Eight unsupported/malformed configs
rejected before loading. HIP/SYCL not built; no upstream review requested.

Both served arms used the same binary/libraries and12 byte-identical requests.
One warmup+five measured seeds per short/~3K cell, all512tokens/cachemiss, fixed80
CPU prompt share/MAX1024, HC1/accepted1,DMA0/deviceplan0. Numeric thinking coding
sampling1/.95/20/0/0/1 remained fixed,262144context,INT8KV/32768resident,CPU F16vision.

| Metric | Control short / ~3K | Barrier64 short / ~3K |
|---|---:|---:|
| server_decode_tps | 88.7 / 84.4 | 85.2 / 89.6 |
| prompt_tps | 217.7 / 496.2 | 226.7 / 497.7 |
| request_e2e_tps | 78.2182 / 41.9663 | 75.6242 / 43.2796 |
| stream_total_tps | 78.2301 / 41.9713 | 75.6342 / 43.2843 |
| TTFT seconds | .80133 / 6.16382 | .77358 / 6.13455 |

Raw decode, seeds101..105:
- R094 short90.2,88.7,85.4,93.1,87.4; longer82.9,84.4,85.7,85.4,83.1.
- R095 short79.9,82.1,85.2,87.6,90.2; longer85.4,89.6,83.4,89.8,90.0.

Short decode -3.946% and E2E -3.316% cross the written loss-stop rule. Therefore
no R096/R097 confirmation pair, no promotion. Longer decode +6.161% and E2E
+3.129% are promising single-pass observations, not confirmed wins or goal proof.
Do not discard the short regression or reinterpret the overall candidate as a win.
All12 enabled requests executed seven barriers; total barrier time median
214.314ms/request, range212.924..216.111ms.
Counts prove activation. Time includes selection, stream fences, copies and
publication; it is not an isolated copy benchmark or removable-time estimate.
Measured draft acceptance short873/1122 control versus812/1084 candidate;
longer1045/1394 versus1064/1410. Text/acceptance can change throughput.

All24 requests passed independent16GiB physical/commit guards and exact process
cleanup. Lowest available physical/commit62509596672/40775720960 bytes. GPU peak
25111236608bytes sampled, no process-memory polling during requests. Final GPU
457MiB, production config hash3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0.
Production launcher/binary unchanged. Source is restored after archiving the
candidate patch/tests/build evidence; build tree and saved candidate binary still
contain C048, so do not mistake them for a rebuilt retained control.

Next distinct hypothesis: the short-path regression may reflect insufficient
cache adaptation early in request history, whereas longer prompts prepare a more
useful cache. The candidate short sequence rises79.9 to90.2, but seeds differ,
so this trend alone does not prove warm-cache causality. The natural existing
prompt-placement boundary is1024tokens (short CPU/GPU sharing versus longer
GPU prefill). A separately planned long-path-only barrier experiment could keep
the original short policy and test the larger-input benefit without assuming
the policies compose: earlier short requests change later cache state. Keep
the interval64 and sampling fixed, compare against the same stack, and include
boundary-neighbor/random-coding checks before any promotion. This is C049's
potential mechanism, not permission to bypass C048's stop or cherry-pick rows.

Goal90/85 and full quality/cold-warm/workload qualification remain active and
unmet. Q007's two incomplete natural-stop coding answers remain unresolved.
