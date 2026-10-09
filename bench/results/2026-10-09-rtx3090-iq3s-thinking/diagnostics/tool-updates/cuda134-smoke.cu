#include <cuda_runtime.h>
#include <cstdio>
__global__ void smoke(float* output) { output[threadIdx.x] = float(threadIdx.x * 3 + 1); }
int main() {
    float *device = nullptr, host[128] = {};
    cudaError_t error = cudaMalloc(&device, sizeof(host));
    if (error != cudaSuccess) { std::printf("allocation: %s\n", cudaGetErrorString(error)); return 1; }
    for (int i = 0; i < 32; ++i) smoke<<<1,128>>>(device);
    error = cudaMemcpy(host, device, sizeof(host), cudaMemcpyDeviceToHost);
    cudaFree(device);
    if (error != cudaSuccess) { std::printf("copy: %s\n", cudaGetErrorString(error)); return 2; }
    for (int i = 0; i < 128; ++i) if (host[i] != float(i * 3 + 1)) return 3;
    int runtime = 0, driver = 0;
    cudaRuntimeGetVersion(&runtime); cudaDriverGetVersion(&driver);
    std::printf("PASS: 32 launches, 128 exact values; runtime=%d driver=%d\n", runtime, driver);
    return 0;
}
