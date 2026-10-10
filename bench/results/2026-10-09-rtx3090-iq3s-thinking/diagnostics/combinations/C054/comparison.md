## E196 / C054 complete ABBA: numeric thresholds reached, no-degradation unproven

Same C051 engine0dea69dc and loaded libraries, modelIQ3_S,262144context,INT8KV, compatible CPUF16vision, serial requests, MTP4/minp.70 and fixed thinking numeric profile. ControlR112/R115 has coupled/Gumbel0/0; candidateR113/R114 has1/1. Other configuration fields match exactly. All measured request bytes match control, seeds101-105,512completion tokens and zero cache reuse. One excluded warmup per cell per fresh process, two opposite workload orders, ten measured rows per cell per configuration. The comparison script verifies these conditions. No cherry-picked seed, peak or upper median.

| Workload | Configuration | Decode median | Prompt median | E2E median | Stream-total median | TTFT median seconds |
|---|---|---:|---:|---:|---:|---:|
| short | control | 88.55 | 209.35 | 77.56124 | 77.57229 | 0.838461 |
| short | candidate | 90.15 | 205.30 | 78.41483 | 78.42810 | 0.856666 |
| longer | control | 86.55 | 496.00 | 42.45596 | 42.46041 | 6.153906 |
| longer | candidate | 87.15 | 496.45 | 42.64870 | 42.65235 | 6.150953 |

All raw decode values in arm order, each arm in seed101-105 order:

- short control: [91.2, 88.7, 88.4, 91.2, 87.4, 87.6, 87.6, 87.7, 92.4, 90.0]; accepted/offered 1663/2229.
- short candidate: [90.9, 91.6, 90.0, 87.7, 88.9, 88.8, 91.5, 90.3, 86.1, 90.7]; accepted/offered 1710/2194.
- longer control: [82.2, 86.7, 88.1, 86.5, 88.1, 81.6, 92.4, 84.2, 86.6, 84.7]; accepted/offered 1952/2584.
- longer candidate: [81.7, 89.7, 84.5, 86.0, 89.8, 83.4, 90.2, 84.7, 88.3, 91.4]; accepted/offered 1927/2527.

Candidate ordinary decode medians90.15short/87.15long reach the corrected numerical90/85 thresholds in these original TTLCache streaming miss cells only. Both candidate five-run arms also reach the corresponding thresholds individually. Pooled short decode+1.81percent and E2E+1.10percent; longer decode+0.69percent and E2E+0.45percent. These modest gains need the remaining workload/quality evidence and are not a global goal-completion claim.

Short prompt processing209.35 to205.30tok/s is -1.93percent; TTFT0.838461 to0.856666seconds rises0.018205seconds. Longer prompt496.00 to496.45tok/s. The preregistered3percent stop threshold was only a screening rule, never permission to accept a regression. The user's no-prompt-degradation requirement is NOT proven. This finite ABBA screen is closed; do not keep repeating it until the prompt difference disappears. Preserve this mixed result and investigate the prompt/cache interaction through separately specified evidence. Coupled/Gumbel changes the seeded text stream; finite target-distribution checks are archived, not a claim of byte-identical output or a full model-quality guarantee.

Quality status: Q010's prior HC/accepted-usage candidate remains4/5 under32768, and its three-request replay does not erase the failure. C054 is a distinct combined configuration with no completed five-answer quality suite yet. Q011 production5/5 cannot be transferred to it. Neither quality nor any missing real-use gate is waived. No production launcher or source change promoted. All four exact launcher trees cleaned up and original production config3457fdfe restored. Physical/commit16GiB floors passed; observed GPU memory returned457MiB and utilization0percent after R115.

Next bounded step: one five-seed32768 complete-answer suite for C054 (Q014-coupled-quality), unchanged checker, tasks and numeric profile. Do not retry it until passing. If it fails, preserve and reject promotion. If it passes, proceed to the outstanding selected-coding/nonstream/cache-hit and real-use cells with matched production controls; quantify prompt behavior in those cells rather than treating the present1.93percent loss as allowed. No further blind C054 TTLCache repetitions. Keep the goal active and leave production unchanged until every gate passes.
