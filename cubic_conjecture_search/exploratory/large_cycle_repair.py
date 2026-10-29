"""Search for a single repair cycle with CP-SAT; verify every witness directly.

The circuit constraint requires one simple cycle. An orientation with
out-degree at most one enforces the pseudoforest condition. Timeouts are
reported as UNKNOWN, not as impossibility certificates.
"""
import json
from pathlib import Path
import sys
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify_round11 import family, bitmask, graph6
from verify_bridge_reduction import graph, edges
from verify_pseudoforest_repair import statistics


def repair(n, es, initial, seconds=30):
    initial_stats = statistics(n, es, initial)
    assert initial_stats['pseudoforest'] and initial_stats['isolated'] > 0
    model = cp_model.CpModel()
    leaves = [model.new_bool_var(f'l{v}') for v in range(n)]
    degree, outgoing = [[] for _ in range(n)], [[] for _ in range(n)]
    circuit = [(v, v, model.new_bool_var(f'self{v}')) for v in range(n)]
    factors, defects = [], []
    for i, (u, v) in enumerate(es):
        a, b = model.new_bool_var(f'a{i}'), model.new_bool_var(f'b{i}')
        circuit += [(u, v, a), (v, u, b)]
        model.add(a+b <= 1)
        f = model.new_bool_var(f'f{i}')
        model.add(f == (1-a-b if initial >> i & 1 else a+b))
        degree[u].append(f); degree[v].append(f)
        ou, ov = model.new_bool_var(f'ou{i}'), model.new_bool_var(f'ov{i}')
        model.add(ou+ov == f)
        outgoing[u].append(ou); outgoing[v].append(ov)
        j = model.new_bool_var(f'j{i}')
        for z in (f, leaves[u], leaves[v]):
            model.add(j <= z)
        model.add(j >= f+leaves[u]+leaves[v]-2)
        factors.append(f); defects.append(j)
    model.add_circuit(circuit)
    for v in range(n):
        model.add(sum(degree[v]) == 3-2*leaves[v])
        model.add(sum(outgoing[v]) <= 1)
    model.add(sum(defects) < initial_stats['isolated'])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 2026102711
    status = solver.solve(model)
    result = dict(status=solver.status_name(status), seconds=solver.wall_time,
                  order=n, initial_j=initial_stats['isolated'])
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        final = sum(1 << i for i, f in enumerate(factors) if solver.value(f))
        s = statistics(n, es, final)
        assert s['pseudoforest'] and s['isolated'] < initial_stats['isolated']
        changed = graph(n, [e for i, e in enumerate(es) if (final ^ initial) >> i & 1])
        vertices = {v for v in range(n) if changed[v]}
        assert vertices and all(len(changed[v]) == 2 for v in vertices)
        seen = {min(vertices)}; todo = list(seen)
        while todo:
            for u in changed[todo.pop()] - seen:
                seen.add(u); todo.append(u)
        assert seen == vertices
        result.update(final_factor=final, final_j=s['isolated'], cycle_length=len(vertices),
                      final_statistics=s)
    return result


def main():
    records = []
    for k in range(3, 7):
        a, es, initial, cores, offsets = family(k)
        if k == 3:
            r = repair(len(a), es, initial)
            assert r['status'] == 'INFEASIBLE'
            records.append(dict(kind='bridge_family', k=k, **r))
            print(json.dumps(records[-1]), flush=True)
        n = len(a)
        lifted = [(2*u+s, 2*v+1-s) for u, v in es for s in (0, 1)]
        h = graph(2*n, lifted)
        he = sorted(edges(h))
        selected = [tuple(sorted((2*u+s, 2*v+1-s)))
                    for i, (u, v) in enumerate(es) if initial >> i & 1 for s in (0, 1)]
        hf = bitmask(he, selected)
        r = repair(2*n, he, hf)
        records.append(dict(kind='bipartite_double_cover', k=k, graph6=graph6(h),
                            edges=he, initial_factor=hf, **r))
        print(json.dumps({key: value for key, value in records[-1].items()
                          if key not in ('edges', 'graph6', 'final_statistics')}), flush=True)
    (ROOT/'round11_data/large_cycle_search.json').write_text(json.dumps(records, indent=2)+'\n')


if __name__ == '__main__':
    main()
