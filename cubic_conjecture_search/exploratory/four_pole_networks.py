"""Recorded exploratory version. UNKNOWN objectives were used in its heuristic
selection and progress minimum; those values are invalid and are excluded from
round4_search_results.json. The upper-bound counterexample test never triggered.
This run is incomplete; do not read it as a proof for all assemblies.
"""
import itertools,json,random,sys,time
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model
sys.path.insert(0,'cubic_conjecture_search/exploratory')
from tight_local_search import franklin

OUT=Path('tmp/cubic_round4');rng=random.Random(20261101)
perms=list(itertools.permutations(range(4)))
remaps=[[sum((i//3**j%3)*3**p[j]for j in range(4))for i in range(81)]for p in perms]

def profile(g,cut):
    h=g.copy();h.remove_edges_from(cut);ports=sum((list(e)for e in cut),[]);a=[sum(1<<u for u in h[v])for v in h];pn={v:i for i,v in enumerate(ports)};scores=[-1000000]*81
    for mask in range(1<<len(g)):
        states=[0]*4;rem=mask;ok=True
        while rem:
            b=rem&-rem;rem-=b;v=b.bit_length()-1;d=(a[v]&mask).bit_count()
            if v in pn:
                if d not in(1,2):ok=False;break
                states[pn[v]]=3-d
            elif d!=2:ok=False;break
        if ok:
            k=sum(s*3**i for i,s in enumerate(states));scores[k]=max(scores[k],2*mask.bit_count()-len(g))
    variants=[tuple(scores[i]for i in remap)for remap in remaps];pi=min(range(24),key=lambda i:variants[i])
    return variants[pi],[ports[j]for j in perms[pi]]

profiles=[];seen=set()
graphs=[franklin()]
# Include the underlying fragments from the 111 difficult chain profiles.
cases=[]
for line in Path('tmp/cubic_full/profiles_diag0.txt').read_text().splitlines():
 t=line.split();cases.append((t[0],[(int(t[1]),int(t[2])),(int(t[3]),int(t[4]))]))
g=graphs[0];code=nx.to_graph6_bytes(g,header=False).decode().strip()
for e,f in itertools.combinations(g.edges(),2):
 if len(set(e+f))==4:cases.append((code,[e,f]))
for code,cut in cases:
 g=nx.from_graph6_bytes(code.encode());a,ports=profile(g,cut)
 if a in seen:continue
 seen.add(a);profiles.append({'graph6':code,'cut':cut,'ports':ports,'a':a,'rows':[[*(i//3**j%3 for j in range(4)),v]for i,v in enumerate(a)if v>-1000000]})
print('distinct four-pole profiles',len(profiles),flush=True);(OUT/'four_pole_network_profiles.json').write_text(json.dumps(profiles,indent=2))


def solve(base,choices,orders):
 m=cp_model.CpModel();state={};scores=[]
 for v,pid in enumerate(choices):
  rows=profiles[pid]['rows'];xs=[m.new_int_var(0,2,f'x{v}_{j}')for j in range(4)];w=m.new_int_var(min(r[-1]for r in rows),max(r[-1]for r in rows),f'w{v}')
  m.add_allowed_assignments(xs+[w],rows);scores.append(w)
  for u,x in zip(orders[v],xs):state[v,u]=x
 for u,v in base.edges:m.add_allowed_assignments([state[u,v],state[v,u]],[(0,0),(0,1),(1,0),(2,2)])
 m.maximize(sum(scores));s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=1
 st=s.solve(m);return s.objective_value,s.best_objective_bound,s.status_name(st)

records=[];best=100
for n in (5,6,7,8,10,12,16,20):
 current=None;value=100
 for step in range(2000):
  if step%200==0:
   base=nx.random_regular_graph(4,n,seed=rng.randrange(2**31));orders={v:list(base[v])for v in base};choices=[rng.randrange(len(profiles))for v in base]
   for v in base:rng.shuffle(orders[v])
  else:
   choices=list(current[0]);orders={v:list(current[1][v])for v in base}
   for _ in range(1 if rng.random()<.8 else 2):
    v=rng.randrange(n);choices[v]=rng.randrange(len(profiles));rng.shuffle(orders[v])
  nv,ub,status=solve(base,choices,orders)
  if nv<best:best=nv;print('new best',n,step,nv,ub,status,flush=True)
  if ub<0:
   r={'base_edges':list(base.edges),'choices':choices,'orders':orders,'value':nv,'upper_bound':ub,'status':status}
   (OUT/'four_pole_network_counterexample.json').write_text(json.dumps(r,indent=2));print('COUNTEREXAMPLE',r,flush=True);raise SystemExit
  if step%200==0 or nv<=value or rng.random()<.01:current=(choices,orders);value=nv
  records.append({'base_order':n,'step':step,'value':nv,'upper_bound':ub,'status':status})
  if step%200==199:
   print('progress',n,step+1,'global minimum',best,flush=True);(OUT/'four_pole_network_results.json').write_text(json.dumps({'complete':False,'records':records}))
(OUT/'four_pole_network_results.json').write_text(json.dumps({'complete':True,'records':records}))
