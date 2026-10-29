"""Full vertex-subset enumeration for a 22-vertex extremal example."""
import json
from collections import Counter
from pathlib import Path
from verify_round12 import decode,connected_cubic

ROOT=Path(__file__).resolve().parent
code,stored,_=(ROOT/'round30_data/minimum_example.txt').read_text().split()
a,es=decode(code);connected_cubic(a);assert len(a)==22
adj=[sum(1<<v for v in ns) for ns in a];hist=Counter();best=0;witness=0
for s in range(1<<22):
    t=s;ok=True
    while t:
        bit=t&-t;v=bit.bit_length()-1;t-=bit
        if (adj[v]&s).bit_count()!=2:ok=False;break
    if ok:
        size=s.bit_count();hist[size]+=1
        if size>best:best=size;witness=s
assert best==12 and int(stored).bit_count()==12
assert all((adj[v]&int(stored)).bit_count()==2 for v in range(22) if int(stored)>>v&1)
result=dict(graph6=code,edges=es,vertex_subsets_checked=1<<22,maximum=best,
            maximum_witness=[v for v in range(22) if witness>>v&1],
            good_set_size_histogram=dict(sorted(hist.items())),
            original_conjecture='unresolved',
            scope='Exact optimum for this one graph. Universal order-22 lower bound is checked separately.')
(ROOT/'round30_minimum_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
