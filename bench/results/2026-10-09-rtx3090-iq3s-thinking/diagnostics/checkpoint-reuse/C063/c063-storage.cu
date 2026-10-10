#include <cuda_runtime.h>
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
static void ck(cudaError_t e){if(e!=cudaSuccess){std::fprintf(stderr,"%s\n",cudaGetErrorString(e));std::exit(2);}}
int main(){constexpr size_t N=117669888;void* device=nullptr;ck(cudaMalloc(&device,N));std::vector<uint8_t> spare(N,7);int bad=0;
 for(int round=-1;round<7;++round){const uint8_t value=uint8_t(17*(round+2));ck(cudaMemset(device,value,N));ck(cudaDeviceSynchronize());
  for(int order=0;order<2;++order){int reuse=(round+1+order)%2;std::vector<uint8_t> fresh;auto& output=reuse?spare:fresh;
   auto a=std::chrono::steady_clock::now();output.resize(N);ck(cudaMemcpy(output.data(),device,N,cudaMemcpyDeviceToHost));auto b=std::chrono::steady_clock::now();
   bool equal=std::all_of(output.begin(),output.end(),[&](uint8_t b){return b==value;});bad+=!equal;
   std::printf("COPY round=%d reuse=%d bytes=%zu ms=%.9f all_bytes_equal=%d\n",round,reuse,N,std::chrono::duration<double,std::milli>(b-a).count(),equal);
  }
 }
 ck(cudaFree(device));return bad?1:0;
}
