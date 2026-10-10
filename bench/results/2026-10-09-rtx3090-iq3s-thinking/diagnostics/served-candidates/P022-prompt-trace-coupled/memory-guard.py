import ctypes

def require_headroom(physical, commit, floor=16*(1<<30)):
    if physical < floor or commit < floor:
        raise RuntimeError(f'Safety headroom stop: physical={physical}, commit={commit}, minimum={floor} bytes')

def memory_headroom():
    class Status(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(name,ctypes.c_ulonglong) for name in ('totalPhys','availPhys','totalPage','availPage','totalVirtual','availVirtual','availExtended')]
    status=Status();status.length=ctypes.sizeof(status)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GlobalMemoryStatusEx.argtypes=[ctypes.POINTER(Status)]
    if not kernel.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError(ctypes.get_last_error())
    return status.availPhys,status.availPage
