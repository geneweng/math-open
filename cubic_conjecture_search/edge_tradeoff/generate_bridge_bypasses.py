import networkx as nx,json,itertools
from pathlib import Path
from ortools.sat.python import cp_model
codes=Path('cubic_conjecture_search/round30_data/extension_parents.g6').read_text().split();G=nx.from_graph6_bytes(codes[2].encode());bridge=list(nx.bridges(G))[0];B=G.copy();B.remove_edge(*bridge);vs=sorted(nx.connected_components(B),key=min);H=B.subgraph(vs[0]).copy();es={tuple(sorted(e)) for e in H.edges()};reps=[]
while es:
 e=min(es);reps.append(e)
 for aut in nx.algorithms.isomorphism.GraphMatcher(H,H).isomorphisms_iter():es.discard(tuple(sorted(aut[v] for v in e)))
print('edge orbit representatives',reps,flush=True)
J=B.subgraph(vs[1]).copy();gm=nx.algorithms.isomorphism.GraphMatcher(H,J);assert gm.is_isomorphic();iso=gm.mapping

def opt(g,force=(),forbid=()):
 m=cp_model.CpModel();x={v:m.new_bool_var(str(v)) for v in g}
 for v in g:m.add(sum(x[u] for u in g[v])==2).only_enforce_if(x[v])
 for v in force:m.add(x[v]==1)
 for v in forbid:m.add(x[v]==0)
 m.maximize(sum(x.values()));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=15;s.parameters.num_search_workers=1;status=s.solve(m);assert status==cp_model.OPTIMAL
 return dict(value=round(s.objective_value),witness=[v for v in g if s.value(x[v])])
rows=[]
for i,e in enumerate(reps):
 for f0 in reps[i:]:
  f=tuple(iso[v] for v in f0);g=G.copy();g.remove_edges_from([e,f]);g.add_edges_from([(e[0],26),(e[1],26),(f[0],27),(f[1],27),(26,27)])
  minus=g.copy();minus.remove_edge(*bridge)
  U=opt(minus);T=opt(g,force=bridge);W=opt(g,forbid=bridge)
  r=dict(edges=[e,f],graph6=nx.to_graph6_bytes(g,header=False).decode().strip(),edge=bridge,U=U,T=T,W=W);rows.append(r)
  print(e,f,'U T W',U['value'],T['value'],W['value'],flush=True)
Path('cubic_conjecture_search/edge_tradeoff/bridge_bypasses.json').write_text(json.dumps(rows,indent=2)+'\n')
