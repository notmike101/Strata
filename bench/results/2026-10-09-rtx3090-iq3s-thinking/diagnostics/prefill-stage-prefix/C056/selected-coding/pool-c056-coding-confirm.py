"""Same audited pooling, expanded to the one predeclared confirmation pair."""
from pathlib import Path
source=Path(__file__).with_name('pool-c056-coding.py').read_text()
changes={
    "'R125-coding-control-reverse']": "'R125-coding-control-reverse','R126-coding-control-confirm','R127-coding-prefix-confirm']",
    "['0','1','1','0']": "['0','1','1','0','0','1']",
    "[['short','longer']]*2+[['longer','short']]*2": "[['short','longer']]*2+[['longer','short']]*2+[['short','longer']]*2",
    'armrows[0]+armrows[3],armrows[1]+armrows[2]': 'armrows[0]+armrows[3]+armrows[4],armrows[1]+armrows[2]+armrows[5]',
    'c056-coding-pooled.json': 'c056-coding-confirmed.json',
}
for old,new in changes.items():
    assert source.count(old)==1,old
    source=source.replace(old,new)
exec(compile(source,str(Path(__file__).with_name('pool-c056-coding.py')),'exec'))
