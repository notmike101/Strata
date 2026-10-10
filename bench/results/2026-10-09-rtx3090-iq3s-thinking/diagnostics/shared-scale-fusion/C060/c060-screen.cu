#include "strata/kernels/native_moe.hpp"
#include <cuda_runtime.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>
#include "c060-scale.inl"
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"%s\n",cudaGetErrorString(e));std::exit(2);}}
struct Buf{float* p;size_t n;Buf(size_t n):n(n){ck(cudaMalloc(&p,n*4));}~Buf(){cudaFree(p);}void put(const std::vector<float>& h){ck(cudaMemcpy(p,h.data(),n*4,cudaMemcpyHostToDevice));}std::vector<float> get(){std::vector<float> h(n);ck(cudaMemcpy(h.data(),p,n*4,cudaMemcpyDeviceToHost));return h;}};
int main(){using namespace strata::kernels;constexpr int N=2560,K=10,MAX=9;cudaStream_t st;ck(cudaStreamCreate(&st));
 Buf parts(MAX*K*N),w(MAX*K),shared(MAX*N),scaled(MAX*N),g(MAX),out(MAX*N),ref(MAX*N);
 int bad=0,cases=0;
 for(int T=2;T<=8;++T)for(int seed=0;seed<5;++seed)for(int dist=0;dist<4;++dist){
  std::mt19937 rng(60000+seed);std::normal_distribution<float> d(0,1);
  auto randomize=[&](Buf& b,float scale){std::vector<float> h(b.n);for(auto& x:h)x=d(rng)*scale;b.put(h);};
  randomize(parts,dist==1?1e-8f:dist==2?1e8f:1.f);randomize(w,.1f);randomize(shared,dist==1?1e-8f:dist==2?1e8f:1.f);
  std::vector<float> gates(MAX);for(int i=0;i<MAX;++i)gates[i]=dist==3?(i%2?100.f:-100.f):d(rng)*3.f;g.put(gates);
  std::vector<float> canary(MAX*N,12345.25f);out.put(canary);ref.put(canary);
  cudaGraph_t graph;cudaGraphExec_t exec;ck(cudaStreamBeginCapture(st,cudaStreamCaptureModeThreadLocal));
  ck(cudaMemcpyAsync(scaled.p,shared.p,shared.n*4,cudaMemcpyDeviceToDevice,st));
  sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,T),128,0,st>>>((float4*)scaled.p,g.p,N/4);
  native_moe_combine_multi_hits(parts.p,w.p,scaled.p,ref.p,N,K,T,st);
  native_moe_combine_multi_hits_gated(parts.p,w.p,shared.p,g.p,out.p,N,K,T,st);
  ck(cudaStreamEndCapture(st,&graph));ck(cudaGraphInstantiate(&exec,graph,nullptr,nullptr,0));ck(cudaGraphLaunch(exec,st));ck(cudaGraphLaunch(exec,st));ck(cudaStreamSynchronize(st));
  auto a=out.get(),b=ref.get();int unequal=0,nonfinite=0,clobber=0;float maxerr=0;
  for(int i=0;i<T*N;++i){unequal+=std::memcmp(&a[i],&b[i],4)!=0;nonfinite+=!std::isfinite(a[i])||!std::isfinite(b[i]);maxerr=std::fmax(maxerr,std::fabs(a[i]-b[i]));}
  for(int i=T*N;i<MAX*N;++i)clobber+=(a[i]!=canary[i]||b[i]!=canary[i]);
  std::printf("CASE T=%d seed=%d distribution=%d differing_floats=%d nonfinite=%d canary_failures=%d max_abs_error=%.9g\n",T,seed,dist,unequal,nonfinite,clobber,maxerr);
  bad+=(unequal||nonfinite||clobber);++cases;ck(cudaGraphExecDestroy(exec));ck(cudaGraphDestroy(graph));
 }
 ck(cudaStreamDestroy(st));std::printf("SUMMARY cases=%d failed=%d\n",cases,bad);return bad?1:0;
}
