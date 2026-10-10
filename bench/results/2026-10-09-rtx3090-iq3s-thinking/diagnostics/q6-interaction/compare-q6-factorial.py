"""All-row, identity-checked Q6/PCIe factorial report; no model launch."""
import hashlib, json, statistics
from pathlib import Path
p = Path(__file__).parent
out = p.parents[1] / 'bench/results/2026-10-09-rtx3090-iq3s-thinking'
groups = {
    'A': ('0', '0.20', ['R057-q6-disabled-retry', 'R059-q6-disabled-reverse']),
    'B': ('1', '0.20', ['R054-q6-enabled', 'R058-q6-enabled-reverse']),
    'C': ('0', '0.10', ['R060-q6off-pcie010', 'R063-q6off-pcie010-reverse']),
    'D': ('1', '0.10', ['R061-q6on-pcie010', 'R062-q6on-pcie010-reverse']),
}
metrics = ['server_decode_tps', 'prompt_tps', 'request_e2e_tps', 'stream_total_tps', 'ttft_seconds', 'request_seconds']
ref = json.loads((p / groups['A'][2][0] / 'identity.json').read_text())
refdir = p / groups['A'][2][0]
result = {'engine_sha256': ref['engine_sha256'], 'groups': {}, 'interaction': {},
          'limits': 'Two AB/BA blocks, not a fully interleaved factorial. No full quality or goal qualification. Failed R053/R055 retained separately, not silently discarded.'}
assert ref['engine_sha256'] == '1dfeecd9869c266e82961426026e14c82ff822e0e004898959a900925ea57cf4'
for key, (flag, share, arms) in groups.items():
    rows = []; process = []
    for name in arms:
        a = p / name
        ident = json.loads((a / 'identity.json').read_text())
        for field in ['engine_sha256', 'backend_library_sha256', 'shards', 'projector_sha256', 'expert_profile_sha256']:
            assert ident[field] == ref[field], (name, field)
        expected = json.loads(json.dumps(ref['config']))
        expected['env']['STRATA_Q6_ONEWARP'] = flag
        expected['args'][expected['args'].index('--pcie-frac') + 1] = share
        assert ident['config'] == expected, name
        for request in a.glob('*.request.json'):
            assert request.read_bytes() == (refdir / request.name).read_bytes(), (name, request.name)
        assert len(list(a.glob('*.request.json'))) == 12
        assert 'expert cache 8409 slots' in (a / 'startup.txt').read_text()
        assert 'Cleanup verified: no live Strata launcher, server, engine or vision process.' in (p / (name.split('-')[0] + '-wrapper.txt')).read_text()
        measured = [r for r in json.loads((a / 'runs.json').read_text()) if not r['warmup']]
        assert len(measured) == 10 and all(r['completion_tokens'] == 512 and r['cached_tokens'] == 0 for r in measured)
        rows += measured
        process.append({'arm': name, 'summary': json.loads((a / 'summary.json').read_text())})
    stats = {}
    for workload in ['short', 'longer']:
        rr = [r for r in rows if r['workload'] == workload]; assert len(rr) == 10
        stats[workload] = {metric: {'values': [r[metric] for r in rr],
                                  'median': statistics.median(r[metric] for r in rr),
                                  'min': min(r[metric] for r in rr), 'max': max(r[metric] for r in rr)} for metric in metrics}
        stats[workload]['mtp'] = {'accepted': sum(r['timings']['draft_n_accepted'] for r in rr), 'offered': sum(r['timings']['draft_n'] for r in rr)}
    result['groups'][key] = {'q6_flag': flag, 'pcie_share': share, 'processes': process, 'stats': stats}
