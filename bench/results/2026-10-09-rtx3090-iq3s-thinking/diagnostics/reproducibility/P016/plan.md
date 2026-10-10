## E136 / P016 finite first-divergence diagnostic

Previous turn was progress: completed C046 six-arm combination and confirmation,
retained disabled experimental component and published08602c45. Current goal
remains90/85 with full quality/matrix unresolved. No model resident at entry.

Two fresh processes, P016-A and P016-B, same C0468057ab78... engine with both
accepted-usage and HC disabled (the exact repeated control that showed divergent
outputs). Each sends the saved R084 short warmup seed100 and short-run1 seed101,
byte-identical512-token streaming payloads, unchanged thinking coding parameters,
262144context, INT8KV/32768resident, CPU F16vision and9workers/30tasks. Sole
instrumentation: existing --dump-routing and STRATA_DUMP_FIRST_LOGITS. Output
paths differ per leg; no new engine code or sampling modification. Four requests
total, one warmup+one diagnostic per leg. NO throughput qualification from these
instrumented one-run cells. No further legs without new evidence and written plan.

Compare complete first-window logits (248320F32values/request), routed expert IDs,
window sizes inferred from per-layer trace records, and generated text prefixes.
Preserve truncated final routing record if abrupt server cleanup leaves one;
never mistake a truncated tail for an early divergence. Trace records have no
explicit request boundary; identify fresh T1/layer0 patterns cautiously, compare
chronological prefix without inventing positions. First divergence localization
does not establish its root cause. Existing source shows seed forwarding and
Philox(seed,position); timing-based draft policy plus placement/shape rounding are
hypotheses. No claim of altered seed or changed nonce. Independent16GiB physical
AND commit guards and exact cleanup/config restoration per leg. Raw binary
traces/logits stay private; publish hashes and parsed aggregate diagnostics only.
