"""Declare a single geometry alternative and first build the failing parity fixture."""
import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert not (p/'C058-timing.txt').exists()
s=(p/'c057-screen.cu').read_text().replace('c057-kernels.inl','c058-kernels.inl').replace('C057','C058')
s=s.replace('specialized_up<T><<<UPM_BLOCKS,THREADS,0,s>>>','half_columns_up<<<N/8,THREADS,0,s>>>')
s=s.replace('test<4>(id,apply,dw,s);','test<4>(id,apply,dw,s);test<5>(id,apply,dw,s);test<6>(id,apply,dw,s);test<7>(id,apply,dw,s);test<8>(id,apply,dw,s);')
(p/'c058-screen.cu').write_text(s)
s=(p/'c057-kernels.inl').read_text().split('template<int EXACT_T>')[0]
(p/'c058-kernels.inl').write_text(s+'\n__global__ void half_columns_up(GrMulti m) {} // failing parity fixture\n')
s=(p/'build-c057.cmd').read_text().replace('c057','c058').replace(' -O3 ',' -O3 --resource-usage ')
(p/'build-c058.cmd').write_text(s)
note='''## E239 / Checkpoint cost review and C058 half-column up-kernel screen

Current upstream main rechecked via the required bot helper: fb58e0dbc8399662c0e47c76578c6e878b14f6cf remains unchanged. Open pull requests are research candidates, not updates silently applied. No default, launcher or source modification.

Checkpoint architecture review: starts_with permits at most n-1 cached tokens. The existing turn-boundary checkpoint supports changed assistant/thinking headers and must remain. The current tail kind is evicted first when capacity is exceeded, so adding n-1 as_tail can immediately discard the new snapshot; replacing the turn checkpoint would degrade other request histories. checkpoint_at synchronizes then conversation_checkpoint_save allocates/copies the complete running state; P025 records one117669888byte D2H transfer18.084902ms and one same-size H2D18.439356ms. These instrumented transfer durations are not the complete checkpoint wall time. A new synchronous snapshot adds fresh-request work even if repeats save their four-token verifier read. Do not implement that proposal without a separate overlap/retention design and fresh-latency proof; it does not address generation speed itself.

C057 resource audit on CUDA13.3/sm86: original generic up107registers,12288bytes shared, zero stack/spills. Exact-T1/2/3/4 uses74/99/110/120registers, zero spills. No spill fix is warranted. NVIDIA's CUDA best-practices guide explains register/occupancy tradeoffs and explicitly cautions that higher occupancy need not mean better performance: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html . This reference motivates a measured test, not a claimed speedup.

C058 is a NEW geometry hypothesis. The generic original block computes64rows in two passes while keeping two groups of five uint4 weights and epilogue values live. Split it into blocks of32rows (8output columns x4streams), one pass,256threads and320blocks instead of160. Retain runtime T1..8, exact BF16 weights, eight-FMA order, XOR tree, apply/in-place R and gate/mean order. Half the row data live per thread may lower register demand and improve latency hiding; extra blocks and duplicated lo staging may instead lose. This is not another exact-T specialization or a favorable subset of C057. No new quantization, TF32/tensor arithmetic, sampler or output change. QFUSE remains omitted identically in reference and candidate as in the served configuration; no QFUSE claim.

Reuse the three original BF16 tensors and deterministic fixture. First ensure a candidate no-op fails the complete-output parity test. Then run all T1..8, apply0/1, three input sets:144 complete-output/canary comparisons. Timing:48cells, one excluded warmup, seven alternating measured rounds per variant,200calls per CUDA graph. Preserve all raw measurements. Integration gate: every parity/finite/canary check passes, at least5percent geometric-mean duration reduction across all48cells and no individual median slower. No repeat-until-favorable and no selecting winning token widths. Close the broad geometry if the gate fails. A pass permits only full-engine opt-in validation, never automatic promotion or a served-TPS claim. Existing C056 failures remain closed. Only small fixtures are loaded;16GiB memory guard and exact child cleanup apply.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True);f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text();assert '## E239 /' not in s;put(f,s+'\n\n'+note)
put(pub/'diagnostics/hc-half-columns/C058/plan.md',note)
put(pub/'diagnostics/hc-exact-t/C057/C057-resource.txt',(p/'C057-resource.txt').read_text())
put(pub/'diagnostics/hc-exact-t/C057/build-c057-resource.cmd',(p/'build-c057-resource.cmd').read_text())
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E239',current='C058 single-pass half-column up kernel declared; C057 closed and synchronous extra checkpoint design deferred.',next=['Confirm failing fixture; implement only the bounded standalone geometry; run all144parity/48timing cells once.','Retain all failures; integrate only if the declared broad gate passes.']);put(f,json.dumps(s,indent=2)+'\n')
print('C058 declared; test fixture prepared with intentionally empty candidate')
