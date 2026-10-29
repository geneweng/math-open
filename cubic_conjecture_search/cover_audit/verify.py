"""Verify the two-lift audit and the explicit common-cover construction.

The finite exact optima are cross-checked against independent cycle-space
enumeration. The general statements are proved in RESULTS.txt.
"""
import collections
import json
from pathlib import Path
import subprocess
import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
codes = (ROOT/'round30_data/extension_parents.g6').read_text().split()
F = nx.from_graph6_bytes(codes[0].encode())


def good(g, s):
    s = set(s)
    return all(len(set(g[v]) & s) == 2 for v in s)


def coloured_neighbours(g, left):
    remaining = g.copy()
    result = {v: {} for v in g}
    for colour in range(3):
        matching = nx.algorithms.bipartite.maximum_matching(remaining, top_nodes=left)
        assert len(matching) == len(g)
        for v, u in matching.items():
            result[v][colour] = u
        remaining.remove_edges_from((v, matching[v]) for v in left)
    assert remaining.number_of_edges() == 0
    return result


def common_cover(g):
    # The canonical bipartite double cover.
    h = nx.Graph()
    h.add_nodes_from((v, b) for v in g for b in (0, 1))
    for u, v in g.edges():
        h.add_edge((u, 0), (v, 1)); h.add_edge((u, 1), (v, 0))
    hc = coloured_neighbours(h, {(v, 0) for v in g})
    fb = nx.algorithms.bipartite.color(F)
    fc = coloured_neighbours(F, {v for v in F if fb[v] == 0})
    cover = nx.Graph()
    cover.add_nodes_from((v, b, f) for v, b in h for f in F if fb[f] == b)
    for v, b, f in list(cover):
        for c in range(3):
            u, d = hc[v, b][c]
            cover.add_edge((v, b, f), (u, d, fc[f][c]))
    assert len(cover) == 12*len(g)
    return cover


def main():
    lifts = json.loads((HERE/'two_lifts.json').read_text())
    exact = [json.loads(s) for s in (HERE/'cycle_space_check.jsonl').read_text().splitlines()]
    assert len(lifts) == len(exact) == 127
    assert {r['mask'] for r in lifts} == set(range(1,128))
    tree = {tuple(sorted(e)) for e in nx.bfs_edges(F,0)}
    free = [e for e in sorted(F.edges()) if e not in tree]
    histogram = collections.Counter()
    sharp_masks = []
    target = nx.from_graph6_bytes(codes[1].encode())
    for r, q in zip(lifts, exact):
        g = nx.from_graph6_bytes(r['graph6'].encode())
        negative = {e for i, e in enumerate(free) if r['mask']>>i&1}
        expected = {tuple(sorted((u+12*b, v+12*(b^int((u,v) in negative)))))
                    for u,v in F.edges() for b in (0,1)}
        assert {tuple(sorted(e)) for e in g.edges()} == expected
        assert nx.is_connected(g)
        assert r['graph6'] == q['graph6'] and r['status'] == 'OPTIMAL'
        assert r['lower'] == r['upper'] == q['maximum']
        assert good(g, r['witness']) and len(r['witness']) == q['maximum']
        assert q['factors_checked'] == 8192
        histogram[q['maximum']] += 1
        if q['maximum'] == 12:
            assert nx.is_isomorphic(g,target) and nx.edge_connectivity(g) == 2
            sharp_masks.append(r['mask'])

    certificate = json.loads((ROOT/'extremal_audit/audit.json').read_text())['classes'][0]['optimization']
    base_sets = certificate['complementary_partition'] + [w['good_set'] for w in certificate['edge_witnesses']]
    tested, components, witnesses = 0, 0, 0
    inputs = []
    for n in (4,6,8,10,12):
        inputs += subprocess.check_output(['geng','-cq','-d3','-D3',str(n)],text=True).split()
    inputs.append(codes[2])  # A bridged base, to test that case explicitly.
    for code in inputs:
        g = nx.from_graph6_bytes(code.encode()); c = common_cover(g)
        for v,b,f in c:
            assert {u for u,d,j in c[v,b,f]} == set(g[v])
            assert {j for u,d,j in c[v,b,f]} == set(F[f])
            assert len(c[v,b,f]) == 3
        for vs in nx.connected_components(c):
            part = c.subgraph(vs)
            gf = collections.Counter(v for v,b,f in vs)
            ff = collections.Counter(f for v,b,f in vs)
            assert set(gf) == set(g) and len(set(gf.values())) == 1
            assert set(ff) == set(F) and len(set(ff.values())) == 1
            for s in base_sets:
                selected = {x for x in vs if x[2] in s}
                assert len(selected)*2 == len(vs) and good(part, selected)
                witnesses += 1
            components += 1
        tested += 1

    # Q3 / antipodal identification is K4; a face projects to all of K4.
    cube = nx.hypercube_graph(3)
    orbit = lambda v: min(v, tuple(1-x for x in v))
    quotient = nx.Graph()
    quotient.add_edges_from((orbit(u), orbit(v)) for u,v in cube.edges())
    assert nx.is_isomorphic(quotient, nx.complete_graph(4))
    for v in cube:
        assert {orbit(u) for u in cube[v]} == set(quotient[orbit(v)])
    face = {v for v in cube if v[0] == 0}
    assert good(cube, face) and not good(quotient, {orbit(v) for v in face})
    result = dict(two_lifts=127, exact_optimum_histogram=dict(histogram),
                  sharp_masks=sharp_masks, sharp_isomorphism_types=1,
                  common_cover_bases_checked=tested, components_checked=components,
                  pulled_back_half_sets_checked=witnesses,
                  projection_failure_checked=True, original_conjecture='unresolved')
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
