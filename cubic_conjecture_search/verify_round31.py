"""Independent finite checks for the unbounded two-edge-extension loss theorem.
The infinite-family upper bound is proved in the paper, not inferred from scans.
"""
from collections import Counter
from pathlib import Path
import json
from verify_round12 import decode, connected_cubic
from verify_round30_extensions import extend
ROOT=Path(__file__).resolve().parent


def good(a,s):
    return all((a[v]&s).bit_count()==2 for v in range(len(a)) if s>>v&1)


def exhaustive(a):
    hist=Counter();best=0
    for s in range(1<<len(a)):
        if good(a,s):
            hist[s.bit_count()]+=1
            if s.bit_count()>best.bit_count():best=s
    return dict(maximum=best.bit_count(),witness=best,histogram=dict(sorted(hist.items())),subsets=1<<len(a))


def cap():
    # Triangles (0,1,2), (3,4,5), matching 03,14,25; subdivide 01 by root 6.
    es=[(0,2),(1,2),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5),(0,6),(1,6)]
    a=[0]*7
    for u,v in es:a[u]|=1<<v;a[v]|=1<<u
    return a


def decorated(core):
    q=cap();a=core.copy();n=len(core)
    for v in range(n):
        for _ in range(3-core[v].bit_count()):
            start=len(a);a.extend(mask<<start for mask in q)
            a[v]|=1<<(start+6);a[start+6]|=1<<v
    return a


def cycle(n):return [(1<<((v-1)%n))|(1<<((v+1)%n)) for v in range(n)]


def as_sets(a):return [{u for u in range(len(a)) if mask>>u&1} for mask in a]


def main():
    q=cap();root=6;gs=[s for s in range(128) if good(q,s)]
    avoid=max((s for s in gs if not s>>root&1),key=int.bit_count)
    contain=max((s for s in gs if s>>root&1),key=int.bit_count)
    assert avoid.bit_count()==contain.bit_count()==5
    # Independently check the exact extension identity's concrete failures.
    examples=[]
    for code,e,f in [('K?ABCN_U?wF?',(0,7),(3,10)),('O???C@_sAaSGIGB_@o?k?',(0,7),(8,12))]:
        adj,_=decode(code);a=[sum(1<<v for v in ns) for ns in adj]
        b=extend(a,e,f);connected_cubic(adj);connected_cubic(as_sets(b))
        before=exhaustive(a);after=exhaustive(b)
        assert after['maximum']<before['maximum']
        assert after['maximum']>=len(b)//2
        examples.append(dict(graph6=code,edges=[e,f],before=before,after=after))
    # Check the theta core exhaustively, independently of the claimed formula.
    cores=[]
    for n in range(4,19):
        for d in range(2,n//2+1):
            b=extend(cycle(n),(0,1),(d,d+1))
            actual=exhaustive(b)
            assert actual['maximum']==max(d,n-d)+2
            cores.append(dict(order=n,separation=d,maximum=actual['maximum']))
    # Explicit whole-graph witnesses for an increasing family, without relying on a solver.
    family=[]
    for k in range(2,101):
        n=2*k;a=decorated(cycle(n));b=extend(a,(0,1),(k,k+1))
        connected_cubic(as_sets(a));connected_cubic(as_sets(b))
        caps=sum(avoid<<(n+7*v) for v in range(n))
        s=caps|((1<<n)-1)
        t=caps|sum(1<<v for v in range(1,k+1))|(1<<len(a))|(1<<(len(a)+1))
        assert good(a,s) and s.bit_count()==12*k
        assert good(b,t) and t.bit_count()==11*k+2
        assert len(a)==16*k and len(b)==16*k+2
        family.append(dict(k=k,order_before=len(a),order_after=len(b),size_before=s.bit_count(),size_after=t.bit_count(),loss=k-2))
    result=dict(original_conjecture='unresolved',cap=dict(adjacency=q,root=root,root_out_mask=avoid,root_in_mask=contain,maximum=5),
                exhaustive_examples=examples,exhaustive_theta_cores=cores,whole_graph_witnesses=family,
                scope='The infinite-family optima follow from bridge separation and the theta-core proof. The finite checks support that proof; they do not settle the original conjecture.')
    (ROOT/'round31_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('VERIFIED cap; exact examples',[(r['before']['maximum'],r['after']['maximum']) for r in examples],'; theta cores',len(cores),'; family witnesses',len(family))

if __name__=='__main__':main()
