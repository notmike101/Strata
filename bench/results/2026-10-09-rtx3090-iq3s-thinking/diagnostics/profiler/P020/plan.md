## E157 / P020 refreshed cumulative-stack short-request profile

Previous goal turn was progress: C049 four-arm comparison finished, source and
ledger pushed d1a15b1c. Candidate89.1/85.0 versus89.4/82.9 control; no promotion.
Refresh profiler evidence before another change. Existing P009/P013 predate HC1
and accepted-usage accounting. Do not infer the remaining bottleneck from them.

One fresh process, exact R099 short warmup(seed100) and short-run1(seed101)
payloads,512tokens each, streaming/cachemiss, frozen thinking coding profile,
IQ3_S/262144/INT8KV/CPU F16vision. Current engineac43e898,HC1/accepted1,auto prompt
share/MAX1024,conditional64/minfresh1025 (inactive for this165-token request),
DMA0/deviceplan0,MTP4/.70,PCIe.20,9workers30tasks. Only host decode timers added.
Nsight Systems2026.5.1 graph-node software trace, CUDA events disabled,1s flush,
CPU sampling/context-switch tracing disabled. Start after warmup, stop after the
entire measured request. Capture includes prompt processing; never label total
GPU sums as decode-only. No GPU phase stamps or source changes.

Finite budget one capture. Independent16GiB physical/commit guard eachsecond,
preflight process inventory, identity-checked requests, exact profile-session and
launcher/model/vision cleanup and production config restore in finally. No other
model/build/profiler/GUI or process-memory polling during generation. Raw nsys-rep
and SQLite stay private; export only selected stats and diagnostics. Audit record
consistency before conclusions; absence of records is not proof of GPU idle.
Overlapping kernel/copy sums and interval unions are not a dependency critical
path or removable latency. Instrumented TPS is diagnostic, never qualification.
