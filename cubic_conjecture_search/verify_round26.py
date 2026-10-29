"""Verify four-port witnesses and the arbitrary-assembly criterion.

Large-profile upper bounds are not independently checked or needed for the
assembly theorem. All positive witnesses used by it are checked directly.
"""
import itertools
import json
import random
import hashlib
from pathlib import Path

from verify_round12 import decode

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'round26_data'
NEG = -1000000


def read_rows(path):
    result = []
    for line in Path(path).read_text().splitlines():
        z = line.split()
        assert len(z) == 169
        result.append(dict(code=z[0], removed=list(map(int,z[1:3])),
                           ports=list(map(int,z[3:7])),
                           values=list(map(int,z[7::2])),
                           witnesses=list(map(int,z[8::2]))))
    return result


def check(row, exact=False):
    a, es = decode(row['code'])
    u,v = row['removed']; ports = row['ports']; removed={u,v}
    assert v in a[u] and not a[u]&a[v]
    assert ports == sorted((a[u]|a[v])-removed) and len(ports)==4
    remaining = set(range(len(a)))-removed
    q = len(remaining)
    witnessed = 0
    for state,(score,mask) in enumerate(zip(row['values'],row['witnesses'])):
        if score == NEG:
            continue
        s={v for v in range(len(a)) if mask>>v&1}
        assert s<=remaining and 2*len(s)-q==score
        for v in remaining-set(ports):
            assert v not in s or len(a[v]&s)==2
        for i,v in enumerate(ports):
            digit=state//3**i%3
            assert (v in s)==(digit!=0)
            if digit:
                assert len(a[v]&s)==3-digit
        witnessed+=1
    if exact:
        best=[NEG]*81; vs=sorted(remaining)
        for mask in range(1<<q):
            s={v for i,v in enumerate(vs) if mask>>i&1}
            if any(len(a[v]&s)!=2 for v in s-set(ports)):
                continue
            if any(len(a[v]&s) not in (1,2) for v in s&set(ports)):
                continue
            state=sum((3-len(a[v]&s))*3**i for i,v in enumerate(ports) if v in s)
            best[state]=max(best[state],2*len(s)-q)
        assert best==row['values']
    return witnessed


def main():
    rows=read_rows(DATA/'profiles.txt')
    count=sum(check(row) for row in rows)
    criteria=[]
    for i,row in enumerate(rows):
        if row['values'][0]>=0:
            criteria.append(dict(row=i,method='no_ports',states=[0]))
        else:
            states=[3**a+3**b for a,b in itertools.combinations(range(4),2)]
            assert all(row['values'][s]>=0 for s in states)
            criteria.append(dict(row=i,method='any_pair',states=states))
    # Independently check that every eligible deletion was generated.
    expected=set()
    for code in (DATA/'seeds.g6').read_text().split():
        a,es=decode(code)
        expected.update((code,u,v) for u,v in es if not a[u]&a[v])
    assert {(r['code'],*r['removed']) for r in rows}==expected
    assert len(rows)==len(expected)==2214
    # Exhaustive vertex-subset oracle on every eligible edge of every
    # connected simple cubic graph through order ten. The test input and
    # computed profiles remain saved for reproducibility.
    small=read_rows(DATA/'small_profiles.txt')
    small_witnesses=sum(check(r,exact=True) for r in small)
    assert len(set(r['code'] for r in small))==26  # K4 has no eligible edge.
    # One assembly uses every retained piece; 40 more vary the size and
    # repetitions. Deterministic port pairings and a direct Hall matching
    # produce complete graph witnesses, checked without profile arithmetic.
    rng=random.Random(260026)
    assemblies=[]
    selections=[list(range(len(rows)))]+[
        [rng.randrange(len(rows)) for _ in range(k)]
        for k in (2,3,4,5,8,12,25,100) for _ in range(5)]
    for indices in selections:
        stubs=[(i,p) for i in range(len(indices)) for p in range(4)]
        while True:
            rng.shuffle(stubs)
            pairs=list(zip(stubs[::2],stubs[1::2]))
            if all(x[0]!=y[0] for x,y in pairs):
                break
        incident=[[] for _ in indices]
        for e,(x,y) in enumerate(pairs):
            incident[x[0]].append(e);incident[y[0]].append(e)
        owners={}
        def augment(slot,seen):
            block=slot//2
            for e in incident[block]:
                if e in seen:continue
                seen.add(e)
                if e not in owners or augment(owners[e],seen):
                    owners[e]=slot;return True
            return False
        for i,r in enumerate(indices):
            if criteria[r]['method']=='any_pair':
                assert augment(2*i,set()) and augment(2*i+1,set())
        used=[set() for _ in indices]
        for e,slot in owners.items():
            block=slot//2
            used[block].update(p for b,p in pairs[e] if b==block)
        adj=[];chosen=set();boundary=[]
        for i,r in enumerate(indices):
            row=rows[r];a,_=decode(row['code'])
            vs=sorted(set(range(len(a)))-set(row['removed']))
            ren={v:len(adj)+j for j,v in enumerate(vs)}
            adj.extend({ren[w] for w in a[v] if w in ren} for v in vs)
            state=sum(3**p for p in used[i])
            assert len(used[i])==(2 if criteria[r]['method']=='any_pair' else 0)
            assert row['values'][state]>=0
            chosen.update(ren[v] for v in vs if row['witnesses'][state]>>v&1)
            boundary.append([ren[v] for v in row['ports']])
        for (i,p),(j,q) in pairs:
            u,v=boundary[i][p],boundary[j][q]
            assert v not in adj[u] and u!=v
            adj[u].add(v);adj[v].add(u)
        assert all(len(ns)==3 for ns in adj)
        assert all(len(adj[v]&chosen)==2 for v in chosen)
        assert 2*len(chosen)>=len(adj)
        digest=hashlib.sha256(json.dumps([sorted(s) for s in adj]).encode()).hexdigest()
        assemblies.append(dict(blocks=len(indices),order=len(adj),
                               selected=len(chosen),graph_sha256=digest))
    result=dict(original_conjecture='unresolved',large_profiles=len(rows),
                large_positive_witnesses=count,
                avoid_all=sum(c['method']=='no_ports' for c in criteria),
                any_pair=sum(c['method']=='any_pair' for c in criteria),
                criterion_certificates=criteria,
                small_exact_profiles=len(small),small_positive_witnesses=small_witnesses,
                assembly_checks=assemblies,
                verification_scope='All large positive masks and all eligible deletions checked. '
                    'Large maxima/infeasibility are not independently checked or used. '
                    'Small profiles checked against exhaustive vertex subsets.')
    (ROOT/'round26_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in
                      ('criterion_certificates','assembly_checks')}))
    print('Direct assembly checks:',len(assemblies),'largest order:',max(r['order'] for r in assemblies))


if __name__=='__main__':
    main()
