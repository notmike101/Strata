## E235 / C056 trace localizes the cache-screen failure

P023/P024 are the single predeclared diagnostic pair from E232. Every one of48requests completed512tokens with valid new/repeat cache state; identical request bytes, C056 executable and loaded libraries. Neither arm adds qualifying repetitions. Original R128-R131 failures remain closed and unchanged.

| Cell | Metric | Control | Prefix candidate |
|---|---|---:|---:|
| longer/stream/hit | logical_lent_slots | 0.0000 | 0.0000 |
| longer/stream/hit | physical_refilled_slots | 0.0000 | 0.0000 |
| longer/stream/hit | refill_ms | 0.0000 | 0.0000 |
| longer/stream/hit | batched_read_ms | 0.0000 | 0.0000 |
| longer/stream/hit | window_read_ms | 40.7000 | 40.1000 |
| longer/stream/hit | server_prompt_ms | 61.4000 | 60.8000 |
| longer/stream/hit | window_count | 326.0000 | 306.0000 |
| longer/stream/hit | verified_rows | 573.0000 | 573.0000 |
| longer/stream/hit | mean_ms_per_window | 17.5896 | 18.1846 |
| longer/stream/hit | server_decode_ms | 5611.1000 | 5564.5000 |
| longer/stream/new | logical_lent_slots | 1371.0000 | 1371.0000 |
| longer/stream/new | physical_refilled_slots | 1371.0000 | 1232.0000 |
| longer/stream/new | refill_ms | 435.1000 | 391.9000 |
| longer/stream/new | batched_read_ms | 5626.0000 | 5625.7000 |
| longer/stream/new | window_read_ms | 53.8000 | 50.8000 |
| longer/stream/new | server_prompt_ms | 6158.0000 | 6108.0000 |
| longer/stream/new | window_count | 321.0000 | 329.0000 |
| longer/stream/new | verified_rows | 581.0000 | 573.0000 |
| longer/stream/new | mean_ms_per_window | 18.3648 | 17.9690 |
| longer/stream/new | server_decode_ms | 5817.7000 | 5812.4000 |
| short/stream/hit | logical_lent_slots | 0.0000 | 0.0000 |
| short/stream/hit | physical_refilled_slots | 0.0000 | 0.0000 |
| short/stream/hit | refill_ms | 0.0000 | 0.0000 |
| short/stream/hit | batched_read_ms | 0.0000 | 0.0000 |
| short/stream/hit | window_read_ms | 41.7000 | 48.2000 |
| short/stream/hit | server_prompt_ms | 62.1000 | 68.8000 |
| short/stream/hit | window_count | 317.0000 | 310.0000 |
| short/stream/hit | verified_rows | 577.0000 | 573.0000 |
| short/stream/hit | mean_ms_per_window | 17.7508 | 17.6177 |
| short/stream/hit | server_decode_ms | 5483.6000 | 5461.5000 |
| short/stream/new | logical_lent_slots | 311.0000 | 311.0000 |
| short/stream/new | physical_refilled_slots | 311.0000 | 177.0000 |
| short/stream/new | refill_ms | 99.5000 | 55.7000 |
| short/stream/new | batched_read_ms | 603.7000 | 603.0000 |
| short/stream/new | window_read_ms | 45.9000 | 44.8000 |
| short/stream/new | server_prompt_ms | 788.3000 | 741.8000 |
| short/stream/new | window_count | 310.0000 | 329.0000 |
| short/stream/new | verified_rows | 570.0000 | 572.0000 |
| short/stream/new | mean_ms_per_window | 18.1652 | 17.2012 |
| short/stream/new | server_decode_ms | 5590.9000 | 5635.3000 |

The intended mechanism is proven on this pair: the logical masks stay311short/1371longer slots while physical refills fall to177/1232. Median refill time drops99.5 to55.7ms short and435.1 to391.9ms longer. Batched-read medians603.7 to603.0ms and5626.0 to5625.7ms are nearly unchanged. The prefix optimization removes approximately44ms of copying/refill work; it is not speeding the batched model arithmetic. Extra relayout cost is0.0ms at displayed short-median precision and0.8ms longer, so relayout synchronization is not the observed large cost here.

Both exact-repeat cells have zero loans, zero refills and zero batched reads. The short-hit prompt interval rises62.1 to68.8ms, localized primarily in the four-token verifier read41.7 to48.2ms. Therefore this repeat-request loss is not directly caused by prefix staging or refill work in that request. The source path at generate.cpp windows_ok/read_windows confirms that short tails bypass lend/read_part. Earlier request state and CPU/GPU execution remain relevant. The prior P016/P017 experiment (E137/E138) had already localized same-seed variation to time-based CPU prompt sharing: disabling it made both first logits and entire outputs identical but reduced prompt throughput to81tok/s, so that path was rejected. Do not repeat it or declare the new pair a proof of the same complete causal chain.

Short-new decode has310 versus329median windows,570 versus572verified rows and5590.9 versus5635.3ms duration. Mean per-window duration medians actually fall18.1652 to17.2012ms. This supports investigating window geometry/fixed per-window costs, not claiming an across-the-board kernel slowdown. Medians of separately varying quantities must not be multiplied as though they describe one request. All raw per-request positions, widths and counts are archived. Across the original cache arms, only1/24and4/24 paired outputs match byte-for-byte; same-configuration opposite-order processes match0/24. Equality is diagnostic, not a quality gate. Existing Q015 completed-answer evidence is neither rerun nor replaced.

Next bounded investigation: use an Nsight capture of the current short new/repeat path (with the exact frozen payload history) to attribute verifier/host/copy costs, building on the existing P020 capture infrastructure. In parallel, inspect a full-prompt checkpoint design: current exact repeats restore before the final four processed prompt tokens and re-read them. An extra checkpoint could avoid that work, but checkpoint_at synchronizes and copies recurrent state, so its fresh-request cost and eviction effect must be measured before implementing or promoting it. Replacing the normal turn checkpoint would lose reuse when assistant/thinking headers change; that alternative is rejected by design. Any retained alternative must preserve the normal checkpoint and all thinking/tool/vision behavior. This is a new cache architecture hypothesis, not permission to select a favorable prompt or reuse old quality proof after behavior changes.

The contract audit also confirms MTP4/minimum draft probability0.70/PCIe0.20 are frozen controls. Earlier T002 and R044 lower-floor trials failed in other sampler configurations. No threshold or target-sampling parameter was changed or proposed as a qualifying shortcut. Q6 one-warp/packed-layout, device planner, fixed80CPUshare and other closed paths are not reopened by this trace.

All48requests retain the exact context262144,IQ3_S,INT8KV,CPUF16vision, unlimited high/xhigh reasoning and1/.95/20/0/0/1 thinking profile. Independent16GiB physical/commit floors, exact model-tree cleanup and production3457fdfe restoration passed for each arm. No engine/source/launcher change in this turn. Goal remains active, candidate experimental and unpromoted. No benchmark model resident at this checkpoint.
