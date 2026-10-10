# P009 retrospective coverage audit

Primary-source refresh, accessed 2026-10-09 local date:
https://forums.developer.nvidia.com/t/nsight-systems-2026-5-1-produced-112-collected-100-warning-despite-complete-coverage-of-32-kernels/384749

The NVIDIA reply attributes that separate probe's warning to forced flushing,
not a demonstrated dropped kernel. This does not prove the Strata trace complete:
the example used Linux and simple launches, whereas P009 uses Windows and graphs.
Correct terminology for P009 is coverage unproven, not known missing kernels
solely from that warning. Keep its instrumented speed diagnostic regardless.

After the model is stopped, inspect the saved SQLite metadata, diagnostics and
CUDA activity/API/graph identifiers. Seek explicit dropped/incomplete records
and, if the trace records enough graph metadata, independently reconcile launches
with expected node activities. Do not equate total producer events with collected
kernel counts: categories and capture boundaries differ. Do not call a matching
aggregate count proof that every kernel or memcpy interval is present.

Official guide: https://docs.nvidia.com/nsight-systems/UserGuide/index.html
Node-level graph tracing adds overhead; graph-level tracing is lighter but does
not expose node costs. Frequent flushing can add overhead. Any future capture
must be isolated from qualifying speed runs and use exact process cleanup.
