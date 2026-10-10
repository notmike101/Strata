#pragma once

namespace strata::core {

// Capture and commit must agree: only a window that advanced its own state
// can skip the later commit graph. Full QFUSE currently captures without it.
inline constexpr bool verify_self_commit(int tokens, bool batch, bool enabled, bool full_qfuse) {
    return tokens == 1 && !batch && enabled && !full_qfuse;
}

}  // namespace strata::core
