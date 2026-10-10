import json, re
from pathlib import Path
p = Path(__file__).parent
pub = p.parents[1] / 'bench/results/2026-10-09-rtx3090-iq3s-thinking'
dest = pub / 'diagnostics/prefill-stage-prefix/C055'
dest.mkdir(parents=True, exist_ok=True)
note = '''## E205 / C055 temporary KV staging hypothesis and implementation plan

The C054 paired trace localized the short prompt loss to compute; it did not prove a root cause. A separate structural opportunity can reduce prompt work without changing context or sampling. Exact allocation counting at the current model geometry, native pack metadata, pinned-share1, CPU share enabled, INT8 KV and262144 context gives634726144bytes for256-token capacity.192-token capacity gives616738304bytes: only17987840bytes saved. Capacity rounding alone is abandoned as insufficiently promising; no inference arm was run for it.

The same counter with a diagnostic fake session page count limited to192 cells gives358104832bytes at unchanged256-token capacity, saving276621312bytes (263.806MiB). Full one-layer temporary INT8 staging costs276825088bytes (264MiB). At3072-token capacity, full-stage2681003776bytes versus3072-cell-stage2407423744bytes saves273580032bytes. These are allocation counts, not measured TPS or live slot counts. Uniform-max-blob slot estimates in CSV are not actual sized-cache slots. Original fake-session diagnostic sources and raw CSV are retained; no real session metadata or model was modified by the diagnostic.

C055 design: an opt-in STRATA_PREFILL_STAGE_PREFIX=1 bounds only the borrowed temporary staging pool to the absolute full request end, including cached prefix and all checkpoint segments. Keep session max_cells, full host KV, resident window, quant, page table, prompt chunk, model and numeric sampler unchanged. Use the same page-rounding helper in allocation counting and carving; require relayout when the bound changes even if chunk and first borrowed slot do not. Refuse out-of-bound prompt ranges before any device work, using overflow-safe subtraction. Zero retains the prior full allocation. Reject batch/multi-GPU/owned-staging combinations; CUDA is the only intended experimental runtime. The default launchers are unchanged.

Risk: fewer lent slots can change expert placement and CPU/GPU floating-point rounding, so this is not claimed to preserve seeded text bit-for-bit. Require completed-answer quality and all original workload/context/memory gates. Prefix restore, split prompt segments, short-after-long and long-after-short requests require explicit validation. Stage lifetime remains synchronized across compute, expert-copy and KV-copy streams before relayout. Full maximum-context memory sizing at startup stays conservative.

TDD: the standalone bounds test first failed because the new header did not exist. After implementation, MSVC compiled and executed boundary, cached-prefix, exact-end, invalid-page, negative-range and INT64 overflow checks successfully. This is only a host helper test, not GPU correctness proof. Next: build CUDA13.3sm86, compare the new counter with original allocation counts, audit caller bounds, then run a same-binary off/on paired screen with unchanged512-token workloads. If promising, require reverse-order confirmation, corrected-v2 five-answer quality at32768, and remaining real-use gates. No promotion or success claim from an allocation estimate. HIP/SYCL are not built or validated and no review is requested.
'''
def put(f, text):
    text = re.sub(r'C:[/\\]+Users[/\\]+me', '<USER_HOME>', text)
    f.write_text(text, encoding='utf-8', newline='\n')
for name in ['c055-footprint.cpp','c055-footprint.csv','c055-footprint-capacity.cpp','c055-footprint-capacity.csv','c055-footprint.cmd','build-c055-test.cmd']:
    put(dest/name, (p/name).read_text())
put(dest/'design.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E205 /' not in s; put(f,s+'\n\n'+note)
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E205',current='C055 prefix-sized temporary KV staging: allocation feasibility and bounds tests only; no speed claim.',next=['Validate CUDA build and allocation-count parity.','Run same-binary off/on screen under the frozen contract; retain only if all quality and workload gates pass.']); put(f,json.dumps(s,indent=2)+'\n')
print('E205 recorded; model not launched.')
