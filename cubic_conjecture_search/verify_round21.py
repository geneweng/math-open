"""Standard-library certificate checks for large three-port constructions.
All feasibility witnesses are checked directly. Bounds need no upper bounds.
"""
import itertools,json,time
from pathlib import Path
from verify_round12 import decode
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round21_data';NEG=-1000000
STATES=[tuple((i//3**j)%3 for j in range(3)) for i in range(27)]
PERMS=list(itertools.permutations(range(3)))
TRANS=[[sum(s[p[j]]*3**j for j in range(3)) for s in STATES] for p in PERMS]

def load():
 rows=[]
 for line in (DATA/'profiles.txt').read_text().splitlines():
  r=line.split();f=list(map(int,r[5::2]));variants=[tuple(f[t[i]] for i in range(27)) for t in TRANS];k=min(range(6),key=lambda k:variants[k])
  rows.append(dict(graph6=r[0],removed=int(r[1]),ports=list(map(int,r[2:5])),values=f,witnesses=list(map(int,r[6::2])),canonical=list(variants[k]),perm=list(PERMS[k])))
 return rows

def main():
 rows=load();witnesses=0;activation=0;reducible=0;exceptions=[]
 for r in rows:
  a,_=decode(r['graph6']);v=r['removed'];ps=r['ports'];assert sorted(a[v])==ps
  assert all(len(ns)==3 for ns in a)
  for i,(value,mask) in enumerate(zip(r['values'],r['witnesses'])):
   if value==NEG:continue
   assert not(mask>>v&1) and 0<=mask<1<<len(a)
   assert 2*mask.bit_count()-(len(a)-1)==value
   states=[]
   for u in range(len(a)):
    if mask>>u&1:
     d=sum(bool(mask>>t&1) for t in a[u]);assert d in ([1,2] if u in ps else [2])
   for p in ps:states.append(3-sum(bool(mask>>t&1) for t in a[p]) if mask>>p&1 else 0)
   assert tuple(states)==STATES[i];witnesses+=1
  f=r['values']
  if f[0]>=-1 and all(max(f[i],f[j])>=1 for i,j in [(8,17),(20,23),(24,25)]):reducible+=1
  if f[0]>=0 or f[0]+max(f[1],f[3],f[9])>=0:activation+=1
  else:exceptions.append(dict(graph6=r['graph6'],removed=v,ports=ps,values=f))
 unique={tuple(r['canonical']):r for r in rows}
 minimal=[r for f,r in unique.items() if not any(g!=f and all(a<=b for a,b in zip(g,f)) for g in unique)]
 assert minimal==json.loads((DATA/'minimal_profiles.json').read_text())
 # Every original table dominates a retained table after port relabelling.
 assert all(any(all(a<=b for a,b in zip(r['canonical'],f)) for r in minimal) for f in unique)
 allowed={(0,0),(0,1),(1,0),(2,2)}
 compatibles=[[(i,j) for i,s in enumerate(STATES) for j,t in enumerate(STATES) if all((s[k],t[p[k]]) in allowed for k in range(3))] for p in PERMS]
 lower=1000;count=0
 for r in minimal:
  for t in minimal:
   for ij in compatibles:
    score=max(r['canonical'][i]+t['canonical'][j] for i,j in ij)
    assert score>=0;lower=min(lower,score);count+=1
 result=dict(original_conjecture_resolved=False,source_graphs=len({r['graph6'] for r in rows}),vertex_deletion_profiles=len(rows),
   local_witnesses_checked=witnesses,unique_canonical_profiles=len(unique),minimal_profiles=len(minimal),
   single_port_criterion_profiles=activation,reducible_profiles=reducible,exceptions=exceptions,pair_orientation_checks=count,
   minimum_certified_doubled_surplus=lower,
   limitation='Positive certificates only: this verifier does not independently prove profile upper bounds or infeasible states.')
 (ROOT/'round21_verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='exceptions'}))
if __name__=='__main__':main()
