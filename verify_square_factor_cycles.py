#!/usr/bin/env python3
"""Construct and independently check induced cycle covers for square factors.

Standard library only. This verifies a special-case theorem, not the general
Henning--Joos--Loewenstein--Sasse conjecture.
Run: python3 verify_square_factor_cycles.py
"""

import json
import random
from collections import Counter
from pathlib import Path


def edge(u, v):
    return min(u, v), max(u, v)


def make_graph(squares, matching):
    n = 4 * len(squares)
    assert sorted(v for square in squares for v in square) == list(range(n))
    edges = set()
    for square in squares:
        for i in range(4):
            edges.add(edge(square[i], square[(i + 1) % 4]))
    assert len(edges) == n
    for u, v in matching:
        assert u != v and edge(u, v) not in edges
        edges.add(edge(u, v))
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    assert all(len(ns) == 3 for ns in adj)
    return adj


def euler_circuits(vertex_count, edges, edge_ids):
    """Edges have distinct IDs; loops and parallel edges retain incidences."""
    adj = [[] for _ in range(vertex_count)]
    for eid in sorted(edge_ids):
        u, v = edges[eid]
        adj[u].append((v, eid))
        adj[v].append((u, eid))
    used = set()
    circuits = []
    for start in range(vertex_count):
        while adj[start] and adj[start][-1][1] in used:
            adj[start].pop()
        if not adj[start]:
            continue
        stack = [(start, None)]
        reverse = []
        while stack:
            v = stack[-1][0]
            while adj[v] and adj[v][-1][1] in used:
                adj[v].pop()
            if adj[v]:
                w, eid = adj[v].pop()
                used.add(eid)
                stack.append((w, (v, w, eid)))
            else:
                _, arrival = stack.pop()
                if arrival is not None:
                    reverse.append(arrival)
        circuit = list(reversed(reverse))
        assert circuit[-1][1] == circuit[0][0]
        assert all(a[1] == b[0] for a, b in zip(circuit, circuit[1:]))
        circuits.append(circuit)
    assert used == set(edge_ids)
    return circuits


def square_cover(squares, matching):
    """Return two induced 2-regular vertex sets whose union is V(G)."""
    adj = make_graph(squares, matching)
    owner = {v: i for i, square in enumerate(squares) for v in square}
    quotient = [(owner[u], owner[v]) for u, v in matching]
    q = len(squares)
    colors = {}
    for circuit in euler_circuits(q, quotient, range(len(matching))):
        assert len(circuit) % 2 == 0
        for i, (_, _, eid) in enumerate(circuit):
            colors[eid] = i % 2
    ports = [[set() for _ in range(q)] for _ in range(2)]
    for eid, (u, v) in enumerate(matching):
        ports[colors[eid]][owner[u]].add(u)
        ports[colors[eid]][owner[v]].add(v)
    assert all(len(p) == 2 for col in ports for p in col)
    bad = set()
    for i, square in enumerate(squares):
        positions = [j for j, v in enumerate(square) if v in ports[0][i]]
        if (positions[0] - positions[1]) % 4 == 2:
            bad.add(i)
    tails = [{}, {}]
    for color in range(2):
        ids = [eid for eid in colors if colors[eid] == color]
        for circuit in euler_circuits(q, quotient, ids):
            for a, b, eid in circuit:
                u, v = matching[eid]
                # A quotient loop still has two different original endpoints.
                tail = u if owner[u] == a else v
                assert a not in tails[color]
                tails[color][a] = tail
        assert len(tails[color]) == q
    result = []
    for color in range(2):
        chosen = set().union(*ports[color])
        chosen.update(tails[1 - color][i] for i in bad)
        result.append(chosen)
    check_cover(adj, *result)
    assert len(result[0]) == len(result[1]) == 2 * q + len(bad)
    return result[0], result[1], sorted(bad)


def check_cover(adj, a, b):
    """Verify directly in the original graph, without quotient information."""
    universe = set(range(len(adj)))
    assert a | b == universe
    for chosen in (a, b):
        assert all(len(adj[v] & chosen) == 2 for v in chosen)
    overlap = a & b
    assert all(len(adj[v] & overlap) == 1 for v in overlap)


def legal_matchings(remaining, forbidden):
    if not remaining:
        yield []
        return
    u = remaining[0]
    for j, v in enumerate(remaining[1:], 1):
        if edge(u, v) in forbidden:
            continue
        rest = remaining[1:j] + remaining[j + 1:]
        for tail in legal_matchings(rest, forbidden):
            yield [(u, v)] + tail


def factor_edges(squares):
    return {edge(s[i], s[(i + 1) % 4]) for s in squares for i in range(4)}


def enumerate_good_sets(adj):
    masks = [sum(1 << w for w in ns) for ns in adj]
    return [s for s in range(1 << len(adj))
            if all(not (s >> v & 1) or (s & masks[v]).bit_count() == 2
                   for v in range(len(adj)))]


