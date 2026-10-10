## E173 / frozen coding baseline and completion-quality refresh

Previous goal turn was progress: six full served arms completed, C052/C053 rejected,
C053 source restored and ledger pushed7e4f5d7a. The fixed goal is90tok/s in both
short and~3K cells; no threshold or sampling change in this refresh.

Use existing randomly selected topological_order fixture SHA25616fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5,
unchanged task/reference, seeds101..105,512output tokens, one warmup per short/
longer streaming cache-miss cell. Two fresh processes R110 short-first/R111
longer-first. Native C051 engine0dea69dc, HC1/accepted1/conditional64/minfresh1025,
IQ3_S262144 INT8KV/32768resident CPUF16vision, MTP4/.70,PCIe.20,lag2,9workers30tasks,
auto prompt shareMAX1024,DMA0/deviceplan0. Numeric thinking1/.95/20/0/0/1 and
frequency0, unlimited reasoning unchanged. No coupled/probabilistic sampler flags.
This is an additional fixed-workload baseline, not an optimization gain against
historical B011 or proof that every cold/cache-hit/nonstream cell passes.

Then Q008 uses the same original quality payloads from Q007, five seeds101..105,
separate8192-token natural-stop allowance and72objective tests per final function.
Do not substitute those throughput values for512-token speed results. Preserve
incomplete answers as failures, keep the cap and prompt fixed. No new variant or
parameter sweep during these checks. Q0073/5 remains historical failed evidence.

Preflight no inference/compiler/profiler, GPU457MiB, config3457fdfe restored.
Independent16GiB physical/commit guard eachsecond, no process-memory polling,
exact launcher/server/model/vision cleanup and config restoration per process.
R110 started; its live exec handle was91599. Do not start a second server.
