## E220 / R125-coding-control-reverse frozen coding matrix arm

longer/stream/new: decode[81.8, 88.3, 90.3, 90.2, 90.3] => ordinary median90.2; prompt510.1, E2E43.290186, stream43.293500, TTFT6.169642s.

short/stream/new: decode[93.9, 94.2, 91.7, 91.6, 91.1] => ordinary median91.7; prompt209.5, E2E80.206426, stream80.222139, TTFT0.818423s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C056 enginecc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.

Minimum physical62528991232 and commit41746485248bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Pool all four declared arms and verify request bytes, medians, target thresholds and no-degradation gates.
