"""Check disjoint-edge extensions and their exact four-case identity."""
import gzip
import itertools
import json
import subprocess
from pathlib import Path
from verify_round12 import decode

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round30_data'


def extend(adj,e,f):
    n=len(adj);b=adj.copy()+[0,0];u,v=e;w,z=f
    b[u]^=1<<v;b[v]^=1<<u;b[w]^=1<<z;b[z]^=1<<w
    for a,c in ((u,n),(v,n),(w,n+1),(z,n+1),(n,n+1)):
        b[a]|=1<<c;b[c]|=1<<a
    return b


def good(adj,s):
    t=s
    while t:
        bit=t&-t;v=bit.bit_length()-1;t-=bit
        if (adj[v]&s).bit_count()!=2:return False
    return True


def main():
    parents=[];expected=set()
    for p,code in enumerate((DATA/'extension_parents.g6').read_text().split()):
        a,es=decode(code);adj=[sum(1<<v for v in ns) for ns in a];parents.append((adj,es))
        expected.update((p,i,j) for i,e in enumerate(es) for j,f in enumerate(es) if i<j and not set(e)&set(f))
    seen=set();min_order=1000;max_order=0
    with gzip.open(DATA/'extension_witnesses.txt.gz','rt') as stream:
        for line in stream:
            p,i,j,s=map(int,line.split());assert (p,i,j) in expected and (p,i,j) not in seen
            seen.add((p,i,j));adj,es=parents[p];b=extend(adj,es[i],es[j])
            assert s>>len(b)==0 and s.bit_count()>=len(b)//2 and good(b,s)
            assert all(mask.bit_count()==3 for mask in b)
            min_order=min(min_order,len(b));max_order=max(max_order,len(b))
    assert seen==expected
    formula_checks=0
    for n in (4,6,8,10):
        codes=subprocess.check_output(['geng','-cq','-d3','-D3',str(n)],text=True).split()
        for code in codes:
            a,es=decode(code);adj=[sum(1<<v for v in ns) for ns in a]
            for i,e in enumerate(es):
                for f in es[i+1:]:
                    if set(e)&set(f):continue
                    u,v=e;w,z=f;minus=adj.copy()
                    for x,y in (e,f):minus[x]^=1<<y;minus[y]^=1<<x
                    minus_e=adj.copy();minus_e[u]^=1<<v;minus_e[v]^=1<<u
                    minus_f=adj.copy();minus_f[w]^=1<<z;minus_f[z]^=1<<w
                    B=0;Te=Tf=P=-1000
                    for s in range(1<<n):
                        size=s.bit_count()
                        if good(minus,s):B=max(B,size)
                        if s>>u&1 and s>>v&1 and good(minus_f,s):Te=max(Te,size)
                        if s>>w&1 and s>>z&1 and good(minus_e,s):Tf=max(Tf,size)
                        if sum(s>>x&1 for x in e)!=1 or sum(s>>x&1 for x in f)!=1:continue
                        ends={x for x in (*e,*f) if s>>x&1}
                        if all((minus[x]&s).bit_count()==(1 if x in ends else 2)
                               for x in range(n) if s>>x&1):P=max(P,size)
                    h=extend(adj,e,f)
                    actual=max(s.bit_count() for s in range(1<<(n+2)) if good(h,s))
                    assert actual==max(B,Te+1,Tf+1,P+2)
                    formula_checks+=1
    result=dict(original_conjecture='unresolved',parent_records=len(parents),
                verified_extensions=len(seen),minimum_order=min_order,maximum_order=max_order,
                exact_small_formula_checks=formula_checks,
                scope='Every disjoint edge pair of each retained parent checked. '
                      'Indexed constructions may repeat graphs; this is not a census at these orders.')
    (ROOT/'round30_extension_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
