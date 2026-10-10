## E217 / R122-coding-control frozen coding matrix arm

longer/stream/new: decode[87.8, 90.3, 92.4, 93.0, 92.0] => ordinary median92.0; prompt510.3, E2E43.707821, stream43.711344, TTFT6.172152s.

short/stream/new: decode[92.9, 96.6, 94.1, 90.2, 88.3] => ordinary median92.9; prompt210.1, E2E81.135157, stream81.155707, TTFT0.816787s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C056 enginecc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.

Minimum physical62358753280 and commit41621708800bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Run R123 with only prefix staging enabled, then complete the reverse-order R124/R125 pair.
