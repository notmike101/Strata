## E234 / P024-cache-trace-prefix trace captured

longer/stream/hit: medians server_prompt_ms=60.8, server_decode_ms=5564.5, window_count=306, verified_rows=573, mean_ms_per_window=18.184640522875817, logical_lent_slots=0, physical_refilled_slots=0, loan_ms=0, refill_ms=0, batched_read_ms=0, window_read_ms=40.1, draft_offered=265, draft_accepted=207.

longer/stream/new: medians server_prompt_ms=6108.0, server_decode_ms=5812.4, window_count=329, verified_rows=573, mean_ms_per_window=17.968975903614457, logical_lent_slots=1371, physical_refilled_slots=1232, loan_ms=1.7, refill_ms=391.9, batched_read_ms=5625.7, window_read_ms=50.8, draft_offered=244, draft_accepted=183.

short/stream/hit: medians server_prompt_ms=68.8, server_decode_ms=5461.5, window_count=310, verified_rows=573, mean_ms_per_window=17.61774193548387, logical_lent_slots=0, physical_refilled_slots=0, loan_ms=0, refill_ms=0, batched_read_ms=0, window_read_ms=48.2, draft_offered=262, draft_accepted=202.

short/stream/new: medians server_prompt_ms=741.8, server_decode_ms=5635.3, window_count=329, verified_rows=572, mean_ms_per_window=17.201215805471126, logical_lent_slots=311, physical_refilled_slots=177, loan_ms=0.1, refill_ms=55.7, batched_read_ms=603.0, window_read_ms=44.8, draft_offered=245, draft_accepted=183.

All24requests retain512tokens and valid new/repeat reuse. Same C056 engine/config plus declared trace switch. Trace timings are diagnostic only, not qualifying repeats. All window positions/widths, prompt pieces, logical loans, physical refills, acceptance and raw timing values retained. Minimum memory bytes{'physical_available': 62105198592, 'commit_available': 40944943104};16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.
