#pragma once
#include "strata/core/conversation_cache.hpp"

namespace strata::core {
// The caller must have proved the donor checkpoint invalid before recycling.
// Metadata is never transferred. The next save must overwrite every state byte.
inline bool recycle_checkpoint_storage(ConversationCheckpoint& target, ConversationCheckpoint& donor) {
    if (&target == &donor || !target.stage_parts.empty() || !donor.stage_parts.empty() ||
        !target.gdn.empty() || !target.ple.empty() || !target.tails.empty() ||
        !target.dead.empty() || !target.block_pos.empty() ||
        (donor.gdn.empty() && donor.ple.empty() && donor.tails.empty() &&
         donor.dead.empty() && donor.block_pos.empty())) return false;
    target.gdn.swap(donor.gdn);
    target.ple.swap(donor.ple);
    target.tails.swap(donor.tails);
    target.dead.swap(donor.dead);
    target.block_pos.swap(donor.block_pos);
    return true;
}
}
