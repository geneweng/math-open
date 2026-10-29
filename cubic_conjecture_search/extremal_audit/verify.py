"""Check positive certificates, isomorphisms and decompositions without CP-SAT.

Does not certify optimization upper bounds. Those are not needed for the
rooted-extension exclusion proved in REVIEW.txt.
"""
import json
from pathlib import Path
import networkx as nx

HERE = Path(__file__).resolve().parent


def edges(g):
    return {tuple(sorted(e)) for e in g.edges()}


def mapping_check(g, h, raw):
    m = {int(u): v for u, v in raw.items()}
    assert set(m) == set(g) and set(m.values()) == set(h)
    assert len(m) == len(set(m.values()))
    assert {tuple(sorted((m[u], m[v]))) for u, v in g.edges()} == edges(h)


def good(g, s):
    assert len(s) == len(set(s)) and set(s) <= set(g)
    return all(sum(u in s for u in g[v]) == 2 for v in s)


def tree_check(g, node, franklin):
    if 'atom' in node:
        assert set(node['vertices']) == set(g)
        assert {tuple(e) for e in node['edges']} == edges(g)
        if node['atom'] == 'Franklin':
            mapping_check(g, franklin, node['map_to_franklin'])
            return [1, 0]
        assert node['atom'] == 'triangle' and len(g) == 3 and len(g.edges()) == 3
        return [0, 1]
    cut = node['cut']
    assert len(cut) == 2 and all(g.has_edge(*e) for e in cut)
    h = g.copy()
    h.remove_edges_from(cut)
    cs = list(nx.connected_components(h))
    assert len(cs) == 2 and len(node['children']) == 2
    total = [0, 0]
    for vs, closure, child in zip(cs, node['closure_edges'], node['children']):
        assert sorted(closure) == sorted(v for e in cut for v in e if v in vs)
        assert len(set(closure)) == 2 and not h.has_edge(*closure)
        q = h.subgraph(vs).copy()
        q.add_edge(*closure)
        assert all(d == 3 for _, d in q.degree())
        atoms = tree_check(q, child, franklin)
        total = [a+b for a, b in zip(total, atoms)]
    return total


def main():
    report = json.loads((HERE/'audit.json').read_text())
    codes = (HERE.parent/report['source']).read_text().split()
    franklin = nx.from_graph6_bytes(codes[0].encode())
    seen, outputs = set(), []
    for row in report['classes']:
        g = nx.from_graph6_bytes(row['graph6'].encode())
        assert all(d == 3 for _, d in g.degree()) and nx.is_connected(g)
        for member in row['members']:
            i = member['index']
            assert i not in seen
            seen.add(i)
            mapping_check(nx.from_graph6_bytes(codes[i].encode()), g, member['map_to_representative'])
        s, t = row['optimization']['complementary_partition']
        assert set(s).isdisjoint(t) and set(s)|set(t) == set(g)
        assert len(s) == len(t) == len(g)//2 and good(g, s) and good(g, t)
        covered = set()
        for w in row['optimization']['edge_witnesses']:
            u, v = w['edge']
            assert g.has_edge(u, v) and u in w['good_set'] and v in w['good_set']
            assert good(g, w['good_set']) and len(w['good_set']) >= len(g)//2
            covered.add(tuple(sorted([u, v])))
        bridges = {tuple(sorted(e)) for e in nx.bridges(g)}
        assert covered == edges(g)-bridges
        dec = row['decomposition']
        assert {tuple(sorted(e)) for e in dec['bridges']} == bridges
        h = g.copy()
        h.remove_edges_from(bridges)
        assert {frozenset(c) for c in nx.connected_components(h)} == {
            frozenset(c['vertices']) for c in dec['components']}
        atoms = [0, 0]
        for c in dec['components']:
            q = h.subgraph(c['vertices']).copy()
            for step in c['suppressions']:
                v = step['vertex']; a, b = step['neighbours']
                assert set(q[v]) == {a, b} and not q.has_edge(a, b)
                q.remove_node(v); q.add_edge(a, b)
            new = tree_check(q, c['result'], franklin)
            atoms = [a+b for a, b in zip(atoms, new)]
        outputs.append(dict(order=len(g), records=len(row['members']),
                            bridges=len(bridges), franklin_atoms=atoms[0],
                            triangle_atoms=atoms[1], covered_edges=len(covered)))
    assert seen == set(range(len(codes)))
    for i, a in enumerate(report['classes']):
        for b in report['classes'][:i]:
            assert not nx.is_isomorphic(nx.from_graph6_bytes(a['graph6'].encode()),
                                        nx.from_graph6_bytes(b['graph6'].encode()))
    result = dict(records=len(codes), distinct_types=len(outputs), types=outputs,
                  half_set_edge_witnesses=sum(x['covered_edges'] for x in outputs),
                  optimization_upper_bounds_checked=False,
                  rooted_extension_exclusion_certificates_checked=True)
    (HERE/'verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
