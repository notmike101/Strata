import collections,hashlib,json,sqlite3,statistics
from pathlib import Path
p=Path(__file__).resolve().parent;db=p/'P025-decode.sqlite'
expected='0e9d29844308e03a051e9bc72ba678dd73388117136d074d65ecbebdf00da11e'
assert hashlib.sha256(db.read_bytes()).hexdigest()==expected
c=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
rows=c.execute('select k.start,k.end,k.graphId,k.correlationId,k.streamId,s.value from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName where s.value like ? or s.value like ?',('%sigmoid_scale_rows_vec4%','%combine_k10_vec4%')).fetchall();c.close()
groups=collections.defaultdict(lambda:collections.defaultdict(list))
for a,b,g,corr,stream,name in rows:
 if stream==19:groups[(g,corr)]['scale' if 'sigmoid' in name else 'combine'].append((a,b))
leads=[];excluded=[];scale_sum=0
for key,group in groups.items():
 if len(group['scale'])!=48 or len(group['combine'])!=48:excluded.append({'counts':{k:len(v) for k,v in group.items()}});continue
 for scale,combine in zip(sorted(group['scale']),sorted(group['combine'])):
  leads.append((combine[0]-scale[1])/1000);scale_sum+=scale[1]-scale[0]
r={'source_sha256':expected,'scope':'P025 stream19 graph-launch groups with exactly48 scales and48 combines, paired by temporal ordinal under the serial unsplit48-layer source structure. Instrumented diagnostic, not a dependency reconstruction.','qualified_graph_groups':(len(leads)//48),'excluded_groups':excluded,'pairs':len(leads),'scale_summed_ms':scale_sum/1e6,'scale_end_to_combine_start_us':{'min':min(leads),'median':statistics.median(leads),'max':max(leads),'positive':sum(x>0 for x in leads),'nonpositive':sum(x<=0 for x in leads)},'limitations':['Nsight reports these graph nodes on the same streamId; this does not recover original capture-stream dependencies.','A positive lead is not proof all scale duration was overlapped or removable.','Recorded event completeness warning and profiling overhead from P025 remain.','No served speed or causal explanation is proven by this timing audit alone.']}
(p/'P025-shared-scale-lead.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
