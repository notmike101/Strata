from pathlib import Path
p=Path(__file__).parent
s=Path('src/kernels/fused_gr_bench.cpp').read_text()
s=s.replace('#include <cmath>', '#include <cmath>\n#include <algorithm>')
start=s.index('                double us[2]')
end=s.index('                if (!same)',start)
s=s[:start]+'''                cudaGraph_t graph[2]; cudaGraphExec_t exec[2];
                auto ck = [](cudaError_t e) { if(e != cudaSuccess) { std::fprintf(stderr,"CUDA ERROR %s\\n",cudaGetErrorString(e)); std::exit(3); } };
                for(int f=0;f<2;++f) {
                    K::fused_gr_set_fast(f);
                    ck(cudaStreamBeginCapture(s,cudaStreamCaptureModeGlobal));
                    for(int i=0;i<iters;++i) K::fused_gr_read_multi(a,T,dxn,s);
                    ck(cudaStreamEndCapture(s,&graph[f]));
                    ck(cudaGraphInstantiate(&exec[f],graph[f],nullptr,nullptr,0));
                    ck(cudaGraphUpload(exec[f],s)); ck(cudaStreamSynchronize(s));
                }
                double samples[2][7];
                for(int round=-1;round<7;++round) for(int order=0;order<2;++order) {
                    const int f=(round+1+order)%2;
                    ck(cudaMemcpy(dR,R.data(),R.size()*4,cudaMemcpyHostToDevice));
                    ck(cudaEventRecord(e0,s)); ck(cudaGraphLaunch(exec[f],s));
                    ck(cudaEventRecord(e1,s)); ck(cudaEventSynchronize(e1));
                    float ms=0; ck(cudaEventElapsedTime(&ms,e0,e1));
                    if(round>=0) { samples[f][round]=1000.0*ms/iters;
                        std::printf("RAW T=%d apply=%d inject=%d round=%d fast=%d us=%.6f\\n",T,apply,inject,round,f,samples[f][round]); }
                }
                for(int f=0;f<2;++f) { std::sort(samples[f],samples[f]+7); ck(cudaGraphExecDestroy(exec[f])); ck(cudaGraphDestroy(graph[f])); }
                std::printf("MEDIAN T=%d apply=%d inject=%d old_us=%.6f fast_us=%.6f ratio=%.6f parity=%s\\n",T,apply,inject,samples[0][3],samples[1][3],samples[1][3]/samples[0][3],same?"bitwise_equal":"DIFFERS");
''' + s[end:]
(p/'c034-hc-graph.cu').write_text(s)
b=(p/'build-c032-integrated.cmd').read_text().replace('c032-integrated-test','c034-hc-graph')
(p/'build-c034-graph.cmd').write_text(b)
(p/'hc-experiment.md').write_text('''# C034: hyper-connection graph screen

P009 attributed 252.274 ms of summed instrumented kernel duration to 20,886
gr_up_multi<1,true> calls (not a critical-path percentage). Existing STRATA_GR_FAST
uses eight lanes per row with the original reduction tree and changes no weights.
CUDA on this RTX3090 defaults off. With HC_SPLIT=2 the norm/down paths stay staged.

The existing eager benchmark passed all 32 parity cells (T1..8, apply/inject on/off),
but its timing reports minima and includes host launch overhead. Preserve it only
as a diagnostic. One graph-replay screen now uses seven alternating-order timing
rounds, one excluded warmup per variant, 200 reads per graph, ordinary medians and
all raw samples. This matches the production graph execution style more closely;
it remains a synthetic kernel diagnostic, never proof of served TPS or quality.

Budget: one graph screen. If dominant T1 cells improve without broad T2..5 losses,
allow one fresh same-binary off/on served pair. Only if both workload medians and
prompt/client rates improve, allow one reversed pair, then fixed full quality
and stability gates. Otherwise close. No new shipping source or launcher change.

NVIDIA graph guidance consulted Oct10 UTC:
https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html
https://developer.nvidia.com/blog/constant-time-launch-for-straight-line-cuda-graphs-and-other-performance-enhancements
These support reducing host launch effects; they do not predict a local speedup.
''')
