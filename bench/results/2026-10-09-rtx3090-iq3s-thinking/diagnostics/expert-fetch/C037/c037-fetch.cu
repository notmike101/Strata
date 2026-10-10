#include <cuda_runtime.h>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <set>
#include <sstream>
#include <string>
#include <vector>
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"CUDA ERROR %s\n",cudaGetErrorString(e));std::exit(3);}}
__global__ void original(const unsigned long long* __restrict__ src,const int* __restrict__ n,uint4* __restrict__ dst,long long per){
    const long long total=(long long)*n*per;
    for(long long i=(long long)blockIdx.x*blockDim.x+threadIdx.x;i<total;i+=(long long)gridDim.x*blockDim.x){
        const long long k=i/per,off=i-k*per;dst[i]=((const uint4*)src[k])[off];
    }
}
__global__ void striped(const unsigned long long* __restrict__ src,const int* __restrict__ n,uint4* __restrict__ dst,long long per){
    const int count=*n;if(count<=0)return;
    const int k=blockIdx.x%count,stripe=blockIdx.x/count;
    const int stripes=(gridDim.x-1-k)/count+1;
    const uint4* from=(const uint4*)src[k];uint4* to=dst+(long long)k*per;
    for(long long off=(long long)stripe*blockDim.x+threadIdx.x;off<per;off+=(long long)stripes*blockDim.x)to[off]=from[off];
}
int main(int argc,char**argv){
    setvbuf(stdout,nullptr,_IONBF,0);if(argc!=2)return 2;
    std::ifstream file(argv[1]);std::set<size_t> sizes;std::string line;
    while(std::getline(file,line)){if(line.empty()||line[0]=='#')continue;std::istringstream s(line);long long layer,gu,down,offset,bytes;s>>layer>>gu>>down>>offset>>bytes;if(!s||bytes<=0||bytes%16)return 2;sizes.insert(bytes);}
    if(sizes.empty())return 2;
    cudaStream_t stream;ck(cudaStreamCreate(&stream));int*dn;unsigned long long*ds;ck(cudaMalloc((void**)&dn,4));ck(cudaMalloc((void**)&ds,64*8));
    for(size_t bytes:sizes){
        const size_t cap=64,stride=bytes+256,total=cap*bytes;
        unsigned char*host;void*mapped;unsigned char*base;ck(cudaHostAlloc((void**)&host,cap*stride,cudaHostAllocMapped));ck(cudaHostGetDevicePointer(&mapped,host,0));ck(cudaMalloc((void**)&base,total+512));
        for(size_t i=0;i<cap*stride;i++)host[i]=(unsigned char)((i*131+(i>>9)*17+(i>>19))&255);
        std::vector<unsigned long long> ptr(cap);std::vector<int> order(cap);
        for(size_t i=0;i<cap;i++){order[i]=(int)((i*17+13)%64);ptr[i]=(unsigned long long)((unsigned char*)mapped+order[i]*stride);}
        ck(cudaMemcpy(ds,ptr.data(),cap*8,cudaMemcpyHostToDevice));uint4*dst=(uint4*)(base+256);
        auto launch=[&](int f){if(f)striped<<<384,256,0,stream>>>(ds,dn,dst,bytes/16);else original<<<384,256,0,stream>>>(ds,dn,dst,bytes/16);ck(cudaGetLastError());};
        std::vector<unsigned char> got(total+512);
        for(int n:{0,1,2,3,4,5,7,8,16,64}){
            ck(cudaMemcpy(dn,&n,4,cudaMemcpyHostToDevice));
            for(int f=0;f<2;f++){
                ck(cudaMemset(base,0xa7,total+512));launch(f);ck(cudaStreamSynchronize(stream));ck(cudaMemcpy(got.data(),base,total+512,cudaMemcpyDeviceToHost));
                bool okay=std::all_of(got.begin(),got.begin()+256,[](unsigned char c){return c==0xa7;})&&std::all_of(got.begin()+256+(size_t)n*bytes,got.end(),[](unsigned char c){return c==0xa7;});
                for(int i=0;i<n;i++)okay=okay&&!std::memcmp(got.data()+256+(size_t)i*bytes,host+(size_t)order[i]*stride,bytes);
                if(!okay){std::printf("FAIL bytes=%zu n=%d candidate=%d\n",bytes,n,f);return 4;}
                std::printf("PARITY bytes=%zu n=%d candidate=%d copied=%zu guards=pass exact=pass\n",bytes,n,f,(size_t)n*bytes);
            }
        }
        for(int n:{0,1,2,4,8}){
            ck(cudaMemcpy(dn,&n,4,cudaMemcpyHostToDevice));constexpr int iters=32;cudaGraph_t graph[2];cudaGraphExec_t exec[2];cudaEvent_t e0,e1;ck(cudaEventCreate(&e0));ck(cudaEventCreate(&e1));
            for(int f=0;f<2;f++){ck(cudaStreamBeginCapture(stream,cudaStreamCaptureModeGlobal));for(int i=0;i<iters;i++)launch(f);ck(cudaStreamEndCapture(stream,&graph[f]));ck(cudaGraphInstantiate(&exec[f],graph[f],nullptr,nullptr,0));ck(cudaGraphUpload(exec[f],stream));ck(cudaStreamSynchronize(stream));}
            double us[2][7];
            for(int round=-1;round<7;round++)for(int order=0;order<2;order++){
                const int f=(round+1+order)%2;ck(cudaEventRecord(e0,stream));ck(cudaGraphLaunch(exec[f],stream));ck(cudaEventRecord(e1,stream));ck(cudaEventSynchronize(e1));float ms;ck(cudaEventElapsedTime(&ms,e0,e1));
                if(round>=0){us[f][round]=1000.0*ms/iters;std::printf("RAW bytes=%zu n=%d round=%d candidate=%d us=%.6f\n",bytes,n,round,f,us[f][round]);}
            }
            for(int f=0;f<2;f++){std::sort(us[f],us[f]+7);ck(cudaGraphExecDestroy(exec[f]));ck(cudaGraphDestroy(graph[f]));}
            std::printf("MEDIAN bytes=%zu n=%d original_us=%.6f candidate_us=%.6f ratio=%.6f\n",bytes,n,us[0][3],us[1][3],us[1][3]/us[0][3]);ck(cudaEventDestroy(e0));ck(cudaEventDestroy(e1));
        }
        ck(cudaFree(base));ck(cudaFreeHost(host));
    }
    ck(cudaFree(dn));ck(cudaFree(ds));ck(cudaStreamDestroy(stream));std::puts("C037 PASS byte parity and guards; timing decision required");
}
