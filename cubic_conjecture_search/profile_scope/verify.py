"""Verify explicit failures of universal profile conditions and core certificates.

The two exceptional profiles are independently computed by all vertex
subsets. The core census uses only positive witness checking; its complete
input list is regenerated with geng. No optimization solver is required.
"""
import collections
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import networkx as nx

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from verify_round12 import decode
from verify_bridge_reduction import complete,edges
sys.path.insert(0,str(ROOT/'ring_closure'))
from verify import parse,multiply,lower,maximum


def validate_state(a,e,mask,state):
    assert mask>=0 and mask>>len(a)==0
    u,v=e
    wanted=[(0,0),(0,1),(1,0),(1,1),(2,2)][state]
    for w in range(len(a)):
        chosen=bool(mask>>w&1)
        degree=sum(mask>>x&1 for x in a[w])
        if w==u:degree-=bool(mask>>v&1)
        if w==v:degree-=bool(mask>>u&1)
        if w in e:
            q=wanted[e.index(w)]
            assert chosen==(q!=0)
            if chosen:assert degree==(1 if q==2 else 2)
        elif chosen:assert degree==2


def exact_weighted_table(a,e):
    branch_mask=sum(1<<v for v in range(len(a)) if len(a[v])==3)
    half=branch_mask.bit_count()//2;table=[None]*5;witnesses=[None]*5
    adj=[s.copy() for s in a];u,v=e;adj[u].remove(v);adj[v].remove(u)
    bm=[sum(1<<v for v in s) for s in adj]
    for mask in range(1<<len(a)):
        states=[0,0];ok=True
        for w in range(len(a)):
            if not(mask>>w&1):continue
            d=(mask&bm[w]).bit_count()
            if w in e:
                if d not in (1,2):ok=False;break
                states[e.index(w)]=3-d
            elif d!=2:ok=False;break
        if not ok:continue
        state=tuple(states)
        j=[(0,0),(0,1),(1,0),(1,1),(2,2)].index(state)
        score=(mask&branch_mask).bit_count()-half
        if table[j] is None or score>table[j]:table[j]=score;witnesses[j]=mask
    return tuple(table),witnesses


