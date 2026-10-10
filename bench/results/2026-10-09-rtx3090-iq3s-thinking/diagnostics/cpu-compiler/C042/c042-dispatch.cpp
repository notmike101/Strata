#define STRATA_CLANG_IQ3S_BUILD 1
#include "src/kernels/cpu/native_expert.cpp"
#define main old_fixture_main
#include "src/kernels/cpu/iq_avx2_parity.cpp"
#undef main
static int calls=0;
namespace strata::kernels::cpu {
void iq3s_clang_iq256_gu_rows_v(int v,int type,const uint8_t*b,size_t row,size_t off,int n,const void*const*a,int nt,float*const*out,int r0,int r1){
 calls++;iq256_gu_rows_v(v,type,b,row,off,n,a,nt,out,r0,r1);
}
}
int main(int argc,char**argv){
 bool on=argc>1&&std::string(argv[1])=="on";_putenv_s("STRATA_IQ3S_CLANG",on?"1":"0");_putenv_s("STRATA_IQ_MT_MIN","1");_putenv_s("STRATA_IQ256_GATHER","1");_putenv_s("STRATA_IQ256_GATHER_IQ2_S","0");ggml_cpu_init();
 for(int type:{18,21,22})for(int nt:{1,2,4,8}){
  cpu::NativeFmt f;std::string error;if(!cpu::native_fmt(type,20,kH,kFF,f,error))return 2;std::vector<uint8_t>b(f.bytes);uint64_t seed=123+type;fill_blob(b.data(),f,seed);Acts act(f,435);std::vector<float>out(nt*kFF),ref(nt*kFF);float*o[8],*r[8];for(int t=0;t<nt;t++){o[t]=out.data()+t*kFF;r[t]=ref.data()+t*kFF;}
  int before=calls;cpu::native_gu_rows(f,b.data(),act.gup,nt,o,0,kFF);cpu::iq256_gu_rows_v(cpu::iq256_variant_for(type),type,b.data(),f.gu_row,f.up_off,kH,act.gup,nt,r,0,kFF);
  bool dispatch=calls-before==(on&&type==21?1:0);size_t diff=rows_differ(out.data(),ref.data(),out.size());std::printf("DISPATCH on=%d type=%d nt=%d calls=%d expected=%d bit_differences=%zu\n",on,type,nt,calls-before,on&&type==21?1:0,diff);if(!dispatch||diff)return 4;
 }std::puts("C042 DISPATCH PASS");
}
