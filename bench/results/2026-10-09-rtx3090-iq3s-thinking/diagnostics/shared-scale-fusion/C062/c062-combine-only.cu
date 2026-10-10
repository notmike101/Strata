#include "strata/kernels/native_moe.hpp"
#include <cuda_runtime.h>
#include <cmath>
#include <limits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>
#include "c060-scale.inl"
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"%s\n",cudaGetErrorString(e));std::exit(2);}}
struct Buf{float* p;size_t n;Buf(size_t n):n(n){ck(cudaMalloc(&p,n*4));}~Buf(){cudaFree(p);}void put(const std::vector<float>& h){ck(cudaMemcpy(p,h.data(),n*4,cudaMemcpyHostToDevice));}std::vector<float> get(){std::vector<float> h(n);ck(cudaMemcpy(h.data(),p,n*4,cudaMemcpyDeviceToHost));return h;}};

static float elapsed(cudaGraphExec_t graph,cudaStream_t stream){
 cudaEvent_t a,b;ck(cudaEventCreate(&a));ck(cudaEventCreate(&b));ck(cudaEventRecord(a,stream));ck(cudaGraphLaunch(graph,stream));ck(cudaEventRecord(b,stream));ck(cudaEventSynchronize(b));float ms;ck(cudaEventElapsedTime(&ms,a,b));ck(cudaEventDestroy(a));ck(cudaEventDestroy(b));return ms*1000/200;
}
static void timing(Buf& parts,Buf& w,Buf& shared,Buf& scaled,Buf& g,Buf& out,Buf& ref,cudaStream_t st){
 using namespace strata::kernels;constexpr int N=2560,K=10;
 std::mt19937 rng(61001);std::normal_distribution<float> d(0,1);
 for(Buf* b:{&parts,&w,&shared,&g}){std::vector<float> h(b->n);for(auto& x:h)x=d(rng)*.25f;b->put(h);}
 ck(cudaMemcpyAsync(scaled.p,shared.p,8*N*4,cudaMemcpyDeviceToDevice,st));
 sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,8),128,0,st>>>((float4*)scaled.p,g.p,N/4);
 ck(cudaStreamSynchronize(st));
 for(int T=1;T<=8;++T){cudaGraph_t graphs[2];cudaGraphExec_t execs[2];
  for(int variant=0;variant<2;++variant){ck(cudaStreamBeginCapture(st,cudaStreamCaptureModeThreadLocal));
   for(int i=0;i<200;++i){
    if(variant)native_moe_combine_multi_gated(parts.p,w.p,shared.p,g.p,out.p,N,K,T,st);
    else{native_moe_combine_multi(parts.p,w.p,scaled.p,ref.p,N,K,T,st);}
   }
   ck(cudaStreamEndCapture(st,&graphs[variant]));ck(cudaGraphInstantiate(&execs[variant],graphs[variant],nullptr,nullptr,0));
  }
  for(int round=-1;round<7;++round)for(int order=0;order<2;++order){int v=(round+1+order)%2;float us=elapsed(execs[v],st);std::printf("TIMING T=%d round=%d candidate=%d us=%.9g\n",T,round,v,us);}
  for(int v=0;v<2;++v){ck(cudaGraphExecDestroy(execs[v]));ck(cudaGraphDestroy(graphs[v]));}
 }
}

int main(){constexpr int N=2560,K=10,MAX=9;cudaStream_t st;ck(cudaStreamCreate(&st));
 Buf parts(MAX*K*N),w(MAX*K),shared(MAX*N),scaled(MAX*N),g(MAX),out(MAX*N),ref(MAX*N);
 timing(parts,w,shared,scaled,g,out,ref,st);ck(cudaStreamDestroy(st));return 0;}
