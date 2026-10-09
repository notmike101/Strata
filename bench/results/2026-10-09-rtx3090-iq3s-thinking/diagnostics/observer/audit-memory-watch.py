"""Time each observer API group, with no model launch or machine changes."""
import json,sys,statistics
from pathlib import Path
base=Path(__file__).with_name('memory-watch.py')
source=base.read_text().split('start=time.monotonic();cpu=time.process_time();samples=0')[0]
exec(compile(source,str(base),'exec'))
rows=[]
def timed(name,fn):
    wall=time.perf_counter();cpu=time.process_time();result=fn()
    rows.append({'utc':datetime.now(timezone.utc).isoformat(),'api':name,'wall_ms':1000*(time.perf_counter()-wall),'cpu_ms':1000*(time.process_time()-cpu)})
    return result
def nv_memory():
    m=Mem();return call('nvmlDeviceGetMemoryInfo',[C.c_void_p,C.POINTER(Mem)],h,C.byref(m))
def process_memory():
    total=0
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower().startswith('strata'):total+=proc.memory_info().rss
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    return total
def system_memory():
    m=WinMem();m.length=C.sizeof(m);return C.windll.kernel32.GlobalMemoryStatusEx(C.byref(m))
def paging():
    pdh.PdhCollectQueryData(query);c=Counter();return pdh.PdhGetFormattedCounterValue(counter,0x200,None,C.byref(c))
start=time.monotonic()
try:
    while time.monotonic()-start<a.seconds and not a.out.with_suffix('.stop').exists():
        timed('nvml_memory',nv_memory);timed('global_memory',system_memory)
        if not a.skip_process:timed('process_memory',process_memory)
        timed('pdh_paging',paging)
        timed('nvml_clock',lambda:value('nvmlDeviceGetClockInfo',1));timed('nvml_power',lambda:value('nvmlDeviceGetPowerUsage'));timed('nvml_temperature',lambda:value('nvmlDeviceGetTemperature',0));timed('nvml_clock_reasons',reasons)
        time.sleep(1)
finally:
    pdh.PdhCloseQuery(query);call('nvmlShutdown',[])
    a.out.write_text(json.dumps({'rows':rows,'summary':{name:{k:{'median':statistics.median([r[k] for r in rows if r['api']==name]),'max':max(r[k] for r in rows if r['api']==name)} for k in ['wall_ms','cpu_ms']} for name in sorted({r['api'] for r in rows})}},indent=2)+'\n')
print(json.dumps(json.loads(a.out.read_text())['summary'],indent=2))
