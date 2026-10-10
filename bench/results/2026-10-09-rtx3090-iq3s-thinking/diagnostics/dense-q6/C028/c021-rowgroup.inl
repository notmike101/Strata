namespace strata::kernels {
namespace {
template<int ROWS>
__launch_bounds__(WARPS * WARP, 1)
__global__ void c021_rowgroup_kernel(const Q6KBlock* __restrict__ w,
                                     const Q81Block* __restrict__ x,
                                     float* __restrict__ y, int n_in, int n_out) {
    constexpr int BLOCKS_PER_ITER=WARPS*WARP/32;
    const int tid=WARP*int(threadIdx.y)+int(threadIdx.x);
    const int row0=ROWS*int(blockIdx.x);
    const int blocks_per_row=n_in/256;
    float tmp[ROWS]={};
    for(int kbx=tid/32;kbx<blocks_per_row;kbx+=BLOCKS_PER_ITER){
        const int kby=kbx*8;
        const int kqs=tid%32;
#pragma unroll
        for(int i=0;i<ROWS;++i){
            if(row0+i<n_out){
                const std::size_t block=std::size_t(row0+i)*blocks_per_row+kbx;
                tmp[i]+=q6_q8_dot(w+block,x+kby,kqs);
            }
        }
    }
    __shared__ float partial[WARPS-1][ROWS][WARP];
    if(threadIdx.y>0){
#pragma unroll
        for(int i=0;i<ROWS;++i)partial[threadIdx.y-1][i][threadIdx.x]=tmp[i];
    }
    __syncthreads();
    if(threadIdx.y>0)return;
#pragma unroll
    for(int i=0;i<ROWS;++i){
#pragma unroll
        for(int l=0;l<WARPS-1;++l)tmp[i]+=partial[l][i][threadIdx.x];
        tmp[i]=warp_sum(tmp[i]);
        // Match lane zero from the original one-row kernel for every row.
        if(threadIdx.x==0&&row0+i<n_out)y[row0+i]=tmp[i];
    }
}
}
void c021_mmvq(int rows, const void* w, const void* x, float* y, int n_in, int n_out, cudaStream_t stream) {
    const dim3 threads(WARP,WARPS);
    const auto* weights=static_cast<const Q6KBlock*>(w);
    const auto* activation=static_cast<const Q81Block*>(x);
    if(rows==2)c021_rowgroup_kernel<2><<<(n_out+1)/2,threads,0,stream>>>(weights,activation,y,n_in,n_out);
    else if(rows==4)c021_rowgroup_kernel<4><<<(n_out+3)/4,threads,0,stream>>>(weights,activation,y,n_in,n_out);
    else if(rows==8)c021_rowgroup_kernel<8><<<(n_out+7)/8,threads,0,stream>>>(weights,activation,y,n_in,n_out);
    else throw std::invalid_argument("Unsupported diagnostic group size");
}
}
