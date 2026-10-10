import argparse,csv,json,subprocess,time,psutil,sys
from datetime import datetime,timezone
from pathlib import Path
import importlib.util
guard_spec=importlib.util.spec_from_file_location('memory_guard',Path(__file__).with_name('memory-guard.py'))
memory_guard=importlib.util.module_from_spec(guard_spec);guard_spec.loader.exec_module(memory_guard)
spec_guard_spec=importlib.util.spec_from_file_location('spec_quality_guard',Path(__file__).with_name('spec-quality-guard.py'))
spec_guard=importlib.util.module_from_spec(spec_guard_spec);spec_guard_spec.loader.exec_module(spec_guard)
resident_spec=importlib.util.spec_from_file_location('resident_guard',Path(__file__).with_name('resident-mode-guard.py'))
resident_guard=importlib.util.module_from_spec(resident_spec);resident_spec.loader.exec_module(resident_guard)
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--goal-coding',action='store_true');p.add_argument('--goal-quality',action='store_true');p.add_argument('--goal-quality-expanded',action='store_true');p.add_argument('--routing-diagnostic',action='store_true');p.add_argument('--mode',default='stream');p.add_argument('--cache-hits',action='store_true');p.add_argument('--reverse-order',action='store_true');p.add_argument('--observer',choices=['full','safety','audit','audit-no-process'],default='full');a=p.parse_args()
if sum([a.goal_coding,a.goal_quality,a.goal_quality_expanded,a.routing_diagnostic]) > 1:p.error('Choose one client workload')
root=Path(r'C:\Strata');local=Path(__file__).parent;python=root/'.venv/Scripts/python.exe';cfg=root/'strata-iq3_s.json'
if a.out.exists():raise RuntimeError('Refuse to overwrite prior arm')
candidate=json.loads(a.candidate.read_text())
spec_guard.require_spec_quality(candidate)
for proc in psutil.process_iter(['pid','name','exe']):
    n=(proc.info['name'] or '').lower()
    if n.startswith(('strata','llama-','nsys','nsight')) or n in ('nvcc.exe','cl.exe'):
        raise RuntimeError('Existing inference/profiler/build process: '+str(proc.info))
a.out.mkdir(parents=True);previous=cfg.read_bytes()
(a.out/'supervisor.py').write_bytes(Path(__file__).read_bytes())
for helper in ['spec-quality-guard.py', 'memory-guard.py', 'resident-mode-guard.py']:
    (a.out/helper).write_bytes((local/helper).read_bytes())
(a.out/'effective-sampling-modes.json').write_text(json.dumps(spec_guard.sampling_mode_manifest(candidate),indent=2)+'\n')
memory_guard.require_headroom(*memory_guard.memory_headroom())
engine_log=Path(candidate['log'])
log_offset=engine_log.stat().st_size if engine_log.exists() else 0
monitor=None
safety_file=(a.out/'safety.csv').open('w',newline='',encoding='utf-8')
safety_writer=csv.writer(safety_file);safety_writer.writerow(['utc','physical_available','commit_available','phase'])
def check_safety(phase):
    physical,commit=memory_guard.memory_headroom()
    safety_writer.writerow([datetime.now(timezone.utc).isoformat(),physical,commit,phase]);safety_file.flush()
    memory_guard.require_headroom(physical,commit)
