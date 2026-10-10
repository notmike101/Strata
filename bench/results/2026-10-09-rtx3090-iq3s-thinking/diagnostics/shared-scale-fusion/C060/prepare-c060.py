import hashlib,json,re
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert not (p/'C060-result.txt').exists()
s=(root/'src/kernels/cuda/shared_expert.cu').read_text();a=s.index('__global__ void sigmoid_scale_rows_vec4_kernel');b=s.index('\nvoid launch_sigmoid_scale_rows',a)
(p/'c060-scale.inl').write_text(s[a:b]+'\n')
build=(p/'build-c059-boundary.cmd').read_text().replace('c059-boundary','c060-screen');(p/'build-c060.cmd').write_text(build)
note='''## E243 / C060 exact shared-scale/combine fusion screen

P025 records117.380654ms in33,124 sigmoid_scale_rows_vec4 launches over the instrumented capture; summed durations overlap and do not establish removable critical-path time. The existing LFUSE option proposes folding this scale into MoE combine, plus an auxiliary router gate GEMV and optional paired Q8 GEMV. This screen isolates ONLY scale/combine arithmetic. It does not test or enable the auxiliary router or paired kernels. Shared weights in inspected model layers are not Q8_0, so paired-Q8 fusion is not an assumed win.

Before timing, compare the actual current native_moe_combine_multi_hits_gated library function against the verbatim shared_expert vec4 sigmoid-scale kernel (compiled without fast math, as in production) followed by actual native_moe_combine_multi_hits. Dimensions N2560,K10,T2..8; five deterministic random sets and four magnitude/gate distributions (ordinary, small, large, saturated gates),140 cases. All active outputs must be bitwise identical and finite, inactive canaries intact. Capture both paths in graphs and replay twice. Keep every failed case. No precision tolerance, change to sampler, or served model run. A failed arithmetic gate ends the unchanged LFUSE route before timing; any corrective proposal needs a separate plan.

Only synthetic buffers, no model. Guard physical and commit headroom16GiB before and every second during the exact child,180s timeout, exact cleanup. No qualifying TPS or full-model quality claim. Full goal and C056 failed cache screen remain active/recorded.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
manifest={'id':'C060','reference_scale_source_sha256':hashlib.sha256((root/'src/kernels/cuda/shared_expert.cu').read_bytes()).hexdigest(),'combine_source_sha256':hashlib.sha256((root/'src/kernels/cuda/native_moe.cu').read_bytes()).hexdigest(),'kernel_library_sha256':hashlib.sha256((p/'build-cuda86-main/strata_kernels.lib').read_bytes()).hexdigest(),'cases':140,'sampler_changed':False,'model_loaded':False}
(p/'C060-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
put(pub/'diagnostics/shared-scale-fusion/C060/plan.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E243 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E243',current='C060 exact arithmetic screen of existing shared-scale/combine fusion before any timing.');put(f,json.dumps(s,indent=2)+'\n')
print('C060 declared')
