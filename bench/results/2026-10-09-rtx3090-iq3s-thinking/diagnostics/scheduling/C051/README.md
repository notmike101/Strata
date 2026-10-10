## E161 / C051 split-window compatibility defect found and guarded

Broader scheduling review followed three closed compiler paths. CUDA mapped()
already uses cudaHostAllocMapped without WriteCombined (verify.cpp:185), unlike
the uncached SYCL path motivating PR1713. Current CUDA GPU resident/PCIe experts
already overlap host CPU work after flagA publication and before flag completion.
A whole-layer drain/CPU-service/relaunch would serialize that work and add host
launches. No measured transferable cost justifies porting Arc's graph segmentation
now. Do not equate its647.7ms waitflag-only trace category with removable work.

Existing --spec-split offers a different supported scheduling architecture:
two token groups interleave pre/post work, allowing CPU experts of one group to
overlap GPU mixer/router work of the other. It increases weight traffic and kernel
launches; source documents an earlier~7% regression on another experiment. No
local campaign comparison found. A bounded same-day screen is more informative
than implementing ungrounded new graph segmentation.

Interaction found BEFORE combining: Verifier::run passes each group's local rows
to pool_multi_cb with no global-row offset. AcceptedUsage::record indexes from
zero on each call. A second group therefore appends routes to first-group rows,
and commit(keep) can count rejected rows as accepted. C046 guard omitted spec_split.
All prior C046-C049/P019/P020 arms used unsplit windows, so this finding does not
invalidate their counters. It does invalidate a prospective combined experiment.

Fix: STRATA_ACCEPTED_USAGE=1 now rejects effective --spec-split at option validation,
with an explicit diagnostic. Default-off and unsplit accepted-usage paths keep
their arithmetic and scheduling. No engine kernel, model bytes, context, sampling
or production launcher change. Full answer-quality equivalence is not claimed.

Regression test tools/test_accepted_usage_modes.py uses absent model paths and
never loads a model. Initial test attempt lacked --ple-gguf and failed too early;
retained as a harness mistake. Corrected test reached the downstream CPU feature
check, proving the missing compatibility guard on the old ac43e898 engine. After
the fix, the unsafe mode returns2 with the new diagnostic. Three controls reach
the no-model sentinel: accepted1/--no-spec-split, accepted0/--spec-split, and
accepted1/--spec-split followed by --no-spec-split (last argument wins).

CUDA13.3 sm86 Release build passed. Token-barrier1.2M oracle steps, accepted-usage
4096 windows, Windows affinity, and IQ AVX2 parity all passed. Final comment-only
rebuild and four CLI controls passed. HIP/SYCL were not built; no upstream review.
Candidate engine SHA256 0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd; kept separately at
engine/strata-cuda133-usage-guard.exe. Existing production executable unchanged.
No throughput claim for this configuration guard.
