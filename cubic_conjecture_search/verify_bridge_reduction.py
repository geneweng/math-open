"""Independent finite checks for the bridge-completion paper; standard library only."""
import itertools
import json
from pathlib import Path


def graph(n, edges=()):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        assert u != v and v not in adj[u]
        adj[u].add(v)
        adj[v].add(u)
    return adj


def edges(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]


def good(adj, chosen):
    return all(len(adj[v] & chosen) == 2 for v in chosen)


def good_sets(adj):
    for mask in range(1 << len(adj)):
        chosen = {v for v in range(len(adj)) if (mask >> v) & 1}
        if good(adj, chosen):
            yield chosen


def franklin():
    es = []
    for i in range(3):
        es.extend((4*i+l, 4*i+2+r) for l in range(2) for r in range(2))
        es.extend((4*i+2+j, 4*((i+1) % 3)+j) for j in range(2))
    return graph(12, es)


def cap():
    es = [e for e in edges(franklin()) if e != (2, 4)]
    return graph(13, es + [(2, 12), (4, 12)])


CAP_IN = {0, 2, 4, 6, 8, 10, 12}
CAP_OUT = {1, 3, 5, 7, 9, 11}


def complete(base, selected):
    es = edges(base)
    chosen = set(selected)
    n = len(base)
    cap_edges = edges(cap())
    for v in range(len(base)):
        for _ in range(3-len(base[v])):
            es.extend((n+u, n+w) for u, w in cap_edges)
            es.append((v, n+12))
            chosen.update(n+u for u in (CAP_OUT if v in selected else CAP_IN))
            n += 13
    return graph(n, es), chosen


def tree_family(core):
    if not core:
        es = edges(cap()) + [(13+u, 13+v) for u, v in edges(cap())] + [(12, 25)]
        chosen = CAP_IN | {13+v for v in CAP_OUT}
        return graph(26, es), chosen
    assert len(edges(core)) == len(core)-1 and max(map(len, core)) <= 3
    colors = {0: 0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in core[v]:
            if u not in colors:
                colors[u] = 1-colors[v]
                stack.append(u)
    assert len(colors) == len(core)
    es = []
    chosen = set()
    for v in range(len(core)):
        es.extend([(3*v, 3*v+1), (3*v+1, 3*v+2), (3*v+2, 3*v)])
        if colors[v] == 0:
            chosen.update(range(3*v, 3*v+3))
    used = [0]*len(core)
    for u, v in edges(core):
        es.append((3*u+used[u], 3*v+used[v]))
        used[u] += 1
        used[v] += 1
    n = 3*len(core)
    for v in range(len(core)):
        for port in range(used[v], 3):
            es.extend((n+u, n+w) for u, w in edges(cap()))
            es.append((3*v+port, n+12))
            chosen.update(n+u for u in (CAP_OUT if colors[v] == 0 else CAP_IN))
            n += 13
    return graph(n, es), chosen


def main():
    f = franklin()
    deleted = graph(12, [e for e in edges(f) if e != (2, 4)])
    p = cap()
    fmax = max(map(len, good_sets(f)))
    deleted_max = max(map(len, good_sets(deleted)))
    a = max(len(s) for s in good_sets(p) if 12 in s)
    b = max(len(s) for s in good_sets(p) if 12 not in s)
    assert (fmax, deleted_max, a, b) == (6, 6, 7, 6)
    assert good(p, CAP_IN) and good(p, CAP_OUT)
    assert CAP_IN.isdisjoint(CAP_OUT) and CAP_IN | CAP_OUT == set(range(13))

    count = 0
    complement_cases = 0
    for n in range(1, 6):
        possible = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            h = graph(n, [e for i, e in enumerate(possible) if (mask >> i) & 1])
            if max(map(len, h)) > 3:
                continue
            branch = {v for v in range(n) if len(h[v]) == 3}
            for s in good_sets(h):
                t = set(range(n))-s
                complement_edges = sum(len(h[v] & t) for v in t)//2
                assert len(s & branch)-(len(edges(h))-n) == len(t)-complement_edges
                complement_cases += 1
            selected = max(good_sets(h), key=lambda s: len(s & branch))
            beta = len(selected & branch)
            d = sum(3-len(ns) for ns in h)
            completed, witness = complete(h, selected)
            assert all(len(ns) == 3 for ns in completed)
            assert len(completed) == n+13*d
            assert good(completed, witness)
            assert len(witness) == 7*d+beta
            assert 2*len(witness)-len(completed) == 2*(beta-len(edges(h))+n)
            count += 1

    cores = [[]]
    cores.extend(graph(n, [(i, i+1) for i in range(n-1)]) for n in range(1, 11))
    cores.append(graph(4, [(0, 1), (0, 2), (0, 3)]))
    cores.append(graph(7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]))
    orders = []
    for core in cores:
        g, chosen = tree_family(core)
        complement = set(range(len(g))) - chosen
        assert all(len(ns) == 3 for ns in g)
        assert good(g, chosen) and good(g, complement)
        assert len(chosen) == len(complement) == 8*len(core)+13
        if core:
            optimum = max(sum(len(core[v]) for v in range(len(core)) if (mask >> v) & 1)
                          for mask in range(1 << len(core))
                          if all(not ((mask >> u) & 1 and (mask >> v) & 1)
                                 for u, v in edges(core)))
            assert optimum == len(core)-1
        orders.append(len(g))
    result = {'cap_included_maximum': a, 'cap_excluded_maximum': b,
              'labelled_subcubic_bases_checked': count,
              'complement_identity_cases_checked': complement_cases,
              'sharp_tree_constructions_checked': len(cores),
              'sharp_tree_orders': orders, 'general_conjecture_solved': False}
    Path(__file__).with_name('bridge_reduction_results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