def wait_child(child,phase,timeout):
    start=time.monotonic()
    while child.poll() is None:
        try:
            check_safety(phase)
            if time.monotonic()-start>timeout:raise RuntimeError('Safety timeout stop')
        except Exception as error:
            (a.out/'failure.json').write_text(json.dumps({'phase':phase,'error':str(error),'utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
            child.terminate();child.wait();raise
        time.sleep(1)
    if child.returncode:raise RuntimeError(phase+' failed: '+str(child.returncode))
try:
    with (a.out/'monitor-log.txt').open('w') as log:
        if a.observer=='full':monitor=subprocess.Popen([str(python),str(local/'memory-watch.py'),'--out',str(a.out/'resources.csv'),'--seconds','3600'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        if a.observer=='audit':monitor=subprocess.Popen([str(python),str(local/'audit-memory-watch.py'),'--out',str(a.out/'observer-audit.json'),'--seconds','3600'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        if a.observer=='audit-no-process':monitor=subprocess.Popen([str(python),str(local/'audit-memory-watch.py'),'--out',str(a.out/'observer-audit.json'),'--seconds','3600','--skip-process'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        (a.out/'observer.json').write_text(json.dumps({'mode':a.observer,'safety_floor_bytes':16*(1<<30),'safety_interval_seconds':1},indent=2)+'\n')
        with (a.out/'prepare.txt').open('w') as prep:
            child=subprocess.Popen([str(python),str(local/'run-arm.py'),str(a.candidate),'--no-benchmark'],stdout=prep,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            wait_child(child,'prepare',660)
        raw=engine_log.read_bytes(); startup=raw[log_offset:] if len(raw)>=log_offset else raw
        (a.out/'startup.txt').write_bytes(startup)
        if candidate.get('env',{}).get('STRATA_ACCEPTED_USAGE') == '1':
            if b'accepted-row adaptive usage enabled (serial, committed inputs only)' not in startup:
                raise RuntimeError('Requested accepted-row cache accounting not proven active')
        modes=spec_guard.sampling_mode_manifest(candidate)
        if modes.get('STRATA_SPEC_COUPLED') == '1' and modes.get('STRATA_SPEC_PROB') in (None,'','0'):
            if b'coupled draft sampling on (STRATA_SPEC_COUPLED)' not in startup:
                raise RuntimeError('Requested coupled drafting not proven active')
        barrier=candidate.get('env',{}).get('STRATA_SERIAL_ADAPT_TOKENS','0')
        if barrier != '0':
            marker=f'serial cache barrier every {int(barrier)} accepted input tokens'.encode()
            if marker not in startup:
                raise RuntimeError('Requested token cache barrier not proven active')
        if '--resident-experts' in candidate.get('args',[]):
            proof=resident_guard.require_resident_startup(startup,require_rotation=spec_guard.effective_environment(candidate).get('STRATA_EXCHANGE_ROTATE')=='1')
            (a.out/'resident-startup-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
        if candidate.get('env',{}).get('STRATA_CPU_IQ3S_CACHE_GIB'):
            if b'exact IQ3_S CPU cache: ready; 9043968000 bytes' not in startup:
                raise RuntimeError('Requested compact cache not proven active in startup')
        if monitor and monitor.poll() is not None:raise RuntimeError('Resource monitor exited')
        check_safety('ready')
        if a.goal_quality_expanded:
            client=local/'goal90-quality-expanded.py';extra=[]
        elif a.goal_quality:
            client=local/'goal90-quality.py';extra=[]
        elif a.routing_diagnostic:
            client=local/('p019-client.py' if a.candidate.stem.startswith('P019-') else 'p016-client.py');extra=[]
        elif a.goal_coding:
            client=local/'goal90-benchmark.py';extra=['--mode',a.mode]+(['--cache-hits'] if a.cache_hits else [])
        else:client=local.parent/'coding-best-practices/benchmark.py';extra=[]
        cmd=[str(python),str(client),'--config',str(cfg),'--out',str(a.out),'--runs','5']+extra+(['--reverse-order'] if a.reverse_order else [])
        (a.out/'client-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
        with (a.out/'client-log.txt').open('w') as benchlog:
            child=subprocess.Popen(cmd,stdout=benchlog,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            wait_child(child,'benchmark',7200 if a.goal_quality_expanded else 2400)
        print('COMPLETE',a.out,flush=True)
finally:
    try:
        try:
            if engine_log.exists():
                raw=engine_log.read_bytes()
                (a.out/'engine-session.txt').write_bytes(raw[log_offset:] if len(raw)>=log_offset else raw)
        finally:
            subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(local.parent/'optimization-262k/server.ps1'),'-Action','Stop'],check=True)
    finally:
        cfg.write_bytes(previous)
        safety_file.close()
        if monitor:
            time.sleep(3);(a.out/'resources.stop').touch();(a.out/'observer-audit.stop').touch()
            try:monitor.wait(timeout=10)
            except subprocess.TimeoutExpired:
                monitor.terminate();monitor.wait(timeout=10)
                (a.out/'monitor-forced-stop.json').write_text(json.dumps({'pid':monitor.pid,'reason':'observer did not exit within10seconds after model cleanup'})+'\n')
