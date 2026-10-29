"""Bounded CEGIS for the original conjecture, without auxiliary inequalities.

All labelled cubic graphs within a specified edge-deletion radius are allowed,
including disconnected ones. UNSAT only excludes this neighbourhood. UNKNOWN
is inconclusive. The exact oracle uses vertex assignments and degree propagation.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
import time
import z3
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_round12 import decode
from rooted_synthesis import good_masks, encode
ROOT=Path(__file__).resolve().parents[1]

def run(args):
    start=time.monotonic()
    rows=[line.split() for line in gzip.open(ROOT/'round18_data/descent_best.txt.gz','rt')]
    rows=[r for r in rows if ord(r[0][0])-63==args.order and int(r[1])==args.order//2]
    row=min(rows,key=lambda r:(int(r[2]),r[0]))
    seed,_=decode(row[0]);n=len(seed);threshold=n//2
    variables={(u,v):z3.Bool(f'e{u}_{v}') for v in range(n) for u in range(v)}
    def edge(u,v):return variables[min(u,v),max(u,v)]
    solver=z3.SolverFor('QF_FD');solver.set(timeout=args.query_ms,random_seed=2026102820)
    for v in range(n):
        solver.add(z3.PbEq([(edge(u,v),1) for u in range(n) if u!=v],3))
    refs=[edge(u,v) for u,v in variables if v in seed[u]]
    solver.add(z3.PbGe([(e,1) for e in refs],len(refs)-args.radius))
    cuts=set();records=[];status_text='iteration_limit'
    def forbid(mask):
        if mask in cuts:return
        vs=[v for v in range(n) if mask>>v&1]
        assert len(vs)>=threshold
        solver.add(z3.Not(z3.And([z3.PbEq([(edge(u,v),1) for u in vs if u!=v],2) for v in vs])))
        cuts.add(mask)
    for mask in good_masks(seed,threshold):forbid(mask)
    initial=len(cuts)
    for iteration in range(args.iterations):
        if time.monotonic()-start>=args.seconds:status_text='wall_time_limit';break
        st=solver.check()
        if st!=z3.sat:
            status_text=str(st);break
        model=solver.model();a=[set() for _ in range(n)]
        for (u,v),x in variables.items():
            if z3.is_true(model.eval(x)):a[u].add(v);a[v].add(u)
        assert all(len(ns)==3 for ns in a)
        masks=good_masks(a,threshold)
        selected=max(masks,key=int.bit_count,default=0)
        records.append(dict(graph6=encode(a),witness=selected,
                            qualifying_sets=len(masks),maximum_size=selected.bit_count() if masks else None))
        if not masks:status_text='COUNTEREXAMPLE_CANDIDATE';break
        before=len(cuts)
        for mask in masks:forbid(mask)
        assert len(cuts)>before
        print(n,args.radius,iteration,len(masks),len(cuts),round(time.monotonic()-start,2),flush=True)
    result=dict(order=n,seed_graph6=row[0],removed_edge_radius=args.radius,
                initial_cuts=initial,total_cuts=len(cuts),forbidden_masks=sorted(cuts),
                records=records,status=status_text,unknown_reason=solver.reason_unknown() if status_text=='unknown' else None,
                elapsed_seconds=time.monotonic()-start,original_conjecture_resolved=False)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('DONE',n,args.radius,status_text,len(records),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--order',type=int,required=True)
    p.add_argument('--radius',type=int,required=True);p.add_argument('--seconds',type=int,default=180)
    p.add_argument('--query-ms',type=int,default=20000);p.add_argument('--iterations',type=int,default=200)
    p.add_argument('--output',type=Path,required=True);run(p.parse_args())
