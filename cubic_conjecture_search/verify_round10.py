#!/usr/bin/env python3
"""Independent checks of the edge-replacement proofs and repair witnesses."""
from collections import Counter
import json
from pathlib import Path

from verify_bridge_reduction import edges, franklin
from verify_edge_inflation import fragment, table
from verify_pseudoforest_repair import decode, cycles_of, odd_factors, statistics, analyze_case
from verify_round9 import subset_histogram

ROOT = Path(__file__).resolve().parent
PORTS = (2, 4)
T = {(0, 2), (1, 2), (1, 3), (1, 11), (4, 6), (4, 7),
     (5, 6), (6, 8), (8, 10), (8, 11), (9, 11)}
P = [2, 0, 3, 5, 7, 4]
PATH_EDGES = {tuple(sorted(e)) for e in zip(P, P[1:])}
U = T ^ PATH_EDGES


def adjacency(n, es):
    result = [set() for _ in range(n)]
    for a, b in es:
        assert a != b and b not in result[a]
        result[a].add(b); result[b].add(a)
    return result


def selected_edges(es, mask):
    return {e for i, e in enumerate(es) if mask >> i & 1}


def make_mask(es, chosen):
    assert chosen <= set(es)
    return sum(1 << i for i, e in enumerate(es) if e in chosen)


def inflation(n, es, edge):
    a, b = edge
    new = (set(es) - {edge}) | {(n + u, n + v) for u, v in edges(fragment())}
    new |= {(a, n + 2), (b, n + 4)}
    ordered = sorted(new, key=lambda e: (e[1], e[0]))
    adj = adjacency(n + 12, ordered)
    assert all(len(x) == 3 for x in adj)
    return ordered, adj


def lift(n, factor, edge):
    a, b = edge
    if edge in factor:
        return ((factor - {edge}) | {(n + u, n + v) for u, v in T}
                | {(a, n + 2), (b, n + 4)})
    return factor | {(n + u, n + v) for u, v in U}


def verify_fragment():
    r = set(edges(fragment()))
    assert T <= r and PATH_EDGES <= r and U <= r
    ta = adjacency(12, T)
    assert len(T) == 11
    assert [len(ta[v]) for v in PORTS] == [2, 2]
    assert all(len(ta[v]) in (1, 3) for v in range(12) if v not in PORTS)
    seen, todo = {0}, [0]
    for v in todo:
        for u in ta[v] - seen:
            seen.add(u); todo.append(u)
    assert len(seen) == 12
    ordered = sorted(r, key=lambda e: (e[1], e[0]))
    us = statistics(12, ordered, make_mask(ordered, U))
    assert us['components'] == [(12, 12)] and us['isolated'] == 0
    assert us['leaves'] == [0, 2, 4, 7, 9, 10]
    boundary, _ = table()
    return dict(tree_edges=sorted(T), switch_path=P, unicyclic_edges=sorted(U),
                unicyclic_statistics=us, boundary_table={str(k): v for k, v in boundary.items()})


def verify_small_lifts():
    codes = (ROOT / 'round8_data/cubic_through18.g6').read_text().splitlines()
    totals = Counter()
    examples = []
    for code in (c for c in codes if ord(c[0]) - 63 <= 6):
        n, es, adj = decode(code)
        cycles = [selected_edges(es, c) for c in cycles_of(n, es, adj)]
        factors = {f: statistics(n, es, f) for f in odd_factors(n, es)}
        original_hist, original_witness = subset_histogram(adj)
        original_max = original_witness.bit_count()
        for edge in es:
            enlarged_edges, enlarged_adj = inflation(n, es, edge)
            deleted_adj = [set(x) for x in adj]
            a, b = edge
            deleted_adj[a].remove(b); deleted_adj[b].remove(a)
            _, deleted_witness = subset_histogram(deleted_adj)
            enlarged_hist, enlarged_witness = subset_histogram(enlarged_adj)
            assert enlarged_witness.bit_count() == 6 + max(original_max, deleted_witness.bit_count())
            totals['edge_replacements'] += 1
            totals['inflated_vertex_subsets_checked'] += 1 << (n + 12)
            for f, before in factors.items():
                if not before['pseudoforest']:
                    continue
                fs = selected_edges(es, f)
                lifted = lift(n, fs, edge)
                lm = make_mask(enlarged_edges, lifted)
                after = statistics(n + 12, enlarged_edges, lm)
                isolated_edge = edge in fs and all(v in before['leaves'] for v in edge)
                assert after['pseudoforest']
                assert after['isolated'] == before['isolated'] - int(isolated_edge)
                assert len(after['leaves']) == len(before['leaves']) + 6
                totals['pseudoforest_lifts'] += 1
                for c in cycles:
                    cc = c if edge not in c else ((c - {edge}) | {(n + u, n + v) for u, v in PATH_EDGES}
                                                  | {(a, n + 2), (b, n + 4)})
                    assert lifted ^ cc == lift(n, fs ^ c, edge)
                    ca = adjacency(n + 12, cc)
                    assert all(len(x) in (0, 2) for x in ca)
                    active = {v for v, nb in enumerate(ca) if nb}
                    reached = {next(iter(active))}; stack = list(reached)
                    for v in stack:
                        for u in ca[v] - reached:
                            reached.add(u); stack.append(u)
                    assert reached == active
                    totals['cycle_exchange_lifts'] += 1
            examples.append(dict(graph6=code, edge=edge, original=original_max,
                                 deleted=deleted_witness.bit_count(), inflated=enlarged_witness.bit_count()))
    return dict(totals), examples


