# Q6 / PCIe interaction: 80 measured requests

Every cell below contains ten measured runs from two fresh processes, each with
one excluded warmup and five measured seeds. All measured requests generated 512
tokens with zero reused prompt tokens. Input JSON is byte-identical by label.
The binary, loaded CUDA libraries, GGUF shards, projector, expert profile,
262,144 context, INT8 KV, vision and thinking sampling match. Every arm retained
8,409 GPU cache slots. Only the named Q6 flag and PCIe share differ.

These are ordinary medians of every measured row, not averages of process medians.
Per-process summaries, ranges and every raw value are in factorial.json. A/B and
C/D are separate AB/BA blocks; temporal drift is a limitation of this matrix.
The earlier memory failures remain in the ledger and are not hidden by this table.

| Setting | Q6 | PCIe share | Workload | Decode tok/s | Prompt tok/s | E2E tok/s | Stream tok/s | TTFT s |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| A | 0 | 0.20 | short | 84.75 | 195.80 | 73.9670 | 73.9834 | 0.8942 |
| A | 0 | 0.20 | longer | 82.70 | 496.25 | 41.5853 | 41.5884 | 6.1490 |
| B | 1 | 0.20 | short | 84.60 | 193.35 | 73.8859 | 73.9032 | 0.9127 |
| B | 1 | 0.20 | longer | 81.20 | 497.15 | 40.9434 | 40.9772 | 6.1479 |
| C | 0 | 0.10 | short | 86.60 | 204.80 | 75.9383 | 75.9526 | 0.8501 |
| C | 0 | 0.10 | longer | 83.20 | 495.35 | 41.6315 | 41.6363 | 6.1728 |
| D | 1 | 0.10 | short | 87.50 | 203.40 | 76.4059 | 76.4202 | 0.8699 |
| D | 1 | 0.10 | longer | 82.85 | 495.80 | 41.5816 | 41.5852 | 6.1653 |

The combination does not reach the target. Compared with PCIe 0.10 alone,
Q6 improves the pooled short decode median but lowers the longer decode median.
It is therefore not a verified improvement across both workloads. Its exact
kernel speedup is real within C030's microbenchmark, but cannot be promoted as a
served-speed win. Production retains its previous engine and settings. All eight
arms completed full-tree cleanup and passed the original host-memory floors.
Full coding, cold/warm, tools, vision and maximum-context qualification is not
claimed. Q007's incomplete coding answers remain an unresolved quality gate.

The arithmetic interaction is retained in factorial.json as (D-C)-(B-A), in each
metric's own units. A positive interaction does not imply that D beats C, reaches
90 tok/s, or meets the prompt/client no-regression requirement.
