# C041: format-selective compiler, independent actual-weight confirmation

C040 blanket Clang GU is rejected: geometric mean time ratio.948452 but worst
cell1.11669 fails the no>3% regression gate. Preserve every C040 cell. IQ3_S alone
won all nine cells by13.6-20.8%, suggesting a distinct format-selective candidate.

Compile fresh copies of the SAME iq_avx2.cpp with MSVC and Clang, both AVX2,
STRATA_AVXVNNI0, /O2, /MT, C++20, no fast math; Clang contractoff. Renamed entry
points coexist in one executable. MSVC pool/down/quantization remain identical.
Candidate uses Clang GU only for IQ3_S type21; all other formats retain MSVC.
This is a new configuration, not deletion of failed C040 cells.

Independent gate: actual ten IQ3_S model layers,64 deterministic experts per
layer (indices29+17*i modulo512), exceeding L3 per layer. Token groups1/2/4,
1/3/6 expert jobs, nine workers plus host,30 tasks. One excluded warmup and five
alternating measured rounds of100 layer calls per cell,90 cells total. Bytewise
finite full-pool output parity per cell before timing. Ordinary medians over all
five rounds. Require >=5% geometric mean gain and no cell>3% slower. One process;
failure closes this compiler choice without served integration or timing retry.

First compare the fresh MSVC and Clang GU paths on all48 layers, three experts,
T1/2/4/8 for576 cases. No model server. Global headroom before/after, fixed copied
weight buffer below256MiB per layer; map source GGUF read-only. Record compiler
versions/flags, source and binary hashes. No context/sampling/quality changes.
