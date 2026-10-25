# Upstream main synchronization plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge fork/main at 7dd5cf18 into perf/rtx3090-thinking-80 while retaining useful opt-in hardware work and the on-demand gateway.

**Architecture:** Use upstream's current implementation for general features and defaults. Combine its verification and prefill safety changes with the local opt-in extensions. Use upstream's checkpoint pool instead of the older local checkpoint-reuse path.

**Tech Stack:** C++20, CUDA 13.3, Python, existing Node desktop/Terminal code.

- [x] Refresh GitHub App installation discovery, verify bot identity, fetch the fork.
- [x] Preserve pre-merge tip at codex/backup-perf-before-main-20261024 (59bd8fce).
- [x] Resolve five conflicted files; retain upstream source-dependent prefill sizing, pipelined verdict guard, chunk fallback, and current checkpoint pool.
- [x] Preserve opt-in accepted usage, serial cache barriers, prefix staging and CPU dispatch; retain the local model gateway.
- [x] Update gateway static assets for upstream's favicon; its regression suite passes.
- [x] Restore the missing C++ build tools with the user's authorization; build and test CUDA plus available CPU checks.
- [x] Run Python server/setup/Terminal checks and inspect integration changes.
- [x] Record actual validation and limitations, commit the merge locally, synchronize local main, and resume post-download model preparation.

The model download continues during integration. Native model preparation/load checks are held to avoid racing changing source files. No push is part of this integration.

## Validation ledger

- Visual Studio Build Tools repair completed with exit 0; MSVC 14.44.35207 restored at its registered path.
- CUDA 13.3, SM86 Release engine built successfully, including the native CPU library and prefill MMQ libraries. The six exact-one gather decisions now honor the same per-format overrides as the other CPU row paths.
- QFUSE GPU regression, accepted-usage and token-barrier CTests: 3 passed. Per-format CPU dispatch: 11 passed. Default and mixed-gather CPU parity: zero failures. Prefix stage-bounds standalone test: passed.
- Accepted-usage CLI modes: unsafe split mode rejected before opening model files; three allowed controls reached the missing-model sentinel. The guard was moved immediately after parsing to retain this behavior with upstream's earlier model preflight.
- Real existing IQ3 profile: merged engine loaded in 43.87 seconds, answered READY (HTTP 200), unloaded, and total GPU allocation returned to 860 MiB. This was a short smoke test, not a speed or long-context benchmark. It ran before the final exact-one dispatch change; that final change was rebuilt and covered by mixed parity and dispatch tests.
- Server plus gateway/runtime suite: 385 tests, OK, 3 skipped. Setup suite after making the golden CPU fixture deterministic: 824 tests, OK, 2 skipped.
- Terminal broad run stopped at five failures: 714 passed, 27 skipped, 56 subtests passed. Three failures reproduced on exact fork/main; the other two passed individually there. No Terminal production code differs from fork/main.
- Desktop TypeScript check passed. Host broad run: 969 passed, 7 failed, 101 skipped (1077 total). It exposed an unsafe upstream whole-drive test cleanup targeting C:\Strata; Windows refused it, and no tracked files were deleted. Removed that cleanup: the fake plan creates no drive-root folder, and the fixture already cleans its own temporary folder. All 14 models-folder tests then passed. Other broad-run failures involve ACL subprocess module loading, Windows cleanup/locking, timing, and host startup; the desktop production code is unchanged from upstream.
- HIP configure was attempted and failed because the HIP root/toolchain is absent. SYCL configure was attempted and failed because icpx is absent. These backends are not validated.
- Ruling: retain upstream's checkpoint pool rather than the old local STRATA_CHECKPOINT_REUSE live path. Keep archived helper/benchmark evidence, but remove its unused include from generation. No default was changed for a claimed speed gain.
- Ruling: keep keys, model paths, generated configuration, environments, logs and builds outside the commit. Preserve the pre-merge branch for rollback; do not push.

- Follow-up host baseline: with installed dependencies and tests run serially, the selected five files ran 24 tests: 22 passed and 2 failed, with no skips: PowerShell ACL module loading and Windows process-cleanup locking. Both failures reproduced on exact fork/main; the other selected broad-run failures passed in isolation.
