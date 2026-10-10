from pathlib import Path
import json
p=Path('local-setup/target-80');pub=Path('bench/results/2026-10-09-rtx3090-iq3s-thinking')
note='''## E145 / P019 first differing longer-window diagnostic

Previous goal turn was progress: P016/P017 localized automatic prompt placement
as a variation source; P018 measured its actual share; C047 retained a6.07%short
prompt improvement as experimental but rejected promotion due decode/E2E loss.
Current goal still90/85 and full quality; no inference process at entry.

P019 replays the exact history through C047's first observed differing request:
shortwarmup+5measured payloads, longerwarmup+run1+run2,9requests per fresh process.
Two legs A/B,18diagnostic512-token requests maximum. Same8057ab78... binary,
fixed80 share/MAX1024,HC1/accepted1,DMA0/deviceplan0,262144context,CPU F16vision,
INT8KV/32768resident,MTP4/.70,PCIe.20,lag2,9workers30tasks. Numeric thinking coding
sampling unchanged. Only hooks: existing STRATA_TRACE request/window position/T
stderr lines and STRATA_DUMP_FIRST_LOGITS, no routing dump or source modification.
Capture every first-window logit file and full text; align trace windows by the
existing request marker. No speed qualification: tracing perturbs timing and
the later cell has only2nonwarmup requests. No third pair if divergence fails
to reproduce. Independent16GiB physical/commit guards, exact cleanup and config
restoration; no concurrent model/profiler/build. Raw logit binaries private.

Compare each request's first logits, sequence of(position,T), draft acceptance
and text. If logits match but window shapes first diverge, timing-driven draft
selection remains implicated; if first logits differ, prior cache/request state
must be examined. Neither alone proves cache scheduling is the sole cause.
The source adaptation schedule uses every4windows, while accepted-row heat alone
does not fix those boundaries. PR1779's accepted-token boundaries are a distinct
architectural candidate: fixed token positions, clipped windows, synchronous
publish after copies; not imported wholesale from its multi-GPU pipeline.
Do not change sampling, quantization or quality gates to obtain equal output.
'''
for f in [p/'findings.md',pub/'ledger.md']:
 s=f.read_text(encoding='utf-8');assert '## E145 /' not in s;f.write_text(s+'\n\n'+note,encoding='utf-8')
d=pub/'diagnostics/reproducibility/P019';d.mkdir(parents=True,exist_ok=True);(d/'plan.md').write_text(note,encoding='utf-8')
for leg in ['A','B']:
 c=json.loads((p/'R091-stack-share80.json').read_text(encoding='utf-8'));c['env'].update(STRATA_TRACE='1',STRATA_DUMP_FIRST_LOGITS=str((p/f'P019-{leg}-logits').resolve()));(p/f'P019-{leg}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
print('P019 finite diagnostic recorded')
