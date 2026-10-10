from pathlib import Path
import csv,hashlib,json,re,statistics,subprocess
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking');d=pub/'diagnostics/combinations/C053'
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
arms=['R106-usage-all','R107-usage-barrier','R108-usage-barrier','R109-usage-all'];datasets={a:json.loads((p/a/'runs.json').read_text()) for a in arms}
result={'arms':arms,'results':{},'activation':{},'qualification':False}
metrics=['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']
for label,aa in [('control',[arms[0],arms[3]]),('barrier_only',[arms[1],arms[2]])]:
    rows=sum([datasets[a] for a in aa],[]); result['results'][label]={}
    for w in ['short','longer']:
        rr=[r for r in rows if r['workload']==w and not r['warmup']];assert len(rr)==10
        result['results'][label][w]={k:{'raw':[r[k] for r in rr],'median':statistics.median(r[k] for r in rr),'min':min(r[k] for r in rr),'max':max(r[k] for r in rr)} for k in metrics}
result['deltas_percent']={w:{k:100*(result['results']['barrier_only'][w][k]['median']/result['results']['control'][w][k]['median']-1) for k in metrics} for w in ['short','longer']}
files=list((p/arms[0]).glob('*.request.json'));assert len(files)==12
samples=[]
for a in arms:
    assert all(f.read_bytes()==(p/a/f.name).read_bytes() for f in files)
    assert len(datasets[a])==12 and all(r['completion_tokens']==512 and r['cached_tokens']==0 for r in datasets[a])
    assert 'Cleanup verified: no live Strata' in (p/(a[:4]+'-wrapper.txt')).read_text()
    log=(p/a/'engine-session.txt').read_text()
    policies=[tuple(map(int,m)) for m in re.findall(r'accepted usage policy: (\d+) fresh prompt tokens, active (\d+), barrier_only (\d+)',log)]
    assert len(policies)==12
    only=1 if 'barrier' in a else 0
    assert all(flag==only and active==int(not only or n>=1025) for n,active,flag in policies)
    barriers=[int(n) for n in re.findall(r'serial cache barriers: (\d+) updates',log)]
    assert barriers==[7]*6
    result['activation'][a]={'request_policies':policies,'barrier_updates':barriers}
    samples+=list(csv.DictReader((p/a/'safety.csv').open()))
result['memory_minimum_bytes']={k:min(int(r[k]) for r in samples) for k in ['physical_available','commit_available']}
assert min(result['memory_minimum_bytes'].values())>=16*2**30
result['decision']='Rejected and source archived/reverted; lower pooled decode and E2E in both workloads. No extra repeats or promotion.'
put(d/'summary.json',json.dumps(result,indent=2)+'\n')
helper=['node','<USER_HOME>/github-agent/identity.mjs','--repo','notmike101/Strata','git']
source=['include/strata/core/accepted_usage.hpp','src/program/generate.cpp','tests/core/accepted_usage.cpp','tools/test_accepted_usage_modes.py']
patch=subprocess.run(helper+['diff','--',*source],capture_output=True,check=True).stdout.decode()
assert 'enabled_for_request' in patch and 'BARRIER_ONLY' in patch
put(d/'C053-rejected.patch',patch)
for f in source:
    if f!='src/program/generate.cpp':put(d/'sources'/f,Path(f).read_text())
for name in ['C053-test-red.txt','C053-cli-red.txt','C053-cli-green.txt','C053-engine-build.txt','build-c053-tests.cmd','record-c053.py']:
    put(d/name,(p/name).read_text(encoding='utf-8'))
table=[]
for w in ['short','longer']:
    for k in metrics:
        a=result['results']['control'][w][k]['median'];b=result['results']['barrier_only'][w][k]['median'];delta=result['deltas_percent'][w][k]
        table.append(f'| {w} {k} |{a:.6f}|{b:.6f}|{delta:+.3f}%|')
