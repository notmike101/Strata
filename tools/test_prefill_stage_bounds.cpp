#include "strata/prefill/stage_bounds.hpp"
#include <cassert>
#include <cstdint>
#include <limits>

int main() {
    using strata::prefill::stage_page_count;
    using strata::prefill::stage_range_fits;
    assert(stage_page_count(0, 8192, 32) == 8192);
    assert(stage_page_count(1, 8192, 32) == 1);
    assert(stage_page_count(32, 8192, 32) == 1);
    assert(stage_page_count(33, 8192, 32) == 2);
    assert(stage_page_count(262144, 8192, 32) == 8192);
    assert(stage_page_count(262145, 8192, 32) == -1);
    assert(stage_page_count(-1, 8192, 32) == -1);
    assert(stage_page_count(1, 0, 32) == -1);
    assert(stage_page_count(1, 8192, 0) == -1);
    const auto big = std::numeric_limits<int64_t>::max();
    assert(stage_page_count(big, big, 1) == big);
    assert(stage_page_count(big, big / 32 + 1, 32) == big / 32 + 1);
    assert(stage_range_fits(0, 163, 192));
    assert(stage_range_fits(160, 32, 192));
    assert(!stage_range_fits(161, 32, 192));
    assert(!stage_range_fits(-1, 1, 192));
    assert(!stage_range_fits(0, -1, 192));
    assert(!stage_range_fits(1, big, big));
    assert(stage_range_fits(big, 0, big));
    using strata::prefill::stage_slot_needs_refill;
    for (int slot = 80; slot < 120; ++slot) {
        assert(stage_slot_needs_refill(false, slot, 100));
        assert(stage_slot_needs_refill(true, slot, 100) == (slot >= 100));
    }
}
