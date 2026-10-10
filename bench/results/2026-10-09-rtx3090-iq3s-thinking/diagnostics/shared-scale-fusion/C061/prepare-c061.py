import csv,hashlib,json,re
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
raw=(p/'C060-result.txt').read_text();assert 'SUMMARY cases=140 failed=105' in raw
source=(root/'src/kernels/cuda/native_moe.cu').read_text()
assert source.count('const float sh = shared[col] * g;')==1
candidate=source.replace('namespace strata::kernels {','namespace c061 {').replace('const float sh = shared[col] * g;','const float sh = __fmul_rn(shared[col], g);')
(p/'c061-candidate.cu').write_text(candidate)
h=(p/'c060-screen.cu').read_text().replace('#include "c060-scale.inl"','#include "c060-scale.inl"\nnamespace c061 { void native_moe_combine_multi_hits_gated(const float*,const float*,const float*,const float*,float*,int64_t,int64_t,int,void*); }')
h=h.replace('dist<4','dist<5').replace('dist==1?1e-8f:dist==2?1e8f:1.f','dist==1?1e-8f:dist==2?1e8f:dist==4?1e-38f:1.f')
h=h.replace('  native_moe_combine_multi_hits_gated(', '  c061::native_moe_combine_multi_hits_gated(')
h=h.replace(' ck(cudaStreamDestroy(st));std::printf', ' if(!bad) timing(parts,w,shared,scaled,g,out,ref,st);\n ck(cudaStreamDestroy(st));std::printf')
timing=r'''
static float elapsed(cudaGraphExec_t graph,cudaStream_t stream){
 cudaEvent_t a,b;ck(cudaEventCreate(&a));ck(cudaEventCreate(&b));ck(cudaEventRecord(a,stream));ck(cudaGraphLaunch(graph,stream));ck(cudaEventRecord(b,stream));ck(cudaEventSynchronize(b));float ms;ck(cudaEventElapsedTime(&ms,a,b));ck(cudaEventDestroy(a));ck(cudaEventDestroy(b));return ms*1000/200;
}
static void timing(Buf& parts,Buf& w,Buf& shared,Buf& scaled,Buf& g,Buf& out,Buf& ref,cudaStream_t st){
 using namespace strata::kernels;constexpr int N=2560,K=10;
 std::mt19937 rng(61001);std::normal_distribution<float> d(0,1);
 for(Buf* b:{&parts,&w,&shared,&g}){std::vector<float> h(b->n);for(auto& x:h)x=d(rng)*.25f;b->put(h);}
 for(int T=2;T<=8;++T){cudaGraph_t graphs[2];cudaGraphExec_t execs[2];
  for(int variant=0;variant<2;++variant){ck(cudaStreamBeginCapture(st,cudaStreamCaptureModeThreadLocal));
   for(int i=0;i<200;++i){
    // Equal restoration copy in BOTH variants; diagnostic time includes it.
    ck(cudaMemcpyAsync(scaled.p,shared.p,T*N*4,cudaMemcpyDeviceToDevice,st));
    if(variant)c061::native_moe_combine_multi_hits_gated(parts.p,w.p,scaled.p,g.p,out.p,N,K,T,st);
    else{sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,T),128,0,st>>>((float4*)scaled.p,g.p,N/4);native_moe_combine_multi_hits(parts.p,w.p,scaled.p,ref.p,N,K,T,st);}
   }
   ck(cudaStreamEndCapture(st,&graphs[variant]));ck(cudaGraphInstantiate(&execs[variant],graphs[variant],nullptr,nullptr,0));
  }
  for(int round=-1;round<7;++round)for(int order=0;order<2;++order){int v=(round+1+order)%2;float us=elapsed(execs[v],st);std::printf("TIMING T=%d round=%d candidate=%d us=%.9g\n",T,round,v,us);}
  for(int v=0;v<2;++v){ck(cudaGraphExecDestroy(execs[v]));ck(cudaGraphDestroy(graphs[v]));}
 }
}
'''
h=h.replace('int main(){',timing+'\nint main(){');(p/'c061-screen.cu').write_text(h)
build=(p/'build-c060.cmd').read_text();line=next(x for x in build.splitlines() if 'nvcc.exe' in x)
extra='"%CUDA_PATH%\\bin\\nvcc.exe" -arch=sm_86 -O3 --use_fast_math -std=c++20 -Xcompiler /MT -I C:\\Strata\\include -c C:\\Strata\\local-setup\\target-80\\c061-candidate.cu -o C:\\Strata\\local-setup\\target-80\\c061-candidate.obj\nif errorlevel 1 exit /b %errorlevel%\n'
build=build.replace(line,extra+line.replace('c060-screen','c061-screen').replace(' -o ',' C:\\Strata\\local-setup\\target-80\\c061-candidate.obj -o '));(p/'build-c061.cmd').write_text(build)
runner=(p/'run-c060.py').read_text().replace('C060','C061').replace('c060','c061');(p/'run-c061.py').write_text(runner)
manifest={'id':'C061','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(),'candidate_compiler_flags':'CUDA13.3 sm86 O3 use_fast_math; reference scale unit no fast math; current native library baseline','parity_cases':175,'timing':'Only after full parity pass: T2..8,one warmup,sevend paired alternating rounds,200 graph calls; identical D2D restoration included in both','integration_gate':'All bitwise finite canary cases pass; geometric duration ratio <=0.95 and no cell median slower; pass only permits opt-in engine validation'}
(p/'C061-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
note='''## E244 / C060 rejected; C061 explicit rounding hypothesis

C060 current LFUSE combine failed105/140 cases. Every ordinary/small/large distribution failed across all T2..8 and five seeds; saturated-gate cases passed. No nonfinite values or inactive-output canary failures. All rows are retained and no timing was run. The entire existing LFUSE option remains disabled. This does not prove generated answers degrade, but fails the required arithmetic equivalence gate before serving.

The gated branch uses a Clang contraction pragma while this CUDA build uses NVCC, and writes sum += shared * sigmoid in one kernel. Hypothesis: that last operation contracts into FMA whereas the original separate scale kernel stores a rounded product. C061 changes only that product in a PRIVATE copy of native_moe.cu to __fmul_rn, preserving the original fast-math compilation and actual native library reference. No production arithmetic changes yet. This tests the proposed cause rather than assuming the pragma was effective.

C061 reruns all140 cases and adds35 subnormal-input cases (175 total), with graph replay and finite/canary checks. Only if every case is bitwise identical, time T2..8, one excluded warmup and seven alternating paired measured rounds,200 repetitions per graph. Both paths include the SAME input-restoration D2D copy; absolute timing is diagnostic and not a served TPS or launch count estimate. Predeclared integration screen: at least5percent geometric mean duration reduction and no slower cell median. Keep all timing rows. A pass permits opt-in engine integration and additional router-aux parity; it cannot enable the whole LFUSE option, transfer C056 quality, or promote a launcher.

Both C060/C061 use16GiB physical and commit guards at1s and exact child cleanup. No model loaded. Fixed sampler/context/output contract unchanged and goal active. No upstream open LFUSE PR was found by the required bot search; no issue or comment posted.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
d=pub/'diagnostics/shared-scale-fusion/C060';put(d/'result.md',note)
for name in ['C060-result.txt','C060-build.txt','C060-safety.csv','C060-manifest.json','prepare-c060.py','c060-screen.cu','c060-scale.inl','build-c060.cmd','run-c060.py']:
    put(d/name,(p/name).read_text())
put(pub/'diagnostics/shared-scale-fusion/C061/plan.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E244 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E244',current='C060 current LFUSE arithmetic failed105/140; C061 isolated rounded-product correction declared.');put(f,json.dumps(s,indent=2)+'\n')
print('C060 closed; C061 declared')
