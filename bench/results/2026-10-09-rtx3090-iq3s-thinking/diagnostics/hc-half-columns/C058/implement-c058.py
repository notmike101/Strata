"""Generate the one-pass geometry without changing row arithmetic."""
import hashlib,json
from pathlib import Path
p=Path(__file__).parent
assert (p/'C058-red.txt').read_text().strip()=='FAIL id=0 T=1 apply=0 seed=0'
s=(p/'c057-kernels.inl').read_text().split('template<int EXACT_T>')[0]
k=s[s.index('__global__ void __launch_bounds__(THREADS) original_up'):]
k=k.replace('original_up','half_columns_up').replace('UPM_COLS','HALF_COLS')
k=k.replace('uint4 w[2][5]','uint4 w[1][5]').replace('[2] = {0.0f, 0.0f}','[1] = {0.0f}')
assert k.count('p < 2')==2
k=k.replace('p < 2','p < 1').replace('HC * HALF_COLS == 64','HC * HALF_COLS == 32')
(p/'c058-kernels.inl').write_text(s+'\nconstexpr int HALF_COLS=8;\n'+k)
m=json.loads((p/'C057-manifest.json').read_text())
for key in ['generated_sha256','executable_sha256','harness_sha256','utc']:m.pop(key,None)
m.update(generated_sha256=hashlib.sha256((p/'c058-kernels.inl').read_bytes()).hexdigest(),scope='generic T1..8 half-column up projection;32rows/block,256threads,320blocks; QFUSE disabled identically')
(p/'C058-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
s=(p/'run-c057.py').read_text().replace('C057','C058').replace('c057','c058')
(p/'run-c058.py').write_text(s)
print('C058 generated; reference unchanged, candidate one row pass per block')
