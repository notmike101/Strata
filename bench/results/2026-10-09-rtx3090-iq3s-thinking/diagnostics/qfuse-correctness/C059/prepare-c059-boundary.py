import json
from pathlib import Path
p=Path(__file__).parent;root=p.parents[1]
files=[json.loads(x) for x in (p/'C059-upstream-files.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.strip()]
def added(name):
    return '\n'.join(x[1:] for x in next(v['patch'] for v in files if v['filename']==name).splitlines() if x.startswith('+') and not x.startswith('+++'))+'\n'
h=(root/'include/strata/kernels/q8_1_finite.hpp').read_text()
h=h.replace('}  // namespace strata::kernels',added('include/strata/kernels/q8_1_finite.hpp')+'\n}  // namespace strata::kernels')
(p/'c059-q8-proposed.cuh').write_text(h)
s=added('tests/qfuse_quant.cu').replace('"strata/kernels/q8_1_finite.hpp"','"c059-q8-proposed.cuh"')
(p/'c059-boundary.cu').write_text(s)
s=(p/'build-c059.cmd').read_text().replace('c059-gdn.cpp','c059-boundary.cu').replace('c059-gdn.exe','c059-boundary.exe')
(p/'build-c059-boundary.cmd').write_text(s)
print('Private boundary fixture prepared; no production quantizer change')
