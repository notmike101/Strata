"""Independent original reference versus the integrated native entry point."""
from pathlib import Path
p = Path(__file__).parent
source = (p.parents[1] / 'src/kernels/cuda/native_mmvq.cu').read_text()
start = source.index('template<bool SmallK>\n__launch_bounds__(WARPS * WARP, 1)\n__global__ void native_q6_k_mmvq_kernel')
end = source.index('\n#if !defined(__HIPCC__)', start)
reference = source[start:end].replace('native_q6_k_mmvq_kernel', 'c032_original_kernel')
text = '#include "c029-original-helpers.inl"\nnamespace strata::kernels { namespace {\nconstexpr int WARPS=4;\n' + reference + '\n}\n'
text += '''void c032_reference(const void*w,const void*x,float*y,int ni,int no,cudaStream_t s) {
    c032_original_kernel<false><<<no,dim3(32,4),0,s>>>(static_cast<const Q6KBlock*>(w),static_cast<const Q81Block*>(x),y,ni,no);
}
void c032_actual(int,const void*w,const void*x,float*y,int ni,int no,cudaStream_t s) {
    native_q6_k_mmvq(w,x,y,ni,no,1,s);
}
}
'''
(p / 'c032-reference.inl').write_text(text)
s = (p / 'c029-dense-test.cu').read_text().replace('#include "c029-onewarp.inl"', '#include "c032-reference.inl"')
s = s.replace('strata::kernels::native_q6_k_mmvq(w,q,a+1,ni,rows_out,1,stream);', 'strata::kernels::c032_reference(w,q,a+1,ni,rows_out,stream);')
s = s.replace('strata::kernels::native_q6_k_mmvq(w,q,a,ni,no,1,stream);', 'strata::kernels::c032_reference(w,q,a,ni,no,stream);')
s = s.replace('c029_mmvq', 'c032_actual').replace('for(int group:{2,4,8})', 'for(int group:{4})').replace('for(int group:{1,2,4,8})', 'for(int group:{1,4})')
s = s.replace('graphs[4]{}', 'graphs[2]{}').replace('execs[4]{}', 'execs[2]{}').replace('groups[4]={1,2,4,8}', 'groups[2]={1,4}')
s = s.replace('i<4;++i', 'i<2;++i').replace('forward[]={1,2,4,8},reverse[]={8,4,2,1}', 'forward[]={1,4},reverse[]={4,1}').replace('order<4;++order', 'order<2;++order')
s = s.replace('warps_per_cta', 'reference_or_integrated').replace('C029 contract', 'C032 contract')
(p / 'c032-integrated-test.cu').write_text(s)
b = (p / 'build-c030-dense.cmd').read_text().replace('c029-dense-test.cu', 'c032-integrated-test.cu').replace('c030-dense-test.exe', 'c032-integrated-test.exe').replace('build-cuda86 ', 'build-cuda86-main ')
(p / 'build-c032-integrated.cmd').write_text(b)
(p / 'build-c031-dispatch-green.cmd').write_text((p / 'build-c031-dispatch.cmd').read_text().replace('build-cuda86 ', 'build-cuda86-main '))
assert 'c032_reference(w,q,a+1' in s and 'for(int group:{4})' in s
print('C032 independent original reference and integrated entry-point test prepared')
