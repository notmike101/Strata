import json,re
from pathlib import Path
p=Path(__file__).resolve().parent;pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
h=(p/'c062-screen.cu').read_text().replace('namespace c062 { void native_moe_combine_multi_gated(const float*,const float*,const float*,const float*,float*,int64_t,int64_t,int,void*); }\n','').replace('c062::native_moe_combine_multi_gated','native_moe_combine_multi_gated')
a=h.index('int main(){');h=h[:a]+'''int main(){constexpr int N=2560,K=10,MAX=9;cudaStream_t st;ck(cudaStreamCreate(&st));
 Buf parts(MAX*K*N),w(MAX*K),shared(MAX*N),scaled(MAX*N),g(MAX),out(MAX*N),ref(MAX*N);
 timing(parts,w,shared,scaled,g,out,ref,st);ck(cudaStreamDestroy(st));return 0;}
'''
spot=' for(int T=1;T<=8;++T){cudaGraph_t graphs[2];'
assert h.count(spot)==1
h=h.replace(spot,''' ck(cudaMemcpyAsync(scaled.p,shared.p,8*N*4,cudaMemcpyDeviceToDevice,st));
 sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,8),128,0,st>>>((float4*)scaled.p,g.p,N/4);
 ck(cudaStreamSynchronize(st));
'''+spot)
h=h.replace('    // Equal restoration copy in BOTH variants; diagnostic time includes it.\n    ck(cudaMemcpyAsync(scaled.p,shared.p,T*N*4,cudaMemcpyDeviceToDevice,st));\n','')
h=h.replace('if(variant)native_moe_combine_multi_gated(parts.p,w.p,scaled.p,','if(variant)native_moe_combine_multi_gated(parts.p,w.p,shared.p,')
h=h.replace('else{sigmoid_scale_rows_vec4_kernel<<<dim3((N/4+127)/128,T),128,0,st>>>((float4*)scaled.p,g.p,N/4);native_moe_combine_multi','else{native_moe_combine_multi')
(p/'c062-combine-only.cu').write_text(h)
build=(p/'build-c060.cmd').read_text().replace('c060-screen','c062-combine-only');(p/'build-c062-combine-only.cmd').write_text(build)
run=(p/'run-c062.py').read_text().replace('C062','C062-combine-only').replace('c062-screen','c062-combine-only');(p/'run-c062-combine-only.py').write_text(run)
(p/'C062-combine-only-manifest.json').write_text(json.dumps({'id':'C062-combine-only','scope':'Actual built native ungated versus gated combine only; original shared sigmoid-scale prepared outside timing. One warmup,seven alternating rounds,200 graph calls,all T1..8. This diagnoses critical-stream cost, not total model latency or TPS.'},indent=2)+'\n')
note='''## E253 / C062 failed served screen; main-stream cost diagnosis

The full R132-R135 comparison fails12 declared gates. The small short decode differences(-0.108percent new,-0.379percent hit) and other client/prompt regressions remain failures under the fixed contract, not statistical proof of a universal slowdown. Fresh~3K decode rises2.885percent but prompt throughput regresses. No promotion, no expanded-quality campaign and no unchanged served rerun.

One structural hypothesis explains why summing serial kernel durations was insufficient: the original sigmoid-scale executes on the forked shared stream, where expert work may hide it, while the fused combine executes on the main stream after joining. Fusion removes an auxiliary launch but adds arithmetic on the main stream. C062-combine-only times the two actual library combine entry points with equivalent pre-scaled/raw shared inputs; reference scaling is prepared outside timing. Keep all eight widths, one warmup and seven alternating rounds of200 graph calls. No model,16GiB memory guards and exact cleanup. This can identify added combine cost, but cannot establish how much scaling overlapped in the served runs; a timeline would be needed for that claim.

After recording this diagnostic, remove the unqualified C062 engine integration from the working source. Preserve its exact patch, regression source, executable hash, configs and all evidence for reproduction. C059 remains committed. A T1 extension is not automatically justified by a serial microbenchmark; require a critical-path theory before another served trial.
'''
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text();assert '## E253 /' not in s;put(f,s+'\n\n'+note)
put(pub/'diagnostics/shared-scale-fusion/C062/combine-only-plan.md',note)
print('C062 combine-only diagnostic declared')
