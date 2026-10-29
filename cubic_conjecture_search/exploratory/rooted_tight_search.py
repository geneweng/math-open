import json,sys,random
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model
sys.path.insert(0,'cubic_conjecture_search/exploratory')
from tight_local_search import initial
from local_search import mutate


def optimize(h,limit=1,weights=None,forced=None):
 m=cp_model.CpModel();x={v:m.new_bool_var(str(v))for v in h}
 for v in h:m.add(sum(x[u]for u in h[v])==2).only_enforce_if(x[v])
 if forced:
  for v,b in forced.items():m.add(x[v]==b)
 if weights is None:weights={v:1 for v in h}
 m.maximize(sum(weights[v]*x[v]for v in h));s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=limit;st=s.solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,s.best_objective_bound,s.status_name(st),[]
 chosen=[v for v in h if s.value(x[v])]
 assert all(d==2 for _,d in h.subgraph(chosen).degree())
 return int(s.objective_value),s.best_objective_bound,s.status_name(st),chosen

records=[]
for n in (24,26,42):
 g=initial(n)
 for edge in g.edges:
  h=g.copy();h.remove_edge(*edge)
  b,ub,status,chosen=optimize(h,3)
  a,ua,statusa,chosena=optimize(g,3,forced={edge[0]:1,edge[1]:1})
  r={'order':n,'edge':edge,'avoid_deleted':b,'avoid_bound':ub,'through_edge':a,'through_bound':ua,'statuses':[status,statusa]};records.append(r)
  if ub<=n/2 and ua+ub<n:
   print('COUNTEREXAMPLE_CAP',r,flush=True);Path('tmp/cubic_round3/cap_counterexample.json').write_text(json.dumps({'edges':list(g.edges),'record':r},indent=2));raise SystemExit
 print('edge profiles done',n,'min deleted',min(r['avoid_deleted']for r in records if r['order']==n),flush=True)
Path('tmp/cubic_round3/tight_edge_profiles.json').write_text(json.dumps(records,indent=2))

rng=random.Random(20261029);stats=[]
for n in (24,26,42):
 base=initial(n);e=rng.choice(list(base.edges));base.remove_edge(*e);g=base.copy();weights={v:int(d==3)for v,d in g.degree};target=sum(weights.values())//2
 val,ub,st,chosen=optimize(g,3,weights);best=val;accepted=0;unknown=0
 print('branch initial',n,target,val,ub,flush=True)
 for step in range(3000):
  h=mutate(g,rng,1 if rng.random()<.9 else 2)
  nv,nu,ns,nc=optimize(h,.5,weights)
  if ns!='OPTIMAL':unknown+=1
  if nu<target:
   rec={'order':n,'target':target,'value':nv,'upper_bound':nu,'edges':list(h.edges),'chosen':nc,'status':ns,'completion_order':n+26}
   Path('tmp/cubic_round3/branch_counterexample.json').write_text(json.dumps(rec,indent=2));print('COUNTEREXAMPLE',rec,flush=True);raise SystemExit
  if nv is not None and nv<best:best=nv;print('improved',n,step,best,flush=True)
  if ns=='OPTIMAL' and nv<=val:g=h;val=nv;accepted+=1
  if step%500==499:print('branch progress',n,step+1,best,accepted,unknown,flush=True)
 stats.append({'order':n,'proposals':3000,'target':target,'best':best,'accepted':accepted,'not_optimal':unknown})
 Path('tmp/cubic_round3/branch_local_search.json').write_text(json.dumps(stats,indent=2))
