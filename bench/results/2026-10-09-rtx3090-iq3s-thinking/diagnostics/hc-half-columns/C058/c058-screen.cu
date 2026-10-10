#include <cuda_runtime.h>
#include "strata/kernels/fused_gr.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <random>
#include <string>
#include <vector>
#include "c058-kernels.inl"
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"CUDA ERROR %s\n",cudaGetErrorString(e));std::exit(3);}}
template<class P> static void alloc(P** p,size_t n){ck(cudaMalloc((void**)p,n));}
static std::vector<unsigned short> weights(const std::string& path){
    std::ifstream f(path,std::ios::binary|std::ios::ate);if(!f || f.tellg()!=6553600)std::exit(2);
    std::vector<unsigned short> v(3276800);f.seekg(0);f.read((char*)v.data(),6553600);if(!f)std::exit(2);return v;
}
template<int T> static void test(int id,int apply,const unsigned short* w,cudaStream_t s){
    constexpr int TM=kFusedGrMaxT,D=N*HC;
    std::vector<float> R(TM*D),lo(TM*LR),wn(D),rs(TM*HC),bo(TM*N),inj(TM*HC);
    float *dr,*dlo,*dwn,*drs,*dbo,*dinj,*dy;
    alloc(&dr,R.size()*4);alloc(&dlo,lo.size()*4);alloc(&dwn,wn.size()*4);alloc(&drs,rs.size()*4);alloc(&dbo,bo.size()*4);alloc(&dinj,inj.size()*4);alloc(&dy,TM*N*4);
    GrMulti m{};m.T=T;
    for(int k=0;k<T;k++){
        auto&a=m.a[k];a.R=dr+k*D;a.R_out=dr+k*D;a.apply=apply;a.w_up=w;a.lo=dlo+k*LR;a.w_norm=dwn;a.rs=drs+k*HC;a.bo_prev=dbo+k*N;a.inj_prev=dinj+k*HC;a.mixed=dy+k*N;
    }
    auto launch=[&](int variant){if(variant)half_columns_up<<<N/8,THREADS,0,s>>>(m);else original_up<<<UPM_BLOCKS,THREADS,0,s>>>(m);ck(cudaGetLastError());};
    std::mt19937 rng(57101);std::uniform_real_distribution<float>d(-1,1);
    for(int seed=0;seed<3;seed++){
        for(auto&v:R)v=d(rng);for(auto&v:lo)v=.2f*d(rng);for(auto&v:wn)v=1+.3f*d(rng);for(auto&v:rs)v=1+.2f*d(rng);for(auto&v:bo)v=.5f*d(rng);for(auto&v:inj)v=d(rng);
        ck(cudaMemcpy(dlo,lo.data(),lo.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(dwn,wn.data(),wn.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(drs,rs.data(),rs.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(dbo,bo.data(),bo.size()*4,cudaMemcpyHostToDevice));ck(cudaMemcpy(dinj,inj.data(),inj.size()*4,cudaMemcpyHostToDevice));
        std::vector<float> output[2];
        for(int variant=0;variant<2;variant++){
            ck(cudaMemcpy(dr,R.data(),R.size()*4,cudaMemcpyHostToDevice));ck(cudaMemset(dy,0,TM*N*4));launch(variant);ck(cudaStreamSynchronize(s));
            output[variant].resize(TM*(D+N));ck(cudaMemcpy(output[variant].data(),dr,TM*D*4,cudaMemcpyDeviceToHost));ck(cudaMemcpy(output[variant].data()+TM*D,dy,TM*N*4,cudaMemcpyDeviceToHost));
            if(std::memcmp(output[variant].data()+T*D,R.data()+T*D,(TM-T)*D*4))std::exit(5);
            for(int i=T*N;i<TM*N;i++)if(output[variant][TM*D+i]!=0)std::exit(5);
        }
        if(std::memcmp(output[0].data(),output[1].data(),output[0].size()*4)||!std::all_of(output[0].begin(),output[0].end(),[](float v){return std::isfinite(v);})){std::printf("FAIL id=%d T=%d apply=%d seed=%d\n",id,T,apply,seed);std::exit(4);}
        std::printf("PARITY id=%d T=%d apply=%d seed=%d floats=%zu bitwise_equal finite canaries_ok\n",id,T,apply,seed,output[0].size());
    }
    constexpr int ITERS=200;cudaGraph_t graph[2];cudaGraphExec_t exec[2];cudaEvent_t e0,e1;ck(cudaEventCreate(&e0));ck(cudaEventCreate(&e1));
    for(int f=0;f<2;f++){ck(cudaStreamBeginCapture(s,cudaStreamCaptureModeGlobal));for(int i=0;i<ITERS;i++)launch(f);ck(cudaStreamEndCapture(s,&graph[f]));ck(cudaGraphInstantiate(&exec[f],graph[f],nullptr,nullptr,0));ck(cudaGraphUpload(exec[f],s));ck(cudaStreamSynchronize(s));}
    double us[2][7];
    for(int round=-1;round<7;round++)for(int order=0;order<2;order++){
        int f=(round+1+order)%2;ck(cudaMemcpyAsync(dr,R.data(),R.size()*4,cudaMemcpyHostToDevice,s));ck(cudaEventRecord(e0,s));ck(cudaGraphLaunch(exec[f],s));ck(cudaEventRecord(e1,s));ck(cudaEventSynchronize(e1));float ms;ck(cudaEventElapsedTime(&ms,e0,e1));
        if(round>=0){us[f][round]=ms*1000/ITERS;std::printf("RAW id=%d T=%d apply=%d round=%d exact=%d us=%.6f\n",id,T,apply,round,f,us[f][round]);}
    }
    for(int f=0;f<2;f++){std::sort(us[f],us[f]+7);ck(cudaGraphExecDestroy(exec[f]));ck(cudaGraphDestroy(graph[f]));}
    std::printf("MEDIAN id=%d T=%d apply=%d original_us=%.6f exact_us=%.6f ratio=%.6f\n",id,T,apply,us[0][3],us[1][3],us[1][3]/us[0][3]);
    ck(cudaEventDestroy(e0));ck(cudaEventDestroy(e1));for(float*x:{dr,dlo,dwn,drs,dbo,dinj,dy})ck(cudaFree(x));
}
int main(int argc,char**argv){setvbuf(stdout,nullptr,_IONBF,0);if(argc!=2)return 2;cudaStream_t s;ck(cudaStreamCreate(&s));
    for(int id=0;id<3;id++){auto w=weights(std::string(argv[1])+"/"+std::to_string(id)+".bf16");unsigned short*dw;alloc(&dw,w.size()*2);ck(cudaMemcpy(dw,w.data(),w.size()*2,cudaMemcpyHostToDevice));
        for(int apply=0;apply<2;apply++){test<1>(id,apply,dw,s);test<2>(id,apply,dw,s);test<3>(id,apply,dw,s);test<4>(id,apply,dw,s);test<5>(id,apply,dw,s);test<6>(id,apply,dw,s);test<7>(id,apply,dw,s);test<8>(id,apply,dw,s);}ck(cudaFree(dw));}
    ck(cudaStreamDestroy(s));std::puts("C058 PASS all finite bitwise/canary checks; timing gate requires all cells");return 0;
}
