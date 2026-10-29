"""Direct original-counterexample synthesis in connected bipartite cubic order 26.

No radius or template restriction. Wall/query limits remain inconclusive.
The fixed first row/column only label one edge and its endpoint neighbours.
"""
import json
from pathlib import Path
import sys
import time
import z3

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'exploratory'))
from rooted_synthesis import good_masks,encode


def main():
    start=time.monotonic();side=13;n=26
    x={(i,j):z3.Bool(f'e_{i}_{j}') for i in range(side) for j in range(side)}
    solver=z3.SolverFor('QF_FD');solver.set(timeout=5000,random_seed=20261029)
    for i in range(side):solver.add(z3.PbEq([(x[i,j],1) for j in range(side)],3))
    for j in range(side):solver.add(z3.PbEq([(x[i,j],1) for i in range(side)],3))
    for j in range(side):solver.add(x[0,j]==(j<3))
    for i in range(side):solver.add(x[i,0]==(i<3))
    cuts=set();records=[];connectivity=[];queries=0;status='wall_time_limit';reason=None
    def save():
        result=dict(status=status,reason=reason,order=n,part_size=side,threshold=14,
                    wall_limit_seconds=60,query_limit_ms=5000,queries=queries,
                    elapsed_seconds=time.monotonic()-start,total_forbidden_sets=len(cuts),
                    connectivity_cuts=connectivity,records=records,
                    original_conjecture_resolved=False,
                    scope='Connected bipartite cubic order 26; no seed-distance restriction. Limits are inconclusive.')
        (HERE/'search.json').write_text(json.dumps(result,indent=2)+'\n')
    while time.monotonic()-start<60:
        queries+=1;answer=solver.check()
        if answer!=z3.sat:
            status=str(answer);reason=solver.reason_unknown() if answer==z3.unknown else None
            break
        model=solver.model();a=[set() for _ in range(n)]
        for (i,j),v in x.items():
            if z3.is_true(model.eval(v)):a[i].add(side+j);a[side+j].add(i)
        seen={0};todo=[0]
        for v in todo:
            for u in a[v]-seen:seen.add(u);todo.append(u)
        if len(seen)!=n:
            crossing=[v for (i,j),v in x.items() if (i in seen)!=((side+j) in seen)]
            solver.add(z3.Or(crossing));connectivity.append(sorted(seen));continue
        masks=good_masks(a,14)
        row=dict(graph6=encode(a),large_good_sets=masks,
                 witness=max(masks,key=int.bit_count,default=None))
        records.append(row)
        if not masks:
            status='counterexample_candidate_requires_independent_verification';save();break
        for mask in masks:
            if mask in cuts:continue
            left=[i for i in range(side) if mask>>i&1]
            right=[j for j in range(side) if mask>>(side+j)&1]
            assert len(left)==len(right) and len(left)>=7
            constraints=[z3.PbEq([(x[i,j],1) for j in right],2) for i in left]
            constraints += [z3.PbEq([(x[i,j],1) for i in left],2) for j in right]
            solver.add(z3.Not(z3.And(constraints)));cuts.add(mask)
        save()
        print('rejected',len(records),'maximum',row['witness'].bit_count(),
              'cuts',len(cuts),'seconds',round(time.monotonic()-start,1),flush=True)
    save();print('STOP',status,reason,flush=True)


if __name__=='__main__':main()
