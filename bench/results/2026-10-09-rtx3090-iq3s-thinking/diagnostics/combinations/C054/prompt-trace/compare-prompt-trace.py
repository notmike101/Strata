"""Decompose instrumented prompt timing; never add these rows to qualification."""
import json
import re
import statistics
from pathlib import Path
p=Path(__file__).parent
names=['P021-prompt-trace-control','P022-prompt-trace-coupled']
result={'diagnostic_only':True,'qualifying_speed_runs':False,'arms':{}}
for name,source in zip(names,['R112-coupled-stack-control','R113-coupled-stack']):
    arm=p/name;ident=json.loads((arm/'identity.json').read_text());base=json.loads((p/source/'identity.json').read_text())
    cfg=json.loads(json.dumps(ident['config']));assert cfg['env'].pop('STRATA_TRACE')=='1';assert cfg==base['config']
    for key in ['engine_sha256','backend_library_sha256','vision_sha256','expert_profile_sha256']:
        assert ident[key]==base[key]
    assert 'Cleanup verified: no live Strata' in (p/(name.split('-')[0]+'-wrapper.txt')).read_text()
    groups=[];cur=None
    for line in (arm/'engine-session.txt').read_text().splitlines():
        request=re.search(r'strata trace: request (\d+) ',line)
        if request:
            cur={'prompt_tokens':int(request[1]),'batched_ms':0.,'windows_ms':0.,'refill_ms':0.,'lend_ms':0.,'refilled_slots':0,'read_tokens':0,'lent_slots':0,'buffer_chunk_tokens':[]}
        if cur is None:continue
        read=re.search(r'strata trace: read (\d+) tokens \((batched|windows)\) in ([\d.]+) ms',line)
        if read:cur[read[2]+'_ms']+=float(read[3]);cur['read_tokens']+=int(read[1])
        refill=re.search(r'strata trace: refilled (\d+) slots on \d+ stage\(s\) in ([\d.]+) ms',line)
        if refill:cur['refilled_slots']+=int(refill[1]);cur['refill_ms']+=float(refill[2])
        lend=re.search(r'strata trace: lent (\d+) slots for (\d+) tokens in ([\d.]+) ms',line)
        if lend:cur['lent_slots']+=int(lend[1]);cur['buffer_chunk_tokens'].append(int(lend[2]));cur['lend_ms']+=float(lend[3])
        if 'strata trace: prompt done (slots refilled)' in line:groups.append(cur);cur=None
    runs=json.loads((arm/'runs.json').read_text());assert len(groups)==len(runs)==12
    for row,g in zip(runs,groups):
        assert g['prompt_tokens']==row['prompt_tokens'] and g['read_tokens']==row['fresh_prompt_tokens']-1
        assert row['cached_tokens']==0 and row['completion_tokens']==512
        assert (arm/(row['label']+'.request.json')).read_bytes()==(p/source/(row['label']+'.request.json')).read_bytes()
        g.update(label=row['label'],workload=row['workload'],warmup=row['warmup'],prompt_ms=row['timings']['prompt_ms'],prompt_tps=row['prompt_tps'],ttft_seconds=row['ttft_seconds'])
        g['other_prompt_ms']=g['prompt_ms']-sum(g[m] for m in ['batched_ms','windows_ms','refill_ms','lend_ms'])
        assert g['other_prompt_ms']>=-1, g
    stats={}
    for cell in ['short','longer']:
        rr=[g for g in groups if g['workload']==cell and not g['warmup']];assert len(rr)==5
        stats[cell]={m:{'median':statistics.median(g[m] for g in rr),'raw':[g[m] for g in rr]} for m in ['prompt_ms','prompt_tps','batched_ms','windows_ms','refill_ms','lend_ms','other_prompt_ms','refilled_slots','ttft_seconds']}
    result['arms'][name]={'rows':groups,'summary':stats}
    ident.setdefault('qualification',{}).update(diagnostic_only=True,full_quality_matrix_pass=False,promoted=False)
    ident['contract']['purpose']='Instrumented prompt-stage diagnostic; excluded from qualifying speed repetitions'
    (arm/'identity.json').write_text(json.dumps(ident,indent=2)+'\n')
(p/'prompt-trace-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{c:{m:x['median'] for m,x in v.items()} for c,v in a['summary'].items()} for k,a in result['arms'].items()},indent=2))
