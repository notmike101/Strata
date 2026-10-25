# On-demand model runtimes implementation plan

> **For agentic workers:** Use superpowers:executing-plans inline, task by task.

**Goal:** Serve chat, embeddings and images on demand with one heavyweight runtime at a time.

**Architecture:** A standalone Python gateway serializes requests and controls three
adapters. Existing Strata code and inference arguments remain unchanged.

**Tech stack:** Python standard library HTTP/process management; optional PyTorch and
Transformers worker; stable-diffusion.cpp CUDA CLI.

**Spec:** `docs/superpowers/specs/2026-10-14-on-demand-model-runtimes-design.md`.

## Global constraints

- Opt-in only; no changes to the existing server or native backends.
- No llama.cpp. Keep network access with an API key.
- One heavyweight worker at a time, no truncation, no shell execution of requests.
- Secrets and downloaded artifacts remain ignored local files.
- Ten-minute idle timeout by default; image subprocess exits after every image.

## Review focus

- Concurrent streamed chat and an embedding request retain FIFO ownership until EOF.
- Unload failure prevents another runtime from loading.
- Worker failure frees owned processes and reports an actionable error.
- Invalid model/input or unauthenticated requests do not trigger loading or evict a model.
- Gateway shutdown and client disconnect cannot leave an unowned heavy worker.

## Task 1: Queue and lifecycle

Files: `serve/runtime_manager.py`, `serve/test_runtime_manager.py`.
Interface: `RuntimeManager.use(model)` context manager, `unload()`, `unload_idle()`,
`status()`, and `close()` over runtime adapters with `load()/unload()/close()`.

- [x] Write and run failing tests for ordering, concurrency, idle time and unload failure.
- [x] Implement FIFO lifecycle ownership and rerun tests.

## Task 2: Workers and gateway

Files: `serve/model_runtimes.py`, `serve/embedding_worker.py`,
`serve/model_gateway.py`, `serve/test_model_gateway.py`.

- [x] Write failing HTTP tests for auth, routing, streams and validation.
- [x] Implement process adapters, embedding input validation, image argument generation,
      chat streaming proxy and opt-in CLI; run tests until green.
- [x] Test startup failure, exit/cleanup and default-path isolation.

## Task 3: Local install and live verification

Files: `docs/ON_DEMAND_MODELS.md`, `examples/model-gateway.json`, `.gitignore`.

- [x] Document model IDs, install requirements, controls, supported limits and rollback.
- [x] Install separate embedding environment and sd-cli, download pinned model revisions.
- [ ] Verify GPU dependencies and each actual model, then switch and inspect memory.
- [ ] Back up local launcher/config; cut over only when existing server is idle.
- [ ] Verify authenticated LAN API and rollback artifacts; commit and push the branch.

## Execution ledger

- 2026-10-14: User requested deleting both untracked files, then starting implementation.
  Both exact files removed; checkout was clean afterward. User chose LAN access with a key.
- Ruling: Execute inline in the current checkout on the explicitly requested branch.
  Further design/plan approval is covered by the user's explicit instruction to start.
- CPU baseline: existing `serve.test_server` passed 271 tests. New lifecycle/gateway/worker
  suites passed 32 tests after regression fixes from a separate code review.
- All model downloads verified against Hugging Face sizes and LFS SHA256 values.
- Live embedding check: 2560-dimensional normalized vectors; related cosine 0.9491,
  unrelated cosine 0.1890. Base64 encoding and 256-dimensional output also passed.
- Ruling: Force the local image backend to CUDA0 and supply CUDA DLLs through the
  child's PATH. The prebuilt binary otherwise silently chose CPU; device listing with
  the scoped library directory detected the RTX 3090. No system PATH or drivers changed.
- Live image check: 512x512 PNG, 10 Euler steps, seed 42 completed in 9.68 seconds.
  Its process exited and total VRAM returned to 712 MiB. Chat/switch validation pending.
