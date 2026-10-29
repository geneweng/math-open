"""Check the cycle-space oracle against direct vertex-subset enumeration.

Only Python's standard library is used. Every size coefficient and every
single-edge-deletion/edge-containing optimum is checked on the retained
connected cubic graphs through order 12. Larger output witnesses are checked
directly; their upper bounds rely on exhaustive cycle-space enumeration.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def decode(code):
    n = ord(code[0])-63
    adj = [0]*n
    edges = []
    bit = 0
    for v in range(1, n):
        for u in range(v):
            if (ord(code[1+bit//6])-63) & (1 << (5-bit % 6)):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                edges.append((u, v))
            bit += 1
    assert all(a.bit_count() == 3 for a in adj)
    return adj, edges


def good(adj, mask):
    return all((a & mask).bit_count() == 2
               for v, a in enumerate(adj) if mask >> v & 1)


def check_witnesses(record):
    adj, edges = decode(record['graph6'])
    n = len(adj)
    assert n == record['order']
    assert record['factors_checked'] == 2**(n//2+1)
    assert good(adj, record['witness'])
    assert record['witness'].bit_count() == record['maximum']
    assert record['maximum'] == max(i for i, c in enumerate(record['histogram']) if c)
    assert len(record['edge_profiles']) == len(edges)
    for (u, v), row in zip(edges, record['edge_profiles']):
        a, b, deleted, through, wd, wt = row
        assert (a, b) == (u, v)
        reduced = adj[:]
        reduced[u] ^= 1 << v
        reduced[v] ^= 1 << u
        assert good(reduced, wd) and wd.bit_count() == deleted
        if through >= 0:
            assert good(adj, wt) and wt.bit_count() == through
            assert wt >> u & 1 and wt >> v & 1
    return adj, edges


def direct_check(record):
    adj, edges = check_witnesses(record)
    n = len(adj)
    histogram = [0]*(n+1)
    through = [-1]*len(edges)
    deleted = [0]*len(edges)
    # Independent subsets, with no cycle-space or odd-factor construction.
    for mask in range(1 << n):
        size = mask.bit_count()
        if good(adj, mask):
            histogram[size] += 1
            for e, (u, v) in enumerate(edges):
                if mask >> u & 1 and mask >> v & 1:
                    through[e] = max(through[e], size)
        for e, (u, v) in enumerate(edges):
            if size <= deleted[e]:
                continue
            if all(((adj[w] & mask).bit_count()
                    - int(w == u and mask >> v & 1)
                    - int(w == v and mask >> u & 1)) == 2
                   for w in range(n) if mask >> w & 1):
                deleted[e] = size
    assert histogram == record['histogram']
    assert deleted == [row[2] for row in record['edge_profiles']]
    assert through == [row[3] for row in record['edge_profiles']]


def main():
    small = [json.loads(line) for line in
             (ROOT/'round7_data/small_histograms.jsonl').read_text().splitlines()]
    assert len(small) == 112
    for record in small:
        direct_check(record)
    larger_file = ROOT/'round7_data/larger_profiles.jsonl'
    larger = ([json.loads(line) for line in larger_file.read_text().splitlines()]
              if larger_file.exists() else [])
    if larger:
        expected = (ROOT/'round7_data/larger_instances.g6').read_text().splitlines()
        assert [r['graph6'] for r in larger] == expected
        assert len(expected) == 240 and len(set(expected)) == 240
    for record in larger:
        check_witnesses(record)
    result = {
        'direct_subset_graphs': len(small),
        'direct_subset_assignments': sum(2**r['order'] for r in small),
        'direct_edge_profiles': sum(len(r['edge_profiles']) for r in small),
        'larger_graphs_with_verified_witnesses': len(larger),
        'larger_factors_checked': sum(r['factors_checked'] for r in larger),
        'larger_edge_profiles': sum(len(r['edge_profiles']) for r in larger),
        'larger_upper_bound_method': 'exhaustive cycle-space enumeration',
        'general_conjecture_resolved': False,
    }
    (ROOT/'round7_verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
