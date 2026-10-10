## E230 / C056 four-arm streaming cache comparison

R128 control and R129 candidate ran short-first; R130 candidate and R131 control ran longer-first. Each fresh process ran one excluded new/repeat warmup pair and five measured new/repeat pairs for each prompt length. All 96 requests are retained: 80 measured and 16 warmups. Each repeat request is byte-identical to its preceding new request. All new requests have zero reused tokens, all repeats have positive reuse, and all responses contain 512 completion tokens. Exact model, context, thinking sampler, prompt fixture, seeds, executable and loaded libraries remain fixed; candidate/control differ only in STRATA_PREFILL_STAGE_PREFIX. Ten measured values per configuration/cell are pooled using ordinary medians. First requests are separately retained in the JSON.

The misses in this interleaved matrix are separate from the closed pure-miss R122-R127 comparison because the expert-cache history differs. Hit prompt throughput represents only five fresh tokens, not rereading the entire cached prompt. Server decode, prompt throughput, client end-to-end, stream-total, TTFT and total latency remain separate. The benchmark client runs on this PC through its LAN IP; a separate LAN device was not measured. Model loading and pre-request identity checks are outside request timing.

| Cell | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
| longer/stream/hit | server_decode_tps | 91.450000 | 90.550000 | -0.984% |
| longer/stream/hit | prompt_tps | 80.300000 | 82.350000 | +2.553% |
| longer/stream/hit | request_e2e_tps | 90.282037 | 89.448428 | -0.923% |
| longer/stream/hit | stream_total_tps | 90.303821 | 89.460911 | -0.933% |
| longer/stream/hit | ttft_seconds | 0.090624 | 0.084702 | -6.535% |
| longer/stream/hit | request_seconds | 5.671446 | 5.724557 | +0.936% |
| longer/stream/new | server_decode_tps | 87.950000 | 89.300000 | +1.535% |
| longer/stream/new | prompt_tps | 508.750000 | 513.150000 | +0.865% |
| longer/stream/new | request_e2e_tps | 42.664828 | 43.193964 | +1.240% |
| longer/stream/new | stream_total_tps | 42.668136 | 43.197958 | +1.242% |
| longer/stream/new | ttft_seconds | 6.189421 | 6.140647 | -0.788% |
| longer/stream/new | request_seconds | 12.000598 | 11.853510 | -1.226% |
| short/stream/hit | server_decode_tps | 93.100000 | 93.750000 | +0.698% |
| short/stream/hit | prompt_tps | 76.950000 | 74.500000 | -3.184% |
| short/stream/hit | request_e2e_tps | 91.771823 | 92.133731 | +0.394% |
| short/stream/hit | stream_total_tps | 91.786058 | 92.155838 | +0.403% |
| short/stream/hit | ttft_seconds | 0.098388 | 0.102914 | +4.601% |
| short/stream/hit | request_seconds | 5.579105 | 5.557141 | -0.394% |
| short/stream/new | server_decode_tps | 93.950000 | 91.150000 | -2.980% |
| short/stream/new | prompt_tps | 208.400000 | 219.850000 | +5.494% |
| short/stream/new | request_e2e_tps | 80.922679 | 80.163395 | -0.938% |
| short/stream/new | stream_total_tps | 80.942396 | 80.179753 | -0.942% |
| short/stream/new | ttft_seconds | 0.824272 | 0.785508 | -4.703% |
| short/stream/new | request_seconds | 6.327504 | 6.386978 | +0.940% |

Gate failures: longer/stream/hit: decode_no_degradation; longer/stream/hit: e2e_no_degradation; longer/stream/hit: latency_no_degradation; short/stream/hit: prompt_no_degradation; short/stream/hit: ttft_no_degradation; short/stream/new: decode_no_degradation; short/stream/new: e2e_no_degradation; short/stream/new: latency_no_degradation.

Raw per-run values, ranges, actual fresh/reused counts and MTP acceptance are retained in c056-stream-cache-pooled.json and each arm's raw export. No failed value is dropped and these medians do not establish statistical certainty. Each arm passed its independent 16 GiB physical/commit headroom floors and exact process cleanup; production configuration was restored. The engine and production launcher were not changed during this comparison. Q015 remains separate completed-answer quality evidence; capped responses are not substitutes for that check.

Full qualification remains pending. No promotion or goal-completion claim. Continue from the recorded gate outcomes; any repeat must be bounded and declared before its result, not repeated until favorable. Nonstream miss/hit and real-use/near-limit checks still remain. The user-facing timing explanation is preserved in metrics-explained.md at the report root, with a raw R129 example and the client timer boundaries; no timing implementation was changed.
