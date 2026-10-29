"""Bounded direct search in arbitrary joins of the eight exceptional fragments.
Only OPTIMAL objectives guide descent. Positive witnesses are checked on the
full expanded graphs; UNKNOWN never certifies a bound or a counterexample.
"""
import json,random,sys,time
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_round21 import load,decode,STATES
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'round22_data'
LIB=[r for r in load() if r['values'][0]<0 and r['values'][0]+max(r['values'][i] for i in [1,3,9])<0]

def solve(choices,pairs):
 m=cp_model.CpModel();vs=[];scores=[]
 for v,rid in enumerate(choices):
  f=LIB[rid]['values'];rows=[list(STATES[i])+[value] for i,value in enumerate(f) if value>-1000]
  ports=[m.new_int_var(0,2,f'p{v}_{j}') for j in range(3)]
  score=m.new_int_var(min(r[-1] for r in rows),max(r[-1] for r in rows),f's{v}')
  m.add_allowed_assignments(ports+[score],rows);vs.extend(ports);scores.append(score)
 for a,b in pairs:m.add_allowed_assignments([vs[a],vs[b]],[(0,0),(0,1),(1,0),(2,2)])
 m.maximize(sum(scores));sol=cp_model.CpSolver();sol.parameters.num_search_workers=1;sol.parameters.max_time_in_seconds=.7
 status=sol.solve(m);r=dict(status=sol.status_name(status),seconds=sol.wall_time)
 if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  r.update(score=sum(sol.value(s) for s in scores),states=[[sol.value(vs[3*i+j]) for j in range(3)] for i in range(len(choices))])
 return r

def expand(choices,pairs,states):
 adj=[];selected=[];ports=[]
 for rid,st in zip(choices,states):
  r=LIB[rid];a,_=decode(r['graph6']);old=[v for v in range(len(a)) if v!=r['removed']];mp={v:len(adj)+j for j,v in enumerate(old)}
  adj.extend([{mp[u] for u in a[v] if u in mp} for v in old]);ports.extend(mp[p] for p in r['ports'])
  mask=r['witnesses'][sum(st[j]*3**j for j in range(3))]
  selected.extend(mp[v] for v in old if mask>>v&1)
 for a,b in pairs:
  u,v=ports[a],ports[b];assert u!=v and v not in adj[u];adj[u].add(v);adj[v].add(u)
 s=set(selected);assert all(len(ns)==3 for ns in adj)
 assert all(len(adj[v]&s)==2 for v in s)
 return adj,selected

def main():
 rng=random.Random(2026102822);records=[];start=time.monotonic()
 for n in [4,6,8,10,12,16,20]:
  base=nx.random_regular_graph(3,n,seed=rng.randrange(1<<30))
  while not nx.is_connected(base):base=nx.random_regular_graph(3,n,seed=rng.randrange(1<<30))
  ns={v:sorted(base[v]) for v in base};seedpairs=[(3*u+ns[u].index(v),3*v+ns[v].index(u)) for u,v in base.edges()]
  current=None;best=None
  for trial in range(60):
   if trial%15==0 or current is None:
    choices=[rng.randrange(len(LIB)) for _ in range(n)];pairs=list(seedpairs)
   else:
    choices=list(current[0]);pairs=list(current[1])
    if rng.random()<.55:choices[rng.randrange(n)]=rng.randrange(len(LIB))
    else:
     i,j=rng.sample(range(len(pairs)),2);a,b=pairs[i];c,d=pairs[j]
     if rng.random()<.5:c,d=d,c
     if a//3==c//3 or b//3==d//3:continue
     pairs[i]=(a,c);pairs[j]=(b,d)
   r=solve(choices,pairs);r.update(blocks=n,trial=trial,choices=choices,pairs=pairs)
   if 'states' in r:
    adj,w=expand(choices,pairs,r['states']);assert 2*len(w)-len(adj)==r['score']
    r.update(order=len(adj),witness=w)
    if r['status']=='OPTIMAL' and r['score']<0:
     r['counterexample_candidate_adjacency']=[sorted(s) for s in adj];records.append(r);break
    if r['status']=='OPTIMAL' and (best is None or r['score']<=best or rng.random()<.02):
     current=(choices,pairs);best=r['score']
   records.append(r)
  print(n,len(records),min((r.get('score',10000) for r in records)),flush=True)
  (DATA/'assemblies.json').write_text(json.dumps(dict(library=LIB,records=records,elapsed_seconds=time.monotonic()-start,original_conjecture_resolved=False),indent=2)+'\n')
  if any(r.get('score',0)<0 and r['status']=='OPTIMAL' for r in records):break
if __name__=='__main__':main()
