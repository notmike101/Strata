// Source-selection integration diagnostic using the actual host verifier.
#include "strata/core/spec_prob.hpp"
#include <cmath>
#include <cstdio>
#include <random>
int main() {
    using namespace strata::core;
    const int32_t ids[]={0,1}; const double p[]={.5,.5}; const float q[]={.75f,.25f};
    const SpecP P{ids,p,2}; const SpecQ Q{ids,q,2};
    constexpr int N=1000000;
    std::mt19937 rng(940321); std::uniform_real_distribution<float> u(0,1);
    int unexpected=0;
    for(int mode=0;mode<3;++mode) {
        int zero=0,lookup=0;
        for(int i=0;i<N;++i) {
            const int draft=u(rng)<q[0]?0:1;
            // generate.cpp: a suffix can be selected only if sbuf[0] == drafts[0].
            const bool use_lookup=mode==0?draft==0:mode==2;
            int token;
            if(use_lookup) { ++lookup; token=spec_sample(P,u(rng)); }
            else { const float accept=u(rng),residual=u(rng); token=spec_verify_row(P,draft,Q,accept,residual).token; }
            zero+=token==0;
        }
        const double first=double(zero)/N,tv=std::fabs(first-.5);
        const bool target_matches=tv<.005;
        std::printf("mode=%s lookup=%d/%d target=(0.500,0.500) observed=(%.6f,%.6f) TV=%.6f target_matches=%s\n",mode==0?"draft-dependent-suffix":mode==1?"suffix-disabled":"suffix-independent",lookup,N,first,1-first,tv,target_matches?"yes":"NO");
        unexpected += mode==0?target_matches:!target_matches;
    }
    std::printf("expected_biased_control_and_unbiased_alternatives: %s\n",unexpected?"FAIL":"PASS");
    return unexpected?1:0;
}
