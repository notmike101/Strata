from pathlib import Path
import json
p=Path(__file__).parent;pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking');d=pub/'diagnostics/profiler/P020';d.mkdir(parents=True,exist_ok=True)
cfg=json.loads((p/'R099-conditional64.json').read_text(encoding='utf-8'))
cfg['env']['STRATA_DECODE_TIMING']='1'
(p/'P020-config.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8')
s=(p/'profile-goal90-new.ps1').read_text(encoding='utf-8').replace('P009','P020').replace('strata90new','strata90p020').replace('profile-one-request-new.py','profile-p020.py')
s=s.replace("capture='CUDA graph nodes, one request,1000ms flush interval, CUDA event tracing disabled, no GPU phase stamps, host decode timers only'","capture='Whole measured request including prompt processing; CUDA graph nodes;1000ms flush; event tracing disabled; host decode timers; diagnostic only'")
(p/'profile-p020.ps1').write_text(s,encoding='utf-8')
s=(p/'profile-one-request-new.py').read_text(encoding='utf-8').replace("read_text()","read_text(encoding='utf-8')").replace('strata90new','strata90p020')
start=s.index('def payload(run):');end=s.index("ask('short-warmup'",start)
s=s[:start]+'''def payload(run):
    label='short-warmup' if run==0 else 'short-run-1'
    return json.loads((Path(__file__).parent/'R099-conditional64'/(label+'.request.json')).read_text(encoding='utf-8'))
'''+s[end:]
s=s.replace('One bounded complete-request profile; not a qualifying throughput repetition set.','P020 exact R099 short payload replay, includes prompt processing; only one measured profile, no TPS qualification.')
(p/'profile-p020.py').write_text(s,encoding='utf-8')
s=(p/'run-p012.py').read_text(encoding='utf-8').replace('P012','P020').replace('P020-device-plan.json','P020-config.json').replace('profile-device-plan.ps1','profile-p020.ps1').replace('strata90device','strata90p020')
(p/'run-p020.py').write_text(s,encoding='utf-8')
note='''## E157 / P020 refreshed cumulative-stack short-request profile

Previous goal turn was progress: C049 four-arm comparison finished, source and
ledger pushed d1a15b1c. Candidate89.1/85.0 versus89.4/82.9 control; no promotion.
Refresh profiler evidence before another change. Existing P009/P013 predate HC1
and accepted-usage accounting. Do not infer the remaining bottleneck from them.

One fresh process, exact R099 short warmup(seed100) and short-run1(seed101)
payloads,512tokens each, streaming/cachemiss, frozen thinking coding profile,
IQ3_S/262144/INT8KV/CPU F16vision. Current engineac43e898,HC1/accepted1,auto prompt
share/MAX1024,conditional64/minfresh1025 (inactive for this165-token request),
DMA0/deviceplan0,MTP4/.70,PCIe.20,9workers30tasks. Only host decode timers added.
Nsight Systems2026.5.1 graph-node software trace, CUDA events disabled,1s flush,
CPU sampling/context-switch tracing disabled. Start after warmup, stop after the
entire measured request. Capture includes prompt processing; never label total
GPU sums as decode-only. No GPU phase stamps or source changes.

Finite budget one capture. Independent16GiB physical/commit guard eachsecond,
preflight process inventory, identity-checked requests, exact profile-session and
launcher/model/vision cleanup and production config restore in finally. No other
model/build/profiler/GUI or process-memory polling during generation. Raw nsys-rep
and SQLite stay private; export only selected stats and diagnostics. Audit record
consistency before conclusions; absence of records is not proof of GPU idle.
Overlapping kernel/copy sums and interval unions are not a dependency critical
path or removable latency. Instrumented TPS is diagnostic, never qualification.
'''
for f in [p/'findings.md',pub/'ledger.md']:
 text=f.read_text(encoding='utf-8');assert '## E157 /' not in text;f.write_text(text+'\n\n'+note,encoding='utf-8')
(d/'plan.md').write_text(note,encoding='utf-8')
f=pub/'goal-90-state.json';v=json.loads(f.read_text(encoding='utf-8'));v.update(last_checkpoint='E157',current='P020 one bounded short-request Nsight capture planned on cumulative stack; no performance qualification.',next=['Capture with guarded run-p020.py; audit recorded activity and decode host timers.']);f.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
