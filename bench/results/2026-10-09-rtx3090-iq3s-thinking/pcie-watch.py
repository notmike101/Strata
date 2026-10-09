"""Read-only NVML device snapshots; no profiler injection or settings changes."""
import argparse, csv, ctypes as C, json, time
from datetime import datetime, timezone
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); p.add_argument('--seconds',type=int,default=300); a=p.parse_args()
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
start=time.monotonic(); cpu=time.process_time(); samples=0
try:
    with a.out.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['utc','pcie_tx_KB_s','pcie_rx_KB_s','sm_MHz','memory_MHz','power_mW','gpu_C','pcie_gen','pcie_width'])
        while time.monotonic()-start<a.seconds and not a.out.with_suffix('.stop').exists():
            w.writerow([datetime.now(timezone.utc).isoformat(),value('nvmlDeviceGetPcieThroughput',0),
                value('nvmlDeviceGetPcieThroughput',1),value('nvmlDeviceGetClockInfo',1),
                value('nvmlDeviceGetClockInfo',2),value('nvmlDeviceGetPowerUsage'),value('nvmlDeviceGetTemperature',0),
                value('nvmlDeviceGetCurrPcieLinkGeneration'),value('nvmlDeviceGetCurrPcieLinkWidth')])
            f.flush(); samples+=1; time.sleep(1)
finally:
    call('nvmlShutdown',[])
    meta=dict(samples=samples,wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu,
        note='NVML PCIe counters sample a 20 ms interval, polled once per second; snapshots, not a continuous trace or per-process attribution. NVML units KB/s retained without conversion.')
    a.out.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta))
