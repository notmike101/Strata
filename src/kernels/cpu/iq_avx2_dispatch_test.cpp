// Environment dispatch tests run in separate processes: settings are cached on first use.
#include "strata/kernels/cpu/expert_layout.hpp"
#include "strata/kernels/cpu/iq_avx2.hpp"
#include <cstdio>
#include <cstdlib>

namespace cpu = strata::kernels::cpu;

int main(int argc, char** argv) {
    if (!cpu::cpu_avx2_ok()) return 77;
    if (argc != 4) return 2;
    const int base = cpu::iq256_variant();
    const int types[] = {18, 21, 22, 16, 17, 20, 23, -1};
    for (int i = 0; i < 8; ++i) {
        const int expected_gather = i < 3 ? std::atoi(argv[i + 1]) : -1;
        const int expected = expected_gather < 0 ? base :
            ((base & ~cpu::kIq256Gather) | (expected_gather ? cpu::kIq256Gather : 0));
        const int actual = cpu::iq256_variant_for(types[i]);
        if (actual != expected) {
            std::fprintf(stderr, "type %d: variant %d, expected %d (legacy %d)\n",
                         types[i], actual, expected, base);
            return 1;
        }
    }
    return 0;
}
