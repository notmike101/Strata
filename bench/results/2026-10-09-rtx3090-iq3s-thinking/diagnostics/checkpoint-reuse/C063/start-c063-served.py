import hashlib,json,re,shutil,statistics,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[1];pub=root/'bench/results/2026-10-09-rtx3090-iq3s-thinking'
assert '100% tests passed out of 8' in (p/'C063-tests-result.txt').read_text()
assert 'FAIL: recycle discarded running-state allocation' in (p/'C063-red-result.txt').read_text()
raw=(p/'C063-storage-result.txt').read_text()
rows=[(int(a),int(b),float(c),int(d)) for a,b,c,d in re.findall(r'COPY round=(-?\d+) reuse=(\d+) bytes=117669888 ms=([\d.]+) all_bytes_equal=(\d+)',raw)]
assert len(rows)==16 and all(r[3]==1 for r in rows)
med=[statistics.median([r[2] for r in rows if r[0]>=0 and r[1]==i]) for i in (0,1)]
assert med[1]<med[0]
exe=root/'engine/strata-cuda133-checkpoint-reuse.exe';assert not exe.exists()
shutil.copy2(p/'build-cuda86-main/strata.exe',exe);sha=hashlib.sha256(exe.read_bytes()).hexdigest()
base=json.loads((p/'R119-prefix-preserve.json').read_text());base['exe']=str(exe)
arms=['R136-checkpoint-control','R137-checkpoint-candidate','R138-checkpoint-candidate-reverse','R139-checkpoint-control-reverse']
for i,name in enumerate(arms):
 assert not (p/(name+'.json')).exists();c=json.loads(json.dumps(base));c['env']['STRATA_CHECKPOINT_REUSE']='1' if i in (1,2) else '0';(p/(name+'.json')).write_text(json.dumps(c,indent=2)+'\n')
runner=(p/'run-c020-arm.py').read_text();spot="        print('COMPLETE',a.out,flush=True)"
check="""        if candidate.get('env',{}).get('STRATA_CHECKPOINT_REUSE') == '1':
            session=engine_log.read_bytes()[log_offset:]
            if b'discarded checkpoint storage reuse active' not in session:
                raise RuntimeError('Requested checkpoint reuse was not exercised; arm invalid')
"""
assert runner.count(spot)==1;(p/'run-c063-arm.py').write_text(runner.replace(spot,check+spot))
for source,dest in [('record-c062-arm.py','record-c063-arm.py'),('pool-c062-stream-cache.py','pool-c063-stream-cache.py'),('record-c062-pool.py','record-c063-pool.py')]:
 s=(p/source).read_text().replace('C062','C063').replace('c062','c063').replace('shared-scale-fusion','checkpoint-reuse').replace('STRATA_SHARED_SCALE_FUSE','STRATA_CHECKPOINT_REUSE').replace('shared scale-only fusion captured (CUDA K10 T2..8)','discarded checkpoint storage reuse active')
 for old,new in zip(['R132-shared-scale-control','R133-shared-scale-candidate','R134-shared-scale-candidate-reverse','R135-shared-scale-control-reverse'],arms):s=s.replace(old,new)
 s=s.replace('R132-R135','R136-R139')
 (p/dest).write_text(s)
