## E223 / R127-coding-prefix-confirm frozen coding matrix arm

longer/stream/new: decode[85.8, 90.3, 92.2, 91.1, 90.5] => ordinary median90.5; prompt513.3, E2E43.464812, stream43.469256, TTFT6.133021s.

short/stream/new: decode[93.3, 92.0, 95.4, 88.8, 95.5] => ordinary median93.3; prompt216.6, E2E81.658357, stream81.680459, TTFT0.789495s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C056 enginecc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.

Minimum physical62495199232 and commit41740632064bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Close the comparison with all fifteen measured values per cell and retain any remaining regression or uncertainty; no more reruns of this pair.
