// Offline prototype. Compiled without --use_fast_math; explicit PTX retains
// the native path's FTZ semantics while the routed path remains precise.
#include "strata/kernels/q8_1_finite.hpp"
struct alignas(4) DualQ81 { __half2 ds; signed char qs[32]; };
static_assert(sizeof(DualQ81)==36);
__device__ __forceinline__ float fast_abs(float x){float y;asm("abs.ftz.f32 %0, %1;":"=f"(y):"f"(x));return y;}
__device__ __forceinline__ float fast_max(float a,float b){float y;asm("max.ftz.f32 %0, %1, %2;":"=f"(y):"f"(a),"f"(b));return y;}
__device__ __forceinline__ float fast_add(float a,float b){float y;asm("add.rn.ftz.f32 %0, %1, %2;":"=f"(y):"f"(a),"f"(b));return y;}
__device__ __forceinline__ float fast_div(float a,float b){float y;asm("div.approx.ftz.f32 %0, %1, %2;":"=f"(y):"f"(a),"f"(b));return y;}
__device__ __forceinline__ float fast_round(float a){float h=copysignf(.5f,a),y,z;asm("add.rz.ftz.f32 %0, %1, %2;":"=f"(y):"f"(a),"f"(h));asm("cvt.rzi.f32.f32 %0, %1;":"=f"(z):"f"(y));return z;}
__global__ __launch_bounds__(256,1) void dual_quant_kernel(const float*x,DualQ81*routed,DualQ81*shared,int n){
 int i=blockIdx.x*256+threadIdx.x;if(i>=n)return;
 float xi=x[i],am=fabsf(xi),af=fast_abs(xi),sum=xi,sf=xi;
 #pragma unroll
 for(int o=16;o;o>>=1){
  am=fmaxf(am,__shfl_xor_sync(0xffffffffu,am,o));
  af=fast_max(af,__shfl_xor_sync(0xffffffffu,af,o));
  sum=__fadd_rn(sum,__shfl_xor_sync(0xffffffffu,sum,o));
  sf=fast_add(sf,__shfl_xor_sync(0xffffffffu,sf,o));
 }
 float d=K::q8_1_finite(__fdiv_rn(am,127.f));
 float df=K::q8_1_finite(fast_div(af,127.f));
 signed char qr=K::q8_1_quant(xi,d,am),qf=0;
 if(af!=0.f){float q=fast_round(fast_div(xi,df));qf=(signed char)(q>127.f?127.f:q< -127.f?-127.f:q);}
 routed[i/32].qs[i%32]=qr;shared[i/32].qs[i%32]=qf;
 if(i%32==0){routed[i/32].ds=K::q8_1_ds(d,sum);shared[i/32].ds=K::q8_1_ds(df,sf);}
}
void dual(const float*x,int T,int N,void*qm,void*qs,cudaStream_t stream){dual_quant_kernel<<<(N*T+255)/256,256,0,stream>>>(x,(DualQ81*)qm,(DualQ81*)qs,N*T);ck(cudaGetLastError());}
