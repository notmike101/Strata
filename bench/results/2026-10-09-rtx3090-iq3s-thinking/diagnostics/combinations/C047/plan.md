## E139 / P018 measured share and C047 cumulative fixed-share plan

P018 completed and cleaned up.90calibrated readings, CPU share median0.7870875,
range0.759230..0.813005. Predeclared rounding selects exactly0.80. No fraction
sweep. Debug-only engine5d43a376...; all readings and source patch retained.
The diagnostic printf extension is removed from working source after capture;
C047 uses the previously tested8057ab78... engine, no debug/routing/logit hooks.

C047 immediate control is C046's EXACT combined stack: HC-fast1, accepted-row
accounting1,DMA0/deviceplan0, CUDA13.3,IQ3_S,262144context, INT8KV/32768resident,
CPU F16vision,MTP4/.70,PCIe.20,lag2,9workers30tasks. Only added performance factor
is fixed CPU prompt share0.80 versus auto (unset). BOTH arms explicitly set
STRATA_PREFILL_CPU_SHARE_MAX=1024 to keep the ~3K prompt path unchanged. Numeric
sampling remains thinking high/xhigh unlimited,1/.95/20/0/0/1,frequency0. This
preserves the user-prioritized complementary stack and isolates the new setting.

Budget: Aauto R090, Bfixed80 R091, Bfixed80 R092, Aauto R093. Each fresh process,
one excluded warmup+5measured seeds101..105 for BOTH original short/~3K tasks,
512tokens,cachemiss,concurrency1.40measured requests,8warmups maximum. No profiling,
builds,Git,GUI or process-memory polling during timing; audit-no-process and
independent16GiBphysical/commit floors. Exact cleanup and config restoration.
If B first pass has any prompt median worse>2% or decode/E2E worse>3%, stop this
candidate without confirmation (diagnostic-only stability does not waive loss).
Otherwise complete the single reversed B/A confirmation pair. No additional
pair/sweep. Pool all10qualifying rows per workload/cell with ordinary medians.

Compare exact payload and output hashes for B/B and A/A, MTP offered/accepted,
cache counters, prompt/decode/client/stream/TTFT and memory. Identical output is
reproducibility evidence, not a quality proof; fixed-share determinism is not
assumed from GPU-only P017. No90/85claim without frozen random coding and full
quality/cold-warm/tool/vision/maxcontext matrix. A smaller reproducible gain may
remain an unpromoted component. Final no-degradation contract is unchanged;
screening tolerances only decide whether to spend confirmation requests.
