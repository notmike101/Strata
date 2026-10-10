import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
root=Path('C:/Strata');p=root/'local-setup/target-80';out=p/'deployment-c056'
assert not out.exists();out.mkdir()
cfg=root/'strata-iq3_s.json';launcher=Path('<USER_HOME>/scripts/Start-Strata-Qwen38-Flash-Next-GSQ-RCO-IQ3_S-Vision.ps1')
candidate=p/'R119-prefix-preserve.json'
old=json.loads(cfg.read_text());new=json.loads(candidate.read_text())
assert {k:v for k,v in old.items() if k not in ('exe','env')}=={k:v for k,v in new.items() if k not in ('exe','env')}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(cfg)=='3457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0'
assert sha(Path(new['exe']))=='cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91'
assert not new.get('api_key') and new['host']=='0.0.0.0'
shutil.copy2(cfg,out/'previous-config.json');shutil.copy2(launcher,out/'previous-launcher.ps1')
cfg.write_bytes(candidate.read_bytes())
record={'utc':datetime.now(timezone.utc).isoformat(),'authorization':'User explicitly requested the launcher use the new optimized engine and configuration after disclosure of incomplete qualification.','candidate':'C056 / R119-prefix-preserve','engine_sha256':sha(Path(new['exe'])),'previous_config_sha256':sha(out/'previous-config.json'),'deployed_config_sha256':sha(cfg),'changed_config_fields':['exe','env'],'fully_qualified':False,'previous_launcher_sha256':sha(out/'previous-launcher.ps1')}
(out/'deployment.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
