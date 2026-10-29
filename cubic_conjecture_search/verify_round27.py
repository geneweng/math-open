"""Check four-port contraction certificates and independently check pair joins."""
import itertools
import json
import sys
from pathlib import Path

from verify_round26 import read_rows, check
from verify_round12 import decode
from verify_bridge_reduction import good_sets, good, graph, edges

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round27_data'
PERMS=list(itertools.permutations(range(4)))
STATES=[tuple(s//3**i%3 for i in range(4)) for s in range(81)]
MAPS=[[sum(z[p[i]]*3**i for i in range(4)) for z in STATES] for p in PERMS]


def certificate(row):
    a,_=decode(row['code']);u,v=row['removed'];ports=row['ports'];f=row['values']
    left=[i for i,p in enumerate(ports) if p in a[u]]
    right=[i for i in range(4) if i not in left]
    assert len(left)==len(right)==2
    if f[0]<-2:return None
    single=[sum(2*3**i for i in pair) for pair in (left,right)]
    if any(f[s]<0 for s in single):return None
    double={}
    for i,j in itertools.product(left,right):
        others=[t for t in range(4) if t not in (i,j)]
        candidates=[2*3**i+2*3**j+sum(3**t for h,t in enumerate(others) if mask>>h&1)
                    for mask in range(4)]
        s=max(candidates,key=lambda s:f[s])
        if f[s]<2:return None
        double[f'{i},{j}']=s
    return dict(left=left,right=right,single=single,double=double)


def main():
    large=read_rows(ROOT/'round26_data/profiles.txt')
    certs=[dict(row=i,**c) for i,r in enumerate(large) if (c:=certificate(r))]
    assert len(certs)==1945
    # Every exterior pattern occurring in every good set of K3,3 is lifted
    # through each certified fragment. This includes all four states of the
    # replaced endpoints; local inequalities handle arbitrary external graphs.
    base=graph(6,[(u,v) for u in range(3) for v in range(3,6)])
    old_u,old_v=0,3;outside=[1,2,4,5];oldsets=list(good_sets(base));lifts=0
    for c in certs:
        r=large[c['row']];a,_=decode(r['code']);ports=r['ports'];removed=set(r['removed'])
        remain=sorted(set(range(len(a)))-removed);ren={v:i for i,v in enumerate(remain)}
        q=len(remain);ext={v:q+i for i,v in enumerate(outside)}
        attachments={c['left'][0]:4,c['left'][1]:5,c['right'][0]:1,c['right'][1]:2}
        es=[(ren[u],ren[v]) for u,v in edges(a) if u in ren and v in ren]
        es += [(ext[u],ext[v]) for u,v in edges(base) if u in ext and v in ext]
        es += [(ren[ports[p]],ext[v]) for p,v in attachments.items()]
        h=graph(q+4,es);assert all(len(ns)==3 for ns in h)
        for s in oldsets:
            nsel=int(old_u in s)+int(old_v in s)
            if nsel==0:state=0
            elif nsel==1:state=c['single'][0 if old_u in s else 1]
            else:
                i=next(i for i in c['left'] if attachments[i] in s)
                j=next(j for j in c['right'] if attachments[j] in s)
                state=c['double'][f'{i},{j}']
            chosen={ren[v] for v in remain if r['witnesses'][state]>>v&1}
            chosen.update(ext[v] for v in s if v in ext)
            assert good(h,chosen) and len(chosen)>=len(s)+(q-2)//2
            lifts+=1
    print('Contraction lifts checked:',lifts,flush=True)
    rows=read_rows(DATA/'profiles.txt')
    positive=sum(check(r) for r in rows)
    expected=set()
    for code in (DATA/'small.g6').read_text().split():
        a,es=decode(code);expected.update((code,u,v) for u,v in es if not a[u]&a[v])
    assert len(rows)==9492 and {(r['code'],*r['removed']) for r in rows}==expected
    reduced=json.loads((DATA/'canonical.json').read_text())['profiles']
    for r in reduced:
        f=rows[r['row']]['values'];p=r['permutation']
        m=MAPS[PERMS.index(tuple(p))]
        assert r['values']==[f[j] for j in m]
    # Check every discarded table is dominated in a suitable port ordering.
    # This numeric comparison uses exact integers, not a solver.
    import numpy as np
    pool=np.array([[r['values'][j] for j in m] for r in reduced for m in MAPS],dtype=np.int32)
    canonical={min(tuple(r['values'][j] for j in m) for m in MAPS) for r in rows}
    for f in canonical:
        assert np.any(np.all(pool<=np.array(f,dtype=np.int32),axis=1))
    print('All profile dominations checked:',len(canonical),flush=True)
    # Independent pair check: bitsets of permissible right-hand boundary
    # states, grouped by their scores, rather than the C++ 256-pair scan.
    compatible=[[s for s,x in enumerate(STATES) if all(
        (a==0 and b<=1) or (a==1 and b==0) or (a==b==2)
        for a,b in zip(x,y))] for y in STATES]
    variants=[];levels=set()
    for r in reduced:
        group=[]
        for m in MAPS:
            byscore={}
            for t,j in enumerate(m):
                value=r['values'][j]
                if value<=-1000000:continue
                byscore[value]=byscore.get(value,0)|(1<<t);levels.add(value)
            group.append(list(byscore.items()))
        variants.append(group)
    pairs=0
    for i,r in enumerate(reduced):
        best=[max(r['values'][s] for s in ss) for ss in compatible]
        accept={v:sum(1<<t for t in range(81) if best[t]+v>=0) for v in levels}
        for group in variants[i:]:
            for scored in group:
                assert any(accept[v]&mask for v,mask in scored)
                pairs+=1
    assert pairs==18436320
    result=dict(original_conjecture='unresolved',contraction_certificates=certs,
                contraction_lifts=lifts,profiles=len(rows),positive_witnesses=positive,
                canonical_profiles=len(canonical),retained_profiles=len(reduced),
                independent_pairing_checks=pairs,
                scope='Positive witnesses, all discarded-profile dominations, and all '
                'retained pairings checked. Large-profile upper bounds are unnecessary. '
                'The contraction theorem is conditional on a simple cubic contracted graph.')
    (ROOT/'round27_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='contraction_certificates'}))


if __name__=='__main__':main()
