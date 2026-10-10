# Small gains and interaction checks

User steering: improvements below the final TPS target may be combined, but their
interactions must be tested. Reaching 90 in an isolated component is not a gate.
The retained format-gather CPU path, IQ2_S gather exclusion and adaptive lag 2
already form a measured stack. Preserve that stack as control A.

Reopen only C029's narrow 2560-input/10240-output, four-warps-per-CTA case as a
provisional component lead. It was faster in 10 of 11 paired microbenchmark rounds,
with ordinary median 27.104 versus 27.360 us. The general mapping remains rejected.
Do not reject the narrow case solely because the gain is small or under target.
Confirm it in two more independent processes and check other actual Q6 tensors of
that shape before deciding whether an opt-in production dispatch is justified.
Do not extrapolate 0.94% kernel improvement into 0.94% whole-request improvement.

R052 tests zero PCIe work for missed experts with the current improved CPU path;
all GPU-cache hits still execute on GPU. It is independent of Q6 dense projections.
Use its measured result to decide whether that component is worth combining.
If zero share loses, the earlier 0.10 result remains an explicitly mixed candidate,
not a production winner. A combination must remove its observed short/client
regression rather than hiding that regression behind the longer-input result.

For two promising components B and C, run A, A+B, A+C and A+B+C with identical
payloads, context and sampling, single request concurrency, warmups and all seeds.
Repeat fresh processes in reversed order. Report all metric medians and ranges;
calculate the observed combined gain and interaction rather than adding isolated
percentages. If the combination loses, remove one component and verify recovery.

Changes in expert placement can alter CPU/GPU rounding, so complete coding, tools,
vision, reasoning modes, cache/nonstream/cold/warm and long-context memory checks
remain promotion gates. An exact kernel component must still pass production-source
parity. The 90 server_decode_tps goal remains active; no target, sampling or output
quality requirement changes. Leave only one benchmark server tree at a time and
none after an arm or handoff.
