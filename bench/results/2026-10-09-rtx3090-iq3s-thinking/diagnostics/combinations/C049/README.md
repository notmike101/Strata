## E156 / C049 complete four-arm comparison; experimental component only

Same-binary ABBA R098/R099/R100/R101 completed,10 measured rows per workload/cell
(40 measured+8 warmups total). All512tokens, cachemiss, exact payload equality,
fixed thinking coding sampling1/.95/20/0/0/1,frequency0. Context262144, INT8KV with
32768 resident, CPU F16vision, MTP4/.70,PCIe.20,9workers30tasks,HC1/acceptedusage1,
auto prompt sharing/MAX1024,DMA0/deviceplan0. No slow seed or graph capture removed.

| All-run ordinary median | Control | Conditional64 | Change |
|---|---:|---:|---:|
| Short server_decode_tps |89.4|89.1|-0.336%|
| ~3K server_decode_tps |82.9|85.0|+2.533%|
| Short prompt_tps |206.35|211.00|+2.253%|
| ~3K prompt_tps |497.05|497.25|+0.040%|
| Short request_e2e_tps |78.24714|78.04901|-0.253%|
| ~3K request_e2e_tps |41.63743|42.17055|+1.280%|
| Short stream_total_tps |78.26603|78.05986|-0.263%|
| ~3K stream_total_tps |41.64120|42.17379|+1.279%|
| Short TTFT seconds |.852411|.833291|-2.243%|
| ~3K TTFT seconds |6.140930|6.141785|+0.014%|

Individual pass decode short/~3K: A90.0/83.8, B88.5/87.8, B90.1/84.2,
A88.8/82.7. Every individual result and raw seed order is retained in E152-E155
and summary.json. The larger first-pass longer gain did not repeat at the same
size. R099 longer run1 includes a captured5-token graph; retained. Its longer
draft acceptance80.01% versus R09872.73% also shows that output/draft behavior
contributes to served speed. No isolated kernel-speed claim follows.

The candidate's longer median reaches85.0 in this screen, but short89.1 misses90,
and short decode/E2E point estimates are below control. Therefore no no-degradation
qualification, no production promotion, no target completion. The complete finite
comparison is closed; no extra repeats to seek a favorable median. Retain the
default-off code as an experimental component for future justified combinations.
It is not a verified overall winner. Same-day control is essential: earlier
same-stack historical controls were sometimes faster; do not pool different
binary histories or present the2.533% as a universal gain.

Runtime proof: all12 enabled-arm short requests logged interval0; all12 longer
requests logged interval64 and seven completed barriers each. Policy uses fresh
prompt tokens n-resume, so long cached conversations with short suffixes retain
ordinary window adaptation. Threshold1025 is anchored to1024 prefill tokens plus
the last prompt token consumed in decode. This request-level rule is a proxy:
checkpoint splits can still make smaller prefill chunks. Boundary-neighbor,
cache-hit and reversed workload-history validation remain required.

Barrier time median214.684ms across12 longer requests,
range210.816..216.275; includes selection/copies/fences/publication,
not removable latency. Full-output byte matches across passes: control
0/12, conditional0/12.
No determinism or answer-quality claim follows from the scheduling policy.

Implementation/build: SHA256ac43e89822e4febce9a2e3ae93a786eaa705bdc61f04ba28302ee50c64bb87c3,
source cacdcd35 plus C049-integration.patch/new header+test. CUDA13.3 sm86 passed;
the registered boundary test,1.2M accepted-prefix oracle steps, accepted-usage
oracle, Windows affinity and IQ AVX2 parity passed. New fresh-count boundary tests
failed before implementation, then passed. Five malformed minimum settings were
rejected before load. Prior C048 routing/config restrictions remain. HIP/SYCL not
built; no upstream review requested. Default-off helper leaves base/tail windows
unchanged in tests; actual default-output byte equivalence is not established
under the preexisting automatic-placement nondeterminism. Full quality is pending.

Use only for further controlled experiments: STRATA_ACCEPTED_USAGE=1,
STRATA_SERIAL_ADAPT_TOKENS=64, STRATA_SERIAL_ADAPT_MIN_PROMPT=1025. Unset/0 token
interval keeps ordinary window-based adaptation. A minimum0 enables the rejected
global policy from C048; it is not recommended. Requires one-GPU serial serving
and active synchronous cache; unsupported helper/peer/batch/pipeline routes fail.
Production config and launcher keep these experimental options off.

All four supervisors passed16GiB physical/commit floors and exact launcher/server/
engine/vision cleanup. Minimum available physical/commit62521552896/40808697856
bytes; maximum sampled GPU25130110976bytes. No process-memory polling during
requests. Production config restored3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0;
idleGPU457MiB. No benchmark model resident. Windows powercfg read-only check shows
High performance scheme8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c already active; no
power-setting mutation or prospective gain claimed.

Next: refresh short-decode profiling on the cumulative native stack before
selecting another kernel/configuration change. Prior P009/P013 traces predate HC1,
accepted usage and this experiment. Reuse profile-goal90-new.ps1 / profile-one-
request-new.py only after inspecting their identity/config/cleanup guards; trace
one warmup plus one measured diagnostic request, never count it as qualifying TPS.
Use dependency/overlap evidence, not summed overlapping durations as saved time.
Full frozen random-coding, cold/warm/cache-hit/vision/tools/reasoning/cancel/max-
context matrix remains required. Q007 two incomplete coding answers unresolved.
Goal remains active and unqualified; no safe experiment is currently blocked.
