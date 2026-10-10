# C040: Blanket Clang GU rejected

Clang19.1.5 replaced GU code generation across IQ3_XXS/IQ3_S/IQ2_S while retaining MSVC pool/down/quantization. All576 actual-weight pool-output cases (48layers, experts0/173/511, T1/2/4/8) matched bitwise. Synthetic large-weight pool timing:27cells, nine workers plus host0,30tasks, T1/2/4, jobs1/3/6; one warmup and five alternating rounds of100calls. Geomean candidate/control time .9484517 but worst1.1166899. Predeclared no-cell>3% regression gate FAILED. Blanket replacement rejected. All failed cells retained; no served speed claim.

Hardware: RTX3090 24GiB, i9-10900KF10c20t,128GiBDDR4-3200, Windows11 build26200. Exact model: ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF IQ3_S. Actual tensors read locally and never published. Raw all-run logs, source, compile commands and parity evidence attached. Prior C040 losses remain part of the ledger. See fixed goal-90-contract.md for served workload and pending quality/memory/matrix gates.
