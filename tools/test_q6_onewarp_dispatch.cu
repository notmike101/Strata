// CUDA graph inspection proves actual opt-in activation and fallback dispatch.
#include "strata/kernels/native_mmvq.hpp"
#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <vector>

static void check(cudaError_t status) {
    if (status != cudaSuccess) throw std::runtime_error(cudaGetErrorString(status));
}
static int run(bool enabled) {
    const int shapes[][3] = {{2560, 10240, 1}, {2560, 6144, 1}, {2304, 10240, 1},
                             {6144, 2560, 1}, {2560, 10240, 2}};
    int checked = 0;
    for (const auto& shape : shapes) {
        const int ni = shape[0], no = shape[1], nc = shape[2];
        void* w = nullptr; void* x = nullptr; float* y = nullptr;
        check(cudaMalloc(&w, strata::kernels::native_mmvq_weight_bytes(14, ni, no)));
        check(cudaMalloc(&x, strata::kernels::native_q8_1_bytes(ni, nc)));
        check(cudaMalloc(&y, size_t(no) * nc * sizeof(float)));
        cudaStream_t stream; check(cudaStreamCreate(&stream));
        cudaGraph_t graph;
        check(cudaStreamBeginCapture(stream, cudaStreamCaptureModeThreadLocal));
        strata::kernels::native_q6_k_mmvq(w, x, y, ni, no, nc, stream);
        check(cudaStreamEndCapture(stream, &graph));
        size_t count = 0; check(cudaGraphGetNodes(graph, nullptr, &count));
        std::vector<cudaGraphNode_t> nodes(count);
        check(cudaGraphGetNodes(graph, nodes.data(), &count));
        int kernels = 0, selected = 0;
        for (auto node : nodes) {
            cudaGraphNodeType type; check(cudaGraphNodeGetType(node, &type));
            if (type != cudaGraphNodeTypeKernel) continue;
            cudaKernelNodeParams params{}; check(cudaGraphKernelNodeGetParams(node, &params));
            const char* name = nullptr; check(cudaFuncGetName(&name, params.func));
            ++kernels;
            if (std::strstr(name, "native_q6_k_onewarp_kernel")) ++selected;
        }
        const bool want = enabled && ni == 2560 && no == 10240 && nc == 1;
        std::printf("shape=%d/%d columns=%d kernels=%d onewarp=%d expected=%d\n", ni, no, nc, kernels, selected, int(want));
        if (kernels != 1 || selected != int(want)) return 1;
        ++checked;
        check(cudaGraphDestroy(graph)); check(cudaStreamDestroy(stream));
        check(cudaFree(w)); check(cudaFree(x)); check(cudaFree(y));
    }
    std::printf("PASS dispatch checks=%d\n", checked);
    return 0;
}
int main(int argc, char** argv) {
    int status = 2;
    try { status = run(argc > 1 && std::strcmp(argv[1], "on") == 0); }
    catch (const std::exception& error) { std::fprintf(stderr, "%s\n", error.what()); }
    cudaDeviceReset();
    return status;
}
