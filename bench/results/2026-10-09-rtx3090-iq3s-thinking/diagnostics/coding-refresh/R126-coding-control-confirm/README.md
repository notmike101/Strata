## E222 / R126-coding-control-confirm frozen coding matrix arm

longer/stream/new: decode[88.5, 90.4, 89.1, 90.8, 93.0] => ordinary median90.4; prompt509.1, E2E43.296641, stream43.299925, TTFT6.186290s.

short/stream/new: decode[93.0, 91.3, 90.1, 91.8, 94.3] => ordinary median91.8; prompt204.8, E2E79.816982, stream79.828765, TTFT0.834416s.

All12requests512tokens/cachemiss, one warmup and5measured per workload; every request matches frozen profile. Exact fixture16fafa0ea4cd5f5a7e535c7df090c9344d11e0909a35bfde0b476ecdc4b743e5, C056 enginecc85c6c787beed24c113a3a5c7fe7bb376bd07f04bc48f3e58264dec701b3c91. HC1/accepted1/conditional64/minfresh1025, model/context/KV/vision unchanged. No comparison against historical B011 claimed. Partial reasoning is not a completed coding answer. Q015 completed-answer quality remains separate; full matrix still required.

Minimum physical62438969344 and commit41634820096bytes,16GiB guard passed. Exact cleanup verified, production config restored by supervisor.

Next: Run the single predeclared matching R127 candidate, then close the comparison using all fifteen measured runs per configuration/cell.
