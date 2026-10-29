"""Verify direct symmetric-bridge searches; the original conjecture is open.

Positive certificates are checked on the FULL doubled cubic graphs. Exact
rooted optima use an independent vertex-assignment recursion with propagation,
rather than the search program's binary cycle-space enumeration.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time

from verify_round12 import decode, connected_cubic, check_set
from verify_pseudoforest_repair import statistics
from verify_bridge_reduction import graph, good_sets

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'round13_data'


def vertex_profiles(a,root):
    n=len(a);full=(1<<n)-1;adj=[sum(1<<u for u in ns) for ns in a]
    maxima=[0,-1000];counts=[0,0];nodes=0
    def visit(yes,no):
        nonlocal nodes
        nodes+=1
        while True:
            old=(yes,no);unknown=full^(yes|no)
            for v,ns in enumerate(adj):
                if no>>v&1:continue
                selected=(yes&ns).bit_count();free=ns&unknown
                if selected>2 or selected+free.bit_count()<2:
                    if yes>>v&1:return
                    no|=1<<v
                elif yes>>v&1:
                    if selected==2:no|=free
                    elif selected+free.bit_count()==2:yes|=free
                if yes&no:return
                unknown=full^(yes|no)
            if old==(yes,no):break
        if not unknown:
            score=yes.bit_count();side=int(bool(yes>>root&1))
            if score>maxima[side]:maxima[side]=score;counts[side]=1
            elif score==maxima[side]:counts[side]+=1
            return
        # Prefer a vertex near already selected vertices, to expose constraints.
        vertices=[v for v in range(n) if unknown>>v&1]
        v=max(vertices,key=lambda v:((adj[v]&yes).bit_count(),-(adj[v]&unknown).bit_count(),-v))
        visit(yes|(1<<v),no);visit(yes,no|(1<<v))
    visit(0,0)
    return dict(A=maxima[1],B=maxima[0],A_count=counts[1],B_count=counts[0],nodes=nodes)


def double(a,root,inside,outside,A,B):
    n=len(a)
    h=[ns.copy() for ns in a]+[{n+u for u in ns} for ns in a]
    h[root].add(n+root);h[n+root].add(root)
    if A+B>2*B:chosen=set(inside)|{n+v for v in outside}
    else:chosen=set(outside)|{n+v for v in outside}
    connected_cubic(h);check_set(h,chosen,n)
    assert len(chosen)==max(A+B,2*B)
    return len(chosen)


def search_certificates():
    totals=Counter();orders=Counter();unique=set();exact_cache={};exact_rows=[]
    for line in (DATA/'cap_candidates.txt').open():
        rs,code,As,Bs,was,wbs,ex=line.split()
        root,A,B,wa,wb,exact=map(int,(rs,As,Bs,was,wbs,ex))
        a,_=decode(code);n=len(a);assert n%2==1
        assert all(len(ns)==(2 if v==root else 3) for v,ns in enumerate(a))
        assert 0<=wa<1<<n and 0<=wb<1<<n
        inside=[v for v in range(n) if wa>>v&1]
        outside=[v for v in range(n) if wb>>v&1]
        assert root not in outside and len(outside)==B
        check_set(a,outside,B)
        if A!=-1000:
            assert root in inside and len(inside)==A;check_set(a,inside,A)
        else:assert wa==0
        double(a,root,inside,outside,A,B)
        if exact:
            key=(code,root)
            if key not in exact_cache:
                r=vertex_profiles(a,root);exact_cache[key]=r
                assert r['A']==A and r['B']==B
                exact_rows.append(dict(graph6=code,root=root,**r))
            totals['exact_profiles']+=1
        else:
            assert max(A+B,2*B)>n
            totals['positive_early_exits']+=1
        totals['proposals']+=1;orders[n]+=1;unique.add((code,root))
        if totals['proposals']%5000==0:print('Verified proposals',totals['proposals'],flush=True)
    assert totals['proposals']==20000 and totals['exact_profiles']==155
    assert totals['positive_early_exits']==19845
    return dict(**totals,unique_labelled_rooted_graphs=len(unique),
                cap_orders=dict(orders),cubic_orders=[2*n for n in sorted(orders)],
                distinct_exact_profiles_checked=len(exact_cache),
                exact_checks=exact_rows)


def symmetrization():
    count=0
    # -1000 encodes infeasible root-in state in this bounded algebra check.
    profiles=[(a,b) for a in [-1000,*range(9)] for b in range(9)]
    for a,b in profiles:
        for c,d in profiles:
            j=max(b+d,a+d,b+c)
            d1=max(2*b,a+b);d2=max(2*d,c+d)
            assert j==b+d+max(0,a-b,c-d)
            assert 2*j>=d1+d2
            count+=1
    return dict(abstract_profile_pairs_checked=count)


def check_vertex_recursion():
    checked=0
    for n in range(1,6):
        pairs=list(itertools.combinations(range(n),2))
        for bits in range(1<<len(pairs)):
            a=graph(n,[e for i,e in enumerate(pairs) if bits>>i&1])
            if max(map(len,a))>3:continue
            sets=list(good_sets(a))
            for root in range(n):
                inside=[len(s) for s in sets if root in s]
                outside=[len(s) for s in sets if root not in s]
                A=max(inside,default=-1000);B=max(outside)
                r=vertex_profiles(a,root)
                assert (r['A'],r['B'],r['A_count'],r['B_count'])==(A,B,inside.count(A),outside.count(B))
                checked+=1
    return dict(brute_force_crosschecked_rooted_graphs=checked)


def failed_loss_estimate():
    code='S??????_E?M?QC@cOg@W?Gg?@g?e??p??'
    a,es=decode(code);connected_cubic(a);factor=1009045269
    st=statistics(len(a),es,factor)
    # Direct enumeration of all vertex subsets is independent of the search.
    adj=[sum(1<<u for u in ns) for ns in a];optimum=0;witness=0
    for mask in range(1<<len(a)):
        if mask.bit_count()<=optimum:continue
        todo=mask;valid=True
        while todo:
            bit=todo&-todo;todo-=bit;v=bit.bit_length()-1
            if (adj[v]&mask).bit_count()!=2:valid=False;break
        if valid:optimum=mask.bit_count();witness=mask
    assert len(st['leaves'])==15 and st['isolated']==1
    assert optimum==12<15-2
    check_set(a,[v for v in range(len(a)) if witness>>v&1],len(a)//2)
    return dict(graph6=code,order=len(a),factor=factor,
                factor_edge_order='graph6: increasing upper endpoint, then lower endpoint',
                leaves=st['leaves'],isolated_edges=st['isolated'],c_ind=optimum,
                proposed_bound=13,good_witness_mask=witness,
                vertex_subsets_checked=1<<len(a),counterexample_to_original=False)


def main():
    start=time.monotonic()
    r=dict(original_conjecture_resolved=False,
           search=search_certificates(),symmetrization=symmetrization(),
           failed_auxiliary_loss_estimate=failed_loss_estimate(),
           vertex_recursion_crosscheck=check_vertex_recursion())
    r['elapsed_seconds']=time.monotonic()-start
    r['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.iterdir()) if p.is_file()}
    (ROOT/'round13_verification.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='search'},indent=2))


if __name__=='__main__':main()
