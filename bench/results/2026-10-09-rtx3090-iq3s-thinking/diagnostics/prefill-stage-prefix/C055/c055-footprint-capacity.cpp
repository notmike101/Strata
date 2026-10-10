#include "strata/prefill/prefill.hpp"
#include "strata/core/layout.hpp"
#include "strata/core/session.hpp"
#include "strata/kernels/cpu/expert_layout.hpp"
#include "strata/kernels/qsa.hpp"
#include <cstdio>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    strata::core::ModelGeometry g;
    std::string error;
    if (!strata::kernels::cpu::expert_layout_load(argv[1], g.n_layers, g.n_expert, error)) {
        std::fprintf(stderr, "%s\n", error.c_str()); return 3;
    }
    strata::prefill::Prefill::set_pinned_share(1.0);
    strata::prefill::Prefill::arm_cpu_share(true, true);
    strata::kernels::QsaShapes shapes = strata::kernels::qsa_real_shapes();
    std::vector<strata::core::QsaState> qs(g.n_qsa_layers());
    strata::core::SessionState ss{};
    ss.max_cells = 262144;
    ss.qsa_states = qs.data();
    const auto& layout = strata::kernels::cpu::expert_layout();
    std::printf("kv_mode,capacity,bytes_needed,max_blob,uniform_maxblob_slots,ring_slots\n");
    for (int mode : {1, 2}) {
        for (auto& q : qs) {
            q.max_cells = ss.max_cells;
            q.kv_mode = mode;
            q.n_pages = (ss.max_cells + shapes.page_size - 1) / shapes.page_size;
            q.kv_int8 = true;
        }
        for (int capacity : {64, 128, 160, 163, 192, 224, 256, 512, 1024, 3072, 8192}) {
            const auto bytes = strata::prefill::Prefill::bytes_needed(g, ss, capacity);
            std::printf("%d,%d,%llu,%llu,%llu,%lld\n", mode, capacity,
                (unsigned long long)bytes, (unsigned long long)layout.max_blob,
                (unsigned long long)((bytes+layout.max_blob-1)/layout.max_blob),
                (long long)strata::prefill::Prefill::ring_slots_for(capacity));
        }
    }
}
