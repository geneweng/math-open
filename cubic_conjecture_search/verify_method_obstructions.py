"""Exact obstructions to stronger proof strategies, not to the main conjecture."""
import json
from pathlib import Path
from verify_certificates import graph6, good, has_bridge


def masks(code):
    adj = graph6(code)
    assert all(len(ns) == 3 for ns in adj) and not has_bridge(adj)
    return adj, [s for s in range(1, 1 << len(adj)) if good(adj, s)]


records = []
adj, sets = masks('GCZJd_')
weights = [0, 1, 1, 0, 0, 1, 0, 2]
weight = lambda s: sum(w for v, w in enumerate(weights) if (s >> v) & 1)
restricted = [s for s in sets if (s & 1) == ((s >> 3) & 1)]
assert sum(weights) == 5 and max(map(weight, restricted)) == 2
assert max(map(weight, sets)) >= 3
records.append({'graph6': 'GCZJd_', 'restriction': 'endpoints 0 and 3 selected together or avoided together',
                'weights': weights, 'total_weight': 5, 'restricted_maximum_weight': 2,
                'unrestricted_maximum_weight': max(map(weight, sets)),
                'unweighted_maximum': max(s.bit_count() for s in sets)})

adj, sets = masks('K?`CRAWK`gGg')
assert max(s.bit_count() for s in sets if (s >> 2) & 1 and (s >> 9) & 1) == 4
assert max(s.bit_count() for s in sets) >= 6
records.append({'graph6': 'K?`CRAWK`gGg', 'required_edge': [2, 9],
                'restricted_maximum': 4, 'unrestricted_maximum': max(s.bit_count() for s in sets)})

adj, sets = masks('M???FBOq@KF?D_B_?')
assert max(s.bit_count() for s in sets if (s >> 11) & 1) == 6
assert max(s.bit_count() for s in sets) == 8
records.append({'graph6': 'M???FBOq@KF?D_B_?', 'required_vertex': 11,
                'restricted_maximum': 6, 'unrestricted_maximum': 8})

result = {'original_conjecture_disproved': False, 'verified_method_obstructions': records}
Path(__file__).with_name('method_obstruction_results.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
