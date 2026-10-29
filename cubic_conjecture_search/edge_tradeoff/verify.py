"""Direct verification of the targeted edge-profile exclusions.

No optimization solver is used. Positive sets alone certify the claimed
exclusions; the six local path capacities are checked by all subsets.
"""
import collections
import gzip
import itertools
import json
from pathlib import Path
import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
codes = (ROOT/'round30_data/extension_parents.g6').read_text().split()


def good(g, mask):
    assert mask >> len(g) == 0
    return all(sum(mask >> u & 1 for u in g[v]) == 2
               for v in g if mask >> v & 1)


def switches(base):
    result = set()
    for e, f in itertools.combinations(base.edges(), 2):
        if len(set(e+f)) != 4:
            continue
        for add in [[(e[0],f[0]),(e[1],f[1])],[(e[0],f[1]),(e[1],f[0])]]:
            if any(base.has_edge(*a) for a in add):
                continue
            g = base.copy(); g.remove_edges_from([e,f]); g.add_edges_from(add)
            if nx.is_connected(g):
                result.add(nx.to_graph6_bytes(g,header=False).decode().strip())
    return result


def main():
    base = nx.from_graph6_bytes(codes[1].encode())
    expected = switches(base)
    supplied = json.loads((HERE/'one_switch_inputs.json').read_text())
    assert expected == set(supplied)
    seen = set(); edge_count = 0; bridge_count = 0
    with gzip.open(HERE/'one_switch_certificates.jsonl.gz','rt') as file:
        for line in file:
            row = json.loads(line); code = row['graph6']
            assert code in expected and code not in seen
            seen.add(code); g = nx.from_graph6_bytes(code.encode())
            assert len(g) == 24 and all(d == 3 for _,d in g.degree())
            assert {tuple(x[:2]) for x in row['edge_profiles']} == {
                tuple(sorted(e)) for e in g.edges()}
            for u,v,U,T,wu,wt in row['edge_profiles']:
                minus = g.copy(); minus.remove_edge(u,v)
                assert good(minus,wu) and wu.bit_count() == U
                assert U >= 12
                if T >= 0:
                    assert good(g,wt) and wt.bit_count() == T
                    assert wt>>u&1 and wt>>v&1
                assert U >= 14 or T >= 12
                # Subdivision: max(2U, U+T+1) >= 25.
                assert max(2*U,U+T+1) >= 25
                # Root triangle: B=max(U,T+2) >= 14, so 2B>=28>27.
                assert max(U,T+2) >= 14
                edge_count += 1
            bridge_count += len(list(nx.bridges(g)))
    assert seen == expected

    # Split the retained 26-vertex double into its 13-vertex cap.
    double = nx.from_graph6_bytes(codes[2].encode())
    bridge = list(nx.bridges(double))[0]
    double.remove_edge(*bridge)
    vertices = min(nx.connected_components(double), key=min)
    cap = double.subgraph(vertices).copy()
    root = next(v for v in cap if cap.degree(v) == 2)
    assert set(cap) == set(range(13))
    paths = []
    for e in sorted(cap.edges()):
        q = cap.copy(); q.remove_edge(*e)
        q.add_edges_from([(e[0],13),(e[1],13)])
        free = [v for v in q if v not in (root,13)]
        best = -1; witness = None
        for bits in range(1<<len(free)):
            s = {root,13} | {v for i,v in enumerate(free) if bits>>i&1}
            if all(len(set(q[v]) & s) == (1 if v in (root,13) else 2) for v in s):
                if len(s)>best:
                    best=len(s); witness=sorted(s)
        assert best >= 8
        paths.append(dict(edge=list(e),capacity=best,witness=witness))
    (HERE/'cap_path_certificates.json').write_text(json.dumps(
        dict(root=root, cap_edges=sorted(sorted(e) for e in cap.edges()),
             records=paths, subsets_per_edge=4096),indent=2)+'\n')

    bypasses = json.loads((HERE/'bridge_bypasses.json').read_text())
    capacities = {tuple(r['edge']):r['capacity'] for r in paths}
    # Directly check every saved positive certificate, including U>=14.
    for row in bypasses:
        g = nx.from_graph6_bytes(row['graph6'].encode()); u,v = row['edge']
        for key in ('U','T','W'):
            s = row[key]['witness']; mask = sum(1<<a for a in s)
            q = g.copy()
            if key == 'U': q.remove_edge(u,v)
            if key == 'T': assert u in s and v in s
            if key == 'W': assert u not in s and v not in s
            assert good(q,mask) and len(s) == row[key]['value']
        assert row['T']['value'] >= 16 and row['U']['value'] >= 14
        assert max(2*row['U']['value'],row['U']['value']+row['T']['value']+1) >= 29
        assert 2*max(row['U']['value'],row['T']['value']+2) >= 31
    result = dict(one_switch_graphs=len(seen), checked_parent_edges=edge_count,
                  bridge_edges=bridge_count, nonbridge_edges=edge_count-bridge_count,
                  both_rooted_forms_excluded=True,
                  cap_edges_enumerated=len(paths), local_subsets_checked=4096*len(paths),
                  cap_path_capacity_histogram=dict(collections.Counter(r['capacity'] for r in paths)),
                  bypass_representatives_checked=len(bypasses),
                  original_conjecture='unresolved')
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
