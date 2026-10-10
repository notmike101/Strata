// Arithmetic adapted from the MIT-licensed pinned ggml CUDA
// moe-weighted-reduction.cu at 3cf03257f219afbe7334045ff7c6a06ac68c627d.
// MIT License
// Copyright (c) 2023-2026 The ggml authors
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
#include <cuda_runtime.h>
#include <cstdint>
#include <stdexcept>
namespace c062 {
__global__ void combine_k10_vec4(const float4* __restrict__ parts4, const float* __restrict__ weights,
                                 const float4* __restrict__ shared4, float4* __restrict__ output4,
                                 int64_t n4, const float* sg) {
    const int64_t tk = blockIdx.y;
    parts4 += tk * 10 * n4;
    weights += tk * 10;
    shared4 += tk * n4;
    output4 += tk * n4;
    const int64_t c4 = int64_t(blockIdx.x) * blockDim.x + threadIdx.x;
    if (c4 >= n4) return;
    const float w0 = __ldg(weights + 0);
    const float4 p0 = parts4[c4];
    float4 sum = make_float4(p0.x * w0, p0.y * w0, p0.z * w0, p0.w * w0);
#pragma unroll
    for (int expert = 1; expert < 10; ++expert) {
        const float w = __ldg(weights + expert);
        const float4 p = parts4[int64_t(expert) * n4 + c4];
        // the documented contract spelled out: the first product rounded, then one FMA per expert in order. Left to the
        // compiler's contraction, a build may fuse a different product (gfx1151: the float4 kernel then differed from the
        // scalar one, native_multi_parity)
        sum.x = fmaf(p.x, w, sum.x);
        sum.y = fmaf(p.y, w, sum.y);
        sum.z = fmaf(p.z, w, sum.z);
        sum.w = fmaf(p.w, w, sum.w);
    }
    float4 sh = shared4[c4];
    const float gate = __fdividef(1.f, 1.f + __expf(-sg[tk]));
    sh.x *= gate; sh.y *= gate; sh.z *= gate; sh.w *= gate;
    sum.x += sh.x;
    sum.y += sh.y;
    sum.z += sh.z;
    sum.w += sh.w;
    output4[c4] = sum;
}
void native_moe_combine_multi_gated(const float* parts,const float* weights,const float* shared,const float* sg,float* output,int64_t n,int64_t k,int t,void* st){
 if(k!=10 || n%4 || !st) throw std::runtime_error("C062 invalid shape");
 combine_k10_vec4<<<dim3((unsigned)((n/4+127)/128),(unsigned)t),128,0,(cudaStream_t)st>>>((const float4*)parts,weights,(const float4*)shared,(float4*)output,n/4,sg);
 auto e=cudaGetLastError();if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));
}
}
