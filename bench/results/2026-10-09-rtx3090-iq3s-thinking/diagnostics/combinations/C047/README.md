# C047 fixed prompt share on the combined stack

## E144 / C047 complete comparison and reproducibility evidence

The finite four-arm ABBA comparison completed: 40 measured requests plus eight
excluded warmups. Every measured request generated 512 tokens with zero cached
prompt tokens. All 36 cross-arm payload-file comparisons are byte-identical.
Same engine 8057ab78..., libraries, model, vision, context and sampling. The sole
factor is fixed 80% CPU prompt share versus auto on the same HC-fast plus
committed-row-accounting stack; both have CPU_SHARE_MAX=1024.

| All 10 runs per workload | Auto short / ~3K | Fixed80 short / ~3K |
|---|---|---|
| server_decode_tps | 90.00 / 84.35 | 88.15 / 83.95 |
| Prompt tok/s | 206.05 / 495.95 | 218.55 / 496.40 |
| request_e2e_tps | 78.5048 / 41.9447 | 77.8091 / 41.8843 |
| stream_total_tps | 78.5225 / 41.9485 | 77.8212 / 41.8881 |
| TTFT seconds | 0.85517 / 6.16258 | 0.80599 / 6.15881 |

Fixed80 changes short/~3K decode by -2.06%/-0.47%, prompt by +6.07%/+0.091%,
and client E2E by -0.89%/-0.14%. It is not a no-degradation winner and is NOT
promoted. The faster prompt path and improved repeatability remain useful
experimental evidence for a distinct future combination. No extra fraction or
repeat is run. Auto's isolated R090 passed both numeric thresholds, but the
paired pooled ~3K median does not. Including the two earlier same-binary C046
HC1/accepted1 auto passes (R086/R088; implicit rather than explicit identical
1024-token sharing limit), all 20 runs per workload give 88.2 / 84.0 decode.
That broader history is not discarded to present a favorable 90 short result.
Full random-coding quality and real-use matrix remain unresolved; goal active.

Output reproducibility: auto 0/12 byte-identical output pairs; fixed80 8/12.
All six fixed short outputs and the longer warmup/run1 match, with identical
draft offered/accepted counts. Longer run2 first diverges; later outputs also
differ. Fixed80 removes the demonstrated prompt-placement variation in these
short requests, but is not full serving determinism or a correctness proof.
P016/P017 separately show first-token logits differing under auto versus fully
identical logits AND text in two fresh GPU-only prompt controls. GPU-only prompt
read around81 tok/s is rejected for production. P018's 90 measured calibrated
share readings selected80% by the predeclared rounding rule, not a sweep.

All four performance arms and five diagnostic processes passed independent
16 GiB available-physical AND commit guards and exact launcher/server/text/vision
cleanup. Per-process memory was not polled during generation. Production config
and executable hashes remain3457fdfe... /6048736d...; idle GPU457MiB. Diagnostic
prefill log extension was archived and removed, with no retained source change.
No benchmark model remains resident.

Next investigation: residual variation can propagate through timing-based
suffix-window selection into cache adaptation scheduled by window count. This
is a hypothesis, not a diagnosis from the final aggregate counts. Inspect the
first differing longer window before fixing anything. PR1779's accepted-token
cache barriers are a larger architectural alternative to the current accepted-
row heat alone; its published implementation waits at fixed token boundaries
and must be separately adapted/tested for single-GPU serial serving. Do not
reuse prior losing intervals or kernels without distinct new mechanism/evidence.

