# C037: remove per-vector division from host expert fetch

Evidence: existing P009 has15,936 fetch_blobs calls totaling305.690ms instrumented
kernel time. Median1.248us means many empty calls; do not treat the sum as a
critical-path share. The retained partial-cache path uses pcie_mode2 and this
kernel. Upstream main remains fb58e0d; no update available. DMA mode is not used:
the repository documents historical Windows driver stalls in that path.

Current kernel flattens n blobs, then divides every 16-byte vector index by the
runtime blob size. Candidate maps each CUDA block to one blob and a stripe,
then strides within that blob without per-vector64-bit division. It retains
384 blocks,256 threads, all bytes, ordering of later consumers and empty behavior.
No expert selection, weights, arithmetic, precision, context or sampling changes.

Budget: one standalone CUDA13.3/sm86 build and one GPU process. Byte parity and
destination guard checks for every distinct actual model blob size at counts
0,1,2,3,4,5,7,8,16,64; mapped pinned host source, device destination, permuted
source pointers. Graph replay uses counts0,1,2,4,8 with32 copies per graph,
one excluded warmup and seven alternating measured rounds. Keep all raw samples.
Retain only if nonempty-cell geometric mean candidate/control time<=0.95,
no nonempty cell>1.03, and no empty-cell absolute penalty>0.3us. Otherwise close
without repeat or integration. This measures transfer kernel cost, not served TPS.
Passing warrants a separate integration/parity/activation and served plan.

Host allocations remain below0.5GiB and GPU allocations below0.5GiB; retain both
16GiB host headroom floors. No model server launch and no production modifications.
Official CUDA guidance corroborates division cost, not an expected local gain:
https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#integer-arithmetic
