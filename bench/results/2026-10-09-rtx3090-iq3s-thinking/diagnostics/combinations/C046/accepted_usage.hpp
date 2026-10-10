#pragma once
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <vector>

namespace strata::core {
// Routing heat for committed verify inputs; rejected draft inputs never heat the cache.
// Serial serve only. This does not change expert selection or expert computation.
class AcceptedUsage {
    std::vector<std::vector<size_t>> rows_;
    int rows_live_ = 0;
public:
    uint64_t examined = 0, retained = 0;
    void begin(int n) {
        assert(n >= 0);
        if (rows_.size() < (size_t)n) rows_.resize((size_t)n);
        rows_live_ = n;
        for (auto& row : rows_) row.clear();
    }
    void record(int64_t layer, int64_t experts, const int32_t* ids, int64_t n, int64_t k) {
        assert(layer >= 0 && experts > 0 && n <= rows_live_);
        for (int64_t t = 0; t < n; ++t)
            for (int64_t j = 0; j < k; ++j) {
                const int32_t e = ids[t*k+j];
                if (e >= 0 && e < experts) rows_[(size_t)t].push_back((size_t)(layer*experts+e));
            }
    }
    void commit(std::vector<float>& usage, int keep) {
        assert(keep >= 0 && keep <= rows_live_);
        for (int t = 0; t < rows_live_; ++t) examined += rows_[(size_t)t].size();
        for (int t = 0; t < keep; ++t)
            for (size_t index : rows_[(size_t)t]) {
                assert(index < usage.size());
                usage[index] += 1.0f;
                ++retained;
            }
    }
};

// Suppress the dispatcher's eager all-row accounting, preserving its allocation
// and accumulated counts even if dispatch throws. No expert data is changed.
class PauseUsage {
    std::vector<float>& usage_;
    std::vector<float> held_;
public:
    explicit PauseUsage(std::vector<float>& usage) : usage_(usage) { held_.swap(usage_); }
    ~PauseUsage() { held_.swap(usage_); }
    PauseUsage(const PauseUsage&) = delete;
    PauseUsage& operator=(const PauseUsage&) = delete;
};
}
