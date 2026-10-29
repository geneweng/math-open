"""Exact optimization of fixed cyclic assemblies; heuristic choice of pieces.

Every step scans the retained profiles and all port permutations for one
position. This is not an exhaustive search over words of fragments.
"""
import itertools
import json
import random
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'round28_data'
NEG=-1000000000


def product(a,b):
    return (a[:,:,None]+b[None,:,:]).max(axis=1)


def main():
    DATA.mkdir(exist_ok=True)
    rows=json.loads((ROOT/'round27_data/canonical.json').read_text())['profiles']
    perms=list(itertools.permutations(range(4)))
    states=[tuple(s//3**i%3 for i in range(4)) for s in range(81)]
    maps=np.array([[sum(z[p[i]]*3**i for i in range(4)) for z in states] for p in perms])
    f=np.array([r['values'] for r in rows],dtype=np.int64)[:,maps].reshape(-1,81)
    f[f<=-1000000]=NEG
    s2=[(s%3,s//3) for s in range(9)]
    compatible=lambda a,b:all((x==0 and y<=1) or (x==1 and y==0) or x==y==2 for x,y in zip(a,b))
    mat=np.full((len(f),9,9),NEG,dtype=np.int64)
    for a in range(9):
        for b in range(9):
            mat[:,a,b]=f[:,[t+9*b for t in range(9) if compatible(s2[a],s2[t])]].max(axis=1)
    identity=np.full((9,9),NEG,dtype=np.int64);np.fill_diagonal(identity,0)
    rng=random.Random(280028);records=[];evaluations=0
    for k in (3,4,5,6,8,12,20,40):
        best=1000000
        for restart in range(3):
            word=[rng.randrange(len(mat)) for _ in range(k)]
            for sweep in range(5):
                order=list(range(k));rng.shuffle(order)
                for i in order:
                    other=identity
                    for j in range(1,k):other=product(other,mat[word[(i+j)%k]])
                    values=(mat+other.T[None,:,:]).max(axis=(1,2))
                    evaluations+=len(mat)
                    value=int(values.min());ties=np.flatnonzero(values==value)
                    word[i]=int(ties[rng.randrange(len(ties))])
                    best=min(best,value)
                    records.append(dict(blocks=k,restart=restart,sweep=sweep,
                                        word=word.copy(),doubled_surplus=value))
                    if value<0:
                        (DATA/'search.json').write_text(json.dumps(dict(
                            status='candidate_requires_independent_verification',
                            coordinate_evaluations=evaluations,records=records),indent=2)+'\n')
                        print('NEGATIVE CANDIDATE',k,value,flush=True);return
        print('DONE blocks',k,'best doubled surplus',best,flush=True)
    (DATA/'search.json').write_text(json.dumps(dict(status='finite_search_no_counterexample',
        matrix_count=len(mat),coordinate_evaluations=evaluations,records=records,
        scope='Coordinate descent only; all orientations and profiles scanned at each update, '
              'not all cyclic assemblies.'),indent=2)+'\n')


if __name__=='__main__':main()
