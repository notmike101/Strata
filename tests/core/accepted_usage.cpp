#ifdef NDEBUG
#undef NDEBUG
#endif
#include "strata/core/accepted_usage.hpp"
#include <cassert>
#include <stdexcept>
#include <vector>
#include <cstdio>

int main() {
    using strata::core::AcceptedUsage;
    AcceptedUsage rows;
    std::vector<float> usage(12, 2.0f);
    const int32_t l0[] = {0,1, 2,3, 1,2, 3,0};
    const int32_t l1[] = {1,-1, 4,2, 0,3, 2,1};
    // Independent scalar oracle for every accepted-prefix length, including zero.
    for (int keep=0; keep<=4; ++keep) {
        rows.begin(4);
        rows.record(0,4,l0,4,2);
        rows.record(2,4,l1,4,2);
        auto got=usage, want=usage;
        for (int t=0;t<keep;++t) for (int j=0;j<2;++j) {
            ++want[l0[2*t+j]];
            int e=l1[2*t+j]; if(e>=0 && e<4) ++want[8+e];
        }
        rows.commit(got,keep);
        assert(got==want);
    }
    rows.begin(1); const int32_t dup[]={2,2}; rows.record(1,4,dup,1,2);
    auto got=usage; rows.commit(got,1); assert(got[6]==4.0f);
    rows.begin(1); rows.commit(got,1); assert(got[6]==4.0f); // no stale rows
    auto* storage=usage.data();
    try {
        strata::core::PauseUsage paused(usage);
        assert(usage.empty());
        throw std::runtime_error("dispatch failed");
    } catch(const std::runtime_error&) {}
    assert(usage.data()==storage && usage==std::vector<float>(12,2.0f));
    // 4096 deterministic windows, full model dimensions, independent oracle.
    uint32_t rng=19;
    auto next=[&] { rng=rng*1664525u+1013904223u; return rng; };
    for(int trial=0;trial<4096;++trial) {
        int n=1+trial%8, keep=(trial/8)%(n+1);
        rows.begin(n); std::vector<float> actual(48*512,0), expected=actual;
        for(int layer=0;layer<48;++layer) {
            std::vector<int32_t> ids(n*10);
            for(auto& id:ids) id=(int32_t)(next()%514)-1;
            rows.record(layer,512,ids.data(),n,10);
            for(int t=0;t<keep;++t) for(int j=0;j<10;++j) {
                int id=ids[t*10+j]; if(id>=0 && id<512) expected[layer*512+id]+=1;
            }
        }
        rows.commit(actual,keep); assert(actual==expected);
    }
    std::puts("accepted usage: all prefix, invalid ID, duplicate, reset, and exception restoration checks passed");
}
