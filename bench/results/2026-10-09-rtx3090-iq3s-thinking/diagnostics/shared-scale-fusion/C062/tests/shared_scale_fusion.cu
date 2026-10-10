// C062 exact scale/combine and actual shared-expert pipeline regression.
#include "strata/kernels/native_moe.hpp"
#include <cuda_runtime.h>
#include <cmath>
#include <limits>
#include "strata/kernels/shared_expert.hpp"
#include "strata/kernels/native_mmvq.hpp"
#include "strata/kernels/bf16_bits.hpp"
#include "strata/kernels/f16_bits.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>
__global__ void sigmoid_scale_rows_vec4_kernel(float4* __restrict__ out4, const float* __restrict__ g, int n4) {
    const int t = blockIdx.y;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n4) {
        const float gt = __fdividef(1.0f, 1.0f + __expf(-__ldg(g + t)));
        float4 v = out4[(size_t) t * n4 + i];
        v.x *= gt;
        v.y *= gt;
        v.z *= gt;
        v.w *= gt;
        out4[(size_t) t * n4 + i] = v;
    }
}


static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"%s\n",cudaGetErrorString(e));std::exit(2);}}
struct Buf{float* p;size_t n;Buf(size_t n):n(n){ck(cudaMalloc(&p,n*4));}~Buf(){cudaFree(p);}void put(const std::vector<float>& h){ck(cudaMemcpy(p,h.data(),n*4,cudaMemcpyHostToDevice));}std::vector<float> get(){std::vector<float> h(n);ck(cudaMemcpy(h.data(),p,n*4,cudaMemcpyDeviceToHost));return h;}};


// Test the actual shared expert flag/dataflow, not only the fused epilogue.
static int shared_pipeline(cudaStream_t st){
 using namespace strata::kernels;constexpr int N=2560,F=512,K=10,MAX=8;
 Buf x(MAX*N),parts(MAX*K*N),weights(MAX*K),wi(N/2),wg(N*F/32*34/4),wu(N*F/32*34/4),wd(N*F/32*34/4),q(MAX*N/32*9),gate(MAX*F),up(MAX*F),logit(MAX),raw(MAX*N),scaled(MAX*N),ref(MAX*N),out(MAX*N);
 std::mt19937 rng(62031);std::normal_distribution<float> d(0,.1f);
 for(Buf* b:{&x,&parts,&weights}){std::vector<float> v(b->n);for(auto& a:v)a=d(rng);b->put(v);}
 std::vector<uint16_t> input_gate(N);for(auto& v:input_gate)v=bf16_from_f32(d(rng));ck(cudaMemcpy(wi.p,input_gate.data(),N*2,cudaMemcpyHostToDevice));
 for(Buf* b:{&wg,&wu,&wd}){std::vector<unsigned char> v(b->n*4);for(size_t i=0;i<v.size();i+=34){uint16_t scale=f16_from_f32(.002f);std::memcpy(v.data()+i,&scale,2);for(int j=0;j<32;++j)v[i+2+j]=(unsigned char)(int(rng()%31)-15);}ck(cudaMemcpy(b->p,v.data(),v.size(),cudaMemcpyHostToDevice));}
 NativeSharedWeights nw;nw.gate_type=nw.up_type=nw.down_type=8;nw.gate_data=wg.p;nw.up_data=wu.p;nw.down_data=wd.p;nw.q8_1=q.p;
 shared_expert_set_native_bf16(true);native_mmvq_set_multi_exact(true);int bad=0;
 for(int T=1;T<=MAX;++T){cudaGraph_t graph;cudaGraphExec_t exec;ck(cudaStreamBeginCapture(st,cudaStreamCaptureModeThreadLocal));
  shared_expert_multi(T,x.p,nullptr,nw,(const uint16_t*)wi.p,gate.p,up.p,logit.p,scaled.p,N,F,st,nullptr,0);
  native_moe_combine_multi(parts.p,weights.p,scaled.p,ref.p,N,K,T,st);
  shared_expert_multi(T,x.p,nullptr,nw,(const uint16_t*)wi.p,gate.p,up.p,logit.p,raw.p,N,F,st,nullptr,4);
  native_moe_combine_multi_gated(parts.p,weights.p,raw.p,logit.p,out.p,N,K,T,st);
  ck(cudaStreamEndCapture(st,&graph));ck(cudaGraphInstantiate(&exec,graph,nullptr,nullptr,0));ck(cudaGraphLaunch(exec,st));ck(cudaGraphLaunch(exec,st));ck(cudaStreamSynchronize(st));
  auto a=out.get(),b=ref.get();int unequal=0,nonfinite=0;for(int i=0;i<T*N;++i){unequal+=std::memcmp(&a[i],&b[i],4)!=0;nonfinite+=!std::isfinite(a[i])||!std::isfinite(b[i]);}
  std::printf("PIPELINE T=%d differing_floats=%d nonfinite=%d\n",T,unequal,nonfinite);bad+=(unequal||nonfinite);ck(cudaGraphExecDestroy(exec));ck(cudaGraphDestroy(graph));
 }
 return bad;
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
  native_moe_combine_multi_gated(parts.p,w.p,shared.p,g.p,out.p,N,K,T,st);
  ck(cudaStreamEndCapture(st,&graph));ck(cudaGraphInstantiate(&exec,graph,nullptr,nullptr,0));ck(cudaGraphLaunch(exec,st));ck(cudaGraphLaunch(exec,st));ck(cudaStreamSynchronize(st));
  auto a=out.get(),b=ref.get();int unequal=0,nonfinite=0,clobber=0;float maxerr=0;
  for(int i=0;i<T*N;++i){unequal+=std::memcmp(&a[i],&b[i],4)!=0;nonfinite+=!std::isfinite(a[i])||!std::isfinite(b[i]);maxerr=std::fmax(maxerr,std::fabs(a[i]-b[i]));}
  for(int i=T*N;i<MAX*N;++i)clobber+=(a[i]!=canary[i]||b[i]!=canary[i]);
  std::printf("CASE T=%d seed=%d distribution=%d differing_floats=%d nonfinite=%d canary_failures=%d max_abs_error=%.9g\n",T,seed,dist,unequal,nonfinite,clobber,maxerr);
  bad+=(unequal||nonfinite||clobber);++cases;ck(cudaGraphExecDestroy(exec));ck(cudaGraphDestroy(graph));
 }
 bad+=shared_pipeline(st);
 ck(cudaStreamDestroy(st));std::printf("SUMMARY cases=%d failed=%d\n",cases,bad);return bad?1:0;
}
