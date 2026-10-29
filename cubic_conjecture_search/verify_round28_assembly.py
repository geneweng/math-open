"""Check the open-port assembly criterion and construct whole-graph witnesses."""
import itertools
import json
import random
from collections import deque
from pathlib import Path

from verify_round26 import read_rows,check
from verify_round12 import decode
from verify_bridge_reduction import edges,graph,good,franklin

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round28_data'


def match(left,neighbours):
    """Bipartite augmenting paths; entries are (edge label, right vertex)."""
    ml={};mr={};labels={}
    for start in left:
        queue=deque([start]);seen={start};parent={};end=None
        while queue and end is None:
            l=queue.popleft()
            for edge,r in neighbours[l]:
                if r in parent:continue
                parent[r]=(l,edge)
                if r not in mr:end=r;break
                other=mr[r]
                if other not in seen:seen.add(other);queue.append(other)
        assert end is not None
        while end is not None:
            l,edge=parent[end];previous=ml.get(l)
            ml[l]=end;mr[end]=l;labels[l]=edge;end=previous
    return labels


def main():
    rows=read_rows(ROOT/'round27_data/profiles.txt');qualified=[]
    for i,r in enumerate(rows):
        f=r['values'];ok=True
        for x,y in itertools.combinations(range(4),2):
            s=2*3**x+2*3**y
            ok &= f[s]>=0 or all(f[s+3**z]>=0 for z in range(4) if z not in (x,y))
        if ok:qualified.append(i)
    assert len(qualified)==5552
    local=sum(check(rows[i]) for i in qualified)
    rng=random.Random(280029);selections=[qualified]+[
        [rng.choice(qualified) for _ in range(k)] for k in (3,4,8,20,100) for _ in range(4)]
    results=[]
    for indices in selections:
        nblocks=len(indices);stubs=[(i,p) for i in range(nblocks) for p in range(4)]
        while True:
            rng.shuffle(stubs);joins=list(zip(stubs[::2],stubs[1::2]))
            if all(a[0]!=b[0] for a,b in joins):break
        inc=[[] for _ in indices]
        for e,(a,b) in enumerate(joins):inc[a[0]].append(e);inc[b[0]].append(e)
        todo=[ns.copy() for ns in inc];used=set();out=[[] for _ in indices];indegree=[0]*nblocks
        for start in range(nblocks):
            stack=[start]
            while stack:
                u=stack[-1]
                while todo[u] and todo[u][-1] in used:todo[u].pop()
                if not todo[u]:stack.pop();continue
                e=todo[u].pop();used.add(e);a,b=joins[e];v=a[0]^b[0]^u
                out[u].append((e,v));indegree[v]+=1;stack.append(v)
        assert all(len(ns)==2 for ns in out) and all(d==2 for d in indegree)
        factor=set(match(range(nblocks),out).values())
        assert all(sum(e in factor for e in ns)==2 for ns in inc)
        states=[];active=[];options=[[] for _ in indices]
        for i,r in enumerate(indices):
            openports=[p for e in inc[i] if e in factor for b,p in joins[e] if b==i]
            s=sum(2*3**p for p in openports);states.append(s)
            if rows[r]['values'][s]<0:
                active.append(i);options[i]=[(e,e) for e in inc[i] if e not in factor]
        assigned=match(active,options)
        for i,e in assigned.items():
            p=next(p for b,p in joins[e] if b==i);states[i]+=3**p
        es=[];n=0;boundary=[];selected=set()
        for i,r in enumerate(indices):
            row=rows[r];a,_=decode(row['code']);vs=sorted(set(range(len(a)))-set(row['removed']))
            ren={v:n+j for j,v in enumerate(vs)};n+=len(vs)
            es.extend((ren[u],ren[v]) for u,v in edges(a) if u in ren and v in ren)
            boundary.append([ren[v] for v in row['ports']]);s=states[i]
            assert row['values'][s]>=0
            selected.update(ren[v] for v in vs if row['witnesses'][s]>>v&1)
        es.extend((boundary[i][p],boundary[j][q]) for (i,p),(j,q) in joins)
        a=graph(n,es)
        assert all(len(ns)==3 for ns in a) and good(a,selected) and 2*len(selected)>=n
        results.append(dict(blocks=nblocks,order=n,selected=len(selected)))
    sharp=json.loads((DATA/'sharp_checks.json').read_text());f=franklin()
    for r in sharp:
        a,_=decode(r['graph6']);perm=r['franklin_isomorphism'];col=r['colours']
        assert sorted(perm)==list(range(12))
        assert all({perm[w] for w in a[v]}==f[perm[v]] for v in range(12))
        assert all(sum(col[w] for w in a[v])==1+col[v] for v in range(12))
        assert sum(col)==6 and r['strict_status']=='INFEASIBLE'
    result=dict(original_conjecture='unresolved',qualified_fragments=len(qualified),
                checked_local_witnesses=local,assembly_checks=results,
                franklin_isomorphisms=len(sharp),qualified_rows=qualified)
    (ROOT/'round28_assembly_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Qualified',len(qualified),'assemblies',len(results),'largest',max(r['order'] for r in results))


if __name__=='__main__':main()
