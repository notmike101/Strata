## E226 / R128-stream-cache-control exact-repeat matrix arm

longer/stream/hit: raw decode[89.5, 92.6, 95.9, 88.9, 89.4], ordinary median89.5; prompt80.0, E2E88.409575, stream={'median': 88.42931742744867, 'min': 87.87655705378653, 'max': 94.73467454320857}, TTFT={'median': 0.08671489998232573, 'min': 0.0822442999924533, 'max': 0.10468260000925511}. Fresh/cached counts[(5, 3133), (5, 3129), (5, 3130), (5, 3130), (5, 3129)].

longer/stream/new: raw decode[87.5, 88.7, 90.5, 88.7, 86.4], ordinary median88.7; prompt508.6, E2E42.824077, stream={'median': 42.8275884752707, 'min': 42.32493514044524, 'max': 43.295183934157464}, TTFT={'median': 6.189837299985811, 'min': 6.185852900031023, 'max': 6.204204500012565}. Fresh/cached counts[(3138, 0), (3134, 0), (3135, 0), (3135, 0), (3134, 0)].

short/stream/hit: raw decode[93.3, 95.2, 92.3, 96.3, 89.6], ordinary median93.3; prompt75.0, E2E92.049187, stream={'median': 92.06364453230265, 'min': 88.35794660141389, 'max': 94.51951135587635}, TTFT={'median': 0.09867969999322668, 'min': 0.088171900017187, 'max': 0.12278969999169931}. Fresh/cached counts[(5, 162), (5, 161), (5, 160), (5, 160), (5, 163)].

short/stream/new: raw decode[95.5, 94.1, 91.6, 96.0, 94.0], ordinary median94.1; prompt209.6, E2E81.770777, stream={'median': 81.78676869958795, 'min': 70.45518895870039, 'max': 83.57159398902456}, TTFT={'median': 0.8145867999992333, 'min': 0.8077404000214301, 'max': 1.9273226000368595}. Fresh/cached counts[(167, 0), (166, 0), (165, 0), (165, 0), (168, 0)].

All24request payloads retain fixed profile/512cap, and each new/hit pair is byte-identical. One excluded warmup and five measured runs per cell. Cache/length gate=True; failures, if any, are retained. Interleaved misses stay separate from the closed pure-miss comparison. Candidate/control config, binary and loaded-library identity checks passed. No completed-answer quality or full goal claim from capped responses.

Minimum physical62481850368 and commit41687445504bytes;16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.

Next: Run R129 candidate with the identical new/repeat sequence, then reverse-order R130/R131.
