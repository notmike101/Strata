from pathlib import Path
import csv,json,re
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking');d=pub/'diagnostics/scheduling/C052'
def put(f,s):
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(re.sub(r'C:[/\\]+Users[/\\]+me','<USER_HOME>',s).replace('<LAN_HOST>','<LAN_HOST>'),encoding='utf-8',newline='\n')
arms=['R102-split0','R103-split1'];data={a:json.loads((p/a/'summary.json').read_text()) for a in arms}
metrics=['server_decode_tps','prompt_tps','request_e2e_tps','stream_total_tps','ttft_seconds','request_seconds']
comparison={w:{k:{'control':data[arms[0]][w][k]['median'],'split':data[arms[1]][w][k]['median'],'percent':100*(data[arms[1]][w][k]['median']/data[arms[0]][w][k]['median']-1)} for k in metrics} for w in ['short','longer']}
files=list((p/arms[0]).glob('*.request.json'));assert len(files)==12
assert all(f.read_bytes()==(p/arms[1]/f.name).read_bytes() for f in files)
samples=[]
for a in arms:
    assert 'Cleanup verified: no live Strata' in (p/(a[:4]+'-wrapper.txt')).read_text()
    samples+=list(csv.DictReader((p/a/'safety.csv').open()))
safe={k:min(int(r[k]) for r in samples) for k in ['physical_available','commit_available']};assert min(safe.values())>=16*2**30
result={'arms':arms,'comparison':comparison,'identical_request_payloads':12,'safety_minimum_bytes':safe,'decision':'Rejected; no R104/R105 confirmation, production unchanged.'}
put(d/'summary.json',json.dumps(result,indent=2)+'\n')
note=f'''## E165 / C052 complete, split-window scheduling rejected

Previous goal turn was progress: C050 closed, C051 guard fixed and pushed49db7853.
This turn completed same-binary C052 A/B with one warmup and five measured runs
per short/~3K workload, exact twelve request payloads byte-identical. Every
request512tokens/cachemiss; C051 engine0dea69dc, HC1, acceptedusage0, barrier0,
fixed model/context/vision/sampling. Sole arm change: --no-spec-split/--spec-split.

| Ordinary five-run median | Unsplit | Split | Change |
|---|---:|---:|---:|
| Short server_decode_tps |90.5|79.0|-12.707%|
| ~3K server_decode_tps |84.5|78.3|-7.337%|
| Short prompt_tps |212.2|204.9|-3.440%|
| ~3K prompt_tps |494.7|494.9|+0.040%|
| Short request_e2e_tps |78.62648|69.80172|-11.224%|
| ~3K request_e2e_tps |41.98263|40.31463|-3.973%|
| Short stream_total_tps |78.63763|69.81643|-11.218%|
| ~3K stream_total_tps |41.98680|40.31906|-3.972%|
| Short TTFT seconds |.818503|.861862|+5.297%|
| ~3K TTFT seconds |6.183140|6.166672|-0.266%|

Control short91.3,87.5,90.5,85.5,96.7; longer83.3,84.5,81.8,86.4,85.8.
Split short79.0,81.0,78.6,79.2,78.3; longer78.3,76.4,76.3,78.4,78.7.
No slower seed or first graph capture removed. Short failure was noticed after
the longer set had begun; completed that already-planned set for evidence and
ran no extra confirmation. R104/R105 reservations unused. Reject; no promotion.
The control90.5 short is not full90/85 qualification (long84.5, quality pending).

Actual codepath evidence: live identity records exact split flags, engine hash,
and captured multiple-token windows. generate.cpp passes spec_split to set_split;
record_window chooses two groups when split_ and T>=2. Source is same in both.
No timing-instrumentation flags. Full output quality remains unqualified; these
truncated throughput samples do not establish compilable coding answers.

Independent16GiB floor passed: minimum physical{safe['physical_available']} and
commit{safe['commit_available']}bytes. All exact launcher/server/engine/vision trees
stopped; config3457fdfe restored, idleGPU457MiB. No process-memory polling during
requests. Production unchanged. The scheduling path is closed without a split
geometry sweep or speculative-accounting combination.
'''
plan='''## E166 / C053 request-conditional cache-accounting composition

Distinct combination hypothesis: C049 enabled accepted-row accounting even on
short requests where its token barrier was inactive. Its paired short89.1 versus
89.4 control did not qualify; C052's HC-only control90.5/84.5 shows useful short
performance without accepted-row accounting, but is NOT a same-day causal proof
against C049. Test that distinction on one binary, not pooled historical arms.

Add default-off STRATA_ACCEPTED_USAGE_BARRIER_ONLY=1. Requires acceptedusage1 and
configured positive barrier interval; malformed values reject before loading.
Effective accepted-row accounting is active only when this request has a positive
barrier interval. The existing minfresh1025 threshold is retained, not tuned to
seeds. Thus the combined experimental policy applies after longer fresh prompts;
short or small cached suffixes retain ordinary all-row accounting and window
adaptation. Minimum0 remains the old all-request mode. No sampling, routing,
weights, quantization or context change. Cache placement can affect CPU/GPU
rounding; no byte-identical whole-model output or quality claim follows.

Test first: enabled/disabled and gated/ungated predicates, inactive/positive
request intervals, alternating request policy with independent accepted/all-row
accounting oracles; malformed/dependency CLI configurations, C051 split rejection.
CUDA build and existing accepted-usage/token-barrier tests. HIP/SYCL unavailable.

Then finite same-binary ABBA: R106 control barrier-only0, R107 candidate1. Both
HC1,acceptedusage1,conditional64/minfresh1025,auto shareMAX1024,DMA0/deviceplan0,
lag2,9workers30tasks,MTP4/.70,PCIe.20. Unsplit only. Exact IQ3_S262144 INT8KV/
32768resident CPUF16vision. Numeric thinking1/.95/20/0/0/1,frequency0 unchanged.
Same original short/~3K requests,512tokens,cachemiss,stream/concurrency1,onewarmup
and five measured seeds101..105 each. If any decode/E2E median falls>3% or prompt
falls>2%, close without confirmation. Else exactly one reversed R108B/R109A pair,
ordinary all10medians per cell, no further threshold or interval sweep. Require
runtime proof of short ordinary accounting and long accepted accounting/barriers.
If retained, reverse-workload history, boundary/cache-hit tests and full frozen
random coding/quality/cold-warm/vision/tools/reasoning/cancel/maxcontext gates
remain. No promotion from screening metrics.16GiB guards and exact cleanup apply.
'''
put(d/'README.md',note);put(pub/'diagnostics/combinations/C053/plan.md',plan)
for f in [p/'findings.md',pub/'ledger.md']:
    old=f.read_text(encoding='utf-8');assert '## E165 /' not in old;put(f,old+'\n\n'+note+'\n\n'+plan)
put(d/'record-c052-prepare-c053.py',Path(__file__).read_text())
f=pub/'goal-90-state.json';v=json.loads(f.read_text());v.update(last_checkpoint='E166',current='C052 rejected after A/B. C053 request-conditional accounting composition planned; implementation gates next.',next=['Implement/test default-off barrier-only accepted-usage policy; same-binary finite comparison afterward.']);put(f,json.dumps(v,indent=2)+'\n')
print('E165 C052 closed; E166 C053 controlled composition plan recorded')
