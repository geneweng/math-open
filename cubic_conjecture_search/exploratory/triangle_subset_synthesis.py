r"""Simultaneous edge-triangle replacements aimed at the ORIGINAL conjecture.

For every Eulerian edge set F of a cubic base, write R=V(F), let X be
the chords E(G[R])\F, and let C be the edge boundary of R. X is a matching.
If A is the set of expanded edges, this state is feasible iff X <= A,
and its best branch score is |R|+2*(|A|-|A intersect C|-|X|).
Taking the maximum over F is the exact optimum, not a relaxation.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_round12 import decode


def states(a,es):
    n=len(a);m=len(es)
    adj=[sum(1<<u for u in ns) for ns in a]
    incident=[sum(1<<i for i,e in enumerate(es) if v in e) for v in range(n)]
    parent=[-1]*n;parent[0]=0;pe=[0]*n;depth=[0]*n;tree=set();queue=[0]
    for v in queue:
        for i,(u,w) in enumerate(es):
            if v!=u and v!=w:continue
            x=u^w^v
            if parent[x]>=0:continue
            parent[x]=v;pe[x]=i;depth[x]=depth[v]+1;tree.add(i);queue.append(x)
    assert len(queue)==n
    basis=[]
    for i,(u,v) in enumerate(es):
        if i in tree:continue
        f=1<<i
        while u!=v:
            if depth[u]<depth[v]:u,v=v,u
            f^=1<<pe[u];u=parent[u]
        basis.append(f)
    assert len(basis)==m-n+1
    f=0;out=[]
    for step in range(1<<len(basis)):
        if step:f^=basis[(step&-step).bit_length()-1]
        r=sum(1<<v for v in range(n) if f&incident[v]);x=0;c=0
        for i,(u,v) in enumerate(es):
            su=r>>u&1;sv=r>>v&1
            if su and sv and not (f>>i&1):x|=1<<i
            elif su!=sv:c|=1<<i
        assert not x&c
        assert all((x&inc).bit_count()<=1 for inc in incident)
        out.append((r,x,c,f))
    return out


def exact_score(state_list,marked):
    candidates=[(r.bit_count()+2*(marked.bit_count()-(marked&c).bit_count()-x.bit_count()),i)
                for i,(r,x,c,f) in enumerate(state_list) if not x&~marked]
    return max(candidates)


def expand(a,es,marked,state):
    r,x,c,f=state;n=len(a);h=[ns.copy() for ns in a]
    chosen={v for v in range(n) if r>>v&1}
    for i,(u,v) in enumerate(es):
        if not (marked>>i&1):continue
        p=len(h);q=p+1;w=p+2;h.extend([set(),set(),set()])
        h[u].remove(v);h[v].remove(u)
        for s,t in [(u,p),(p,q),(q,v),(p,w),(q,w)]:h[s].add(t);h[t].add(s)
        if f>>i&1:chosen.update((p,q))
        elif not (r>>u&1 or r>>v&1):chosen.update((p,q,w))
    assert all(len(h[v]&chosen)==2 for v in chosen)
    return h,chosen


def solve(code,seconds):
    from ortools.sat.python import cp_model
    a,es=decode(code);n=len(a);ss=states(a,es)
    model=cp_model.CpModel();chosen=[model.new_bool_var(f'a{i}') for i in range(len(es))]
    k=sum(chosen)
    for r,x,c,f in ss:
        crossing=[chosen[i] for i in range(len(es)) if c>>i&1]
        # If every chord is expanded, this state must remain below the target.
        ct=model.add(k-2*sum(crossing)<=n//2-1-r.bit_count()+2*x.bit_count())
        if x:ct.only_enforce_if([chosen[i] for i in range(len(es)) if x>>i&1])
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=1
    solver.parameters.max_time_in_seconds=seconds;solver.parameters.random_seed=2026102815
    status=solver.solve(model)
    result=dict(graph6=code,order=n,edge_count=len(es),cycle_states=len(ss),
                status=solver.status_name(status),seconds=solver.wall_time,
                conflicts=solver.num_conflicts,branches=solver.num_branches)
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        marked=sum(1<<i for i,z in enumerate(chosen) if solver.value(z))
        value,index=exact_score(ss,marked)
        assert value<n//2+marked.bit_count()
        h,w=expand(a,es,marked,ss[index]);branches={v for v,ns in enumerate(h) if len(ns)==3}
        assert len(w&branches)==value
        result.update(marked=marked,branch_optimum=value,target=n//2+marked.bit_count(),
                      expanded_edges=[list(e) for i,e in enumerate(es) if marked>>i&1],
                      expanded_graph=[sorted(ns) for ns in h],good_witness=sorted(w),
                      cubic_completion_order=n+16*marked.bit_count(),
                      ORIGINAL_COUNTEREXAMPLE_CANDIDATE=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs',nargs='+',type=Path)
    p.add_argument('--seconds',type=float,default=5)
    p.add_argument('--wall-seconds',type=float,default=600)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    start=time.monotonic();seen=set();count=0
    with args.output.open('w') as out:
        for path in args.inputs:
            for code in path.read_text().splitlines():
                if code in seen:continue
                seen.add(code)
                if time.monotonic()-start>args.wall_seconds:break
                result=solve(code,args.seconds);out.write(json.dumps(result)+'\n');out.flush();count+=1
                if result.get('ORIGINAL_COUNTEREXAMPLE_CANDIDATE'):
                    print('COUNTEREXAMPLE',result,flush=True);raise SystemExit(1)
                if count%25==0 or result['status']!='INFEASIBLE':
                    print('bases',count,'last',result['status'],'seconds',round(time.monotonic()-start,2),flush=True)
            if time.monotonic()-start>args.wall_seconds:break
    print('DONE bases',count,'elapsed',round(time.monotonic()-start,2),flush=True)
