## E228 / R130-stream-cache-prefix-reverse exact-repeat matrix arm

longer/stream/hit: raw decode[88.7, 91.5, 94.5, 92.9, 94.3], ordinary median92.9; prompt83.3, E2E91.766349, stream={'median': 91.7810417686884, 'min': 87.54088539776805, 'max': 93.20812254152963}, TTFT={'median': 0.08404970000265166, 'min': 0.07522339996648952, 'max': 0.09279779996722937}. Fresh/cached counts[(5, 3133), (5, 3129), (5, 3130), (5, 3130), (5, 3129)].

longer/stream/new: raw decode[88.4, 86.3, 91.7, 90.6, 90.0], ordinary median90.0; prompt513.1, E2E43.348303, stream={'median': 43.351469968393516, 'min': 42.50613445717879, 'max': 43.66641506160547}, TTFT={'median': 6.15007820003666, 'min': 6.134955899964552, 'max': 6.163187700032722}. Fresh/cached counts[(3138, 0), (3134, 0), (3135, 0), (3135, 0), (3134, 0)].

short/stream/hit: raw decode[92.1, 89.4, 95.9, 94.6, 91.6], ordinary median92.1; prompt74.7, E2E90.961567, stream={'median': 90.98805277076427, 'min': 88.17507491776358, 'max': 94.58452951020729}, TTFT={'median': 0.10271309997187927, 'min': 0.09139200003119186, 'max': 0.10436890000710264}. Fresh/cached counts[(5, 162), (5, 161), (5, 160), (5, 160), (5, 163)].

short/stream/new: raw decode[93.6, 91.6, 88.9, 92.8, 91.3], ordinary median91.6; prompt221.0, E2E80.698661, stream={'median': 80.72420331527456, 'min': 78.56264003369631, 'max': 82.176665996409}, TTFT={'median': 0.7828591000288725, 'min': 0.7785131999989972, 'max': 0.7955770999542437}. Fresh/cached counts[(167, 0), (166, 0), (165, 0), (165, 0), (168, 0)].

All24request payloads retain fixed profile/512cap, and each new/hit pair is byte-identical. One excluded warmup and five measured runs per cell. Cache/length gate=True; failures, if any, are retained. Interleaved misses stay separate from the closed pure-miss comparison. Candidate/control config, binary and loaded-library identity checks passed. No completed-answer quality or full goal claim from capped responses.

Minimum physical62464278528 and commit41733947392bytes;16GiB floors pass. Exact cleanup and production3457fdfe restoration verified.

Next: Run the final opposite-order control R131, then pool all four arms without omitting any run.
