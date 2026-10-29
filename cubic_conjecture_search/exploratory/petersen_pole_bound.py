"""Constructive bound from vertex-disjoint induced Petersen four-poles.
No claim of resolution of the unrestricted induced-cycle conjecture.
"""
import itertools
import json
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]

def pole():
    w = nx.petersen_graph()
    w.remove_nodes_from([0, 1])
    return w

def local_cycles():
    w = pole(); ports = {v for v in w if w.degree(v) == 2}
    result = {}
    for k in range(5, 9):
        for s in itertools.combinations(w, k):
            if all(sum(u in s for u in w[v]) == 2 for v in s):
                result[frozenset(set(s) & ports)] = list(s)
    assert set(result) == {frozenset(s) for s in itertools.combinations(ports, 2)}
    return result

def construct(g, blocks):
    # blocks map the canonical pole vertices to graph vertices.
    table = local_cycles(); ports = {2, 4, 5, 6}
    used = set(); incidence = {}
    for i, block in enumerate(blocks):
        vertices = set(block.values()); assert not used & vertices; used |= vertices
        assert len(vertices) == 8
        for u in pole():
            assert set(g[block[u]]) & vertices == {block[v] for v in pole()[u]}
        for p in ports:
            outside = set(g[block[p]]) - vertices
            assert len(outside) == 1
            edge = tuple(sorted((block[p], outside.pop())))
            incidence[i, p] = edge
    # Two demand slots for each block; each external edge has capacity one.
    bip = nx.Graph(); left = []
    for i in range(len(blocks)):
        for j in range(2):
            slot = ('slot', i, j); left.append(slot)
            for p in ports:
                bip.add_edge(slot, ('edge',) + incidence[i, p])
    match = nx.algorithms.bipartite.maximum_matching(bip, top_nodes=left)
    assert all(slot in match for slot in left)
    chosen = set()
    for i, block in enumerate(blocks):
        assigned = {match['slot', i, j][1:] for j in range(2)}
        pair = frozenset(p for p in ports if incidence[i, p] in assigned)
        chosen.update(block[v] for v in table[pair])
    assert all(sum(u in chosen for u in g[v]) == 2 for v in chosen)
    assert len(chosen) >= 5 * len(blocks)
    return sorted(chosen)

def find_blocks(g):
    gm = nx.algorithms.isomorphism.GraphMatcher(g, pole())
    seen = set(); candidates = []
    for mapping in gm.subgraph_isomorphisms_iter():
        key = frozenset(mapping)
        if key not in seen:
            seen.add(key); candidates.append({v:u for u,v in mapping.items()})
    m = cp_model.CpModel(); x = [m.new_bool_var(str(i)) for i in range(len(candidates))]
    for v in g:
        m.add(sum(x[i] for i,b in enumerate(candidates) if v in b.values()) <= 1)
    m.maximize(sum(x)); solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 30
    status = solver.solve(m)
    assert status in (cp_model.FEASIBLE, cp_model.OPTIMAL)
    return [b for i,b in enumerate(candidates) if solver.value(x[i])]

def main():
    results = []
    for gid in [57244, 57278]:
        d = json.loads(Path(f'/tmp/hog{gid}.json').read_text()); a = d['adjacencyList']
        g = nx.Graph();g.add_nodes_from(range(len(a)))
        g.add_edges_from((v,u) for v,ns in enumerate(a) for u in ns)
        assert nx.is_connected(g) and all(d==3 for _,d in g.degree()) and nx.number_of_selfloops(g)==0
        blocks = find_blocks(g); selected = construct(g, blocks)
        r = dict(id=gid,source=f'https://houseofgraphs.org/api/graphs/{gid}',
                 adjacency=a, blocks=blocks, witness=selected, order=len(g),
                 guaranteed_size=5*len(blocks), actual_size=len(selected))
        results.append(r)
        print(gid,len(g),len(blocks),len(selected),flush=True)
    (ROOT/'round19_data/petersen_examples.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__ == '__main__': main()
