"""Reproduce the retained equality-library audit; no claim of completeness.

Requires NetworkX and OR-Tools. Positive witnesses and every decomposition
step are checked directly. Maximum upper bounds additionally rely on CP-SAT.
Run from any directory: python3 .../extremal_audit/audit.py
"""
import itertools
import json
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'round30_data/extension_parents.g6'


def edge_list(g):
    return sorted(sorted(e) for e in g.edges())


def isomorphism(g, h):
    gm = nx.algorithms.isomorphism.GraphMatcher(g, h)
    return gm.mapping if gm.is_isomorphic() else None


def good(g, s):
    s = set(s)
    return all(len(set(g[v]) & s) == 2 for v in s)


def split_two_cuts(g, franklin):
    for e, f in itertools.combinations(sorted(g.edges()), 2):
        h = g.copy()
        h.remove_edges_from([e, f])
        components = list(nx.connected_components(h))
        if len(components) != 2:
            continue
        pieces, closures = [], []
        for vertices in components:
            ports = [v for edge in (e, f) for v in edge if v in vertices]
            if len(ports) != 2 or ports[0] == ports[1] or h.has_edge(*ports):
                break
            q = h.subgraph(vertices).copy()
            q.add_edge(*ports)
            assert all(d == 3 for _, d in q.degree())
            pieces.append(q)
            closures.append(ports)
        if len(pieces) == 2:
            return dict(cut=[list(e), list(f)], closure_edges=closures,
                        children=[split_two_cuts(q, franklin) for q in pieces])
    mapping = isomorphism(g, franklin)
    assert mapping is not None, 'Unexpected terminal cubic core'
    return dict(atom='Franklin', vertices=sorted(g), edges=edge_list(g),
                map_to_franklin=mapping)


def decomposition(g, franklin):
    h = g.copy()
    bridges = list(nx.bridges(h))
    h.remove_edges_from(bridges)
    pieces = []
    for vs in nx.connected_components(h):
        q = h.subgraph(vs).copy()
        suppressions = []
        while len(q) > 3 and any(d == 2 for _, d in q.degree()):
            v = min(v for v, d in q.degree() if d == 2)
            a, b = sorted(q[v])
            assert not q.has_edge(a, b), 'Suppression would create parallel edges'
            suppressions.append(dict(vertex=v, neighbours=[a, b]))
            q.remove_node(v)
            q.add_edge(a, b)
        if all(d == 3 for _, d in q.degree()):
            result = split_two_cuts(q, franklin)
        else:
            assert len(q) == 3 and all(d == 2 for _, d in q.degree())
            result = dict(atom='triangle', vertices=sorted(q), edges=edge_list(q))
        pieces.append(dict(vertices=sorted(vs), suppressions=suppressions, result=result))
    return dict(bridges=[list(e) for e in bridges], components=pieces)


def optimization_audit(g):
    n = len(g)
    model = cp_model.CpModel()
    x = [model.new_bool_var(str(v)) for v in range(n)]
    for v in g:
        model.add(sum(x[u] for u in g[v]) == 2).only_enforce_if(x[v])
    model.maximize(sum(x))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 1
    assert solver.solve(model) == cp_model.OPTIMAL
    optimum = round(solver.objective_value)
    assert optimum == n // 2
    model.clear_objective()
    model.add(sum(x) == optimum)
    witnesses, uncovered = [], []
    for u, v in sorted(g.edges()):
        model.clear_assumptions()
        model.add_assumptions([x[u], x[v]])
        status = solver.solve(model)
        assert status in (cp_model.OPTIMAL, cp_model.INFEASIBLE)
        if status == cp_model.INFEASIBLE:
            uncovered.append(sorted([u, v]))
        else:
            s = [w for w in g if solver.value(x[w])]
            assert len(s) == optimum and u in s and v in s and good(g, s)
            witnesses.append(dict(edge=[u, v], good_set=s))
    # No cycle, hence no induced 2-regular subgraph, can contain a bridge.
    assert sorted(uncovered) == sorted(sorted(e) for e in nx.bridges(g))
    model.clear_assumptions()
    for v in g:
        model.add(sum(1-x[u] for u in g[v]) == 2).only_enforce_if(x[v].Not())
    assert solver.solve(model) == cp_model.OPTIMAL
    s = [v for v in g if solver.value(x[v])]
    t = sorted(set(g) - set(s))
    assert len(s) == len(t) == n // 2 and good(g, s) and good(g, t)
    return dict(maximum=optimum, upper_bound_method='CP-SAT OPTIMAL',
                complementary_partition=[s, t], edge_witnesses=witnesses,
                uncovered_edges=uncovered)


def main():
    codes = SOURCE.read_text().split()
    classes = []
    for i, code in enumerate(codes):
        g = nx.from_graph6_bytes(code.encode())
        for row in classes:
            if len(g) != len(row['graph']):
                continue
            mapping = isomorphism(g, row['graph'])
            if mapping is not None:
                row['members'].append(dict(index=i, map_to_representative=mapping))
                break
        else:
            classes.append(dict(graph=g, graph6=code, representative=i,
                                members=[dict(index=i, map_to_representative=dict(zip(g,g)))]))
    franklin = classes[0]['graph']
    for row in classes:
        g = row.pop('graph')
        row['order'] = len(g)
        row['decomposition'] = decomposition(g, franklin)
        row['optimization'] = optimization_audit(g)
        print('audited', row['order'], 'vertices;', len(row['members']), 'records', flush=True)
    result = dict(source=str(SOURCE.relative_to(HERE.parent)), records=len(codes),
                  isomorphism_classes=len(classes), classes=classes,
                  original_conjecture='unresolved',
                  limitation='Retained library only; decomposition is descriptive, not a classification theorem.')
    (HERE / 'audit.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