note='''## E172 / C053 closed and rejected; goal-threshold correction

Four-arm ABBA completed: R106A89.9/84.8, R107B88.8/86.9,
R108B88.8/86.0, R109A90.2/90.0 short/~3K decode medians. All48requests
were512tokens/cachemiss, exact twelve payloads equal across all four processes.
Warmups excluded, all ten measured rows per workload/configuration retained.
Same a5f34477 engine; only STRATA_ACCEPTED_USAGE_BARRIER_ONLY0/1 differs.

| Ordinary all-ten-run median | All-request accounting | Barrier-only accounting | Change |
|---|---:|---:|---:|
'''+ '\n'.join(table)+f'''

The candidate fails no-degradation: pooled decode and E2E are lower in both
workloads. Short88.8 misses90; longer86.05 misses90. Reject, archive patch/tests/
build evidence, and restore the four changed source files to49db7853. C051's
split/accounting incompatibility guard remains. Production launcher/config/engine
remain unchanged. No extra repetitions or threshold sweep. The C053 a5f34477
binary remains a diagnostic artifact; build-cuda86-main contains its objects until
a future rebuild. Do not silently call it current clean-source code after restore.

Runtime proof: all24control requests used accepted accounting; both candidate
processes logged active0 on all12short requests and active1 on all12longer
requests. Every longer request logged seven64-token barrier updates. Therefore
the failed result is not an inactive-setting/fallback explanation. Longer results
can change despite identical longer policy because prior short requests change
cache history. Output/draft behavior also varies; no isolated kernel gain inferred.

Safety: minimum available physical{result['memory_minimum_bytes']['physical_available']}
and commit{result['memory_minimum_bytes']['commit_available']}bytes;16GiB floor passed
through all48requests. Exact launcher/server/engine/vision cleanup passed each arm,
config3457fdfe restored, GPU457MiB idle. No benchmark model resident.

THRESHOLD CORRECTION: goal-90-contract.md established90tok/s in BOTH short and~3K
qualifying speed cells. Several later progress/ledger summaries, including recent
90/85 wording, accidentally repeated the earlier pre-goal85longer target. They do
not amend the fixed goal contract. Keep historical numbers; interpret completion
against90/90 and every quality, stability, memory and workload gate. This correction
restores the existing contract, not a new threshold or a relaxation. The saved
contract file itself is unchanged. Current summaries will explicitly say90/90.

The C053 control's90.05/86.65screen medians therefore do NOT meet the goal. The
short margin is only0.05tok/s, long is below90, and frozen random coding/full quality
remain unqualified. C052's90.5/84.5 control was also unqualified. No speed or quality
promotion follows from any of these control observations.

Next: stop selecting from the TTLCache screen alone. Measure the retained native
HC1/acceptedusage1/conditional64/minfresh1025 stack on the already-frozen random
medium coding fixture with unchanged512token speed and8192token separate quality
checks. Use the clean-source C051 engine0dea69dc, same numeric thinking profile,
context/vision, independent memory guards and exact cleanup. That is a NEW measured
baseline on that fixture, not a reuse of a5f34477's90.05result. Preserve Q007's two
incomplete answers as failures; establish whether they persist on this stack before
another sampled-drafting combination. Goal remains active; no blocker declared.
'''
put(d/'README.md',note)
for f in [p/'findings.md',pub/'ledger.md']:
    old=f.read_text(encoding='utf-8');assert '## E172 /' not in old;put(f,old+'\n\n'+note)
f=p/'export-ledger.py';v=f.read_text(encoding='utf-8');idx=v.index('        public_identity["engine_build"] = builds.get(')
sha='a5f344775873de8f9d1567dc153beb2736a1ce526571aca7eaff1d285dc1e4c8';assert sha not in v
entry=f"        builds['{sha}'] = {{'kind':'C053 rejected barrier-only accounting experiment (control option0 and candidate option1)','source_commit':'49db7853','dirty_source':True,'source_patch':'diagnostics/combinations/C053/C053-rejected.patch','cuda':'13.3.73','sm':'86','msvc':'19.44.35228.0'}}\n";f.write_text(v[:idx]+entry+v[idx:],encoding='utf-8')
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint='E172',target_short_tps=90,target_longer_tps=90,current='C052 and C053 rejected. Goal contract is90/90; recent90/85 summaries corrected. Source restored toC051 after archiving C053.',next=['Frozen random-coding baseline and separate completion quality on clean-source C051 HC1/accepted1/conditional64 stack.'],resume_command='Read E172 and goal-90-contract.md. No model resident. C053 four-file source changes archived as diagnostics/combinations/C053/C053-rejected.patch and restored. Clean engine0dea69dc at engine/strata-cuda133-usage-guard.exe; C053 a5f34477 binary/build objects are diagnostic only. Inspect goal90-benchmark.py and Q007 quality helper before next fixed-fixture run. Production unchanged.',safety='C053 all48requests passed16GiB physical/commit floors and exact process cleanup. Config3457fdfe restored; idleGPU457MiB.');put(f,json.dumps(v,indent=2)+'\n')
f=pub/'README.md';v=f.read_text(encoding='utf-8');start=v.index('Current goal checkpoint');end=v.index('\n\n',start);v=v[:start]+'Current goal checkpoint (E172): **90 tok/s at both short and ~3K input is not qualified**. This is the existing goal-contract threshold; recent90/85 summaries repeated the older target incorrectly. C052 scheduling and C053 conditional accounting rejected. C053 all-ten medians: control90.05/86.65, candidate88.8/86.05 server_decode_tps; neither meets the full contract. Candidate source archived/reverted. Next: frozen random-coding speed and completion-quality checks on the retained native stack. Production unchanged; no benchmark model resident.'+v[end:];put(f,v)
print('E172 recorded; now restore only the four C053 source files from HEAD')
