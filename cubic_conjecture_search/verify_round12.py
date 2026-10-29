"""Independent standard-library checks of direct half-bound witnesses.

No optimization package is imported. Finite positive certificates do not
resolve the original conjecture. Triangle base completeness relies on geng.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import time

from verify_pseudoforest_repair import odd_factors, statistics
from verify_bridge_reduction import graph, good_sets, edges, good

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'round12_data'


def decode(code):
    vals = [ord(c)-63 for c in code]
    assert vals and all(0 <= x < 64 for x in vals)
    if vals[0] < 63:
        n, start = vals[0], 1
    else:
        assert len(vals) >= 4 and vals[1] < 63
        n, start = (vals[1]<<12)+(vals[2]<<6)+vals[3], 4
        assert n >= 63
    assert n > 0 and len(vals) == start+(n*(n-1)//2+5)//6
    a, es, bit = [set() for _ in range(n)], [], 0
    for v in range(n):
        for u in range(v):
            if vals[start+bit//6] >> (5-bit%6) & 1:
                a[u].add(v); a[v].add(u); es.append((u,v))
            bit += 1
    if bit % 6:
        assert vals[-1] & ((1 << (6-bit%6))-1) == 0
    return a, es


def connected_cubic(a):
    assert all(len(ns) == 3 for ns in a)
    seen, todo = {0}, [0]
    while todo:
        v = todo.pop()
        for u in a[v]-seen:
            seen.add(u); todo.append(u)
    assert len(seen) == len(a)


def check_set(a, chosen, target, branches_only=False):
    s = set(chosen)
    assert len(s) == len(chosen) and s <= set(range(len(a)))
    assert all(len(a[v]&s) == 2 for v in s)
    score = sum(len(a[v]) == 3 for v in s) if branches_only else len(s)
    assert score >= target
    return score


def direct_search():
    retries = {r['graph6']:r['query'] for r in json.loads((DATA/'original_retries.json').read_text())}
    totals, seen = Counter(), set()
    for line in (DATA/'original_candidates.jsonl').open():
        row = json.loads(line); code = row['graph6']; assert code not in seen
        seen.add(code); a, _ = decode(code); connected_cubic(a)
        assert len(a) == row['order']
        queries = [row[k] for k in ('strict_query','half_query') if k in row]
        if code in retries:
            queries.append(retries[code]);totals['retry_certificates'] += 1
        positive = False
        for q in queries:
            if 'witness' in q:
                assert q['status'] in ('FEASIBLE','OPTIMAL')
                assert q['target'] >= len(a)//2
                check_set(a,q['witness'],q['target']);positive = True
                totals['witnesses'] += 1
        assert positive
        totals['graphs'] += 1
    assert set(retries) <= seen
    totals['unresolved_after_retry'] = 0
    return dict(totals)


def named_graphs():
    inputs = json.loads((DATA/'named_cubic_inputs.json').read_text())
    results = json.loads((DATA/'named_cubic_results.json').read_text())
    byname = {r['name']:r for r in inputs['records']}
    verified = []
    for row in results:
        inp = byname.pop(row['name']); a, _ = decode(row['graph6']);n=len(a)
        assert row['graph6'] == inp['graph6'] and n == inp['order'] == row['order']
        connected_cubic(a)
        b = [set() for _ in range(n)]
        def edge(u,v):
            assert u != v
            b[u].add(v);b[v].add(u)
        for v in range(n):edge(v,(v+1)%n)
        shifts = inp['shifts']*inp['repeats']
        assert len(shifts) == n
        for v,shift in enumerate(shifts):edge(v,(v+shift)%n)
        assert a == b
        q = row['query']; assert q['target'] == n//2+1
        score = check_set(a,q['witness'],q['target'])
        verified.append(dict(name=row['name'],order=n,lower_bound=score))
    assert not byname
    return verified


def triangle_pairs():
    bases = (DATA/'triangle_pair_bases.g6').read_text().splitlines()
    assert len(set(bases)) == len(bases)
    counts, total = Counter(), 0
    with gzip.open(DATA/'triangle_pair_witnesses.txt.gz','rt') as stream:
        for code in bases:
            original, es = decode(code); connected_cubic(original);n=len(original)
            assert n in (12,14,16)
            counts[n] += 1
            for e,f in itertools.combinations(range(len(es)),2):
                line = next(stream).split(); assert len(line) == 5
                g,ei,fi,score,mask = line
                assert g == code and int(ei) == e and int(fi) == f
                a = [ns.copy() for ns in original] + [set() for _ in range(6)]
                for index,off in ((e,n),(f,n+3)):
                    u,v = es[index];a[u].remove(v);a[v].remove(u)
                    for x,y in ((u,off),(off,off+1),(off+1,v),(off,off+2),(off+1,off+2)):
                        a[x].add(y);a[y].add(x)
                m = sum(map(len,a))//2
                assert m == len(es)+8 and len(a) == n+6
                assert sum(len(ns)==2 for ns in a) == 2
                mask = int(mask); assert 0 <= mask < 1 << len(a)
                chosen = [v for v in range(len(a)) if mask>>v&1]
                got = check_set(a,chosen,m-len(a),branches_only=True)
                assert got == int(score)
                total += 1
            if sum(counts.values())%1000 == 0:
                print(f'Triangle bases verified: {sum(counts.values())}; witnesses: {total}',flush=True)
        assert stream.read() == ''
    assert counts == {12:85,14:509,16:4060}
    assert total == 1240455
    return dict(base_counts=dict(counts),constructions=total,
                branch_orders=[18,20,22],cubic_completion_orders=[44,46,48],
                isomorphism_completeness_depends_on='geng')


def global_objective():
    # Auxiliary method obstruction; the original conjecture holds here.
    code = 'O???C@_cUAL?J?CgAo?[?'
    a,es = decode(code);n=len(a);connected_cubic(a)
    best, good, count = -1,-1,0
    for f in odd_factors(n,es):
        count += 1;s=statistics(n,es,f)
        if s['pseudoforest']:
            best=max(best,s['edges'])
            if not s['isolated']:good=max(good,s['edges'])
    assert count == 512 and (best,good) == (15,14)
    adjacency=[sum(1<<u for u in ns) for ns in a]
    optimum=0
    for mask in range(1<<n):
        if mask.bit_count() <= optimum:continue
        if all((mask&adjacency[v]).bit_count()==2 for v in range(n) if mask>>v&1):
            optimum=mask.bit_count()
    assert optimum >= n//2
    return dict(graph6=code,order=n,odd_factors_checked=count,maximum_edges=best,
                maximum_edges_without_isolated_edges=good,c_ind=optimum,
                counterexample_to_original_conjecture=False)


def consecutive_triangles():
    cases = lifts = 0
    configurations = Counter()
    for n in range(2,6):
        possible = list(itertools.combinations(range(n),2))
        for mask in range(1 << len(possible)):
            base = graph(n,[e for i,e in enumerate(possible) if mask>>i&1])
            if max(map(len,base)) > 3:continue
            sets = list(good_sets(base)); branch = {v for v in range(n) if len(base[v])==3}
            for u,v in edges(base):
                a,b,w,c,d,z = range(n,n+6)
                es = [e for e in edges(base) if e != (u,v)]
                es += [(u,a),(a,b),(a,w),(b,w),(b,c),(c,d),(c,z),(d,z),(d,v)]
                h = graph(n+6,es); hbranch = {x for x in range(n+6) if len(h[x])==3}
                assert len(es)-len(h) == len(edges(base))-n+2
                for s in sets:
                    state = (u in s,v in s)
                    chosen = s | ({a,b,c,d} if all(state) else
                                  {c,d,z} if state[0] else {a,b,w})
                    assert good(h,chosen)
                    gain = len(chosen & hbranch)-len(s & branch)
                    assert gain == (4 if all(state) else 2)
                    configurations[str(state)] += 1;lifts += 1
                cases += 1
    return dict(edge_replacements=cases,good_set_lifts=lifts,
                endpoint_states=dict(configurations))


def main():
    start=time.monotonic()
    result=dict(original_conjecture_resolved=False,
                direct_search=direct_search(),named_graphs=named_graphs(),
                triangle_pairs=triangle_pairs(),auxiliary_objective=global_objective(),
                consecutive_triangles=consecutive_triangles())
    result['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(DATA.iterdir()) if p.is_file()}
    result['elapsed_seconds']=time.monotonic()-start
    (ROOT/'round12_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('named_graphs','data_sha256')},indent=2))


if __name__ == '__main__':main()
