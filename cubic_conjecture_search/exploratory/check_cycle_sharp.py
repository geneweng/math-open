"""Independent CP-SAT checks of the sharp cyclic assemblies."""
import json
import sys
from pathlib import Path
from ortools.sat.python import cp_model
import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_round12 import decode
from verify_bridge_reduction import franklin,edges

records=json.loads((ROOT/'round28_data/sharp.json').read_text())
for r in records:
    a,_=decode(r['graph6']);n=len(a)
    model=cp_model.CpModel();x=[model.NewBoolVar(f'x{v}') for v in range(n)]
    for v in range(n):model.Add(sum(x[u] for u in a[v])==2).OnlyEnforceIf(x[v])
    model.Add(sum(x)>=n//2+1)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=10
    solver.parameters.num_search_workers=1
    status=solver.Solve(model);r['strict_status']=solver.StatusName(status)
    assert status!=cp_model.OPTIMAL and status!=cp_model.FEASIBLE
    model=cp_model.CpModel();x=[model.NewBoolVar(f'x{v}') for v in range(n)]
    for v in range(n):model.Add(sum(x[u] for u in a[v])==1+x[v])
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=10
    solver.parameters.num_search_workers=1
    status=solver.Solve(model);r['partition_status']=solver.StatusName(status)
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        r['colours']=[solver.Value(v) for v in x]
    gm=nx.algorithms.isomorphism.GraphMatcher(nx.Graph(edges(a)),nx.Graph(edges(franklin())))
    if gm.is_isomorphic():r['franklin_isomorphism']=[gm.mapping[i] for i in range(n)]
    print(n,r['strict_status'],r['partition_status'],flush=True)
(ROOT/'round28_data/sharp_checks.json').write_text(json.dumps(records,indent=2)+'\n')
