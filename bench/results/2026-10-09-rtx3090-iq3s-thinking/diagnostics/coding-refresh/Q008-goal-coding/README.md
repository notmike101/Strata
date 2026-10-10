## E178 / Q008 completed-answer quality results

Seed101: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed102: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed103: 6600tokens, finishstop, passed=True; {"passed": true, "compiled": true, "cases": 72, "test_seed": 904001}

Seed104: 8192tokens, finishlength, passed=False; Did not stop naturally

Seed105: 8192tokens, finishlength, passed=False; Did not stop naturally

Quality pass count1/5. Every request exactly matchesQ007, including numeric profile, thinking, seed, task and8192 cap. All actual cache counts are zero. Every passing answer stopped naturally, compiled and passed72 objective tests. All failures retained. These variable-length answers are excluded from512-token target statistics. No quality warmup; inherited manifest warmup wording is corrected in this audit.

Minimum physical62487044096 and commit41671241728bytes; both16GiB floors pass. Supervisor exact cleanup verified and production config3457fdfe restored. Native experimental C051 stack remains unpromoted.

Next: Run identical Q009 quality suite on production control to separate inherent8192-token incompletion from candidate regressions before more tuning.