def verify_search_witnesses(stem):
    records = [json.loads(s) for s in (ROOT / f'round10_data/{stem}_distances.jsonl').read_text().splitlines()]
    totals = Counter()
    for row in records:
        assert row['status'] == 'repaired'
        n, es, adj = decode(row['graph6'])
        path = row['path']
        assert len(path) == row['minimum_moves'] + 1 and path[0] == row['factor']
        last_j = row['initial_j']
        for i, f in enumerate(path):
            s = statistics(n, es, f)
            assert s['pseudoforest'] and s['isolated'] <= last_j
            last_j = s['isolated']
            if i:
                cycle = selected_edges(es, path[i - 1] ^ f)
                ca = adjacency(n, cycle)
                active = {v for v in range(n) if ca[v]}
                assert active and all(len(ca[v]) == 2 for v in active)
                reached = {next(iter(active))}; stack = list(reached)
                for v in stack:
                    for u in ca[v] - reached:
                        reached.add(u); stack.append(u)
                assert reached == active
        assert last_j < row['initial_j']
        if last_j == 0:
            chosen = set(s['leaves'])
            assert len(chosen) >= n // 2
            assert all(len(adj[v] & chosen) == 2 for v in chosen)
        totals[f"{row['minimum_moves']}_move_witnesses"] += 1
        totals['graphs'] += 1
    return dict(totals)


def verify_census_representatives():
    data = ROOT / 'round10_data'
    rows = [json.loads(s) for s in (data / 'inflated_neutral_distances.jsonl').read_text().splitlines()]
    inputs = [tuple(line.split()) for line in (data / 'inflated_neutral_inputs.txt').read_text().splitlines()]
    assert [(r['graph6'], str(r['factor'])) for r in rows] == inputs
    assert len(rows) == 1838
    assert all(r['minimum_moves'] == 2 and r['root_cycles_exhausted'] for r in rows)
    representatives = {}
    for row in rows:
        representatives.setdefault(row['graph6'], row)
    assert len(representatives) == 54
    checked = []
    for i, row in enumerate(representatives.values(), 1):
        result = analyze_case(row['graph6'], row['factor'], 'k2')
        assert result['minimum_repair_moves'] == 2 and result['direct_improvements'] == 0
        assert result['simple_cycles'] == row['cycles_examined_at_root']
        checked.append(result)
        if i % 10 == 0:
            print(f'Independently exhausted cycles in {i}/54 census representatives', flush=True)
    assert sum(r['simple_cycles'] for r in checked) == 968802
    return checked


def main():
    totals, examples = verify_small_lifts()
    result = dict(general_conjecture_resolved=False,
                  fragment=verify_fragment(), small_checks=totals, exact_examples=examples,
                  expansion_witnesses=verify_search_witnesses('expansion'),
                  inflation_witnesses=verify_search_witnesses('inflation'),
                  census_neutral_witnesses=verify_search_witnesses('inflated_neutral'),
                  census_representatives=verify_census_representatives(),
                  scope='All retained search paths verified. Shortestness independently checked for one neutral factor in each of 54 inflated graphs, not every factor. Exact replacement identity checked by all vertex subsets on 24 inflated graphs.')
    (ROOT / 'round10_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('exact_examples', 'fragment', 'census_representatives')}, indent=2))


if __name__ == '__main__':
    main()
