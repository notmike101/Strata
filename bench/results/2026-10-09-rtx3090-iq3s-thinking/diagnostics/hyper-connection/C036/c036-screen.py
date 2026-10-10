import hashlib,importlib.util,json,time
from pathlib import Path
import numpy as np
p=Path(__file__).parent;root=p.parents[1]
spec=importlib.util.spec_from_file_location('guard',p/'memory-guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
cfg=json.loads((root/'strata-iq3_s.json').read_text());args=cfg['args'];pack=Path(args[args.index('--pack')+1]);draft=Path(args[args.index('--mtp')+1])
target_rows=json.loads((p/'C035-result.json').read_text())['tensors'];draft_rows=json.loads((p/'C035-draft-result.json').read_text())['tensors']
idx={r.split()[0]:r.split() for r in (pack/'index.txt').read_text().splitlines() if r and not r.startswith('#')}
di={r.split()[0]:r.split() for r in (draft/'dense.txt').read_text().splitlines()}
out=p/'C036-result.json';assert not out.exists()
rows=[];start=time.monotonic();minimum=list(guard.memory_headroom())
for scope,source,items in [('target',pack,target_rows),('draft',draft,draft_rows)]:
    with (source/'dense.bin').open('rb') as f:
        for item in items:
            if item.get('source_type',item.get('type'))!='BF16':continue
            name=item['name'];short=name.removeprefix('mtp.').removeprefix('layers.0.')
            ix=idx[name] if scope=='target' else di[short];off,size=map(int,ix[3:5] if scope=='target' else ix[4:6])
            head=guard.memory_headroom();guard.require_headroom(*head);minimum=[min(x,y) for x,y in zip(minimum,head)]
            f.seek(off);raw=f.read(size);assert hashlib.sha256(raw).hexdigest()==item['packed_sha256']
            u=np.frombuffer(raw,dtype='<u2').reshape(-1,32);exp=(u>>7)&255;base=exp.min(axis=1);eligible=exp.max(axis=1)-base<=15
            header=base.astype('<u4');esc=np.flatnonzero(~eligible);fallback=u[esc].copy();header[esc]=np.arange(len(esc),dtype=np.uint32)|np.uint32(0x80000000)
            delta=((exp-base[:,None])&15).astype(np.uint8);nibbles=delta[:,0::2]|(delta[:,1::2]<<4)
            sm=((u&127)|((u>>8)&128)).astype(np.uint8)
            encoded=np.empty((len(u),52),dtype=np.uint8);encoded[:,:4]=header.view(np.uint8).reshape(-1,4);encoded[:,4:20]=nibbles;encoded[:,20:]=sm
            h=encoded[:,:4].copy().view('<u4').reshape(-1);n=encoded[:,4:20];s=encoded[:,20:]
            de=np.empty_like(u);de[:,0::2]=(n&15).astype(np.uint16);de[:,1::2]=(n>>4).astype(np.uint16)
            reconstructed=((s.astype(np.uint16)&128)<<8)|((de+(h[:,None]&255)).astype(np.uint16)<<7)|(s&127).astype(np.uint16)
            mask=(h&0x80000000)!=0;reconstructed[mask]=fallback[h[mask]&0x7fffffff]
            mismatch=int(np.count_nonzero(reconstructed!=u));assert not mismatch,name
            rows.append({'scope':scope,'name':name,'shape':item.get('shape'),'coefficients':int(u.size),'blocks':len(u),'eligible_blocks':int(eligible.sum()),'fallback_blocks':len(esc),'original_bytes':size,'encoded_bytes':int(encoded.nbytes+fallback.nbytes),'mismatching_coefficients':mismatch,'source_sha256':hashlib.sha256(raw).hexdigest(),'reconstructed_sha256':hashlib.sha256(reconstructed.astype('<u2').tobytes()).hexdigest()})
original=sum(r['original_bytes'] for r in rows);encoded=sum(r['encoded_bytes'] for r in rows);blocks=sum(r['blocks'] for r in rows);eligible=sum(r['eligible_blocks'] for r in rows)
result={'experiment':'C036','format':'52 bytes per32 BF16 values plus64 bytes per fallback block','tensor_count':len(rows),'coefficients':sum(r['coefficients'] for r in rows),'original_bytes':original,'encoded_bytes':encoded,'reduction_fraction':1-encoded/original,'eligible_fraction':eligible/blocks,'mismatching_coefficients':sum(r['mismatching_coefficients'] for r in rows),'eligibility_pass':eligible/blocks>=.95 and 1-encoded/original>=.15,'minimum_physical_available_bytes':minimum[0],'minimum_commit_available_bytes':minimum[1],'seconds':time.monotonic()-start,'tensors':rows}
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='tensors'},indent=2))
