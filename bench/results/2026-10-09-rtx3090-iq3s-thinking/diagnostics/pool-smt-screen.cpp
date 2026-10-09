// Windows diagnostic only. Reuse the established synthetic quantized-block fixture.
#define main parity_fixture_main
#include "../../src/kernels/cpu/iq_avx2_parity.cpp"
#undef main
#include "strata/kernels/cpu/pool.hpp"
#include <tlhelp32.h>
#include <set>
#include <stdexcept>

std::set<DWORD> thread_ids() {
    std::set<DWORD> ids;
    HANDLE s = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    if (s == INVALID_HANDLE_VALUE) throw std::runtime_error("thread snapshot");
    THREADENTRY32 t{}; t.dwSize = sizeof(t);
    if (Thread32First(s, &t)) do {
        if (t.th32OwnerProcessID == GetCurrentProcessId()) ids.insert(t.th32ThreadID);
    } while (Thread32Next(s, &t));
    CloseHandle(s); return ids;
}

std::vector<DWORD_PTR> worker_masks() {
    DWORD bytes = 0;
    GetLogicalProcessorInformation(nullptr, &bytes);
    std::vector<SYSTEM_LOGICAL_PROCESSOR_INFORMATION> info(bytes / sizeof(SYSTEM_LOGICAL_PROCESSOR_INFORMATION));
    if (!GetLogicalProcessorInformation(info.data(), &bytes)) throw std::runtime_error("topology");
    std::vector<DWORD_PTR> cores;
    for (const auto& i : info) if (i.Relationship == RelationProcessorCore) cores.push_back(i.ProcessorMask);
    std::sort(cores.begin(), cores.end());
    if (cores.size() != 10) throw std::runtime_error("this fixture requires the inspected ten-core CPU");
    DWORD_PTR host = cores[0] & (~cores[0] + 1);
    if (!SetThreadAffinityMask(GetCurrentThread(), host)) throw std::runtime_error("host pin");
    std::vector<DWORD_PTR> primary, siblings;
    for (size_t i = 1; i < cores.size(); ++i) {
        DWORD_PTR first = cores[i] & (~cores[i] + 1), second = cores[i] ^ first;
        if (!second || (second & (second - 1))) throw std::runtime_error("expected two threads per core");
        primary.push_back(first); siblings.push_back(second);
    }
    primary.insert(primary.end(), siblings.begin(), siblings.end());
    return primary;
}

int main() {
    setvbuf(stdout, nullptr, _IONBF, 0);
    ggml_cpu_init();
    const auto masks = worker_masks();
    std::printf("workers,tasks,gu_type,nt,jobs,repeat,ms_per_layer,parity\n");
    for (int type : {22, 18, 21}) {
        cpu::NativeFmt f; std::string err;
        if (!cpu::native_fmt(type, 20, kH, kFF, f, err)) return 2;
        size_t experts = (256ull << 20) / f.bytes;
        std::vector<uint8_t> blobs(experts * f.bytes);
        uint64_t seed = 0xbe9c0000ull + type;
        for (size_t i = 0; i < experts; ++i) fill_blob(blobs.data() + i*f.bytes, f, seed);
        Acts act(f, 5);
        std::vector<float> output(6 * 2 * kH), reference;
        for (int nt : {1, 2}) for (int count : {1, 3, 6}) {
            std::vector<cpu::ExpertJobMulti> jobs(count);
            for (int i = 0; i < count; ++i) {
                jobs[i].nt = nt;
                jobs[i].blob = blobs.data() + i*f.bytes;
                for (int t = 0; t < nt; ++t) {
                    jobs[i].nact[t] = act.gup[t];
                    jobs[i].out[t] = output.data() + (i*2+t)*kH;
                }
            }
            // ABBA pools, same fixed thirty tasks and same floating-point kernels.
            for (int workers : {9,18,18,9}) {
                auto before = thread_ids();
                cpu::ExpertPool pool(workers, false, true, cpu::PoolAffinity::All, 30);
                auto after = thread_ids();
                int pinned = 0;
                for (DWORD id : after) if (!before.count(id)) {
                    HANDLE t = OpenThread(THREAD_SET_INFORMATION | THREAD_QUERY_INFORMATION, FALSE, id);
                    if (!t || pinned >= workers || !SetThreadAffinityMask(t, masks[pinned])) return 3;
                    GROUP_AFFINITY observed{};
                    if (!GetThreadGroupAffinity(t, &observed) || observed.Mask != masks[pinned]) return 3;
                    CloseHandle(t); ++pinned;
                }
                if (pinned != workers) return 3;
                for (int i = 0; i < count; ++i) jobs[i].blob = blobs.data() + i*f.bytes;
                std::fill(output.begin(), output.end(), 0.f);
                pool.run_split_multi_native(f, jobs.data(), count);
                for (float v : output) if (!std::isfinite(v)) return 4;
                if (reference.empty()) reference = output;
                else if (std::memcmp(reference.data(), output.data(), output.size()*sizeof(float))) return 5;
                for (int repeat = 0; repeat < 5; ++repeat) {
                    auto start = Clock::now();
                    for (int step = 0; step < 200; ++step) {
                        for (int i = 0; i < count; ++i) jobs[i].blob = blobs.data() + ((step*count+i)%experts)*f.bytes;
                        pool.run_split_multi_native(f, jobs.data(), count);
                    }
                    double ms = std::chrono::duration<double,std::milli>(Clock::now()-start).count()/200;
                    std::printf("%d,30,%d,%d,%d,%d,%.6f,pass\n", workers,type,nt,count,repeat,ms);
                }
            }
            reference.clear();
        }
    }
}
