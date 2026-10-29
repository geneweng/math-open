"""Exact, standard-library checks for the latest reductions and obstructions.

These are implementation checks and finite results, not a proof of the
general induced cycles conjecture. Run from any working directory.
"""
import itertools
import json
from pathlib import Path

from verify_bridge_reduction import graph, edges, good_sets, good
from verify_certificates import graph6


def delete(adj, removed, add=()):
    vertices = [v for v in range(len(adj)) if v not in removed]
    rename = {v: i for i, v in enumerate(vertices)}
    es = [e for e in edges(adj) if not (set(e) & removed)] + list(add)
    return graph(len(vertices), [(rename[u], rename[v]) for u, v in es]), vertices


def reductions():
    pruning = suppression = lifts = 0
    for n in range(1, 6):
        possible = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            h = graph(n, [e for i, e in enumerate(possible) if mask >> i & 1])
            if max(map(len, h)) > 3:
                continue
            branches = {v for v in range(n) if len(h[v]) == 3}
            beta = max(len(s & branches) for s in good_sets(h))
            for w in range(n):
                if len(h[w]) <= 1:
                    hp, vertices = delete(h, {w})
                    branchp = {v for v in range(len(hp)) if len(hp[v]) == 3}
                    bp = max(len(s & branchp) for s in good_sets(hp))
                    assert bp <= beta
                    assert len(edges(hp))-len(hp) >= len(edges(h))-n
                    pruning += 1
                if len(h[w]) != 2:
                    continue
                u, v = h[w]
                if v in h[u]:
                    continue
                hp, vertices = delete(h, {w}, [(u, v)])
                branchp = {x for x in range(len(hp)) if len(hp[x]) == 3}
                for sp in good_sets(hp):
                    s = {vertices[x] for x in sp}
                    if u in s and v in s:
                        s.add(w)
                    assert good(h, s)
                    assert len(s & branches) == len(sp & branchp)
                    lifts += 1
                assert len(edges(hp))-len(hp) == len(edges(h))-n
                suppression += 1
    return {'prunings': pruning, 'suppressions': suppression, 'suppression_lifts': lifts}


def profiles():
    checked = 0
    for line in Path(__file__).with_name('three_pole_profiles.txt').read_text().splitlines():
        fields = line.split()
        adj = graph6(fields[0])
        removed = int(fields[1])
        ports = list(map(int, fields[2:5]))
        claimed = list(map(int, fields[5:]))
        assert set(ports) == adj[removed] and len(ports) == 3
        hp, vertices = delete(adj, {removed})
        rename = {v: i for i, v in enumerate(vertices)}
        port_index = {rename[v]: j for j, v in enumerate(ports)}
        neighbours = [sum(1 << u for u in ns) for ns in hp]
        actual = [-1000] * 27
        for mask in range(1 << len(hp)):
            state = [0, 0, 0]
            remaining = mask
            valid = True
            while remaining:
                bit = remaining & -remaining
                remaining -= bit
                v = bit.bit_length()-1
                degree = (neighbours[v] & mask).bit_count()
                if v in port_index:
                    if degree not in (1, 2):
                        valid = False
                        break
                    state[port_index[v]] = 3-degree
                elif degree != 2:
                    valid = False
                    break
            if valid:
                key = state[0]+3*state[1]+9*state[2]
                actual[key] = max(actual[key], 2*mask.bit_count()-len(hp))
        assert actual == claimed, (fields[:5], actual, claimed)
        checked += 1
    return checked


def pendant_cycles():
    checks = 0
    for n in range(3, 7):
        possible = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            h = graph(n, [e for i, e in enumerate(possible) if mask >> i & 1])
            if max(map(len, h)) > 3:
                continue
            branches = {v for v in range(n) if len(h[v]) == 3}
            for cycle in good_sets(h):
                if len(cycle) < 3 or len(cycle & branches) != 1:
                    continue
                u = next(iter(cycle & branches))
                external = h[u] - cycle
                if len(external) != 1 or any(len(h[v]) != 2 for v in cycle-{u}):
                    continue
                z = next(iter(external))
                hp, vertices = delete(h, cycle)
                branchp = {v for v in range(len(hp)) if len(hp[v]) == 3}
                for sp in good_sets(hp):
                    selected = {vertices[v] for v in sp}
                    if z not in selected:
                        selected |= cycle
                    assert good(h, selected)
                    assert len(selected & branches) == len(sp & branchp)+1
                    checks += 1
    return checks


def cover_obstructions():
    # A three-connected graph whose vertices cannot be covered by two good sets.
    code = 'ICOedO[X?'
    adj = graph6(code)
    sets = [sum(1 << v for v in s) for s in good_sets(adj)]
    full = (1 << len(adj))-1
    assert not any(s | t == full for s in sets for t in sets)
    for removed in itertools.combinations(range(len(adj)), 2):
        remaining = set(range(len(adj))) - set(removed)
        reached = {next(iter(remaining))}
        stack = list(reached)
        while stack:
            for u in adj[stack.pop()] & remaining:
                if u not in reached:
                    reached.add(u)
                    stack.append(u)
        assert reached == remaining
    two_cover = {'graph6': code, 'three_connected': True,
                 'maximum_good_set': max(s.bit_count() for s in sets),
                 'two_good_sets_cover_all_vertices': False}

    # Four good sets may cover each vertex twice, but the extra edge cap fails.
    code = 'O??CA?oBCDT?U?D_CgAA_'
    adj = graph6(code)
    sets = [sum(1 << v for v in s) for s in good_sets(adj)]
    full = (1 << len(adj))-1
    edge_masks = [(1 << u) | (1 << v) for u, v in edges(adj)]
    count = covering = 0
    smallest_maximum_edge_use = 4
    witness = None
    for choice in itertools.combinations_with_replacement(sets, 4):
        count += 1
        covered_twice = 0
        for i, j in itertools.combinations(range(4), 2):
            covered_twice |= choice[i] & choice[j]
        if covered_twice != full:
            continue
        covering += 1
        maximum = max(sum(s & edge == edge for s in choice) for edge in edge_masks)
        assert maximum > 2
        if maximum < smallest_maximum_edge_use:
            smallest_maximum_edge_use = maximum
            witness = choice
    assert covering > 0 and smallest_maximum_edge_use == 3
    four_cover = {'graph6': code, 'good_sets_including_empty': len(sets),
                  'four_multisets_checked': count, 'covering_multisets': covering,
                  'minimum_maximum_edge_multiplicity': smallest_maximum_edge_use,
                  'four_cover_witness_masks': witness,
                  'maximum_good_set': max(s.bit_count() for s in sets)}
    return two_cover, four_cover


def main():
    two, four = cover_obstructions()
    result = {'reductions': reductions(), 'pendant_cycle_extensions': pendant_cycles(),
              'independently_verified_profiles': profiles(),
              'two_cover_obstruction': two, 'edge_capped_four_cover_obstruction': four,
              'general_conjecture_solved': False}
    Path(__file__).with_name('further_reduction_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
