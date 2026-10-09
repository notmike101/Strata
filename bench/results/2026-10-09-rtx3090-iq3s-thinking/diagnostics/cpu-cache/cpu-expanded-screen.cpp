// C015 CPU diagnostic only. Include current kernels to reuse exact internal decode.
#include "src/kernels/cpu/iq_avx2.cpp"
#define main parity_fixture_main
#include "src/kernels/cpu/iq_avx2_parity.cpp"
#undef main
#include "cpu-expanded-kernel-c015.inl"

int main(int argc,char** argv) {
    setvbuf(stdout,nullptr,_IONBF,0); ggml_cpu_init();
    if(!cpu::cpu_avx2_ok() || !pin_to(2))return 3;
    const bool bench=argc>1 && std::string(argv[1])=="--bench";
    for(int type:{18,21,22}) {
        cpu::NativeFmt fmt; std::string error;
        if(!cpu::native_fmt(type,20,kH,kFF,fmt,error))return 4;
        uint64_t seed=0xc0151234+type;
        const int variant=type==22?0:cpu::kIq256Gather;
        std::vector<uint8_t> weights(fmt.down_off);
        fill_blocks(weights.data(),weights.size(),type,seed);
        auto expanded=expanded_probe::expand(weights.data(),2*kFF*(kH/256),type);
        Acts activations(fmt,1501);
        std::vector<float> a(kMaxT*kFF),b(a.size()); float* ap[kMaxT]; float* bp[kMaxT];
        for(int t=0;t<kMaxT;++t){ap[t]=a.data()+t*kFF;bp[t]=b.data()+t*kFF;}
        for(int extreme=0;extreme<2;++extreme) {
            if(extreme) {
                for(int t=0;t<kMaxT;++t)for(int bi=0;bi<kH/256;++bi) {
                    auto& q=reinterpret_cast<block_q8_K*>(activations.gu[t].data())[bi];
                    q.d=bi%3==0?0.f:((bi%2)?-.001f:.001f);
                    for(int j=0;j<256;++j)q.qs[j]=((j+t)%3==0)?-128:(((j+t)%3==1)?127:0);
                }
            }
            for(int nt=1;nt<=8;++nt) {
                std::fill(a.begin(),a.end(),0.f);std::fill(b.begin(),b.end(),0.f);
                cpu::iq256_gu_rows_v(variant,type,weights.data(),fmt.gu_row,fmt.up_off,kH,activations.gup,nt,ap,0,kFF);
                expanded_probe::gu(expanded.data(),kH/256,activations.gup,nt,bp,kFF);
                size_t different=rows_differ(a.data(),b.data(),nt*kFF);
                for(float value:b)if(!std::isfinite(value))return 5;
                std::printf("PARITY type=%d nt=%d extreme=%d rows=%lld different=%zu\n",type,nt,extreme,(long long)(nt*kFF),different);
                if(different)return 2;
            }
        }
        if(!bench)continue;
        Acts normal(fmt,1502);
        // Equivalent experts in two representations; the compressed pool alone exceeds this CPU's20MiB L3.
        const size_t count=(64ull<<20)/fmt.down_off;
        std::vector<uint8_t> pool(count*fmt.down_off);
        for(size_t i=0;i<count;++i)fill_blocks(pool.data()+i*fmt.down_off,fmt.down_off,type,seed);
        auto started=Clock::now();
        auto cache=expanded_probe::expand(pool.data(),count*2*kFF*(kH/256),type);
        double prep=std::chrono::duration<double,std::milli>(Clock::now()-started).count();
        std::printf("MEMORY type=%d experts=%zu native_bytes=%zu expanded_bytes=%zu expand_ms=%.6f\n",type,count,pool.size(),cache.size()*sizeof(expanded_probe::Block),prep);
        for(int nt:{1,2,3,4})for(int rep=0;rep<5;++rep)for(int phase=0;phase<2;++phase) {
            bool candidate=((rep+phase)&1)!=0;
            auto start=Clock::now();
            for(int sweep=0;sweep<2;++sweep)for(size_t i=0;i<count;++i) {
                if(candidate)expanded_probe::gu(cache.data()+i*2*kFF*(kH/256),kH/256,normal.gup,nt,bp,kFF);
                else cpu::iq256_gu_rows_v(variant,type,pool.data()+i*fmt.down_off,fmt.gu_row,fmt.up_off,kH,normal.gup,nt,ap,0,kFF);
            }
            double ms=std::chrono::duration<double,std::milli>(Clock::now()-start).count()/(2*count);
            std::printf("TIMING type=%d nt=%d repeat=%d variant=%s ms=%.6f\n",type,nt,rep,candidate?"expanded":"native",ms);
        }
    }
    std::puts("C015 ALL PARITY PASSED");
}
