import csv,hashlib,importlib.util,json,subprocess,time,psutil
from datetime import datetime,timezone
from pathlib import Path
p=Path(__file__).parent.resolve()
assert not (p/'C058-timing.txt').exists()
for proc in psutil.process_iter(['pid','name']):
    assert not (proc.info['name'] or '').lower().startswith(('strata','llama-','nsys','nvcc','cl.exe')),proc.info
spec=importlib.util.spec_from_file_location('guard',p/'memory-guard.py'); guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
guard.require_headroom(*guard.memory_headroom())
manifest=json.loads((p/'C058-manifest.json').read_text())
for w in manifest['input_weights']:
    assert hashlib.sha256((p/'C036-private'/f"{w['id']}.bf16").read_bytes()).hexdigest()==w['sha256']
manifest.update(executable_sha256=hashlib.sha256((p/'c058-screen.exe').read_bytes()).hexdigest(),harness_sha256=hashlib.sha256((p/'c058-screen.cu').read_bytes()).hexdigest(),utc=datetime.now(timezone.utc).isoformat())
(p/'C058-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with (p/'C058-timing.txt').open('w') as log,(p/'C058-safety.csv').open('w',newline='') as safe:
    writer=csv.writer(safe);writer.writerow(['utc','physical_available','commit_available']); child=None
    try:
        child=subprocess.Popen([str(p/'c058-screen.exe'),str(p/'C036-private')],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        start=time.monotonic()
        while True:
            values=guard.memory_headroom();writer.writerow([datetime.now(timezone.utc).isoformat(),*values]);safe.flush();guard.require_headroom(*values)
            if child.poll() is not None:break
            if time.monotonic()-start>180:raise RuntimeError('Microbenchmark timeout')
            time.sleep(1)
        if child.returncode:raise RuntimeError('Screen exit '+str(child.returncode))
    finally:
        if child and child.poll() is None:child.terminate();child.wait(timeout=10)
print('C058 process completed; inspect all timing cells before integration')
