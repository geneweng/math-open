"""Independent standard-library checks of the Petersen-pole certificates."""
import itertools
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
ES = [(2,3),(2,7),(3,4),(3,8),(4,9),(5,7),(5,8),(6,8),(6,9),(7,9)]
VS = set(range(2,10)); PORTS = {2,4,5,6}
a = {v:set() for v in VS}
for u,v in ES:a[u].add(v);a[v].add(u)
cycles = {}
for k in range(9):
    for choice in itertools.combinations(sorted(VS),k):
        s=set(choice)
        if all(len(a[v]&s)==2 for v in s):
            key=tuple(sorted(s&PORTS))
            if len(s)>len(cycles.get(key,[])):cycles[key]=list(choice)
pairs=list(itertools.combinations(sorted(PORTS),2))
assert all(len(cycles[p])>=5 for p in pairs)
# The natural smoothing pairs the neighbours of each deleted Petersen vertex.
mate={2:6,6:2,4:5,5:4}; boundary=[]
for z in itertools.product([0,1],repeat=4):
    out=dict(zip(sorted(PORTS),z)); best=-1; witness=None
    for k in range(9):
        for choice in itertools.combinations(sorted(VS),k):
            s=set(choice)
            if any(out[p] and int(p in s)!=out[mate[p]] for p in PORTS):continue
            if all(len(a[v]&s)+out.get(v,0)==2 for v in s):
                best=k;witness=list(choice)
    boundary.append(dict(outside=z,optimum=best,witness=witness))
assert all(r['optimum']>=5 for r in boundary[:-1])
assert boundary[-1]['optimum']==-1
records=json.loads((ROOT/'round19_data/petersen_examples.json').read_text())
for r in records:
    g=[set(ns) for ns in r['adjacency']]; n=len(g)
    assert n==52 and all(len(ns)==3 for ns in g)
    assert all(v not in g[v] and all(v in g[u] for u in g[v]) for v in range(n))
    seen={0};todo=[0]
    while todo:
        for u in g[todo.pop()]-seen:seen.add(u);todo.append(u)
    assert len(seen)==n
    used=set()
    for b in r['blocks']:
        b={int(k):v for k,v in b.items()};assert set(b)==VS
        image=set(b.values());assert len(image)==8 and not used&image;used|=image
        for v in VS:assert g[b[v]]&image=={b[u] for u in a[v]}
    s=set(r['witness']);assert len(s)==len(r['witness'])==r['actual_size']
    assert all(len(g[v]&s)==2 for v in s)
    assert len(s)>=5*len(r['blocks'])==30
result=dict(local_pair_cycles=[dict(ports=p,cycle=cycles[p]) for p in pairs],
            smoothing_profiles=boundary,
            examples=[dict(id=r['id'],order=r['order'],poles=len(r['blocks']),witness_size=r['actual_size']) for r in records],
            original_conjecture_resolved=False)
(ROOT/'round19_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['examples']))
