"""Complete all-run PCIe comparison; never select only favorable process medians."""
import hashlib
import json
import statistics
from pathlib import Path

p = Path(__file__).parent
arms = {'A': ['R047-fresh-control', 'R051-control-reverse'],
        'B': ['R049-pcie010', 'R050-pcie010-reverse']}
metrics = ['server_decode_tps', 'prompt_tps', 'request_e2e_tps',
           'stream_total_tps', 'ttft_seconds', 'request_seconds']
result = {'order': ['R047-fresh-control', 'R049-pcie010',
                    'R050-pcie010-reverse', 'R051-control-reverse'],
          'settings': {'A': 0.20, 'B': 0.10}, 'workloads': {}}
reference = json.loads((p / arms['A'][0] / 'identity.json').read_text())
for names in arms.values():
    for name in names:
        ident = json.loads((p / name / 'identity.json').read_text())
        assert ident['engine_sha256'] == reference['engine_sha256']
        assert ident['backend_library_sha256'] == reference['backend_library_sha256']
        config = json.loads(json.dumps(ident['config']))
        config['args'][config['args'].index('--pcie-frac') + 1] = '0.20'
        assert config == reference['config'], name
        assert 'Cleanup verified: no live Strata launcher, server, engine or vision process.' in (p / (name.split('-')[0] + '-wrapper.txt')).read_text()
for workload in ['short', 'longer']:
    cell = {'payload_sha256': {}, 'settings': {}}
    for label in ['warmup'] + [f'run-{i}' for i in range(1, 6)]:
        payloads = [(p / name / f'{workload}-{label}.request.json').read_bytes()
                    for names in arms.values() for name in names]
        assert all(v == payloads[0] for v in payloads), (workload, label)
        cell['payload_sha256'][label] = hashlib.sha256(payloads[0]).hexdigest()
    for setting, names in arms.items():
        rows = []
        process_medians = {}
        for name in names:
            rr = [r for r in json.loads((p / name / 'runs.json').read_text())
                  if r['workload'] == workload and not r['warmup']]
            assert len(rr) == 5
            assert all(r['completion_tokens'] == 512 and r['cached_tokens'] == 0 for r in rr)
            process_medians[name] = {m: statistics.median(r[m] for r in rr) for m in metrics}
            rows.extend(dict(r, arm=name) for r in rr)
        cell['settings'][setting] = {
            'n': len(rows), 'process_medians': process_medians,
            'metrics': {m: {'all_runs': [r[m] for r in rows],
                            'median': statistics.median(r[m] for r in rows),
                            'min': min(r[m] for r in rows), 'max': max(r[m] for r in rows)} for m in metrics},
            'draft_accepted': sum(r['timings']['draft_n_accepted'] for r in rows),
            'draft_offered': sum(r['timings']['draft_n'] for r in rows),
            'raw_rows': rows}
    cell['candidate_percent_change'] = {m: 100 * (cell['settings']['B']['metrics'][m]['median'] /
                                                cell['settings']['A']['metrics'][m]['median'] - 1)
                                       for m in metrics}
    result['workloads'][workload] = cell
result['limits'] = ['Original TTLCache streaming cache-miss workload only.',
                    'Two fresh processes and ten measured rows per setting and workload.',
                    'Five seeds repeat across processes; runs are not independent samples of all prompts.',
                    'Full quality, random coding and cold/warm workload matrix not passed; unpromoted.',
                    'Pooled medians do not replace individual-process qualification gates.']
(p / 'pcie-abba-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
for w, cell in result['workloads'].items():
    print(w, json.dumps({s: {m: v['median'] for m, v in data['metrics'].items()}
                         for s, data in cell['settings'].items()}))
    print('candidate_percent_change', json.dumps(cell['candidate_percent_change']))
