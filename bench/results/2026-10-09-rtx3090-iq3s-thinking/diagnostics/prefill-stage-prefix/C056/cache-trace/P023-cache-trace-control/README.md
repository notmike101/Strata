## E233 / P023-cache-trace-control trace captured

longer/stream/hit: medians server_prompt_ms=61.4, server_decode_ms=5611.1, window_count=326, verified_rows=573, mean_ms_per_window=17.58960244648318, logical_lent_slots=0, physical_refilled_slots=0, loan_ms=0, refill_ms=0, batched_read_ms=0, window_read_ms=40.7, draft_offered=258, draft_accepted=187.

longer/stream/new: medians server_prompt_ms=6158.0, server_decode_ms=5817.7, window_count=321, verified_rows=581, mean_ms_per_window=18.36475903614458, logical_lent_slots=1371, physical_refilled_slots=1371, loan_ms=0.9, refill_ms=435.1, batched_read_ms=5626.0, window_read_ms=53.8, draft_offered=268, draft_accepted=191.

short/stream/hit: medians server_prompt_ms=62.1, server_decode_ms=5483.6, window_count=317, verified_rows=577, mean_ms_per_window=17.750788643533124, logical_lent_slots=0, physical_refilled_slots=0, loan_ms=0, refill_ms=0, batched_read_ms=0, window_read_ms=41.7, draft_offered=261, draft_accepted=195.

short/stream/new: medians server_prompt_ms=788.3, server_decode_ms=5590.9, window_count=310, verified_rows=570, mean_ms_per_window=18.16516129032258, logical_lent_slots=311, physical_refilled_slots=311, loan_ms=0.1, refill_ms=99.5, batched_read_ms=603.7, window_read_ms=45.9, draft_offered=260, draft_accepted=202.

All24requests retain512tokens and valid new/repeat reuse. Same C056 engine/config plus declared trace switch. Trace timings are diagnostic only, not qualifying repeats. All window positions/widths, prompt pieces, logical loans, physical refills, acceptance and raw timing values retained. Minimum memory bytes{'physical_available': 62456541184, 'commit_available': 41689260032};16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.
