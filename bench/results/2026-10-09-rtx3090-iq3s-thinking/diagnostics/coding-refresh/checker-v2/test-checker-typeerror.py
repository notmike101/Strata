"""Regression: ordinary exception handling must retain standard Python semantics."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

p = Path(__file__).parent
a = argparse.ArgumentParser()
a.add_argument('checker', type=Path)
args = a.parse_args()
checker = args.checker.resolve()
answer = p / 'Q014-coupled-quality/coding-105.answer.txt'
result = subprocess.run([sys.executable, '-I', str(checker), str(answer)], text=True, capture_output=True, timeout=5)
assert result.returncode == 0, result.stderr
assert json.loads(result.stdout) == {'passed': True, 'compiled': True, 'cases': 72, 'test_seed': 904001}
with tempfile.TemporaryDirectory() as folder:
    f = Path(folder)/'bad-answer.txt'
    for name, source in [
        ('wrong ordering', 'def topological_order(nodes, edges):\n    return list(nodes)\n'),
        ('missing endpoint validation', 'def topological_order(nodes, edges):\n    return sorted(nodes)\n'),
        ('imports remain rejected', 'import os\ndef topological_order(nodes, edges):\n    return []\n'),
        ('dunder access remains rejected', 'def topological_order(nodes, edges):\n    return nodes.__class__\n'),
    ]:
        f.write_text(source)
        bad = subprocess.run([sys.executable, '-I', str(checker), str(f)], text=True, capture_output=True, timeout=5)
        assert bad.returncode != 0, name
print('PASS: valid exception handling and unchanged 72 cases; 4 invalid/unsafe answers rejected')
