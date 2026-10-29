"""Check explicit witnesses used in the matching criterion.

The proof, not these finite examples, covers arbitrary bridgeless bases.
Run verify_boundary_profiles.py first to check every fragment table.
"""
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path
from verify_certificates import graph6
from verify_bridge_reduction import graph, edges, good

STATES = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2)]


def matchings(n, es):
    found = []
    for chosen in itertools.combinations(range(len(es)), n//2):
        degree = [0]*n
        for i in chosen:
            u, v = es[i]
            degree[u] += 1
            degree[v] += 1
        if degree == [1]*n:
            found.append(set(chosen))
    assert found
    assert all(Fraction(sum(i in m for m in found), len(found)) == Fraction(1, 3)
               for i in range(len(es)))
    return found


def witness(n, es, fragments, choices, matching):
    selected = set() if matching is None else set(range(n))
    enlarged_edges = []
    offset = n
    score = -n if matching is None else n
    for i, ((u, v), (pid, reverse)) in enumerate(zip(es, choices)):
        fragment = fragments[pid]
        adj = graph6(fragment['graph6'])
        a, b = fragment['ports']
        enlarged_edges.extend((offset+x, offset+y) for x, y in edges(adj)
                              if {x, y} != {a, b})
        if reverse:
            a, b = b, a
        enlarged_edges.extend([(u, offset+a), (v, offset+b)])
        values = fragment['doubled_surplus_table']
        if matching is None:
            state_index = max(range(4), key=lambda k: values[k])
        else:
            state_index = 0 if i in matching else 4
        local = fragment['maximizing_witnesses'][str(STATES[state_index])]
        selected.update(offset+x for x in local)
        score += values[state_index]
        offset += len(adj)
    result = graph(offset, enlarged_edges)
    assert all(len(ns) == 3 for ns in result)
    assert good(result, selected)
    assert score == 2*len(selected)-len(result)
    return score, len(result)


def main():
    root = Path(__file__).parent
    data = json.loads((root/'boundary_profile_checks.json').read_text())
    fragments = [r for r in data['records'] if r['doubled_surplus_table'][4] > -1000000]
    assert len(fragments) == 21
    k4 = (4, list(itertools.combinations(range(4), 2)))
    petersen_edges = [(i, (i+1) % 5) for i in range(5)]
    petersen_edges += [(i, i+5) for i in range(5)]
    petersen_edges += [(i+5, (i+2) % 5+5) for i in range(5)]
    bases = [('K4', *k4), ('Petersen', 10, petersen_edges)]
    rng = random.Random(20261104)
    records = []
    witness_count = 0
    for name, n, es in bases:
        ms = matchings(n, es)
        configurations = [[(pid, bool(i % 2)) for i in range(len(es))]
                          for pid in range(len(fragments))]
        configurations += [[(rng.randrange(len(fragments)), bool(rng.randrange(2)))
                            for _ in es] for _ in range(20)]
        for choices in configurations:
            z0, order = witness(n, es, fragments, choices, None)
            zs = [witness(n, es, fragments, choices, m)[0] for m in ms]
            local_sum = sum(3*max(fragments[pid]['doubled_surplus_table'][:4])
                            +fragments[pid]['doubled_surplus_table'][0]
                            +2*fragments[pid]['doubled_surplus_table'][4]
                            for pid, _ in choices)
            assert (z0+Fraction(sum(zs), len(zs)))/2 == Fraction(local_sum, 6)
            assert local_sum >= 0 and max([z0]+zs) >= 0
            witness_count += 1+len(ms)
            records.append({'base': name, 'expanded_order': order, 'choices': choices,
                            'closed_surplus': z0, 'matching_surpluses': zs,
                            'local_inequality_sum': local_sum})
    result = {'assemblies_checked': len(records), 'good_sets_checked': witness_count,
              'records': records, 'general_conjecture_solved': False}
    (root/'matching_criterion_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'assemblies_checked': len(records), 'good_sets_checked': witness_count,
                      'general_conjecture_solved': False}))


if __name__ == '__main__':
    main()
