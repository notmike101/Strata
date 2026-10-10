"""Archive integrated exact-kernel checks and the failed disabled control."""
import csv, hashlib, json, re
from pathlib import Path
p = Path(__file__).parent
root = p.parents[1]
out = root / 'bench/results/2026-10-09-rtx3090-iq3s-thinking'
prefix = 'diagnostics/q6-integration/C031-C032/'
def put(name, text):
    f = out / name; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me', '<USER_HOME>', text).replace('<LAN_HOST>', '<LAN_HOST>'), encoding='utf-8', newline='\n')
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
cases = comparisons = 0
logs = list((p / 'C032-integrated').glob('*.txt'))
assert len(logs) == 44
for f in logs:
    match = re.search(r'PARITY PASS cases=(\d+) float_comparisons=(\d+)', f.read_text())
    assert match, f
    c, n = map(int, match.groups()); cases += c; comparisons += n
    put(prefix + 'actual-weight-parity/' + f.name, f.read_text())
assert (cases, comparisons) == (2464, 7219168), (cases, comparisons)
for mode in ['unset', 'default', 'enabled']:
    assert 'PASS dispatch checks=5' in (p / f'C031-review-{mode}.txt').read_text()
for name in ['C031-red.txt', 'C031-engine-build-path-failure.txt', 'C031-green-build.txt',
             'C031-default.txt', 'C031-enabled.txt', 'C031-unset.txt', 'C031-ctest.txt',
             'C031-review-build.txt', 'C031-review-unset.txt', 'C031-review-default.txt',
             'C031-review-enabled.txt', 'C032-build.txt', 'C032-wrapper.txt',
             'build-c031-engine.cmd', 'build-c031-dispatch.cmd', 'build-c031-dispatch-green.cmd',
             'build-c032-integrated.cmd', 'c032-integrated-test.cu', 'c032-reference.inl',
             'c029-original-helpers.inl', 'prepare-c032.py', 'run-c032.ps1', 'q6-onewarp-integration-plan.md']:
    put(prefix + name, (p / name).read_text())
for name in ['src/kernels/cuda/native_mmvq.cu', 'tools/test_q6_onewarp_dispatch.cu']:
    put(prefix + 'source/' + name, (root / name).read_text())
put(prefix + 'build-cache.txt', (p / 'build-cuda86-main/CMakeCache.txt').read_text())
identity = {'engine_sha256': sha(root / 'engine/strata-cuda133-q6-onewarp.exe'),
            'kernel_source_sha256': sha(root / 'src/kernels/cuda/native_mmvq.cu'),
            'compiler': 'CUDA 13.3.73, sm_86, Release', 'actual_weight_cases': cases,
            'finite_bitwise_float_comparisons': comparisons, 'dispatch_cases_per_mode': 5,
            'backend_scope': 'CUDA tested. New code excluded by __HIPCC__. HIP and SYCL builds unavailable; not claimed.',
            'review': 'Independent read-only review found no blocking correctness issue. Added the requested wrong-input/correct-output dispatch case 2304/10240; all three flag modes passed again.',
            'quality_scope': 'Kernel parity and dispatch only, not completed coding-answer or full workload qualification.'}
put(prefix + 'identity.json', json.dumps(identity, indent=2) + '\n')
arm = p / 'R053-q6-disabled'
assert not (arm / 'summary.json').exists()
wrapper = (p / 'R053-wrapper.txt').read_text()
assert 'Cleanup verified: no live Strata launcher, server, engine or vision process.' in wrapper
assert 'Safety headroom stop' in wrapper
for f in arm.iterdir():
    if f.suffix in ['.txt', '.json', '.py', '.csv']:
        put(prefix + 'R053-disabled-stop/' + f.name, f.read_text())
put(prefix + 'R053-disabled-stop/supervisor-output.txt', wrapper)
put(prefix + 'R053-disabled-stop/configuration.json', (p / 'R053-q6-disabled.json').read_text())
s = (out / 'ledger.md').read_text(); assert '## E078 /' not in s
s += '''

## E078 / C031-C032 integrated Q6 opt-in; R053 memory stop

The narrow CUDA-only STRATA_Q6_ONEWARP=1 component is now implemented for
single-column Q6_K projections with input width2560 and output width10240.
Four physical warps own four rows. Each lane retains four virtual partials and
the original ordered combination and warp reduction. Unset, zero and all other
shapes retain the original dispatch. No sampling, precision or model change.

C031 graph inspection failed against the unchanged library before implementation,
then passed against the new library. Independent review found no blocking issue;
its requested additional wrong-input/correct-output shape2304/10240 now passes,
alongside eligible, wrong-output, both-wrong and multicolumn shapes. All five
dispatch cases passed with the flag absent, zero and one. Both existing CUDA
MMVQ parity suites passed (2/2). CUDA13.3.73 Release sm_86 was built; HIP/SYCL
execution is unavailable and is not claimed. The initial nonexistent CMake-path
failure and the corrected build command remain archived.

C032 links the actual integrated native entry against an independent copy of the
original reference. Both flag modes across all22 actual tensors passed2,464 cases
and7,219,168 finite bitwise float comparisons, including odd/full row counts and
eight activation patterns. Output canaries passed. All44 subprocesses exited and
GPU usage returned to451MiB. The first PowerShell runner invocation had a string
interpolation parse error before execution; it was corrected before these checks.
These are kernel-correctness results, not served TPS or coding-answer proof.

R053 attempted the rebuilt binary with the opt-in disabled, preserving the
retained configuration. It produced no completed warmup or measured run. The
independent memory guard stopped it at physical headroom39,973,257,216 bytes and
commit headroom16,785,092,608 bytes, below the16GiB commit floor. All launcher,
server, engine and vision processes were stopped; the production config was
restored byte-for-byte and GPU returned to451MiB. No TPS is assigned to this arm.

Startup cache8409, prefill8192, ring384 and borrowed-cache2315 match R051. The
R053 starting commit headroom was about8.28GB lower than R051; the subsequent
growth remains unexplained. The retained executable is therefore being rerun
under current host conditions before attributing this to the code or enabling
the new dispatch. Safety floors remain unchanged. Production is not promoted.
The small component remains a candidate for stacking, subject to the same
sampling, quality, memory and workload contract. Goal90 remains active.
'''
put('ledger.md', s); (p / 'findings.md').write_text(s, encoding='utf-8')
state = json.loads((out / 'goal-90-state.json').read_text())
state.update(last_checkpoint='E078', current='Integrated Q6 parity and dispatch passed; disabled served control R053 stopped on commit headroom. No TPS or promotion. Retained-binary current-host control R055 is the next comparison.',
             next=['Inspect R055 retained control and cleanup. Resolve R053 memory growth, then run the same rebuilt binary disabled/enabled and interaction matrix.'])
put('goal-90-state.json', json.dumps(state, indent=2) + '\n')
print('E078 recorded', cases, comparisons, identity['engine_sha256'])
