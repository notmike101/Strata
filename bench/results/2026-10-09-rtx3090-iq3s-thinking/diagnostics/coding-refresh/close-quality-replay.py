"""Close the preregistered Q012/Q013 diagnosis without replacing quality evidence."""
import json
from pathlib import Path

p = Path(__file__).parent
pub = p.parents[1] / 'bench/results/2026-10-09-rtx3090-iq3s-thinking'
dest = pub / 'diagnostics/coding-refresh'
names = ['Q012-replay-candidate', 'Q013-replay-production']
audits = [json.loads((dest / n / 'audit.json').read_text()) for n in names]
assert all(a['diagnostic_only'] and not a['full_quality_qualified'] for a in audits)
for seed in [101, 102, 103]:
    assert (p / names[0] / f'coding-{seed}.request.json').read_bytes() == (p / names[1] / f'coding-{seed}.request.json').read_bytes()
assert audits[0]['focus_seed_103_completed'], 'Interpretation requires candidate non-reproduction'
note = '''## E192 / bounded replay closes; no causal component identified

The immediately preceding user-question response explained metrics and made no optimization progress. This continuation authoritatively polled live session32540, completed its audit, and ran the already registered production replay serially. No run was restarted because an observation expired.

Q012 did not reproduce the candidate seed103 cap failure. Three requests in the original101/102/103 order all completed and passed72tests. Q013 provides the matched production replay below. Request files are byte-identical between arms and to the corresponding expanded suite. Fresh process per arm; no warmup; fixed32768 allowance and unchanged numerical thinking profile, checker, model, context and vision. Prior generated text and hidden adaptive-cache state need not be identical even with the same request seeds.

| Seed | Candidate tokens / outcome | Production tokens / outcome |
|---|---|---|
'''
for c, a in zip(audits[0]['checks'], audits[1]['checks']):
    note += f"| {c['seed']} | {c['completion_tokens']} / {c['finish_reason']} / pass={c['passed']} | {a['completion_tokens']} / {a['finish_reason']} / pass={a['passed']} |\n"
note += '''
This ends the one-pair diagnosis. Do not rerun the unchanged configuration until a favorable result appears, and do not attribute the earlier cap failure to HC or accepted-row accounting without causal evidence. Q010 remains4/5 and ineligible for promotion; Q011 remains5/5 for production only. Three passing diagnostic answers never replace the full five-answer gate. All earlier failures and generated answers remain published. Fixed512-token speed measurements are separate.

Qualification assessment before another speed test:

- Retained production has Q011 five completed answers passing all72tests, but is not certified to meet the new90/85 speed goal. Its previous real-use checks remain historical evidence.
- Experimental C051 HC/accepted-usage/conditional-barrier stack has R110/R111 selected-coding streaming medians93.6/89.35, but original-workload R112 short88.7 is below90. Its Q010 quality gate failed4/5. These are two independent blockers to promotion.
- Current experimental stack still lacks two qualifying confirmations of selected-coding nonstream misses and exact-repeat hits in both modes, plus refreshed mixed-history, tools, vision, reasoning controls, cancellation, idle and near-limit checks. No old production result certifies this stack.
- Q012 is diagnostic evidence only and does not clear any missing full-quality or workload gate. A broad component ablation is unsupported by this non-reproduction.

Next: resume the already preregistered C054 combination screen, R113 coupled/Gumbel drafting on the unchanged HC/accepted-usage/conditional-barrier stack versus R112. This is an explicitly new candidate, not continued qualification of the failed unchanged candidate. The bounded speed screen comes before a costly full matrix because the existing candidate is already ineligible and below the original-workload short target. This tests a new composition of existing mechanisms, not a quality retry or promotion. Numeric sampling and all fixed workload settings remain unchanged. If either decode/E2E/prompt median loses more than3percent, reject after the first pair; otherwise finish the bounded reverse-order R114/R115 comparison and pool every measured row. New seeded streams require their own full quality and real-use gates before any promotion. No production launcher changes.
'''
for f in [p / 'findings.md', pub / 'ledger.md']:
    old = f.read_text(encoding='utf-8')
    assert '## E192 /' not in old
    f.write_text(old + '\n\n' + note, encoding='utf-8', newline='\n')
(dest / 'replay-comparison.md').write_text(note, encoding='utf-8', newline='\n')
state = json.loads((pub / 'goal-90-state.json').read_text())
state.update(last_checkpoint='E192', current='Bounded replay closed: candidate seed103 failure not reproduced; full quality failure retained.', next=['C054 R113 paired screen; stop on preregistered loss or finish R114/R115 reverse order.', 'No quality promotion from three-request diagnosis.'], resume_command='Q012/Q013 exact cleanup verified. Inspect live state, then run R113 once with the guarded supervisor.')
(pub / 'goal-90-state.json').write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8', newline='\n')
print(note)
