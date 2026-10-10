## E151 / C049 longer-prefill-only cache barriers

Previous goal turn was progress: C048 global barriers rejected for short decode
-3.95%, while ~3K decode improved6.16%. Candidate source was archived and restored.
C049 is a distinct policy-composition experiment, not a rerun of that failed arm.
Reuse its tested64-token boundary mechanism only after a request freshly reads
at least1025 prompt tokens. Prefill consumes all but the final prompt token, and
the existing CPU-sharing limit is chunks below1024. Thus this threshold follows
the existing prompt-path boundary, not the specific3034-token fixture. Cached
long contexts with short fresh suffixes retain window-based adaptation. Rejected
draft rows still do not count; synchronization and64-token interval stay fixed.

Default off. Gate tests cover fresh1/1024/1025/262144, configured interval0,
minimum0 and cached-suffix semantics. Preserve CUDA/math/model/quant/sampling,
262144context,INT8KV/32768resident,CPU F16vision,MTP4/.70,PCIe.20,lag2,HC1 and
acceptedusage1,DMA0/deviceplan0,9workers30tasks. Both arms use auto prompt share
with explicitMAX1024: fixed80 was not a promoted performance win. This differs
from C048 in both arms; only the barrier option differs within this new pair.

Bounded comparison A R098 control0, B R099 conditional64; each fresh process,
one warmup+five measured seeds101..105 per original short/~3K cell,512tokens,
streaming/cachemiss/concurrency1. Byte-identical payloads; no arithmetic or
sampling change. If any decode/E2E median loses>3% or prompt median loses>2%,
close without confirmation. Otherwise one reverse B R100/A R101 pair maximum;
pool all10rows/cell ordinary medians. No threshold or interval sweep. Since short
requests run before long ones, repeated short results also test the new binary's
inactive branch; mixed history in the reverse workload order remains a later
gate, not an implied guarantee. R096/97 remain unused closed-C048 reservations.

16GiB physical/commit floors, no per-process polling during requests, no builds/
Git/GUI/profiler concurrently. Exact process-tree cleanup/config restore eacharm.
Require runtime log proof short interval0 and long interval64, seven updates per
512-token longer request. If retained, test boundary-neighbor workloads, cache
hits, fresh cold and random coding before promotion. Full quality/workload gates
unchanged;512-token throughput screens do not prove compilable answer quality.
