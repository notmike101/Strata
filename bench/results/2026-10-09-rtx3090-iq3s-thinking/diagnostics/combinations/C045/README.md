# C045 results

## E127 / C045 completed combination assessment

All four arms completed: one excluded warmup plus five measured seeds per short/~3K workload, 40 measured requests total. All 36 cross-arm request-file comparisons are byte-identical. Engine/library hashes match; config differs only in HC-fast and batch-transfer flags. All 48 requests including warmups generated512tokens with zero prompt-cache tokens. E123-E126 preserve ranges, TTFT, stream/E2E, MTP, memory and cleanup.

| Arm | HC-fast | Batch transfers | Short server_decode_tps | ~3K server_decode_tps | Short/~3K prompt tok/s |
|---|---:|---:|---:|---:|---|
| R080 A | 0 | 0 | 88.2 | 85.1 | 204.4 / 495.8 |
| R081 B | 1 | 0 | 86.5 | 85.7 | 211.2 / 496.0 |
| R082 D | 1 | 1 | 88.9 | 82.5 | 208.5 / 496.8 |
| R083 C | 0 | 1 | 85.2 | 82.7 | 206.6 / 495.5 |

D versus A: short+0.79%, longer-3.06%; E2E77.2826/41.5286 versus77.0436/42.1234. The combined stack fails the finite confirmation trigger and final no-degradation contract. No reversed pair is run. Descriptive HC effects are B-A=-1.7/+0.6 tok/s with DMAoff versus D-C=+3.7/-0.2 with DMAon. These medians demonstrate interaction/noise, not an additive or causal estimate. No arm independently qualifies90/85 and full quality. Preserve HC-fast as an unpromoted component for a distinct justified combination. This specific DMA combination is closed. Production remains unchanged; all exact launcher trees stopped.

Next hypothesis: exclude rejected speculative rows from adaptive cache heat, reducing transfer quantity rather than copy submission overhead. Inspect and test a scoped single-GPU serial-serve derivation of PR1779; do not import its multi-GPU pipeline. Keep all numeric computation, model, sampling, MTP, context and cache precision unchanged. Any runtime placement rounding still needs quality validation.

