"""Read-only trace consistency audit; never export capture environment metadata."""
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

p = Path(__file__).parent
db = p / 'P025-decode.sqlite'
c = sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True)
pid_shift = 24
groups = defaultdict(list)
direct = set()
kernel_count = 0
invalid_intervals = 0
for pid, corr, graph, node, start, end in c.execute('select globalPid,correlationId,graphId,graphNodeId,start,end from CUPTI_ACTIVITY_KIND_KERNEL'):
    key = (pid >> pid_shift, corr)
    kernel_count += 1
    invalid_intervals += end <= start
    if graph is None:
        direct.add(key)
    else:
        groups[graph, key].append(node)

graph_apis = set()
direct_apis = {}
nonzero_launch_returns = 0
for tid, corr, name, ret in c.execute("select r.globalTid,r.correlationId,s.value,r.returnValue from CUPTI_ACTIVITY_KIND_RUNTIME r join StringIds s on s.id=r.nameId where s.value like '%Launch%'"):
    key = (tid >> pid_shift, corr)
    nonzero_launch_returns += ret != 0
    if name.startswith('cudaGraphLaunch'):
        graph_apis.add(key)
    elif 'LaunchKernel' in name:
        direct_apis[key] = name

cohorts = defaultdict(list)
graph_keys = set()
for (graph, key), nodes in groups.items():
    cohorts[graph].append(nodes)
    graph_keys.add(key)
graph_summary = []
for graph, launches in sorted(cohorts.items()):
    reference = Counter(launches[0])
    graph_summary.append({'graph_id': graph, 'observed_launches': len(launches),
                          'kernel_nodes_per_launch': sorted(set(map(len, launches))),
                          'different_node_multisets_from_first': sum(Counter(nodes) != reference for nodes in launches),
                          'duplicate_node_ids_within_launch': sum(len(nodes) != len(set(nodes)) for nodes in launches)})

all_kernel_launch_keys = graph_keys | direct
unmatched = Counter(name for key, name in direct_apis.items() if key not in all_kernel_launch_keys)
api_rows = list(c.execute("select r.globalTid,r.correlationId,s.value,r.start,r.end from CUPTI_ACTIVITY_KIND_RUNTIME r join StringIds s on s.id=r.nameId where s.value like '%LaunchKernel%' or s.value like '%Capture%' order by r.start"))
open_capture = {}
capture_ranges = []
for tid, corr, name, start, end in api_rows:
    if name.startswith('cudaStreamBeginCapture'):
        open_capture[tid] = end
    elif name.startswith('cudaStreamEndCapture') and tid in open_capture:
        capture_ranges.append((tid, open_capture.pop(tid), start))
node_events = list(c.execute('select graphNodeId,originalGraphNodeId,start from CUDA_GRAPH_NODE_EVENTS'))
original_nodes = {node: original for node, original, _ in node_events if original is not None}
capture_proofs = []
for tid, begin, end in capture_ranges:
    apis = [r for r in api_rows if r[0] == tid and 'LaunchKernel' in r[2] and begin <= r[3] <= r[4] <= end and (tid >> pid_shift, r[1]) not in all_kernel_launch_keys]
    created = {node for node, _, start in node_events if begin <= start <= end}
    matching_graphs = []
    for graph, launches in cohorts.items():
        if {original_nodes.get(node, node) for node in launches[0]} == created:
            matching_graphs.append(graph)
    capture_proofs.append({'begin_after_api_ns': begin, 'end_before_api_ns': end,
                           'unmatched_launch_apis_inside_capture': len(apis),
                           'nodes_created_in_capture': len(created),
                           'executed_graphs_with_exact_original_node_set': matching_graphs})
diagnostics = []
for source, severity, pid, text in c.execute('select source,severity,globalPid,text from DIAGNOSTIC_EVENT'):
    if any(term in text.lower() for term in ['collected', 'produced', 'hardware tracing', 'software instrumented', 'dropped', 'incomplete']):
        diagnostics.append({'source': source, 'severity': severity, 'global_pid': pid,
                            'text': re.sub(r'C:[/\\]+Users[/\\]+me', '<USER_HOME>', text)})

allowed_metadata = ['CAPTURE_EVENT_TYPE', 'DEVICE_TYPE', 'CUDA_GRAPH_TRACE_OPTIONS:MODE', 'CUDA_FLUSH_PERIOD', 'CUDA_SKIP_SOME_API_CALLS', 'RUN_DURATION_MS']
metadata = {}
for name in allowed_metadata:
    rows = list(c.execute('select value from META_DATA_CAPTURE where name=?', (name,)))
    metadata[name] = [row[0] for row in rows]

measured = [r for r in json.loads((p / 'P025-short-profile/runs.json').read_text()) if not r['warmup']]
result = {'sqlite_sha256': hashlib.sha256(db.read_bytes()).hexdigest(), 'capture_settings_allowlist': metadata,
          'kernel_records': kernel_count, 'invalid_kernel_intervals': invalid_intervals,
          'graph_launch_apis': len(graph_apis), 'graph_launch_activity_keys': len(graph_keys),
          'graph_apis_without_kernel_records': len(graph_apis - graph_keys),
          'graph_activity_keys_without_launch_api': len(graph_keys - graph_apis),
          'graph_cohorts': graph_summary, 'direct_kernel_activity_keys': len(direct),
          'direct_launch_api_keys': len(direct_apis), 'direct_launch_apis_without_kernel_record_by_name': dict(unmatched),
          'capture_api_reconciliation': capture_proofs,
          'direct_kernel_records_without_matching_launch_api': len(direct - set(direct_apis)),
          'nonzero_launch_api_returns': nonzero_launch_returns, 'selected_diagnostics': diagnostics,
          'measured_request_timings': [r['timings'] for r in measured],
          'limitation': 'Internal consistency is not independent proof of all expected kernel or memory activity. Uniformly absent records can pass cohort equality. No performance qualification follows from this instrumented capture.'}
(p / 'P025-coverage-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
