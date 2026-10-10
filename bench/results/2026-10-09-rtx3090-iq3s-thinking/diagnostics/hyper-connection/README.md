# Hyper-connection fast path: complete ABBA comparison

Four fresh processes, one excluded warmup and five measured seeds per workload
per process. The second pair reverses both arm and workload order. Each table
cell is the ordinary median of all ten measured512-token requests, with zero
cached prompt tokens. Request JSON, binary, libraries, model shards, projector,
expert profile and all config except STRATA_GR_FAST match. Cache8409 in all arms.
The script asserts those properties; abba.json preserves every value and process
summary. Hardware, runtime and fixed262144-context thinking profile are unchanged.

| Setting | Workload | Decode tok/s | Prompt tok/s | E2E tok/s | Stream tok/s | TTFT s |
|---|---|---:|---:|---:|---:|---:|
| off | short | 85.00 | 200.35 | 74.4052 | 74.4213 | 0.8716 |
| off | longer | 83.10 | 495.75 | 41.6164 | 41.6201 | 6.1673 |
| on | short | 87.30 | 202.75 | 76.4360 | 76.4482 | 0.8696 |
| on | longer | 83.15 | 496.15 | 41.6442 | 41.6494 | 6.1664 |

Short decode improved2.71%; the longer result is effectively tied (+0.06%).
Both individual paired short and longer decode medians increased, but the second
enabled process had slower short prompt processing. Pooled prompt/client medians
do not regress. Retain as a combination candidate, not a promoted configuration.
This does not meet90 TPS or the full quality/stability/workload matrix. Q007's
two incomplete coding answers remain unresolved. Synthetic bitwise parity is
necessary evidence for unchanged arithmetic, not a substitute for coding quality.
All four arms passed both16GiB memory floors and complete process-tree cleanup.

## Next bounded interaction

E073 found PCIe share0.10 improved longer decode82.2 to85.2 but slightly lowered
short decode87.3 to86.85. Fast HC now improves short and ties longer. Hypothesis:
their different costs (GPU HC arithmetic vs missed-expert transfer/CPU division)
may complement each other. They also share GPU scheduling and host waits, so
additivity is explicitly unproven. No sampler, precision or context change.

Budget: one fresh R070 fast=1/PCIe0.20 control and R071 fast=1/PCIe0.10 candidate,
same fixed short/~3K requests, warmup+five measured seeds each. Only if both
decode medians improve and prompt/client rates do not fall, permit one reversed
pair. Otherwise close this combination. No more repetitions to chase a peak.
Any retention still requires activation and full fixed quality/matrix checks.


## E101 / HC and PCIe interaction closed; next architecture screen

R070/R071 preserve byte-identical request JSON and exact binary, loaded libraries,
GGUF, projector and expert-profile identities; configs differ only in PCIe share.
With HC fast enabled, lowering share0.20 to0.10 changed short decode86.1 to85.9,
longer83.1 to82.9; longer E2E41.6311 to41.6246. This fails the predeclared rule.
Close this interaction without another pair. Peak90.7 is not a qualifying result.
Production launcher and config remain unchanged; full cleanup verified after both
arms. Production config SHA256 is3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0.
Idle GPU after cleanup589MiB. No benchmark model remains resident.

The earlier predeclared four-process HC ABBA comparison remains available in
diagnostics/hyper-connection/abba.json. Include R070 as well when describing the
candidate's cumulative results: all-fast020-runs.json contains all15 measured
rows per workload across R067/R068/R070, not a selected fast subset.

All15 fast/PCIe0.20 short rows: decode median86.50, prompt202.30, E2E75.7012, stream75.7241 tok/s; TTFT0.8710s.

All15 fast/PCIe0.20 longer rows: decode median83.10, prompt496.10, E2E41.6313, stream41.6370 tok/s; TTFT6.1632s.

Remaining architecture hypothesis, not implemented or benchmarked: compress the
BF16 HC projection storage losslessly relative to current packed weights using
the source Q8_0 blocks, reconstruct the exact BF16-rounded coefficients on load,
and preserve the current accumulation tree. P009's HC projection read costs make
bandwidth reduction a plausible mechanism. The existing STRATA_HC_Q8 is NOT this
candidate: fused_gr.cu explicitly changes both weights and reduction order, and
native_dense.cpp adds another allocation without releasing the packed weights.
Do not enable it as a shortcut or call it quality-neutral. A new candidate needs
all-actual-tensor reconstruction parity, graph microbenchmark and finite budget
before any integration or served test. No source or runtime change for this idea.

Q007 still has3/5 compiled/tested answers and2/5 incomplete answers. The full90
TPS contract is not qualified. Keep the objective unchanged. The goal tool still
reported a preexisting blocked status at this turn's entry; the user explicitly
resumed work, but the available update_goal interface cannot set active. No
completion or threshold change was made. The durable campaign retains active
optimization intent and this exact resume checkpoint.
