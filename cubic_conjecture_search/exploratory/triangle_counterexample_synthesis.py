"""CEGIS directly targeting cubic counterexamples with a prescribed triangle.
No auxiliary failure is reported as a counterexample. UNKNOWN is inconclusive.
"""
import argparse,json,sys,time
from pathlib import Path
import z3
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_round12 import decode
from rooted_synthesis import good_masks,encode
from verify_round23 import expand
ROOT=Path(__file__).resolve().parents[1]
def run(args):
 start=time.monotonic();a,_=decode((ROOT/f'round20_data/seed{args.order}.g6').read_text().strip());n=len(a)
 order=[args.vertex]+sorted(a[args.vertex]);order += [v for v in range(n) if v not in order];mp={v:i for i,v in enumerate(order)}
 seed=[{mp[u] for u in a[v]} for v in order]
 variables={(u,v):z3.Bool(f'e{u}_{v}') for v in range(1,n) for u in range(1,v)}
 def edge(u,v):return variables[min(u,v),max(u,v)]
 solver=z3.SolverFor('QF_FD');solver.set(timeout=args.query_ms,random_seed=2026102824)
 for v in range(1,n):solver.add(z3.PbEq([(edge(u,v),1) for u in range(1,n) if u!=v],2 if v<=3 else 3))
 refs=[x for (u,v),x in variables.items() if v in seed[u]]
 solver.add(z3.PbGe([(x,1) for x in refs],len(refs)-args.radius))
 triangle={0,n,n+1};fixed={frozenset(e) for e in [(0,n),(n,n+1),(n+1,0),(0,1),(n,2),(n+1,3)]}
 def he(u,v):
  if u in triangle or v in triangle:return z3.BoolVal(frozenset([u,v]) in fixed)
  return edge(u,v)
 cuts=set();records=[];threshold=n//2+1
 def forbid(mask):
  if mask in cuts:return
  vs=[v for v in range(n+2) if mask>>v&1];assert len(vs)>=threshold
  solver.add(z3.Not(z3.And([z3.PbEq([(he(u,v),1) for u in vs if u!=v],2) for v in vs])));cuts.add(mask)
 hs,_,_=expand(seed,0)
 for mask in good_masks(hs,threshold):forbid(mask)
 initial=len(cuts);status='iteration_limit'
 for iteration in range(100):
  if time.monotonic()-start>=args.seconds:status='wall_time_limit';break
  st=solver.check()
  if st!=z3.sat:status=str(st);break
  model=solver.model();parent=[set() for _ in range(n)]
  for v in [1,2,3]:parent[0].add(v);parent[v].add(0)
  for (u,v),x in variables.items():
   if z3.is_true(model.eval(x)):parent[u].add(v);parent[v].add(u)
  h,_,_=expand(parent,0);masks=good_masks(h,threshold)
  r=dict(parent_graph6=encode(parent),expanded_graph6=encode(h),large_set_count=len(masks),witness=max(masks,key=int.bit_count,default=0))
  records.append(r)
  if not masks:status='COUNTEREXAMPLE_CANDIDATE';break
  for mask in masks:forbid(mask)
  print(n,iteration,len(masks),len(cuts),round(time.monotonic()-start,2),flush=True)
 result=dict(parent_order=n,expanded_order=n+2,original_seed_vertex=args.vertex,seed_graph6=encode(seed),
  removed_edge_radius=args.radius,fixed_neighbours=[1,2,3],status=status,
  unknown_reason=solver.reason_unknown() if status=='unknown' else None,
  initial_cuts=initial,total_cuts=len(cuts),forbidden_masks=sorted(cuts),records=records,
  elapsed_seconds=time.monotonic()-start,original_conjecture_resolved=False)
 args.output.write_text(json.dumps(result,indent=2)+'\n');print('DONE',n,status,len(records),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--order',type=int,required=True);p.add_argument('--vertex',type=int,default=0)
 p.add_argument('--radius',type=int,default=6);p.add_argument('--query-ms',type=int,default=20000);p.add_argument('--seconds',type=int,default=150);p.add_argument('--output',type=Path,required=True);run(p.parse_args())
