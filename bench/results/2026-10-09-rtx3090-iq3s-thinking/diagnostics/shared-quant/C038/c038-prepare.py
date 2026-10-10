import json,sys,hashlib,importlib.util
from pathlib import Path
p=Path(__file__).parent;root=p.parents[1];sys.path.insert(0,str(root/'tools'))
import iq_pack
spec=importlib.util.spec_from_file_location('mg',p/'memory-guard.py');mg=importlib.util.module_from_spec(spec);spec.loader.exec_module(mg)
h=mg.memory_headroom();mg.require_headroom(*h)
cfg=json.loads((root/'strata-iq3_s.json').read_text());a=cfg['args'];m=iq_pack.Model(Path(a[a.index('--native')+1]))
d=p/'C038-private';d.mkdir(exist_ok=False);rows=[]
for i,l in enumerate([0,23,47]):
    row={'layer':l,'weights':[]}
    for key in ['gate','up']:
        name=f'blk.{l}.ffn_{key}_shexp.weight';_,t,_,shard=m.where[name];raw=m.bytes(name).tobytes()
        assert list(t.shape)==[2560,640],t.shape
        (d/f'{i}-{key}.bin').write_bytes(raw)
        row['weights'].append({'name':name,'type':t.type_name,'type_id':int(t.ggml_type) if hasattr(t,'ggml_type') else None,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    rows.append(row)
(p/'C038-manifest.json').write_text(json.dumps({'memory_snapshot':{'physical_available':h[0],'commit_available':h[1]},'tensors':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
