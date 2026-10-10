import json,statistics
from pathlib import Path
p=Path(__file__).parent
pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
groups={'off':['R066-grfast-control','R069-grfast-control-reverse'],'on':['R067-grfast-enabled','R068-grfast-enabled-reverse']}
refdir=p/groups['off'][0]; ref=json.loads((refdir/'identity.json').read_text())
result={'engine_sha256':ref['engine_sha256'],'groups':{},'limits':'ABBA with opposite workload order; synthetic parity passed, full coding quality remains unresolved. No promotion.'}
metrics=['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']
for flag,arms in groups.items():
    allrows=[];processes=[]
    for arm in arms:
        a=p/arm; identity=json.loads((a/'identity.json').read_text())
        for key in ['engine_sha256','backend_library_sha256','shards','projector_sha256','expert_profile_sha256']:
            assert identity[key]==ref[key],(arm,key)
        cfg=json.loads(json.dumps(ref['config']));cfg['env']['STRATA_GR_FAST']='1' if flag=='on' else '0'
        assert cfg==identity['config'],arm
        requests=list(a.glob('*.request.json')); assert len(requests)==12
        for request in requests: assert request.read_bytes()==(refdir/request.name).read_bytes(),(arm,request.name)
        assert 'expert cache 8409 slots' in (a/'startup.txt').read_text()
        assert 'Cleanup verified: no live Strata launcher, server, engine or vision process.' in (p/(arm.split('-')[0]+'-wrapper.txt')).read_text()
        rows=[r for r in json.loads((a/'runs.json').read_text()) if not r['warmup']]
        assert len(rows)==10 and all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in rows)
        allrows+=rows
        processes.append({'arm':arm,'summary':json.loads((a/'summary.json').read_text())})
    stats={}
    for w in ['short','longer']:
        rows=[r for r in allrows if r['workload']==w];assert len(rows)==10
        stats[w]={m:{'values':[r[m] for r in rows],'median':statistics.median(r[m] for r in rows),'min':min(r[m] for r in rows),'max':max(r[m] for r in rows)} for m in metrics}
        stats[w]['mtp']={'accepted':sum(r['timings']['draft_n_accepted'] for r in rows),'offered':sum(r['timings']['draft_n'] for r in rows)}
    result['groups'][flag]={'processes':processes,'stats':stats}
d=pub/'diagnostics/hyper-connection';d.mkdir(exist_ok=True)
(d/'abba.json').write_text(json.dumps(result,indent=2)+'\n')
(d/'compare-grfast.py').write_bytes(Path(__file__).read_bytes())
table='| Setting | Workload | Decode tok/s | Prompt tok/s | E2E tok/s | Stream tok/s | TTFT s |\n|---|---|---:|---:|---:|---:|---:|\n'
for flag,g in result['groups'].items():
    for w,s in g['stats'].items():
        table+=f"| {flag} | {w} | {s['server_decode_tps']['median']:.2f} | {s['prompt_tps']['median']:.2f} | {s['request_e2e_tps']['median']:.4f} | {s['stream_total_tps']['median']:.4f} | {s['ttft_seconds']['median']:.4f} |\n"
(d/'table.md').write_text(table)
print(table)
