"""Reproduce the actual one-token policy and fused GDN quantizer before editing."""
import hashlib,json,re
from pathlib import Path
p=Path(__file__).parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert not (p/'C059-before.txt').exists()
files=[json.loads(x) for x in (p/'C059-upstream-files.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.strip()]
f=next(x for x in files if x['filename']=='tests/qfuse_gdn.cpp')
s='\n'.join(x[1:] for x in f['patch'].splitlines() if x.startswith('+') and not x.startswith('+++'))+'\n'
s=s.replace('#include <vector>','#include <vector>\n#include "c059-policy.inl"')
probe='''
// Exercise the production capture/commit predicates on the actual recurrent
// kernel. This isolates GDN state; full verifier/session validation is separate.
static int commit_probe() {
    using namespace strata::kernels;
    constexpr int HK=16, HV=48, Z=128*HV, C=(2*HK+HV)*128, ST=128*HV*128;
    Buffer state(ST), reference(ST), h(C), gate(HV), beta(HV), z(Z), gamma(128), y(Z), ref(Z), q(Z/32*9), keep(1);
    std::mt19937 rng(59001);
    state.random(rng,.01f); h.random(rng,.03f); gate.random(rng,.02f); beta.random(rng,.02f); z.random(rng,1.f); gamma.random(rng,1.f);
    check(cudaMemcpy(reference.p,state.p,ST*4,cudaMemcpyDeviceToDevice));
    int one=1;check(cudaMemcpy(keep.p,&one,4,cudaMemcpyHostToDevice));
    auto nk=reinterpret_cast<const int32_t*>(keep.p);
    gdn_step_norm_multi(reference.p,h.p,C,gate.p,beta.p,z.p,gamma.p,1e-6f,ref.p,HK,HV,1,nk,nullptr);
    const bool captured=capture_self_commit(1,false,true,true);
    const bool skipped=skip_commit(1,false,true,true);
    gdn_step_norm_multi(state.p,h.p,C,gate.p,beta.p,z.p,gamma.p,1e-6f,y.p,HK,HV,1,captured?nk:nullptr,nullptr,0,q.p);
    if(!skipped) gdn_step_norm_multi(state.p,h.p,C,gate.p,beta.p,z.p,gamma.p,1e-6f,y.p,HK,HV,1,nk,nullptr,1);
    check(cudaDeviceSynchronize());
    const int state_diff=differences(state.p,reference.p,ST*4);
    std::printf("COMMIT qfuse=1 enabled=1 T=1 captured=%d skipped=%d state_bytes_differ=%d\\n",captured,skipped,state_diff);
    return state_diff!=0;
}
'''
s=s.replace('int main() {',probe+'\nint main() {')
s=s.replace('return bad?1:0;','const int commit_bad=commit_probe();\n    return bad||commit_bad?1:0;')
(p/'c059-gdn.cpp').write_text(s)
source=(root/'src/core/verify.cpp').read_text()
capture=re.search(r'const bool self_commit = ([^;]+);',source)[1]
skip=re.search(r'if \((last_t_ == 1 && one_token_self_commit\(\))\)',source)[1]
def translate(s):return s.replace('last_t_','T').replace('batch_rec_','batch').replace('g_qfuse()','qfuse').replace('one_token_self_commit()','enabled')
(p/'c059-policy.inl').write_text('// Extracted from current src/core/verify.cpp before edits.\n'+f'bool capture_self_commit(int T,bool batch,bool enabled,bool qfuse) {{ return {translate(capture)}; }}\n'+f'bool skip_commit(int T,bool batch,bool enabled,bool qfuse) {{ return {translate(skip)}; }}\n')
build=(p/'build-c039-corpus.cmd').read_text().replace('c039-corpus.cu','c059-gdn.cpp').replace('c039-corpus.exe','c059-gdn.exe')
(p/'build-c059.cmd').write_text(build)
manifest={'upstream_test_source':'https://github.com/tntcannon5000/Strata/blob/0a3b624aba82775a8b1949fb905dd178902049c2/tests/qfuse_gdn.cpp','upstream_test_changes':'add actual current-source capture/commit policy probe using GDN kernel; original64quantizer cases retained','verify_source_sha256':hashlib.sha256((root/'src/core/verify.cpp').read_bytes()).hexdigest(),'kernel_library_sha256':hashlib.sha256((p/'build-cuda86-main/strata_kernels.lib').read_bytes()).hexdigest(),'capture_predicate':capture,'commit_skip_predicate':skip}
(p/'C059-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
note='''## E241 / Current QFUSE correctness diagnosis before another optimization

Previous goal turn was progress: P025 and two complete negative HC screens were published at8bac0526. Entry revalidated that HEAD, clean tracked tree, only known unrelated untracked profile/key, no inference/profiler, GPU457MiB/0percent. Goal active.

PR1822 applicability: P025 has7431 copy16_kernel calls summing41.122543ms, no copy16_group_kernel. Current group_gather requires stream_all; short CPU-share prompts use the eight-slot staged walk and do not reach PR1822's in-place grouped branch. Therefore do not apply the patch as a demonstrated short-prompt fix. The ~41ms includes all relevant copy16 work in the instrumented pair and cannot all be assumed removable. Longer prompts/other branches may differ; not tested here.

Source inspection of unused QFUSE identifies a concrete mismatch: record_window sets self_commit only for T1, nonbatch, QFUSEoff and enabled one-token commits; Verifier::commit skips its graph for T1 and enabled one-token commits without checking QFUSE. Thus QFUSEon can leave recurrent/conv state unadvanced. This is present in upstream main and blame352cad8f, not introduced by this campaign. Production and current C056 both have QFUSEoff. Old R008/R014 QFUSE rate results remain recorded but must not be used to qualify correctness/performance of a safe QFUSE implementation.

Required existing-thread search found upstream PR1335 (3d1cb39cbb21ec46aefd34014f8dc71d4d33ffbb) already corroborating this on different hardware and referring to closed PR1209 (0a3b624aba82775a8b1949fb905dd178902049c2). No issue/comment/review posted. PR1209 also reports native-versus-precise Q8_1 rounding differences, directly relevant to the earlier C038 finding; its wide/concurrent decoding is outside this serial contract and will not be imported. References: https://github.com/Niko1221/Strata/pull/1335 and https://github.com/Niko1221/Strata/pull/1209 . External reports are not local proof.

C059 first runs64 upstream GDN fused-versus-separate quantizer cases on the current CUDA13.3 library (T1..8, output begin0/tail, ordinary/large gamma, direct/graph), plus a local actual-kernel state probe driven by predicates extracted verbatim from current verify.cpp. Compare the T1 QFUSEon capture+commit path with the reference accepted state. No source edits before reproduction. Failures are expected evidence, not successful qualification. Only small synthetic state buffers, no model server, original numeric arithmetic and16GiB memory floors. Next fix only a proven cause, preserve QFUSEoff bytes/defaults, test state and quantizer equality before any served comparison. Do not rerun an unchanged rejected QFUSE stack or relax parity.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E241 /' not in s;put(f,s+'\n\n'+note)
put(pub/'diagnostics/qfuse-correctness/C059/plan.md',note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E241',current='C059 reproducing QFUSE one-token state/rounding hazards before any new performance test.',next=['Build/run the current-library C059 fixture; retain failures.','Fix only locally reproduced causes, with default-off unchanged, before testing a corrected fusion stack.']);put(f,json.dumps(s,indent=2)+'\n')
print('C059 declared; current-source predicates and upstream64case fixture prepared')
