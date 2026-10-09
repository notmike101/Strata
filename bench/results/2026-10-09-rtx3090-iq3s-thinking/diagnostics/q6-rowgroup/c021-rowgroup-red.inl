namespace strata::kernels {
// Deliberately incorrect stub for the first parity test.
void c021_mmvq(int rows, const void* w, const void* x, float* y, int n_in, int n_out, cudaStream_t stream) {
    (void)rows; (void)w; (void)x; (void)n_in;
    cudaMemsetAsync(y, 0xff, sizeof(float)*n_out, stream);
}
}
