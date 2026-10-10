"""Build the test before implementing one-warp Q6; extract original helpers verbatim."""
from pathlib import Path
p = Path(__file__).parent
source = (p.parents[1] / 'src/kernels/cuda/native_mmvq.cu').read_text()
def extract(start):
    i = source.index(start); brace = source.index('{', i); depth = 1; j = brace + 1
    while depth:
        depth += (source[j] == '{') - (source[j] == '}'); j += 1
    return source[i:j]
prefix = source[:source.index('#include')]
prefix += '#include "strata/kernels/native_mmvq.hpp"\n#include "strata/kernels/dp4a.hpp"\n#include <cuda_fp16.h>\n#include <cuda_runtime.h>\n#include <cstdint>\n#include <stdexcept>\n'
prefix += 'namespace strata::kernels { namespace {\nconstexpr int WARP=32;\n'
prefix += extract('struct Q81Block') + ';\n' + extract('struct Q6KBlock') + ';\n'
prefix += 'static_assert(sizeof(Q81Block)==36 && sizeof(Q6KBlock)==210);\n'
for name in ['__device__ __forceinline__ float warp_sum(', '__device__ __forceinline__ int load_int_b2(',
             '__device__ __forceinline__ float q6_q8_dot_impl(', '__device__ __forceinline__ float q6_q8_dot(']:
    prefix += extract(name) + '\n'
prefix += '} }\n'
(p / 'c029-original-helpers.inl').write_text(prefix)
stub = '''#include "c029-original-helpers.inl"
namespace strata::kernels {
void c029_mmvq(int rows,const void*,const void*,float*y,int,int n_out,cudaStream_t stream) {
    cudaMemsetAsync(y,0,n_out*sizeof(float),stream); // deliberately wrong RED stub
}
}
'''
(p / 'c029-onewarp.inl').write_text(stub)
(p / 'c029-red-stub.inl').write_text(stub)
s = (p / 'c028-dense-test.cu').read_text()
s = s.replace('// Diagnostic only. Compile the reference and candidate in one translation unit.', '// Diagnostic only. Candidate links against the unchanged C022 native reference library.')
s = s.replace('#include "src/kernels/cuda/native_mmvq.cu"\n#include "c021-rowgroup.inl"', '#include "c029-onewarp.inl"')
s = s.replace('c021_mmvq', 'c029_mmvq').replace('rows_per_cta', 'warps_per_cta').replace('C028 contract', 'C029 contract')
(p / 'c029-dense-test.cu').write_text(s)
(p / 'build-c029-dense.cmd').write_text((p / 'build-c028-dense.cmd').read_text().replace('c028-dense-test', 'c029-dense-test').replace('-std=c++17', '-std=c++20'))
print('C029 test, unchanged helpers and intentionally incorrect RED stub prepared')
