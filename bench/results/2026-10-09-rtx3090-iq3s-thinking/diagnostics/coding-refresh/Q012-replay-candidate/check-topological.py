"""Compile a generated topological-order answer and run fixed objective tests.

Call in an isolated subprocess with a timeout. Imports, dunder access and unsafe
builtins are unavailable to generated code. This is a coding check, not a sandbox.
"""
import ast, builtins, itertools, json, random, re, sys
from pathlib import Path
text=Path(sys.argv[1]).read_text(encoding='utf-8')
blocks=re.findall(r'```(?:python)?\s*([\s\S]*?)```',text)
code=blocks[0] if blocks else text
tree=ast.parse(code)
assert tree.body and all(isinstance(n,ast.FunctionDef) for n in tree.body),'Only function definitions expected'
assert not any(isinstance(n,(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal)) for n in ast.walk(tree))
assert not any(isinstance(n,ast.Name) and n.id.startswith('__') or isinstance(n,ast.Attribute) and n.attr.startswith('_') for n in ast.walk(tree))
assert not any(n.decorator_list for n in ast.walk(tree) if isinstance(n,ast.FunctionDef))
allowed=['sorted','list','tuple','dict','len','min','max','range','enumerate','zip','reversed','int','float','str','set','ValueError','any','all','isinstance']
ns={'__builtins__':{k:getattr(builtins,k) for k in allowed}}
exec(compile(tree,'generated-topological','exec'),ns)
fn=ns['topological_order']; cases=[]

def reference(nodes,edges):
    if any(a not in nodes or b not in nodes for a,b in edges):raise ValueError()
    for order in sorted(itertools.permutations(nodes)):
        pos={v:i for i,v in enumerate(order)}
        if all(pos[a]<pos[b] for a,b in edges):return list(order)
    raise ValueError()

def check(nodes,edges):
    original_nodes=list(nodes); original_edges=list(edges)
    try: expected=reference(nodes,edges); raises=False
    except ValueError: expected=None; raises=True
    try: got=fn(nodes,edges)
    except ValueError:
        assert raises,('unexpected ValueError',nodes,edges)
    else:
        assert not raises,('expected ValueError',nodes,edges,got)
        assert got==expected,(nodes,edges,got,expected)
    assert nodes==original_nodes and edges==original_edges,'Input mutated'
    cases.append(dict(nodes=nodes,edges=edges,expected=expected,value_error=raises))

for nodes,edges in [([],[]),(['z'],[]),(['c','b','a'],[]),(['a','b','c'],[('a','c'),('a','c')]),
                    (['a','b'],[('a','b'),('b','a')]),(['a'],[('a','a')]),(['a'],[('a','x')]),
                    (['a','b','c','d'],[('a','c'),('b','c'),('c','d')])]:check(nodes,edges)
rng=random.Random(904001)
for i in range(64):
    nodes=list('abcd'); rng.shuffle(nodes)
    edges=[(a,b) for a in nodes for b in nodes if rng.random()<0.13]
    if i%4==0 and edges:edges.append(edges[0])
    check(nodes,edges)
print(json.dumps(dict(passed=True,compiled=True,cases=len(cases),test_seed=904001)))
