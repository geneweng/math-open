"""Exact certificate and independent subset checks for continuation 15.

The unrestricted conjecture remains unresolved. No optimization package is
needed here. Numerical LP and SAT statuses are not used as proof certificates.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

from verify_round12 import decode,connected_cubic
from verify_bridge_reduction import complete,good

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round15_data'


def cut_certificates():
    expected=(DATA/'near_tight_bases.g6').read_text().splitlines()
    rows=[json.loads(s) for s in (DATA/'cut_certificates.jsonl').read_text().splitlines()]
    assert [r['graph6'] for r in rows]==expected and len(rows)==2249
    rows += [json.loads(s) for s in (DATA/'cut_certificates_tight.jsonl').read_text().splitlines()]
    certified=0;methods=Counter();orders=Counter();indexed=0;limits=[]
    for row in rows:
        a,es=decode(row['graph6']);connected_cubic(a);n=len(a)
        terms=[(r['mask'],Fraction(r['coefficient'])) for r in row['terms']]
        assert sum(c for s,c in terms)==1 and all(c>=0 for s,c in terms)
        for mask,c in terms:
            assert 0<=mask<1<<n
            selected={v for v in range(n) if mask>>v&1}
            assert good(a,selected)
        p=[sum((c for s,c in terms if bool(s>>u&1)!=bool(s>>v&1)),Fraction(0)) for u,v in es]
        value=sum((min(x,1-x) for x in p),Fraction(0))
        assert value==Fraction(row['cut_total'])
        if row['status']=='certified':
            assert value>=Fraction(n,2)
            certified+=1;methods[row['method']]+=1;orders[n]+=1;indexed+=1<<len(es)
        else:
            assert row['status']=='no_certificate' and n==26 and value==Fraction(25,2)
            limits.append(dict(order=n,achieved_cut_total=str(value),required=n//2))
    assert certified==2250
    return dict(certified_bases=certified,by_order=dict(orders),methods=dict(methods),
                indexed_zero_or_one_patterns=indexed,limited_cases=limits,
                scope='Every subset of edge replacements; triangle-chain extension follows from the proved reduction')


def brute_states(a,es):
    incident=[sum(1<<i for i,e in enumerate(es) if v in e) for v in range(len(a))]
    out=set()
    for f in range(1<<len(es)):
        if any((f&inc).bit_count() not in (0,2) for inc in incident):continue
        r=sum(1<<v for v,inc in enumerate(incident) if f&inc);x=0;c=0
        for i,(u,v) in enumerate(es):
            su=bool(r>>u&1);sv=bool(r>>v&1)
            if su and sv and not (f>>i&1):x|=1<<i
            if su!=sv:c|=1<<i
        out.add((r,x,c,f))
    return out


def formula_checks():
    sys.path.insert(0,str(ROOT/'exploratory'))
    from triangle_subset_synthesis import states,exact_score,expand
    codes=[s for s in (ROOT/'round8_data/cubic_through18.g6').read_text().splitlines()
           if ord(s[0])-63<=8]
    cases=0;subsets=0;full_orders=[]
    for code in codes:
        a,es=decode(code);n=len(a);ss=states(a,es)
        assert set(ss)==brute_states(a,es)
        markings=range(1<<len(es)) if n==4 else [sum(1<<i for i in comb)
            for k in range(3) for comb in itertools.combinations(range(len(es)),k)]
        for marked in markings:
            predicted,index=exact_score(ss,marked)
            h,chosen=expand(a,es,marked,ss[index])
            assert good(h,chosen)
            adj=[sum(1<<u for u in ns) for ns in h]
            branch=sum(1<<v for v,ns in enumerate(h) if len(ns)==3)
            best=0
            for s in range(1<<len(h)):
                score=(s&branch).bit_count()
                if score<=best:continue
                todo=s;ok=True
                while todo:
                    bit=todo&-todo;todo-=bit;v=bit.bit_length()-1
                    if (adj[v]&s).bit_count()!=2:ok=False;break
                if ok:best=score
            assert best==predicted==sum(len(h[v])==3 for v in chosen)
            target=sum(map(len,h))//2-len(h)
            assert predicted>=target
            cubic,witness=complete(h,chosen);connected_cubic(cubic)
            assert good(cubic,witness) and 2*len(witness)>=len(cubic)
            assert len(cubic)==n+16*marked.bit_count()
            cases+=1;subsets+=1<<len(h);full_orders.append(len(cubic))
    assert cases==551
    return dict(base_graphs=len(codes),marked_patterns=cases,
                vertex_subsets_checked=subsets,full_cubic_completions_checked=cases,
                maximum_completion_order=max(full_orders))


def positive_descent_witnesses():
    seen=set();children=set();stats={}
    for path in sorted(DATA.glob('*_nodes.txt.gz')):
        rows=0;root_rows=0;child_rows=0
        with gzip.open(path,'rt') as handle:
            for line in handle:
                depth_s,code,score_s,w_s,exact_s=line.split()
                depth,score,w,exact=map(int,(depth_s,score_s,w_s,exact_s));rows+=1
                if depth:child_rows+=1;children.add(code)
                else:root_rows+=1
                key=(code,score,w)
                if key in seen:continue
                seen.add(key);a,_=decode(code);n=len(a)
                assert all(len(ns) in (2,3) for ns in a)
                assert 0<=w<1<<n
                selected={v for v in range(n) if w>>v&1}
                assert good(a,selected)
                assert sum(len(a[v])==3 for v in selected)==score
                target=sum(map(len,a))//2-n
                assert score>=target
                if not exact:assert depth==0 and score>n//2+2
        stats[path.name]=dict(records=rows,root_rows=root_rows,child_rows=child_rows)
    assert stats['descent_nodes.txt.gz']['root_rows']==45982
    assert stats['descent20_nodes.txt.gz']['root_rows']==510489
    assert stats['neutral_nodes.txt.gz']['root_rows']==556471
    assert stats['neutral_nodes.txt.gz']['child_rows']==11193
    return dict(files=stats,distinct_labelled_children=len(children),
                verified_positive_records=len(seen),
                scope='Checks lower-bound witnesses; does not independently assert every recorded optimum')


def synthesis_statuses():
    stats={}
    for path in sorted(DATA.glob('subset_synthesis*.jsonl')):
        rows=[json.loads(s) for s in path.read_text().splitlines()]
        assert not any(r.get('ORIGINAL_COUNTEREXAMPLE_CANDIDATE') for r in rows)
        stats[path.name]=dict(cases=len(rows),statuses=dict(Counter(r['status'] for r in rows)))
    return dict(runs=stats,scope='Solver reports only; no formal infeasibility proof files retained')


if __name__=='__main__':
    start=time.monotonic()
    result=dict(original_conjecture_resolved=False,cut_certificates=cut_certificates(),
                formula_checks=formula_checks(),positive_search=positive_descent_witnesses(),
                synthesis_statuses=synthesis_statuses())
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(DATA.iterdir()) if p.is_file()}
    (ROOT/'round15_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
