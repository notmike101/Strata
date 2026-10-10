#include "c029-original-helpers.inl"
namespace strata::kernels {
void c029_mmvq(int rows,const void*,const void*,float*y,int,int n_out,cudaStream_t stream) {
    cudaMemsetAsync(y,0,n_out*sizeof(float),stream); // deliberately wrong RED stub
}
}
