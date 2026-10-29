import itertools,json
from pathlib import Path
P=Path('cubic_conjecture_search/round21_data');perm=list(itertools.permutations(range(3)))
states=[tuple((i//3**j)%3 for j in range(3)) for i in range(27)]
trans=[[sum(s[p[j]]*3**j for j in range(3)) for s in states] for p in perm]
rows=[]
for line in (P/'profiles.txt').read_text().splitlines():
 r=line.split();f=tuple(map(int,r[5::2]));ws=list(map(int,r[6::2]));variants=[tuple(f[t[i]] for i in range(27)) for t in trans];k=min(range(6),key=lambda k:variants[k]);rows.append(dict(graph6=r[0],removed=int(r[1]),ports=list(map(int,r[2:5])),values=list(f),witnesses=ws,canonical=list(variants[k]),perm=list(perm[k])))
unique={tuple(r['canonical']):r for r in rows}
minimal=[r for f,r in unique.items() if not any(g!=f and all(a<=b for a,b in zip(g,f)) for g in unique)]
print('rows',len(rows),'unique',len(unique),'minimal',len(minimal))
(P/'minimal_profiles.json').write_text(json.dumps(minimal,indent=2)+'\n')
