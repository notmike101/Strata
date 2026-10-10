#pragma once
#include <cstdint>

namespace strata::prefill {
// Zero retains the full staging allocation. A positive bound is an absolute
// prompt end, including any cached prefix, not the number of fresh tokens.
inline int64_t stage_page_count(int64_t cells, int64_t full_pages, int64_t page_size) {
    if (cells < 0 || full_pages <= 0 || page_size <= 0) return -1;
    if (cells == 0) return full_pages;
    const int64_t pages = cells / page_size + (cells % page_size != 0);
    return pages <= full_pages ? pages : -1;
}
inline bool stage_range_fits(int64_t pos, int64_t count, int64_t capacity) {
    return pos >= 0 && count >= 0 && pos <= capacity && count <= capacity - pos;
}
inline bool stage_slot_needs_refill(bool prefix_bound, int64_t slot, int64_t scratch_first) {
    return !prefix_bound || slot >= scratch_first;
}
}  // namespace strata::prefill
