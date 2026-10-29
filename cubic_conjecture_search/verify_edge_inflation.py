"""Exact checks for edge inflation; standard library only."""
import itertools
import json
from pathlib import Path
from verify_bridge_reduction import franklin, graph, edges, good
from verify_certificates import graph6

PORTS = (2, 4)
OFF = {1, 3, 5, 7, 9, 11}
ON = {0, 2, 4, 6, 8, 10}


def fragment():
    return graph(12, [e for e in edges(franklin()) if e != PORTS])


def table():
    h = fragment()
    values = {}
    witnesses = {}
    for mask in range(1 << 12):
        chosen = {v for v in range(12) if mask >> v & 1}
        state = []
        valid = True
        for v in range(12):
            if v not in chosen:
                if v in PORTS:
                    state.append(0)
                continue
            degree = len(h[v] & chosen)
            if v in PORTS:
                if degree not in (1, 2):
                    valid = False
                    break
                state.append(3-degree)
            elif degree != 2:
                valid = False
                break
        if valid:
            key = tuple(state)
            if len(chosen) > values.get(key, -1):
                values[key] = len(chosen)
                witnesses[key] = sorted(chosen)
    expected = {(0, 0): 6, (0, 1): 6, (1, 0): 6, (2, 2): 6}
    assert values == expected
    return values, witnesses


def packing(order, base_edges):
    """Allow loops and parallel edges; a loop contributes two to the degree."""
    best = -1
    best_edges = None
    for mask in range(1 << len(base_edges)):
        degrees = [0] * order
        chosen_edges = []
        for i, (u, v) in enumerate(base_edges):
            if mask >> i & 1:
                degrees[u] += 1
                degrees[v] += 1
                chosen_edges.append(i)
        if all(d in (0, 2) for d in degrees):
            score = sum(d == 2 for d in degrees)
            if score > best:
                best, best_edges = score, chosen_edges
    return best, best_edges


def inflate(order, base_edges, chosen_edges):
    chosen_edges = set(chosen_edges)
    base_degree = [0] * order
    selected_degree = [0] * order
    es = []
    chosen = set()
    offset = order
    for i, (u, v) in enumerate(base_edges):
        base_degree[u] += 1
        base_degree[v] += 1
        es.extend((offset+a, offset+b) for a, b in edges(fragment()))
        es.extend([(u, offset+PORTS[0]), (v, offset+PORTS[1])])
        chosen.update(offset+x for x in (ON if i in chosen_edges else OFF))
        if i in chosen_edges:
            selected_degree[u] += 1
            selected_degree[v] += 1
        offset += 12
    assert all(d == 3 for d in base_degree)
    assert all(d in (0, 2) for d in selected_degree)
    chosen.update(v for v, d in enumerate(selected_degree) if d == 2)
    result = graph(offset, es)
    assert all(len(ns) == 3 for ns in result)
    assert good(result, chosen)
    assert len(result) == 19*order
    assert len(chosen) == 6*len(base_edges)+sum(d == 2 for d in selected_degree)
    return result, chosen


def loop_tree(core_order):
    """The internal degree-three vertices form a path; leaves carry loops."""
    if core_order == 0:
        return 2, [(0, 1), (0, 0), (1, 1)]
    es = [(i, i+1) for i in range(core_order-1)]
    degrees = [0] * core_order
    for u, v in es:
        degrees[u] += 1
        degrees[v] += 1
    n = core_order
    for v in range(core_order):
        for _ in range(3-degrees[v]):
            es.extend([(v, n), (n, n)])
            n += 1
    return n, es


def main():
    values, witnesses = table()
    cases = [(2, [(0, 1)]*3), loop_tree(0), loop_tree(1), loop_tree(2)]
    # The finite base census is already stored in the repository.
    data = json.loads(Path(__file__).with_name('certificates.json').read_text())
    for record in data['graphs']:
        adj = graph6(record['graph6'])
        if len(adj) <= 8:
            cases.append((len(adj), edges(adj)))
    checked = []
    for n, es in cases:
        optimum, chosen_edges = packing(n, es)
        result, chosen = inflate(n, es, chosen_edges)
        assert 2*optimum >= n+2
        checked.append({'base_order': n, 'base_edges': es, 'cycle_packing_maximum': optimum,
                        'expanded_order': len(result), 'induced_cycle_maximum_by_exact_formula': len(chosen)})
    sharp = []
    for t in range(11):
        n, es = loop_tree(t)
        selected = [i for i, (u, v) in enumerate(es) if u == v]
        result, chosen = inflate(n, es, selected)
        assert n == 2*t+2 and len(result) == 38*t+38
        assert len(chosen) == 19*t+20
        sharp.append({'internal_tree_vertices': t, 'order': len(result), 'maximum': len(chosen)})
    result = {'fragment_table': {str(k): v for k, v in values.items()},
              'fragment_witnesses': {str(k): v for k, v in witnesses.items()},
              'small_base_checks': checked, 'sharp_family_checks': sharp,
              'general_conjecture_solved': False}
    Path(__file__).with_name('edge_inflation_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'fragment_states': len(values), 'small_bases_checked': len(checked),
                      'sharp_family_members_checked': len(sharp), 'general_conjecture_solved': False}, indent=2))


if __name__ == '__main__':
    main()
