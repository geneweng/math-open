"""Independent checks of the exchange obstructions; standard library only."""
import itertools
import json
from pathlib import Path
from verify_bridge_reduction import (
    CAP_IN, cap, edges, good, good_sets, graph, tree_family,
)
from verify_two_defect_search import decode

ROOT = Path(__file__).resolve().parent


def encode(adj):
    n = len(adj)
    bits = [int(u in adj[v]) for v in range(1, n) for u in range(v)]
    bits += [0] * (-len(bits) % 6)
    return chr(n + 63) + ''.join(chr(63 + sum(bits[i+j] << (5-j) for j in range(6)))
                               for i in range(0, len(bits), 6))


def cycle_edges(adj):
    """Every simple cycle exactly once, via minimum vertex and orientation."""
    for start in range(len(adj)):
        def extend(path, visited):
            for v in sorted(adj[path[-1]]):
                if v == start and len(path) >= 3:
                    if path[1] < path[-1]:
                        yield frozenset(tuple(sorted(e)) for e in
                                        zip(path, path[1:] + [start]))
                elif v > start and v not in visited:
                    yield from extend(path + [v], visited | {v})
        yield from extend([start], {start})


def selected_edges(adj, selected):
    return frozenset(e for e in edges(adj) if set(e) <= selected)


def single_cycle_difference(adj, first, second):
    delta = selected_edges(adj, first) ^ selected_edges(adj, second)
    if not delta:
        return False
    vertices = set(v for e in delta for v in e)
    seen = {next(iter(vertices))}
    while True:
        expanded = seen | {v for u, v in delta if u in seen} | {u for u, v in delta if v in seen}
        if expanded == seen:
            break
        seen = expanded
    return seen == vertices and all(sum(v in e for e in delta) == 2 for v in vertices)


def bridge_trap():
    g, optimum = tree_family(graph(2, [(0, 1)]))
    offsets = (6, 19, 32, 45)
    initial = {offset + v for offset in offsets for v in CAP_IN}
    assert len(g) == 58 and len(initial) == 28 and len(optimum) == 29
    assert good(g, initial) and good(g, optimum)
    assert all(len(nb) == 3 for nb in g)
    complement = set(range(58)) - initial
    assert sorted(len(g[v] & complement) for v in complement) == [2]*28 + [3]*2
    p = cap()
    cap_sets = list(good_sets(p))
    included = max(len(s) for s in cap_sets if 12 in s)
    excluded = max(len(s) for s in cap_sets if 12 not in s)
    assert (included, excluded) == (7, 6)
    # The two triangles are adjacent by a bridge. For each of the three
    # permitted triangle choices, maximize the four independent cap states.
    upper_bounds = [4*included, 3 + 2*excluded + 2*included]
    assert max(upper_bounds) == 29
    cap_cycles = list(cycle_edges(p))
    cycles = [frozenset((offset+u, offset+v) for u, v in c)
              for offset in offsets for c in cap_cycles]
    cycles += [frozenset(((0, 1), (1, 2), (0, 2))),
               frozenset(((3, 4), (4, 5), (3, 5)))]
    old_edges = selected_edges(g, initial)
    valid_moves = []
    for c in cycles:
        new_edges = old_edges ^ c
        selected = {v for e in new_edges for v in e}
        if good(g, selected) and selected_edges(g, selected) == new_edges:
            valid_moves.append(len(selected))
    assert valid_moves and max(valid_moves) <= 28
    # Explicit escape with the optimal two-vertex loss barrier.
    root_out = {0, 3, 5, 6, 8, 10}
    assert good(p, root_out) and single_cycle_difference(p, CAP_IN, root_out)
    path = [set(initial)]
    for offset in offsets[:2]:
        path.append((path[-1] - set(range(offset, offset+13))) |
                    {offset + v for v in root_out})
    path.append(path[-1] | {0, 1, 2})
    assert list(map(len, path)) == [28, 27, 26, 29]
    assert all(good(g, selected) for selected in path)
    assert all(single_cycle_difference(g, a, b) for a, b in zip(path, path[1:]))
    return dict(graph6=encode(g), order=58, initial=sorted(initial), optimum=29,
                initial_size=28, cap_simple_cycles=len(cap_cycles),
                all_simple_cycles_checked=len(cycles), valid_single_cycle_moves=len(valid_moves),
                largest_valid_single_cycle_result=max(valid_moves),
                escape_path=[sorted(s) for s in path], escape_sizes=list(map(len, path)),
                exact_loss_barrier=2)


def check_exchange_records():
    data = ROOT / 'round6_data'
    inputs = json.loads((data/'exchanges.json').read_text())['records']
    results = [json.loads(line) for line in (data/'exchange_results.jsonl').read_text().splitlines()]
    assert len(inputs) == len(results) == 600
    tested = 0
    histogram = {}
    for i, (row, result) in enumerate(zip(inputs, results)):
        adj = decode(row['graph6'])
        n = len(adj)
        s = {v for v in range(n) if row['planted'] >> v & 1}
        t = set(range(n)) - s
        assert good(adj, s) and len(s) == n//2-1
        assert all(len(adj[v] & s) <= 1 for v in t)
        assert result['case'] == i and result['status'] == 'OPTIMAL'
        witness = {v for v in range(n) if result['witness'] >> v & 1}
        radius = result['radius']
        assert good(adj, witness) and len(witness) > len(s)
        assert len(s-witness) == radius and radius in (1, 2)
        # Enumerate all smaller deletion choices. A new vertex adjacent to
        # an unchanged degree-two vertex would create degree three and is
        # forbidden. Exhaust every subset of the remaining possible vertices.
        for deleted_count in range(radius):
            for deleted in itertools.combinations(sorted(s), deleted_count):
                retained = s - set(deleted)
                if any(len(adj[v] & retained) == 0 for v in retained):
                    continue
                saturated = {v for v in retained if len(adj[v] & retained) == 2}
                allowed = sorted(v for v in t if not adj[v] & saturated)
                for mask in range(1 << len(allowed)):
                    chosen = retained | {v for j, v in enumerate(allowed) if mask >> j & 1}
                    tested += 1
                    assert len(chosen) <= len(s) or not good(adj, chosen)
        key = f'{n}:{radius}'
        histogram[key] = histogram.get(key, 0) + 1
    return dict(instances=600, exact_smaller_deletion_candidates=tested, radius_histogram=histogram)


def main():
    result = dict(bridge_trap=bridge_trap(), exchange_checks=check_exchange_records(),
                  general_conjecture_solved=False,
                  scope='Counterexamples to restricted improvement strategies, not to the induced-cycles conjecture.')
    (ROOT/'round6_verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'bridge_trap'}, indent=2))
    print(json.dumps({key: value for key, value in result['bridge_trap'].items()
                      if key not in ('initial', 'escape_path', 'graph6')}, indent=2))


if __name__ == '__main__':
    main()
