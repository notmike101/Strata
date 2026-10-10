# Narrow Q6 one-warp component implementation plan

> Execution: use the executing-plans workflow inline in the current branch.

Goal: retain C030's small, repeated exact-kernel gain as an opt-in component and
measure its effect in the existing optimized service before promotion.

Architecture: add a CUDA-only one-warp kernel to src/kernels/cuda/native_mmvq.cu.
The STRATA_Q6_ONEWARP=1 opt-in selects it only for one column, input width 2560,
output rows 10240. Every other shape and the unset default keep the original
dispatch. Reuse the existing original Q6 dot and warp reduction helpers.

Spec: q6-onewarp-plan.md, c030-confirmation-plan.md and stack-qualification-plan.md.
No sampling, model/quant, context, expert placement or precision changes.

- [x] Add a graph-inspection dispatch test. Link it against the unchanged library;
      assert the opt-in selects a kernel named native_q6_k_onewarp_kernel. Observe
      failure before implementation. Test default and wrong-shape fallbacks too.
- [x] Add only the measured four-warps-per-CTA kernel with four virtual partials
      per lane and ordered reduction; gate CUDA-only and exact measured shape.
- [x] Build current C:\Strata source using the existing CUDA 13.3 main build,
      preserving retained engine and control library. Run dispatch checks and
      integrated actual-weight parity with the independent old reference.
- [ ] Test the new binary with the opt-in disabled to prove default behavior,
      then enabled on the same fixed served short/3K and random coding workloads.
      Keep binary/hash/config/source receipts and every measured row. Reject or
      repeat according to all metrics, not whether one component alone hits 90.
- [ ] Test promising combinations using the predeclared factorial plan. Run all
      fixed quality/stability/memory checks before changing launcher defaults.
- [ ] Review, publish to the existing fork branch, and verify full cleanup. CUDA
      is available; HIP/SYCL execution is unavailable and must be disclosed.
