from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1]
assert 'SUMMARY cases=320 failed=0' in (p/'C062-result.txt').read_text()
assert 'SUMMARY cases=320 failed=8' in (p/'C062-integration-red-result.txt').read_text()
guard='!defined(STRATA_USE_HIP) && !defined(STRATA_HIP_GFX906)'
f=root/'src/kernels/cuda/native_moe.cu';s=f.read_text();c=(p/'c062-candidate.cu').read_text();a=c.index('__global__ void combine_k10_vec4');b=c.index('\nvoid native_moe_combine_multi_gated',a)
kernel=c[a:b].replace('combine_k10_vec4','combine_k10_vec4_gated')
s=s.replace('\nbool valid_span',f'\n#if {guard}\n// Scale-only fusion keeps the separately rounded shared product.\n'+kernel+'\n#endif\nbool valid_span',1)
api='''
void native_moe_combine_multi_gated(const float* parts, const float* weights, const float* shared,
                                   const float* gate, float* output, int64_t n, int64_t k, int tokens, void* stream) {
    if (!stream || n <= 0 || n > std::numeric_limits<int>::max() || (n & 3) || k != 10 || tokens < 1 || tokens > 8)
        throw std::invalid_argument("scale-only combine requires aligned K10 rows and 1..8 tokens");
    const size_t row = size_t(n) * tokens * sizeof(float), wb = size_t(k) * tokens * sizeof(float);
    if (!valid_span(parts, row * k) || !valid_span(shared, row) || !valid_span(output, row) ||
        !valid_span(weights, wb) || !valid_span(gate, size_t(tokens) * sizeof(float)) ||
        ((uintptr_t(parts) | uintptr_t(shared) | uintptr_t(output)) & 15u) ||
        overlap(output, row, parts, row * k) || overlap(output, row, shared, row) ||
        overlap(output, row, weights, wb) || overlap(output, row, gate, size_t(tokens) * sizeof(float)))
        throw std::invalid_argument("scale-only combine requires disjoint aligned output");
    combine_k10_vec4_gated<<<dim3(unsigned((n / 4 + 127) / 128), unsigned(tokens)), 128, 0,
                             static_cast<cudaStream_t>(stream)>>>(
        reinterpret_cast<const float4*>(parts), weights, reinterpret_cast<const float4*>(shared),
        reinterpret_cast<float4*>(output), n / 4, gate);
    const auto error = cudaGetLastError();
    if (error != cudaSuccess) throw std::runtime_error(cudaGetErrorString(error));
}
'''
idx=s.rfind('\n}');s=s[:idx]+f'\n#if {guard}\n'+api+'#endif\n'+s[idx:];f.write_text(s)
f=root/'include/strata/kernels/native_moe.hpp';s=f.read_text();idx=s.rfind('\n}');s=s[:idx]+f'\n#if {guard}\n'+'''/// CUDA scale-only path: K10 aligned float4 rows, 1..8 tokens. The raw shared gate is
/// applied with a separately rounded multiply before the final reduction add.
/// The original ungated entry points and their kernel arithmetic are unchanged.
void native_moe_combine_multi_gated(const float* parts, const float* weights, const float* shared,
                                   const float* gate, float* output, int64_t n, int64_t k, int tokens, void* stream);
#endif
'''+s[idx:];f.write_text(s)
f=root/'src/kernels/cuda/shared_expert.cu';s=f.read_text();s=s.replace('const bool gate_deferred = (lfuse & 1) != 0, pair = (lfuse & 2) != 0;','const bool gate_deferred = (lfuse & 1) != 0, pair = (lfuse & 2) != 0;\n    const bool scale_deferred = (lfuse & 4) != 0;')
old='        launch_sigmoid_scale_rows(out, g, (int) n_embd, n_tok, cs);';assert s.count(old)==1;s=s.replace(old,'        if (!scale_deferred) launch_sigmoid_scale_rows(out, g, (int) n_embd, n_tok, cs);')
old='        launch_sigmoid_scale_rows(out, g, (int) n_embd, 1, cs);';assert s.count(old)==1;s=s.replace(old,'        if (!scale_deferred) launch_sigmoid_scale_rows(out, g, (int) n_embd, 1, cs);')
# Reject unsupported flag combinations before enqueuing work.
spot='    cudaStream_t cs = (cudaStream_t) stream;';start=s.index('void shared_expert_multi(');idx=s.index(spot,start)
s=s[:idx]+'''    if (scale_deferred && (!native_bf16 || gate_deferred ||
        (n_tok > 1 && std::getenv("STRATA_DEC_BATCH") && std::atoi(std::getenv("STRATA_DEC_BATCH")) == 0)))
        throw std::invalid_argument("shared scale deferral requires native BF16 batched gate calculation");
'''+s[idx:];f.write_text(s)
f=root/'include/strata/kernels/shared_expert.hpp';s=f.read_text().replace('bit 1 gate/up pair','bit 1 gate/up pair; bit 2 compute raw gate, defer scale only');f.write_text(s)
f=root/'src/core/verify.cpp';s=f.read_text();spot='inline bool g_lfuse_gate()';idx=s.index(spot)
s=s[:idx]+f'''// C062: CUDA-only scale deferral for the staged verifier; no router/pair fusion.
inline bool g_shared_scale_fuse() {{
#if {guard}
    static const bool on = [] {{ const char* v = std::getenv("STRATA_SHARED_SCALE_FUSE"); return v && v[0] == '1'; }}();
    return on;
#else
    return false;
#endif
}}
'''+s[idx:]
s=s.replace('    bool sg_gated_[2] = {false, false};','''    auto scale_fuse_on = [&](int n) {
        return g_shared_scale_fuse() && !g_lfuse() && !ar_on() && !batch_rec_ && !remote_opt_ &&
               native_moe_combine_enabled() && dec_batch && n > 1 && n <= 8 && K == 10 && (N & 3) == 0 &&
               shared_expert_native_bf16_enabled();
    };
    bool scale_deferred_[2] = {false, false};
    bool sg_gated_[2] = {false, false};''')
