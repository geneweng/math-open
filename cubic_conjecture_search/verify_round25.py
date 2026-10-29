"""Exhaust cap states and check edge-budget repair-barrier certificates.

The original conjecture remains unresolved. The universal lower bound
with denominator four has a proof independent of this finite check.
"""
import json
from pathlib import Path

from verify_bridge_reduction import cap, edges, good, good_sets
from verify_round11 import family, bitmask
from verify_pseudoforest_repair import statistics

ROOT = Path(__file__).resolve().parent


def main():
    p = cap()
    es = sorted(edges(p))
    assert len(es) == 19
    inc = [sum(1 << i for i, e in enumerate(es) if v in e)
           for v in range(13)]
    avoiding = max(len(s) for s in good_sets(p) if 12 not in s)
    assert avoiding == 6
    table = {}
    count = 0
    for mask in range(1 << 19):
        deg = [(mask & b).bit_count() for b in inc]
        if deg[12] % 2 or any(d % 2 != 1 for d in deg[:12]):
            continue
        count += 1
        # In a simple graph, an edge between two degree-one vertices is
        # exactly an isolated K2 component; no component routine is used.
        j = sum(bool(mask >> i & 1) and deg[u] == deg[v] == 1
                for i, (u, v) in enumerate(es))
        w = j + int(deg[12] == 0)
        m = mask.bit_count()
        row = table.setdefault(w, dict(count=0, min_edges=19, max_edges=0))
        row['count'] += 1
        row['min_edges'] = min(row['min_edges'], m)
        row['max_edges'] = max(row['max_edges'], m)
        assert 2*m+w >= 19
        assert m >= 13 - 4*w
        if w == 0:
            leaves = {v for v in range(12) if deg[v] == 1}
            assert good(p, leaves) and m == 19-len(leaves) and m >= 13
    assert count == 128
    assert {w: r['min_edges'] for w, r in table.items()} == {
        0: 13, 1: 9, 2: 9, 3: 8, 4: 8, 5: 7, 7: 6}

    records = []
    local_cycle = [0, 2, 12, 4, 6, 5, 3]
    for k in range(3, 41):
        a, ge, initial, cores, offsets = family(k)
        n = len(a)
        assert n == 28*k-26 and all(len(x) == 3 for x in a)
        path = [initial]
        for off in offsets[:k-1]:
            vs = [off+v for v in local_cycle]
            ce = [tuple(sorted((u, v))) for u, v in zip(vs, vs[1:]+vs[:1])]
            assert all(v in a[u] for u, v in ce)
            path.append(path[-1] ^ bitmask(ge, ce))
        path.append(path[-1] ^ bitmask(ge, cores[0]))
        ss = [statistics(n, ge, m) for m in path]
        assert [s['isolated'] for s in ss] == list(range(1, k+1))+[0]
        assert [m.bit_count() for m in path] == list(range(n-1, n-k-1, -1))+[n]
        assert all(m.bit_count() <= n for m in path)
        assert all(s['pseudoforest'] for s in ss)
        final = set(ss[-1]['leaves'])
        assert good(a, final) and len(final) == n//2
        records.append(dict(k=k, order=n, initial_edges=n-1,
                            peak_j=k, final_j=0, final_good_size=len(final),
                            analytic_excess_lower_bound=(k+2)//4))
    result = dict(original_conjecture='unresolved', cap_edge_subsets=1 << 19,
                  parity_states=count, root_avoiding_maximum=avoiding,
                  cap_table=table, explicit_repair_checks=records,
                  scope='All cap edge subsets; explicit family repairs for 3 <= k <= 40. '
                        'The general barrier is proved in the paper, not inferred from these tests.')
    (ROOT/'round25_verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(parity_states=count, cap_table=table,
                          checked_repairs=len(records), original_conjecture='unresolved')))


if __name__ == '__main__':
    main()
