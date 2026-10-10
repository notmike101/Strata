## E219 / R124-coding-prefix-reverse frozen coding matrix arm

longer/stream/new: decode[81.8, 88.6, 90.2, 90.5, 90.6] => ordinary median90.2; prompt512.1, E2E43.415884, stream43.419378, TTFT6.151300s.

short/stream/new: decode[93.8, 93.9, 94.1, 92.1, 91.7] => ordinary median93.8; prompt213.7, E2E81.841211, stream81.867415, TTFT0.812772s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C056 enginecc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.

Minimum physical62528376832 and commit41760288768bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Run matching reverse-order control R125, then pool every run in the declared four-arm matrix.
