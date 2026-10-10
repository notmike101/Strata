# Q6 and PCIe-share interaction

A: rebuilt binary, Q6 off, PCIe0.20. B: Q6 on, PCIe0.20.
C: Q6 off, PCIe0.10. D: Q6 on, PCIe0.10.
All use engine SHA2561dfeecd9869c266e82961426026e14c82ff822e0e004898959a900925ea57cf4.
Keep original TTLCache requests, seeds101-105, one warmup,512 generated tokens,
streaming, concurrency1,262144 context, INT8 KV, vision and fixed thinking profile.

A/B measured as A,B,B,A in fresh processes, the second pair longer-first.
Next measure C,D,D,C the same way. These are two AB/BA blocks, not one perfectly
interleaved factorial. If a combination wins, recheck it against a fresh A and
on the frozen random coding task before broader quality/stability qualification.
Keep all per-process and pooled ordinary medians. Compute observed interaction
(D-C)-(B-A) separately for short/longer decode, prompt and client rates; do not
sum isolated gains. Preserve every slow run and all failed arms. No promotion
from this preliminary matrix; Q007 and full real-use checks remain unresolved.

R057/R059 A and R054/R058 B used8409 cache slots. Reject a request/config mismatch;
record any cache-size or host-state change explicitly. Keep one server tree at a
time. No builds, publication, code edits, UI capture or process-memory polling
during timed runs. The supervisor guards16GiB physical and commit headroom and
cleans the complete launcher tree in finally.
