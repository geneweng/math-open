"""Audit bounded edge-coverage diagnostic from odd_factor_enumerate JSONL.

Usage: python3 diagnostic.py path/to/small_profiles.jsonl
Input should enumerate connected simple cubic graphs of orders 4..16.
Completeness relies on geng and upper bounds on cycle-space enumeration;
each negative example is independently checked by all vertex subsets.
"""
import collections
import json
from pathlib import Path
import sys
import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from verify_round12 import decode
from verify_round23 import sets

counts = collections.Counter()
failures, retained = [], []
codes = set()
for line in Path(sys.argv[1]).open():
    r = json.loads(line)
    assert r['graph6'] not in codes
    codes.add(r['graph6'])
    n = r['order']; counts['graphs'] += 1
    if r['maximum'] > n//2+1:
        continue
    counts['near_sharp'] += 1
    retained.append(r)
    g = nx.from_graph6_bytes(r['graph6'].encode())
    bridges = {tuple(sorted(e)) for e in nx.bridges(g)}
    for u, v, U, T, wu, wt in r['edge_profiles']:
        if (u, v) in bridges:
            continue
        counts['edges'] += 1
        if T < n//2:
            a, _ = decode(r['graph6']); gs = sets(a)
            b = [ns.copy() for ns in a]
            b[u].remove(v); b[v].remove(u)
            bs = sets(b)
            assert r['maximum'] == max(s.bit_count() for s in gs)
            assert T == max((s.bit_count() for s in gs if s>>u&1 and s>>v&1), default=-1)
            assert U == max(s.bit_count() for s in bs)
            W = max(s.bit_count() for s in gs if not(s>>u&1 or s>>v&1))
            failures.append(dict(graph6=r['graph6'], order=n, maximum=r['maximum'],
                                 edge=[u,v], U=U, T=T, W=W,
                                 verification='all vertex subsets'))
        else:
            chosen = {v for v in g if wt>>v&1}
            assert u in chosen and v in chosen and len(chosen) == T
            assert all(len(set(g[w]) & chosen) == 2 for w in chosen)
assert counts['graphs'] == 4681
(HERE/'edge_coverage_diagnostic.json').write_text(json.dumps(
    dict(counts=dict(counts), failures=failures,
         limitation='Bounded diagnostic, not proof of a universal tradeoff.'), indent=2)+'\n')
(HERE/'near_sharp_profiles.json').write_text(json.dumps(retained, indent=2)+'\n')
print(dict(counts), 'failed edge incidences:', len(failures))
