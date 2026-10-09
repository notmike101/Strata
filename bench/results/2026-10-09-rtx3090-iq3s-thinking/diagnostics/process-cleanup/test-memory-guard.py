import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('memory_guard',Path(__file__).with_name('memory-guard.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
g=1<<30
m.require_headroom(16*g,16*g)
for physical,commit in [(32*g,16*g-1),(16*g-1,32*g),(0,32*g),(32*g,0)]:
    try:m.require_headroom(physical,commit)
    except RuntimeError:continue
    raise AssertionError(f'unsafe headroom accepted: physical={physical},commit={commit}')
print('PASS: physical and commit floors independently enforced')
