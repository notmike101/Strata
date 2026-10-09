# C021: Q6_K row grouping diagnostic

Status: queued behind observer audit and unchanged-source CUDA 13.4 build. No production source changed.

Question: can grouping 2, 4, or 8 output rows in one 128-thread CTA reduce the cost of the actual Q6_K output head without changing its computed values or adding weight storage?

Evidence: `NativeHead::load` copies the original GGUF tensor and selects its actual type. The startup Q5_K text is hardcoded and misleading; the actual-weight C014 diagnostic verified Q6_K, input 2560, output 248320, 521472000 bytes. The single-column native Q6_K kernel uses four warps and one row per CTA for this input width. P009 includes substantial Q6_K activity but has completeness warnings; its aggregate percentages are not whole-request critical-path shares. C014's packed layout was slower and added memory, so no packed weights are proposed here.

Keep each row's per-thread block stride, signed scales, activation quantization, DP4A sequence, FMA sequence, warp combination order and lane-zero result. Each thread accumulates independent rows in additional registers; shared partials retain the current warp order. Guard final rows. No extra persistent device or host weight buffer, quantization change, model change, sampling change or context change.

1. Build unchanged production source using the verified CUDA13.4.92 toolchain, sm86 and existing MSVC/Release options. Preserve current CUDA13.3 engine and runtime. Record linked/loaded library identities; do not silently combine compiler and runtime experiments.
2. Write a standalone actual-weight harness. The candidate stub deliberately produces an incorrect result so the parity test must fail before implementing row grouping. Compare baseline and candidate built in the same translation unit/toolchain.
3. Verify bitwise equality on full head and small/odd output-row slices for zero, alternating signs, random and varied-scale finite inputs. Verify guard values around outputs and CUDA launch/synchronization errors. Target at least 8 input patterns x 7 output-row shapes x 3 group sizes; count every comparison. CUDA math flags match the native source contract.
4. Only after parity passes, run one warmup and at least 11 alternating CUDA-event timing pairs per group on the full head. Report all values, ordinary medians and ranges. This is a kernel diagnostic, never server TPS or goal proof.
5. Reject if no repeatable gain. If successful, integrate opt-in exact-head dispatch with unchanged default, review the change, and build all available affected backends; explicitly report HIP/SYCL limitations. Re-test actual integrated source parity.
6. Test the unchanged fixed served matrix against same-day same-toolchain control. Preserve cold/cache, prompt speed, compiler/test quality, tools, vision, long-context, memory and stability gates. Promote only a repeated whole-service winner; otherwise archive the patch and restore source/config.

Even a kernel win may be too small to bridge the entire 90 tok/s gap. Continue broader bottleneck investigation rather than claiming a target from this microbenchmark.
