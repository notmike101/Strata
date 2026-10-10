"""Report every row of the bounded coupled-drafting combination screen."""
import argparse
import json
import statistics
from pathlib import Path

p = Path(__file__).parent
a = argparse.ArgumentParser()
a.add_argument('--complete', action='store_true')
args = a.parse_args()
arms = {'control': ['R112-coupled-stack-control'], 'candidate': ['R113-coupled-stack']}
if args.complete:
    arms['control'].append('R115-coupled-stack-control-reverse')
    arms['candidate'].append('R114-coupled-stack-reverse')
baseline = json.loads((p / arms['control'][0] / 'identity.json').read_text())
metrics = ['server_decode_tps', 'request_e2e_tps', 'stream_total_tps', 'prompt_tps', 'ttft_seconds', 'request_seconds']
result = {'experiment': 'C054', 'complete_abba': args.complete, 'arms': arms, 'cells': {}, 'promoted': False, 'full_quality_matrix_pass': False}
for group, names in arms.items():
    rows = []
    for name in names:
        identity = json.loads((p / name / 'identity.json').read_text())
        for key in ['engine_sha256', 'vision_sha256', 'backend_library_sha256', 'expert_profile_sha256']:
            assert identity[key] == baseline[key], (name, key)
        wanted = '1' if group == 'candidate' else '0'
        config = identity['config']
        for key in ['STRATA_SPEC_COUPLED', 'STRATA_SPEC_GUMBEL']:
            assert config['env'][key] == wanted
        comparable = json.loads(json.dumps(config))
        for key in ['STRATA_SPEC_COUPLED', 'STRATA_SPEC_GUMBEL']:
            comparable['env'][key] = '0'
        assert comparable == baseline['config'], name
        assert 'Cleanup verified: no live Strata' in (p / (name.split('-')[0]+'-wrapper.txt')).read_text()
        raw = json.loads((p / name / 'runs.json').read_text())
        for cell in ['short', 'longer']:
            measured = [r for r in raw if r['workload'] == cell and not r['warmup']]
            assert len(measured) == 5
            payloads = [(p / name / (r['label'] + '.request.json')).read_bytes() for r in measured]
            assert [json.loads(b)['seed'] for b in payloads] == list(range(101, 106))
            for r, payload in zip(measured, payloads):
                assert payload == (p / arms['control'][0] / (r['label'] + '.request.json')).read_bytes()
            assert all(r['completion_tokens'] == 512 and r['cached_tokens'] == 0 for r in measured)
            assert len([r for r in raw if r['workload'] == cell and r['warmup']]) == 1
        rows.extend(dict(r, arm=name) for r in raw if not r['warmup'])
    for cell in ['short', 'longer']:
        rr = [r for r in rows if r['workload'] == cell]
        record = {m: {'raw': [r[m] for r in rr], 'median': statistics.median(r[m] for r in rr), 'min': min(r[m] for r in rr), 'max': max(r[m] for r in rr)} for m in metrics}
        record['count'] = len(rr)
        record['draft_accepted'] = sum(r['timings']['draft_n_accepted'] for r in rr)
        record['draft_offered'] = sum(r['timings']['draft_n'] for r in rr)
        record['acceptance_ratio'] = record['draft_accepted'] / record['draft_offered']
        result['cells'].setdefault(cell, {})[group] = record
losses = []
for cell, groups in result['cells'].items():
    groups['delta_percent'] = {m: 100 * (groups['candidate'][m]['median'] / groups['control'][m]['median'] - 1) for m in metrics}
    for metric in ['server_decode_tps', 'request_e2e_tps', 'prompt_tps']:
        if groups['delta_percent'][metric] < -3:
            losses.append({'cell': cell, 'metric': metric, 'delta_percent': groups['delta_percent'][metric]})
result['screen_losses_over_3_percent'] = losses
result['decision'] = 'reject at prespecified screen' if losses else 'finish reverse-order pair' if not args.complete else 'inspect all gates; no automatic promotion'
print(json.dumps(result, indent=2))
