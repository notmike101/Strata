import hashlib,json,re
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert not (p/'C062-result.txt').exists()
source=(root/'src/kernels/cuda/native_moe.cu').read_text();a=source.index('__global__ void combine_k10_vec4');b=source.index('\nbool valid_span',a)
k=source[a:b].replace('int64_t n4) {','int64_t n4, const float* sg) {').replace('const float4 sh = shared4[c4];','float4 sh = shared4[c4];\n    const float gate = __fdividef(1.f, 1.f + __expf(-sg[tk]));\n    sh.x *= gate; sh.y *= gate; sh.z *= gate; sh.w *= gate;')
wrapper='''
void native_moe_combine_multi_gated(const float* parts,const float* weights,const float* shared,const float* sg,float* output,int64_t n,int64_t k,int t,void* st){
 if(k!=10 || n%4 || !st) throw std::runtime_error("C062 invalid shape");
 combine_k10_vec4<<<dim3((unsigned)((n/4+127)/128),(unsigned)t),128,0,(cudaStream_t)st>>>((const float4*)parts,weights,(const float4*)shared,(float4*)output,n/4,sg);
 auto e=cudaGetLastError();if(e!=cudaSuccess)throw std::runtime_error(cudaGetErrorString(e));
}
'''
candidate=source[:source.index('#include')]+ '#include <cuda_runtime.h>\n#include <cstdint>\n#include <stdexcept>\nnamespace c062 {\n'+k+wrapper+'}\n'
(p/'c062-candidate.cu').write_text(candidate);(p/'c062-red-candidate.cu').write_text(candidate)
h=(p/'c061-screen.cu').read_text().replace('c061','c062').replace('native_moe_combine_multi_hits_gated','native_moe_combine_multi_gated').replace('native_moe_combine_multi_hits','native_moe_combine_multi').replace('T=2;T<=8','T=1;T<=8').replace('dist<5','dist<8')
h=h.replace('#include <cmath>','#include <cmath>\n#include <limits>')
spot='  std::vector<float> canary'
boundary=r'''
  if(dist>=5){
   std::vector<float> ph(parts.n,0.f),wh(w.n,0.f),sh(shared.n,0.f);
   const float edge[]={0.f,-0.f,std::numeric_limits<float>::denorm_min(),-std::numeric_limits<float>::denorm_min(),std::numeric_limits<float>::min(),-std::numeric_limits<float>::min(),1.f,std::nextafter(1.f,2.f)};
   for(int t=0;t<MAX;++t){wh[t*K]=1.f;gates[t]=dist==7?float(t-4)*20.f:0.f;
    for(int i=0;i<N;++i){float v=dist==5?float(i%31-15)*.03125f:edge[(i+seed)%8];ph[(t*K)*N+i]=v;sh[t*N+i]=dist==5?-2.f*v:dist==6?-0.f:v;}
   }
   parts.put(ph);w.put(wh);shared.put(sh);g.put(gates);
  }
'''
h=h.replace(spot,boundary+spot);(p/'c062-screen.cu').write_text(h)
build=(p/'build-c061.cmd').read_text().replace('c061','c062');(p/'build-c062.cmd').write_text(build)
run=(p/'run-c061.py').read_text().replace('C061','C062').replace('c061','c062');(p/'run-c062.py').write_text(run)
(p/'run-c062-red.py').write_text(run.replace('C062','C062-red'))
m={'id':'C062','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'reference':'actual staged native_moe_combine_multi K10 vectorized library plus precise sigmoid-scale','parity_cases':320,'timing_cells':8,'rounds':7,'warmups':1,'calls_per_graph':200,'gate':'All exact/finite/canary cases; geometric candidate/control duration <=0.95 and no slower median cell. Diagnostic only.'}
for name in ['C062','C062-red']:(p/f'{name}-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
note='''## E246 / C062 staged vector-combine screen

Previous goal turn was progress: C059 state fix and C060/C061 evidence were published atcd872326 on the existing branch. Entry revalidated that exact HEAD, clean tracked state and no CodeGraph index. Goal remains active; no new upstream release has been asserted.

C062 tests the actual staged baseline native_moe_combine_multi K10 vector path plus the verbatim precise sigmoid-scale kernel. Candidate copies that vector reduction and folds shared scaling into its epilogue. First build the unrounded product as a negative control; retain its complete failed corpus. Then replace only the four products with explicit rounded multiplies. This is a new staged-path applicability check, not a rerun seeking favorable C061 timing.

Parity matrix: T1..8, five deterministic seeds, eight distributions =320 full-output cases. Ordinary, small, large, saturated-gate, subnormal, exact cancellation, signed-zero/edge and first-normal/saturation cases; graph replay twice, all active bytes equal, finite, inactive canaries unchanged. Only if every case passes, time all eight token widths with one excluded warmup, seven paired alternating measured rounds and200 repetitions/graph; equal input-restoration copies included in both. Predeclared gate: at least5percent geometric duration reduction, no slower median cell. This is not a TPS or end-to-end claim.

If the gate passes, integrate a CUDA-only, default-off scale-only path using the unchanged shared gate GEMV, explicit raw-gate output and new vector combine. Keep existing LFUSE and QFUSE disabled; staged/CPU/PCIe expert contributions remain combined in the original order. T1 may be benchmarked here but integration must verify the single-token caller before enabling it. No model loaded for this screen;16GiB physical/commit guard and exact cleanup. Full contract and C056 failed cache screen unchanged.
'''
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text();assert '## E246 /' not in s;put(f,s+'\n\n'+note)
put(pub/'diagnostics/shared-scale-fusion/C062/plan.md',note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E246',current='C062 testing actual staged vector combine before scale-only integration.');put(f,json.dumps(s,indent=2)+'\n')
print('C062 declared')