def main():
    old=json.loads((ROOT/'ring_closure/invariant.json').read_text())
    first=json.loads((HERE/'expanded_invariant.json').read_text())
    second=json.loads((HERE/'second_expanded_invariant.json').read_text())
    final=json.loads((HERE/'census_invariant.json').read_text())
    examples=[];new_profiles={}
    sources=[(json.loads((HERE/'outside_cone.json').read_text()),old,'outside_core_62'),
             (json.loads((HERE/'outside_expanded_cone.json').read_text()),first,'outside_core_64'),
             (json.loads((HERE/'census_outside_profiles.json').read_text())['records'][0],second,'outside_census_64')]
    for raw,baseline,label in sources:
        a,_=decode(raw['core_graph6']);e=tuple(raw['edge'])
        profile,witnesses=exact_weighted_table(a,e)
        assert profile==parse(raw['profile'])
        assert not any(lower(parse(r['profile']),profile) for r in baseline['invariant'])
        new_profiles[label]=profile
        full,_=complete(a,set());n=len(full);h=n//2;sets=[]
        for j,mask in enumerate(witnesses):
            if mask is None:sets.append(None);continue
            selected={v for v in range(len(a)) if mask>>v&1}
            same,lift=complete(a,selected);assert same==full
            bigmask=sum(1<<v for v in lift)
            validate_state(full,e,bigmask,j)
            assert len(lift)-h==profile[j]
            sets.append(sorted(lift))
        g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(edges(full))
        assert all(d==3 for _,d in g.degree()) and nx.is_connected(g)
        examples.append(dict(core=raw['core_graph6'],edge=list(e),
                             completed_graph6=nx.to_graph6_bytes(g,header=False).decode().strip(),
                             order=n,profile=list(profile),state_witnesses=sets,
                             parent_maximum=h+maximum([profile[j] for j in (0,1,2,4)]),
                             U=h+maximum(profile[:4]),T=h+profile[4],W=h+profile[0]))
    (HERE/'verified_examples.json').write_text(json.dumps(examples,indent=2)+'\n')

    # The extended invariant is a new conditional theorem, not universal.
    base_generators={json.dumps(r,sort_keys=True):parse(r['profile']) for r in old['generators']}
    for certificate in (first,second,final):
        generators=[]
        for r in certificate['generators']:
            if isinstance(r['source'],str) and r['source'] in new_profiles:
                q=new_profiles[r['source']]
                if r['flip']:q=(q[0],q[2],q[1],q[3],q[4])
                assert q==parse(r['profile'])
            else:q=base_generators[json.dumps(r,sort_keys=True)]
            generators.append(q)
        basis=[parse(r['profile']) for r in certificate['invariant']]
        for r,b in zip(certificate['invariant'],basis):
            q=generators[r['word'][0]]
            for i in r['word'][1:]:q=multiply(q,generators[i])
            assert q==b and maximum([b[j] for j in (0,1,2,4)])>=0
        assert all(any(lower(b,g) for b in basis) for g in generators)
        assert all(any(lower(c,multiply(a,b)) for c in basis) for a in basis for b in basis)
        assert all(any(lower(c,(b[0],b[2],b[1],b[3],b[4])) for c in basis) for b in basis)
    final_basis=[parse(r['profile']) for r in final['invariant']]

    expected=[]
    for n,m in [(12,16),(14,19)]:
        expected+=subprocess.check_output(['geng','-cq','-d2','-D3',str(n),f'{m}:{m}'],text=True).split()
    counts=collections.Counter();parent_edges=0;sets_checked=0
    with gzip.open(HERE/'core_certificates.jsonl.gz','rt') as file:
        for index,line in enumerate(file):
            r=json.loads(line);assert r['graph6']==expected[index] and r['failure'] is False
            a,es=decode(r['graph6']);n=len(a)
            assert all(len(s) in (2,3) for s in a)
            branch_mask=sum(1<<v for v in range(n) if len(a[v])==3)
            b=branch_mask.bit_count();assert b==r['branches']==n-4
            assert n-b==4
            mask=r['core_witness'];assert mask>>n==0
            assert all(sum(mask>>u&1 for u in a[v])==2 for v in range(n) if mask>>v&1)
            assert (mask&branch_mask).bit_count()>=b//2
            assert len(r['states'])==len(es)
            for e,ms in zip(es,r['states']):
                assert len(ms)==5
                values=[]
                for j,s in enumerate(ms):
                    if s==-1:values.append(None);continue
                    validate_state(a,e,s,j);sets_checked+=1
                    values.append((s&branch_mask).bit_count()-b//2)
                u=maximum(values[:4]);p=values[4];w=values[0]
                assert u is not None and w is not None
                assert max(2*u,u+p+1 if p is not None else -1000000)>=1
                B=max(u,p+2 if p is not None else -1000000)
                assert max(2*B,w+3+B)>=3
                assert any(lower(q,values) for q in final_basis)
                parent_edges+=1
            counts[n]+=1
    assert index+1==len(expected)==23326
    report=dict(core_counts=dict(counts),parent_edge_cases=parent_edges,
                positive_boundary_sets_checked=sets_checked,
                completed_parent_orders=[64,66],original_and_both_rooted_tests_pass=True,
                explicit_outside_examples=[{k:r[k] for k in ('order','profile','parent_maximum','U','T','W')} for r in examples],
                first_expanded_basis=len(first['invariant']),second_expanded_basis=len(second['invariant']),
                final_basis=len(final_basis),all_census_profiles_dominate_final_basis=True,
                extended_closure_products_checked=sum(len(x['invariant'])**2 for x in (first,second,final)),
                certificate_sha256=hashlib.sha256((HERE/'core_certificates.jsonl.gz').read_bytes()).hexdigest(),
                original_conjecture='unresolved')
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
