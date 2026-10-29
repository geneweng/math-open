import itertools
import json
import random
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model
from local_search import trilobite


def profile(g,deleted):
    ports=list(g[deleted]);h=g.copy();h.remove_node(deleted);rows=[]
    for states in itertools.product(range(3),repeat=3):
        if states.count(2)%2:continue
        m=cp_model.CpModel();x={v:m.new_bool_var(str(v)) for v in h}
        for v in h:
            if v in ports:
                st=states[ports.index(v)]
                m.add(x[v]==int(st>0))
                if st:m.add(sum(x[u] for u in h[v])==3-st)
            else:m.add(sum(x[u] for u in h[v])==2).only_enforce_if(x[v])
        m.maximize(sum(x.values()));s=cp_model.CpSolver();s.parameters.num_search_workers=1
        st=s.solve(m)
        if st==cp_model.INFEASIBLE:continue
        assert st==cp_model.OPTIMAL
        rows.append([*states,2*int(s.objective_value)-len(h)])
    return rows


def solve(g,profiles,choices,rng):
    m=cp_model.CpModel();states={};scores=[];port_orders={}
    for v in g:
        neighbors=list(g[v]);rng.shuffle(neighbors);port_orders[v]=neighbors
        xs=[m.new_int_var(0,2,f'{v}_{j}') for j in range(3)]
        rows=profiles[choices[v]]['rows'];score=m.new_int_var(min(r[3] for r in rows),max(r[3] for r in rows),f'w{v}')
        scores.append(score);m.add_allowed_assignments([*xs,score],rows)
        for u,x in zip(neighbors,xs):states[v,u]=x
    for u,v in g.edges():m.add_allowed_assignments([states[u,v],states[v,u]],[(0,0),(0,1),(1,0),(2,2)])
    m.maximize(sum(scores));s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=2
    st=s.solve(m)
    if st not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return None
    return {'value':s.objective_value,'upper_bound':s.best_objective_bound,'optimal':st==cp_model.OPTIMAL,'port_orders':port_orders}


if __name__=='__main__':
    profiles=[];seen=set()
    for k in range(1,9):
        for deleted in (0,3):
            rows=profile(trilobite(k),deleted);key=tuple(tuple(r) for r in rows)
            if key not in seen:
                seen.add(key);profiles.append({'k':k,'deleted':deleted,'order':9+4*k,'rows':rows})
    print('distinct profiles',len(profiles),[(p['k'],p['deleted']) for p in profiles],flush=True)
    Path('tmp/cubic_full/three_port_profiles.json').write_text(json.dumps(profiles,indent=2))
    rng=random.Random(20261026);best=100;records=[];checked=0
    for n in (4,6,8,10,12,16,20):
        for trial in range(100):
            seed=rng.randrange(2**31);g=nx.random_regular_graph(3,n,seed=seed)
            choices=[rng.randrange(len(profiles)) for v in g]
            result=solve(g,profiles,choices,rng)
            if result is None:continue
            checked+=1
            if result['value']<best:best=result['value'];print('new best',n,trial,best,result['upper_bound'],flush=True)
            if result['upper_bound']<0:
                record={'base_edges':list(g.edges()),'choices':choices,'profiles':profiles,**result}
                Path('tmp/cubic_full/three_port_counterexample.json').write_text(json.dumps(record,indent=2))
                print('COUNTEREXAMPLE',record,flush=True);raise SystemExit
        print('done',n,'checked',checked,'best',best,flush=True)
    Path('tmp/cubic_full/three_port_results.json').write_text(json.dumps({'checked':checked,'minimum_found_surplus':best,'counterexample_found':False},indent=2))
