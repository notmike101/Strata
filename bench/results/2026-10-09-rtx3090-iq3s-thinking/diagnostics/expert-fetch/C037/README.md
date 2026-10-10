# C037: expert-fetch division removal rejected

The predeclared offline screen replaced per-vector64-bit division with per-block
blob/stripe assignment. Both paths retain384 blocks,256 threads and identical
16-byte copies. P009 established the kernel's presence; instrumented duration
was not interpreted as a critical-path percentage. Current upstream main remains
fb58e0dbc8399662c0e47c76578c6e878b14f6cf; no update was available.

All140 parity/guard cases passed across seven actual model blob sizes, counts
0,1,2,3,4,5,7,8,16,64 and both paths. A total3,131,392,000
copied bytes were verified against pinned host input, including source-pointer
permutation and untouched destination prefix/tail guards. Data patterns are
synthetic; exact copy parity is independent of tensor arithmetic.

CUDA13.3.73/sm86 graph timing used32 copies per graph, one excluded warmup per
variant and seven alternating measured rounds. Ordinary medians and every raw
round are retained. Nonempty geometric mean candidate/control ratio0.999604
fails the required<=0.95; cell range0.979664..1.021740.
Maximum empty-call penalty0.224000us. Reject without another run or integration.
The unchanged copier's measured payload bandwidth median was
6.440GB/s (decimal), range6.211..6.466.
This supports a bandwidth-bound interpretation for this isolated transfer screen,
not a proof of the whole engine's bottleneck or physical TPS ceiling.

| Blob bytes | Count | Original us | Candidate us | Ratio |
|---:|---:|---:|---:|---:|
| 1510400 | 0 | 1.433000 | 1.376000 | 0.960223 |
| 1510400 | 1 | 234.303996 | 234.043002 | 0.998886 |
| 1510400 | 2 | 468.032002 | 467.005014 | 0.997806 |
| 1510400 | 4 | 935.711980 | 938.015997 | 1.002462 |
| 1510400 | 8 | 1872.128010 | 1880.473971 | 1.004458 |
| 1715200 | 0 | 2.272000 | 2.227000 | 0.980194 |
| 1715200 | 1 | 267.866999 | 267.520010 | 0.998705 |
| 1715200 | 2 | 531.418979 | 529.247999 | 0.995915 |
| 1715200 | 4 | 1068.639994 | 1083.423972 | 1.013834 |
| 1715200 | 8 | 2122.047901 | 2168.181896 | 1.021740 |
| 1868800 | 0 | 2.272000 | 2.240000 | 0.985915 |
| 1868800 | 1 | 290.847987 | 291.359007 | 1.001757 |
| 1868800 | 2 | 590.080023 | 578.079998 | 0.979664 |
| 1868800 | 4 | 1171.607018 | 1157.248020 | 0.987744 |
| 1868800 | 8 | 2355.360031 | 2355.999947 | 1.000272 |
| 1971200 | 0 | 1.888000 | 2.039000 | 1.079979 |
| 1971200 | 1 | 307.289988 | 307.608008 | 1.001035 |
| 1971200 | 2 | 610.656023 | 611.168027 | 1.000838 |
| 1971200 | 4 | 1224.279046 | 1223.423958 | 0.999302 |
| 1971200 | 8 | 2538.877010 | 2510.047913 | 0.988645 |
| 2176000 | 0 | 1.504000 | 1.728000 | 1.148936 |
| 2176000 | 1 | 338.164002 | 337.433010 | 0.997838 |
| 2176000 | 2 | 674.965978 | 674.399018 | 0.999160 |
| 2176000 | 4 | 1349.753976 | 1351.552010 | 1.001332 |
| 2176000 | 8 | 2727.072001 | 2696.928024 | 0.988946 |
| 2329600 | 0 | 1.459000 | 1.408000 | 0.965045 |
| 2329600 | 1 | 360.960007 | 360.222012 | 0.997955 |
| 2329600 | 2 | 723.551989 | 721.271992 | 0.996849 |
| 2329600 | 4 | 1448.384047 | 1445.119977 | 0.997746 |
| 2329600 | 8 | 2906.719923 | 2917.632103 | 1.003754 |
| 2662400 | 0 | 1.472000 | 1.404000 | 0.953804 |
| 2662400 | 1 | 411.872000 | 411.552012 | 0.999223 |
| 2662400 | 2 | 824.703991 | 829.501987 | 1.005818 |
| 2662400 | 4 | 1651.826978 | 1648.733974 | 0.998128 |
| 2662400 | 8 | 3310.688019 | 3343.647957 | 1.009956 |


Memory was checked with one global snapshot, not continuous monitoring:
physical120,894,988,288 and
commit124,079,091,712 bytes available, above
the original16GiB floors. Fixed host/device allocations were below0.5GiB each.
The process exited successfully and no model server was launched. No production
source, launcher, quality gate, sampling, context, vision or model changes.

Next direction: reduce transfers through a separately justified residency or
prefetch architecture, rather than reworking this already bandwidth-limited copy
loop. Prior lower-PCIe-share, device-plan and cache-profile failures remain binding
evidence; do not repeat them without a distinct new mechanism. Full90 TPS and
coding quality qualification remain unmet. The goal tool now reports active.
