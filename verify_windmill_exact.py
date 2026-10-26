#!/usr/bin/env python3
"""Exact certificates for the windmill autonomy formula.

Run with Python 3.10+ and NetworkX. No numerical optimization is used.
We verify the rank-count construction and dual bound through dimension 300,
and construct capacity-attaining binary codes through dimension 10 by implementing
the balancing operation in Bryant (2016), Theorem 1.
"""

from collections import Counter
from itertools import combinations
import json
from math import comb, log2, pi, sqrt
from pathlib import Path

import networkx as nx


def binomial(d, j):
    return comb(d, j) if 0 <= j <= d else 0


def capacity(d):
    if d < 2:
        return 0
    k, residue = divmod(d, 3)
    b = lambda j: binomial(d, j)
    s = lambda j: sum(b(i) for i in range(j + 1))
    if residue == 0:
        return s(k - 2) + (2 * b(k - 1) + b(k)) // 3
    if residue == 1:
        return s(k - 1) + b(k) // 2
    return s(k - 2) + b(k) + 3 * b(k - 1) // 4


def dimension(r):
    if r < 1:
        raise ValueError("r must be positive")
    d = 2
    while capacity(d) < r:
        d += 1
    return d


def type_counts(d):
    """Optimal multiset of triples of block sizes; empty blocks are allowed."""
    assert d >= 2
    k, residue = divmod(d, 3)
    b = lambda j: binomial(d, j)
    counts = Counter()

    def add(sizes, count):
        if count:
            assert min(sizes) >= 0 and sum(sizes) == d
            counts[tuple(sorted(sizes))] += count

    if residue == 0:
        for j in range(k - 1):
            add((j, k + 1, 2 * k - 1 - j), b(j))
        add((k - 1, k, k + 1), b(k - 1))
        add((k, k, k), (b(k) - b(k - 1)) // 3)
    elif residue == 1:
        for j in range(k):
            add((j, k + 1, 2 * k - j), b(j))
        add((k, k, k + 1), b(k) // 2)
    else:
        for j in range(k - 1):
            add((j, k + 2, 2 * k - j), b(j))
        a, b_k = b(k - 1), b(k)
        x = (a + 1) // 4
        y = b_k - (a + 1) // 2
        add((k - 1, k + 1, k + 2), a)
        add((k, k, k + 2), x)
        add((k, k + 1, k + 1), y)
    return counts


def dual_weights(d):
    """Return integer numerators and a common denominator for the dual."""
    k, residue = divmod(d, 3)
    t = k + 2 if residue == 2 else k + 1
    denominator = 3 * t - d
    return [min(denominator, max(0, t - j)) for j in range(d + 1)], denominator


def verify_arithmetic(d):
    counts = type_counts(d)
    used = Counter()
    for sizes, multiplicity in counts.items():
        assert sum(sizes) == d and len(sizes) == 3
        for size in sizes:
            used[size] += multiplicity
    assert all(used[j] <= binomial(d, j) for j in range(d + 1))
    assert sum(counts.values()) == capacity(d)
    weights, denominator = dual_weights(d)
    for a in range(d + 1):
        for b in range(a, (d - a) // 2 + 1):
            c = d - a - b
            assert weights[a] + weights[b] + weights[c] >= denominator
    bound = sum(binomial(d, j) * weights[j] for j in range(d + 1))
    assert bound // denominator == capacity(d)
    return {"dimension": d, "capacity": capacity(d),
            "dual_numerator": bound, "dual_denominator": denominator,
            "types": [{"sizes": list(sizes), "count": count}
                      for sizes, count in sorted(counts.items())]}


def realize_partitions(d):
    """Construct optimal partitions by exact recoloring of the Boolean lattice.

    A color is a triple with a prescribed list of sizes; color 0 holds unused
    subsets. Swapping two coordinates induces pairs of equal-sized subsets.
    A balanced Euler orientation of the auxiliary color multigraph gives
    simultaneous swaps that balance those two coordinate degrees in every
    color. The sum of squared degrees strictly decreases each iteration.
    """
    types = type_counts(d)
    r = capacity(d)
    colors = [0] * (1 << d)
    by_size = [[mask for mask in range(1 << d) if mask.bit_count() == j]
               for j in range(d + 1)]
    positions = [0] * (d + 1)
    color = 0
    for sizes, count in sorted(types.items()):
        for _ in range(count):
            color += 1
            for size in sizes:
                mask = by_size[size][positions[size]]
                positions[size] += 1
                assert colors[mask] == 0
                colors[mask] = color
    assert color == r

    def degrees():
        deg = [[0] * d for _ in range(r + 1)]
        for mask, label in enumerate(colors):
            for j in range(d):
                deg[label][j] += (mask >> j) & 1
        return deg

    iterations = 0
    while True:
        deg = degrees()
        bad = next((row for row in deg if max(row) - min(row) > 1), None)
        if bad is None:
            break
        alpha, beta = bad.index(max(bad)), bad.index(min(bad))
        potential = sum(x*x for row in deg for x in row)
        graph = nx.MultiGraph()
        pair_data = {}
        edge_id = 0
        for first in range(1 << d):
            if not ((first >> alpha) & 1) or ((first >> beta) & 1):
                continue
            second = first ^ (1 << alpha) ^ (1 << beta)
            a, b = colors[first], colors[second]
            if a == b:
                continue
            pair_data[edge_id] = (first, second, a, b)
            graph.add_edge(a, b, key=edge_id)
            edge_id += 1
        # Adjoin one auxiliary vertex to make all degrees even.
        auxiliary = r + 1
        for vertex in list(graph.nodes):
            if graph.degree(vertex) % 2:
                graph.add_edge(vertex, auxiliary, key=edge_id)
                edge_id += 1
        for component in nx.connected_components(graph):
            subgraph = graph.subgraph(component)
            for source, target, key in nx.eulerian_circuit(subgraph, keys=True):
                if key not in pair_data:
                    continue
                first, second, a, b = pair_data[key]
                assert {source, target} == {a, b}
                if source == b:
                    colors[first], colors[second] = b, a
        updated = degrees()
        assert all(abs(row[alpha] - row[beta]) <= 1 for row in updated)
        assert sum(x*x for row in updated for x in row) < potential
        iterations += 1

    partitions = [[] for _ in range(r)]
    for mask, label in enumerate(colors):
        if label:
            partitions[label - 1].append(mask)
    full = (1 << d) - 1
    used = set()
    for triple in partitions:
        assert len(triple) == 3
        assert len(set(triple)) == 3
        assert not any(a & b for a, b in combinations(triple, 2))
        assert triple[0] | triple[1] | triple[2] == full
        assert not used.intersection(triple)
        used.update(triple)
    missing = next(mask for mask in range(1 << d) if mask not in used)
    code = [0] + [mask ^ missing for triple in partitions for mask in triple]
    assert len(set(code)) == 3*r + 1
    assert all(value < (1 << d) for value in code)
    # Check cross-neighbor counts on the actual K4-windmill, with hub 0.
    for j in range(d):
        selected = [sum((word >> j) & 1 for word in code[3*i+1:3*i+4])
                    for i in range(r)]
        assert len(set(selected)) == 1 and selected[0] in (1, 2)
        k = selected[0]
        hub_cross, hub_degree = r*k, 3*r
        assert hub_cross * 3 == k * hub_degree
        for i in range(r):
            triangle = code[3*i+1:3*i+4]
            for word in triangle:
                bit = (word >> j) & 1
                # Its neighbors are the other two triangle words and the hub.
                cross = sum(((other >> j) & 1) != bit for other in triangle if other != word)
                cross += bit  # hub has bit zero
                assert cross == (4-k if bit else k)
    return {"dimension": d, "triangles": r, "balancing_iterations": iterations,
            "translation_mask": missing, "partitions_as_bitmasks": partitions,
            "vertex_codes_hex": [format(word, "x") for word in code]}


def main():
    for d in range(2, 301):
        verify_arithmetic(d)
    print("PASS: matching lower and upper arithmetic certificates, d=2..300", flush=True)
    witnesses = []
    for d in range(2, 11):
        witness = realize_partitions(d)
        witnesses.append(witness)
        print(f"PASS: capacity-attaining code d={d}, r={capacity(d)}, "
              f"balancing steps={witness['balancing_iterations']}", flush=True)
    assert [capacity(d) for d in range(2, 11)] == [1, 1, 3, 5, 10, 18, 35, 62, 116]
    assert dimension(18) == 7 and dimension(19) == 8
    h = log2(3) - 2/3
    constants = [7/(4*sqrt(pi)), 9/(4*2**(1/3)*sqrt(pi)),
                 45/(16*2**(2/3)*sqrt(pi))]
    result = {"networkx_version": nx.__version__,
              "arithmetic_verified_through_dimension": 300,
              "capacity_table": [verify_arithmetic(d) for d in range(2, 31)],
              "capacity_code_witnesses": witnesses,
              "asymptotic_h": h, "capacity_constants_by_residue": constants}
    output = Path(__file__).with_name("windmill_exact_results.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
