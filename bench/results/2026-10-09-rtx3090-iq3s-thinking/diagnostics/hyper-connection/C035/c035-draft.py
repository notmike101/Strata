import hashlib,json,sys
from pathlib import Path
import numpy as np
p=Path(__file__).parent;root=p.parents[1];sys.path.insert(0,str(root/'tools'))
import iq_pack
cfg=json.loads((root/'strata-iq3_s.json').read_text());args=cfg['args'];pack=Path(args[args.index('--mtp')+1]);source=pack.parent/'mtp-q2_0.gguf'
model=iq_pack.Model(source);index={r.split()[0]:r.split() for r in (pack/'dense.txt').read_text().splitlines()}
rows=[]
with (pack/'dense.bin').open('rb') as f:
    for name,(_,t,_,_) in sorted(model.where.items()):
        if 'hyper_connection' not in name:continue
        short=name.removeprefix('mtp.').removeprefix('layers.0.');ix=index[short];kind=ix[1];offset=int(ix[4]);size=int(ix[5]);f.seek(offset);packed=f.read(size)
        raw=model.bytes(name)
        if t.type_name=='BF16' and kind=='bf16':reconstructed=raw.tobytes();method='unchanged BF16 bytes'
        elif t.type_name=='F32' and kind=='f32':reconstructed=(raw.view('<f4')+np.float32(1)).tobytes();method='existing GemmaRMSNorm pack transform FP32 source + 1'
        else:raise RuntimeError((name,t.type_name,kind))
        assert len(reconstructed)==size and reconstructed==packed,name
        rows.append({'name':name,'type':t.type_name,'coefficients':t.elements,'bytes':size,'method':method,'source_sha256':hashlib.sha256(raw).hexdigest(),'packed_sha256':hashlib.sha256(packed).hexdigest(),'reconstructed_sha256':hashlib.sha256(reconstructed).hexdigest(),'mismatching_bytes':0})
assert {r['name'].removeprefix('mtp.').removeprefix('layers.0.') for r in rows}=={n for n in index if 'hyper_connection' in n}
result={'source_file':source.name,'source_bytes':source.stat().st_size,'index_sha256':hashlib.sha256((pack/'dense.txt').read_bytes()).hexdigest(),'count':len(rows),'coefficients':sum(r['coefficients'] for r in rows),'q8_source_tensors':sum(r['type']=='Q8_0' for r in rows),'mismatching_bytes':0,'tensors':rows}
out=p/'C035-draft-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='tensors'},indent=2))
