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
namespace c062 { void native_moe_combine_multi_gated(const float*,const float*,const float*,const float*,float*,int64_t,int64_t,int,void*); }
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"%s\n",cudaGetErrorString(e));std::exit(2);}}
struct Buf{float* p;size_t n;Buf(size_t n):n(n){ck(cudaMalloc(&p,n*4));}~Buf(){cudaFree(p);}void put(const std::vector<float>& h){ck(cudaMemcpy(p,h.data(),n*4,cudaMemcpyHostToDevice));}std::vector<float> get(){std::vector<float> h(n);ck(cudaMemcpy(h.data(),p,n*4,cudaMemcpyDeviceToHost));return h;}};

static float elapsed(cudaGraphExec_t graph,cudaStream_t stream){
 cudaEvent_t a,b;ck(cudaEventCreate(&a));ck(cudaEventCreate(&b));ck(cudaEventRecord(a,stream));ck(cudaGraphLaunch(graph,stream));ck(cudaEventRecord(b,stream));ck(cudaEventSynchronize(b));float ms;ck(cudaEventElapsedTime(&ms,a,b));ck(cudaEventDestroy(a));ck(cudaEventDestroy(b));return ms*1000/200;
}
static void timing(Buf& parts,Buf& w,Buf& shared,Buf& scaled,Buf& g,Buf& out,Buf& ref,cudaStream_t st){
 using namespace strata::kernels;constexpr int N=2560,K=10;
 std::mt19937 rng(61001);std::normal_distribution<float> d(0,1);
 for(Buf* b:{&parts,&w,&shared,&g}){std::vector<float> h(b->n);for(auto& x:h)x=d(rng)*.25f;b->put(h);}
 for(int T=1;T<=8;++T){cudaGraph_t graphs[2];cudaGraphExec_t execs[2];
  for(int variant=0;variant<2;++variant){ck(cudaStreamBeginCapture(st,cudaStreamCaptureModeThreadLocal));
   for(int i=0;i<200;++i){
    // Equal restoration copy in BOTH variants; diagnostic time includes it.
    ck(cudaMemcpyAsync(scaled.p,shared.p,T*N*4,cudaMemcpyDeviceToDevice,st));
    if(variant)c062::native_moe_combine_multi_gated(parts.p,w.p,scaled.p,g.p,out.p,N,K,T,st);
    else{sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,T),128,0,st>>>((float4*)scaled.p,g.p,N/4);native_moe_combine_multi(parts.p,w.p,scaled.p,ref.p,N,K,T,st);}
   }
   ck(cudaStreamEndCapture(st,&graphs[variant]));ck(cudaGraphInstantiate(&execs[variant],graphs[variant],nullptr,nullptr,0));
  }
  for(int round=-1;round<7;++round)for(int order=0;order<2;++order){int v=(round+1+order)%2;float us=elapsed(execs[v],st);std::printf("TIMING T=%d round=%d candidate=%d us=%.9g\n",T,round,v,us);}
  for(int v=0;v<2;++v){ck(cudaGraphExecDestroy(execs[v]));ck(cudaGraphDestroy(graphs[v]));}
 }
}

int main(){using namespace strata::kernels;constexpr int N=2560,K=10,MAX=9;cudaStream_t st;ck(cudaStreamCreate(&st));
 Buf parts(MAX*K*N),w(MAX*K),shared(MAX*N),scaled(MAX*N),g(MAX),out(MAX*N),ref(MAX*N);
 int bad=0,cases=0;
 for(int T=1;T<=8;++T)for(int seed=0;seed<5;++seed)for(int dist=0;dist<8;++dist){
  std::mt19937 rng(60000+seed);std::normal_distribution<float> d(0,1);
  auto randomize=[&](Buf& b,float scale){std::vector<float> h(b.n);for(auto& x:h)x=d(rng)*scale;b.put(h);};
  randomize(parts,dist==1?1e-8f:dist==2?1e8f:dist==4?1e-38f:1.f);randomize(w,.1f);randomize(shared,dist==1?1e-8f:dist==2?1e8f:dist==4?1e-38f:1.f);
  std::vector<float> gates(MAX);for(int i=0;i<MAX;++i)gates[i]=dist==3?(i%2?100.f:-100.f):d(rng)*3.f;g.put(gates);

  if(dist>=5){
   std::vector<float> ph(parts.n,0.f),wh(w.n,0.f),sh(shared.n,0.f);
   const float edge[]={0.f,-0.f,std::numeric_limits<float>::denorm_min(),-std::numeric_limits<float>::denorm_min(),std::numeric_limits<float>::min(),-std::numeric_limits<float>::min(),1.f,std::nextafter(1.f,2.f)};
   for(int t=0;t<MAX;++t){wh[t*K]=1.f;gates[t]=dist==7?float(t-4)*20.f:0.f;
    for(int i=0;i<N;++i){float v=dist==5?float(i%31-15)*.03125f:edge[(i+seed)%8];ph[(t*K)*N+i]=v;sh[t*N+i]=dist==5?-2.f*v:dist==6?-0.f:v;}
   }
   parts.put(ph);w.put(wh);shared.put(sh);g.put(gates);
  }
  std::vector<float> canary(MAX*N,12345.25f);out.put(canary);ref.put(canary);
  cudaGraph_t graph;cudaGraphExec_t exec;ck(cudaStreamBeginCapture(st,cudaStreamCaptureModeThreadLocal));
  ck(cudaMemcpyAsync(scaled.p,shared.p,shared.n*4,cudaMemcpyDeviceToDevice,st));
  sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,T),128,0,st>>>((float4*)scaled.p,g.p,N/4);
  native_moe_combine_multi(parts.p,w.p,scaled.p,ref.p,N,K,T,st);
  c062::native_moe_combine_multi_gated(parts.p,w.p,shared.p,g.p,out.p,N,K,T,st);
  ck(cudaStreamEndCapture(st,&graph));ck(cudaGraphInstantiate(&exec,graph,nullptr,nullptr,0));ck(cudaGraphLaunch(exec,st));ck(cudaGraphLaunch(exec,st));ck(cudaStreamSynchronize(st));
  auto a=out.get(),b=ref.get();int unequal=0,nonfinite=0,clobber=0;float maxerr=0;
  for(int i=0;i<T*N;++i){unequal+=std::memcmp(&a[i],&b[i],4)!=0;nonfinite+=!std::isfinite(a[i])||!std::isfinite(b[i]);maxerr=std::fmax(maxerr,std::fabs(a[i]-b[i]));}
  for(int i=T*N;i<MAX*N;++i)clobber+=(a[i]!=canary[i]||b[i]!=canary[i]);
  std::printf("CASE T=%d seed=%d distribution=%d differing_floats=%d nonfinite=%d canary_failures=%d max_abs_error=%.9g\n",T,seed,dist,unequal,nonfinite,clobber,maxerr);
  bad+=(unequal||nonfinite||clobber);++cases;ck(cudaGraphExecDestroy(exec));ck(cudaGraphDestroy(graph));
 }
 if(!bad) timing(parts,w,shared,scaled,g,out,ref,st);
 ck(cudaStreamDestroy(st));std::printf("SUMMARY cases=%d failed=%d\n",cases,bad);return bad?1:0;
}
