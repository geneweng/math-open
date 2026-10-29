"""Bounded CEGIS search targeting an original-conjecture counterexample.
The 25-vertex rooted search fixes its two neighbours and an edge-distance
radius of six from a retained sharp-parent seed. No timeout is UNSAT.
"""
import json,sys,time
from pathlib import Path
import z3
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_round12 import decode
from rooted_synthesis import good_masks,encode
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'round34_data'

def main():
 start=time.monotonic();seedrow=json.loads((DATA/'seed.json').read_text());old,_=decode(seedrow['graph6']);r=seedrow['root'];order=[r]+sorted(old[r]);order += [v for v in range(len(old)) if v not in order];rename={v:i for i,v in enumerate(order)}
 seed=[{rename[u] for u in old[v]} for v in order];n=25
 var={(u,v):z3.Bool(f'e{u}_{v}') for v in range(1,n) for u in range(v)}
 edge=lambda u,v:var[min(u,v),max(u,v)]
 solver=z3.SolverFor('QF_FD');solver.set(timeout=30000,random_seed=340034)
 for v in range(n):solver.add(z3.PbEq([(edge(u,v),1) for u in range(n) if u!=v],2 if v==0 else 3))
 for v in range(1,n):solver.add(edge(0,v)==(v in (1,2)))
 solver.add(z3.Not(edge(1,2)))
 reference=[edge(u,v) for v in range(n) for u in seed[v] if u<v]
 solver.add(z3.PbGe([(x,1) for x in reference],len(reference)-6))
 cuts=set();records=[];connectivity_cuts=0;status='wall_time_limit'
 def forbidden(s):
  return (s&1 and s.bit_count()>=13) or (not s&1 and s.bit_count()>=14) or (not s&7 and s.bit_count()>=11)
 def forbid(s):
  assert forbidden(s)
  if s in cuts:return
  vs=[v for v in range(n) if s>>v&1]
  solver.add(z3.Not(z3.And([z3.PbEq([(edge(u,v),1) for u in vs if u!=v],2) for v in vs])))
  cuts.add(s)
 for s in good_masks(seed,11):
  if forbidden(s):forbid(s)
 initial=len(cuts)
 def save():
  result=dict(status=status,seconds=time.monotonic()-start,root_order=n,radius=6,query_timeout_ms=30000,seed=encode(seed),initial_cuts=initial,total_cuts=len(cuts),connectivity_cuts=connectivity_cuts,records=records,
   scope='Bounded labelled search near one seed. An unknown/timeout result is inconclusive; candidate counterexamples require independent verification.')
  (DATA/'synthesis.json').write_text(json.dumps(result,indent=2)+'\n')
 while time.monotonic()-start<360:
  answer=solver.check()
  if answer!=z3.sat:
   status=str(answer);save();print('STOP',status,solver.reason_unknown() if answer==z3.unknown else '',flush=True);return
  model=solver.model();a=[set() for _ in range(n)]
  for (u,v),x in var.items():
   if z3.is_true(model.eval(x)):a[u].add(v);a[v].add(u)
  # The suppressed parent edge is non-bridging exactly when Q-root is connected.
  seen={1};todo=[1]
  for u in todo:
   for v in a[u]-seen-{0}:seen.add(v);todo.append(v)
  if len(seen)!=n-1:
   solver.add(z3.Or([edge(u,v) for u in seen for v in range(1,n) if v not in seen]));connectivity_cuts+=1;continue
  masks=good_masks(a,11)
  wa=max((s for s in masks if s&1),key=int.bit_count,default=0)
  wb=max((s for s in masks if not s&1),key=int.bit_count,default=0)
  wc=max((s for s in masks if not s&7),key=int.bit_count,default=0)
  A=wa.bit_count() if wa else 10;B=wb.bit_count() if wb else 10;C=wc.bit_count() if wc else 10
  upper0=max(2*B,A+B);upper1=max(2*max(B,A+1),C+3+max(B,A+1))
  row=dict(graph6=encode(a),root=0,witnesses=dict(A=wa,B=wb,C=wc),upper_bounds=dict(A=A,B=B,C=C),violating_masks=[s for s in masks if forbidden(s)])
  records.append(row)
  if upper0<25 or upper1<27:
   status='candidate_requires_independent_verification';save();print('CANDIDATE',row['graph6'],upper0,upper1,flush=True);return
  for s in row['violating_masks']:forbid(s)
  assert row['violating_masks']
  save();print('CANDIDATE REJECTED',len(records),'bounds',A,B,C,'cuts',len(cuts),'seconds',round(time.monotonic()-start,1),flush=True)
 save();print('STOP wall_time_limit',flush=True)
if __name__=='__main__':main()
