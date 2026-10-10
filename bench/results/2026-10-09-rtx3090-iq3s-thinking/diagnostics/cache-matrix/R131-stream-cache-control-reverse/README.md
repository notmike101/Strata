## E229 / R131-stream-cache-control-reverse exact-repeat matrix arm

longer/stream/hit: raw decode[88.5, 92.1, 93.8, 93.2, 90.8], ordinary median92.1; prompt82.1, E2E90.969741, stream={'median': 90.99852216300609, 'min': 87.13704103719526, 'max': 92.47960878823783}, TTFT={'median': 0.0912234999705106, 'min': 0.08401539997430518, 'max': 0.11118389997864142}. Fresh/cached counts[(5, 3133), (5, 3129), (5, 3130), (5, 3130), (5, 3129)].

longer/stream/new: raw decode[88.5, 88.4, 85.9, 84.5, 87.2], ordinary median87.2; prompt509.6, E2E42.419538, stream={'median': 42.42291625603938, 'min': 41.9209090653885, 'max': 42.84573506058342}, TTFT={'median': 6.177239799988456, 'min': 6.1744049999979325, 'max': 6.217188599985093}. Fresh/cached counts[(3138, 0), (3134, 0), (3135, 0), (3135, 0), (3134, 0)].

short/stream/hit: raw decode[91.6, 97.9, 92.9, 89.3, 93.3], ordinary median92.9; prompt77.0, E2E91.494459, stream={'median': 91.50847139677565, 'min': 87.83128282999446, 'max': 96.52527122128036}, TTFT={'median': 0.09809610003139824, 'min': 0.09029540000483394, 'max': 0.11830010003177449}. Fresh/cached counts[(5, 162), (5, 161), (5, 160), (5, 160), (5, 163)].

short/stream/new: raw decode[94.8, 90.6, 88.2, 93.9, 89.4], ordinary median90.6; prompt202.3, E2E79.434069, stream={'median': 79.458719752056, 'min': 77.16507801513428, 'max': 82.18650651282947}, TTFT={'median': 0.841768599988427, 'min': 0.8095237999805249, 'max': 0.8523502000025474}. Fresh/cached counts[(167, 0), (166, 0), (165, 0), (165, 0), (168, 0)].

All24request payloads retain fixed profile/512cap, and each new/hit pair is byte-identical. One excluded warmup and five measured runs per cell. Cache/length gate=True; failures, if any, are retained. Interleaved misses stay separate from the closed pure-miss comparison. Candidate/control config, binary and loaded-library identity checks passed. No completed-answer quality or full goal claim from capped responses.

Minimum physical62460960768 and commit41674158080bytes;16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.

Next: Pool all four streaming cache arms, retain every run, and inspect each target/non-degradation gate before choosing the next experiment.
