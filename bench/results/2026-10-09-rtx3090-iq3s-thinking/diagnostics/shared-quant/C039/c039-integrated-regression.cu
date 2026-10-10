#include "strata/kernels/native_mmvq.hpp"
#include "strata/kernels/iq_kernels.hpp"
#include <cuda_runtime.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>
namespace K=strata::kernels;
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"CUDA %s\n",cudaGetErrorString(e));std::exit(2);}}
void dual(const float*x,int T,int N,void*qm,void*qs,cudaStream_t stream){K::quantize_q8_1_rows_dual(x,T,N,qm,qs,stream);}
int main(){
 setvbuf(stdout,nullptr,_IONBF,0);constexpr int N=2560,MT=8;size_t qb=K::native_q8_1_bytes(N,MT),cap=qb+512;
 cudaStream_t stream;ck(cudaStreamCreate(&stream));float*x;ck(cudaMalloc((void**)&x,N*MT*4));unsigned char*buf[4];for(auto&v:buf)ck(cudaMalloc((void**)&v,cap));
 std::vector<float> h(N*MT);std::vector<unsigned char> ref(cap),got(cap);std::mt19937 rng(13021);size_t values=0,bytes=0;
 for(int T=1;T<=MT;T++)for(int r=0;r<512;r++){
  for(int i=0;i<N*T;i++){
   unsigned bits=rng();switch(r%8){
    case 0:bits&=0x80000000u;break; // signed zero
    case 1:bits=(bits&0x807fffffu);break; // subnormal
    case 2:bits=(bits&0x807fffffu)|0x00800000u;break; // first normal exponent
    case 3:bits=(bits&0x807fffffu)|((rng()%157)<<23);break; // finite mixed exponents incl clamp
    case 4:bits=(bits&0x807fffffu)|(117u<<23);break;
    case 5:bits=(bits&0x807fffffu)|(127u<<23);break;
    case 6:bits=(bits&0x807fffffu)|(145u<<23);break;
    default:bits=(bits&0x807fffffu)|(150u<<23);break;
   }std::memcpy(&h[i],&bits,4);
  }
  ck(cudaMemcpy(x,h.data(),N*T*4,cudaMemcpyHostToDevice));for(auto v:buf)ck(cudaMemset(v,0xa7,cap));
  K::quantize_q8_1_rows(x,T,N,buf[0]+256,stream);K::native_quantize_q8_1(x,buf[1]+256,N,T,stream);dual(x,T,N,buf[2]+256,buf[3]+256,stream);ck(cudaStreamSynchronize(stream));
  size_t used=K::native_q8_1_bytes(N,T);
  for(int k=0;k<2;k++){
   ck(cudaMemcpy(ref.data(),buf[k],cap,cudaMemcpyDeviceToHost));ck(cudaMemcpy(got.data(),buf[k+2],cap,cudaMemcpyDeviceToHost));
   if(ref!=got){for(size_t j=0;j<cap;j++)if(ref[j]!=got[j]){std::printf("FAIL T=%d round=%d path=%d byte=%zu ref=%u got=%u\n",T,r,k,j,ref[j],got[j]);break;}return 4;}
   if(!std::all_of(got.begin(),got.begin()+256,[](unsigned char b){return b==0xa7;})||!std::all_of(got.begin()+256+used,got.end(),[](unsigned char b){return b==0xa7;}))return 5;
  }
  values+=N*T;bytes+=2*used;
  if(r==511)std::printf("CORPUS T=%d cases=512 cumulative_values=%zu cumulative_bytes=%zu guards=pass exact=pass\n",T,values,bytes);
 }
 for(auto v:buf)ck(cudaFree(v));ck(cudaFree(x));ck(cudaStreamDestroy(stream));std::printf("C039 CORPUS PASS cases=4096 values=%zu bytes=%zu\n",values,bytes);
}
