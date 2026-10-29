"""Exact checks for the marked-forest restriction and new rooted searches.

The original conjecture is unresolved. The search regions are not proved
infeasible. No optimization package is used in this verifier.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time

from verify_round12 import decode
from verify_round14 import cycle_space_good_sets
from verify_round16 import induced, target, score
from verify_bridge_reduction import good, good_sets

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round17_data'


def expand(a, es, marked):
    h=[s.copy() for s in a];triangles={}
    for i,(u,v) in enumerate(es):
        if not marked>>i&1:continue
        p=len(h);q=p+1;w=p+2
        h.extend([set(),set(),set()]);triangles[i]={p,q,w}
        h[u].remove(v);h[v].remove(u)
        for x,y in ((u,p),(p,q),(q,v),(p,w),(q,w)):
            h[x].add(y);h[y].add(x)
    return h,triangles


def forest_quotient(n,es,marked):
    parent=list(range(n));covered=set()
    def find(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]];v=parent[v]
        return v
    for i,(u,v) in enumerate(es):
        if marked>>i&1:
            covered.update((u,v));x,y=find(u),find(v)
            if x==y:return False,False
            parent[x]=y
    groups={find(v) for v in covered};index={r:i for i,r in enumerate(sorted(groups))}
    quotient=[(index[find(u)],index[find(v)]) for i,(u,v) in enumerate(es)
              if not marked>>i&1 and u in covered and v in covered]
    for mask in range(1,1<<len(groups)):
        internal=sum(bool(mask>>u&1 and mask>>v&1) for u,v in quotient)
        if internal>2*mask.bit_count()-1:return True,False
    return True,True


def sparsity_checks():
    codes=[s for s in (ROOT/'round8_data/cubic_through18.g6').read_text().splitlines()
           if ord(s[0])-63<=8]
    counts=Counter()
    for code in codes:
        a,es=decode(code);n=len(a);m=len(es)
        supports=[0]*(1<<m)
        for mask in range(1,1<<m):
            bit=mask&-mask;u,v=es[bit.bit_length()-1]
            supports[mask]=supports[mask^bit]|1<<u|1<<v
        inside=[sum(1<<i for i,(u,v) in enumerate(es) if s>>u&1 and s>>v&1)
                for s in range(1<<n)]
        for marked in range(1<<m):
            direct=True;subset=marked
            while subset:
                vertices=supports[subset]
                q=(inside[vertices]&~marked).bit_count()
                if 2*subset.bit_count()+q>=2*vertices.bit_count():
                    direct=False;break
                subset=(subset-1)&marked
            forest,quotient=forest_quotient(n,es,marked)
            assert direct==(forest and quotient)
            counts['markings']+=1;counts['forests']+=forest
            counts['satisfying_sparsity']+=direct
            if marked.bit_count()>3:continue
            h,triangles=expand(a,es,marked)
            subset=marked
            while subset:
                selected=set().union(*(triangles[i] for i in triangles if subset>>i&1))
                neighbours={v for v in range(n) if supports[subset]>>v&1}
                assert good(h,selected)
                assert set().union(*(h[v] for v in selected))-selected==neighbours
                reduced,old=induced(h,set(range(len(h)))-selected-neighbours)
                q=(inside[supports[subset]]&~marked).bit_count()
                assert target(h)-target(reduced)==2*len(neighbours)-q
                assert score(h,selected)==2*subset.bit_count()
                for s in good_sets(reduced):
                    lifted=selected|{old[v] for v in s}
                    assert good(h,lifted)
                    assert score(h,lifted)-score(reduced,s)>=2*subset.bit_count()
                    counts['lifts']+=1
                counts['deletions']+=1
                subset=(subset-1)&marked
    return dict(base_graphs=len(codes),**counts)


def searches():
    results=[]
    for path in sorted(DATA.glob('rooted29_*.json')):
        run=json.loads(path.read_text());assert run['status']!='running'
        seed,seed_es=decode(run['seed_graph6']);seed_edges=set(seed_es)
        profiles=[]
        for record in run['records']:
            a,es=decode(record['graph6']);n=len(a)
            assert n==29 and a[0]=={1,2}
            assert all(len(ns)==(2 if v==0 else 3) for v,ns in enumerate(a))
            assert len(seed_edges-set(es))<=run['removed_edge_radius']
            masks=cycle_space_good_sets(a)
            wa=max((s for s in masks if s&1),key=int.bit_count,default=0)
            wb=max((s for s in masks if not s&1),key=int.bit_count)
            A=wa.bit_count() if wa else -1000;B=wb.bit_count()
            assert (A,B)==(record['root_in_optimum'],record['root_out_optimum'])
            d=max(A+B,2*B);assert d==record['doubled_optimum'] and d>=n
            doubled=[s.copy() for s in a]+[{n+v for v in ns} for ns in a]
            doubled[0].add(n);doubled[n].add(0)
            first=wa if A+B>2*B else wb
            chosen={v for v in range(n) if first>>v&1}|{n+v for v in range(n) if wb>>v&1}
            assert all(len(ns)==3 for ns in doubled)
            assert good(doubled,chosen) and len(chosen)==d>=len(doubled)//2
            profiles.append(dict(graph6=record['graph6'],A=A,B=B,doubled_order=2*n,
                                 doubled_optimum=d,doubled_witness=sorted(chosen)))
        results.append(dict(file=path.name,status=run['status'],profiles=profiles,
                            scope='Bounded search ended without proving its region infeasible'))
    return results


if __name__=='__main__':
    start=time.monotonic()
    result=dict(original_conjecture_resolved=False,sparsity_checks=sparsity_checks(),searches=searches())
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(DATA.iterdir()) if p.is_file()}
    (ROOT/'round17_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='searches'},indent=2))
    print('Verified rooted candidates:',sum(len(r['profiles']) for r in result['searches']))
