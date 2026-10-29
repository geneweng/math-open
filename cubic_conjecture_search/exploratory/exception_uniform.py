"""Append a fixed uniform-assembly check, idempotently."""
import json
import networkx as nx
from exception_assemblies import solve,expand,LIB,DATA
p=DATA/'assemblies.json';d=json.loads(p.read_text());d['records']=[r for r in d['records'] if not r.get('uniform')]
for n in [4,6,8,10,12,16,20]:
 g=nx.complete_graph(4) if n==4 else nx.circular_ladder_graph(n//2)
 assert all(d==3 for _,d in g.degree())
 ns={v:sorted(g[v]) for v in g};pairs=[(3*u+ns[u].index(v),3*v+ns[v].index(u)) for u,v in g.edges()]
 for rid in range(len(LIB)):
  choices=[rid]*n;r=solve(choices,pairs);r.update(blocks=n,uniform=True,choices=choices,pairs=pairs)
  if 'states' in r:
   a,w=expand(choices,pairs,r['states']);r.update(order=len(a),witness=w);assert 2*len(w)-len(a)==r['score']
  d['records'].append(r)
p.write_text(json.dumps(d,indent=2)+'\n');print('records',len(d['records']))
