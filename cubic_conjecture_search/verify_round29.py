"""Direct checks of mixed-criterion assemblies and synthesis witnesses."""
import itertools
import json
import random
from pathlib import Path

from verify_round26 import read_rows,check
from verify_round12 import decode
from verify_bridge_reduction import graph,edges,good
from verify_round28 import Library,MAPS,PERMS
from verify_round28_assembly import match

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round29_data'


def criteria(f):
    closed=f[0]>=0 or all(f[3**i+3**j]>=0 for i,j in itertools.combinations(range(4),2))
    opened=all(f[2*3**i+2*3**j]>=0 or all(f[2*3**i+2*3**j+3**k]>=0
        for k in range(4) if k not in(i,j)) for i,j in itertools.combinations(range(4),2))
    return closed,opened


def expand(rows,ports,joins,states):
    es=[];n=0;selected=set();boundary=[]
    for row,ordered,st in zip(rows,ports,states):
        a,_=decode(row['code']);vs=sorted(set(range(len(a)))-set(row['removed']))
        ren={v:n+i for i,v in enumerate(vs)};n+=len(vs)
        es.extend((ren[u],ren[v]) for u,v in edges(a) if u in ren and v in ren)
        boundary.extend(ren[v] for v in ordered)
        selected.update(ren[v] for v in vs if row['witnesses'][st]>>v&1)
    es.extend((boundary[u],boundary[v]) for u,v in joins)
    a=graph(n,es)
    assert all(len(ns)==3 for ns in a) and good(a,selected)
    return a,selected


def main():
    DATA.mkdir(exist_ok=True)
    rows=read_rows(ROOT/'round27_data/profiles.txt');groups={}
    for i,r in enumerate(rows):groups.setdefault(criteria(r['values']),[]).append(i)
    ns=[[v for v in range(5) if v!=u] for u in range(5)]
    joins=[(4*u+ns[u].index(v),4*v+ns[v].index(u)) for u in range(5) for v in range(u+1,5)]
    incident=[[] for _ in range(5)]
    for e,(u,v) in enumerate(joins):incident[u//4].append(e);incident[v//4].append(e)
    rng=random.Random(290029);records=[]
    for count in (3,4):
        for trial in range(500):
            opened=set(rng.sample(range(5),count));cyc=list(opened);rng.shuffle(cyc)
            fedges={tuple(sorted((cyc[i],cyc[(i+1)%count]))) for i in range(count)}
            factor={e for e,(u,v) in enumerate(joins) if tuple(sorted((u//4,v//4))) in fedges}
            assert all(sum(e in factor for e in incident[i])==(2 if i in opened else 0) for i in range(5))
            chosen=[rng.choice(groups[(False,True)] if i in opened else groups[(True,False)]) for i in range(5)]
            states=[];slots=[];neighbours={}
            for i,r in enumerate(chosen):
                f=rows[r]['values']
                if i in opened:
                    ps=[p%4 for e in incident[i] if e in factor for p in joins[e] if p//4==i]
                    s=sum(2*3**p for p in ps);demand=int(f[s]<0)
                else:s=0;demand=0 if f[0]>=0 else 2
                states.append(s)
                for j in range(demand):
                    slot=(i,j);slots.append(slot);neighbours[slot]=[(e,e) for e in incident[i] if e not in factor]
            assigned=match(slots,neighbours)
            for (i,j),e in assigned.items():
                p=next(p%4 for p in joins[e] if p//4==i);states[i]+=3**p
            rr=[rows[i] for i in chosen]
            assert all(r['values'][s]>=0 for r,s in zip(rr,states))
            a,s=expand(rr,[r['ports'] for r in rr],joins,states)
            assert 2*len(s)>=len(a)
            records.append(dict(open_count=count,rows=chosen,states=states,order=len(a),selected=sorted(s)))
    (DATA/'mixed_certificates.json').write_text(json.dumps(records,indent=2)+'\n')
    synthesis=json.loads((DATA/'mixed_synthesis.json').read_text());lib=Library()
    checked=set()
    for opt in synthesis['options']:
        r=lib.reduced[opt['profile']]
        assert opt['values']==[r['values'][j] for j in MAPS[opt['permutation']]]
        if r['row'] not in checked:check(lib.raw[r['row']]);checked.add(r['row'])
    for rec in synthesis['records']:
        flat=[st//3**j%3 for st in rec['states'] for j in range(4)]
        assert all((flat[u],flat[v]) in ((0,0),(0,1),(1,0),(2,2)) for u,v in synthesis['joins'])
        rr=[];pp=[];source=[]
        for idx,st in zip(rec['options'],rec['states']):
            opt=synthesis['options'][idx];item=lib.item(24*opt['profile']+opt['permutation'])
            reduced=lib.reduced[opt['profile']]
            first=MAPS[PERMS.index(tuple(reduced['permutation']))]
            source.append(first[MAPS[opt['permutation']][st]])
            rr.append(item['raw']);pp.append(item['ports'])
        a,s=expand(rr,pp,synthesis['joins'],source)
        assert len(a)==rec['order'] and sorted(s)==rec['selected']
        assert 2*len(s)-len(a)==rec['doubled_surplus'] and rec['doubled_surplus']>=0
    fixed=json.loads((DATA/'k5_exhaust.json').read_text());options={}
    for rid in (2,24):
        f=lib.reduced[rid]['values'];unique={}
        for p,m in enumerate(MAPS):unique.setdefault(tuple(f[j] for j in m),p)
        options[rid]=list(unique.values());assert len(options[rid])==3
        assert fixed['options'][str(rid)]==options[rid]
    expected={(count,ori) for count in (1,2) for ori in itertools.product(
        *(options[rid] for rid in [2]*count+[24]*(5-count)))}
    assert {(r['open_count'],tuple(r['orientations'])) for r in fixed['records']}==expected
    assert len(fixed['records'])==len(expected)==486
    for rec in fixed['records']:
        rr=[];pp=[];source=[]
        assert rec['profiles']==[2]*rec['open_count']+[24]*(5-rec['open_count'])
        for r,p,st in zip(rec['profiles'],rec['orientations'],rec['states']):
            item=lib.item(24*r+p);rr.append(item['raw']);pp.append(item['ports'])
            first=MAPS[PERMS.index(tuple(lib.reduced[r]['permutation']))]
            source.append(first[MAPS[p][st]])
        a,s=expand(rr,pp,fixed['joins'],source)
        assert len(a)==rec['order'] and sorted(s)==rec['selected']
        assert 2*len(s)-len(a)==rec['doubled_surplus'] and rec['doubled_surplus']>=10
    result=dict(original_conjecture='unresolved',mixed_theorem_checks=len(records),
                minimum_order=min(r['order'] for r in records),maximum_order=max(r['order'] for r in records),
                synthesis_status=synthesis['status'],synthesis_positive_witnesses=len(synthesis['records']),
                fixed_k5_profile_assignments=len(fixed['records']),
                fixed_k5_minimum_doubled_surplus=min(r['doubled_surplus'] for r in fixed['records']),
                scope='Whole-graph positive witnesses checked directly. Synthesis cut validity '
                      'uses these witnesses; no general exclusion follows from a time limit.')
    (ROOT/'round29_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
