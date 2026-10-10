#pragma once
#include <algorithm>
#include <cstdint>
#include <stdexcept>

namespace strata::core {
// The serial verifier may consume only accepted input rows up to this boundary.
// Disabled mode preserves the caller's base and chained window unchanged.
class TokenBarrier {
    int64_t interval_, next_;
public:
    static int64_t interval_for_prompt(int64_t interval, int64_t minimum_fresh, int64_t fresh) {
        return fresh >= minimum_fresh ? interval : 0;
    }
    TokenBarrier(int64_t start, int64_t interval) : interval_(interval), next_(start + interval) {}
    void clip(int64_t position, int& base, int& tail) const {
        if (!interval_) return;
        const int64_t left = next_ - position;
        if (left <= 0) throw std::logic_error("unpublished token barrier");
        base = (int) std::min<int64_t>(base, left);
        tail = (int) std::min<int64_t>(tail, left - base);
    }
    bool due(int64_t position) const { return interval_ > 0 && position == next_; }
    int64_t position() const { return next_; }
    void advance(int64_t position) {
        if (!due(position)) throw std::logic_error("token barrier advanced at wrong position");
        next_ += interval_;
    }
};
} // namespace strata::core
