"""Bounded activation profile with independent memory floors and full cleanup."""
import csv, importlib.util, json, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
import psutil
p = Path(__file__).parent.resolve(); root = p.parents[1]
cfg = root / 'strata-iq3_s.json'; arm = p / 'P025-supervisor'
assert not arm.exists(), 'Refuse to overwrite a prior diagnostic'
for proc in psutil.process_iter(['pid', 'name']):
    name = (proc.info['name'] or '').lower()
    assert not name.startswith(('strata', 'llama-', 'nsys', 'nvcc', 'cl.exe')), proc.info
spec = importlib.util.spec_from_file_location('guard', p / 'memory-guard.py')
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
guard.require_headroom(*guard.memory_headroom())
arm.mkdir(); previous = cfg.read_bytes(); child = None
spec_guard_spec=importlib.util.spec_from_file_location('spec_guard',p/'spec-quality-guard.py')
spec_guard=importlib.util.module_from_spec(spec_guard_spec); spec_guard_spec.loader.exec_module(spec_guard)
candidate=json.loads((p/'P025-config.json').read_text())
spec_guard.require_spec_quality(candidate)
(arm/'effective-sampling-modes.json').write_text(json.dumps(spec_guard.sampling_mode_manifest(candidate),indent=2)+'\n')
logpath = Path(json.loads(previous)['log']); offset = logpath.stat().st_size if logpath.exists() else 0
(arm / 'supervisor.py').write_bytes(Path(__file__).read_bytes())
try:
    cfg.write_bytes((p / 'P025-config.json').read_bytes())
    with (arm / 'safety.csv').open('w', newline='') as sf, (p / 'P025-wrapper.txt').open('w') as log:
        writer = csv.writer(sf); writer.writerow(['utc', 'physical_available', 'commit_available'])
        child = subprocess.Popen(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(p / 'profile-p025.ps1')],
                                 stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        started = time.monotonic()
        while child.poll() is None:
            values = guard.memory_headroom(); writer.writerow([datetime.now(timezone.utc).isoformat(), *values]); sf.flush()
            guard.require_headroom(*values)
            if time.monotonic() - started > 720: raise RuntimeError('Profile safety timeout')
            time.sleep(1)
        if child.returncode: raise RuntimeError('Profile wrapper exit ' + str(child.returncode))
    summary = json.loads((p / 'P025-short-profile/summary.json').read_text())
    assert set(summary)=={'short/stream/new','short/stream/hit'}
    assert all(cell['completion_tokens']==[512] for cell in summary.values())
    assert (p / 'P025-decode.nsys-rep').is_file()
    print('P025 capture complete; not a qualifying TPS arm', flush=True)
except Exception as error:
    (arm / 'failure.json').write_text(json.dumps({'error': str(error)}, indent=2) + '\n')
    if child and child.poll() is None: child.terminate(); child.wait(timeout=10)
    raise
finally:
    try:
        nsys = root / '.tools/n5/ProgramFiles64Folder/NVIDIA Corporation/Nsight Systems 2026.5.1/target-windows-x64/nsys.exe'
        with (arm / 'cleanup.txt').open('w') as log:
            try:
                subprocess.run([str(nsys), 'shutdown', '--session=strata90p025', '--kill=false'], stdout=log, stderr=subprocess.STDOUT, timeout=30)
            finally:
                subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(p.parent / 'optimization-262k/server.ps1'), '-Action', 'Stop'],
                               stdout=log, stderr=subprocess.STDOUT, timeout=60, check=True)
    finally:
        cfg.write_bytes(previous)
        if logpath.exists():
            raw = logpath.read_bytes(); (arm / 'engine-session.txt').write_bytes(raw[offset:] if len(raw) >= offset else raw)
