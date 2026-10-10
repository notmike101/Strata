#include "strata/kernels/cpu/pool.hpp"
#include <cstdio>
namespace cpu=strata::kernels::cpu;
int main(){for(auto mode:{cpu::HostCore::First,cpu::HostCore::Last,cpu::HostCore::Sibling}){cpu::set_host_core(mode);auto t=cpu::detect_cpu_topology(true,cpu::PoolAffinity::All);std::printf("mode=%d host=%d sibling=%d workers=",int(mode),t.host_core,t.host_sibling);for(auto c:t.worker_cores)std::printf("%d,",c);std::puts("");}return 0;}
