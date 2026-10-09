#include "src/kernels/cpu/iq_avx2.cpp"
#define main parity_fixture_main
#include "src/kernels/cpu/iq_avx2_parity.cpp"
#undef main
#include "cpu-expanded-kernel.inl"
#include <atomic>
namespace {
std::atomic<bool> c016_on{false};
const uint8_t* c016_base=nullptr;
size_t c016_stride=0,c016_blocks=0,c016_experts=0;
const expanded_probe::Block* c016_expanded=nullptr;
}
namespace strata::kernels::cpu {
void c016_native_gu_rows(const NativeFmt& f,const uint8_t* blob,const void* const* act,int nt,float* const* ff,int r0,int r1) {
    if(!c016_on.load(std::memory_order_relaxed)) {native_gu_rows(f,blob,act,nt,ff,r0,r1);return;}
    const size_t offset=size_t(blob-c016_base),index=offset/c016_stride;
    if(offset%c016_stride || index>=c016_experts)std::abort();
    expanded_probe::gu_range(c016_expanded+index*c016_blocks,int(f.n_embd/256),act,nt,ff,int(f.n_ff),r0,r1);
}
}
#define native_gu_rows c016_native_gu_rows
#include "src/kernels/cpu/pool.cpp"
#undef native_gu_rows

int main(int argc,char** argv) {
    setvbuf(stdout,nullptr,_IONBF,0);ggml_cpu_init();
    if(!cpu::cpu_avx2_ok()||!pin_to(0))return 3;
    _putenv_s("STRATA_IQ256_GATHER","1");_putenv_s("STRATA_IQ256_GATHER_IQ2_S","0");_putenv_s("STRATA_IQ_MT_MIN","1");
    const bool bench=argc>1&&std::string(argv[1])=="--bench";
    for(int type:{18,21,22}) {
        cpu::NativeFmt f;std::string error;if(!cpu::native_fmt(type,20,kH,kFF,f,error))return 4;
        size_t count=(64ull<<20)/f.bytes;uint64_t seed=0xc0169988+type;
        std::vector<uint8_t> blobs(count*f.bytes);
        std::vector<expanded_probe::Block> cache;cache.reserve(count*2*kFF*(kH/256));
        for(size_t i=0;i<count;++i) {
            fill_blob(blobs.data()+i*f.bytes,f,seed);
            auto e=expanded_probe::expand(blobs.data()+i*f.bytes,2*kFF*(kH/256),type);
            cache.insert(cache.end(),e.begin(),e.end());
        }
        c016_base=blobs.data();c016_stride=f.bytes;c016_blocks=2*kFF*(kH/256);c016_experts=count;c016_expanded=cache.data();
        Acts act(f,1601);std::vector<float> output(6*4*kH),reference;
        cpu::ExpertPool pool(9,false,true,cpu::PoolAffinity::All,30);
        std::printf("MEMORY type=%d experts=%zu native_bytes=%zu expanded_extra_bytes=%zu\n",type,count,blobs.size(),cache.size()*sizeof(expanded_probe::Block));
        for(int nt:{1,2,4})for(int nj:{1,3,6}) {
            std::vector<cpu::ExpertJobMulti> jobs(nj);
            for(int i=0;i<nj;++i) {
                jobs[i].blob=blobs.data()+i*f.bytes;jobs[i].nt=nt;
                for(int t=0;t<nt;++t){jobs[i].nact[t]=act.gup[t];jobs[i].out[t]=output.data()+(i*4+t)*kH;}
            }
            for(int v=0;v<2;++v) {
                c016_on.store(v!=0);std::fill(output.begin(),output.end(),0.f);
                pool.run_split_multi_native(f,jobs.data(),nj);
                if(v==0)reference=output;
                else {
                    size_t different=rows_differ(reference.data(),output.data(),output.size());
                    std::printf("PARITY type=%d nt=%d jobs=%d values=%zu different=%zu\n",type,nt,nj,output.size(),different);
                    if(different)return 2;
                    for(float value:output)if(!std::isfinite(value))return 5;
                }
            }
            if(!bench)continue;
            for(int rep=0;rep<5;++rep)for(int phase=0;phase<2;++phase) {
                bool candidate=((rep+phase)&1)!=0;c016_on.store(candidate);
                auto start=Clock::now();
                for(int step=0;step<200;++step) {
                    for(int j=0;j<nj;++j)jobs[j].blob=blobs.data()+((step*nj+j)%count)*f.bytes;
                    pool.run_split_multi_native(f,jobs.data(),nj);
                }
                double ms=std::chrono::duration<double,std::milli>(Clock::now()-start).count()/200;
                std::printf("TIMING type=%d nt=%d jobs=%d repeat=%d variant=%s ms=%.6f\n",type,nt,nj,rep,candidate?"expanded":"native",ms);
            }
        }
    }
    std::puts("C016 ALL PARITY PASSED");
}
