# C045: complementary HC-fast x batch-transfer matrix

The user explicitly prioritized combining smaller complementary improvements.
This replaces C043's isolated no-regression continuation rule for the NEW combined
configuration; it does not erase prior losses or relax final qualification.

## Inventory

| Status | Change / exact reference | Bottleneck and compatibility | Known interactions |
|---|---|---|---|
| Production retained | CPU F16 vision, CUDA13.3 engine6048736d..., gathered IQ3/MT_MIN1 with IQ2_S gather0, adaptive lag2; F001/F002 full20rows medians87.35/83.30 vs B006 normal CUDA13.3 CPU-vision79.2/73.0 | Frees text VRAM, CPU expert decode, copy overlap; fixed model/context/INT8KV/sampling | This is an already combined stack, not additive attribution. Q007/full90 qualification pending. |
| Implemented, unpromoted | HC-fast STRATA_GR_FAST1; R067/R068 vs R066/R069, same6048736d... binary, PCIe.20/deviceplan0; all10/cell87.30/83.15 vs85.0/83.10 | GPU hyper-connection read arithmetic; C03432bitwise cases; short gain, longer tie | Include R070 too: all15enabled .20 rows86.5/83.1. HC-fast+PCIe.10 R071 lost against R070; that combination remains closed. |
| Implemented, not yet served-tested | Batch transfers STRATA_DMA_BATCH1; C043126byte/event-order checks; P01580successful CUDA batch calls | Fewer CPU submissions/driver calls for adaptive copies; preserves immutable bytes, destinations, stream/event ordering and lag2; no added tensor buffer | Complements GPU HC work but shares PCIe/scheduling. No measured combined gain yet; no sum of percentages. |
| Rolled back, conditional future interaction | IQ3_S-only Clang C042;576actual-weight parity;90offline pool cells15.1%less time; R07587.5/82.6 vs R07487.5/83.3 | CPU GU; isolated short tie/long loss | A faster GPU could expose CPU work currently hidden by overlap. This is a possible DISTINCT interaction, not an automatic reuse. Not in this matrix; requires profiling evidence before a bounded new stack test. |
| Rolled back | PR1166 host sibling C044; R07986.3/83.4 vs R07887.4/84.2 | Host scheduling; correct topology, both decode losses | No current evidence to justify stacking it. |
| Closed | Dual-Q8 C039, Q6onewarp, device planner, PCIe.10+HC-fast, compact CPU cache, lag3/tasks/SMT/residency variants | Each has archived parity, activation and/or served failure | Do not launch a blind powerset or repeat closed combinations. Reopening requires a distinct mechanism/evidence. |
| Compatible upstream reserve | PR1368 quantize/scatter; PR1525 exact prompt fusions/dequant | Prompt processing only; absent locally | Could complement a decode winner and protect read rate; no claim these alone reach90decode. No integration in current matrix. |

## Finite comparison budget and exact next combination

A=HC0/DMA0 (R080), B=HC1/DMA0 (R081), D=HC1/DMA1 (R082),
C=HC0/DMA1 (R083), in that order. The next COMBINATION is D, HC-fast plus batch
adaptive transfers on the already retained production stack. Four fresh process
arms; each one excluded warmup and five measured seeds101..105 for BOTH original
short/~3K cache-miss tasks,512generated tokens, concurrency1. Forty measured
requests plus eight warmups. Same binary6048736d..., backend libraries, model,
262144context, CPU F16vision, INT8KV/32768resident, MTP4/.70, PCIe.20, lag2,
workers9 and tasks30. Fixed coding thinking sampling1/.95/20/0/0/1. Explicit
GR_FAST and DMA_BATCH flags are the only factors; no speculative quality flags.
No other builds/profiling/Git/GUI/process-memory polling during timed requests.
Identity every request;16GiB physical AND commit floors; exact cleanup each arm.

P015 proved batch API activation before this matrix. Prior C034/E098 establishes
HC-fast arithmetic/dispatch; the same executable is used. Check every saved
request byte-for-byte across four arms, every cap/cache count, and all memory
logs. Preserve all results, including R076's earlier control separately.

Primary assessment is D versus A under the full contract. Report B/C as
components and D-B/C-A interactions; do not reject D merely because B or C is
below90 or loses an isolated metric. No selective seeds or favorable medians.
A candidate may remain an unpromoted stack component below target.

Continuation budget: at most ONE reversed D/A pair (20more measured requests),
if D improves either decode median by>=1% while the other decode, prompt and
client medians are no worse than1% versus A. This1% is ONLY a screening allowance
for confirmation, not permission for final degradation. If clearly worse, stop
this combination; if within noise with no>=1%gain, classify inconclusive and
keep data, no extra timing sweep. A confirmed stack can remain experimental
below90. Final promotion still requires90short/85~3K ordinary repeated medians,
no demonstrated prompt/read/quality/stability regression, frozen random coding
and complete cold/warm/cache/tool/vision/max-context matrix. Q007 still pending.
