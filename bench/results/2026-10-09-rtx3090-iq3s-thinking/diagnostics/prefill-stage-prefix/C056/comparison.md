## E213 / C056 complete original-workload ABBA timing result

R118control/R119candidate short-first, then R120candidate/R121control longer-first completed with fresh processes. Exact engine SHA256cc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91 and loaded libraries match; configs differ only by STRATA_PREFILL_STAGE_PREFIX0/1. Every one of the12request payload files is byte-identical across all four arms. One excluded warmup and five measured512-token cache-miss requests per cell per arm. Ordinary pooled medians below include all ten measured values, including the slower second control. No selective deletion, substitution or favorable-subset median.

| Workload | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
| short | server_decode_tps | 89.25000 | 90.05000 | +0.896% |
| short | prompt_tps | 205.55000 | 221.20000 | +7.614% |
| short | request_e2e_tps | 77.72713 | 79.19281 | +1.886% |
| short | stream_total_tps | 77.74002 | 79.20550 | +1.885% |
| short | ttft_seconds | 0.85968 | 0.79026 | -8.075% |
| short | request_seconds | 6.58717 | 6.46523 | -1.851% |
| longer | server_decode_tps | 85.90000 | 88.00000 | +2.445% |
| longer | prompt_tps | 495.50000 | 499.35000 | +0.777% |
| longer | request_e2e_tps | 42.32524 | 43.02415 | +1.651% |
| longer | stream_total_tps | 42.32902 | 43.02803 | +1.651% |
| longer | ttft_seconds | 6.16107 | 6.11338 | -0.774% |
| longer | request_seconds | 12.09681 | 11.90029 | -1.625% |

Both candidate fresh-process decode medians meet their cell thresholds: R11990.1/89.5 and R12090.0/88.0. Pooled90.05short/88.0longer meets90/85. Short prompt221.2versus205.55 and longer499.35versus495.5 also pass the no-degradation comparison; E2E79.19281/43.02415versus77.72713/42.32524 passes. Margin above90 is small; this is finite workload evidence, not a universal speed guarantee or statistical certainty. The control's drift is retained and disclosed. Server decode is not real-world TPS. Client E2E runs on the server PC's loopback endpoint, not the remote LAN harness. Thinking tokens count toward512. Cold process loading and first warmup are recorded separately, excluded from these warm medians.

All four safety floors and exact launcher/server/text/vision cleanup passed; production config3457fdfe restored after each. No model remained at the end of R121. The original C055 mixed screen is preserved and not pooled with this revised mechanism. Bounds/refill unit tests and CUDA13.3sm86 build pass; HIP/SYCL are not built or validated. Original shared-header method signatures are retained through overloads for the separate SYCL implementation. No production launcher promotion.

Next Q015 evaluates the frozen selected coding fixture with seeds101-105, natural-stop answers, approved32768cap and corrected-v2 checker hash, same72objective cases and numeric thinking sampler. The512-token speed contract is unchanged. Remaining required selected-coding speed, nonstream/repeated-prefix, tools, vision, reasoning-levels, cancellation, mixed history and near-limit memory checks still apply to C056 itself; historical configurations cannot satisfy them. Goal remains active and unqualified as a whole.
