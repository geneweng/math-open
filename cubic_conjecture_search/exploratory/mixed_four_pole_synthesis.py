"""Counterexample-guided search of mixed four-port pieces on K5.

Finite search domain; UNKNOWN is never treated as an impossibility proof.
"""
import itertools
import json
import sys
import time
from pathlib import Path
from ortools.sat.python import cp_model

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_round26 import read_rows
from verify_round12 import decode
from verify_bridge_reduction import graph,edges,good
from verify_round28 import MAPS,PERMS,STATES

DATA=ROOT/'round29_data'


def main():
    DATA.mkdir(exist_ok=True)
    library=json.loads((ROOT/'round27_data/canonical.json').read_text())['profiles']
    raw=read_rows(ROOT/'round27_data/profiles.txt');closed=[];opened=[]
    for i,r in enumerate(library):
        f=r['values']
        c=f[0]>=0 or all(f[3**a+3**b]>=0 for a,b in itertools.combinations(range(4),2))
        o=all(f[2*3**a+2*3**b]>=0 or all(f[2*3**a+2*3**b+3**d]>=0
              for d in range(4) if d not in (a,b)) for a,b in itertools.combinations(range(4),2))
        if c and not o and f[0]<0:closed.append(i)
        if o and not c:opened.append(i)
    opened=[opened[i*(len(opened)-1)//9] for i in range(10)]
    selected=closed+opened;options=[]
    for r in selected:
        for p,mapping in enumerate(MAPS):
            options.append(dict(profile=r,permutation=p,values=[library[r]['values'][j] for j in mapping],
                                kind='closed' if r in closed else 'open'))
    assert len(closed)==10 and len(options)==480
    neighbours=[[v for v in range(5) if v!=u] for u in range(5)]
    joins=[(4*u+neighbours[u].index(v),4*v+neighbours[v].index(u)) for u in range(5) for v in range(u+1,5)]
    model=cp_model.CpModel()
    choice=[model.NewIntVar(0,len(options)-1,f'c{i}') for i in range(5)]
    model.Add(choice[0]<240);model.Add(choice[1]>=240)
    records=[];start=time.monotonic();status='wall_time_limit';attempts=0
    while time.monotonic()-start<120 and len(records)<500:
        solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=2
        solver.parameters.num_search_workers=1
        st=solver.Solve(model);attempts+=1
        if st==cp_model.INFEASIBLE:status='restricted_domain_unsat';break
        if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):continue
        ids=[solver.Value(c) for c in choice]
        witness=cp_model.CpModel();ports=[];scores=[]
        for i,j in enumerate(ids):
            f=options[j]['values'];table=[list(STATES[s])+[v] for s,v in enumerate(f) if v>-1000000]
            ps=[witness.NewIntVar(0,2,f'p{i}_{j}') for j in range(4)]
            sc=witness.NewIntVar(min(t[-1] for t in table),max(t[-1] for t in table),f's{i}')
            witness.AddAllowedAssignments(ps+[sc],table);ports.extend(ps);scores.append(sc)
        for a,b in joins:witness.AddAllowedAssignments([ports[a],ports[b]],[(0,0),(0,1),(1,0),(2,2)])
        witness.Maximize(sum(scores));ws=cp_model.CpSolver();ws.parameters.max_time_in_seconds=.3
        ws.parameters.num_search_workers=1;wst=ws.Solve(witness)
        if wst not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
            status='witness_solver_inconclusive';break
        value=sum(ws.Value(s) for s in scores)
        states=[sum(ws.Value(ports[4*i+j])*3**j for j in range(4)) for i in range(5)]
        if value<0:
            status='candidate_requires_independent_verification' if ws.BestObjectiveBound()<0 else 'witness_solver_inconclusive'
            break
        es=[];n=0;selected_vertices=set();allports=[]
        for i,j in enumerate(ids):
            opt=options[j];r=library[opt['profile']];rr=raw[r['row']]
            first=MAPS[PERMS.index(tuple(r['permutation']))];mapping=[first[t] for t in MAPS[opt['permutation']]]
            a,_=decode(rr['code']);vs=sorted(set(range(len(a)))-set(rr['removed']));ren={v:n+k for k,v in enumerate(vs)};n+=len(vs)
            es.extend((ren[u],ren[v]) for u,v in edges(a) if u in ren and v in ren)
            allports.extend(ren[rr['ports'][next(t for t in range(4) if mapping[3**k]==3**t)]] for k in range(4))
            mask=rr['witnesses'][mapping[states[i]]]
            selected_vertices.update(ren[v] for v in vs if mask>>v&1)
        es.extend((allports[a],allports[b]) for a,b in joins)
        a=graph(n,es);assert all(len(ns)==3 for ns in a) and good(a,selected_vertices)
        assert 2*len(selected_vertices)-n==value
        rec=dict(options=ids,states=states,order=n,doubled_surplus=value,
                 solver_status=ws.StatusName(wst),selected=sorted(selected_vertices))
        records.append(rec)
        # Any actual nonnegative witness is a valid exclusion cut, even if
        # it was not certified optimal by the witness solver.
        terms=[]
        for i,state in enumerate(states):
            vals=[o['values'][state] for o in options]
            term=model.NewIntVar(min(vals),max(vals),f'cut{len(records)}_{i}')
            model.AddElement(choice[i],vals,term);terms.append(term)
        model.Add(sum(terms)<=-2)
        if len(records)%20==0:print('cuts',len(records),'seconds',round(time.monotonic()-start,1),flush=True)
    result=dict(original_conjecture='unresolved',status=status,options=options,joins=joins,
                records=records,attempts=attempts,seconds=time.monotonic()-start,
                scope='Only 20 selected fragment profiles, their 24 port orders, and K5 incidence. '
                      'Block 0 closed and block 1 open; no conclusion outside this restricted domain.')
    (DATA/'mixed_synthesis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(status,'cuts',len(records),'seconds',round(result['seconds'],1),flush=True)


if __name__=='__main__':main()
