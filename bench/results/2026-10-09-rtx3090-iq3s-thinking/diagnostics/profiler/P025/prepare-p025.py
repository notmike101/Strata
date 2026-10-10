"""Prepare one guarded C056 new/repeat Nsight capture from audited P020 helpers."""
import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert not (p/'P025-supervisor').exists() and not (p/'P025-short-profile').exists()
cfg=json.loads((p/'R119-prefix-preserve.json').read_text()); cfg['env']['STRATA_DECODE_TIMING']='1'
(p/'P025-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
s=(p/'profile-p020.ps1').read_text().replace('P020','P025').replace('p020','p025')
s=s.replace('Whole measured request including prompt processing','Both measured new/repeat requests including prompt processing')
(p/'profile-p025.ps1').write_text(s)
s=(p/'run-p020.py').read_text().replace('P020','P025').replace('p020','p025')
s=s.replace("assert summary['short']['completion_tokens'] == [512]", "assert set(summary)=={'short/stream/new','short/stream/hit'}\n    assert all(cell['completion_tokens']==[512] for cell in summary.values())")
(p/'run-p025.py').write_text(s)
note='''## E236 / P025 current-stack short new/repeat Nsight capture

Previous goal turn was progress: P023/P024 proved reduced physical refill work but located short repeat-read regression in verifier windows, not a direct staging cost. Current HEAD25f34499, no tracked edits at entry, only known unrelated untracked profile/key files. No inference/profiler resident; GPU457MiB/0percent. Use exact C056 cc85c6c7 engine/R119 configuration, adding only STRATA_DECODE_TIMING=1. No source/build, target sampler, context, MTP4/.70,PCIe.20 or production-launcher changes.

One fresh process and four byte-identical saved R129 requests: short-warmup-new,short-warmup-hit,short-run-1-new,short-run-1-hit. Both warmups precede collection. Capture the complete measured new/repeat pair in one Nsight Systems2026.5.1 software CUDA graph-node session. CUDA event tracing, CPU sampling/context-switch tracing and GPU phase stamps remain disabled;1s flush. Retain host decode timers per request. This capture includes prompt processing and the inter-request identity-check gap. Whole-capture sums must not be called decode-only, per-request, critical-path or removable latency. Split request activity only if trace boundaries can be corroborated; otherwise keep aggregate and host-request results separate.

Questions: how much current per-window time is verifier GPU reach, CPU expert work, draft, commit/emit and other host work? Which kernel/copy categories dominate the traced path? Do the saved-window observations support reducing fixed window overhead, or is CPU/expert placement the larger constraint? Existing P020 predates coupled/prefix staging and cannot establish these current costs. This is one diagnostic capture, not qualifying repetitions or a favorable repeat of R128-R131.

Reuse audited P020 launch/supervision/cleanup behavior under unique P025 paths/session. Same independent16GiB physical/commit floors each second, live identity checks before each request, no other model/build/profiler/process-memory or GUI polling during inference. Exact session and model-tree cleanup and production-config restoration in finally. Raw nsys-rep/SQLite remain private because they can contain captured environment metadata; publish only allowlisted timing/count summaries and sanitized scripts. Audit graph/API record consistency before drawing conclusions.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True); f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/profiler/P025'; put(d/'plan.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E236 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E236',current='P025 single current-stack new/repeat Nsight diagnostic declared.',next=['Run guarded run-p025.py; inspect host decode timers and export/audit CUDA records.','Select an exact optimization from current evidence; keep failed cache screen and full goal active.']); put(f,json.dumps(s,indent=2)+'\n')
print('P025 config/supervisor/wrapper prepared')