for workload in ['short', 'longer']:
    result['interaction'][workload] = {}
    for metric in metrics:
        vals = {k: result['groups'][k]['stats'][workload][metric]['median'] for k in groups}
        result['interaction'][workload][metric] = {'Q6_at_020': vals['B'] - vals['A'], 'Q6_at_010': vals['D'] - vals['C'],
            'difference_of_differences': (vals['D'] - vals['C']) - (vals['B'] - vals['A']),
            'combined_vs_control_percent': 100 * (vals['D'] / vals['A'] - 1)}
folder = out / 'diagnostics/q6-interaction'; folder.mkdir(exist_ok=True)
(folder / 'factorial.json').write_text(json.dumps(result, indent=2) + '\n')
(folder / 'compare-q6-factorial.py').write_bytes(Path(__file__).read_bytes())
table = '| Setting | Q6 | PCIe share | Workload | Decode tok/s | Prompt tok/s | E2E tok/s | Stream tok/s | TTFT s |\n|---|---:|---:|---|---:|---:|---:|---:|---:|\n'
for k, g in result['groups'].items():
    for w, s in g['stats'].items():
        table += f"| {k} | {g['q6_flag']} | {g['pcie_share']} | {w} | {s['server_decode_tps']['median']:.2f} | {s['prompt_tps']['median']:.2f} | {s['request_e2e_tps']['median']:.4f} | {s['stream_total_tps']['median']:.4f} | {s['ttft_seconds']['median']:.4f} |\n"
report = '''# Q6 / PCIe interaction: 80 measured requests

Every cell below contains ten measured runs from two fresh processes, each with
one excluded warmup and five measured seeds. All measured requests generated 512
tokens with zero reused prompt tokens. Input JSON is byte-identical by label.
The binary, loaded CUDA libraries, GGUF shards, projector, expert profile,
262,144 context, INT8 KV, vision and thinking sampling match. Every arm retained
8,409 GPU cache slots. Only the named Q6 flag and PCIe share differ.

These are ordinary medians of every measured row, not averages of process medians.
Per-process summaries, ranges and every raw value are in factorial.json. A/B and
C/D are separate AB/BA blocks; temporal drift is a limitation of this matrix.
The earlier memory failures remain in the ledger and are not hidden by this table.

''' + table + '''
The combination does not reach the target. Compared with PCIe 0.10 alone,
Q6 improves the pooled short decode median but lowers the longer decode median.
It is therefore not a verified improvement across both workloads. Its exact
kernel speedup is real within C030's microbenchmark, but cannot be promoted as a
served-speed win. Production retains its previous engine and settings. All eight
arms completed full-tree cleanup and passed the original host-memory floors.
Full coding, cold/warm, tools, vision and maximum-context qualification is not
claimed. Q007's incomplete coding answers remain an unresolved quality gate.

The arithmetic interaction is retained in factorial.json as (D-C)-(B-A), in each
metric's own units. A positive interaction does not imply that D beats C, reaches
90 tok/s, or meets the prompt/client no-regression requirement.
'''
(folder / 'README.md').write_text(report)
s = (out / 'ledger.md').read_text(); assert '## E089 /' not in s
s += '\n\n## E089 / complete Q6 and PCIe interaction matrix\n\n' + report.split('\n\n', 1)[1]
s += '\nNext: close this Q6/PCIe combination as unpromoted; refresh upstream and test the existing device-side resident-group planning path only after its parity and activation checks. Fixed thinking sampling and goal90 remain unchanged.\n'
(out / 'ledger.md').write_text(s); (p / 'findings.md').write_text(s)
f = out / 'goal-90-state.json'; state = json.loads(f.read_text())
state.update(last_checkpoint='E089', current='Completed80 measured requests in Q6/PCIe interaction matrix; no across-workload served winner or90 TPS qualification. Previous production stack retained.',
             next=['Refresh upstream. Test resident_plan parity and verify activation before a controlled device-planning experiment.'],
             resume_command='No model resident after R063. Read E089 and diagnostics/q6-interaction/README.md; preserve all failed and slow runs.')
f.write_text(json.dumps(state, indent=2) + '\n')
print(table)
