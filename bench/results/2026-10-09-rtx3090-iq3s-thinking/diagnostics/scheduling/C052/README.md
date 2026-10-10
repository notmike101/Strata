## E165 / C052 complete, split-window scheduling rejected

Previous goal turn was progress: C050 closed, C051 guard fixed and pushed49db7853.
This turn completed same-binary C052 A/B with one warmup and five measured runs
per short/~3K workload, exact twelve request payloads byte-identical. Every
request512tokens/cachemiss; C051 engine0dea69dc, HC1, acceptedusage0, barrier0,
fixed model/context/vision/sampling. Sole arm change: --no-spec-split/--spec-split.

| Ordinary five-run median | Unsplit | Split | Change |
|---|---:|---:|---:|
| Short server_decode_tps |90.5|79.0|-12.707%|
| ~3K server_decode_tps |84.5|78.3|-7.337%|
| Short prompt_tps |212.2|204.9|-3.440%|
| ~3K prompt_tps |494.7|494.9|+0.040%|
| Short request_e2e_tps |78.62648|69.80172|-11.224%|
| ~3K request_e2e_tps |41.98263|40.31463|-3.973%|
| Short stream_total_tps |78.63763|69.81643|-11.218%|
| ~3K stream_total_tps |41.98680|40.31906|-3.972%|
| Short TTFT seconds |.818503|.861862|+5.297%|
| ~3K TTFT seconds |6.183140|6.166672|-0.266%|

Control short91.3,87.5,90.5,85.5,96.7; longer83.3,84.5,81.8,86.4,85.8.
Split short79.0,81.0,78.6,79.2,78.3; longer78.3,76.4,76.3,78.4,78.7.
No slower seed or first graph capture removed. Short failure was noticed after
the longer set had begun; completed that already-planned set for evidence and
ran no extra confirmation. R104/R105 reservations unused. Reject; no promotion.
The control90.5 short is not full90/85 qualification (long84.5, quality pending).

Actual codepath evidence: live identity records exact split flags, engine hash,
and captured multiple-token windows. generate.cpp passes spec_split to set_split;
record_window chooses two groups when split_ and T>=2. Source is same in both.
No timing-instrumentation flags. Full output quality remains unqualified; these
truncated throughput samples do not establish compilable coding answers.

Independent16GiB floor passed: minimum physical62413287424 and
commit41514856448bytes. All exact launcher/server/engine/vision trees
stopped; config3457fdfe restored, idleGPU457MiB. No process-memory polling during
requests. Production unchanged. The scheduling path is closed without a split
geometry sweep or speculative-accounting combination.
