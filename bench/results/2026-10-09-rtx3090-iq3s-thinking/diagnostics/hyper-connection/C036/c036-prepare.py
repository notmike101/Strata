import json
from pathlib import Path
import numpy as np
p=Path(__file__).parent;root=p.parents[1];cfg=json.loads((root/'strata-iq3_s.json').read_text());args=cfg['args'];pack=Path(args[args.index('--pack')+1])
index={r.split()[0]:r.split() for r in (pack/'index.txt').read_text().splitlines() if r and not r.startswith('#')}
names=sorted(n for n in index if n.endswith(('.hc_attn_up.weight','.hc_ffn_up.weight')) or n=='output_hc_up.weight')
selected=[names[0],names[len(names)//2],names[-1]];d=p/'C036-private';d.mkdir(exist_ok=False);manifest=[]
with (pack/'dense.bin').open('rb') as f:
    for i,name in enumerate(selected):
        ix=index[name];assert ix[7:9]==['320','10240'];off,size=map(int,ix[3:5]);f.seek(off);raw=f.read(size)
        u=np.frombuffer(raw,dtype='<u2').reshape(-1,32);exp=(u>>7)&255;base=exp.min(axis=1);eligible=exp.max(axis=1)-base<=15
        header=base.astype('<u4');esc=np.flatnonzero(~eligible);fallback=u[esc].copy();header[esc]=np.arange(len(esc),dtype=np.uint32)|np.uint32(0x80000000)
        delta=((exp-base[:,None])&15).astype(np.uint8);encoded=np.empty((len(u),52),dtype=np.uint8)
        encoded[:,:4]=header.view(np.uint8).reshape(-1,4);encoded[:,4:20]=delta[:,0::2]|(delta[:,1::2]<<4);encoded[:,20:]=((u&127)|((u>>8)&128)).astype(np.uint8)
        prefix=d/str(i);prefix.with_suffix('.bf16').write_bytes(raw);prefix.with_suffix('.packed').write_bytes(encoded.tobytes());prefix.with_suffix('.fallback').write_bytes(fallback.tobytes())
        manifest.append({'id':i,'name':name,'bf16_bytes':len(raw),'packed_bytes':encoded.nbytes,'fallback_bytes':fallback.nbytes})
(p/'C036-timing-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
src=(root/'src/kernels/cuda/fused_gr.cu').read_text();start=src.index('struct Bf16x8');end=src.index('__global__ void',start)
(p/'c036-dot.inl').write_text(src[start:end])
b=(p/'build-c034-graph.cmd').read_text().replace('c034-hc-graph','c036-kernel')
(p/'build-c036.cmd').write_text(b)
