#include "strata/kernels/cpu/iq3s_cache.hpp"
#include "strata/kernels/cpu/pool.hpp"
int main() {
    strata::kernels::cpu::ExpertPool pool(1,false,true);
    strata::kernels::cpu::Iq3sCache cache;
    strata::kernels::cpu::ExpertLayout layout;
    std::string reason;
    uint8_t b=0;
    if(cache.prepare(&b,1,layout,1,32ull<<30,32ull<<30,16ull<<30,reason))return 1;
    return cache.get(0,0)!=nullptr;
}
