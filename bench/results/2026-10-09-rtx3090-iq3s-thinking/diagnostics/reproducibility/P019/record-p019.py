from pathlib import Path
import json, re

p=Path('local-setup/target-80')
pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
d=pub/'diagnostics/reproducibility/P019'
def put(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',text).replace('<LAN_HOST>','<LAN_HOST>')
    path.write_text(text,encoding='utf-8')
result=json.loads((d/'summary.json').read_text(encoding='utf-8'))
note=(p/'P019-conclusion.md').read_text(encoding='utf-8')
put(d/'README.md',note)
for path in [p/'findings.md',pub/'ledger.md']:
    text=path.read_text(encoding='utf-8')
    assert '## E146 /' not in text
    put(path,text+'\n\n'+note)
for arm in result['arms']:
    for name in ['safety.csv','observer.json','observer-audit.json','engine-session.txt','startup.txt','prepare.txt','supervisor.py','effective-sampling-modes.json']:
        put(d/arm/name,(p/arm/name).read_text(encoding='utf-8'))
    put(d/arm/'supervisor-output.txt',(p/(arm+'-wrapper.txt')).read_text(encoding='utf-8'))
for name in ['analyze-p019.py','p019-client.py','prepare-p019.py','record-p019.py']:
    put(d/name,(p/name).read_text(encoding='utf-8'))
f=pub/'goal-90-state.json'
v=json.loads(f.read_text(encoding='utf-8'))
v.update(last_checkpoint='E146',current='P019 diagnostic pair closed; see detailed conclusion. C047 remains unpromoted; 90/85 and full quality not qualified.',next=['Review P019 evidence before selecting accepted-token cache barrier architecture.'],resume_command='Read E145-E146 and diagnostics/reproducibility/P019. No model resident. Remain on perf/rtx3090-thinking-80. Production unchanged; build tree still contains P018 debug objects.',safety='P019 A/B: all eighteen 512-token requests passed 16 GiB physical/commit guards; exact process cleanup and production config restore verified.')
put(f,json.dumps(v,indent=2)+'\n')
print('Recorded E146/P019')
