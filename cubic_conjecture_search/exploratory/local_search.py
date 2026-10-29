import json
import random
import sys
import time
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model


def trilobite(k):
    g=nx.Graph()
    for i in range(k+2):
        g.add_nodes_from((i,j) for j in range(3))
        if i:
            g.add_edges_from(((i-1,j),(i,j)) for j in range(3))
        if i in (0,k+1):
            for a in (3,4):
                g.add_edges_from(((i,a),(i,j)) for j in range(3))
        else:
            g.add_edges_from(((i,3),(i,j)) for j in range(3))
    return nx.convert_node_labels_to_integers(g)


def optimize(g,limit=1):
    m=cp_model.CpModel();x=[m.new_bool_var(str(v)) for v in g]
    for v in g:
        m.add(sum(x[u] for u in g[v])==2).only_enforce_if(x[v])
    m.maximize(sum(x));s=cp_model.CpSolver()
    s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=limit
    st=s.solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise RuntimeError(s.status_name(st))
    chosen=[v for v in g if s.value(x[v])]
    assert all(d==2 for _,d in g.subgraph(chosen).degree())
    return len(chosen),s.best_objective_bound,chosen,st==cp_model.OPTIMAL


def mutate(g,rng,count=1):
    h=g.copy()
    for _ in range(count):
        for trial in range(100):
            (a,b),(c,d)=rng.sample(list(h.edges()),2)
            if rng.randrange(2):c,d=d,c
            if len({a,b,c,d})<4 or h.has_edge(a,c) or h.has_edge(b,d):continue
            h.remove_edges_from([(a,b),(c,d)]);h.add_edges_from([(a,c),(b,d)]);break
    return h


def main():
    k=int(sys.argv[1]);steps=int(sys.argv[2]) if len(sys.argv)>2 else 2000
    rng=random.Random(261026+k);g=trilobite(k);n=len(g)
    val,upper,chosen,exact=optimize(g)
    best=val;bestg=g.copy();records=[];start=time.monotonic()
    print('start',n,val,upper,flush=True)
    for step in range(steps):
        h=mutate(g,rng,1 if rng.random()<.9 else 2)
        nv,nu,nc,ne=optimize(h)
        if nu<n/2:
            record={'order':n,'value':nv,'upper_bound':nu,'chosen':nc,'edges':list(h.edges()),'exact':ne}
            Path(f'tmp/cubic_full/counterexample_{n}.json').write_text(json.dumps(record,indent=2))
            print('COUNTEREXAMPLE',record,flush=True);return
        if nv<best:
            best=nv;bestg=h.copy()
            print('new best',step,best,nu,flush=True)
            records.append({'step':step,'value':nv,'upper_bound':nu,'edges':list(h.edges()),'exact':ne})
        if nv<=val or (nv==val+1 and rng.random()<.003):g=h;val=nv
        if step%200==199:
            print('step',step+1,'current',val,'best',best,'seconds',round(time.monotonic()-start,1),flush=True)
        if step%500==499:g=bestg.copy();val=best
    Path(f'tmp/cubic_full/local_search_{n}.json').write_text(json.dumps({'order':n,'steps':steps,'best':best,'records':records},indent=2))
    print('DONE',n,'best',best,flush=True)


if __name__=='__main__':main()
