# C046: committed-row cache heat and HC-fast

Hypothesis: current serial verify dispatch counts rejected draft rows in adaptive
expert heat. Keeping only committed input rows may improve cache placement and
reduce misses/transfers; HC-fast addresses independent GPU arithmetic. P013 proves
transfers occur, not that their whole interval is removable. Inspired by the
accepted-usage portion of upstreamPR1779 headf3727b2464321a35c4638491d75bcda1d4ecbb9c;
no multi-GPU pipeline code is imported. This is a new cache policy, not a repeat
of C045 copy-submission batching or prior adapt-every/lag sweeps.

Implementation: opt-in STRATA_ACCEPTED_USAGE=1 for single-GPU serial serve with
synchronous adaptive cache. Record routed expert indices per verify input row;
temporarily suppress eager usage accounting with RAII restoration; count rows
0..a before the existing adaptation point, matching ver.commit(a+1). Preserve
duplicate ID counts and invalid ID handling. Discard rejected rows. Final-window
counts follow committed input rows even if output cap/EOS prevents emitting all
outputs; no change to the existing commit/emission policy. Empty/default flag
keeps the original accounting. Unsupported batch/pipeline/async/peer/helper/
all-resident modes reject opt-in. Prompt path, model bytes, expert routing,
computation, KV, sampling, MTP depth/threshold, PCIe fraction and adapt schedule
remain unchanged. Placement may change CPU/GPU rounding; this is NOT an assertion
of identical generated text or automatic quality parity.

Correctness gate: first reproduce missing-helper test failure, then pass scalar
oracle checks over all accepted prefixes, invalid IDs, duplicate IDs, repeated
windows, exception restoration, and4096 random48-layer512-expert windows. Build
CUDA13.3/sm86 engine and run existing IQ AVX2 parity and topology tests. HIP/SYCL
toolchains unavailable; not built, no upstream review/merge request. Verify
active startup message and actual retained/routed counters in each enabled arm.

Finite served budget: four fresh arms A=usage0/HC0 R084, B=usage1/HC0 R085,
D=usage1/HC1 R086, C=usage0/HC1 R087, in A/B/D/C order. SAME newly built engine
for every arm; DMA0/deviceplan0. One excluded warmup plus five seeds101..105 per
short and ~3K cell,512tokens,cachemiss,concurrency1. Forty measured requests.
Fixed262144context,INT8KV/32768resident,CPU F16vision,thinking high->xhigh unlimited,
temperature1/top_p.95/top_k20/min_p0/presence0/repetition1, MTP4/.70, PCIe.20,
lag2,9workers30tasks. Identity per request; independent16GiB physical AND commit
floors; audit-no-process; no competing builds/profilers/GUI/Git during timings.
Exact cleanup and config restore after each arm. Assert byte-identical payloads.

Assess D against A, B/C retained as component/interactions. Maximum ONE reversed
D/A pair (20more measured requests) if either decode median improves>=1% and
neither other decode/prompt/E2E median falls>1%. This is a continuation screen,
not final permission for degradation. Otherwise stop this combination. No
component must individually reach90 or win every isolated metric. Retain useful
unpromoted components with evidence. Full promotion requires90/85 repeated
ordinary medians, fixed random coding with completed tested answer, and all
cold/warm/cache/tool/vision/maxcontext/quality/stability checks; Q007 is unresolved.
No peak/microbenchmark/short-only success qualifies. Retained production stays
unchanged until all requirements pass. No model resident at handoff.
