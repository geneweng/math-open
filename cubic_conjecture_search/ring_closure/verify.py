"""Independent finite certificate for an infinite ring-assembly theorem.

No optimization solver. Uses genuine -infinity via None, validates every
finite source lower bound by a vertex witness, checks all 100 products,
and exhaustively checks the small cap and representative theta cores.
"""
import itertools
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from verify_bridge_reduction import cap, good_sets, graph, edges, complete, good
from verify_round12 import decode


def add(a,b):return None if a is None or b is None else a+b
def maximum(values):return max((x for x in values if x is not None),default=None)
def lower(a,b):return all(x is None or (y is not None and x<=y) for x,y in zip(a,b))


def multiply(a,b):
    # The connecting ports may be 00, 01, or 10 in the closed channel.
    out=[]
    for left,right in itertools.product((0,1),repeat=2):
        out.append(maximum([add(a[2*left],b[right]),
                            add(a[2*left],b[2+right]),
                            add(a[2*left+1],b[right])]))
    return tuple(out+[add(a[4],b[4])])


def parse(values):return tuple(None if x==-1000000 else x for x in values)


def theta(lengths):
    es=[];n=2
    for length in lengths:
        path=[0]+list(range(n,n+length-1))+[1]
        n+=length-1
        es.extend(zip(path,path[1:]))
    return graph(n,es)


def weighted_core_table(a,e,branches=frozenset((0,1)),offset=-1):
    u,v=e;b=[s.copy() for s in a];b[u].remove(v);b[v].remove(u)
    values=[None]*5
    state_index={(0,0):0,(0,1):1,(1,0):2,(1,1):3,(2,2):4}
    for mask in range(1<<len(a)):
        s={w for w in range(len(a)) if mask>>w&1};states=[0,0];ok=True
        for w in s:
            degree=len(b[w]&s)
            if w in e:
                if degree not in (1,2):ok=False;break
                states[e.index(w)]=3-degree
            elif degree!=2:ok=False;break
        if not ok:continue
        state=tuple(states)
        assert state in state_index
        score=len(s&branches)+offset
        j=state_index[state];values[j]=maximum([values[j],score])
    return tuple(values)


def main():
    data=json.loads((HERE/'invariant.json').read_text())
    assert data['complete'] is True
    source=json.loads((ROOT/'boundary_profile_checks.json').read_text())['records']
    bykey={(r['graph6'],tuple(r['ports'])):r for r in source}
    states=[(0,0),(0,1),(1,0),(1,1),(2,2)]
    generators=[];positive_witnesses=0
    templates={'theta_direct_edge':(-1,None,None,1,1),
               'theta_branch_internal':(-1,None,1,None,1),
               'theta_internal_internal':(1,None,None,None,1),
               'two_disjoint_P13_caps':(-1,0,0,1,None),
               'completed_cycle_edge':(0,None,None,None,0)}
    for rec in data['generators']:
        expected=parse(rec['profile']);src=rec['source']
        if isinstance(src,list):
            code,u,v=src;ports=(int(u),int(v));row=bykey[code,ports]
            a,_=decode(code);h=len(a)//2;a[ports[0]].remove(ports[1]);a[ports[1]].remove(ports[0])
            original=parse(row['doubled_surplus_table'])
            values=tuple(None if x is None else x//2 for x in original)
            for state,value in zip(states,values):
                if value is None:continue
                s=set(row['maximizing_witnesses'][str(state)])
                assert len(s)-h==value
                for w in range(len(a)):
                    if w in ports:
                        q=state[ports.index(w)]
                        assert (w in s)==(q!=0)
                        if q:assert len(a[w]&s)==(2 if q==1 else 1)
                    elif w in s:assert len(a[w]&s)==2
                positive_witnesses+=1
        else:values=templates[src]
        if rec['flip']:values=(values[0],values[2],values[1],values[3],values[4])
        assert expected==values
        generators.append(values)
    basis=[parse(r['profile']) for r in data['invariant']]
    assert len(basis)==len(set(basis))==10
    for row,b in zip(data['invariant'],basis):
        value=generators[row['word'][0]]
        for i in row['word'][1:]:value=multiply(value,generators[i])
        assert value==b
        assert maximum([b[0],b[1],b[2],b[4]])>=0
        u=maximum(b[:4]);p=b[4]
        assert maximum([2*u,add(add(u,p),1)])>=1
        t=maximum([u,add(p,2)])
        assert maximum([2*t,add(add(b[0],3),t)])>=3
    entry=[next(i for i,b in enumerate(basis) if lower(b,g)) for g in generators]
    closure=[]
    for a in basis:
        closure.append([next(i for i,c in enumerate(basis) if lower(c,multiply(a,b))) for b in basis])

    # Exact small cap calculation supports all theta-completion identities.
    p=cap();sets=list(good_sets(p))
    assert max(len(s) for s in sets if 12 in s)==7
    assert max(len(s) for s in sets if 12 not in s)==6
    core_edges_checked=0
    for lengths in [(1,2,2),(2,2,2),(1,2,3),(2,3,4)]:
        a=theta(lengths)
        for e in edges(a):
            typ=sum(v in (0,1) for v in e)
            expected={2:templates['theta_direct_edge'],0:templates['theta_internal_internal']} .get(typ)
            if typ==1:
                expected=templates['theta_branch_internal']
                if e[0] not in (0,1):expected=(expected[0],expected[2],expected[1],expected[3],expected[4])
            assert weighted_core_table(a,e)==expected
            core_edges_checked+=1
    for n in range(3,9):
        cyc=graph(n,[(i,(i+1)%n) for i in range(n)])
        assert weighted_core_table(cyc,(0,1),frozenset(),0)==templates['completed_cycle_edge']
    core=theta((1,2,2));completed,witness=complete(core,{0,1,2})
    assert len(completed)==30 and len(witness)==16 and good(completed,witness)
    _,avoid=complete(core,set())
    assert len(avoid)==14 and 0 not in avoid and good(completed,avoid)
    result=dict(basis_size=len(basis),oriented_generators=len(generators),
                positive_source_witnesses_checked=positive_witnesses,
                ordered_basis_products_checked=len(basis)**2,
                generator_to_basis=entry,product_to_basis=closure,
                cap_subsets_checked=8192,theta_core_edges_checked=core_edges_checked,
                thirty_vertex_example=dict(edges=edges(completed),maximum=16,
                    maximum_witness=sorted(witness),deleted_vertex=0,
                    vertex_deleted_maximum=14,vertex_deleted_witness=sorted(avoid)),
                original_conjecture='unresolved',
                proof_scope='Arbitrary ring assemblies with profiles dominating the certified basis.')
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('generator_to_basis','product_to_basis','thirty_vertex_example')},indent=2))


if __name__=='__main__':main()
