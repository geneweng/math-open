"""Check explicit witnesses using only Python's standard library.

The verifier proves the asserted lower bounds for the listed graphs. It does
not prove that nauty generated every isomorphism class, and does not certify
the separately recorded maximum sizes as upper bounds.
"""
import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def graph6(text):
    if not text or not all(63 <= ord(c) <= 126 for c in text):
        raise ValueError('invalid graph6 characters')
    n = ord(text[0]) - 63
    if not 1 <= n <= 62 or len(text) != 1 + (n * (n - 1) // 2 + 5) // 6:
        raise ValueError('unsupported graph6 order or length')
    adj = [set() for _ in range(n)]
    bit = 0
    for v in range(1, n):
        for u in range(v):
            if (ord(text[1 + bit // 6]) - 63) & (1 << (5 - bit % 6)):
                adj[u].add(v)
                adj[v].add(u)
            bit += 1
    return adj


def connected_without(adj, forbidden=None):
    reached = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if forbidden == (min(u, v), max(u, v)):
                continue
            if u not in reached:
                reached.add(u)
                stack.append(u)
    return len(reached) == len(adj)


def has_bridge(adj):
    return any(not connected_without(adj, (u, v))
               for u in range(len(adj)) for v in adj[u] if u < v)


def good(adj, mask):
    if not isinstance(mask, int) or mask <= 0 or mask >= 1 << len(adj):
        return False
    return all(sum((mask >> u) & 1 for u in adj[v]) == 2
               for v in range(len(adj)) if (mask >> v) & 1)


def verify(data):
    counts = Counter()
    weighted_counts = Counter()
    seen = set()
    for index, record in enumerate(data['graphs']):
        def require(condition, message):
            if not condition:
                raise ValueError(f'graph {index}: {message}')
        code = record['graph6']
        require(code not in seen, 'duplicate graph6 string')
        seen.add(code)
        adj = graph6(code)
        n = len(adj)
        require(all(len(ns) == 3 for ns in adj), 'graph is not cubic')
        require(connected_without(adj), 'graph is disconnected')
        witness = record['half_witness']
        require(good(adj, witness), 'half witness is not good')
        require(2 * witness.bit_count() >= n, 'half witness is too small')
        counts[n] += 1
        bridge = has_bridge(adj)
        certificate = record.get('fractional_cover')
        require((certificate is None) == bridge, 'bridge/cover classification mismatch')
        if certificate is None:
            continue
        coverage = [Fraction(0) for _ in adj]
        total = Fraction(0)
        for entry in certificate:
            mask = entry['mask']
            coefficient = Fraction(entry['coefficient'])
            require(coefficient > 0, 'cover coefficient is not positive')
            require(good(adj, mask), 'cover contains a non-good set')
            total += coefficient
            for v in range(n):
                if (mask >> v) & 1:
                    coverage[v] += coefficient
        require(total <= 2, 'total cover coefficient exceeds two')
        require(all(c >= 1 for c in coverage), 'a vertex is not covered to weight one')
        weighted_counts[n] += 1
    result = {'verified_graphs': sum(counts.values()),
              'verified_fractional_covers': sum(weighted_counts.values()),
              'graphs_by_order': dict(sorted(counts.items())),
              'fractional_covers_by_order': dict(sorted(weighted_counts.items())),
              'general_conjecture_solved': False}
    if 'summary' in data and result != data['summary']:
        # JSON object keys are strings; normalize the generated result first.
        if json.loads(json.dumps(result)) != data['summary']:
            raise ValueError('recorded summary does not match certificates')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path,
                        default=Path(__file__).with_name('certificates.json'))
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.path.read_text())), indent=2))
