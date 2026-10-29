"""Reproducible larger inputs for the odd-factor and rooted-cap search."""
import json
import random
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify_bridge_reduction import cap, edges, franklin, graph, tree_family


def nx_graph(adj):
    g = nx.Graph()
    g.add_nodes_from(range(len(adj)))
    g.add_edges_from(edges(adj))
    return g


def ring(blocks):
    g = nx.Graph()
    for i in range(blocks):
        g.add_edges_from((12*i+u, 12*i+v) for u, v in edges(franklin())
                         if (u, v) != (2, 4))
        g.add_edge(12*i+4, 12*((i+1) % blocks)+2)
    return g


def switch(g, rng):
    for _ in range(100):
        (a, b), (c, d) = rng.sample(list(g.edges()), 2)
        if rng.randrange(2):
            c, d = d, c
        if len({a, b, c, d}) < 4 or g.has_edge(a, d) or g.has_edge(c, b):
            continue
        h = g.copy()
        h.remove_edges_from([(a, b), (c, d)])
        h.add_edges_from([(a, d), (c, b)])
        if nx.is_connected(h):
            return h
    raise RuntimeError('no legal switch')


def main():
    rng = random.Random(2026102707)
    cases = []
    seen = set()

    def keep(g, family):
        g = nx.convert_node_labels_to_integers(g, ordering='sorted')
        assert nx.is_connected(g) and all(d == 3 for _, d in g.degree())
        code = nx.to_graph6_bytes(g, header=False).decode().strip()
        if code not in seen:
            seen.add(code)
            cases.append({'graph6': code, 'family': family, 'order': len(g)})

    for name in ('descent26_best.g6', 'descent30_best.g6', 'lex26_best.g6', 'lex_tight26_best.g6'):
        for code in (ROOT/'round5_data'/name).read_text().splitlines():
            keep(nx.from_graph6_bytes(code.encode()), 'retained local-search candidate')
    seeds = [ring(2), ring(3), nx_graph(tree_family([])[0]),
             nx_graph(tree_family(graph(1))[0])]
    for base in seeds:
        keep(base, 'sharp construction')
        for trial in range(40):
            g = base.copy()
            for _ in range(1+trial % 8):
                g = switch(g, rng)
            keep(g, 'one to eight switches from a sharp construction')
    for n in (24, 26, 30, 34, 38, 42):
        for trial in range(12):
            while True:
                g = nx.random_regular_graph(3, n, seed=rng.randrange(2**32))
                if nx.is_connected(g):
                    break
            keep(g, 'seeded random cubic')
    dest = ROOT/'round7_data'
    (dest/'larger_instances.g6').write_text(''.join(r['graph6']+'\n' for r in cases))
    (dest/'larger_instances.json').write_text(json.dumps({
        'seed': 2026102707, 'cases': cases,
        'scope': 'labelled samples, not an exhaustive graph census'}, indent=2)+'\n')
    print(json.dumps({'cases': len(cases), 'orders': sorted({r['order'] for r in cases})}))


if __name__ == '__main__':
    main()
