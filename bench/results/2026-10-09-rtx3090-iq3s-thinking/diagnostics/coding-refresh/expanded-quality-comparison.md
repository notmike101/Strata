## E187 / approved expanded quality comparison closes

Q010 candidate4/5 versus matched Q011 production5/5 at the user-approved32768 completed-answer allowance. All five request files are byte-identical between arms, and equalQ007 after changing only max_tokens. Profile, seeds, task, checker and72 test cases remain unchanged. Production's successful answers were reviewed as coherent implementations; finite test coverage is not a claim of universal model quality.

| Seed | Candidate tokens | Candidate outcome | Production tokens | Production outcome |
|---|---:|---|---:|---|
|101|15491|natural stop;72tests pass|9087|natural stop;72tests pass|
|102|6210|natural stop;72tests pass|3740|natural stop;72tests pass|
|103|32768|cap reached; no final answer|3417|natural stop;72tests pass|
|104|2254|natural stop;72tests pass|5742|natural stop;72tests pass|
|105|7939|natural stop;72tests pass|7482|natural stop;72tests pass|

Candidate seed103 exhausted32768 while production seed103 finished3417 and passed. Candidate is ineligible for promotion under the fixed all-five condition. This one pair does not identify a causal component or prove a general distributional quality regression. Do not rerun the unchanged candidate until a favorable pass count appears. Preserve all Q007/Q008/Q0098192 failures and Q01032768 failure. No source/runtime/launcher change was promoted. Both exact trees stopped, production config3457fdfe restored, idleGPU457MiB/0percent. Both host16GiB floors passed.

Long-answer throughput is diagnostic only, not the512-token target. Q010 selected coding speed medians from earlier R110/R11193.6/89.35 remain separate. Original-workload R112 control88.7/86.7 is below the short90 target, so full performance qualification also remains incomplete. Q011's5/5 quality applies to production6048736d configuration only; it cannot be transferred to C051 HC/accepted1 stack.

C054 state: integration6/6 checks pass, R112 control completed, R113/R114/R115 were never started after quality took priority. Keep that proposed combination queued; no combined winner exists. Next controlled diagnosis: same C051 executable and HC1, disable accepted-row accounting and its dependent barriers for a complete five-seed32768 quality suite. All quality inputs are148 fresh tokens, below the1025 barrier threshold, so barriers were inactive in Q010; the changed active mechanism is accepted-row accounting. This is a component-isolation test, not a new sampling profile or a retry of the same configuration. Inspect dependency guards before preparing it. After quality is resolved, prioritize the outstanding unchanged nonstream/cache-hit, mixed-history and real-use matrix before additional speed searches.

Changes implementing approval: goal-90-contract.md quality allowance; new goal90-quality-expanded.py (legacy client preserved); private supervisor expanded-client selector and7200s whole-suite timeout with original per-second memory guards; record-expanded-quality.py validates exact request equivalence except approved cap and preserves natural-stop/72-test scoring. Checker check-topological.py unchanged.512-token benchmark client unchanged. The generated final functions are published separately from their reasoning for inspection.
