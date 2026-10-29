import json
import random
import sys
import time
from pathlib import Path

import networkx as nx
sys.path.insert(0,'cubic_conjecture_search/exploratory')
from local_search import optimize,mutate


def franklin():
    return nx.LCF_graph(12,[5,-5],6)


def cap():
    g=franklin();g.remove_edge(0,1);g.add_edges_from([(0,12),(1,12)]);return g


def initial(n):
    if n==24:
        g=nx.disjoint_union(franklin(),franklin())
        g.remove_edges_from([(0,1),(12,13)]);g.add_edges_from([(0,12),(1,13)])
    elif n==26:
        g=nx.disjoint_union(cap(),cap());g.add_edge(12,25)
    elif n==42:
        g=nx.complete_graph(3)
        for v in range(3):
            offset=len(g);g=nx.disjoint_union(g,cap());g.add_edge(v,offset+12)
    else:raise ValueError(n)
    assert len(g)==n and nx.is_connected(g) and all(d==3 for _,d in g.degree())
    return g


if __name__=='__main__':
    n=int(sys.argv[1]);steps=int(sys.argv[2]);rng=random.Random(20261027+n)
    g=initial(n);start=time.monotonic();val,ub,chosen,exact=optimize(g,10)
    print('initial',n,val,ub,exact,flush=True)
    baseline=g.copy();best=val;accepted=0;unknown=0;checked=0
    records=[];found=False
    for step in range(steps):
        h=mutate(g,rng,1 if rng.random()<.9 else 2)
        nv,nu,nc,ne=optimize(h,.3);checked+=1
        if not ne:unknown+=1
        if nu<n/2:
            r={'order':n,'value':nv,'upper_bound':nu,'edges':list(h.edges()),'chosen':nc,'exact':ne,'step':step}
            Path(f'tmp/cubic_continue/counterexample{n}.json').write_text(json.dumps(r,indent=2))
            found=True;print('COUNTEREXAMPLE',r,flush=True);break
        if nv<best:
            best=nv;records.append({'step':step,'value':nv,'upper_bound':nu,'exact':ne,'edges':list(h.edges())})
            print('new best',n,step,best,nu,flush=True)
        if ne and nv<=val:g=h;val=nv;accepted+=1
        if step%500==499:print('progress',n,step+1,'best',best,'accepted',accepted,'not_optimal',unknown,'seconds',round(time.monotonic()-start,1),flush=True)
    result={'order':n,'checked':checked,'best_feasible_size':best,'accepted':accepted,'not_optimal':unknown,'records':records,'counterexample_found':found}
    Path(f'tmp/cubic_continue/tight_local{n}.json').write_text(json.dumps(result,indent=2))
    print('done',result,flush=True)
