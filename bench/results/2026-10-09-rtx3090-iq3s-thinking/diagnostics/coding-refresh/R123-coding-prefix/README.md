## E218 / R123-coding-prefix frozen coding matrix arm

longer/stream/new: decode[87.3, 93.8, 92.8, 91.1, 88.4] => ordinary median91.1; prompt514.0, E2E43.609018, stream43.612254, TTFT6.130268s.

short/stream/new: decode[92.3, 91.9, 90.0, 98.2, 87.2] => ordinary median91.9; prompt222.1, E2E81.032552, stream81.049504, TTFT0.777003s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C056 enginecc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.

Minimum physical62447947776 and commit41661689856bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Complete the predeclared reverse-order candidate R124 and control R125; retain all runs in pooled medians.
