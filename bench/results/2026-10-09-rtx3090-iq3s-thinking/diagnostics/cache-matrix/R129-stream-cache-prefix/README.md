## E227 / R129-stream-cache-prefix exact-repeat matrix arm

longer/stream/hit: raw decode[87.2, 89.5, 94.6, 89.6, 88.2], ordinary median89.5; prompt81.0, E2E88.433721, stream={'median': 88.45266674925388, 'min': 86.11791490281269, 'max': 93.35629727998435}, TTFT={'median': 0.08535430004121736, 'min': 0.08170679997419938, 'max': 0.09349840000504628}. Fresh/cached counts[(5, 3133), (5, 3129), (5, 3130), (5, 3130), (5, 3129)].

longer/stream/new: raw decode[89.4, 87.5, 89.2, 87.4, 90.9], ordinary median89.2; prompt513.3, E2E43.175595, stream={'median': 43.178962750522906, 'min': 42.76866672913166, 'max': 43.554514557248986}, TTFT={'median': 6.138781199988443, 'min': 6.133494400011841, 'max': 6.146514499967452}. Fresh/cached counts[(3138, 0), (3134, 0), (3135, 0), (3135, 0), (3134, 0)].

short/stream/hit: raw decode[95.2, 93.7, 91.4, 96.7, 93.8], ordinary median93.8; prompt74.1, E2E92.180675, stream={'median': 92.19589149212929, 'min': 90.07214444461314, 'max': 95.4289584800809}, TTFT={'median': 0.10935410001548007, 'min': 0.09227119997376576, 'max': 0.11791570001514629}. Fresh/cached counts[(5, 162), (5, 161), (5, 160), (5, 160), (5, 163)].

short/stream/new: raw decode[89.6, 92.6, 90.3, 91.0, 88.8], ordinary median90.3; prompt218.9, E2E79.613420, stream={'median': 79.62499365068565, 'min': 78.26309969141472, 'max': 81.55194108434496}, TTFT={'median': 0.7926385999890044, 'min': 0.7743619999964722, 'max': 0.8114922000095248}. Fresh/cached counts[(167, 0), (166, 0), (165, 0), (165, 0), (168, 0)].

All24request payloads retain fixed profile/512cap, and each new/hit pair is byte-identical. One excluded warmup and five measured runs per cell. Cache/length gate=True; failures, if any, are retained. Interleaved misses stay separate from the closed pure-miss comparison. Candidate/control config, binary and loaded-library identity checks passed. No completed-answer quality or full goal claim from capped responses.

Minimum physical62458945536 and commit41695301632bytes;16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.

Next: Run the reverse-order candidate R130 and control R131, then pool all four streaming cache arms.
