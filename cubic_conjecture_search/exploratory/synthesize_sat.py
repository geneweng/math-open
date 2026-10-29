import json
import random
import subprocess
import sys
import time
from pathlib import Path

import z3


def encode(n,edges):
    bits=[int((u,v) in edges) for v in range(1,n) for u in range(v)]
    bits.extend([0]*((-len(bits))%6))
    return chr(n+63)+''.join(chr(63+sum(bits[i+j]<<(5-j) for j in range(6))) for i in range(0,len(bits),6))


if __name__=='__main__':
    n=int(sys.argv[1]);rounds=int(sys.argv[2]);rng=random.Random(20261026+n)
    solver=z3.SolverFor("QF_FD");solver.set(timeout=30000,random_seed=20261026)
    variables={(u,v):z3.Bool(f'e{u}_{v}') for v in range(1,n) for u in range(v)}
    def edge(u,v):return variables[min(u,v),max(u,v)]
    for v in range(n):solver.add(z3.PbEq([(edge(u,v),1) for u in range(n) if u!=v],3))
    # Every connected graph has a labeling satisfying these two conditions.
    for v in range(1,n):solver.add(z3.Or([edge(u,v) for u in range(v)]))
    for v in range(1,n):solver.add(edge(0,v)==(v in (1,2,3)))
    cuts=set();records=[];best=n;start=time.monotonic()
    for iteration in range(rounds):
        status=solver.check()
        if status!=z3.sat:
            print('solver stopped',status,solver.reason_unknown() if status==z3.unknown else '',flush=True)
            records.append({'iteration':iteration,'status':str(status)});break
        model=solver.model();es={uv for uv,x in variables.items() if z3.is_true(model.eval(x))}
        code=encode(n,es);path=Path(f'tmp/cubic_round4/candidate{n}.g6');path.write_text(code+'\n')
        data=subprocess.check_output(['tmp/cubic_round3/enumerate_large',str(path)],text=True).split()
        good=list(map(int,data[1:]));value=max(s.bit_count() for s in good)
        large=[s for s in good if 2*s.bit_count()>=n]
        if value<best:
            best=value;Path(f'tmp/cubic_round4/synthesis_best{n}.json').write_text(json.dumps({'graph6':code,'cind':value,'iteration':iteration,'edges':sorted(es)},indent=2))
        if not large:
            print('COUNTEREXAMPLE',n,code,value,flush=True)
            Path(f'tmp/cubic_round4/counterexample{n}.json').write_text(json.dumps({'graph6':code,'cind':value,'edges':sorted(es)},indent=2));break
        rng.shuffle(large);new=0
        for s in large[:20]:
            if s in cuts:continue
            vertices=[v for v in range(n) if s>>v&1]
            solver.add(z3.Not(z3.And([z3.PbEq([(edge(u,v),1) for u in vertices if u!=v],2) for v in vertices])))
            cuts.add(s);new+=1
        assert new>0
        record={'iteration':iteration,'cind':value,'best':best,'large_good_sets':len(large),'cuts':len(cuts),'seconds':round(time.monotonic()-start,2)}
        records.append(record)
        print(record,flush=True)
        Path(f'tmp/cubic_round4/synthesis{n}.json').write_text(json.dumps(records,indent=2))
    Path(f'tmp/cubic_round4/synthesis{n}.json').write_text(json.dumps(records,indent=2))
