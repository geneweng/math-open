"""Recorded exploratory version. Interpret objective values only for
OPTIMAL or FEASIBLE statuses. The saved run contains no UNKNOWN results.
"""
import json,random
from pathlib import Path
from ortools.sat.python import cp_model
OUT=Path('tmp/cubic_round4');ps=json.loads((OUT/'four_pole_network_profiles.json').read_text());rng=random.Random(20261102)

def solve(choices,pairs):
 m=cp_model.CpModel();xs=[];scores=[]
 for v,pid in enumerate(choices):
  rows=ps[pid]['rows'];vs=[m.new_int_var(0,2,f'{v}_{j}')for j in range(4)];xs.extend(vs);w=m.new_int_var(min(r[-1]for r in rows),max(r[-1]for r in rows),f'w{v}');scores.append(w);m.add_allowed_assignments(vs+[w],rows)
 for a,b in pairs:m.add_allowed_assignments([xs[a],xs[b]],[(0,0),(0,1),(1,0),(2,2)])
 m.maximize(sum(scores));s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=.3;status=s.solve(m)
 return s.objective_value,s.best_objective_bound,s.status_name(status)

k4=next(i for i,p in enumerate(ps)if p['graph6']=='C~');ports=ps[k4]['ports'];left=[ports.index(i)for i in(0,1)];right=[ports.index(i)for i in(2,3)]
def ring(n):return [(4*i+right[j],4*((i+1)%n)+left[j])for i in range(n)for j in(0,1)]
print('Franklin validation',solve([k4]*3,ring(3)),flush=True)
records=[];best=100
for n in(3,4,5,6,8,10,12):
 current=None;value=100
 for step in range(2000):
  if step%250==0:
   pairs=ring(n);choices=[k4]*n if step<1000 else[rng.randrange(len(ps))for _ in range(n)]
  else:
   choices=list(current[0]);pairs=list(current[1])
   if rng.random()<.55:
    v=rng.randrange(n);choices[v]=rng.randrange(len(ps))
   else:
    i,j=rng.sample(range(len(pairs)),2);a,b=pairs[i];c,d=pairs[j]
    if rng.random()<.5:c,d=d,c
    if a//4==c//4 or b//4==d//4:continue
    pairs[i]=(a,c);pairs[j]=(b,d)
  val,ub,status=solve(choices,pairs)
  if val<best:best=val;print('new minimum',n,step,val,ub,status,flush=True)
  if ub<0:
   rec={'choices':choices,'pairs':pairs,'value':val,'upper_bound':ub,'status':status}
   (OUT/'stub_counterexample.json').write_text(json.dumps(rec,indent=2));print('COUNTEREXAMPLE',rec,flush=True);raise SystemExit
  if step%250==0 or (status=='OPTIMAL' and val<=value) or rng.random()<.005:current=(choices,pairs);value=val
  records.append({'blocks':n,'step':step,'value':val,'upper_bound':ub,'status':status})
  if step%250==249:print('progress',n,step+1,best,flush=True);(OUT/'stub_results.json').write_text(json.dumps({'complete':False,'records':records}))
(OUT/'stub_results.json').write_text(json.dumps({'complete':True,'records':records}))
