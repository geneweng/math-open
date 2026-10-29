"""Check direct triangle-search witnesses and their lifted good sets.
The large reconnection enumeration is not independently regenerated here.
"""
import json
from collections import Counter
from pathlib import Path
from verify_round12 import decode
from verify_round14 import cycle_space_good_sets
from verify_round23 import expand,good
from verify_boundary_profiles import exact_table,STATES
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round24_data'
def edges(a):return {(v,u) for v in range(len(a)) for u in a[v] if v<u}
def selected(mask,n):
 assert 0<=mask<1<<n
 return {v for v in range(n) if mask>>v&1}
def main():
 types=Counter();lifts=0;counts={};solver=[]
 for n in [24,26]:
  seed,_=decode((ROOT/f'round20_data/seed{n}.g6').read_text().strip());se=edges(seed)
  for line in (DATA/f'ball{n}_novel.txt').read_text().splitlines():
   fields=line.split();kind=fields[0];types[kind]+=1
   assert kind in ['STRICT','HALF'], 'An expanded fallback or counterexample requires explicit examination.'
   a,_=decode(fields[1]);S=selected(int(fields[2]),len(a));assert len(a)==n and all(len(ns)==3 for ns in a)
   assert len(se-edges(a))<=4 and good(a,S)
   assert len(S)>n//2 if kind=='STRICT' else len(S)>=n//2
   vertices=range(n) if kind=='STRICT' else S
   for v in vertices:
    h,triangle,ns=expand(a,v)
    T=(S-{v})|{w for w,u in zip(triangle,ns) if u in S} if v in S else S
    assert len(T)>=n//2+1 and good(h,T);lifts+=1
  counts[n]=[list(map(int,l.split())) for l in (DATA/f'ball{n}_counts.txt').read_text().splitlines()]
  previous=[list(map(int,l.split())) for l in (ROOT/f'round20_data/ball{n}_counts.txt').read_text().splitlines()]
  assert [r[:2] for r in counts[n]]==[r[:2] for r in previous]
  r=json.loads((DATA/f'triangle{n}.json').read_text());source,_=decode(r['seed_graph6']);source_edges=edges(source)
  for c in r['records']:
   parent,_=decode(c['parent_graph6']);h,_=decode(c['expanded_graph6'])
   assert len(parent)==n and all(len(ns)==3 for ns in parent) and parent[0]=={1,2,3}
   assert len(source_edges-edges(parent))<=r['removed_edge_radius']
   parent_sets=cycle_space_good_sets(parent)
   assert max(m.bit_count() for m in parent_sets)>=n//2, 'Original parent counterexample candidate'
   expected=edges(parent)-{(0,1),(0,2),(0,3)}
   expected|={(0,1),(2,n),(3,n+1),(0,n),(0,n+1),(n,n+1)}
   assert edges(h)==expected and all(len(ns)==3 for ns in h)
   S=selected(c['witness'],len(h));assert len(S)>=len(h)//2 and good(h,S)
   masks=cycle_space_good_sets(h);large=[m for m in masks if m.bit_count()>=len(h)//2]
   assert len(large)==c['large_set_count'] and max(m.bit_count() for m in masks)==len(S)
  solver.append(dict(parent_order=n,status=r['status'],expanded_candidates=len(r['records']),total_cuts=r['total_cuts']))
 # Reproduce the small critical-star edge-join calculation, without a solver.
 code='M???FBOq@KF?D_B_?';a,_=decode(code);K={(0,0),(0,1),(1,0),(2,2)};low=10000;join_count=0
 old=[list(map(int,l.split()[3:])) for l in (ROOT/'two_pole_profiles.txt').read_text().splitlines()]
 for u,v in sorted(edges(a)):
  f,_=exact_table(code,[u,v])
  for t in old:
   for reverse in [False,True]:
    value=max(f[i]+t[j] for i,s in enumerate(STATES) for j,z in enumerate(STATES) if all((s[k],z[1-k] if reverse else z[k]) in K for k in [0,1]))
    assert value>=0;low=min(low,value);join_count+=1
 result=dict(original_conjecture_resolved=False,new_witness_types=dict(types),explicit_lifts_checked=lifts,
  parent_reconnection_records=sum(r[1] for rows in counts.values() for r in rows),
  indexed_triangle_expansions=sum(n*r[1] for n,rows in counts.items() for r in rows),
  reconnection_counts=counts,synthesis=solver,critical_star_pair_checks=join_count,
  critical_star_minimum_doubled_surplus=low,
  limitation='Independent checks cover retained witnesses and all solver candidates. Completeness of the large edge balls relies on the C++ reconnection enumeration; its generator was separately tested in round 20.')
 (ROOT/'round24_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
