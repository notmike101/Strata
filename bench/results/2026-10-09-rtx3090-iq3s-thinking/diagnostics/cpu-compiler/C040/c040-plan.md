# C040: alternate CPU code generation for unchanged AVX2 expert GU

Question: does Clang19.1.5 generate faster AVX2 code for the current expert
gate/up source than MSVC19.44, without changing a single output bit?
Installed clang-cl uses the MSVC ABI. Keep MSVC pool, quantizers, down projections,
runtime and linked ggml unchanged. Only compile iq_avx2.cpp into renamed symbols
using clang-cl /O2 /arch:AVX2 /fp:precise /clang:-ffp-contract=off. Explicit FMA
intrinsics remain; no fast-math, reassociation, reduced precision or ISA change.
The10900KF does not support VNNI, so its unused variant is disabled in the probe.

One same-process correctness comparison: all actual48 layers, experts0/173/511,
token groups1/2/4/8, complete native pool output. Stop on any mismatch. Also
record unsupported source formats rather than silently claim coverage.

Only if parity passes: nine-worker pool, host core0, workers on remaining
physical cores,30 tasks, three active i-quant GU formats, IQ4_NL down, token
groups1/2/4 and1/3/6 expert jobs,256MiB synthetic streaming weights per format.
One warmup per variant and five alternating measured rounds of100 layer calls.
Require >=5% geometric mean improvement and no cell>3% slower before considering
engine integration. No timing retries or settings search after failure.

The pool screen is not served TPS and does not satisfy the goal. Preserve fixed
model/context/sampling/quality contract. Existing C039 native build objects are
not a source baseline; use the unchanged CPU library in build-cuda86. No source
or launcher modifications in this stage. Save all logs, compiler flags/hashes,
source fingerprints and sampled global memory headroom; no model server.

References: https://clang.llvm.org/docs/MSVCCompatibility.html and
https://clang.llvm.org/docs/UsersManual.html. Compatibility is tested locally,
not assumed from these documents. This tests an installed compiler, not a claim
that Clang19 is the latest LLVM release.
