from pathlib import Path
p=Path(__file__).resolve().parent
h=(p/'c062-screen.cu').read_text()
a=h.index('static float elapsed(');b=h.index('int main()',a);h=h[:a]+h[b:]
h=h.replace(' if(!bad) timing(parts,w,shared,scaled,g,out,ref,st);',' bad+=shared_pipeline(st);')
h=h.replace('#include "c060-scale.inl"',(p/'c060-scale.inl').read_text())
h=h.replace('#include <limits>','#include <limits>\n#include "strata/kernels/shared_expert.hpp"\n#include "strata/kernels/native_mmvq.hpp"\n#include "strata/kernels/bf16_bits.hpp"\n#include "strata/kernels/f16_bits.hpp"')
fixture=r'''
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
  c062::native_moe_combine_multi_gated(parts.p,weights.p,raw.p,logit.p,out.p,N,K,T,st);
  ck(cudaStreamEndCapture(st,&graph));ck(cudaGraphInstantiate(&exec,graph,nullptr,nullptr,0));ck(cudaGraphLaunch(exec,st));ck(cudaGraphLaunch(exec,st));ck(cudaStreamSynchronize(st));
  auto a=out.get(),b=ref.get();int unequal=0,nonfinite=0;for(int i=0;i<T*N;++i){unequal+=std::memcmp(&a[i],&b[i],4)!=0;nonfinite+=!std::isfinite(a[i])||!std::isfinite(b[i]);}
  std::printf("PIPELINE T=%d differing_floats=%d nonfinite=%d\n",T,unequal,nonfinite);bad+=(unequal||nonfinite);ck(cudaGraphExecDestroy(exec));ck(cudaGraphDestroy(graph));
 }
 return bad;
}
'''
h=h.replace('int main(){',fixture+'\nint main(){')
(p/'c062-integration-red.cu').write_text(h)
build=(p/'build-c062.cmd').read_text().replace('c062-screen.cu','c062-integration-red.cu').replace('c062-screen.exe','c062-integration-red.exe');(p/'build-c062-integration-red.cmd').write_text(build)
run=(p/'run-c062.py').read_text().replace('C062','C062-integration-red').replace('c062-screen','c062-integration-red');(p/'run-c062-integration-red.py').write_text(run)
(p/'C062-integration-red-manifest.json').write_bytes((p/'C062-manifest.json').read_bytes())
print('Integration red fixture prepared; source unchanged')
