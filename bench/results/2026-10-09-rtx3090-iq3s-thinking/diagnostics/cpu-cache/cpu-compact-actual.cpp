#include "src/kernels/cpu/iq_avx2.cpp"
#define main parity_fixture_main
#include "src/kernels/cpu/iq_avx2_parity.cpp"
#undef main
#include "cpu-compact-kernel.inl"
#include <atomic>
namespace {
std::atomic<bool> c018_on{false};
const uint8_t* c018_base=nullptr;
size_t c018_stride=0,c018_blocks=0,c018_experts=0;
const compact_probe::Block* c018_expanded=nullptr;
}
namespace strata::kernels::cpu {
void c018_native_gu_rows(const NativeFmt& f,const uint8_t* blob,const void* const* act,int nt,float* const* ff,int r0,int r1) {
    if(!c018_on.load(std::memory_order_relaxed)) {native_gu_rows(f,blob,act,nt,ff,r0,r1);return;}
    const size_t offset=size_t(blob-c018_base),index=offset/c018_stride;
    if(offset%c018_stride || index>=c018_experts)std::abort();
    compact_probe::gu(f.gu_type,c018_expanded+index*c018_blocks,int(f.n_embd/256),act,nt,ff,int(f.n_ff),r0,r1);
}
}
#define native_gu_rows c018_native_gu_rows
#include "src/kernels/cpu/pool.cpp"
#undef native_gu_rows


#include "strata/artifact/gguf_reader.hpp"
int main(int argc,char** argv) {
    if(argc!=3)return 1;
    setvbuf(stdout,nullptr,_IONBF,0);ggml_cpu_init();
    if(!cpu::cpu_avx2_ok()||!pin_to(0))return 3;
    _putenv_s("STRATA_IQ256_GATHER","1");_putenv_s("STRATA_IQ256_GATHER_IQ2_S","0");_putenv_s("STRATA_IQ_MT_MIN","1");
    strata::GgufModel model({argv[1],argv[2]});
    const auto* arch=model.meta().get("general.architecture");
    if(!arch||arch->s!="qwen4exp")return 4;
    cpu::ExpertPool pool(9,false,true,cpu::PoolAffinity::All,30);
    int layers=0,cases=0;
    for(int l=0;l<48;++l) {
        size_t shard[3];const strata::TensorInfo* tensor[3];
        const char* roles[3]={"ffn_gate_exps.weight","ffn_up_exps.weight","ffn_down_exps.weight"};
        for(int role=0;role<3;++role) {
            tensor[role]=model.find("blk."+std::to_string(l)+"."+roles[role],&shard[role]);
            if(!tensor[role]||!model.in_bounds(*tensor[role],shard[role]))return 5;
        }
        if(int(tensor[0]->type)!=21)continue;
        ++layers;
        if(int(tensor[1]->type)!=21)return 6;
        for(int r=0;r<3;++r) {
            auto s=tensor[r]->shape;
            if(s.size()!=3||s[0]!=uint64_t(r==2?kFF:kH)||s[1]!=uint64_t(r==2?kH:kFF)||s[2]!=512)return 7;
        }
        cpu::NativeFmt f;std::string error;
        if(!cpu::native_fmt(21,int(tensor[2]->type),kH,kFF,f,error))return 8;
        Acts act(f,1901+l);
        for(int e:{0,173,511}) {
            std::vector<uint8_t> blob(f.bytes);
            const size_t offsets[3]={0,f.up_off,f.down_off};
            const size_t bytes[3]={f.up_off,f.up_off,f.bytes-f.down_off};
            for(int r=0;r<3;++r)std::memcpy(blob.data()+offsets[r],model.shard(shard[r]).tensor_data(*tensor[r])+size_t(e)*bytes[r],bytes[r]);
            auto cache=compact_probe::expand(blob.data(),2*kFF*(kH/256),21);
            c018_base=blob.data();c018_stride=f.bytes;c018_blocks=cache.size();c018_experts=1;c018_expanded=cache.data();
            std::vector<float> output(8*kH),ref;
            for(int nt:{1,2,3,4,5,6,8}) {
                cpu::ExpertJobMulti job{};job.nt=nt;job.blob=blob.data();
                for(int t=0;t<nt;++t){job.nact[t]=act.gup[t];job.out[t]=output.data()+t*kH;}
                for(int v=0;v<2;++v) {
                    c018_on.store(v!=0);std::fill(output.begin(),output.end(),0.f);
                    pool.run_split_multi_native(f,&job,1);
                    if(v==0)ref=output;
                    else {
                        size_t n=rows_differ(ref.data(),output.data(),size_t(nt)*kH);
                        std::printf("C019 layer=%d expert=%d gu=21 down=%d nt=%d compared=%lld different=%zu\n",l,e,f.d_type,nt,(long long)(nt*kH),n);
                        if(n)return 9;
                        for(float x:output)if(!std::isfinite(x))return 10;
                        ++cases;
                    }
                }
            }
        }
    }
    std::printf("C019 layers=%d cases=%d all actual-weight outputs BITWISE EQUAL\n",layers,cases);
    return layers==10&&cases==210?0:11;
}
