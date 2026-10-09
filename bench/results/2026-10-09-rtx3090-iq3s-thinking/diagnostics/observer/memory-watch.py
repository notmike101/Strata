"""Read-only NVML device snapshots; no profiler injection or settings changes."""
import argparse, csv, ctypes as C, json, time
from datetime import datetime, timezone
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); p.add_argument('--seconds',type=int,default=300); p.add_argument('--skip-process',action='store_true'); a=p.parse_args()
nv=C.CDLL(r'C:\Windows\System32\nvml.dll')
def call(name, types, *args):
    f=getattr(nv,name); f.argtypes=types; f.restype=C.c_int
    return f(*args)
assert call('nvmlInit_v2',[])==0
h=C.c_void_p()
assert call('nvmlDeviceGetHandleByIndex_v2',[C.c_uint,C.POINTER(C.c_void_p)],0,C.byref(h))==0
def value(name,*selectors):
    v=C.c_uint()
    rc=call(name,[C.c_void_p]+[C.c_uint]*len(selectors)+[C.POINTER(C.c_uint)],h,*selectors,C.byref(v))
    return v.value if rc==0 else f'NVML_ERROR_{rc}'
class NvValue(C.Union):
    _fields_=[('d',C.c_double),('si',C.c_int),('ui',C.c_uint),('ul',C.c_ulong),('ull',C.c_ulonglong),('sll',C.c_longlong)]
class NvField(C.Structure):
    _fields_=[('id',C.c_uint),('scope',C.c_uint),('timestamp',C.c_longlong),('latency',C.c_longlong),
              ('type',C.c_int),('rc',C.c_int),('value',NvValue)]
def field(fid):
    f=NvField(); f.id=fid
    rc=call('nvmlDeviceGetFieldValues',[C.c_void_p,C.c_int,C.POINTER(NvField)],h,1,C.byref(f))
    if rc or f.rc:return f'NVML_ERROR_{rc or f.rc}'
    return getattr(f.value,{0:'d',1:'ui',2:'ul',3:'ull',4:'sll',5:'si'}[f.type])
def reasons():
    v=C.c_ulonglong()
    rc=call('nvmlDeviceGetCurrentClocksEventReasons',[C.c_void_p,C.POINTER(C.c_ulonglong)],h,C.byref(v))
    return v.value if rc==0 else f'NVML_ERROR_{rc}'

import psutil
class Mem(C.Structure):
    _fields_=[('total',C.c_ulonglong),('free',C.c_ulonglong),('used',C.c_ulonglong)]
class WinMem(C.Structure):
    _fields_=[('length',C.c_ulong),('load',C.c_ulong)]+[(n,C.c_ulonglong) for n in ['totalPhys','availPhys','totalPage','availPage','totalVirtual','availVirtual','availExtended']]
class CounterUnion(C.Union):
    _fields_=[('double',C.c_double),('long',C.c_long),('large',C.c_longlong)]
class Counter(C.Structure):
    _fields_=[('status',C.c_ulong),('value',CounterUnion)]
pdh=C.WinDLL('pdh'); query=C.c_void_p(); counter=C.c_void_p()
pdh.PdhOpenQueryW.argtypes=[C.c_wchar_p,C.c_size_t,C.POINTER(C.c_void_p)]
pdh.PdhAddEnglishCounterW.argtypes=[C.c_void_p,C.c_wchar_p,C.c_size_t,C.POINTER(C.c_void_p)]
pdh.PdhCollectQueryData.argtypes=[C.c_void_p]
pdh.PdhGetFormattedCounterValue.argtypes=[C.c_void_p,C.c_ulong,C.c_void_p,C.POINTER(Counter)]
pdh.PdhCloseQuery.argtypes=[C.c_void_p]
assert pdh.PdhOpenQueryW(None,0,C.byref(query))==0
assert pdh.PdhAddEnglishCounterW(query,r'\Memory\Pages Input/sec',0,C.byref(counter))==0
pdh.PdhCollectQueryData(query)
start=time.monotonic();cpu=time.process_time();samples=0
try:
    with a.out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['utc','gpu_used','gpu_free','ram_available','commit_available','engine_rss','engine_private','pages_input_sec','sm_MHz','power_mW','gpu_C','clock_event_mask']);w.writeheader()
        while time.monotonic()-start<a.seconds and not a.out.with_suffix('.stop').exists():
            mem=Mem();rc=call('nvmlDeviceGetMemoryInfo',[C.c_void_p,C.POINTER(Mem)],h,C.byref(mem))
            wm=WinMem();wm.length=C.sizeof(wm);assert C.windll.kernel32.GlobalMemoryStatusEx(C.byref(wm))
            rss=private=None if a.skip_process else 0
            for proc in ([] if a.skip_process else psutil.process_iter(['name'])):
                try:
                    if proc.info['name'].lower().startswith('strata'):
                        info=proc.memory_info();rss+=info.rss;private+=info.private
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            pdh.PdhCollectQueryData(query);count=Counter()
            cr=pdh.PdhGetFormattedCounterValue(counter,0x200,None,C.byref(count))
            pages=getattr(count.value,'double') if cr==0 and count.status in (0,1) else None
            w.writerow(dict(utc=datetime.now(timezone.utc).isoformat(),gpu_used=mem.used if rc==0 else None,gpu_free=mem.free if rc==0 else None,
                ram_available=wm.availPhys,commit_available=wm.availPage,engine_rss=rss,engine_private=private,pages_input_sec=pages,
                sm_MHz=value('nvmlDeviceGetClockInfo',1),power_mW=value('nvmlDeviceGetPowerUsage'),gpu_C=value('nvmlDeviceGetTemperature',0),clock_event_mask=reasons()))
            f.flush();samples+=1;time.sleep(1)
finally:
    pdh.PdhCloseQuery(query);call('nvmlShutdown',[])
    a.out.with_suffix('.json').write_text(json.dumps(dict(samples=samples,wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu,
        note='One-second snapshots, not exact peaks. Pages Input/sec is system-wide, not engine attribution.'),indent=2)+'\n')
