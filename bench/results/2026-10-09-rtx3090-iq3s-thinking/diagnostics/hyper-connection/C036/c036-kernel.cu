#include <cuda_runtime.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <random>
#include <string>
#include <vector>
#include "c036-dot.inl"
static void ck(cudaError_t e) { if(e!=cudaSuccess){std::fprintf(stderr,"CUDA ERROR: %s\n",cudaGetErrorString(e));std::exit(3);} }
__device__ __forceinline__ uint4 packed8(const unsigned char* bytes,const unsigned short* fallback,int row,int chunk){
    const int block=row*10+chunk/4,j=(chunk%4)*8;
    const unsigned char* p=bytes+(size_t)block*52;
    const unsigned h=*(const unsigned*)p;
    if(h&0x80000000u)return __ldg((const uint4*)(fallback+(size_t)(h&0x7fffffffu)*32+j));
    const unsigned nib=*(const unsigned*)(p+4+j/2),s0=*(const unsigned*)(p+20+j),s1=*(const unsigned*)(p+24+j);
    unsigned w[4]={};
    #pragma unroll
    for(int k=0;k<8;k++){
        const unsigned sm=((k<4?s0:s1)>>((k%4)*8))&255;
        const unsigned value=((sm&128)<<8)|(((h&255)+((nib>>(k*4))&15))<<7)|(sm&127);
        w[k/2]|=value<<((k%2)*16);
    }
    return make_uint4(w[0],w[1],w[2],w[3]);
}
template<int T,bool PACKED> __global__ __launch_bounds__(256) void project(const unsigned short* weights,const unsigned char* packed,const unsigned short* fallback,const float* x,float* y){
    __shared__ __align__(16) float lo[T][320];
    const int t=threadIdx.x,lane=t&31,warp=t>>5,d0=blockIdx.x*16;
    for(int i=t;i<T*320;i+=256)lo[i/320][i%320]=x[i];
    __syncthreads();
    for(int r=warp;r<64;r+=8){
        const int row=(r/16)*2560+d0+r%16;
        const uint4* w4=(const uint4*)(weights+(size_t)row*320);
        const Bf16x8 a=unpack8(PACKED?packed8(packed,fallback,row,lane):__ldg(w4+lane));
        const Bf16x8 b=unpack8(lane<8?(PACKED?packed8(packed,fallback,row,32+lane):__ldg(w4+32+lane)):make_uint4(0,0,0,0));
        #pragma unroll
        for(int k=0;k<T;k++){
            float acc=dot8u_ptr(a,lo[k]+lane*8);
            if(lane<8)acc+=dot8u_ptr(b,lo[k]+(32+lane)*8);
            #pragma unroll
            for(int o=16;o>0;o>>=1)acc+=__shfl_xor_sync(0xffffffffu,acc,o);
            if(lane==k)y[k*10240+row]=acc;
        }
    }
}
static std::vector<unsigned char> read(const std::string& path){std::ifstream f(path,std::ios::binary|std::ios::ate);if(!f){std::fprintf(stderr,"missing input\n");std::exit(2);}size_t n=f.tellg();f.seekg(0);std::vector<unsigned char> b(n);f.read((char*)b.data(),n);return b;}
template<typename P> static void upload(P** out,const void* data,size_t bytes){ck(cudaMalloc((void**)out,std::max(bytes,(size_t)1)));if(bytes)ck(cudaMemcpy(*out,data,bytes,cudaMemcpyHostToDevice));}
template<int T> void test(int id,const unsigned short* dw,const unsigned char* dp,const unsigned short* df,cudaStream_t s){
    float *dx,*dy;ck(cudaMalloc((void**)&dx,T*320*4));ck(cudaMalloc((void**)&dy,T*10240*4));
    auto launch=[&](int f){if(f)project<T,true><<<160,256,0,s>>>(dw,dp,df,dx,dy);else project<T,false><<<160,256,0,s>>>(dw,dp,df,dx,dy);ck(cudaGetLastError());};
    std::vector<float>x(T*320),out[2];std::mt19937 rng(36101);std::uniform_real_distribution<float> dist(-1,1);
    for(int seed=0;seed<3;seed++){
        for(float&v:x)v=dist(rng);ck(cudaMemcpy(dx,x.data(),x.size()*4,cudaMemcpyHostToDevice));
        for(int f=0;f<2;f++){launch(f);ck(cudaStreamSynchronize(s));out[f].resize(T*10240);ck(cudaMemcpy(out[f].data(),dy,out[f].size()*4,cudaMemcpyDeviceToHost));}
        if(std::memcmp(out[0].data(),out[1].data(),out[0].size()*4)||!std::all_of(out[0].begin(),out[0].end(),[](float v){return std::isfinite(v);})){std::printf("FAIL parity id=%d T=%d seed=%d\n",id,T,seed);std::exit(4);}
        std::printf("PARITY id=%d T=%d seed=%d floats=%zu bitwise_equal finite\n",id,T,seed,out[0].size());
    }
    constexpr int iters=200;cudaGraph_t graph[2];cudaGraphExec_t ex[2];cudaEvent_t e0,e1;ck(cudaEventCreate(&e0));ck(cudaEventCreate(&e1));
    for(int f=0;f<2;f++){ck(cudaStreamBeginCapture(s,cudaStreamCaptureModeGlobal));for(int i=0;i<iters;i++)launch(f);ck(cudaStreamEndCapture(s,&graph[f]));ck(cudaGraphInstantiate(&ex[f],graph[f],nullptr,nullptr,0));ck(cudaGraphUpload(ex[f],s));ck(cudaStreamSynchronize(s));}
    double us[2][7];
    for(int round=-1;round<7;round++)for(int order=0;order<2;order++){
        int f=(round+1+order)%2;ck(cudaEventRecord(e0,s));ck(cudaGraphLaunch(ex[f],s));ck(cudaEventRecord(e1,s));ck(cudaEventSynchronize(e1));float ms;ck(cudaEventElapsedTime(&ms,e0,e1));
        if(round>=0){us[f][round]=ms*1000/iters;std::printf("RAW id=%d T=%d round=%d packed=%d us=%.6f\n",id,T,round,f,us[f][round]);}
    }
    for(int f=0;f<2;f++){std::sort(us[f],us[f]+7);ck(cudaGraphExecDestroy(ex[f]));ck(cudaGraphDestroy(graph[f]));}
    std::printf("MEDIAN id=%d T=%d original_us=%.6f packed_us=%.6f ratio=%.6f\n",id,T,us[0][3],us[1][3],us[1][3]/us[0][3]);
    ck(cudaEventDestroy(e0));ck(cudaEventDestroy(e1));ck(cudaFree(dx));ck(cudaFree(dy));
}
int main(int argc,char**argv){setvbuf(stdout,nullptr,_IONBF,0);if(argc!=2)return 2;cudaStream_t s;ck(cudaStreamCreate(&s));
    for(int id=0;id<3;id++){std::string prefix=std::string(argv[1])+"/"+std::to_string(id);auto w=read(prefix+".bf16"),p=read(prefix+".packed"),f=read(prefix+".fallback");if(w.size()!=6553600||p.size()!=5324800)return 2;
        unsigned short *dw,*df;unsigned char*dp;upload(&dw,w.data(),w.size());upload(&dp,p.data(),p.size());upload(&df,f.data(),f.size());
        test<1>(id,dw,dp,df,s);test<2>(id,dw,dp,df,s);test<3>(id,dw,dp,df,s);test<4>(id,dw,dp,df,s);test<5>(id,dw,dp,df,s);
        ck(cudaFree(dw));ck(cudaFree(dp));ck(cudaFree(df));
    }ck(cudaStreamDestroy(s));std::puts("C036 PASS finite bitwise parity; timing interpretation required");
}
