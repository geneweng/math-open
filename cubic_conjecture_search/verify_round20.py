"""Check new positive witnesses, exact SAT candidate optima, and generator scope.
Small generator tests compare against independently generated labelled cubic graphs.
Large-radius aggregate counts are not independently re-enumerated here.
"""
import itertools
import json
from pathlib import Path
import subprocess
from verify_round12 import decode
from verify_round14 import cycle_space_good_sets
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round20_data'

def check(a,mask):
    assert 0<=mask<1<<len(a) and mask.bit_count()>=len(a)//2
    assert all(sum(bool(mask>>u&1) for u in a[v])==2 for v in range(len(a)) if mask>>v&1)

def labelled_cubic(n):
    a=[set() for _ in range(n)]
    def visit(v):
        if v==n:
            yield [s.copy() for s in a];return
        need=3-len(a[v]);pool=[u for u in range(v+1,n) if len(a[u])<3]
        if need<0 or len(pool)<need:return
        for extra in itertools.combinations(pool,need):
            for u in extra:a[v].add(u);a[u].add(v)
            yield from visit(v+1)
            for u in extra:a[v].remove(u);a[u].remove(v)
    yield from visit(0)

def edgekey(a):return frozenset((v,u) for v in range(len(a)) for u in a[v] if v<u)

def encode(a):
    bits=[int(u in a[v]) for v in range(1,len(a)) for u in range(v)]
    bits += [0]*(-len(bits)%6)
    return chr(len(a)+63)+''.join(chr(63+sum(bits[i+j]<<(5-j) for j in range(6))) for i in range(0,len(bits),6))

def main():
    small=[];tmp=ROOT.parent/'tmp/cubic_round20';exe=tmp/'edge_ball_enumerate'
    for n in [6,8]:
        seed=next(labelled_cubic(n));ek=edgekey(seed);code=encode(seed)
        # Select connected seeds because the shared graph6 reader requires them.
        if n==8:
            seed=[{(v-1)%8,(v+1)%8,(v+4)%8} for v in range(8)];ek=edgekey(seed);code=encode(seed)
        masks=[s for s in range(1<<n) if s.bit_count()>=n//2 and all(sum(bool(s>>u&1) for u in seed[v])==2 for v in range(n) if s>>v&1)]
        (tmp/f'test{n}.g6').write_text(code+'\n');(tmp/f'test{n}_masks.txt').write_text(''.join(str(s)+'\n' for s in masks))
        dump=tmp/f'test{n}_all.txt'
        subprocess.run([str(exe),str(tmp/f'test{n}.g6'),str(tmp/f'test{n}_masks.txt'),'4',str(tmp/f'test{n}'),str(dump)],check=True,capture_output=True)
        actual=set();records=0
        for line in dump.read_text().splitlines():
            c,m=line.split();a,_=decode(c);check(a,int(m));actual.add(edgekey(a));records+=1
        allgraphs=list(labelled_cubic(n));expected={edgekey(a) for a in allgraphs if len(ek-edgekey(a))<=4}
        assert actual==expected,(n,len(actual),len(expected))
        small.append(dict(order=n,labelled_cubic_graphs=len(allgraphs),unique_graphs_in_ball=len(actual),reconnection_records=records))
    novel=0;direct=[];counts={}
    for n in [24,26]:
        seed,_=decode((DATA/f'seed{n}.g6').read_text().strip());ek=edgekey(seed)
        for line in (DATA/f'ball{n}_novel.txt').read_text().splitlines():
            c,m=line.split();a,_=decode(c);assert len(a)==n and all(len(ns)==3 for ns in a)
            assert len(ek-edgekey(a))<=4;check(a,int(m));novel+=1
        rows=json.loads((DATA/f'direct{n}_radius4.json').read_text())
        for r in rows['records']:
            a,_=decode(r['graph6']);check(a,r['witness']);assert len(ek-edgekey(a))<=4
            masks=cycle_space_good_sets(a)
            assert max(s.bit_count() for s in masks)==r['maximum_size']
            assert sum(s.bit_count()>=n//2 for s in masks)==r['qualifying_sets']
        direct.append(dict(order=n,status=rows['status'],candidates=len(rows['records']),cuts=rows['total_cuts']))
        counts[n]=[list(map(int,l.split())) for l in (DATA/f'ball{n}_counts.txt').read_text().splitlines()]
    result=dict(original_conjecture_resolved=False,small_generator_checks=small,
                new_positive_witnesses_checked=novel,direct_synthesis=direct,large_reconnection_counts=counts,
                scope='Large balls verified by C++ enumeration; independent Python verifies small generator completeness, all newly required witnesses, and all SAT candidate maxima.')
    (ROOT/'round20_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
