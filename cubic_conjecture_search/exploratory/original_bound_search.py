"""Search the original induced-cycle half bound around certified tight graphs.

The two queries ask for >=n/2+1 and >=n/2 vertices. UNKNOWN never means
infeasible. Every positive certificate is checked directly before saving.
"""
import argparse
import json
from pathlib import Path
import random
import sys
import time

import networkx as nx
from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify_round11 import family
from verify_bridge_reduction import franklin, edges


def witness(g, target, limit, hint=None):
    n = len(g)
    model = cp_model.CpModel()
    x = [model.new_bool_var(f'x{v}') for v in range(n)]
    for v in range(n):
        model.add(sum(x[u] for u in g[v]) == 2).only_enforce_if(x[v])
    model.add(sum(x) >= target)
    if hint is not None:
        chosen = set(hint)
        for v in range(n):
            model.add_hint(x[v], int(v in chosen))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 2026102712
    solver.parameters.max_time_in_seconds = limit
    st = solver.solve(model)
    result = dict(target=target, status=solver.status_name(st), seconds=solver.wall_time)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [v for v in range(n) if solver.value(x[v])]
        assert len(chosen) >= target
        selected = set(chosen)
        assert all(len(set(g[v]) & selected) == 2 for v in selected)
        result['witness'] = chosen
    return result


def ring(k):
    f = franklin()
    g = nx.Graph()
    g.add_nodes_from(range(12*k))
    for i in range(k):
        g.add_edges_from((12*i+u, 12*i+v) for u, v in edges(f) if (u, v) != (2, 4))
        g.add_edge(12*i+4, 12*((i+1) % k)+2)
    return g


def switched(g, rng, count):
    h = g.copy()
    changes = []
    bridges = set(tuple(sorted(e)) for e in nx.bridges(h))
    for _ in range(count):
        for attempt in range(100):
            e, f = rng.sample(list(h.edges), 2)
            a, b = e; c, d = f
            if rng.randrange(2):
                c, d = d, c
            if len({a,b,c,d}) < 4 or h.has_edge(a,c) or h.has_edge(b,d):
                continue
            # Avoid merely permuting two cap attachment bridges.
            if tuple(sorted(e)) in bridges and tuple(sorted(f)) in bridges:
                continue
            h.remove_edges_from([e, f]); h.add_edges_from([(a,c), (b,d)])
            if nx.is_connected(h):
                changes.append(dict(removed=[list(e), list(f)], added=[[a,c],[b,d]]))
                break
            h.remove_edges_from([(a,c),(b,d)]);h.add_edges_from([e,f])
    return h, changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases-per-seed', type=int, default=200)
    parser.add_argument('--seconds', type=float, default=.5)
    args = parser.parse_args()
    rng = random.Random(2026102712)
    seeds = []
    for k in (3,4,5):
        a, es, _, _, _ = family(k)
        g = nx.Graph();g.add_nodes_from(range(len(a)));g.add_edges_from(es)
        seeds.append((f'bridge_{k}', g))
    for k in (3,4,5,6,8):
        seeds.append((f'ring_{k}', ring(k)))
    output = ROOT/'round12_data/original_candidates.jsonl'
    seen = set()
    start = time.monotonic()
    totals = dict(candidates=0, strict_witnesses=0, tight_certified=0,
                  half_witness_only=0, unresolved=0, counterexample_candidates=0)
    with output.open('w') as stream:
        for label, seed in seeds:
            g = seed.copy(); n = len(g); hint = None
            accepted = 0
            for trial in range(args.cases_per_seed):
                if trial % 40 == 0:
                    g = seed.copy(); hint = None
                h, changes = switched(g, rng, 1 if rng.random()<.7 else 2)
                if not changes:
                    continue
                code = nx.to_graph6_bytes(h, header=False).decode().strip()
                if code in seen:
                    continue
                seen.add(code)
                assert nx.is_connected(h) and all(d == 3 for _,d in h.degree())
                q = witness(h, n//2+1, args.seconds, hint)
                half = q if 'witness' in q else witness(h, n//2, args.seconds, hint)
                row = dict(seed=label, trial=trial, order=n, graph6=code,
                           mutations=changes, strict_query=q)
                if half is not q:
                    row['half_query'] = half
                if 'witness' in q:
                    totals['strict_witnesses'] += 1
                    if rng.random()<.02:
                        g = h; hint = q['witness']; accepted += 1
                elif 'witness' in half:
                    hint = half['witness']
                    if q['status'] == 'INFEASIBLE':
                        totals['tight_certified'] += 1
                        g = h; accepted += 1
                    else:
                        totals['half_witness_only'] += 1
                elif half['status'] == 'INFEASIBLE':
                    totals['counterexample_candidates'] += 1
                    row['requires_independent_counterexample_verification'] = True
                else:
                    totals['unresolved'] += 1
                totals['candidates'] += 1
                stream.write(json.dumps(row)+'\n'); stream.flush()
                if totals['counterexample_candidates']:
                    print('COUNTEREXAMPLE CANDIDATE', label, trial, flush=True)
                    break
                if (trial+1)%40 == 0:
                    print(json.dumps(dict(seed=label, trial=trial+1, accepted=accepted,
                                          elapsed=round(time.monotonic()-start,1), **totals)), flush=True)
            if totals['counterexample_candidates']:
                break
    totals.update(seed=2026102712, seconds_per_query=args.seconds,
                  cases_per_seed=args.cases_per_seed, elapsed_seconds=time.monotonic()-start,
                  general_conjecture_resolved=False)
    (ROOT/'round12_data/original_search_summary.json').write_text(json.dumps(totals,indent=2)+'\n')
    print(json.dumps(totals,indent=2), flush=True)


if __name__ == '__main__':
    main()