old='(sg_ready ? 1 : 0) | (lfuse_on(n) && g_lfuse_pair() ? 2 : 0));';assert s.count(old)==1;s=s.replace(old,'(sg_ready ? 1 : 0) | (lfuse_on(n) && g_lfuse_pair() ? 2 : 0) | (scale_fuse_on(n) ? 4 : 0));')
s=s.replace('                sg_gated_[grp] = sg_ready;','''                sg_gated_[grp] = sg_ready;
                scale_deferred_[grp] = scale_fuse_on(n);
                if (scale_deferred_[grp]) {
                    static const bool announced = [] {
                        std::fprintf(stderr, "strata verify: shared scale-only fusion captured (CUDA K10 T2..8)\\n");
                        return true;
                    }();
                    (void) announced;
                }''')
spot='        if (sg_gated_[grp]) {';idx=s.index(spot)
s=s[:idx]+f'''#if {guard}
        if (scale_deferred_[grp]) {{
            try {{
                native_moe_combine_multi_gated(parts_out, w_ + tb * K, shared_ + tb * N, sh_g_ + tb,
                                              bo_ + tb * N, N, K, n, cs);
            }} catch (const std::exception& e) {{ err = "verify scale-only combine: " + std::string(e.what()); return false; }}
        }} else
#endif
'''+s[idx:];f.write_text(s)
# Permanent actual-library test: remove the private candidate declaration/call.
h=(p/'c062-integration-red.cu').read_text();h=h.replace('namespace c062 { void native_moe_combine_multi_gated(const float*,const float*,const float*,const float*,float*,int64_t,int64_t,int,void*); }\n','').replace('c062::native_moe_combine_multi_gated','native_moe_combine_multi_gated')
h='// C062 exact scale/combine and actual shared-expert pipeline regression.\n'+h
(root/'tests/shared_scale_fusion.cu').write_text(h)
f=root/'CMakeLists.txt';s=f.read_text();spot='    add_test(NAME qfuse_gdn_test COMMAND qfuse_gdn_test)';assert s.count(spot)==1;s=s.replace(spot,spot+'''
    if(NOT STRATA_HIP_GFX906)
      add_executable(shared_scale_fusion_test tests/shared_scale_fusion.cu)
      target_include_directories(shared_scale_fusion_test PRIVATE ${_strata_gpu_include_directories})
      target_link_libraries(shared_scale_fusion_test PRIVATE strata_kernels ${_strata_gpu_runtime_target})
      add_test(NAME shared_scale_fusion_test COMMAND shared_scale_fusion_test)
    endif()''');f.write_text(s)
build=(p/'build-c059-engine.cmd').read_text().replace('qfuse_gdn_test gdn_parity gr_parity verify_parity','shared_scale_fusion_test qfuse_gdn_test native_multi_parity shared_expert_parity gdn_parity gr_parity verify_parity');(p/'build-c062-engine.cmd').write_text(build)
print('Opt-in staged scale-only path and actual-library regression implemented')
