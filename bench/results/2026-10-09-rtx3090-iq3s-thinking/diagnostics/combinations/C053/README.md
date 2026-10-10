## E172 / C053 closed and rejected; goal-threshold correction

Four-arm ABBA completed: R106A89.9/84.8, R107B88.8/86.9,
R108B88.8/86.0, R109A90.2/90.0 short/~3K decode medians. All48requests
were512tokens/cachemiss, exact twelve payloads equal across all four processes.
Warmups excluded, all ten measured rows per workload/configuration retained.
Same a5f34477 engine; only STRATA_ACCEPTED_USAGE_BARRIER_ONLY0/1 differs.

| Ordinary all-ten-run median | All-request accounting | Barrier-only accounting | Change |
|---|---:|---:|---:|
| short server_decode_tps |90.050000|88.800000|-1.388%|
| short prompt_tps |206.950000|207.950000|+0.483%|
| short request_e2e_tps |78.864052|77.595824|-1.608%|
| short stream_total_tps |78.877924|77.606974|-1.611%|
| short ttft_seconds |0.842238|0.833783|-1.004%|
| short request_seconds |6.492189|6.598294|+1.634%|
| longer server_decode_tps |86.650000|86.050000|-0.692%|
| longer prompt_tps |495.600000|495.250000|-0.071%|
| longer request_e2e_tps |42.471709|42.298843|-0.407%|
| longer stream_total_tps |42.475400|42.302017|-0.408%|
| longer ttft_seconds |6.160471|6.169093|+0.140%|
| longer request_seconds |12.056357|12.104357|+0.398%|

The candidate fails no-degradation: pooled decode and E2E are lower in both
workloads. Short88.8 misses90; longer86.05 misses90. Reject, archive patch/tests/
build evidence, and restore the four changed source files to49db7853. C051's
split/accounting incompatibility guard remains. Production launcher/config/engine
remain unchanged. No extra repetitions or threshold sweep. The C053 a5f34477
binary remains a diagnostic artifact; build-cuda86-main contains its objects until
a future rebuild. Do not silently call it current clean-source code after restore.

Runtime proof: all24control requests used accepted accounting; both candidate
processes logged active0 on all12short requests and active1 on all12longer
requests. Every longer request logged seven64-token barrier updates. Therefore
the failed result is not an inactive-setting/fallback explanation. Longer results
can change despite identical longer policy because prior short requests change
cache history. Output/draft behavior also varies; no isolated kernel gain inferred.

Safety: minimum available physical62421921792
and commit41622216704bytes;16GiB floor passed
through all48requests. Exact launcher/server/engine/vision cleanup passed each arm,
config3457fdfe restored, GPU457MiB idle. No benchmark model resident.

THRESHOLD CORRECTION: goal-90-contract.md established90tok/s in BOTH short and~3K
qualifying speed cells. Several later progress/ledger summaries, including recent
90/85 wording, accidentally repeated the earlier pre-goal85longer target. They do
not amend the fixed goal contract. Keep historical numbers; interpret completion
against90/90 and every quality, stability, memory and workload gate. This correction
restores the existing contract, not a new threshold or a relaxation. The saved
contract file itself is unchanged. Current summaries will explicitly say90/90.

The C053 control's90.05/86.65screen medians therefore do NOT meet the goal. The
short margin is only0.05tok/s, long is below90, and frozen random coding/full quality
remain unqualified. C052's90.5/84.5 control was also unqualified. No speed or quality
promotion follows from any of these control observations.

Next: stop selecting from the TTLCache screen alone. Measure the retained native
HC1/acceptedusage1/conditional64/minfresh1025 stack on the already-frozen random
medium coding fixture with unchanged512token speed and8192token separate quality
checks. Use the clean-source C051 engine0dea69dc, same numeric thinking profile,
context/vision, independent memory guards and exact cleanup. That is a NEW measured
baseline on that fixture, not a reuse of a5f34477's90.05result. Preserve Q007's two
incomplete answers as failures; establish whether they persist on this stack before
another sampled-drafting combination. Goal remains active; no blocker declared.
