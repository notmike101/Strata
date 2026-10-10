## E175 / R111-random-native-reverse frozen coding baseline

longer/stream/new: decode[78.1, 84.2, 91.5, 90.9, 89.7] => ordinary median89.7; prompt509.0, E2E43.154368, stream43.157858, TTFT6.182458s.

short/stream/new: decode[93.5, 93.7, 95.2, 94.1, 91.2] => ordinary median93.7; prompt210.4, E2E81.998981, stream82.014900, TTFT0.824625s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C051 engine0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Full matrix and quality remain required.

Minimum physical62384869376 and commit41575317504bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Pool both coding arms and run Q008 complete-answer quality under unchanged profile and corrected 90 short / 85 long thresholds.
