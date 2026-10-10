## E146 / P019 window divergence reproduced; bounded diagnostic closed

Two fresh processes replayed the exact nine R091 requests in order, with
512 generated tokens each and zero cached prompt tokens. Same 8057ab78 engine,
backend library hashes, fixed CPU share .80/MAX1024, HC1, accepted usage1 and
unchanged sampling/context/model/vision; only the logit dump destination differs.
All eighteen requests completed. This is instrumentation evidence, not a
qualifying throughput comparison; neither tracing nor its timings is promoted.

The first three requests (short warmup, short runs1/2) have identical first
logits, full output, window sequences and offered/accepted draft counts. Each
first-logit snapshot contains248320 finite F32 values. Short run3 also starts
with bit-identical logits, but its window sequence first differs at zero-based
index347: absolute position644 has T4 in A and T2 in B. A has374 windows and
198/138 offered/accepted drafts; B has373 windows and197/139. Full output differs.
Thus the first observed divergence occurs earlier than C047's longer run2.
This supersedes any interpretation that fixed80 guarantees short reproducibility;
C047's six matching short pairs remain valid observations for those runs only.

The subsequent short run4 already has different first logits (maximum absolute
difference1.12157655); short run5 .97195768; longer warmup .78262842; longer run1
.80348349; longer run2 .82470608. Every subsequent full output differs. Across
all nine requests, first logits match4/9, full outputs and windows match3/9.
Exact raw hashes and per-request first differing window positions are in
summary.json; complete request-aligned position/T sequences in window-traces.json.
Raw binary logits stay private. Every request payload matches R091 byte-for-byte.

Interpretation: equal initial logits do not guarantee equal subsequent decoding.
The observed T4/T2 split is consistent with the existing timing-dependent draft
policy, and later-request initial differences are consistent with carried cache
state. We have not captured every intermediate logit/token or residency map, so
this does not prove the window policy caused the first text difference, nor
that cache adaptation is the sole source. Tracing itself can perturb timing.
The finite two-process budget is closed; no third repeat is needed.

Next architectural hypothesis: adaptation every four variable-length windows
can create different cache publication positions. A separately designed
accepted-token-boundary scheduler could hold placement stable within fixed token
blocks, clip speculative windows to boundaries, and fence cache publication.
PR1779 is a reference, but its multi-GPU implementation cannot be imported
unchanged into this single-GPU serial path. Before implementation, establish a
finite test plan, preserve .20 PCIe/sampling/quality, prove copy ordering and
default-off behavior, and measure its synchronization cost. No such code or
production setting was changed by P019. This is a candidate, not a verified fix.

Memory safety: minimum available physical/commit bytes A62252527616/40998223872,
B62169985024/40726831104, both above the independent16GiB floors. Exact supervisor
cleanup verified no remaining Strata launcher/server/engine/vision processes.
Production config restored to SHA2563457fdfe7d69fbf6651e2031320cdebf88a9d8d269ebbe459db7fdd885e8c9f0;
GPU memory returned to457MiB. No benchmark model remains resident.

The90/85 server_decode_tps goal and full quality/workload matrix remain active
and unqualified. C047 remains unpromoted: its automatic-share pooled short/3K
decode90.00/84.35 versus fixed80 88.15/83.95. End-to-end metrics remain separate
and include prompt processing plus generation and API completion overhead.
