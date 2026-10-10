# C046 results

## E135 / C046 full confirmation and retained experimental component

Sixty measured512-token requests across six fresh-process arms, plus twelve excluded warmups. Fixed numeric sampling and262144context. All60 cross-arm request-file comparisons are byte-identical; same engine8057ab78... and backend libraries, only accepted-usage and HC flags differ. All measured/warmup responses have512tokens and zero cache reuse. Each arm passed independent16GiB physical/commit guards and exact cleanup.

| Group | Measured runs per workload | Short / ~3K server_decode_tps | Short / ~3K prompt tok/s | Short / ~3K request_e2e_tps |
|---|---:|---|---|---|
| A control R084+R089 | 10 | 87.40 / 81.50 | 202.25 / 496.80 | 76.6252 / 41.2801 |
| D combined R086+R088 | 10 | 87.45 / 83.30 | 203.70 / 496.40 | 76.6509 / 41.7356 |
| B accepted-usage only R085 | 5 | 87.50 / 82.80 | 206.00 / 496.00 | 77.1226 / 41.5491 |
| C HC only R087 | 5 | 88.40 / 84.20 | 201.80 / 496.50 | 77.3560 / 41.8582 |

D versus A: short+0.057%, longer+2.209%; prompt+0.717%/-0.081%; request E2E+0.033%/+1.103%. Short TTFT0.85642s versus0.84527s; longer6.16156s versus6.14619s. This is a longer-input signal with unchanged short decode, small prompt/TTFT differences and incomplete quality; not a verified no-degradation winner. The HC-only five-run arm was faster than D, so additive/causal benefit is not established. No extra repetition is authorized by the exhausted finite plan. Both targets remain unmet.

Keep accepted-row accounting disabled by default as an experimental component with tests and reproducible source; production launcher/executable/config remain unchanged. Same model bytes, routing, computation, sampling and precision; cache placement can alter CPU/GPU rounding, so full quality remains required. The meaningful longer-input result is preserved for justified future combinations, not discarded solely for missing90. Do not blindly repeat this matrix.

Runtime activation: all12requests in each of R085/R086/R088 logged positive retained/routed counts with rejected rows excluded; full counts in summary.json. This proves accounting activation, not fewer copied bytes. Tests cover all prefix lengths, invalid/duplicate IDs, reset, exception restoration and4096 random48-layer512-expert windows. Post-matrix test strengthening explicitly covers T1..8 and is registered in CMake with assertions enabled in Release. Existing IQ AVX2 parity reports0failures; Windows affinity test passes. CUDA13.3sm86 built; HIP/SYCL not built and no upstream review/merge requested.

Follow-up P016 read-only reproducibility audit: R084/R089 have identical payloads/config/binary but all12output texts differ; common prefixes range57..506characters (warmup included), not a tokenizer-level divergence measurement. Positive seeds are forwarded in serve/server.py:959-961, parsed in generate.cpp, and Verifier::run draws Philox(seed,position). Source also feeds measured round times into DraftPolicy::observe, while CPU/GPU expert arithmetic can round differently (documented at the adaptation barrier). Those are plausible contributors, NOT proof of root cause. Do not change the sampling contract or blame a different nonce. Next bounded diagnostic should isolate the first differing routing/window/logit state using identical fresh-process requests, preserving production and all safety guards.

