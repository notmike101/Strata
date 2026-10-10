__global__ void sigmoid_scale_rows_vec4_kernel(float4* __restrict__ out4, const float* __restrict__ g, int n4) {
    const int t = blockIdx.y;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n4) {
        const float gt = __fdividef(1.0f, 1.0f + __expf(-__ldg(g + t)));
        float4 v = out4[(size_t) t * n4 + i];
        v.x *= gt;
        v.y *= gt;
        v.z *= gt;
        v.w *= gt;
        out4[(size_t) t * n4 + i] = v;
    }
}
