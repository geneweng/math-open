"""Reproduce the larger sharp inputs used in continuation 18."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_bridge_reduction import cap,franklin,edges,graph
from verify_round12 import decode
from verify_round14 import cycle_space_good_sets
from rooted_synthesis import encode

r=franklin();r[2].remove(4);r[4].remove(2)
es=[]
for i in range(3):
    es.extend((12*i+u,12*i+v) for u,v in edges(r))
    es.append((12*i+4,12*((i+1)%3)+2))
ring=graph(36,es)
code=(ROOT/'round15_data/tight_large_bases.g6').read_text().splitlines()[-1]
base,_=decode(code)
stable=None
for u,v in edges(base):
    a=[s.copy() for s in base];a[u].remove(v);a[v].remove(u)
    if max(map(int.bit_count,cycle_space_good_sets(a)))==13:
        stable=(u,v);break
assert stable is not None
u,v=stable;inflated=[s.copy() for s in base]+[{26+x for x in ns} for ns in r]
inflated[u].remove(v);inflated[v].remove(u)
for x,y in ((u,28),(v,30)):inflated[x].add(y);inflated[y].add(x)
p=cap();es=[(0,1),(1,2),(0,2)]
for i in range(3):
    off=3+13*i
    es.extend((off+u,off+v) for u,v in edges(p));es.append((i,off+12))
star=graph(42,es)
data=ROOT/'round18_data';data.mkdir(exist_ok=True)
(data/'large_seeds.g6').write_text('\n'.join(map(encode,(ring,inflated,star)))+'\n')
(data/'large_seed_constructions.json').write_text(json.dumps(dict(
    orders=[36,38,42], constructions=['Three copies of R in a ring',
    'Insert R in a deletion-stable edge of the sharp 26-vertex double',
    'A triangle joined to three copies of P'],
    inflated_base_graph6=code,stable_edge=stable,deleted_base_optimum=13),indent=2)+'\n')