result={'id':'C063','engine_sha256':sha,'micro_bytes':117669888,'micro_control_median_ms':med[0],'micro_reuse_median_ms':med[1],'micro_all_bytes_verified':True,'cuda_test_targets':8,'arms':arms,'full_goal_qualified':False}
(p/'C063-summary.json').write_text(json.dumps(result,indent=2)+'\n')
diff=subprocess.check_output(['node',r'<USER_HOME>/github-agent/identity.mjs','--repo','notmike101/Strata','git','diff','--','src/program/generate.cpp','src/core/conversation_snapshot_test.cpp'],cwd=root,text=True)
note=f'''## E256 / C063 regression checks passed; fixed served comparison declared

The allocation/copy screen retained all16 rows: one warmup and seven alternating paired rounds, each117669888bytes (112.21875MiB). Ordinary fresh-allocation median{med[0]:.4f}ms versus retained-allocation{med[1]:.4f}ms. Every byte matched the changing fill pattern. This is an isolated host-allocation and D2H copy result, not generation throughput or a full checkpoint timing.

The initial test build failed because conversation-test targets were disabled; enabling STRATA_BUILD_CONVERSATION_TESTS repaired the build configuration. The deliberate stub then failed the actual snapshot regression at allocation recycling. The implemented helper passed all eight selected CUDA regression targets, including real save/restore, fresh overwrite of all five payload vectors, allocation ownership, metadata preservation, occupied/self/stage exclusions and abandoning an unused spare. The abandoned-spare test is a unit ownership check, not served cancellation qualification. No HIP/SYCL build or upstream review claim.

STRATA_CHECKPOINT_REUSE is default-off, single-engine, unbatched, with parked conversation caching disabled. It retains at most one discarded checkpoint's host payload after the unchanged prefix predicate proves that checkpoint invalid. Valid checkpoints and token/image metadata are unchanged. The next save resizes and overwrites all payload bytes; memory-pressure admission releases the spare. No additional VRAM, model arithmetic, sampling or context change. C059 correctness fix is common to both variants; QFUSE remains off. C062 integration stays removed.

Fresh named engine SHA256 {sha}. The served comparison uses this same binary and C056 optimization stack, differing only in STRATA_CHECKPOINT_REUSE0/1. C056 is an experimental stack, not the qualified production launcher; its previous cache regression remains unresolved. This isolation screen cannot itself promote the stack over production.

Predeclared sequence: R136 control short-first, R137 candidate short-first, R138 candidate longer-first, R139 control longer-first. Four fresh processes, one warmup new/repeat pair and five measured new/repeat pairs per length:96 requests,80 measured,16 warmups. Frozen selected coding fixture and seeds101..105,512tokens, stream, serial,262144context,IQ3_S,INT8KV,CPUvision, thinking1/.95/20/min-p0/presence0/repetition1, MTP4/.70 andPCIe.20 remain fixed. Separate32,768 completed-answer allowance remains approved; no capped answer is a quality pass.

Pool every qualifying measured row with the ordinary median; require90short/85long in pooled and individual candidate-process medians. Keep the declared no-degradation prompt/client/decode/TTFT gates, every failed arm and first-request warmup separately. Do not silently redefine the control or repeat unchanged arms until favorable. The contract allows investigating ambiguous differences, but this screen is fixed in advance. Fresh-process first rows are not full cold qualification. Supervisor checks actual reuse marker after requests,16GiB physical/commit floors every second, identity, cache hits,512length, exact cleanup and production-config restoration. No process-memory polling or concurrent profiling/builds during requests. Same-PC client through LAN address, not a separate LAN client's latency.
'''
def put(f,s):
 f.parent.mkdir(parents=True,exist_ok=True);s=re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>');f.write_text('\n'.join(x.rstrip() for x in s.splitlines()).rstrip()+'\n',encoding='utf-8',newline='\n')
d=pub/'diagnostics/checkpoint-reuse/C063';put(d/'integration-and-served-plan.md',note);put(d/'source.patch.json',json.dumps({'patch':diff},indent=2))
put(d/'checkpoint_storage_reuse.hpp',(root/'include/strata/core/checkpoint_storage_reuse.hpp').read_text())
put(d/'C063-test-detail.txt',(p/'build-cuda86-main/Testing/Temporary/LastTest.log').read_text())
names=['C063-summary.json','start-c063-served.py','c063-storage.cu','build-c063-storage.cmd','run-c063-storage.py','build-c063-red.cmd','run-c063-red.py','build-c063-engine.cmd','run-c063-tests.py','run-c063-arm.py']
names += [f.name for f in p.glob('C063-*') if f.is_file() and f.suffix in ('.txt','.csv','.json')]
for name in sorted(set(names)):put(d/name,(p/name).read_text())
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text().replace('112.2197MiB','112.21875MiB');assert '## E256 /' not in s;put(f,s+'\n\n'+note)
f=d/'plan.md';put(f,f.read_text().replace('112.2197MiB','112.21875MiB'))
f=pub/'goal-90-state.json';s=json.loads(f.read_text());s.update(last_checkpoint='E256',current='C063 eight CUDA tests passed; fixed R136-R139 served comparison declared.',next=['Run R136-R139 once, record every arm, pool all measurements; no launcher promotion.'],resume_command='Follow the live run-c063-arm process/session. Never duplicate a live arm.');s['c063']=result;put(f,json.dumps(s,indent=2))
print(json.dumps(result,indent=2))
