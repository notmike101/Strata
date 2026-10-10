# Request timing boundaries

`server_decode_tps` measures token generation during the server's reported decode interval. The benchmark records `timings.predicted_per_second` directly. This is served generation with the configured MTP path, including its work in the server interval; it is not an isolated target-kernel microbenchmark. It excludes the separately reported prompt-processing interval.

`request_e2e_tps` is completion tokens divided by elapsed client time from immediately before opening the HTTP request until the response is read and the response context closes. It includes request/response transfer, server request handling, prompt processing, generation and client response processing. A queue wait would count if present; the benchmark deliberately sends one request at a time. Payload construction, identity checks, model loading and benchmark setup happen before the timer and are excluded. The client runs on this computer and addresses the server through this computer's LAN IP. These measurements do not include a separate LAN device's network path.

For streaming requests, `stream_total_tps` uses the same start but ends on receipt of the last nonempty reasoning/content chunk. The client records `request_e2e_tps` after consuming the stream terminator, so the two values are close but have different endpoints. Chunks can contain multiple tokens. `ttft_seconds` ends on the first nonempty reasoning/content chunk; empty events and keep-alives do not qualify. Thinking tokens count toward completion tokens and timing. These are not final-code-only rates.

## A measured example

R129, `longer-run-3-new`, seed 103, had 3,135 fresh input tokens, zero cached tokens and 512 completion tokens:

| Measurement | Value |
|---|---:|
| Server prompt interval | 6.1055 seconds |
| Server decode interval | 5.7430 seconds |
| Server decode throughput | 89.2 tok/s |
| Client complete-request interval | 11.8585512 seconds |
| Client end-to-end throughput | 43.175595 tok/s |
| Client stream-total throughput | 43.178963 tok/s |
| Client time to first text | 6.1375134 seconds |

The decode rate is approximately `512 / 5.7430`; the end-to-end rate is `512 / 11.8585512`. Prompt processing explains most of the difference in this example. This is one raw run used to explain the metric, not a median or a qualification claim. See [the raw R129 records](raw/target-80/R129-stream-cache-prefix/runs.json) and [the benchmark script](goal90-benchmark.py) for the full evidence.

The target is 90 short / 85 approximately-3K **server decode** tok/s. End-to-end throughput, prompt throughput, TTFT, latency, quality and memory remain separate acceptance checks. A decode-only value is never labeled real-world TPS.
