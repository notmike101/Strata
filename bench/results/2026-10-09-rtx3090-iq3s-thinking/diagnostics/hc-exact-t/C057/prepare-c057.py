"""Extract the unchanged up kernel and generate a bounded exact-T research variant."""
import hashlib,json,re
from pathlib import Path
p=Path(__file__).parent; root=p.parents[1]; pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert not (p/'C057-timing.txt').exists()
src=(root/'src/kernels/cuda/fused_gr.cu').read_text()
dot=src[src.index('struct Bf16x8'):src.index('__global__ void __launch_bounds__(THREADS) gr_down_kernel')]
xor=src[src.index('__device__ __forceinline__ float xor8'):src.index('__global__ void __launch_bounds__(THREADS) gr_up_fast_kernel(GrMulti m) {')]
start=src.index('__global__ void __launch_bounds__(THREADS) gr_up_fast_kernel(GrMulti m) {')
end=src.index('\n}\n#endif',start)+2
original=src[start:end]
tail='    if (m.a[0].q8_mixed != nullptr) gr_q8_tail(m, d0);   // S26 STRATA_QFUSE, as gr_up_multi_kernel\n'
assert original.count(tail)==1
original=original.replace(tail,'') # both variants: QFUSE is disabled in this frozen production path
specialized='template<int EXACT_T>\n'+original.replace('gr_up_fast_kernel','specialized_up').replace('kFusedGrMaxT','EXACT_T').replace('const int T = m.T;','constexpr int T = EXACT_T;')
header='''// Generated from current fused_gr.cu; only the disabled q8 epilogue is omitted.
using namespace strata::kernels;
constexpr int N=2560,HC=4,LR=320,THREADS=256,UPM_COLS=16,UPM_BLOCKS=N/UPM_COLS;
struct GrMulti { FusedGrArgs a[kFusedGrMaxT]; float* xn; int T; };
__device__ __forceinline__ float sigmoidf_(float x) { return 1.0f / (1.0f + __expf(-x)); }
'''
(p/'c057-kernels.inl').write_text(header+dot+xor+original.replace('gr_up_fast_kernel','original_up')+'\n'+specialized+'\n')
manifest={'source_sha256':hashlib.sha256((root/'src/kernels/cuda/fused_gr.cu').read_bytes()).hexdigest(),'generated_sha256':hashlib.sha256((p/'c057-kernels.inl').read_bytes()).hexdigest(),'input_weights':[{**m,'sha256':hashlib.sha256((p/'C036-private'/f"{m['id']}.bf16").read_bytes()).hexdigest()} for m in json.loads((p/'C036-timing-manifest.json').read_text())],'scope':'complete fast up projection and apply/mix epilogue; q8 epilogue disabled in both as in current served configuration; no norm/down timing'}
(p/'C057-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
note='''## E237 / P025 evidence and C057 exact-T up-projection screen

P025 completed four frozen R129 requests; two warmups excluded from capture, one new/repeat pair captured. Exact C056 identity/libraries verified; all512tokens and valid miss/hit reuse. No production setting or source changed. Profiler/model cleanup and configuration restoration completed. Host decode timers for measured new/hit:331/335windows,19.87/20.07ms per window, GPU-reach wait10.66/10.75ms, CPU work2.87/3.04ms, draft1.35/1.36ms. These are instrumented measurements, not qualifying TPS or an additive dependency critical path.

Trace audit:1,519,023kernel records;2,009graph launches all matched to activity, stable per-graph node multisets, zero invalid kernel intervals, zero unmatched kernel-to-launch records and zero nonzero launch returns. Nsight still warns not all CUDA events might have been collected (software tracing on this GPU); internal consistency does not prove complete collection. Full capture spans15,323.240ms of recorded activity, including prompts and the inter-request gap. Summed gr_up_fast time873.136ms across67,978calls (median11.584us). The Q6family remains large but previously failed kernels are not reopened. Raw Nsight/SQLite remain private. Selected graph/kernel/overlap summaries are retained with their limitations.

C057 is a bounded standalone research screen, not a production modification. Current gr_up_fast_kernel uses runtime T with eight-token shared arrays and loop bounds. Generate an exact-T template for T1..4 by retaining its exact BF16 loads, eight-FMA dot order, XOR reduction, apply and gate/mean epilogue, while specializing array extents and loop bounds. This is a distinct mechanism from the rejected Q6/layout and lossless-HC-compression paths. The original kernel body is extracted directly from current source. Both harness variants omit only the disabled QFUSE epilogue; this screen cannot validate QFUSE, other shapes/backends, norm or down kernels.

Use the three existing source-verified BF16 up tensors: blk.0.hc_attn_up.weight,blk.30.hc_attn_up.weight,output_hc_up.weight. No model/pack mutation or new quantization. Three deterministic input sets for each T1..4 and apply0/1:72 bitwise comparisons of both mixed output and the entire R buffer, with finite-output checks and untouched-token canaries. Then200calls per CUDA graph, one excluded warmup and seven alternating measured rounds per variant in each of24cells. Save every raw value and ordinary medians; never a minimum or peak. Microtimings are not served TPS.

Finite screen: any parity/canary/CUDA error rejects integration. Require at least5percent geometric-mean improvement across24cells, and no individual measured median slower than the original before considering full-engine integration. If the broad specialization loses, preserve and close it; no arbitrary repeated grid or favorable-cell promotion. Any later narrower alternative needs separate evidence and a written rationale. No performance/quality claim until fresh served checks pass. Memory use is only small actual tensor fixtures and activation/output buffers; no inference model resident during build or tests. The goal remains active.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True); f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E237 /' not in s; put(f,s+'\n\n'+note)
put(pub/'diagnostics/hc-exact-t/C057/plan.md',note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E237',current='P025 complete; exact-T HC up-projection standalone parity/performance screen declared.',next=['Compile/run C057 once, retain all72parity and24timing cells.','Integrate only if the stated parity/performance gates pass; all full-goal gates remain.']); put(f,json.dumps(s,indent=2)+'\n')
print('C057 extracted from current source, fixed screen declared')
