"""Read only Q6 kernel launch geometry and durations from the local P025 trace."""
import json
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

p = Path(__file__).parent
c = sqlite3.connect((p / 'P025-decode.sqlite').resolve().as_uri() + '?mode=ro', uri=True)
rows = defaultdict(list)
for name, gx, gy, gz, bx, by, bz, regs, start, end in c.execute(
        "select s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,"
        "k.registersPerThread,k.start,k.end from CUPTI_ACTIVITY_KIND_KERNEL k "
        "join StringIds s on s.id=k.demangledName "
        "where s.value like '%native_q6_k_mmvq_kernel%' or s.value like '%Q6KTraits%' or s.value like '%IlQ6K%'"):
    rows[name, gx, gy, gz, bx, by, bz, regs].append((end - start) / 1000)
result = {'trace': 'P025-decode.sqlite', 'scope': 'Instrumented durations; overlapping costs are not request critical-path shares.',
          'cohorts': []}
for key, durations in sorted(rows.items(), key=lambda kv: -sum(kv[1])):
    name, gx, gy, gz, bx, by, bz, regs = key
    result['cohorts'].append({'name': name, 'grid': [gx, gy, gz], 'block': [bx, by, bz],
                              'registers_per_thread': regs, 'count': len(durations),
                              'sum_ms': sum(durations) / 1000,
                              'median_us': statistics.median(durations),
                              'min_us': min(durations), 'max_us': max(durations)})
(p / 'P025-q6-shapes.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
