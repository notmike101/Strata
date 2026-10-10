## E221 / selected-coding ABBA and bounded ambiguity repeat

The predeclared R122control/R123candidate short-first and R124candidate/R125control longer-first matrix completed: same binary/libraries, exact fixture, configs differing only by prefix-stage0/1, all12payload files byte-identical across arms. Every response512tokens with zero cache reuse; one excluded warmup and five measured seeds101-105 per cell per arm. All forty measured runs retained, including the slow81.8 values. Ordinary ten-run medians:

| Workload | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
| short/stream/new | server_decode_tps | 92.30000 | 92.20000 | -0.108% |
| short/stream/new | prompt_tps | 209.80000 | 217.90000 | +3.861% |
| short/stream/new | request_e2e_tps | 80.67079 | 81.11180 | +0.547% |
| short/stream/new | stream_total_tps | 80.68892 | 81.12850 | +0.545% |
| short/stream/new | ttft_seconds | 0.81828 | 0.80017 | -2.213% |
| short/stream/new | request_seconds | 6.34699 | 6.31228 | -0.547% |
| longer/stream/new | server_decode_tps | 90.30000 | 90.35000 | +0.055% |
| longer/stream/new | prompt_tps | 510.20000 | 513.20000 | +0.588% |
| longer/stream/new | request_e2e_tps | 43.29510 | 43.42237 | +0.294% |
| longer/stream/new | stream_total_tps | 43.29902 | 43.42572 | +0.293% |
| longer/stream/new | ttft_seconds | 6.16989 | 6.13393 | -0.583% |
| longer/stream/new | request_seconds | 11.82582 | 11.79116 | -0.293% |

Both named decode targets are met, as are the measured prompt and client-E2E comparisons. However short server decode is92.20candidate versus92.30control, a0.10tok/s decrease, not an improvement. The first pair also had small E2E decreases, while the pooled E2E medians improved. Preserve this ambiguity and do not turn it into a general no-degradation claim. Decode ranges overlap widely; no statistical certainty is asserted.

Bounded next action, declared before more inference: one additional unchanged matched pair, R126control then R127candidate, both short-first, same frozen payloads/seeds. This repeats the order that showed the first-pair loss. Include every earlier and additional measured run in final ordinary fifteen-run medians per configuration/cell. Close this comparison after this pair; do not keep rerunning it until favorable. No seed exclusion, changing prompt, sampling, context, allowance or quality checker. If uncertainty or a regression remains, retain it as unproven and investigate a new mechanism instead of promoting on a selected subset.

Q0155/5 completed-answer quality and original TTL matrix remain separate. Stream/nonstream cache-hit and nonstream-miss confirmations plus real-use/near-limit gates are still missing for C056. Full goal remains active and unqualified. All four arms passed16GiB physical/commit guards and exact cleanup; production configuration restored after each. No launcher changes.
