# C044: upstream PR1166 host sibling integration

Reviewed PR1166 head a71da892150aa6b30cf560c2294c936a0353c5a8 from verified
Niko1221/Strata (origin). Preserve exact upstream patch plus any adaptation.
Current main fb58e0d unchanged; no stable update to apply. No new branch.
Candidate changes only thread placement: host first physical core's SMT sibling,
no workers on that physical core. No sampling/routing/numerical changes.
This is distinct from closed host-last trials; the host stays on the first
physical core. Upstream IRQ/performance claims are hypotheses, not host proof.

Apply upstream Windows layout test first; expected compile failure against
current HostCore enum is the red check. Then integrate opt-in enum/topology,
CLI/env and startup log, adapting outdated generate.cpp context only. Default
remains first. Run pool_affinity_test and existing CPU parity regression. Add
an explicit topology printout of first/last/sibling on this host. CUDA13.3 sm86
build, no Linux/HIP/SYCL runtime validation or upstream review/merge request.

Same candidate binary runtime first versus sibling, one fresh process per arm.
Fixed TTLCache short/~3K cache miss,512tokens,one excludedwarmup+five measured
seeds101..105, context262144, same vision, numeric sampling, MTP4/.70,lag2,
PCIe.20,workers9,16GiB physical/commit floors,audit-no-process. Confirm startup
host/worker IDs. No batchDMA or Clang candidate combined. Reject if generation
or prompt median regresses. Apparent win needs reverse replication, frozen
random coding plus full quality/stability/memory/cold/warm/real-use matrix.
Production launcher unchanged until qualified. Clean exact process tree.
