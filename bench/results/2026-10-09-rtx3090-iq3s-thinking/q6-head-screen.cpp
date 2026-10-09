// Diagnostic only: the existing packed-head self-test on actual model weights.
#include "strata/core/native_head.hpp"
#include "strata/artifact/gguf_reader.hpp"
#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
int main(int argc, char** argv) {
    if (argc < 2) return 2;
    _putenv_s("STRATA_Q6_PACKED", "1");
    _putenv_s("STRATA_Q6P_SELFTEST", "1");
    std::vector<std::string> shards;
    for (int i=1; i<argc; ++i) shards.emplace_back(argv[i]);
    try {
        strata::GgufModel model(shards);
        const auto* tensor=model.find("output.weight");
        if (!tensor || tensor->shape.size()!=2 || (int)tensor->type!=14) return 3;
        std::printf("head shape %llu x %llu, Q6_K; original model quant unchanged\n",
                    (unsigned long long)tensor->shape[0],(unsigned long long)tensor->shape[1]);
        strata::core::NativeHead head; std::string error;
        if (!head.load(shards,tensor->shape[0],tensor->shape[1],error)) {
            std::fprintf(stderr,"%s\n",error.c_str()); return 4;
        }
        size_t free=0,total=0; cudaMemGetInfo(&free,&total);
        std::printf("diagnostic free/total MiB %zu/%zu\n",free>>20,total>>20);
    } catch (const std::exception& e) { std::fprintf(stderr,"%s\n",e.what()); return 5; }
    cudaDeviceReset();
    return 0;
}
