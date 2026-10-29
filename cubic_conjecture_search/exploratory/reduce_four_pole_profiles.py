"""Reproduce round 27's exact profile domination reduction."""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_round26 import read_rows

DATA=ROOT/'round27_data'
rows=read_rows(DATA/'profiles.txt')
perms=list(itertools.permutations(range(4)))
states=[tuple(s//3**i%3 for i in range(4)) for s in range(81)]
maps=[[sum(z[p[i]]*3**i for i in range(4)) for z in states] for p in perms]
unique={}
for i,r in enumerate(rows):
    unique.setdefault(tuple(r['values']),i)
canonical={}
for f,i in unique.items():
    variants=[tuple(f[j] for j in m) for m in maps]
    key=min(variants)
    canonical.setdefault(key,(i,variants.index(key)))
fixed=[]
for f in sorted(canonical,key=lambda f:(sum(f),f)):
    if not any(all(a<=b for a,b in zip(g,f)) for g in fixed):
        fixed.append(f)
kept=[];pool=np.empty((0,81),dtype=np.int32);mm=np.array(maps)
for f in fixed:
    a=np.array(f,dtype=np.int32)
    if len(pool) and np.any(np.all(pool<=a,axis=1)):
        continue
    i,p=canonical[f]
    kept.append(dict(values=f,row=i,permutation=perms[p]))
    pool=np.concatenate((pool,a[mm]))
result=dict(profiles=kept,raw_count=len(rows),unique_count=len(unique),
            canonical_count=len(canonical),fixed_orientation_minima=len(fixed))
(DATA/'canonical.json').write_text(json.dumps(result,indent=2)+'\n')
(DATA/'minimal_values.txt').write_text('\n'.join(
    ' '.join(map(str,r['values'])) for r in kept)+'\n')
print('Retained profiles:',len(kept))
