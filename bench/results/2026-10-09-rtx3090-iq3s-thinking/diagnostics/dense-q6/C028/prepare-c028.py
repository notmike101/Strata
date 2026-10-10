"""Adapt the existing C021 harness to actual dense tensors; keep its candidate unchanged."""
import json
from pathlib import Path
p = Path(__file__).parent
s = (p / 'c021-rowgroup-test.cu').read_text()
s = s.replace('if(argc<3)return 2;', 'if(argc<4)return 2;')
s = s.replace('for(int i=1;i<argc;++i)shards.emplace_back(argv[i]);', 'for(int i=2;i<argc;++i)shards.emplace_back(argv[i]);')
s = s.replace('model.find("output.weight",&at)', 'model.find(argv[1],&at)')
s = s.replace('if(!tensor||tensor->type!=14||tensor->shape!=std::vector<uint64_t>{2560,248320})throw std::runtime_error("Unexpected actual head identity");\n    constexpr int ni=2560,no=248320;',
              'if(!tensor||tensor->type!=14||tensor->shape.size()!=2)throw std::runtime_error("Unexpected actual dense tensor identity");\n    const int ni=int(tensor->shape[0]),no=int(tensor->shape[1]);\n    if(ni<1024||no>12288)throw std::runtime_error("Shape outside C028 contract");\n    std::printf("TENSOR %s input=%d output=%d\\n",argv[1],ni,no);')
s = s.replace('bytes!=521472000||', '')
s = s.replace('{1,3,4,5,17,2560,no}', '{1,3,4,5,17,no-1,no}')
s = s.replace('constexpr int repeats=16;', '''constexpr int repeats=64;
    cudaGraph_t graphs[4]{};cudaGraphExec_t execs[4]{};
    const int groups[4]={1,2,4,8};
    for(int i=0;i<4;++i){
        check(cudaStreamBeginCapture(stream,cudaStreamCaptureModeThreadLocal));
        for(int r=0;r<repeats;++r)launch(groups[i]);
        check(cudaStreamEndCapture(stream,&graphs[i]));
        check(cudaGraphInstantiate(&execs[i],graphs[i],nullptr,nullptr,0));
        check(cudaGraphLaunch(execs[i],stream));
    }
    check(cudaStreamSynchronize(stream));
    size_t free_bytes=0,total_bytes=0;check(cudaMemGetInfo(&free_bytes,&total_bytes));
    std::printf("DEVICE_ALLOCATED_WITH_GRAPHS bytes=%zu\\n",total_bytes-free_bytes);''')
s = s.replace('milliseconds_per_head', 'milliseconds_per_projection')
s = s.replace('for(int rep=0;rep<repeats;++rep)launch(group);',
              'int gi=0;while(groups[gi]!=group)++gi;check(cudaGraphLaunch(execs[gi],stream));')
s = s.replace('check(cudaEventDestroy(begin));check(cudaEventDestroy(end));',
              'for(int i=0;i<4;++i){check(cudaGraphExecDestroy(execs[i]));check(cudaGraphDestroy(graphs[i]));}\n    check(cudaEventDestroy(begin));check(cudaEventDestroy(end));')
(p / 'c028-dense-test.cu').write_text(s)
(p / 'build-c028-dense.cmd').write_text((p / 'build-c021-rowgroup.cmd').read_text().replace('c021-rowgroup-test', 'c028-dense-test'))
assert 'constexpr int ni=2560,no=248320' not in s
assert 'cudaGraphLaunch(execs[gi]' in s
print('C028 harness prepared; original C021 candidate unchanged')
