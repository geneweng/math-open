import networkx as nx,json
from pathlib import Path
from ortools.sat.python import cp_model
p=Path('cubic_conjecture_search');F=nx.from_graph6_bytes((p/'round30_data/extension_parents.g6').read_text().split()[0].encode());es=sorted(F.edges());tree={tuple(sorted(e)) for e in nx.bfs_edges(F,0)};free=[e for e in es if e not in tree];rows=[]
for mask in range(1,1<<len(free)):
 negative={e for i,e in enumerate(free) if mask>>i&1};g=nx.Graph();g.add_nodes_from(range(24))
 for u,v in es:
  sign=int((u,v) in negative)
  for s in (0,1):g.add_edge(u+12*s,v+12*(s^sign))
 assert nx.is_connected(g)
 m=cp_model.CpModel();x=[m.new_bool_var(str(v)) for v in g]
 for v in g:m.add(sum(x[u] for u in g[v])==2).only_enforce_if(x[v])
 m.maximize(sum(x));solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=10;solver.parameters.num_search_workers=1;status=solver.solve(m)
 row=dict(mask=mask,negative_edges=sorted(negative),graph6=nx.to_graph6_bytes(g,header=False).decode().strip(),status=status.name,lower=round(solver.objective_value),upper=round(solver.best_objective_bound),witness=[v for v in g if solver.value(x[v])]);rows.append(row)
 if row['lower']==12:print('SHARP?',mask,row['status'],row['upper'],'edge connectivity',nx.edge_connectivity(g),flush=True)
(p/'cover_audit/two_lifts.json').write_text(json.dumps(rows,indent=2)+'\n');print('DONE',len(rows),flush=True)
