#pragma once
namespace strata::kernels::cpu {
bool c041_msvc_iq256_supported(int ggml_type) noexcept;
void c041_msvc_iq256_gu_rows(int ggml_type, const uint8_t* blob, size_t gu_row, size_t up_off, int n, const void* const* act,
                   int nt, float* const* ff, int r0, int r1);
void c041_msvc_iq256_rows(int ggml_type, const uint8_t* w, size_t row_bytes, int n, const void* const* act, int nt,
                float* const* out, int r0, int r1);
int c041_msvc_iq256_variant() noexcept;
int c041_msvc_iq256_variant_for(int ggml_type) noexcept;
int c041_msvc_iq256_variants() noexcept;
void c041_msvc_iq256_gu_rows_v(int variant, int ggml_type, const uint8_t* blob, size_t gu_row, size_t up_off, int n,
                     const void* const* act, int nt, float* const* ff, int r0, int r1);
void c041_msvc_iq256_rows_v(int variant, int ggml_type, const uint8_t* w, size_t row_bytes, int n, const void* const* act,
                  int nt, float* const* out, int r0, int r1);
void c041_msvc_q8k_quant_avx2(const float* x, void* y, int64_t n);
void c041_msvc_iq4nl256_down_rows(const uint8_t* w, size_t row_bytes, int n, const void* const* hq, int nt,
                        float* const* out, int r0, int r1);
void c041_msvc_iq4nl256_down_rows_v(int variant, const uint8_t* w, size_t row_bytes, int n, const void* const* hq, int nt,
                          float* const* out, int r0, int r1);
}
