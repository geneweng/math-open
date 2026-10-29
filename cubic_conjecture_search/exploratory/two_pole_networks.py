"""Heuristic assembly search, with exact boundary tables and solver bounds."""
import itertools
import json
import random
import sys
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model
sys.path.insert(0, 'cubic_conjecture_search')
from verify_edge_inflation import loop_tree

OUT = Path('tmp/cubic_round4')
rng = random.Random(20261103)
states = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2)]
profiles = []
for line in (OUT/'two_pole_profiles.txt').read_text().splitlines():
    t = line.split()
    profiles.append({'graph6': t[0], 'ports': list(map(int, t[1:3])),
                     'values': list(map(int, t[3:]))})
zero = next(i for i, p in enumerate(profiles) if p['values'] == [0, 0, 0, -1000000, 0])


def solve(n, es, choices):
    m = cp_model.CpModel()
    incident = [[] for _ in range(n)]
    objective = []
    for i, ((u, v), (pid, reverse)) in enumerate(zip(es, choices)):
        p = profiles[pid]
        rows = [[*(s[::-1] if reverse else s), z] for s, z in zip(states, p['values']) if z > -1000000]
        a, b = [m.new_int_var(0, 2, f'p{i}_{j}') for j in range(2)]
        w = m.new_int_var(min(r[-1] for r in rows), max(r[-1] for r in rows), f'w{i}')
        m.add_allowed_assignments([a, b, w], rows)
        incident[u].append(a)
        incident[v].append(b)
        objective.append(w)
    vertex_rows = [[0, *s] for s in itertools.product((0, 1), repeat=3)]
    vertex_rows += [[1, *s] for s in set(itertools.permutations((0, 2, 2))) ]
    for v in range(n):
        assert len(incident[v]) == 3
        x = m.new_bool_var(f'x{v}')
        m.add_allowed_assignments([x, *incident[v]], vertex_rows)
        objective.append(2*x-1)
    m.maximize(sum(objective))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = .5
    status = solver.solve(m)
    return solver.objective_value, solver.best_objective_bound, solver.status_name(status)


records = []
best = 100
bases = [('parallel', 2, [(0, 1)]*3)]
bases += [(f'loop_tree_{t}', *loop_tree(t)) for t in (0, 1, 2, 4, 8, 16)]
bases += [(f'random_{n}', n, list(nx.random_regular_graph(3, n, seed=20261103+n).edges)) for n in (4, 6, 10, 16, 24)]
for name, n, es in bases:
    current = [(zero, False)]*len(es)
    value = 100
    for trial in range(1000):
        if trial % 200 == 0:
            choices = [(zero, False)]*len(es)
        else:
            choices = current.copy()
            for _ in range(1 if rng.random() < .8 else 2):
                choices[rng.randrange(len(es))] = (rng.randrange(len(profiles)), bool(rng.randrange(2)))
        val, ub, status = solve(n, es, choices)
        if status not in ('OPTIMAL', 'FEASIBLE'):
            records.append({'base': name, 'trial': trial, 'status': status, 'upper_bound': ub})
            continue
        if val < best:
            best = val
            print('new minimum', name, trial, val, ub, status, flush=True)
        if ub < 0:
            record = {'base_order': n, 'base_edges': es, 'choices': choices, 'profiles': profiles,
                      'value': val, 'upper_bound': ub, 'status': status}
            (OUT/'two_pole_counterexample.json').write_text(json.dumps(record, indent=2))
            raise RuntimeError('candidate counterexample requires independent verification')
        if trial % 200 == 0 or (status == 'OPTIMAL' and val <= value) or rng.random() < .01:
            current, value = choices, val
        records.append({'base': name, 'trial': trial, 'value': val, 'upper_bound': ub, 'status': status})
        if trial % 200 == 199:
            print('progress', name, trial+1, 'minimum', best, flush=True)
            (OUT/'two_pole_network_results.json').write_text(json.dumps({'complete': False, 'records': records}))
(OUT/'two_pole_network_results.json').write_text(json.dumps({'complete': True, 'records': records}))
