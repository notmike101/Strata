#ifdef NDEBUG
#undef NDEBUG
#endif
#include "strata/core/token_barrier.hpp"
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <stdexcept>

int main() {
    using strata::core::TokenBarrier;
    // A cached long context with a tiny fresh suffix must keep the short policy.
    assert(TokenBarrier::interval_for_prompt(64,1025,1)==0);
    assert(TokenBarrier::interval_for_prompt(64,1025,1024)==0);
    assert(TokenBarrier::interval_for_prompt(64,1025,1025)==64);
    assert(TokenBarrier::interval_for_prompt(64,1025,262144)==64);
    assert(TokenBarrier::interval_for_prompt(0,1025,3034)==0);
    assert(TokenBarrier::interval_for_prompt(64,0,1)==64);
    TokenBarrier off(164, 0);
    int t=4, chain=3;
    off.clip(200,t,chain);
    assert(t==4 && chain==3 && !off.due(200));
    // Different accepted-prefix lengths must reach exactly the same boundaries.
    for (int interval : {1,2,3,7,64,257}) {
        for (int seed=1;seed<=100;++seed) {
            TokenBarrier b(164,interval);
            uint32_t rng=seed;
            int64_t pos=164, last=164;
            for (int step=0;step<2000;++step) {
                rng=rng*1664525u+1013904223u;
                int base=1+(rng%8), tail=(rng>>4)%8;
                int old_base=base, old_tail=tail;
                b.clip(pos,base,tail);
                assert(base>=1 && base<=old_base && tail>=0 && tail<=old_tail);
                assert(pos+base+tail<=last+interval);
                int keep=1+(rng>>12)%(base+tail);
                pos+=keep;
                assert(b.due(pos)==(pos==last+interval));
                if (b.due(pos)) { b.advance(pos); last=pos; }
            }
        }
    }
    TokenBarrier b(3032,64);
    t=4;chain=4;b.clip(3094,t,chain);assert(t==2 && chain==0);
    t=1;chain=4;b.clip(3094,t,chain);assert(t==1 && chain==1);
    assert(b.due(3096));b.advance(3096);assert(!b.due(3096));
    bool rejected=false;
    try { b.advance(3097); } catch(const std::logic_error&) { rejected=true; }
    assert(rejected);
    rejected=false;
    try { t=1;chain=0;b.clip(3161,t,chain); } catch(const std::logic_error&) { rejected=true; }
    assert(rejected);
    std::puts("PASS token barriers: disabled identity, 1.2M accepted-prefix steps, clipping and boundary validation");
}
