#!/usr/bin/env python3
"""Check all retained witnesses and exhaust the ten fixed-factor traps."""
import json
from pathlib import Path
from verify_pseudoforest_repair import decode, cycles_of, statistics

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'round8_data'


def connected(adj, excluded):
    left = set(range(len(adj))) - set(excluded)
    todo = [next(iter(left))]; left.remove(todo[0])
    while todo:
        for u in adj[todo.pop()] & left:
            left.remove(u); todo.append(u)
    return not left


def main():
    rows = [json.loads(line) for line in
            (DATA / 'bipartite_switch_probes.jsonl').read_text().splitlines()]
    inputs = {c: int(m) for c, m in (line.split() for line in
              (DATA / 'bipartite_switch_inputs.txt').read_text().splitlines())}
    assert len(inputs) == len(rows) == 7616
    out = dict(inputs=len(rows), improving_witnesses_checked=0,
               traps_exhausted=0, trap_cycles_checked=0,
               traps_with_verified_vertex_connectivity_two=0)
    for r in rows:
        assert inputs.pop(r['graph6']) == r['factor']
        n, edges, adj = decode(r['graph6']); factor = r['factor']
        assert n == 36 and connected(adj, ())
        assert all(u < 18 <= v for u, v in edges)
        initial = statistics(n, edges, factor)
        assert initial['pseudoforest'] and initial['isolated'] == 1
        if r['best_cycle']:
            c = r['best_cycle']; ca = [set() for _ in range(n)]
            for i, (u, v) in enumerate(edges):
                if c >> i & 1:
                    ca[u].add(v); ca[v].add(u)
            active = {v for v in range(n) if ca[v]}
            assert active and all(len(ca[v]) == 2 for v in active)
            seen = {next(iter(active))}; todo = list(seen)
            while todo:
                for u in ca[todo.pop()] - seen:
                    seen.add(u); todo.append(u)
            assert seen == active
            after = statistics(n, edges, factor ^ c)
            assert after['pseudoforest'] and after['isolated'] == 0
            out['improving_witnesses_checked'] += 1
        else:
            assert r['all_cycles_exhausted']
            cycles = cycles_of(n, edges, adj)
            assert len(cycles) == r['cycles']
            for c in cycles:
                after = statistics(n, edges, factor ^ c)
                assert not after['pseudoforest'] or after['isolated'] >= 1
            assert all(connected(adj, [v]) for v in range(n))
            assert any(not connected(adj, [u, v]) for v in range(n) for u in range(v))
            out['traps_exhausted'] += 1
            out['trap_cycles_checked'] += len(cycles)
            out['traps_with_verified_vertex_connectivity_two'] += 1
    assert not inputs and out['traps_exhausted'] == 10
    (ROOT / 'round8_switch_verification.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
