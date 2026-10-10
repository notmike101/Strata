from pathlib import Path
import json
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking');d=pub/'diagnostics/combinations/C048'
d.mkdir(parents=True,exist_ok=True)
note=(p/'C048-plan.md').read_text(encoding='utf-8')
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text(encoding='utf-8');assert '## E147 /' not in s;f.write_text(s+'\n\n'+note,encoding='utf-8')
(d/'plan.md').write_text(note,encoding='utf-8')
for arm,on in [('R094-barrier0',False),('R095-barrier64',True),('R096-barrier64',True),('R097-barrier0',False)]:
 c=json.loads((p/'R091-stack-share80.json').read_text(encoding='utf-8'))
 c['exe']=r'C:\strata\engine\strata-cuda133-token-barrier.exe'
 c['env']['STRATA_SERIAL_ADAPT_TOKENS']='64' if on else '0'
 (p/(arm+'.json')).write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
f=pub/'goal-90-state.json';v=json.loads(f.read_text(encoding='utf-8'));v.update(last_checkpoint='E147',current='C048 default-off single-GPU accepted-token barrier candidate in build; red/green CPU boundary test passed.',next=['Build CUDA and run registered CPU tests; then finite R094/R095 comparison.'],resume_command='Read E147/C048 plan. Same branch. C048 source uncommitted; production unchanged.');f.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
