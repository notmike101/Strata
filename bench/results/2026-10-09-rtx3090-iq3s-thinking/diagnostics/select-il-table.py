"""Conservative exact-layout candidate: >=3% over shipped choice in both sweeps."""
import json,re
from pathlib import Path
p=Path(__file__).resolve().parent
baseline={23:[[0,0,0,0,0],[0,0,2,4,4],[0,1,1,1,1]],
          12:[[0,0,1,1,1],[0,1,1,1,1],[0,1,1,1,1]],
          13:[[0,0,1,1,1],[0,4,1,1,1],[0,1,1,1,2]],
          14:[[0,0,1,1,0],[0,0,1,1,2],[0,0,1,1,1]]}
candidate=json.loads(json.dumps(baseline)); candidate={int(k):v for k,v in candidate.items()}
types={'IQ4_XS':23,'Q4_K':12,'Q5_K':13,'Q6_K':14}
cells={}
for label in ('a','b'):
    text=(p/f'C013-il-{label}.txt').read_text()
    assert 'mmvq_il_parity: OK' in text and 'FAIL ' not in text
    for match in re.finditer(r'BENCH (.*?)\s+T=(\d+)\s+multi ([\d.]+) us \| il rows1 ([\d.]+) rows2 ([\d.]+) rows4 ([\d.]+) us',text):
        name,nt,*times=match.groups(); ty=types[name.split()[0]]; nt=int(nt)
        nout=int(re.findall(r'\d+x(\d+)',name)[-1]); cls=next((i for i,v in enumerate((2048,4096,8192,12288)) if nout<v),4)
        if 2<=nt<=4: cells.setdefault((ty,nt,cls),[]).append(dict(sweep=label,shape=name,times=dict(zip((0,1,2,4),map(float,times)))))
changes=[]
for (ty,nt,cls),observations in sorted(cells.items()):
    assert {x['sweep'] for x in observations}=={'a','b'}
    old=baseline[ty][nt-2][cls]
    ratios={r:max(x['times'][r]/x['times'][old] for x in observations) for r in (0,1,2,4)}
    new=min(ratios,key=ratios.get)
    if new!=old and ratios[new]<=0.97:
        candidate[ty][nt-2][cls]=new
        changes.append(dict(type=ty,nt=nt,row_class=cls,old=old,new=new,worst_ratio=ratios[new],observations=observations))
env=';'.join(f'{ty}:{nt}:'+','.join(map(str,rows)) for ty,table in candidate.items() for nt,rows in enumerate(table,2))
result=dict(rule='Every measured shape in both sweeps must beat the shipped row choice by at least3%; unmeasured/uncertain cells unchanged.',changes=changes,env=env)
(p/'C013-il-selection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if changes:
    config=json.loads((p/'B008-promoted-control.json').read_text())
    config['env']['STRATA_MMVQ_IL_ROWS']=env
    (p/'R028-measured-il-table.json').write_text(json.dumps(config,indent=2)+'\n')
