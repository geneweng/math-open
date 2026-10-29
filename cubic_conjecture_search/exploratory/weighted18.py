import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

from ortools.linear_solver import pywraplp
sys.path.insert(0,'cubic_conjecture_search')
from verify_certificates import graph6,has_bridge

p=subprocess.Popen(['tmp/cubic_full/cert_enumerator','tmp/cubic_continue/cubic18.g6'],stdout=subprocess.PIPE,text=True)
checked=0;graphs=0;start=time.monotonic();max_ratio=Fraction(0)
for line in p.stdout:
    f=line.split();g=graph6(f[0]);n=len(g);graphs+=1
    assert n==18
    ss=list(map(int,f[1:]));cind=max(s.bit_count() for s in ss)
    if 2*cind<n:
        Path('tmp/cubic_continue/full_counterexample18.json').write_text(json.dumps({'graph6':f[0],'cind':cind}))
        print('FULL COUNTEREXAMPLE',f[0],cind,flush=True);p.terminate();break
    if has_bridge(g):continue
    lp=pywraplp.Solver.CreateSolver('GLOP');w=[lp.NumVar(0,1,str(v)) for v in range(n)]
    for s in ss:
        c=lp.Constraint(0,1)
        for v in range(n):
            if s>>v&1:c.SetCoefficient(w[v],1)
    lp.Maximize(sum(w));assert lp.Solve()==lp.OPTIMAL
    checked+=1
    if lp.Objective().Value()>2+1e-8:
        weights=[Fraction(v.solution_value()).limit_denominator(100000) for v in w]
        maximum=max(sum(weights[v] for v in range(n) if s>>v&1) for s in ss)
        ratio=sum(weights)/maximum
        if ratio>2:
            record={'graph6':f[0],'weights':list(map(str,weights)),'maximum':str(maximum),
                    'total':str(sum(weights)),'ratio':str(ratio),'cind':cind,'checked':checked}
            Path('tmp/cubic_continue/weighted_counterexample18.json').write_text(json.dumps(record,indent=2))
            print('WEIGHTED COUNTEREXAMPLE',record,flush=True);p.terminate();break
    if checked%2000==0:
        print('checked',checked,'graphs',graphs,'seconds',round(time.monotonic()-start,1),flush=True)
        Path('tmp/cubic_continue/weighted18_progress.json').write_text(json.dumps({'checked':checked,'graphs':graphs,'complete':False}))
else:
    if graphs!=41301:
        raise RuntimeError('the input did not contain the expected 41,301 graphs; run geng to completion first')
    Path('tmp/cubic_continue/weighted18_progress.json').write_text(json.dumps({'checked':checked,'graphs':graphs,'complete':True,'counterexample_found':False}))
p.wait()
print('finished',checked,graphs,flush=True)
