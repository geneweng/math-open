"""Rational certificates for ALL subsets of edge-triangle replacements.

A distribution on good vertex sets, with edge-cut probabilities p_e,
certifies every replacement subset if sum_e min(p_e,1-p_e) >= n/2.
Floating-point LP proposes distributions; only exact Fraction checks accept.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import time

from triangle_subset_synthesis import decode,states


def checked(a,es,terms):
    assert sum(c for _,c in terms)==1
    assert all(c>=0 for _,c in terms)
    for r,c in terms:
        assert all(sum(r>>u&1 for u in a[v])==2 for v in range(len(a)) if r>>v&1)
    probs=[sum((c for r,c in terms if bool(r>>u&1)!=bool(r>>v&1)),Fraction(0)) for u,v in es]
    total=sum((min(p,1-p) for p in probs),Fraction(0))
    return total,total>=Fraction(len(a),2)


def certificate(code):
    a,es=decode(code);ss=states(a,es);good=[r for r,x,c,f in ss if not x]
    M=max(map(int.bit_count,good));maxima=[r for r in good if r.bit_count()==M]
    terms=[(r,Fraction(1,len(maxima))) for r in maxima]
    total,ok=checked(a,es,terms)
    if ok:method='uniform_maxima'
    else:
        from ortools.linear_solver import pywraplp
        lp=pywraplp.Solver.CreateSolver('GLOP')
        lam=[lp.NumVar(0,1,f'l{i}') for i in range(len(good))]
        y=[lp.NumVar(0,1,f'y{i}') for i in range(len(es))]
        lp.Add(sum(lam)==1)
        for e,(u,v) in enumerate(es):
            lp.Add(y[e]>=2*sum(l for r,l in zip(good,lam) if bool(r>>u&1)!=bool(r>>v&1))-1)
        lp.Minimize(sum(y)-sum(r.bit_count()*l for r,l in zip(good,lam)))
        status=lp.Solve()
        if status!=lp.OPTIMAL:return dict(graph6=code,status='LP_unknown')
        terms=[(r,Fraction(l.solution_value()).limit_denominator(1000000)) for r,l in zip(good,lam) if l.solution_value()>1e-9]
        if sum(c for r,c in terms)!=1:return dict(graph6=code,status='rationalization_failed')
        total,ok=checked(a,es,terms);method='rational_LP'
    return dict(graph6=code,order=len(a),status='certified' if ok else 'no_certificate',
                method=method,cut_total=str(total),maximum=M,
                terms=[dict(mask=r,coefficient=str(c)) for r,c in terms])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs',nargs='+',type=Path)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    count=0;start=time.monotonic();stats={}
    with args.output.open('w') as out:
        for path in args.inputs:
            for code in path.read_text().splitlines():
                r=certificate(code);out.write(json.dumps(r)+'\n');out.flush();count+=1
                stats[r['status']]=stats.get(r['status'],0)+1
                if count%100==0 or r['status']!='certified':
                    print(count,stats,'seconds',round(time.monotonic()-start,2),flush=True)
    print('DONE',count,stats,'seconds',round(time.monotonic()-start,2),flush=True)
