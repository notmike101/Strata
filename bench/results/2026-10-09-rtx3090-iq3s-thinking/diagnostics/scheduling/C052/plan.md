## E162 / C052 finite split-window scheduling screen prepared, not run

Hypothesis: interleaving token groups can hide CPU expert work behind GPU mixer/
router work on this host. Risk: repeated weight reads, smaller batches and more
kernels can outweigh overlap. This is existing --spec-split, not Arc graph-segment
porting. Source's older~7% loss is a warning, not a measurement on this stack.

Same current C051 binary for both arms. A R102 unsplit, B R103 split. Both use
HC-fast1, acceptedusage0, tokenbarrier0 (required by C051), auto prompt share with
MAX1024, DMA0/deviceplan0; lag2,9workers30tasks,PCIe.20,MTP4/.70. Only --spec-split
versus --no-spec-split changes within the pair. Do not compare B directly with
C049 and attribute all differences to scheduling. If promising, correct row-offset
accounting before any future combination with C046/C049; do not bypass the guard.

Exact IQ3_S,262144context,INT8KV/32768resident,CPU F16vision. Fixed thinking profile
temperature1,top_p.95,top_k20,min_p0,presence0,repetition1,frequency0. Identical
original short165/~3K3034 coding payloads,512 generated tokens, concurrency1,
stream/cachemiss,one warmup plus five measured seeds101..105 per workload. All
raw runs retained with ordinary medians, decode/prompt/E2E/stream/TTFT separate.
This is a screen; frozen random coding and full quality matrix remain mandatory.

Finite budget A/B then at most one reversed B/A confirmation if neither decode nor
E2E median loses>3% and neither prompt median loses>2%. Close immediately on these
stop conditions, malformed output, incorrect effective parameters, or memory/
cleanup failure. Pool all10rows/cell if the reverse pair runs; no favorable subset.
No additional split geometry or spec width sweep. Qualifying>90/85 cannot be
claimed from this screen alone. Neither candidate is promoted before full gates.

Before launch inventory exact model/profiler/device users and validate binary/
config identity. Independent16GiB physical/commit floor eachsecond, no per-process
memory polling, no Git/build/GUI/profiler during measured requests. Current
run-c020-arm.py supervisor with --observer audit-no-process; exact whole-tree stop
and production config restore in finally. Runtime proof: exact parsed args plus
successful captured T>=2 windows and source's split_&&T>=2 group selection; retain
any capture on a measured request instead of dropping that seed.
