from pathlib import Path
import json,hashlib,numpy as np,os
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
stats=[]
for i in range(2):
 fa=p/f'P016-A-logits.{i}';fb=p/f'P016-B-logits.{i}';a=np.fromfile(fa,dtype=np.float32);b=np.fromfile(fb,dtype=np.float32)
 assert len(a)==len(b)==248320 and np.isfinite(a).all() and np.isfinite(b).all()
 stats.append({'request':i,'bit_identical':fa.read_bytes()==fb.read_bytes(),'different_values':int(np.count_nonzero(a!=b)),'max_absolute_difference':float(np.max(abs(a-b))),'mean_absolute_difference':float(np.mean(abs(a-b))),'argmax_A':int(a.argmax()),'argmax_B':int(b.argmax()),'sha256_A':hashlib.sha256(fa.read_bytes()).hexdigest(),'sha256_B':hashlib.sha256(fb.read_bytes()).hexdigest()})
d=pub/'diagnostics/reproducibility/P016';(d/'logits-summary.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
note='''## E137 / P016 result and P017 causal control

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
'''
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text(encoding='utf-8');assert '## E137 /' not in s;f.write_text(s+'\n\n'+note,encoding='utf-8')
d=pub/'diagnostics/reproducibility/P017';d.mkdir(parents=True,exist_ok=True);(d/'plan.md').write_text(note,encoding='utf-8')
for leg in ['A','B']:
 c=json.loads((p/'R084-usage0-hc0.json').read_text(encoding='utf-8'));c['args']+=['--dump-routing',str((p/f'P017-{leg}-routing.bin').resolve())];c['env'].update(STRATA_PREFILL_CPU_SHARE='0',STRATA_DUMP_FIRST_LOGITS=str((p/f'P017-{leg}-logits').resolve()));(p/f'P017-{leg}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
print('P017 prelaunch plan recorded')
