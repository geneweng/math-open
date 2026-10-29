"""Seeded two-defect instances for the exchange-radius experiment."""
import argparse
import json
import random
from pathlib import Path
import networkx as nx


def instance(k, rng):
    s, length = 6 * k, 2 * k + 1
    g = nx.cycle_graph(s)
    a, b = s, s + 1
    next_vertex = s + 2
    for _ in range(3):
        path = [a] + list(range(next_vertex, next_vertex + length - 1)) + [b]
        next_vertex += length - 1
        g.add_edges_from(zip(path, path[1:]))
    colour = nx.bipartite.color(g)
    left = [v for v in range(s) if colour[v] == 0]
    right = [v for v in range(s) if colour[v] == 1]
    tl = [v for v in range(s, next_vertex) if g.degree(v) == 2 and colour[v] == 0]
    tr = [v for v in range(s, next_vertex) if g.degree(v) == 2 and colour[v] == 1]
    rng.shuffle(tl)
    rng.shuffle(tr)
    g.add_edges_from(zip(left, tr))
    g.add_edges_from(zip(right, tl))
    assert len(g) == 12 * k + 2 and nx.is_bipartite(g)
    assert all(d == 3 for _, d in g.degree())
    return g, (1 << s) - 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--cases', type=int, default=200)
    parser.add_argument('--seed', type=int, default=2026102706)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    records = []
    for k in (2, 3, 4):
        for _ in range(args.cases):
            g, selected = instance(k, rng)
            records.append(dict(graph6=nx.to_graph6_bytes(g, header=False).decode().strip(),
                                planted=selected, order=len(g), girth=nx.girth(g)))
    args.output.write_text('\n'.join(f"{r['graph6']} {r['planted']}" for r in records) + '\n')
    args.output.with_suffix('.json').write_text(json.dumps(dict(seed=args.seed, records=records), indent=2) + '\n')
    print(json.dumps(dict(cases=len(records), seed=args.seed)))


if __name__ == '__main__':
    main()
