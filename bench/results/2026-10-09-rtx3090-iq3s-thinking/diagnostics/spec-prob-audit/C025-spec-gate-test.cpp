// Integration diagnostic: the selected draft-confidence gate plus the actual host verifier.
#include "strata/core/spec_prob.hpp"
#include <array>
#include <cmath>
#include <cstdio>
#include <random>

int main() {
    using namespace strata::core;
    constexpr int N = 1000000;
    const bool pick_gate = spec_gate_pick();
    std::mt19937 rng(79013);
    std::uniform_real_distribution<float> uniform(0.0f,1.0f);
    int failures=0;
    struct Case { std::array<double,3> p; std::array<float,3> q; float floor; };
    const Case cases[] = {
        {{.5,.5,0.},{.75f,.25f,0.f},.70f},
        {{.3,.7,0.},{.8f,.1f,.1f},.70f},
        {{.5,.5,0.},{.5f,.5f,0.f},.70f},
        {{.5,.5,0.},{.75f,.25f,0.f},0.f},
    };
    const int32_t ids[]={0,1,2};
    for (int c=0;c<4;++c) {
        const auto& k=cases[c];
        const SpecP P{ids,k.p.data(),3};
        const SpecQ Q{ids,k.q.data(),3};
        int count[3]={},verified=0;
        for (int i=0;i<N;++i) {
            const float u=uniform(rng);
            const int draft=u<k.q[0]?0:u<k.q[0]+k.q[1]?1:2;
            const float gate=pick_gate?k.q[draft]:k.q[0];
            int token;
            if (gate>=k.floor) {
                ++verified;
                const float accept=uniform(rng), residual=uniform(rng);
                token=spec_verify_row(P,draft,Q,accept,residual).token;
            } else token=spec_sample(P,uniform(rng));
            ++count[token];
        }
        double tv=0;
        for (int i=0;i<3;++i) tv+=std::fabs(double(count[i])/N-k.p[i]);
        tv*=.5;
        const bool pass=tv<.005;
        failures+=!pass;
        std::printf("case=%d gate=%s floor=%.2f verified=%d/%d target=(%.3f,%.3f,%.3f) observed=(%.6f,%.6f,%.6f) TV=%.6f %s\n",c,pick_gate?"picked-token":"distribution-top",k.floor,verified,N,k.p[0],k.p[1],k.p[2],double(count[0])/N,double(count[1])/N,double(count[2])/N,tv,pass?"PASS":"FAIL");
    }
    std::printf("cases=4 failures=%d\n",failures);
    return failures?1:0;
}
