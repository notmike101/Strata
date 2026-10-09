// Diagnostic only. Compile the reference and candidate in one translation unit.
#include "src/kernels/cuda/native_mmvq.cu"
#include "c021-rowgroup.inl"
#include "strata/artifact/gguf_reader.hpp"
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>

static void check(cudaError_t e) {
    if(e!=cudaSuccess) throw std::runtime_error(cudaGetErrorString(e));
}
static int run(int argc,char**argv) {
    if(argc<3)return 2;
    std::vector<std::string> shards;
    for(int i=1;i<argc;++i)shards.emplace_back(argv[i]);
    strata::GgufModel model(shards);size_t at=0;
    const auto* tensor=model.find("output.weight",&at);
    if(!tensor||tensor->type!=14||tensor->shape!=std::vector<uint64_t>{2560,248320})throw std::runtime_error("Unexpected actual head identity");
    constexpr int ni=2560,no=248320;
    const size_t bytes=strata::kernels::native_mmvq_weight_bytes(14,ni,no);
    if(bytes!=521472000||!model.in_bounds(*tensor,at))throw std::runtime_error("Head payload mismatch");
    cudaStream_t stream;check(cudaStreamCreate(&stream));
    void*w=nullptr,*q=nullptr;float*x=nullptr,*a=nullptr,*b=nullptr;
    check(cudaMalloc(&w,bytes));check(cudaMalloc(&q,strata::kernels::native_q8_1_bytes(ni,1)));
    check(cudaMalloc(&x,ni*sizeof(float)));check(cudaMalloc(&a,(no+2)*sizeof(float)));check(cudaMalloc(&b,(no+2)*sizeof(float)));
    check(cudaMemcpy(w,model.shard(at).tensor_data(*tensor),bytes,cudaMemcpyHostToDevice));
    std::vector<float> input(ni);std::vector<uint32_t> ref(no+2),got(no+2);
    uint64_t comparisons=0;int cases=0;
    for(int pattern=0;pattern<8;++pattern){
        uint32_t state=uint32_t(987651+pattern*991);
        for(int i=0;i<ni;++i){
            state=state*1664525u+1013904223u;
            float v=float(int32_t((state>>8)&0xffff)-32768)/8192.0f;
            if(pattern==0)v=0;
            if(pattern==1)v=(i&1)?-1.0f:1.0f;
            if(pattern==2)v*=0.0001f;
            if(pattern==3)v*=100.0f;
            input[i]=v;
        }
        check(cudaMemcpyAsync(x,input.data(),ni*sizeof(float),cudaMemcpyHostToDevice,stream));
        strata::kernels::native_quantize_q8_1(x,q,ni,1,stream);
        for(int rows_out:{1,3,4,5,17,2560,no}){
            check(cudaMemsetAsync(a,0xcd,(rows_out+2)*sizeof(float),stream));
            strata::kernels::native_q6_k_mmvq(w,q,a+1,ni,rows_out,1,stream);
            check(cudaMemcpyAsync(ref.data(),a,(rows_out+2)*sizeof(float),cudaMemcpyDeviceToHost,stream));
            check(cudaStreamSynchronize(stream));
            for(int group:{2,4,8}){
                check(cudaMemsetAsync(b,0xcd,(rows_out+2)*sizeof(float),stream));
                strata::kernels::c021_mmvq(group,w,q,b+1,ni,rows_out,stream);
                check(cudaGetLastError());
                check(cudaMemcpyAsync(got.data(),b,(rows_out+2)*sizeof(float),cudaMemcpyDeviceToHost,stream));
                check(cudaStreamSynchronize(stream));
                if(ref[0]!=0xcdcdcdcd||ref[rows_out+1]!=0xcdcdcdcd||got[0]!=0xcdcdcdcd||got[rows_out+1]!=0xcdcdcdcd)throw std::runtime_error("Output guard overwritten");
                for(int i=1;i<=rows_out;++i){
                    float rf,gf;std::memcpy(&rf,&ref[i],4);std::memcpy(&gf,&got[i],4);
                    if(ref[i]!=got[i]||!std::isfinite(rf)||!std::isfinite(gf)){
                        std::printf("FAIL pattern=%d n_out=%d group=%d row=%d ref=%08x got=%08x\n",pattern,rows_out,group,i-1,ref[i],got[i]);return 1;
                    }
                }
                comparisons+=rows_out;++cases;
            }
        }
    }
    std::printf("PARITY PASS cases=%d float_comparisons=%llu original_weight_bytes=%zu\n",cases,(unsigned long long)comparisons,bytes);
    auto launch=[&](int group){
        if(group==1)strata::kernels::native_q6_k_mmvq(w,q,a,ni,no,1,stream);
        else strata::kernels::c021_mmvq(group,w,q,b,ni,no,stream);
    };
    cudaEvent_t begin,end;check(cudaEventCreate(&begin));check(cudaEventCreate(&end));
    for(int group:{1,2,4,8})launch(group);
    check(cudaStreamSynchronize(stream));
    constexpr int repeats=16;
    std::puts("round,order,rows_per_cta,milliseconds_per_head");
    for(int round=0;round<11;++round){
        const int forward[]={1,2,4,8},reverse[]={8,4,2,1};
        for(int order=0;order<4;++order){
            const int group=(round&1)?reverse[order]:forward[order];
            check(cudaEventRecord(begin,stream));
            for(int rep=0;rep<repeats;++rep)launch(group);
            check(cudaEventRecord(end,stream));check(cudaEventSynchronize(end));
            float ms=0;check(cudaEventElapsedTime(&ms,begin,end));
            std::printf("%d,%d,%d,%.9f\n",round,order,group,ms/repeats);
        }
    }
    check(cudaGetLastError());
    check(cudaEventDestroy(begin));check(cudaEventDestroy(end));
    check(cudaFree(w));check(cudaFree(q));check(cudaFree(x));check(cudaFree(a));check(cudaFree(b));check(cudaStreamDestroy(stream));
    return 0;
}
int main(int argc,char**argv){
    int result=0;
    try{result=run(argc,argv);}catch(const std::exception&e){std::fprintf(stderr,"ERROR: %s\n",e.what());result=2;}
    cudaDeviceReset();return result;
}
