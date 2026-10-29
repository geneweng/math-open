"""All boundary-profile orientations of two selected pieces on K5."""
import itertools
import json
import sys
from pathlib import Path
from ortools.sat.python import cp_model

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_round28 import Library,MAPS,STATES,PERMS
from verify_round29 import expand
lib=Library();options={}
for rid in (2,24):
    f=lib.reduced[rid]['values'];seen={}
    for p,m in enumerate(MAPS):seen.setdefault(tuple(f[j] for j in m),p)
    options[rid]=list(seen.values());assert len(seen)==3
ns=[[v for v in range(5) if v!=u] for u in range(5)]
joins=[(4*u+ns[u].index(v),4*v+ns[v].index(u)) for u in range(5) for v in range(u+1,5)]
records=[]
for count in (1,2):
    rids=[2]*count+[24]*(5-count)
    for orientations in itertools.product(*(options[r] for r in rids)):
        model=cp_model.CpModel();ports=[];scores=[]
        for i,(r,p) in enumerate(zip(rids,orientations)):
            f=[lib.reduced[r]['values'][j] for j in MAPS[p]]
            table=[list(STATES[s])+[v] for s,v in enumerate(f) if v>-1000000]
            ps=[model.NewIntVar(0,2,f'p{i}_{j}') for j in range(4)]
            sc=model.NewIntVar(min(t[-1] for t in table),max(t[-1] for t in table),f's{i}')
            model.AddAllowedAssignments(ps+[sc],table);ports.extend(ps);scores.append(sc)
        for a,b in joins:model.AddAllowedAssignments([ports[a],ports[b]],[(0,0),(0,1),(1,0),(2,2)])
        model.Maximize(sum(scores));sol=cp_model.CpSolver();sol.parameters.max_time_in_seconds=1
        sol.parameters.num_search_workers=1;status=sol.Solve(model)
        rec=dict(open_count=count,profiles=rids,orientations=orientations,status=sol.StatusName(status))
        if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
            states=[sum(sol.Value(ports[4*i+j])*3**j for j in range(4)) for i in range(5)]
            rr=[];pp=[];source=[]
            for r,p,st in zip(rids,orientations,states):
                item=lib.item(24*r+p);rr.append(item['raw']);pp.append(item['ports'])
                first=MAPS[PERMS.index(tuple(lib.reduced[r]['permutation']))]
                source.append(first[MAPS[p][st]])
            a,s=expand(rr,pp,joins,source);value=sum(sol.Value(x) for x in scores)
            assert 2*len(s)-len(a)==value
            rec.update(states=states,order=len(a),doubled_surplus=value,selected=sorted(s))
            assert value>=0,'Potential original counterexample requires independent certification'
        records.append(rec)
    print('DONE open_count',count,'records',len(records),flush=True)
(ROOT/'round29_data/k5_exhaust.json').write_text(json.dumps(dict(options=options,joins=joins,records=records),indent=2)+'\n')
