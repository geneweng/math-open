import json
import math
import random
from fractions import Fraction
from pathlib import Path

import networkx as nx
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from local_search import trilobite


def oracle(g,weights):
    m=cp_model.CpModel();x=[m.new_bool_var(str(v)) for v in g]
    for v in g:m.add(sum(x[u] for u in g[v])==2).only_enforce_if(x[v])
    m.maximize(sum(w*xv for w,xv in zip(weights,x)))
    s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=10
    status=s.solve(m)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return None
    selected=[v for v in g if s.value(x[v])]
    assert all(d==2 for _,d in g.subgraph(selected).degree())
    return selected,s.objective_value,s.best_objective_bound,status==cp_model.OPTIMAL


def test(g):
    assert nx.is_connected(g) and not nx.has_bridges(g)
    n=len(g);lp=pywraplp.Solver.CreateSolver('GLOP')
    w=[lp.NumVar(0,1,str(v)) for v in g];t=lp.NumVar(0,1,'t')
    norm=lp.Constraint(1,1)
    for v in g:norm.SetCoefficient(w[v],1)
    def add(vertices):
        c=lp.Constraint(-lp.infinity(),0);c.SetCoefficient(t,-1)
        for v in vertices:c.SetCoefficient(w[v],1)
    for v in g:add([v])
    lp.Minimize(t);seen=set()
    for it in range(200):
        assert lp.Solve()==lp.OPTIMAL
        bound=t.solution_value()
        if bound>=.5-1e-9:return {'status':'no_weighted_violation','iterations':it,'lp_bound':bound}
        weights=[q.solution_value() for q in w]
        result=oracle(g,weights)
        if result is None:return {'status':'oracle_unknown','iterations':it}
        selected,val,ub,exact=result
        if ub<.5-1e-7:
            rational=[Fraction(a).limit_denominator(10000) for a in weights]
            scale=math.lcm(*(a.denominator for a in rational))
            ints=[int(a*scale) for a in rational]
            if scale>=10**12:return {'status':'precision_limit'}
            check=oracle(g,ints)
            if check is not None and 2*check[2]<sum(ints):
                return {'status':'weighted_counterexample','iterations':it,'weights':ints,
                        'maximum_good_weight':check[1],'upper_bound':check[2],
                        'total_weight':sum(ints),'edges':list(g.edges()),'exact':check[3]}
        key=tuple(selected)
        if key in seen:return {'status':'duplicate_column','iterations':it,'lp_bound':bound,'oracle_bound':ub}
        seen.add(key);add(selected)
    return {'status':'iteration_limit','iterations':200}


if __name__=='__main__':
    graphs=[(f'trilobite_{k}',trilobite(k)) for k in range(1,11)]
    for n in (24,30,40):
        for i in range(20):
            g=nx.random_regular_graph(3,n,seed=20261026+n*100+i)
            if nx.is_connected(g) and not nx.has_bridges(g):graphs.append((f'random_{n}_{i}',g))
    records=[]
    for label,g in graphs:
        r=test(g);r['label']=label;r['order']=len(g);records.append(r)
        print(label,r,flush=True)
        if r['status']=='weighted_counterexample':break
    Path('tmp/cubic_full/weighted_oracle_results.json').write_text(json.dumps(records,indent=2))
