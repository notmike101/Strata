#include "c029-original-helpers.inl"
namespace strata::kernels {
namespace {
template<int ROWS>
__launch_bounds__(32 * ROWS, 1)
__global__ void c029_onewarp_kernel(const Q6KBlock* __restrict__ weights,
                                    const Q81Block* __restrict__ activation,
                                    float* __restrict__ output,int n_in,int n_out) {
    const int row=int(blockIdx.x)*ROWS+int(threadIdx.y);
    if(row>=n_out)return; // whole warp, so every participating XOR lane remains active
    const int lane=int(threadIdx.x),blocks=n_in/256;
    float partial[4]={};
    for(int base=0;base<blocks;base+=4){
#pragma unroll
        for(int virtual_warp=0;virtual_warp<4;++virtual_warp){
            const int kbx=base+virtual_warp;
            if(kbx<blocks){
                partial[virtual_warp]+=q6_q8_dot(weights+std::size_t(row)*blocks+kbx,
                                                activation+kbx*8,lane);
            }
        }
    }
    float sum=partial[0];
#pragma unroll
    for(int virtual_warp=1;virtual_warp<4;++virtual_warp)sum+=partial[virtual_warp];
    sum=warp_sum(sum);
    if(lane==0)output[row]=sum;
}
}
void c029_mmvq(int rows,const void*w,const void*x,float*y,int n_in,int n_out,cudaStream_t stream) {
    const auto*weights=static_cast<const Q6KBlock*>(w);
    const auto*activation=static_cast<const Q81Block*>(x);
    if(rows==2)c029_onewarp_kernel<2><<<(n_out+1)/2,dim3(32,2),0,stream>>>(weights,activation,y,n_in,n_out);
    else if(rows==4)c029_onewarp_kernel<4><<<(n_out+3)/4,dim3(32,4),0,stream>>>(weights,activation,y,n_in,n_out);
    else if(rows==8)c029_onewarp_kernel<8><<<(n_out+7)/8,dim3(32,8),0,stream>>>(weights,activation,y,n_in,n_out);
    else throw std::invalid_argument("Unsupported diagnostic warp count");
}
}
