// Throwaway C038 two-stream quantization DAG screen; not production code.
#include "strata/kernels/native_mmvq.hpp"
#include "strata/kernels/iq_kernels.hpp"
#include <cuda_runtime.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <random>
#include <string>
#include <vector>
namespace K=strata::kernels;
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"CUDA %s\n",cudaGetErrorString(e));std::exit(2);}}
template<class T> T* alloc(size_t bytes){T*p;ck(cudaMalloc((void**)&p,bytes));return p;}
int main(){
 setvbuf(stdout,nullptr,_IONBF,0); K::native_mmvq_set_multi_exact(true);
 cudaStream_t main,side;ck(cudaStreamCreateWithFlags(&main,cudaStreamNonBlocking));ck(cudaStreamCreateWithFlags(&side,cudaStreamNonBlocking));
 cudaEvent_t fork,join,e0,e1;ck(cudaEventCreateWithFlags(&fork,cudaEventDisableTiming));ck(cudaEventCreateWithFlags(&join,cudaEventDisableTiming));ck(cudaEventCreate(&e0));ck(cudaEventCreate(&e1));
 constexpr int N=2560,M=640,MAXT=8,ITERS=100;size_t qb=K::native_q8_1_bytes(N,MAXT);
 float*x=alloc<float>(N*MAXT*4),*ym=alloc<float>(M*MAXT*4),*ys=alloc<float>(M*MAXT*4);
 void*qm=alloc<char>(qb),*qs=alloc<char>(qb);std::vector<float> hx(N*MAXT);std::mt19937 rng(90210);std::uniform_real_distribution<float> dist(-1,1);
 int types[3][2]={{12,23},{13,13},{12,13}}; // actual Q4_K/IQ4_XS/Q5_K source metadata in manifest
 for(int layer=0;layer<3;layer++){
  void*w[2];for(int j=0;j<2;j++){std::string name="C:/Strata/local-setup/target-80/C038-private/"+std::to_string(layer)+(j?"-up.bin":"-gate.bin");std::ifstream f(name,std::ios::binary);std::vector<char>b((std::istreambuf_iterator<char>(f)),{});if(b.empty())return 3;w[j]=alloc<char>(b.size());ck(cudaMemcpy(w[j],b.data(),b.size(),cudaMemcpyHostToDevice));}
  for(int T=1;T<=MAXT;T++){
   auto dag=[&](bool share){
    if(share)K::quantize_q8_1_rows(x,T,N,qm,main);
    ck(cudaEventRecord(fork,main));ck(cudaStreamWaitEvent(side,fork,0));
    if(!share)K::native_quantize_q8_1(x,qs,N,T,side);
    K::native_mmvq(types[layer][1],w[1],share?qm:qs,ys,N,M,T,side);
    if(!share)K::quantize_q8_1_rows(x,T,N,qm,main);
    K::native_mmvq(types[layer][0],w[0],qm,ym,N,M,T,main);
    ck(cudaEventRecord(join,side));ck(cudaStreamWaitEvent(main,join,0));
   };
   for(int pattern=0;pattern<4;pattern++){
    for(size_t i=0;i<hx.size();i++)hx[i]=pattern==0?0.f:dist(rng)*(pattern==1?.001f:pattern==2?1.f:100.f);
    ck(cudaMemcpy(x,hx.data(),hx.size()*4,cudaMemcpyHostToDevice));
    dag(false);ck(cudaStreamSynchronize(main));size_t bytes=K::native_q8_1_bytes(N,T);
    std::vector<char>a(bytes),b(bytes);ck(cudaMemcpy(a.data(),qm,bytes,cudaMemcpyDeviceToHost));ck(cudaMemcpy(b.data(),qs,bytes,cudaMemcpyDeviceToHost));if(a!=b){std::printf("FAIL quant layer=%d T=%d pattern=%d\n",layer,T,pattern);return 4;}
    std::vector<float>ref(M*T*2),got(M*T*2);ck(cudaMemcpy(ref.data(),ym,M*T*4,cudaMemcpyDeviceToHost));ck(cudaMemcpy(ref.data()+M*T,ys,M*T*4,cudaMemcpyDeviceToHost));
    ck(cudaMemset(ym,0xa7,M*MAXT*4));ck(cudaMemset(ys,0xa7,M*MAXT*4));ck(cudaMemset(qm,0xa7,qb));dag(true);ck(cudaStreamSynchronize(main));
    ck(cudaMemcpy(got.data(),ym,M*T*4,cudaMemcpyDeviceToHost));ck(cudaMemcpy(got.data()+M*T,ys,M*T*4,cudaMemcpyDeviceToHost));
    if(std::memcmp(ref.data(),got.data(),got.size()*4)||!std::all_of(got.begin(),got.end(),[](float v){return std::isfinite(v);})){std::printf("FAIL output layer=%d T=%d pattern=%d\n",layer,T,pattern);return 5;}
    std::printf("PARITY layer=%d T=%d pattern=%d qbytes=%zu floats=%zu exact=pass\n",layer,T,pattern,bytes,got.size());
   }
   cudaGraph_t graph[2];cudaGraphExec_t exec[2];
   for(int f=0;f<2;f++){ck(cudaStreamBeginCapture(main,cudaStreamCaptureModeGlobal));for(int k=0;k<ITERS;k++)dag(f!=0);ck(cudaStreamEndCapture(main,&graph[f]));ck(cudaGraphInstantiate(&exec[f],graph[f],nullptr,nullptr,0));ck(cudaGraphUpload(exec[f],main));ck(cudaStreamSynchronize(main));}
   double times[2][7];
   for(int r=-1;r<7;r++)for(int order=0;order<2;order++){int f=(r+1+order)%2;ck(cudaEventRecord(e0,main));ck(cudaGraphLaunch(exec[f],main));ck(cudaEventRecord(e1,main));ck(cudaEventSynchronize(e1));float ms;ck(cudaEventElapsedTime(&ms,e0,e1));if(r>=0){times[f][r]=1000.*ms/ITERS;std::printf("RAW layer=%d T=%d round=%d candidate=%d us=%.6f\n",layer,T,r,f,times[f][r]);}}
   for(int f=0;f<2;f++){std::sort(times[f],times[f]+7);ck(cudaGraphExecDestroy(exec[f]));ck(cudaGraphDestroy(graph[f]));}
   std::printf("MEDIAN layer=%d T=%d original_us=%.6f candidate_us=%.6f ratio=%.6f\n",layer,T,times[0][3],times[1][3],times[1][3]/times[0][3]);
  }
  ck(cudaFree(w[0]));ck(cudaFree(w[1]));
 }
 ck(cudaFree(x));ck(cudaFree(ym));ck(cudaFree(ys));ck(cudaFree(qm));ck(cudaFree(qs));ck(cudaEventDestroy(fork));ck(cudaEventDestroy(join));ck(cudaEventDestroy(e0));ck(cudaEventDestroy(e1));ck(cudaStreamDestroy(side));ck(cudaStreamDestroy(main));std::puts("C038 PASS parity; inspect timing gate");
}
