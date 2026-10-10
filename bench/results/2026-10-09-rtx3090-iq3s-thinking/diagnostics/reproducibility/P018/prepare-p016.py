from pathlib import Path
import json
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
note='''## E136 / P016 finite first-divergence diagnostic

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
'''
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text(encoding='utf-8');assert '## E136 /' not in s;f.write_text(s+'\n\n'+note,encoding='utf-8')
d=pub/'diagnostics/reproducibility/P016';d.mkdir(parents=True,exist_ok=True);(d/'plan.md').write_text(note,encoding='utf-8')
for leg in ['A','B']:
 c=json.loads((p/'R084-usage0-hc0.json').read_text(encoding='utf-8'));c['args']+=['--dump-routing',str((p/f'P016-{leg}-routing.bin').resolve())];c['env']['STRATA_DUMP_FIRST_LOGITS']=str((p/f'P016-{leg}-logits').resolve());(p/f'P016-{leg}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
f=pub/'goal-90-state.json';v=json.loads(f.read_text(encoding='utf-8'));v.update(last_checkpoint='E136',current='P016 bounded first-divergence diagnostics; no code/sampling changes.',resume_command='Read E135/E136; source includes disabled C046 candidate08602c45; current C046 binary8057ab78..., production6048736d... unchanged.',safety='All six C046 arms passed16GiB floors and exact cleanup. Idle GPU457MiB; no model resident at checkpoint.');f.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
print('P016 finite plan saved')