def necklace(k):
    # Each block is K_{2,2}, in cycle order (left0,right0,left1,right1).
    squares = [(4*i, 4*i+2, 4*i+1, 4*i+3) for i in range(k)]
    matching = [(4*i+j+2, 4*((i+1) % k)+j) for i in range(k) for j in range(2)]
    return squares, matching


def necklace_dp(k):
    """Exact transfer computation on 16 block masks, including cyclic closure."""
    def compatible(a, b):
        left_a = (a & 3).bit_count()
        right_b = ((b >> 2) & 3).bit_count()
        for j in range(2):
            if a >> (j+2) & 1 and left_a + (b >> j & 1) != 2:
                return False
            if b >> j & 1 and right_b + (a >> (j+2) & 1) != 2:
                return False
        return True
    transitions = [[b for b in range(16) if compatible(a,b)] for a in range(16)]
    best = 0
    for start in range(16):
        dp = {start: start.bit_count()}
        for _ in range(k - 1):
            nxt = {}
            for a, value in dp.items():
                for b in transitions[a]:
                    nxt[b] = max(nxt.get(b, -1), value + b.bit_count())
            dp = nxt
        best = max(best, max((value for a, value in dp.items()
                             if start in transitions[a]), default=0))
    return best


def obstruction():
    # Two diamonds with tips joined to x=0,y=1, together with xy.
    edges = [(0,1)]
    for a,b,c,d in ((2,3,4,5),(6,7,8,9)):
        edges += [(a,c),(a,d),(b,c),(b,d),(c,d),(0,a),(1,b)]
    adj = [set() for _ in range(10)]
    for u,v in edges:
        adj[u].add(v); adj[v].add(u)
    good = enumerate_good_sets(adj)
    assert max(s.bit_count() for s in good) == 6
    assert not any(a | b == 1023 for a in good for b in good)
    # No edge is a bridge: test connectivity after deleting each one.
    for u,v in edges:
        seen = {0}
        stack = [0]
        while stack:
            z = stack.pop()
            for w in adj[z]:
                if edge(z,w) != edge(u,v) and w not in seen:
                    seen.add(w); stack.append(w)
        assert len(seen) == 10
    return {"order":10,"edges":edges,"good_set_count_including_empty":len(good),
            "maximum":6,"two_cover_exists":False,"bridgeless":True}


def main():
    report = {"status":"partial result; the general cubic conjecture is not solved",
              "exhaustive_fixed_square_factors":[], "random_seed":20261026}
    for q in (1,2,3):
        squares = [tuple(range(4*i,4*i+4)) for i in range(q)]
        count = 0
        hist = Counter()
        for matching in legal_matchings(tuple(range(4*q)), factor_edges(squares)):
            a,b,bad = square_cover(squares, matching)
            hist[len(bad)] += 1
            count += 1
        report["exhaustive_fixed_square_factors"].append(
            {"squares":q,"vertices":4*q,"legal_labeled_matchings":count,
             "split_square_count_histogram":dict(sorted(hist.items()))})
        print("exhaustive",q,count,flush=True)
    rng = random.Random(report["random_seed"])
    random_count = 0
    random_orders = (16,20,40,80,160,400)
    for n in random_orders:
        squares = [tuple(range(i,i+4)) for i in range(0,n,4)]
        forbidden = factor_edges(squares)
        for _ in range(100):
            while True:
                vertices = list(range(n)); rng.shuffle(vertices)
                matching = list(zip(vertices[::2],vertices[1::2]))
                if all(edge(*e) not in forbidden for e in matching):
                    break
            square_cover(squares,matching)
            random_count += 1
    report["sampled_constructions"] = {"count":random_count,"orders":random_orders,
                                      "per_order":100,"all_checks_passed":True}
    necklace_values = []
    for k in range(2,101):
        value = necklace_dp(k)
        expected = 3*k if k % 2 == 0 else 3*k-3
        assert value == expected
        necklace_values.append({"blocks":k,"order":4*k,"maximum":value})
    report["necklace_exact_transfer_checks"] = necklace_values
    squares,matching = necklace(3)
    adj = make_graph(squares,matching)
    good = enumerate_good_sets(adj)
    assert max(s.bit_count() for s in good) == 6
    a,b,bad = square_cover(squares,matching)
    report["sharp_example"] = {"order":12,"squares":squares,"matching":matching,
                               "maximum":6,"checked_vertex_subsets":4096,
                               "cover_a":sorted(a),"cover_b":sorted(b),
                               "good_set_size_histogram":dict(Counter(s.bit_count() for s in good))}
    report["obstruction_to_two_cover_extension"] = obstruction()
    path = Path(__file__).with_name("square_factor_cycles_results.json")
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("random constructions",random_count,flush=True)
    print("necklace parameters checked",len(necklace_values),flush=True)
    print("all exact checks passed; report:",path,flush=True)


if __name__ == "__main__":
    main()
