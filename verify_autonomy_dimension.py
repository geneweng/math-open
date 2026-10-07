#!/usr/bin/env python3
"""Exact finite checks accompanying autonomy_dimension.tex.

Requires Python 3.10+ and NetworkX. All graph tests and matrix ranks use
integer or rational arithmetic. Entropy decimals are only presentation.
Run: python3 verify_autonomy_dimension.py
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from math import comb, gcd, log2
from pathlib import Path

import networkx as nx


def indexed(graph):
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def flip_parameters(graph, bits):
    """Return exact (a,b), or None if a nonconstant bit is not autonomous."""
    if len(set(bits)) != 2:
        return None
    rates = [None, None]
    for vertex in graph:
        bit = bits[vertex]
        rate = Fraction(sum(bits[w] != bit for w in graph[vertex]),
                        graph.degree(vertex))
        if rates[bit] is not None and rates[bit] != rate:
            return None
        rates[bit] = rate
    return tuple(rates)


def autonomous_masks(graph):
    """Exhaust all nonconstant bits up to complementation (bit at 0 is 0)."""
    n = len(graph)
    neighbor_masks = [sum(1 << w for w in graph[v]) for v in range(n)]
    degrees = [graph.degree(v) for v in range(n)]
    result = []
    for mask in range(2, 1 << n, 2):
        rates = [None, None]
        for v in range(n):
            bit = (mask >> v) & 1
            selected = (mask & neighbor_masks[v]).bit_count()
            cross = degrees[v] - selected if bit else selected
            if rates[bit] is None:
                rates[bit] = (cross, degrees[v])
            elif cross * rates[bit][1] != rates[bit][0] * degrees[v]:
                break
        else:
            result.append(mask)
    return result


def exact_dimension(n, masks):
    """Exact minimum set cover on unordered vertex pairs, or None for infinity."""
    pairs = list(combinations(range(n), 2))
    full = (1 << len(pairs)) - 1
    covers = []
    union = 0
    for mask in masks:
        cover = sum(1 << p for p, (u, v) in enumerate(pairs)
                    if ((mask >> u) ^ (mask >> v)) & 1)
        covers.append(cover)
        union |= cover
    if union != full:
        return None
    for d in range((n - 1).bit_length(), min(n - 1, len(masks)) + 1):
        for selection in combinations(range(len(masks)), d):
            covered = 0
            for i in selection:
                covered |= covers[i]
            if covered == full:
                return d
    raise AssertionError("Separating family exists but search missed it")


def exact_rank(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    rows, cols = len(a), len(a[0])
    rank = 0
    for c in range(cols):
        pivot = next((i for i in range(rank, rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        divisor = a[rank][c]
        a[rank] = [x / divisor for x in a[rank]]
        for i in range(rank + 1, rows):
            if a[i][c]:
                multiplier = a[i][c]
                a[i] = [x - multiplier * y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def verify_code(graph, codes):
    assert len(codes) == len(graph)
    assert len(set(codes)) == len(graph)
    width = len(codes[0])
    assert all(len(code) == width for code in codes)
    rates = []
    for j in range(width):
        rate = flip_parameters(graph, [code[j] for code in codes])
        assert rate is not None
        rates.append([str(x) for x in rate])
    return rates


def windmill(r):
    """r copies of K4 sharing vertex 0, with disjoint outer triangles."""
    graph = nx.Graph()
    for i in range(r):
        graph.add_edges_from(combinations([0, 3*i+1, 3*i+2, 3*i+3], 2))
    return graph


def atlas_checks():
    counts = Counter()
    finite_graphs = []
    regular_complement_checks = 0
    for atlas_id, original in enumerate(nx.graph_atlas_g()):
        if len(original) < 2 or not nx.is_connected(original):
            continue
        graph = indexed(original)
        masks = autonomous_masks(graph)
        dimension = exact_dimension(len(graph), masks)
        counts[(len(graph), dimension)] += 1
        if dimension is not None:
            degrees = [graph.degree(v) for v in graph]
            total = sum(degrees)
            centered = []
            for mask in masks:
                mean = Fraction(sum(d for v, d in enumerate(degrees)
                                    if (mask >> v) & 1), total)
                centered.append([((mask >> v) & 1) - mean for v in graph])
            rank = exact_rank(centered)
            assert (len(graph)-1).bit_length() <= dimension <= rank <= len(graph)-1
            finite_graphs.append({"atlas_id": atlas_id, "order": len(graph),
                                  "dimension": dimension, "autonomy_rank": rank})
        if len(set(dict(graph.degree()).values())) == 1:
            complement = nx.complement(graph)
            if nx.is_connected(complement):
                assert masks == autonomous_masks(complement)
                regular_complement_checks += 1
    observed = [{"order": n, "dimension": d, "count": count}
                for (n, d), count in sorted(counts.items(),
                    key=lambda item: (item[0][0], item[0][1] or 999))]
    assert sum(counts.values()) == 995
    assert len(finite_graphs) == 19
    return {"connected_graph_count": 995, "finite_dimension_count": 19,
            "counts": observed, "finite_graphs": finite_graphs,
            "regular_complement_checks": regular_complement_checks}


def cycle_checks():
    result = []
    for n in range(3, 19):
        masks = autonomous_masks(nx.cycle_graph(n))
        signatures = [tuple((mask >> v) & 1 for mask in masks) for v in range(n)]
        g = gcd(n, 12)
        for u, v in combinations(range(n), 2):
            assert (signatures[u] == signatures[v]) == ((u-v) % g == 0)
        dimension = exact_dimension(n, masks)
        assert dimension == {3: 2, 4: 2, 6: 3, 12: 4}.get(n)
        result.append({"order": n, "cuts_up_to_complement": len(masks),
                       "signature_classes": len(set(signatures)),
                       "dimension": dimension})
    return result


def product_checks():
    vertices = [(x, y) for x in range(5) for y in range(5)]
    index = {v: i for i, v in enumerate(vertices)}
    graph = nx.Graph()
    for x, y in vertices:
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            graph.add_edge(index[x,y], index[(x+dx) % 5, (y+dy) % 5])
    u = [(x + 2*y) % 5 for x, y in vertices]
    v = [(x - 2*y) % 5 for x, y in vertices]
    assert len(set(zip(u, v))) == 25
    codes = [tuple((value >> j) & 1 for value in (u[i], v[i]) for j in range(3))
             for i in range(25)]
    rates = verify_code(graph, codes)
    adjacency = [[int(graph.has_edge(i, j)) for j in range(25)] for i in range(25)]
    ranks = {}
    for theta in range(-4, 4):
        rank = exact_rank([[adjacency[i][j] - theta * (i == j)
                            for j in range(25)] for i in range(25)])
        assert rank == (17 if theta == -1 else 25)
        ranks[str(theta)] = rank
    basis = [[5*int(coordinate[i] == a)-1 for i in range(25)]
             for coordinate in (u, v) for a in range(4)]
    assert exact_rank(basis) == 8
    assert all(sum(vector[j] for j in graph[i]) == -vector[i]
               for vector in basis for i in range(25))
    # The proof in the paper shows this family is complete; no 2^25 search.
    masks = set()
    for coordinate in (u, v):
        for selected in range(1, 31):
            mask = sum(1 << i for i in range(25) if (selected >> coordinate[i]) & 1)
            if mask & 1:
                mask ^= (1 << 25) - 1
            masks.add(mask)
    assert len(masks) == 30
    assert all(flip_parameters(graph, [(mask >> i) & 1 for i in range(25)])
               is not None for mask in masks)
    assert exact_dimension(25, sorted(masks)) == 6
    return {"order": 25, "dimension": 6, "candidate_family": "proof-assisted",
            "cuts_up_to_complement": 30, "ranks_A_minus_theta_I": ranks,
            "eigenbasis_rank": 8, "witness_flip_parameters": rates}


def windmill_checks():
    small = []
    for r in range(1, 4):
        graph = windmill(r)
        masks = autonomous_masks(graph)
        expected = set()
        # Independent combinatorial description: equal positive counts per triangle.
        for mask in range(2, 1 << len(graph), 2):
            counts = [sum((mask >> (3*i+j)) & 1 for j in (1,2,3)) for i in range(r)]
            if counts[0] > 0 and len(set(counts)) == 1:
                expected.add(mask)
        assert set(masks) == expected
        dimension = exact_dimension(len(graph), masks)
        assert dimension == {1: 2, 2: 4, 3: 4}[r]
        small.append({"triangles": r, "dimension": dimension,
                      "cuts_up_to_complement": len(masks)})
    code_w2 = ["0000", "1000", "0100", "0011", "0010", "0001", "1100"]
    verify_code(windmill(2), [tuple(map(int, code)) for code in code_w2])
    constructions = []
    for k in range(1, 5):
        width = 3*k
        full = (1 << width)-1
        subsets = sorted(sum(1 << i for i in choice)
                         for choice in combinations(range(width), k))
        used, matching = set(), []
        for first in subsets:
            if not (first & 1):
                continue
            rest = [i for i in range(width) if not (first >> i) & 1]
            for choice in combinations(rest, k):
                second = sum(1 << i for i in choice)
                third = full ^ first ^ second
                if second > third:
                    continue
                blocks = (first, second, third)
                if all(block not in used for block in blocks):
                    used.update(blocks)
                    matching.append(blocks)
        assert 9*len(matching) >= comb(3*k, k)
        codes = [tuple(0 for _ in range(width))]
        codes += [tuple((block >> i) & 1 for i in range(width))
                  for blocks in matching for block in blocks]
        rates = verify_code(windmill(len(matching)), codes)
        assert all(rate == ["1/3", "1"] for rate in rates)
        constructions.append({"width": width, "triangles": len(matching),
                              "order": len(codes), "available_words": comb(3*k,k)})
    h = -log2(1/3)/3 - 2*log2(2/3)/3
    return {"small_exact": small, "greedy_constructions": constructions,
            "H2_one_third": h, "asymptotic_ratio": 1/h}


def main():
    checks = {}
    for name, check in [("atlas", atlas_checks), ("cycles", cycle_checks),
                        ("product", product_checks), ("windmills", windmill_checks)]:
        checks[name] = check()
        print(f"PASS: {name}", flush=True)
    output = Path(__file__).with_name("autonomy_verification_results.json")
    output.write_text(json.dumps({"networkx_version": nx.__version__,
                                 "null_dimension_means": "infinity", **checks}, indent=2)+"\n")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
