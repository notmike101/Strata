import argparse,json,subprocess,time,psutil,sys
from pathlib import Path
import importlib.util
guard_spec=importlib.util.spec_from_file_location('memory_guard',Path(__file__).with_name('memory-guard.py'))
memory_guard=importlib.util.module_from_spec(guard_spec);guard_spec.loader.exec_module(memory_guard)
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--goal-coding',action='store_true');p.add_argument('--mode',default='stream');p.add_argument('--cache-hits',action='store_true');p.add_argument('--reverse-order',action='store_true');a=p.parse_args()
root=Path(r'C:\Strata');local=Path(__file__).parent;python=root/'.venv/Scripts/python.exe';cfg=root/'strata-iq3_s.json'
if a.out.exists():raise RuntimeError('Refuse to overwrite prior arm')
for proc in psutil.process_iter(['pid','name','exe']):
    n=(proc.info['name'] or '').lower()
    if n.startswith(('strata','llama-','nsys','nsight')) or n in ('nvcc.exe','cl.exe'):
        raise RuntimeError('Existing inference/profiler/build process: '+str(proc.info))
a.out.mkdir(parents=True);previous=cfg.read_bytes()
memory_guard.require_headroom(*memory_guard.memory_headroom())
candidate=json.loads(a.candidate.read_text()); engine_log=Path(candidate['log'])
log_offset=engine_log.stat().st_size if engine_log.exists() else 0
monitor=None
try:
    with (a.out/'monitor-log.txt').open('w') as log:
        monitor=subprocess.Popen([str(python),str(local/'memory-watch.py'),'--out',str(a.out/'resources.csv'),'--seconds','3600'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        with (a.out/'prepare.txt').open('w') as prep:
            subprocess.run([str(python),str(local/'run-arm.py'),str(a.candidate),'--no-benchmark'],check=True,stdout=prep,stderr=subprocess.STDOUT)
        raw=engine_log.read_bytes(); startup=raw[log_offset:] if len(raw)>=log_offset else raw
        (a.out/'startup.txt').write_bytes(startup)
        if candidate.get('env',{}).get('STRATA_CPU_IQ3S_CACHE_GIB'):
            if b'exact IQ3_S CPU cache: ready; 9043968000 bytes' not in startup:
                raise RuntimeError('Requested compact cache not proven active in startup')
        if monitor.poll() is not None:raise RuntimeError('Resource monitor exited')
        memory_guard.require_headroom(*memory_guard.memory_headroom())
        if a.goal_coding:
            client=local/'goal90-benchmark.py';extra=['--mode',a.mode]+(['--cache-hits'] if a.cache_hits else [])
        else:client=local.parent/'coding-best-practices/benchmark.py';extra=[]
        cmd=[str(python),str(client),'--config',str(cfg),'--out',str(a.out),'--runs','5']+extra+(['--reverse-order'] if a.reverse_order else [])
        (a.out/'client-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
        with (a.out/'client-log.txt').open('w') as benchlog:
            child=subprocess.Popen(cmd,stdout=benchlog,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            start=time.monotonic()
            while child.poll() is None:
                try:
                    memory_guard.require_headroom(*memory_guard.memory_headroom())
                    if time.monotonic()-start>2400:raise RuntimeError('Safety timeout stop')
                except Exception:
                    child.terminate();child.wait();raise
                time.sleep(1)
            if child.returncode:raise RuntimeError('Benchmark failed: '+str(child.returncode))
        print('COMPLETE',a.out,flush=True)
finally:
    try:
        subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(local.parent/'optimization-262k/server.ps1'),'-Action','Stop'],check=True)
    finally:
        cfg.write_bytes(previous)
        if monitor:
            time.sleep(3);(a.out/'resources.stop').touch();monitor.wait(timeout=10)
