"""Document an execution-environment bug without rewriting original quality outcomes."""
import json
import re
from pathlib import Path
p=Path(__file__).parent; pub=p.parents[1]/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
result=json.loads((p/'checker-v2-recheck.json').read_text())
assert result['arms']['Q014-coupled-quality']['corrected_passed_count']==5
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
note='''## E200 / checker execution-environment defect: preserve original result, recheck all frozen answers

Q014 generated all five answers to natural stop:7748,14847,16435,7830,12225tokens. Original v1 checker reported4/5. Seed105 correctly raises ValueError for a missing endpoint inside a try with an except TypeError clause. In ordinary Python, the ValueError propagates because it is not a TypeError. The checker omitted the standard TypeError builtin, so evaluating the exception handler instead raised NameError. The task only prohibited imports; it did not prohibit built-in exception classes. This is an execution-environment defect, not evidence of an incorrect topological ordering.

Preserved check-topological.py and all original checks.json, stdout/stderr, answers, requests, cap failures and E1994/5. A regression against the frozen seed105 answer fails v1 with the exact NameError. New check-topological-v2.py differs by one addition to the allowed builtin list: TypeError. The AST restrictions,72 test cases, reference function, random seed904001, natural-stop requirement, timeout, expected exceptions, input immutability checks and score threshold are byte-identical. No imports/eval/open or other capabilities were enabled. Valid-answer regression passes v2; four deliberately incorrect/unsafe answers remain rejected. The same frozen answer passes all72 tests using ordinary Python builtins as a separate diagnostic.

Rechecked every stored answer in Q007-Q014 under v1 and v2, with ordinary-Python parity for naturally completed answers. No inference requests or new seed selection.36answers total; all v1 outcomes reproduced. Only Q014seed105 changes. Counts v1 to v2: Q0073/5 to3/5; Q0081/5 to1/5; Q0091/5 to1/5; Q0104/5 to4/5; Q0115/5 to5/5; Q0123/3 to3/3; Q0133/3 to3/3; Q0144/5 to5/5. All output-cap failures remain failures. Original and corrected records coexist with checker/answer hashes and per-answer stdout/stderr.

Q014's five frozen final functions were reviewed as coherent topological-order implementations and each passes the unchanged72-case objective suite under corrected standard exception semantics. This qualifies only the completed-answer coding gate for C054, not universal quality or the full goal. Numeric thinking sampler, prompts, seeds,512speed requests and approved32768quality allowance unchanged. Future quality runs must use v2 consistently for controls and candidates, retaining the checker hash. This repairs evaluation fidelity; it does not lower the quality standard. Short-prompt slowdown and the missing real-use/speed cells remain open. Exact cleanup passed; no benchmark model resident at this checkpoint.
'''
dest=pub/'diagnostics/coding-refresh/checker-v2'
for name in ['check-topological.py','check-topological-v2.py','check-topological-normal-python-diagnostic.py','test-checker-typeerror.py','recheck-topological-v2.py','checker-typeerror-red.txt','checker-v2-recheck.json']:
    put(dest/name,(p/name).read_text(encoding='utf-8'))
put(pub/'diagnostics/coding-refresh/record-coupled-quality.py',(p/'record-coupled-quality.py').read_text())
put(dest/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    s=f.read_text(encoding='utf-8');assert '## E200 /' not in s;put(f,s+'\n\n'+note)
f=pub/'goal-90-contract.md';s=f.read_text();s+='\n\nChecker execution-environment correction (E200,2026-10-10): use check-topological-v2.py, which exposes the standard TypeError exception omitted by v1. The same72 objective cases, reference, AST restrictions, seed904001 and pass criteria remain unchanged. All36 stored answers were rechecked consistently without generation; only Q014seed105 changes from a checker NameError to a pass. Preserve original v1 outcomes and corrected v2 records side by side. This is not permission to alter test cases, loosen scoring, or erase cap failures. See diagnostics/coding-refresh/checker-v2/README.md.\n';put(f,s)
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint='E200',current='C054 Q014 corrected coding gate5/5; original checker4/5 preserved. Short prompt regression and remaining matrix unqualified.',quality='Q014 v1 4/5; v2 same72tests5/5 after TypeError builtin repair. All36 stored answers rechecked; only Q014seed105 changed. Q0104/5 and older cap failures preserved.');v['quality_checker_revision']='v2: standard TypeError restored, objective cases unchanged';v['c054']['quality']='Q014 5/5 corrected v2; original v1 4/5 preserved';put(f,json.dumps(v,indent=2)+'\n')
print(note)
