"""Optional full-graph cross-check; requires NetworkX and OR-Tools.

The model uses only degree constraints and the general fact that a good set
cannot contain both ends of a bridge. It does not use the cap optimum as an
upper bound. Time-limited runs are reported as incomplete, not proved optimal.
"""
import json
from pathlib import Path
import networkx as nx
from ortools.sat.python import cp_model
from verify_bridge_reduction import graph, good_sets, complete, edges

bases = [graph(1), graph(2, [(0, 1)]),
         graph(3, [(0, 1), (1, 2), (0, 2)]),
         graph(4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
         graph(4, [(0, 1), (1, 2), (0, 2), (2, 3)]),
         graph(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
         graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)])]
records = []
for h in bases:
    branch = {v for v in range(len(h)) if len(h[v]) == 3}
    selected = max(good_sets(h), key=lambda s: len(s & branch))
    g, witness = complete(h, selected)
    model = cp_model.CpModel()
    x = [model.new_bool_var(str(v)) for v in range(len(g))]
    for v in range(len(g)):
        model.add(sum(x[u] for u in g[v]) == 2).only_enforce_if(x[v])
        model.add_hint(x[v], int(v in witness))
    nxg = nx.Graph()
    nxg.add_nodes_from(range(len(g)))
    nxg.add_edges_from(edges(g))
    for u, v in nx.bridges(nxg):
        model.add(x[u]+x[v] <= 1)
    model.maximize(sum(x))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 15
    status = solver.solve(model)
    record = {'base_order': len(h), 'base_edges': edges(h),
              'completion_order': len(g), 'predicted_maximum': len(witness),
              'status': solver.status_name(status),
              'model_includes_general_bridge_constraints': True}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        record['feasible_size'] = int(solver.objective_value)
        record['upper_bound'] = solver.best_objective_bound
        if solver.objective_value > len(witness):
            raise AssertionError('completion formula contradicted')
        if status == cp_model.OPTIMAL:
            assert solver.objective_value == len(witness)
    records.append(record)
    Path(__file__).with_name('completion_solver_results.json').write_text(json.dumps(records, indent=2)+'\n')
    print(record, flush=True)
