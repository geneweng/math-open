"""Check every rejected graph and cross-check both enumeration methods."""
import collections
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from verify_round12 import decode,connected_cubic


def main():
    run=json.loads((HERE/'search.json').read_text())
    exact=[json.loads(line) for line in (HERE/'cycle_space_checks.jsonl').read_text().splitlines()]
    assert len(exact)==len(run['records'])
    previous=set();hist=collections.Counter();states=0
    for row,check in zip(run['records'],exact):
        assert row['graph6']==check['graph6']
        a,_=decode(row['graph6']);connected_cubic(a)
        assert len(a)==26 and all((v<13)!=(u<13) for v in range(26) for u in a[v])
        assert a[0]=={13,14,15} and a[13]=={0,1,2}
        masks=row['large_good_sets'];assert len(masks)==len(set(masks))
        assert not previous.intersection(masks)
        for mask in masks:
            assert mask>>26==0 and mask.bit_count()>=14
            assert (mask&((1<<13)-1)).bit_count()==(mask>>13).bit_count()
            assert all(sum(mask>>u&1 for u in a[v])==2 for v in range(26) if mask>>v&1)
        # Independent C++ cycle-space enumeration supplies the size histogram.
        assert len(masks)==sum(check['histogram'][14:])
        assert collections.Counter(mask.bit_count() for mask in masks)=={
            size:count for size,count in enumerate(check['histogram']) if size>=14 and count}
        assert row['witness'] in masks and row['witness'].bit_count()==check['maximum']
        assert check['maximum']==18 and check['factors_checked']==16384
        previous.update(masks);hist[check['maximum']]+=1;states+=check['factors_checked']
    assert len(previous)==run['total_forbidden_sets']
    for cut in run['connectivity_cuts']:
        assert 0 in cut and 0<len(set(cut))==len(cut)<26
        assert set(cut)<=set(range(26))
    result=dict(status=run['status'],elapsed_seconds=run['elapsed_seconds'],
                graphs_checked=len(exact),exact_optimum_histogram=dict(hist),
                independently_enumerated_cycle_vectors=states,
                verified_forbidden_good_sets=len(previous),
                original_counterexample_found=False,
                completeness='No completeness or infeasibility claim; run ended at its wall-time guard.',
                assessment='All candidates attained the class upper bound 18; no observed movement toward the target <=12.')
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
