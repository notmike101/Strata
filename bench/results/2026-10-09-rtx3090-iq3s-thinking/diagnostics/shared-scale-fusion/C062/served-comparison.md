## E252 / C062 complete served cache screen

R132 control and R133 candidate ran short-first; R134 candidate and R135 control ran longer-first. Same executable and exact C056 stack, only STRATA_SHARED_SCALE_FUSE0/1 differs. All96 requests retained:80 measured,16 warmups,10 measured values per config/cell. Each new/hit request pair is byte-identical. All new prompts have zero reuse, repeats have positive reuse, and every response produced512completion tokens. Capture markers prove the candidate branch was captured; controls have none. Each arm passed the16GiB physical/commit guard and exact cleanup, with production config restored. Fixed sampling,262144context,IQ3_S,vision,MTP4/.70,PCIe.20 unchanged.

These interleaved new/hit results remain separate from the earlier pure-miss matrix. Hit prompt speed concerns only five fresh tokens, not the entire cached prefix. Loading and identity checks precede request timing. Client runs on thisPC through itsLAN address, not a remote client. Ordinary medians use every measured value; no selection or repeat-until-favorable. First requests are separately retained as warmups, not cold qualification.

| Cell | Metric | Control | Candidate | Change |
|---|---|---:|---:|---:|
| longer/stream/hit | server_decode_tps | 92.450000 | 92.900000 | +0.487% |
| longer/stream/hit | prompt_tps | 80.450000 | 80.500000 | +0.062% |
| longer/stream/hit | request_e2e_tps | 91.272401 | 91.636226 | +0.399% |
| longer/stream/hit | stream_total_tps | 91.297189 | 91.653863 | +0.391% |
| longer/stream/hit | ttft_seconds | 0.092212 | 0.089713 | -2.711% |
| longer/stream/hit | request_seconds | 5.609591 | 5.587311 | -0.397% |
| longer/stream/new | server_decode_tps | 86.650000 | 89.150000 | +2.885% |
| longer/stream/new | prompt_tps | 512.500000 | 512.100000 | -0.078% |
| longer/stream/new | request_e2e_tps | 42.499906 | 43.141394 | +1.509% |
| longer/stream/new | stream_total_tps | 42.504203 | 43.144849 | +1.507% |
| longer/stream/new | ttft_seconds | 6.153060 | 6.150697 | -0.038% |
| longer/stream/new | request_seconds | 12.047107 | 11.867954 | -1.487% |
| short/stream/hit | server_decode_tps | 92.250000 | 91.900000 | -0.379% |
| short/stream/hit | prompt_tps | 78.650000 | 75.750000 | -3.687% |
| short/stream/hit | request_e2e_tps | 91.114499 | 90.554829 | -0.614% |
| short/stream/hit | stream_total_tps | 91.146602 | 90.569291 | -0.633% |
| short/stream/hit | ttft_seconds | 0.094009 | 0.099586 | +5.933% |
| short/stream/hit | request_seconds | 5.619304 | 5.654107 | +0.619% |
| short/stream/new | server_decode_tps | 92.900000 | 92.800000 | -0.108% |
| short/stream/new | prompt_tps | 218.000000 | 219.750000 | +0.803% |
| short/stream/new | request_e2e_tps | 81.586202 | 81.363149 | -0.273% |
| short/stream/new | stream_total_tps | 81.600556 | 81.380783 | -0.269% |
| short/stream/new | ttft_seconds | 0.788472 | 0.793254 | +0.607% |
| short/stream/new | request_seconds | 6.275572 | 6.292776 | +0.274% |

Failed declared gates: longer/stream/new: prompt_no_degradation; short/stream/hit: stream_no_degradation; short/stream/hit: decode_no_degradation; short/stream/hit: prompt_no_degradation; short/stream/hit: e2e_no_degradation; short/stream/hit: latency_no_degradation; short/stream/hit: ttft_no_degradation; short/stream/new: stream_no_degradation; short/stream/new: decode_no_degradation; short/stream/new: e2e_no_degradation; short/stream/new: latency_no_degradation; short/stream/new: ttft_no_degradation.

The mechanism fails the declared all-cell non-degradation/target screen. Do not promote or run expanded quality as if it were a winner. Preserve the evidence and assess whether a distinct, profiler-supported correction exists; do not rerun the unchanged arm hoping for favorable medians. The standalone24.32percent operation-duration gain does not establish a served improvement.

Raw per-run values/ranges, MTP accepted/offered tokens, client times and prompt counts remain attached. These observed medians are not a statistical certainty claim. Goal remains active, launcher unchanged and no benchmark model resident.
