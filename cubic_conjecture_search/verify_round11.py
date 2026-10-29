"""Check an unbounded barrier to odd-pseudoforest repair, independently.

Standard library only. The original induced-cycles conjecture is NOT
disproved: every graph in this family attains its conjectured half bound.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

from verify_bridge_reduction import CAP_IN, cap, edges, good, good_sets, graph
from verify_exchange_obstructions import cycle_edges
from verify_pseudoforest_repair import statistics

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "round11_data"
ROOT_OUT = {0, 3, 5, 6, 8, 10}


def local_statistics(n, es, mask, root):
    a = graph(n, [e for i, e in enumerate(es) if mask >> i & 1])
    seen, components = set(), []
    for v in range(n):
        if v in seen:
            continue
        todo, part = [v], []
        seen.add(v)
        while todo:
            x = todo.pop()
            part.append(x)
            for y in a[x] - seen:
                seen.add(y)
                todo.append(y)
        components.append((part, sum(len(a[x]) for x in part) // 2))
    rv, re = next((vs, m) for vs, m in components if root in vs)
    j = sum(len(vs) == 2 for vs, m in components)
    return dict(root_degree=len(a[root]), root_cycle_rank=re-len(rv)+1,
                internal_j=j, cost=j + (len(a[root]) == 0),
                pseudoforest=all(m <= len(vs) for vs, m in components),
                component_orders=sorted(len(vs) for vs, m in components))


def bitmask(es, chosen):
    chosen = set(chosen)
    return sum(1 << i for i, e in enumerate(es) if e in chosen)


def graph6(a):
    n = len(a)
    assert n < 258048
    prefix = chr(n + 63) if n <= 62 else "~" + "".join(
        chr(63 + ((n >> s) & 63)) for s in (12, 6, 0))
    bits = [int(u in a[v]) for v in range(n) for u in range(v)]
    bits += [0] * (-len(bits) % 6)
    return prefix + "".join(chr(63 + sum(bits[i+j] << (5-j) for j in range(6)))
                            for i in range(0, len(bits), 6))


def family(k):
    assert k >= 3
    p = cap()
    es, cores, offsets = [(0, k)], [], []
    for side in (0, k):
        cyc = {tuple(sorted((side+i, side+(i+1) % k))) for i in range(k)}
        cores.append(cyc)
        es.extend(cyc)
    n = 2*k
    for side in (0, k):
        for v in range(side+1, side+k):
            offsets.append(n)
            es.extend((n+u, n+w) for u, w in edges(p))
            es.append((v, n+12))
            n += 13
    a = graph(n, es)
    es = sorted(edges(a))
    selected = {off+v for off in offsets for v in ROOT_OUT}
    removed = set.union(*cores) | {e for e in es if set(e) <= selected}
    initial = bitmask(es, set(es)-removed)
    return a, es, initial, cores, offsets


def cover_case(k):
    a, es, initial, _, _ = family(k)
    h = graph(2*len(a), [(2*u+s, 2*v+1-s) for u, v in es for s in (0, 1)])
    he = sorted(edges(h))
    hf = bitmask(he, [tuple(sorted((2*u+s, 2*v+1-s)))
                     for i, (u, v) in enumerate(es) if initial >> i & 1 for s in (0, 1)])
    return h, he, hf


def check_cover_repairs():
    # Two explicit cycles on the order-116 double cover, found by the
    # exploratory CP-SAT search. Transport their local support to larger k.
    first = [6, 9, 88, 73, 76, 75, 70, 65, 68, 89, 8, 7, 10, 115,
             98, 105, 108, 113, 106, 103, 100, 97, 90, 95, 114, 11]
    second = [90, 95, 114, 99, 102, 107, 110, 91, 94, 115, 98, 105,
              100, 103, 106, 113, 108, 111]
    records = []
    for k in range(3, 13):
        h, es, initial = cover_case(k)
        n = len(h)

        def transport(v):
            b, sheet = divmod(v, 2)
            if b in (3, 4, 5):
                b = {3:k, 4:k+1, 5:2*k-1}[b]
            elif 32 <= b <= 44:
                b = 2*k + 13*(k-1) + b-32
            else:
                assert 45 <= b <= 57
                b = 2*k + 13*(2*k-3) + b-45
            return 2*b + sheet

        path = [initial]
        changed_cycles = []
        for template in (first, second):
            vs = [transport(v) for v in template]
            assert len(set(vs)) == len(vs)
            ce = [tuple(sorted((u, v))) for u, v in zip(vs, vs[1:]+vs[:1])]
            assert all(v in h[u] for u, v in ce)
            changed_cycles.append(vs)
            path.append(path[-1] ^ bitmask(es, ce))
        stats = [statistics(n, es, f) for f in path]
        assert [s['isolated'] for s in stats] == [2, 1, 0]
        assert all(s['pseudoforest'] for s in stats)
        chosen = set(stats[-1]['leaves'])
        assert good(h, chosen) and len(chosen) == n//2+4
        assert all((u ^ v) & 1 for u, v in es)  # bipartition by sheet
        # Independently check connectedness after deletion of every edge.
        for banned in es:
            seen, todo = {0}, [0]
            while todo:
                u = todo.pop()
                for v in h[u] - seen:
                    if tuple(sorted((u, v))) != banned:
                        seen.add(v); todo.append(v)
            assert len(seen) == n
        records.append(dict(k=k, order=n, graph6=graph6(h), edges=es,
                            factor_encoding='Bit i refers to edges[i], in lexicographic (u,v) order.',
                            initial_factor=initial,
                            cycle_vertices=changed_cycles, path=path,
                            j=[2, 1, 0], final_good_set=sorted(chosen),
                            good_set_size=len(chosen), connected=True, bridgeless=True))
    (OUT/'double_cover_repairs.json').write_text(json.dumps(records, indent=2)+'\n')
    return [r['order'] for r in records]


def main():
    OUT.mkdir(exist_ok=True)
    p = cap()
    es = sorted(edges(p))
    inc = [sum(1 << i for i, e in enumerate(es) if v in e) for v in range(13)]
    table = {}
    # Exhaust every edge subset, not a cycle basis or solver encoding.
    for mask in range(1 << len(es)):
        if (mask & inc[12]).bit_count() % 2:
            continue
        if any((mask & inc[v]).bit_count() % 2 != 1 for v in range(12)):
            continue
        table[mask] = local_statistics(13, es, mask, 12)
    assert len(table) == 128
    sets = list(good_sets(p))
    assert max(len(s) for s in sets if 12 in s) == 7
    assert max(len(s) for s in sets if 12 not in s) == 6
    for s in table.values():
        if s['pseudoforest'] and s['root_cycle_rank'] == 0:
            assert s['cost'] >= 1
    zero = {f for f, s in table.items() if s['pseudoforest'] and s['cost'] == 0}
    assert len(zero) == 12
    assert all(table[f]['root_cycle_rank'] == 1 for f in zero)
    cycles = [bitmask(es, c) for c in cycle_edges(p)]
    assert len(cycles) == 107
    # All twelve states are connected by single-cycle exchanges.
    todo = deque([min(zero)])
    seen = set(todo)
    while todo:
        f = todo.popleft()
        for c in cycles:
            if f ^ c in zero and f ^ c not in seen:
                seen.add(f ^ c)
                todo.append(f ^ c)
    assert seen == zero
    for f in zero:
        for c in cycles:
            assert f ^ c in table
            s = table[f ^ c]
            if s['pseudoforest'] and s['cost'] <= 0:
                assert f ^ c in zero
    x = bitmask(es, [e for e in es if not set(e) <= ROOT_OUT])
    y = bitmask(es, [e for e in es if not set(e) <= CAP_IN])
    assert x in zero and table[y]['root_degree'] == 0
    assert table[y]['cost'] == 1 and table[y]['pseudoforest']
    assert x ^ y in cycles and (x ^ y).bit_count() == 7
    delta_edges = [e for i, e in enumerate(es) if (x ^ y) >> i & 1]
    (OUT/'cap_profiles.json').write_text(json.dumps(
        [dict(mask=f, **s) for f, s in sorted(table.items())], indent=2)+'\n')

    families = []
    for k in range(3, 13):
        a, ge, initial, cores, offsets = family(k)
        n = len(a)
        assert n == 28*k-26 and all(len(nb) == 3 for nb in a)
        ss = statistics(n, ge, initial)
        assert ss['pseudoforest'] and ss['isolated'] == 1
        assert len(ss['leaves']) == n//2+1
        path = [initial]
        for off in offsets[:k-1]:
            path.append(path[-1] ^ bitmask(ge, [(off+u, off+v) for u, v in delta_edges]))
        path.append(path[-1] ^ bitmask(ge, cores[0]))
        stats = [statistics(n, ge, f) for f in path]
        assert [s['isolated'] for s in stats] == list(range(1, k+1)) + [0]
        assert all(s['pseudoforest'] for s in stats)
        selected = set(stats[-1]['leaves'])
        assert good(a, selected) and len(selected) == n//2
        # Boundary-table upper bound: neither core, or exactly one core.
        assert max(14*(k-1), k+13*(k-1)) == n//2
        record = dict(k=k, order=n, graph6=graph6(a), edges=ge,
                      factor_encoding='Bit i refers to edges[i], in lexicographic (u,v) order.',
                      initial_factor=initial, initial_statistics=ss,
                      escape_path=path, escape_j=[s['isolated'] for s in stats],
                      escape_factor_sizes=[s['edges'] for s in stats],
                      final_good_set=sorted(selected), optimum=n//2,
                      exact_barrier_height=k, exact_excess_barrier=k-1,
                      exact_shortest_repair_length=k,
                      monotone_component_size=12**(2*k-2))
        if k == 3:
            allcycles = [bitmask(ge, c) for c in cycle_edges(a)]
            assert len(allcycles) == 430
            counts = Counter()
            for c in allcycles:
                s = statistics(n, ge, initial ^ c)
                counts[(s['pseudoforest'], s['isolated'])] += 1
            record['one_step_table'] = [dict(pseudoforest=ps, j=j, count=v)
                                       for (ps, j), v in sorted(counts.items())]
            # Exhaust the complete product of neutral cap states globally.
            fixed = initial
            lifted = []
            for off in offsets:
                fixed ^= bitmask(ge, [(off+u, off+v) for i, (u, v) in enumerate(es) if x >> i & 1])
                lifted.append([bitmask(ge, [(off+u, off+v) for i, (u, v) in enumerate(es) if f >> i & 1])
                               for f in sorted(zero)])
            states = 0
            for fs in itertools.product(*lifted):
                f = fixed
                for local in fs:
                    f |= local
                s = statistics(n, ge, f)
                assert s['pseudoforest'] and s['isolated'] == 1
                for core in cores:
                    assert not statistics(n, ge, f ^ bitmask(ge, core))['pseudoforest']
                states += 1
            assert states == 20736
            record['neutral_states_checked_globally'] = states
            record['core_exits_checked_globally'] = 2*states
        families.append(record)
    (OUT/'barrier_family.json').write_text(json.dumps(families, indent=2)+'\n')
    cover_orders = check_cover_repairs()
    result = dict(general_conjecture_resolved=False,
                  monotone_pseudoforest_repair_assertion='disproved',
                  cap_edge_subsets=1 << len(es), cap_parity_states=len(table),
                  cap_vertex_subsets=1 << 13, cap_simple_cycles=len(cycles),
                  zero_cost_cap_states=len(zero), local_transitions_checked=len(zero)*len(cycles),
                  neutral_states_checked_globally=20736, core_exits_checked_globally=41472,
                  family_orders=[r['order'] for r in families],
                  first_escape_j=families[0]['escape_j'],
                  bridgeless_double_cover_orders=cover_orders,
                  double_cover_repairs='All have verified two-cycle repairs with j=2,1,0 and good sets of order n/2+4.',
                  scope='Finite checks support the unrestricted barrier theorem. Every constructed graph has c_ind=n/2; none is a counterexample to the original conjecture.')
    result['sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(OUT.glob('*.json'))}
    (ROOT/'round11_verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
