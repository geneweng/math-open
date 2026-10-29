"""Reproduce the 216 lifted factors on 54 labelled edge replacements."""
import json
from pathlib import Path
import sys
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify_bridge_reduction import franklin, edges, good_sets
from verify_pseudoforest_repair import decode


def main():
    base_fragment = franklin()
    r = nx.Graph(); r.add_nodes_from(range(12))
    r.add_edges_from(e for e in edges(base_fragment) if e != (2, 4))
    trees = []
    for selected in good_sets(base_fragment):
        if len(selected) != 6 or selected & {2, 4}:
            continue
        tree = nx.Graph(); tree.add_nodes_from(range(12))
        tree.add_edges_from(e for e in r.edges if not set(e) <= selected)
        if nx.is_tree(tree):
            trees.append(list(tree.edges))
    assert len(trees) == 4
    cases = json.loads((ROOT / 'round9_verification.json').read_text())['order20']['cases']
    seeds = [s for s in cases if s['connectivity'] == 3]
    rows = []
    for seed in seeds:
        n, ge, _ = decode(seed['graph6'])
        g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(ge)
        me = [e for i, e in enumerate(ge) if seed['factor'] >> i & 1]
        mf = nx.Graph(); mf.add_nodes_from(range(n)); mf.add_edges_from(me)
        for u, v in me:
            if mf.degree(u) == mf.degree(v) == 1:
                continue
            for ti, tree in enumerate(trees):
                h = g.copy(); h.remove_edge(u, v); h.add_nodes_from(range(n, n + 12))
                h.add_edges_from((n + a, n + b) for a, b in r.edges)
                h.add_edges_from([(u, n + 2), (v, n + 4)])
                mm = mf.copy(); mm.remove_edge(u, v); mm.add_nodes_from(range(n, n + 12))
                mm.add_edges_from((n + a, n + b) for a, b in tree)
                mm.add_edges_from([(u, n + 2), (v, n + 4)])
                code = nx.to_graph6_bytes(h, header=False).decode().strip()
                ee = [(a, b) for b in range(len(h)) for a in range(b) if h.has_edge(a, b)]
                mask = sum(1 << i for i, e in enumerate(ee) if mm.has_edge(*e))
                rows.append(dict(graph6=code, factor=mask, base=seed['graph6'], edge=[u, v],
                                 fragment_tree_index=ti, fragment_tree_edges=tree))
    directory = ROOT / 'round10_data'
    inputs = ''.join(f"{r['graph6']} {r['factor']}\n" for r in rows)
    (directory / 'inflation_inputs.txt').write_text(inputs)
    (directory / 'inflation_inputs.json').write_text(json.dumps(rows, indent=2) + '\n')
    codes = sorted({r['graph6'] for r in rows})
    (directory / 'inflated_graphs.g6').write_text('\n'.join(codes) + '\n')
    print(json.dumps(dict(factors=len(rows), labelled_graphs=len(codes))))


if __name__ == '__main__':
    main()
