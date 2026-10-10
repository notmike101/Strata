import csv,hashlib,importlib.util,json,subprocess,time,psutil
from datetime import datetime,timezone
from pathlib import Path
p=Path(__file__).resolve().parent
assert not (p/'C062-combine-only-result.txt').exists()
for proc in psutil.process_iter(['pid','name']):
    assert not (proc.info['name'] or '').lower().startswith(('strata','llama-','nsys','nvcc','cl.exe')),proc.info
spec=importlib.util.spec_from_file_location('guard',p/'memory-guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
guard.require_headroom(*guard.memory_headroom())
m=json.loads((p/'C062-combine-only-manifest.json').read_text());m.update(executable_sha256=hashlib.sha256((p/'c062-combine-only.exe').read_bytes()).hexdigest(),harness_sha256=hashlib.sha256((p/'c062-combine-only.cu').read_bytes()).hexdigest(),utc=datetime.now(timezone.utc).isoformat())
with (p/'C062-combine-only-result.txt').open('w') as log,(p/'C062-combine-only-safety.csv').open('w',newline='') as safe:
    writer=csv.writer(safe);writer.writerow(['utc','physical_available','commit_available']);child=None
    try:
        child=subprocess.Popen([str(p/'c062-combine-only.exe')],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);start=time.monotonic()
        while True:
            values=guard.memory_headroom();writer.writerow([datetime.now(timezone.utc).isoformat(),*values]);safe.flush();guard.require_headroom(*values)
            if child.poll() is not None:break
            if time.monotonic()-start>180:raise RuntimeError('Fixture timeout')
            time.sleep(1)
        m['exit_code']=child.returncode
        assert child.returncode in (0,1),'Unexpected execution failure'
    finally:
        if child and child.poll() is None:child.terminate();child.wait(timeout=10)
(p/'C062-combine-only-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Fixture exit',m['exit_code'],'; all cases retained')
