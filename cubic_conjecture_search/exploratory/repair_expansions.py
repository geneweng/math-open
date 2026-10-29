"""Seeded triangle expansions of the three order-20 repair obstructions."""
import json
from pathlib import Path
import random
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]


def edge_order(g):
    return [(u, v) for v in range(len(g)) for u in range(v) if g.has_edge(u, v)]


def main():
    rng = random.Random(2026102710)
    records = json.loads((ROOT / 'round9_verification.json').read_text())['order20']['cases']
    seeds = [r for r in records if r['connectivity'] == 3]
    output, seen = [], set()
    for seed in seeds:
        for trial in range(100):
            g = nx.from_graph6_bytes(seed['graph6'].encode())
            f = nx.Graph(); f.add_nodes_from(g)
            f.add_edges_from(e for i, e in enumerate(edge_order(g)) if seed['factor'] >> i & 1)
            expansion_vertices = []
            for step in range(11):
                eligible = [v for v in f if f.degree(v) == 1 and f.degree(next(iter(f[v]))) == 3]
                v = rng.choice(eligible)
                a, b = len(g), len(g) + 1
                y, z = sorted(set(g[v]) - set(f[v]))
                g.remove_edges_from([(v, y), (v, z)])
                g.add_edges_from([(v, a), (v, b), (a, b), (a, y), (b, z)])
                f.add_edges_from([(v, a), (v, b)])
                expansion_vertices.append(v)
                assert all(d == 3 for _, d in g.degree())
                assert all(d in (1, 3) for _, d in f.degree())
                code = nx.to_graph6_bytes(g, header=False).decode().strip()
                mask = sum(1 << i for i, e in enumerate(edge_order(g)) if f.has_edge(*e))
                if (code, mask) in seen:
                    continue
                seen.add((code, mask))
                output.append(dict(graph6=code, factor=mask, seed_graph6=seed['graph6'],
                                   seed_factor=seed['factor'], trial=trial, expansions=expansion_vertices.copy()))
    directory = ROOT / 'round10_data'
    (directory / 'expansion_inputs.txt').write_text(''.join(f"{r['graph6']} {r['factor']}\n" for r in output))
    (directory / 'expansion_inputs.json').write_text(json.dumps(dict(seed=2026102710, records=output), indent=2) + '\n')
    print(json.dumps(dict(cases=len(output), orders=sorted(set(ord(r['graph6'][0])-63 for r in output)))))


if __name__ == '__main__':
    main()
