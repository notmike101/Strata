## E137 / P016 result and P017 causal control

P016 two fresh identical-config processes completed with exact cleanup. Both
requests have248320finite F32 first-window logits. Warmup: all248320values differ,
maxabs0.718124/meanabs0.101710. Run1: all248320differ,maxabs0.983901/meanabs0.157924.
Argmax1596matches in both cases. Output common prefixes57/44characters. Both
startup profiles/cache sizes match (8409experts,2315borrowed prefill slots).
Routing traces parse completely,54960/55200records; raw first divergence at record26,
layer6, a swapped ordering of the final2expert IDs. However the trace starts with
T4capture/warmup work and lacks explicit request boundaries: this record is NOT
assigned to an actual generated-token position. First-window logit divergence
is the reliable localization, before decode adaptation can be its sole cause.

Source evidence: prefill.cpp:2986-3040 updates CPU share/gate from measured GPU/CPU
layer timing; line3083 selects that share. CPU/GPU arithmetic differs by documented
implementation. This supports but does not yet prove a causal hypothesis.

P017 bounded control: two fresh legs A/B, two exact saved R084 requests each
(shortwarmup100/run1seed101),512tokens. Same8057ab78... binary/context/model/KV/
vision/sampling, accepted-usage0/HC0/DMA0. Add only STRATA_PREFILL_CPU_SHARE=0;
retain existing routing/first-logit instrumentation with leg-specific paths.
Four diagnostic requests total, no throughput qualification or production
promotion. Compare first-logit bit identity and text, alongside original P016.
If first logits still differ, CPU-share timing is not a sufficient explanation;
investigate earlier prompt state rather than more blind performance sweeps.
If logits stabilize, retain as localized evidence; do not infer all decode
reproducibility or quality. GPU-only prompt processing is NOT a candidate winner
without the unchanged no-prompt-rate-degradation and complete quality gates.
Independent16GiB physical/commit guards and exact cleanup/config restoration.
No third pair in this plan. Raw binaries private, summaries/hashes publishable.
