import itertools,json,random,time,sys
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model

OUT=Path('tmp/cubic_round3');rng=random.Random(2601026)
profiles=[]
for line in (OUT/'three_pole_profiles.txt').read_text().splitlines():
    t=line.split();a=list(map(int,t[5:]));profiles.append({'graph6':t[0],'deleted':int(t[1]),'ports':list(map(int,t[2:5])),'a':a,'rows':[[i%3,i//3%3,i//9,x]for i,x in enumerate(a)if x>-1000]})
compatible={(0,0),(0,1),(1,0),(2,2)}
# Exhaust all ordered endpoint correspondences for two fragments joined by three edges.
best=100;pair=None;count=0
for i,p in enumerate(profiles):
    for j,q in enumerate(profiles[:i+1]):
        for perm in itertools.permutations(range(3)):
            val=max(r[3]+s[3]for r in p['rows']for s in q['rows']if all((r[k],s[perm[k]])in compatible for k in range(3)))
            count+=1
            if val<best:best=val;pair=(i,j,perm)
            if val<0:raise RuntimeError(('COUNTEREXAMPLE',i,j,perm,val))
print('all pairs',count,'minimum surplus',best,'pair',pair,flush=True)


def solve(base,choices,orders):
    model=cp_model.CpModel();state={};scores=[]
    for v,pid in enumerate(choices):
        p=profiles[pid];xs=[model.new_int_var(0,2,f'x{v}_{k}')for k in range(3)]
        score=model.new_int_var(min(r[3]for r in p['rows']),max(r[3]for r in p['rows']),f'w{v}')
        model.add_allowed_assignments(xs+[score],p['rows']);scores.append(score)
        for k,u in enumerate(orders[v]):state[v,u]=xs[k]
    for u,v in base.edges:model.add_allowed_assignments([state[u,v],state[v,u]],list(compatible))
    model.maximize(sum(scores));solver=cp_model.CpSolver();solver.parameters.num_search_workers=1;solver.parameters.max_time_in_seconds=2
    status=solver.solve(model)
    return solver.objective_value,solver.best_objective_bound,solver.status_name(status)

records=[];globalbest=100
for n in (4,6,8,10,12,16,20):
    current=None;currentval=100
    for trial in range(700):
        if trial%100==0:
            base=nx.random_regular_graph(3,n,seed=rng.randrange(2**31));orders={v:list(base[v])for v in base};choices=[rng.randrange(len(profiles))for v in base]
            for v in base:rng.shuffle(orders[v])
        elif current is not None:
            choices=list(current[0]);orders={v:list(current[1][v])for v in base}
            for _ in range(1 if rng.random()<.8 else 2):
                v=rng.randrange(n);choices[v]=rng.randrange(len(profiles));rng.shuffle(orders[v])
        value,bound,status=solve(base,choices,orders)
        if value<globalbest:globalbest=value;print('new minimum',n,trial,value,bound,status,flush=True)
        if value<=currentval or rng.random()<.03 or trial%100==0:current=(choices,orders);currentval=value
        if bound<0:
            record={'base_edges':list(base.edges),'choices':choices,'orders':orders,'profiles':profiles,'value':value,'upper_bound':bound,'status':status}
            (OUT/'pole_counterexample.json').write_text(json.dumps(record,indent=2));raise RuntimeError('COUNTEREXAMPLE')
        records.append({'base_order':n,'trial':trial,'value':value,'upper_bound':bound,'status':status})
        if trial%100==99:
            print('progress',n,trial+1,'best',globalbest,flush=True)
            (OUT/'pole_assembly_results.json').write_text(json.dumps({'pair_cases':count,'pair_minimum':best,'records':records,'complete':False}))
(OUT/'pole_assembly_results.json').write_text(json.dumps({'pair_cases':count,'pair_minimum':best,'records':records,'complete':True}))
