"""P013: offline interval-union audit; no raw profiler environment is exported."""
import json,sqlite3,collections,statistics
from pathlib import Path
p=Path(__file__).parent
c=sqlite3.connect((p/'P009-decode.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
names=dict(c.execute('select id,value from StringIds'))
def category(name):
 if 'wait_flag' in name:return 'wait_flag'
 if 'mmvq' in name and ('native_q6_k_' in name or 'Q6K' in name):return 'q6_mmvq'
 if 'sampler' in name or 'sample_' in name:return 'sampler'
 if 'fetch' in name:return 'expert_fetch'
 return 'other_kernel'
events=[];counts=collections.Counter();sums=collections.Counter();by_stream=collections.defaultdict(list);graphs=collections.defaultdict(list)
for start,end,stream,graph,corr,n in c.execute('select start,end,streamId,graphId,correlationId,demangledName from CUPTI_ACTIVITY_KIND_KERNEL'):
 cat=category(names[n]);counts[cat]+=1;sums[cat]+=end-start;events.extend([(start,1,cat),(end,-1,cat)]);by_stream[stream].append((start,end))
 if graph is not None:graphs[(graph,corr)].append((start,end))
for table in ['CUPTI_ACTIVITY_KIND_MEMCPY','CUPTI_ACTIVITY_KIND_MEMSET']:
 for start,end in c.execute('select start,end from '+table):
  cat=table.split('_')[-1].lower();counts[cat]+=1;sums[cat]+=end-start;events.extend([(start,1,cat),(end,-1,cat)])
events.sort();first=events[0][0];last=events[-1][0];prev=first;active=collections.Counter();unions=collections.Counter();only=collections.Counter();hist=collections.Counter()
for t,d,cat in events:
 dt=t-prev;present=[k for k,v in active.items() if v]
 hist['any_activity' if present else 'no_recorded_activity']+=dt
 for k in present:unions[k]+=dt
 if len(present)==1:only[present[0]]+=dt
 active[cat]+=d;assert active[cat]>=0;prev=t

def merge_stats(xs):
 xs.sort();a,b=xs[0];union=0;gaps=[]
 for s,e in xs[1:]:
  if s>b:union+=b-a;gaps.append(s-b);a=s;b=e
  else:b=max(b,e)
 union+=b-a
 return {'span_ms':(max(x[1] for x in xs)-xs[0][0])/1e6,'union_ms':union/1e6,'gaps_ms':sum(gaps)/1e6,'gap_count':len(gaps),'median_gap_us':statistics.median(gaps)/1e3 if gaps else 0,'max_gap_us':max(gaps)/1e3 if gaps else 0}
r={'source':'P009-decode.sqlite','source_sha256':'85ba11f5d3d2d71f059c5b70495709211bce2def39473f8f7d5b621f735cb394','scope':'all recorded CUDA kernel/memcpy/memset intervals, software node-instrumented diagnostic capture','span_ms':(last-first)/1e6,'activity_ms':{k:v/1e6 for k,v in hist.items()},'categories':{k:{'count':counts[k],'summed_ms':sums[k]/1e6,'union_ms':unions[k]/1e6,'only_category_active_ms':only[k]/1e6} for k in counts},'streams':{str(k):merge_stats(v) for k,v in by_stream.items()},'graph_launch_envelopes':len(graphs),'limitations':['Temporal overlap is not a CUDA dependency or critical-path reconstruction.','Only-category-active time includes multiple kernels of that category; it is not removable latency.','No recorded activity is not proof the GPU was idle or blocked on CPU; missing activity and instrumentation gaps remain possible.','P010 internal consistency does not independently prove completeness. No served speed or optimization benefit is inferred.']}
r['copy_groups']=[dict(zip(['copy_kind','src_kind','dst_kind','calls','bytes','summed_ms'],row)) for row in c.execute('select copyKind,srcKind,dstKind,count(*),sum(bytes),sum(end-start)/1e6 from CUPTI_ACTIVITY_KIND_MEMCPY group by copyKind,srcKind,dstKind')]
(p/'P013-overlap.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['span_ms','activity_ms','categories']},indent=2))
