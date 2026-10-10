## E174 / R110-random-native frozen coding baseline

longer/stream/new: decode[88.2, 90.2, 88.3, 89.0, 90.3] => ordinary median89.0; prompt510.2, E2E42.960721, stream42.965072, TTFT6.180677s.

short/stream/new: decode[92.2, 95.0, 98.1, 90.9, 92.7] => ordinary median92.7; prompt214.0, E2E81.283776, stream81.305735, TTFT0.807274s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C051 engine0dea69dcbf10b0f925549552ec58c76d64c2acf51276187b60adb1a62b90b4dd. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Full matrix and quality remain required.

Minimum physical62218043392 and commit41268506624bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Run R111 in reversed workload order, then Q008 complete-answer quality under unchanged profile.
