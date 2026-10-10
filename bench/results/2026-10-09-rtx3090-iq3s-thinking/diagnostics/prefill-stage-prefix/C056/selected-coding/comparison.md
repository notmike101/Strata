## E224 / C056 selected-coding comparison closed with all fifteen runs

The single additional pair declared in E221 completed. R126control and R127candidate both ran short-first, matching the order that showed the initial small loss. No more repeats of this comparison. Final ordinary medians include all fifteen measured values per configuration/cell from R122-R127, not just the latest pair. All six arms share the exact binary, loaded libraries and fixture; all twelve request files per arm are byte-identical. Every measured and warmup response has512tokens with zero cache reuse. Sixty measured requests and twelve excluded warmups total. Original four-arm medians and the small short-decode decrease remain in first-comparison.md and c056-coding-pooled.json.

| Workload | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
| short/stream/new | server_decode_tps | 91.80000 | 92.30000 | +0.545% |
| short/stream/new | prompt_tps | 208.80000 | 216.60000 | +3.736% |
| short/stream/new | request_e2e_tps | 80.19192 | 81.19105 | +1.246% |
| short/stream/new | stream_total_tps | 80.21467 | 81.20750 | +1.238% |
| short/stream/new | ttft_seconds | 0.82610 | 0.79745 | -3.469% |
| short/stream/new | request_seconds | 6.38468 | 6.30611 | -1.231% |
| longer/stream/new | server_decode_tps | 90.30000 | 90.50000 | +0.221% |
| longer/stream/new | prompt_tps | 509.90000 | 513.20000 | +0.647% |
| longer/stream/new | request_e2e_tps | 43.29664 | 43.42885 | +0.305% |
| longer/stream/new | stream_total_tps | 43.29993 | 43.43206 | +0.305% |
| longer/stream/new | ttft_seconds | 6.17425 | 6.13374 | -0.656% |
| longer/stream/new | request_seconds | 11.82540 | 11.78940 | -0.304% |

Both90short/85approximately3K targets pass. Final short decode92.3candidate versus91.8control and longer90.5versus90.3 are non-decreasing observed medians; this does not establish statistical certainty or a per-seed speed guarantee. Prompt216.6/513.2versus208.8/509.9 and client E2E81.19105/43.42885versus80.19192/43.29664 also pass the measured non-degradation gate. Candidate fresh-process medians were91.9/91.1,93.8/90.2 and93.3/90.5, each meeting the respective target. All raw ranges and MTP acceptance counts remain published. Server decode, client E2E, stream-total and TTFT are separate metrics. The client runs on this PC through its LAN IP; no remote-device network latency was measured.

This closes only the selected-coding streaming cache-miss requirement. Original TTL streaming-miss proof remains90.05/88.00 over ten runs/cell in its separate comparison. Q0155/5 natural-stop answers with72checks each remains the completed-answer quality proof at the approved32768 allowance. Thinking sampler,262144 configured context, IQ3_S quant, INT8 KV, CPUF16 vision, MTP and expert profile remained fixed. No quality-test substitution, changed allowance, disabled gate, quant reduction or context reduction.

Each of the six arms passed the independent16GiB physical/commit floors, full launcher/server/text/vision cleanup and production configuration restoration. No new engine or launcher edit in this turn. The existing candidate is engine/strata-cuda133-prefix-preserve.exe SHA256cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. No promotion and no benchmark model retained at this checkpoint.

Next required work: selected-coding stream exact-repeat cache-hit and nonstream miss/hit cells, each with fresh-process confirmations in opposite workload order and matched controls. Keep misses from hit-interleaved arms separate from this closed pure-miss comparison because the expert-cache history differs. Record actual positive prompt reuse for hits. Then complete tools, vision, remote reasoning levels, natural-stop/exact-output, cancellation, mixed history, idle/cleanup and near-limit recall/memory gates on this exact candidate. Preserve the earlier258901input2.6decode observation; do not imply90tok/s at full occupied context. Full goal remains active and unqualified.
