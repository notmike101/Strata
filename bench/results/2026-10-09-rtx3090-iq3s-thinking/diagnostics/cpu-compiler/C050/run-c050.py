"""Finite offline parity/timing gate; no model server or GPU allocations."""
import csv, hashlib, importlib.util, json, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
import psutil

p = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('guard', p / 'memory-guard.py')
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    name = (proc.info['name'] or '').lower()
    cmd = ' '.join(proc.info['cmdline'] or [])
    assert not name.startswith(('strata', 'llama-', 'nsys', 'nvcc', 'cl.exe', 'clang-cl', 'c050-')), proc.info
    assert '-m serve.server' not in cmd, proc.info
out = p / 'C050-run'
assert not out.exists(), 'Refuse overwrite'
guard.require_headroom(*guard.memory_headroom())
out.mkdir()
models = [str(Path('C:/models/Qwen3.8-Flash-Next/IQ3_S') / f'Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-0000{i}-of-00002.gguf') for i in (1,2)]
record = {'utc': datetime.now(timezone.utc).isoformat(), 'model_paths': models, 'phases': []}
with (out / 'safety.csv').open('w', newline='') as sf:
    writer = csv.writer(sf); writer.writerow(['utc','phase','physical_available','commit_available'])
    for phase in ('actual','pool'):
        exe = p / f'c050-{phase}.exe'
        entry = {'phase': phase, 'sha256': hashlib.sha256(exe.read_bytes()).hexdigest()}
        record['phases'].append(entry)
        child = None
        try:
            guard.require_headroom(*guard.memory_headroom())
            with (out / f'{phase}.txt').open('w') as log:
                child = subprocess.Popen([str(exe), *models], stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                entry['pid'] = child.pid; start = time.monotonic()
                print(f'C050 {phase} pid={child.pid}', flush=True)
                while child.poll() is None:
                    values = guard.memory_headroom()
                    writer.writerow([datetime.now(timezone.utc).isoformat(),phase,*values]); sf.flush()
                    guard.require_headroom(*values)
                    if time.monotonic()-start > 900: raise RuntimeError('Finite phase timeout')
                    time.sleep(1)
                entry.update(exit_code=child.returncode, seconds=time.monotonic()-start)
                if child.returncode: raise RuntimeError(f'{phase} exit {child.returncode}')
                print(f'C050 {phase} passed exit=0', flush=True)
        except Exception as error:
            entry['error'] = str(error)
            raise
        finally:
            if child and child.poll() is None: child.terminate(); child.wait(timeout=10)
            entry['cleanup_complete'] = child is None or child.poll() is not None
            (out / 'manifest.json').write_text(json.dumps(record, indent=2)+'\n')
print('C050 finite offline gates complete; timing results still require analysis', flush=True)
