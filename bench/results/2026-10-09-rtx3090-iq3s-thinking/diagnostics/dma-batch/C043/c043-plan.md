# C043: existing batched adaptive-transfer path

P013 reanalyzes P009 interval unions, not a new performance run. Recorded
host-to-device pinned copies:3973calls,8,041,226,240bytes,1295.604ms summed.
There are also768.870ms where memcpy is the only recorded activity category;
this is NOT critical-path/removable time, nor proof all copies are adaptation.
Current generate.cpp adaptation uses copy_blobs when STRATA_DMA_BATCH1 while
preserving slots, immutable source bytes, stream/event ordering and deterministic
lag2 admission. Default kernel-based on-demand PCIe fetch remains unchanged.
This mechanism has not been tested in the prior ledger. It differs from failed
adapt-every8, lag3, resident exchange, expert-fetch copy-kernel and device-planner
experiments; none of those is repeated.

Existing tests/core/dma_batch_parity.cu built CUDA13.3.73/sm86; both cudaHostAlloc
and VirtualAlloc+cudaHostRegister paths passed63byte/event-order cases each,
including0/1/4/17/64/128/129uploads and37B/4KiB/2MiB sizes, modes0/1/2.
The test's aggregate diagnostic timings are retained, but it does not emit raw
per-repeat times and thus cannot establish a campaign all-run speed win. For
registered48x2MiB, submission .3348ms->.0431ms, total15.6793->15.6212ms. Do not
add submission to total, and do not extrapolate this to served TPS.

R076 defaultDMA0 versus R077 DMA1, same retained engine6048736d... and all fixed
production parameters. Fresh process per arm; TTLCache short/~3K,512tokens,
one warmup+five measured seeds101..105 each, audit-no-process,16GiB floors.
One variable only: STRATA_DMA_BATCH. No sampling/context/quant/caching policy,
PCIe mode, adapt frequency/budget/lag, precision, or kernel change.

Reject if either decode or prompt median regresses; no repeat/stack retry for a
loser. An apparent winner requires reverse-order replication and Nsight proof
of actual successful cudaMemcpyBatchAsync calls (a set flag is insufficient),
then frozen random coding, complete output tests and full required matrix.
Silent fallback means no proof the batch implementation was measured. Candidate
rates remain unqualified until activation is proven. Production unchanged.
