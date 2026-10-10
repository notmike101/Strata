"""Read-only actual-source inventory and full packed HC coefficient parity."""
import hashlib,importlib.util,json,sys,time
from pathlib import Path
import numpy as np
p=Path(__file__).parent; root=p.parents[1]
sys.path.insert(0,str(root/'tools'))
import iq_pack
spec=importlib.util.spec_from_file_location('memory_guard',p/'memory-guard.py')
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
out=p/'C035-result.json';assert not out.exists(),'Refuse to overwrite evidence'
config=json.loads((root/'strata-iq3_s.json').read_text())
args=config['args'];source=Path(args[args.index('--native')+1]);pack=Path(args[args.index('--pack')+1])
before=guard.memory_headroom();guard.require_headroom(*before)
start=time.monotonic();model=iq_pack.Model(source)
index={r.split()[0]:r.split() for r in (pack/'index.txt').read_text().splitlines() if r and not r.startswith('#')}
def hc(n):return n.startswith('output_hc_') or '.hc_attn_' in n or '.hc_ffn_' in n
selected=sorted(n for n in model.where if hc(n))
assert selected and set(selected)=={n for n in index if hc(n)}
rows=[];minimum=list(before)
with (pack/'dense.bin').open('rb') as f:
    for name in selected:
        head=guard.memory_headroom();guard.require_headroom(*head);minimum=[min(x,y) for x,y in zip(minimum,head)]
        _,t,_,shard=model.where[name];ix=index[name]
        kind=int(ix[2]);offset=int(ix[3]);size=int(ix[4]);f.seek(offset);packed=f.read(size);assert len(packed)==size
        raw=model.bytes(name);src=np.asarray(raw,dtype=np.uint8)
        if t.type_name=='Q8_0' and kind==4:
            blocks=src.reshape(-1,34);scale=blocks[:,:2].copy().view('<f2').reshape(-1).astype(np.float32)
            values=scale[:,None]*blocks[:,2:].view(np.int8).astype(np.float32)
            bits=values.view(np.uint32);reconstructed=((bits+np.uint32(0x7fff)+((bits>>16)&1))>>16).astype('<u2').tobytes()
        elif (t.type_name,kind) in [('BF16',4),('F32',2)]:reconstructed=src.tobytes()
        else:raise RuntimeError(f'Unexpected HC source/pack type {name} {t.type_name}/{kind}; stop without approximation')
        assert len(reconstructed)==size,(name,len(reconstructed),size)
        mismatch=sum(x!=y for x,y in zip(reconstructed,packed)) if reconstructed!=packed else 0
        rows.append({'name':name,'source_shard':shard.name,'source_type':t.type_name,'pack_kind':kind,'shape':t.shape,'coefficients':t.elements,'source_bytes':int(src.size),'pack_bytes':size,'source_sha256':hashlib.sha256(src).hexdigest(),'packed_sha256':hashlib.sha256(packed).hexdigest(),'reconstructed_sha256':hashlib.sha256(reconstructed).hexdigest(),'mismatching_bytes':mismatch})
        if mismatch:break
types={ty:sum(r['source_type']==ty for r in rows) for ty in sorted({r['source_type'] for r in rows})}
q8=sum(r['source_type']=='Q8_0' for r in rows)
result={'experiment':'C035','model':'ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF IQ3_S','scope':'all target HC projection/injection/normalization tensors in both model shards; draft weights separately inventoried','source_shards':[{'name':f.name,'bytes':f.stat().st_size} for f in model.paths],'pack_index_sha256':hashlib.sha256((pack/'index.txt').read_bytes()).hexdigest(),'config_sha256':hashlib.sha256((root/'strata-iq3_s.json').read_bytes()).hexdigest(),'tensor_count':len(rows),'expected_tensor_count':len(selected),'type_counts':types,'coefficients_compared':sum(r['coefficients'] for r in rows),'packed_bytes_compared':sum(r['pack_bytes'] for r in rows),'mismatching_bytes':sum(r['mismatching_bytes'] for r in rows),'q8_source_tensors':q8,'decision':'reject: required Q8 source blocks absent' if not q8 else 'parity evaluated; inspect before timing','microbenchmark_run':False,'server_launched':False,'minimum_physical_available_bytes':minimum[0],'minimum_commit_available_bytes':minimum[1],'seconds':time.monotonic()-start,'tensors':rows}
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='tensors'},indent=2))
