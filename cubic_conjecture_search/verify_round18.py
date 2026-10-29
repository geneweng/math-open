"""Verify retained direct cubic-search witnesses and exact best profiles.

Independent degree-propagation enumeration checks best profiles; the
search used a binary cycle space. All other retained records are checked
as lower-bound witnesses, not as independent optimum certificates.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import time

from verify_round12 import decode, connected_cubic
from verify_round13 import vertex_profiles
from verify_bridge_reduction import good

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round18_data'


def rows(stem):
    compressed=DATA/(stem+'.txt.gz')
    path=compressed if compressed.exists() else DATA/(stem+'.txt')
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as stream:
        for line in stream:
            code, size, count, witness, exact=line.split()
            yield code,int(size),int(count),int(witness),int(exact)


if __name__=='__main__':
    start=time.monotonic();counts=Counter();orders=Counter();unique=set()
    candidate_rows=(row for stem in ('descent_candidates','large_candidates') for row in rows(stem))
    for code,size,count,witness,exact in candidate_rows:
        a,es=decode(code);connected_cubic(a);n=len(a)
        assert n in (24,26,28,30,32,36,38,42) and exact in (0,1)
        assert 0<=witness<1<<n
        chosen={v for v in range(n) if witness>>v&1}
        assert good(a,chosen) and len(chosen)==size
        if 2*size<n:
            raise RuntimeError('Retained candidate requires counterexample audit: '+code)
        counts['records']+=1;counts['reported_exact']+=exact;orders[n]+=1;unique.add(code)
    assert counts['records']==30185
    bests=[];cache={}
    best_rows=(row for stem in ('descent_best','large_best') for row in rows(stem))
    for code,size,count,witness,exact in best_rows:
        assert exact==1
        a,es=decode(code);connected_cubic(a)
        if code not in cache:cache[code]=vertex_profiles(a,0)
        p=cache[code];maximum=max(p['A'],p['B'])
        multiplicity=(p['A_count'] if p['A']==maximum else 0)+(p['B_count'] if p['B']==maximum else 0)
        assert (size,count)==(maximum,multiplicity)
        chosen={v for v in range(len(a)) if witness>>v&1}
        assert good(a,chosen) and len(chosen)==maximum and maximum>=len(a)//2
        bests.append(dict(graph6=code,order=len(a),maximum=maximum,
                         maximum_set_count=multiplicity,witness=sorted(chosen)))
    assert len(bests)==45
    per_order={}
    for row in bests:
        n=row['order'];value=(row['maximum'],row['maximum_set_count'])
        if n not in per_order or value<tuple(per_order[n]):per_order[n]=value
    codes=(DATA/'simultaneous_bases.g6').read_text().splitlines()
    certificates=[json.loads(s) for s in (DATA/'cut_certificates.jsonl').read_text().splitlines()]
    assert [r['graph6'] for r in certificates]==codes and len(codes)==4
    checked_certificates=[]
    for row in certificates:
        a,es=decode(row['graph6']);connected_cubic(a)
        terms=[(r['mask'],Fraction(r['coefficient'])) for r in row['terms']]
        assert all(c>0 and 0<=s<1<<len(a) for s,c in terms)
        assert sum(c for s,c in terms)==1
        for s,c in terms:assert good(a,{v for v in range(len(a)) if s>>v&1})
        probabilities=[sum((c for s,c in terms if bool(s>>u&1)!=bool(s>>v&1)),Fraction())
                       for u,v in es]
        total=sum(min(p,1-p) for p in probabilities)
        assert row['status']=='certified' and total==Fraction(row['cut_total'])>=Fraction(len(a),2)
        checked_certificates.append(dict(order=len(a),terms=len(terms),cut_total=str(total),
                                          guaranteed_integer_surplus=math.ceil(total-Fraction(len(a),2)),
                                          scope='Certifies all marked subsets and arbitrary triangle chains'))
    solver_rows=[json.loads(s) for s in (DATA/'simultaneous_results.jsonl').read_text().splitlines()]
    assert [r['graph6'] for r in solver_rows]==codes
    assert not any(r.get('ORIGINAL_COUNTEREXAMPLE_CANDIDATE') for r in solver_rows)
    result=dict(original_conjecture_resolved=False,positive_witnesses=dict(counts),
                distinct_labelled_graphs=len(unique),records_by_order=dict(orders),
                exact_best_records=bests,distinct_exact_best_graphs=len(cache),
                best_size_and_multiplicity_by_order=per_order,
                exact_cut_certificates=checked_certificates,
                exploratory_solver_statuses=dict(Counter(r['status'] for r in solver_rows)),
                solver_proof_files_retained=False,
                scope='Bounded heuristic search; no exhaustive coverage claim. Non-best records are independently checked only as positive witnesses.',
                elapsed_seconds=round(time.monotonic()-start,3))
    result['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(DATA.iterdir()) if p.is_file()}
    (ROOT/'round18_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='exact_best_records'},indent=2))
