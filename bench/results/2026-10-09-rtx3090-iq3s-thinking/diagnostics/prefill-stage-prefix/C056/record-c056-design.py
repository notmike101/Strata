import json,re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
note='''## E208 / C056 preserve logical placement, skip only untouched-slot copies

C055's first matched pair is mixed, not a verified winner: short decode91.5control/89.7candidate, prompt205.2/213.2, E2E80.1798/79.4939; longer decode88.7/89.7, prompt495.5/503.7, E2E43.0277/43.5903. All five seeds per cell remain included. No reverse confirmation or completed-answer quality was run for C055; no promotion. Its precise prototype patch, added helper/test, allocation calculation, build log and first-pair comparison are archived. Runtime marker proves the opt-in active. Minimum physical/commit floors and exact cleanup passed for both arms; production3457fdfe restored. No model remains from C055.

C056 changes the prefix-staging algorithm to separate logical expert placement from scratch writes. Compute the original full-stage loan boundary and mask the same experts as the control for prompt computation. Carve scratch only in the smaller prefix-stage tail. At refill, restore residency for every masked expert, but skip H2D refill for slots strictly below the actual scratch boundary: their bytes were never lent or overwritten. Refill slots at or above the scratch boundary normally, synchronize as before, and release only the source pages actually used for refill. Trace refill counts now count physical copies, while lent counts remain logical masks. Fail if the reduced scratch region would exceed the original loan. This retains the original initial CPU/GPU placement; it does not claim universal seeded-text identity under adaptive timing.

Source audit: ExpertCache::fill_slot_queued/blocking writes bytes and increments its fills counter; it does not change expert identity or routing. All scratch carve pointers, GEMM rebind and scratch-region aliases are rebased by relayout. The request's absolute full token count bounds staging; cached prefixes are included. Shared-header API compatibility repaired by retaining the original relayout/bytes_needed/bytes_needed_impl signatures and adding overloads used only by the CUDA path. The separate SYCL source continues to define its original signatures. HIP/SYCL were not built or performance-tested; no review request.

TDD: untouched-slot decision tests failed with missing stage_slot_needs_refill, then compiled and passed after implementation, covering every slot around the actual boundary and default behavior. Original page/range/overflow tests still pass. CUDA13.3sm86 rebuilt successfully. A new same-binary0/1 pair R118/R119 will use the unchanged original fixed workloads, one warmup plus five measured seeds each,512tokens, numeric thinking sampler,262144 context and16GiB physical/commit floors. This is a revised mechanism, not selective repetition of C055. Require all original prompt/decode/E2E/quality gates before any promotion. No launcher change.
'''
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s),encoding='utf-8',newline='\n')
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(); assert '## E208 /' not in s; put(f,s+'\n\n'+note)
d=pub/'diagnostics/prefill-stage-prefix/C056'; put(d/'design.md',note)
for n in ['c056-test-red.txt','c056-test-green.txt','c056-build.txt']:
    put(d/n,(p/n).read_text())
f=pub/'goal-90-state.json'; s=json.loads(f.read_text()); s.update(last_checkpoint='E208',current='C055 mixed screen closed without promotion; C056 preserves original logical expert placement while avoiding untouched-slot reloads.',next=['Run same-binary R118/R119 fixed-contract screen.','Retain all-run statistics and require reverse-order, coding quality and real-use gates for a promising candidate.']); put(f,json.dumps(s,indent=2)+'\n')
print('E208 recorded')
