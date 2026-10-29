#!/usr/bin/env python3
"""Independent finite checks for odd-pseudoforest exchanges (standard library).

Uses direct edge-parity recursion and vertex-path cycle enumeration, rather
than the C++ cycle-space enumeration and disjoint-set component test.
No finite result from this program is a proof of the general conjecture.
"""
from collections import Counter, deque
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def decode(code):
    n = ord(code[0]) - 63
    assert 4 <= n <= 42 and n % 2 == 0
    assert len(code) == 1 + (n * (n - 1) // 2 + 5) // 6
    edges, adj, bit = [], [set() for _ in range(n)], 0
    for v in range(1, n):
        for u in range(v):
            if (ord(code[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                edges.append((u, v)); adj[u].add(v); adj[v].add(u)
            bit += 1
    assert all(len(a) == 3 for a in adj)
    return n, edges, adj


def cycles_of(n, edges, adj):
    index = {e: i for i, e in enumerate(edges)}
    cycles = []

    def visit(start, second, v, seen, mask):
        for u in sorted(adj[v]):
            edge = 1 << index[tuple(sorted((u, v)))]
            if u == start and second < v:
                cycles.append(mask | edge)
            elif u > start and not seen >> u & 1:
                visit(start, second, u, seen | (1 << u), mask | edge)

    for start in range(n):
        for u in sorted(adj[start]):
            if u > start:
                visit(start, u, u, (1 << start) | (1 << u),
                      1 << index[(start, u)])
    assert len(set(cycles)) == len(cycles)
    return cycles


def odd_factors(n, edges):
    last = [0] * n
    for i, (u, v) in enumerate(edges):
        last[u] = last[v] = i

    def visit(i, parity, mask):
        if i == len(edges):
            assert parity == (1 << n) - 1
            yield mask
            return
        u, v = edges[i]
        forced = {1 ^ (parity >> w & 1) for w in (u, v) if last[w] == i}
        if len(forced) == 2:
            return
        for bit in forced or (0, 1):
            yield from visit(i + 1, parity ^ (((1 << u) | (1 << v)) if bit else 0),
                             mask | (bit << i))

    yield from visit(0, 0, 0)


def statistics(n, edges, factor):
    assert 0 <= factor < 1 << len(edges)
    a = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if factor >> i & 1:
            a[u].append(v); a[v].append(u)
    assert all(len(x) in (1, 3) for x in a)
    seen, components = set(), []
    for s in range(n):
        if s in seen:
            continue
        todo, part = [s], []
        seen.add(s)
        while todo:
            v = todo.pop(); part.append(v)
            for u in a[v]:
                if u not in seen:
                    seen.add(u); todo.append(u)
        components.append((len(part), sum(len(a[v]) for v in part) // 2))
    leaves = [v for v in range(n) if len(a[v]) == 1]
    return dict(edges=factor.bit_count(),
                isolated=sum(v == 2 for v, e in components),
                pseudoforest=all(e <= v for v, e in components),
                components=sorted(components), leaves=leaves)


def analyze_case(code, factor, objective):
    n, edges, adj = decode(code)
    cycles = cycles_of(n, edges, adj)
    cache = {}

    def state(f):
        if f not in cache:
            cache[f] = statistics(n, edges, f)
        return cache[f]

    def score(s):
        return (s['edges'], -s['isolated']) if objective == 'lex' else (-s['isolated'],)

    initial = state(factor)
    assert initial['pseudoforest'] and initial['isolated'] > 0
    base = score(initial)
    table = Counter()
    improving, neutral = [], []
    for c in cycles:
        f = factor ^ c; s = state(f)
        if s['pseudoforest']:
            table[(s['edges'], s['isolated'])] += 1
            if score(s) > base:
                improving.append(f)
            elif score(s) == base:
                neutral.append(f)
    # Breadth-first search only the initial potential level, stopping at the
    # first strict improvement. The returned path has minimum move count.
    queue, parent, terminal = deque([factor]), {factor: None}, None
    while queue and terminal is None:
        f = queue.popleft()
        for c in cycles:
            nxt = f ^ c; s = state(nxt)
            if not s['pseudoforest'] or score(s) < base:
                continue
            if nxt in parent:
                continue
            parent[nxt] = f
            if score(s) > base:
                terminal = nxt
                break
            queue.append(nxt)
    path = []
    f = terminal
    while f is not None:
        path.append(f); f = parent[f]
    path.reverse()
    good = None
    if terminal is not None and state(terminal)['isolated'] == 0:
        good = state(terminal)['leaves']
        selected = set(good)
        assert all(len(adj[v] & selected) == 2 for v in selected)
        assert len(good) >= n / 2
    if n <= 16:
        good_sets = [s for s in range(1 << n)
                     if all(sum(s >> u & 1 for u in adj[v]) == 2
                            for v in range(n) if s >> v & 1)]
        optimum = max(s.bit_count() for s in good_sets)
    else:
        optimum = None
    def connected(excluded):
        left = set(range(n)) - set(excluded)
        todo = [next(iter(left))]; left.remove(todo[0])
        while todo:
            v = todo.pop()
            for u in adj[v] & left:
                left.remove(u); todo.append(u)
        return not left
    assert connected(())
    cut = next(([v] for v in range(n) if not connected([v])), None)
    if cut is None:
        cut = next(([u, v] for v in range(n) for u in range(v)
                    if not connected([u, v])), None)
    color, todo, bipartite = {0: 0}, [0], True
    while todo:
        v = todo.pop()
        for u in adj[v]:
            if u not in color:
                color[u] = 1-color[v]; todo.append(u)
            elif color[u] == color[v]:
                bipartite = False
    return dict(graph6=code, order=n, edges=edges, factor=factor,
                bipartite=bipartite, vertex_connectivity=len(cut) if cut else 3,
                minimum_vertex_cut=cut,
                factor_edges=[e for i, e in enumerate(edges) if factor >> i & 1],
                objective=objective, initial=initial, simple_cycles=len(cycles),
                allowed_move_table=[[m, k, count] for (m, k), count in sorted(table.items())],
                direct_improvements=len(improving), neutral_moves=len(neutral),
                repair_path=path, repair_path_statistics=[state(f) for f in path],
                minimum_repair_moves=len(path)-1 if path else None,
                neutral_states_discovered=len(parent) - (terminal is not None),
                good_witness=good, exact_c_ind=optimum)


def small_check():
    totals = Counter()
    codes = (ROOT / 'round8_data/cubic_through18.g6').read_text().splitlines()
    for n in (4, 6, 8, 10, 12):
        for code in (c for c in codes if ord(c[0]) - 63 == n):
            nn, edges, adj = decode(code)
            assert nn == n
            cycles = cycles_of(n, edges, adj)
            states = {f: statistics(n, edges, f) for f in odd_factors(n, edges)}
            assert len(states) == 1 << (n // 2 + 1)
            totals['graphs'] += 1
            totals['odd_factors'] += len(states)
            induced = []
            for c in cycles:
                vertices = {v for i, e in enumerate(edges) if c >> i & 1 for v in e}
                if all(len(adj[v] & vertices) == 2 for v in vertices):
                    induced.append(c)
            for f, s in states.items():
                if s['edges'] == n // 2:
                    totals['perfect_matchings'] += 1
                    candidates = [c for c in induced if 2 * (c & f).bit_count() < c.bit_count()]
                    assert candidates
                    for c in candidates:
                        after = states[f ^ c]
                        assert after['pseudoforest'] and after['isolated'] < s['isolated']
                        totals['matching_cycle_repairs'] += 1
                if not s['pseudoforest']:
                    continue
                totals['odd_pseudoforests'] += 1
                if s['isolated']:
                    totals['bad_odd_pseudoforests'] += 1
                    assert any(states[f ^ c]['pseudoforest'] and
                               states[f ^ c]['isolated'] < s['isolated'] for c in cycles)
    assert totals['graphs'] == 112 and totals['odd_factors'] == 12296
    assert totals['odd_pseudoforests'] == 10911
    assert totals['bad_odd_pseudoforests'] == 9334
    return dict(totals)


def main():
    bip = json.loads((ROOT / 'round8_data/bipartite_neutral_cases.json').read_text())[0]
    specs = [('M?AAD?WEIcKOHOb??', 1912485, 'lex'),
             ('O???C@_cSoAgQ_P_D_@D?', 4716667, 'lex'),
             ('M?`@?aGqBCCoDOCW?', 1296836, 'k2'),
             (bip['graph6'], bip['factor'], 'k2')]
    cases = []
    for code, factor, objective in specs:
        case = analyze_case(code, factor, objective)
        assert case['direct_improvements'] == 0
        cases.append(case)
        print(json.dumps({k: case[k] for k in ('order', 'objective', 'simple_cycles',
                         'neutral_moves', 'minimum_repair_moves')}), flush=True)
    assert cases[0]['minimum_repair_moves'] == 2
    assert cases[1]['neutral_moves'] == 0 and not cases[1]['repair_path']
    assert cases[2]['minimum_repair_moves'] == 2
    assert cases[3]['minimum_repair_moves'] == 2
    assert cases[3]['bipartite'] and cases[3]['vertex_connectivity'] == 2
    result = dict(status='Verified finite certificates; the general conjecture is unresolved.',
                  small_check=small_check(), cases=cases)
    (ROOT / 'round8_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['small_check'], sort_keys=True))


if __name__ == '__main__':
    main()
