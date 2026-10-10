#define main parity_fixture_main
#include "src/kernels/cpu/iq_avx2_parity.cpp"
#undef main
#include "c040-api.hpp"
#include "c041-api.hpp"
#include <atomic>
namespace {std::atomic<bool> c040_on{false};}
namespace strata::kernels::cpu {
void c040_native_gu_rows(const NativeFmt& f,const uint8_t* blob,const void* const* act,int nt,float* const* ff,int r0,int r1){
 if(!c040_on.load(std::memory_order_relaxed)){c041_msvc_iq256_gu_rows(f.gu_type,blob,f.gu_row,f.up_off,(int)f.n_embd,act,nt,ff,r0,r1);return;}
 c040_iq256_gu_rows(f.gu_type,blob,f.gu_row,f.up_off,(int)f.n_embd,act,nt,ff,r0,r1);
}
}
#define native_gu_rows c040_native_gu_rows
#include "src/kernels/cpu/pool.cpp"
#undef native_gu_rows


#include "strata/artifact/gguf_reader.hpp"
int main(int argc,char**argv){
 if(argc!=3)return 1;setvbuf(stdout,nullptr,_IONBF,0);ggml_cpu_init();if(!cpu::cpu_avx2_ok()||!pin_to(0))return 3;
 _putenv_s("STRATA_IQ256_GATHER","1");_putenv_s("STRATA_IQ256_GATHER_IQ2_S","0");_putenv_s("STRATA_IQ_MT_MIN","1");
 strata::GgufModel model({argv[1],argv[2]});cpu::ExpertPool pool(9,false,true,cpu::PoolAffinity::All,30);int layers=0,cases=0;
 for(int l=0;l<48;l++){
  size_t shard[3];const strata::TensorInfo*tensor[3];const char*roles[3]={"ffn_gate_exps.weight","ffn_up_exps.weight","ffn_down_exps.weight"};
  for(int r=0;r<3;r++){tensor[r]=model.find("blk."+std::to_string(l)+"."+roles[r],&shard[r]);if(!tensor[r]||!model.in_bounds(*tensor[r],shard[r]))return 4;}
  if(int(tensor[0]->type)!=21)continue;if(int(tensor[1]->type)!=21)return 5;layers++;
  cpu::NativeFmt f;std::string error;if(!cpu::native_fmt(21,int(tensor[2]->type),kH,kFF,f,error))return 6;
  constexpr int count=64;std::vector<uint8_t>blobs(count*f.bytes);size_t offsets[3]={0,f.up_off,f.down_off},sizes[3]={f.up_off,f.up_off,f.bytes-f.down_off};
  for(int i=0;i<count;i++){int expert=(29+17*i)%512;for(int r=0;r<3;r++)std::memcpy(blobs.data()+i*f.bytes+offsets[r],model.shard(shard[r]).tensor_data(*tensor[r])+expert*sizes[r],sizes[r]);}
  std::printf("MEMORY layer=%d experts=%d bytes=%zu down_type=%d\n",l,count,blobs.size(),f.d_type);Acts act(f,2401+l);std::vector<float>output(6*4*kH),ref;
  for(int nt:{1,2,4})for(int nj:{1,3,6}){
   std::vector<cpu::ExpertJobMulti>jobs(nj);for(int j=0;j<nj;j++){jobs[j].blob=blobs.data()+j*f.bytes;jobs[j].nt=nt;for(int t=0;t<nt;t++){jobs[j].nact[t]=act.gup[t];jobs[j].out[t]=output.data()+(j*4+t)*kH;}}
   for(int v=0;v<2;v++){c040_on.store(v!=0);std::fill(output.begin(),output.end(),0.f);pool.run_split_multi_native(f,jobs.data(),nj);if(!v)ref=output;else{size_t diff=rows_differ(ref.data(),output.data(),output.size());std::printf("PARITY layer=%d nt=%d jobs=%d values=%zu different=%zu\n",l,nt,nj,output.size(),diff);if(diff||!std::all_of(output.begin(),output.end(),[](float x){return std::isfinite(x);}))return 7;cases++;}}
   for(int rep=-1;rep<5;rep++)for(int phase=0;phase<2;phase++){
    bool candidate=((rep+1+phase)&1)!=0;c040_on.store(candidate);auto start=Clock::now();
    for(int step=0;step<100;step++){for(int j=0;j<nj;j++)jobs[j].blob=blobs.data()+((step*nj+j)%count)*f.bytes;pool.run_split_multi_native(f,jobs.data(),nj);}
    double ms=std::chrono::duration<double,std::milli>(Clock::now()-start).count()/100;
    std::printf("%s layer=%d nt=%d jobs=%d repeat=%d variant=%s ms=%.6f\n",rep<0?"WARMUP":"TIMING",l,nt,nj,rep,candidate?"clang":"msvc",ms);
   }
  }
 }
 std::printf("C041 layers=%d cases=%d all parity passed\n",layers,cases);return layers==10&&cases==90?0:8;
}
