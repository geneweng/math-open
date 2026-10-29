"""Search for a cubic counterexample with a fixed near-half good set.

This is a bounded, incomplete search. An UNSAT result concerns only the
specified planted cycle partition and complement, not the conjecture.
The exact good-set oracle checks every candidate on at most 26 vertices.
"""
import argparse
import itertools
import json
import random
import subprocess
import time
from pathlib import Path
import networkx as nx
import z3


def complement(t, rng):
    while True:
        h = nx.from_prufer_sequence([rng.randrange(t) for _ in range(t-2)])
        if max(dict(h.degree()).values()) > 3:
            continue
        for _ in range(2):
            possible = [(u, v) for u, v in itertools.combinations(range(t), 2)
                        if not h.has_edge(u, v) and h.degree(u) < 3 and h.degree(v) < 3]
            if not possible:
                break
            h.add_edge(*rng.choice(possible))
        if h.number_of_edges() == t+1:
            return h


def template_complement(t, rng, theta, barbell):
    if theta:
        assert len(theta) == 3 and sum(theta)-1 == t and min(theta) >= 1
        assert theta.count(1) <= 1
        h = nx.Graph()
        h.add_nodes_from(range(t))
        next_vertex = 2
        for length in theta:
            path = [0]+list(range(next_vertex, next_vertex+length-1))+[1]
            h.add_edges_from(zip(path, path[1:]))
            next_vertex += length-1
        assert next_vertex == t
        return h
    if barbell:
        assert len(barbell) == 2 and sum(barbell) == t and min(barbell) >= 3
        h = nx.Graph()
        h.add_nodes_from(range(t))
        start = 0
        for length in barbell:
            h.add_edges_from((start+i, start+(i+1) % length) for i in range(length))
            start += length
        h.add_edge(0, barbell[0])
        return h
    return complement(t, rng)


def search(cycles, seed, seconds, oracle, out, theta=None, barbell=None):
    s = sum(cycles)
    t = s+2
    n = s+t
    assert n <= 26 and min(cycles) >= 3
    rng = random.Random(seed)
    h = template_complement(t, rng, theta, barbell)
    fixed = nx.Graph()
    fixed.add_nodes_from(range(n))
    offset = 0
    for length in cycles:
        fixed.add_edges_from((offset+i, offset+(i+1) % length) for i in range(length))
        offset += length
    fixed.add_edges_from((s+u, s+v) for u, v in h.edges)
    variables = {(u, v): z3.Bool(f'e{u}_{v}') for u in range(s)
                 for v in range(s, n) if fixed.degree(v) < 3}
    solver = z3.SolverFor('QF_FD')
    solver.set(timeout=15000, random_seed=seed)
    for u in range(s):
        solver.add(z3.PbEq([(x, 1) for (a, b), x in variables.items() if a == u], 1))
    for v in range(s, n):
        vs = [(x, 1) for (a, b), x in variables.items() if b == v]
        if vs:
            solver.add(z3.PbEq(vs, 3-fixed.degree(v)))
    # Rotation of the single planted cycle makes this symmetry choice lossless.
    if len(cycles) == 1:
        first = min(v for _, v in variables)
        solver.add(variables[0, first])
    cuts = set()
    records = []
    best = n
    start = time.monotonic()
    destination = out/('case_'+str(seed)+'_'+'_'.join(map(str, cycles)))
    destination.mkdir(parents=True, exist_ok=True)
    metadata = {'cycles': cycles, 'seed': seed, 'fixed_complement_edges': sorted(h.edges),
                'order': n, 'target': n//2, 'complete_for_fixed_template': False,
                'general_conjecture_solved': False, 'records': records}

    def save():
        metadata['forbidden_good_sets'] = sorted(cuts)
        (destination/'results.json').write_text(json.dumps(metadata, indent=2)+'\n')

    while time.monotonic()-start < seconds:
        status = solver.check()
        if status != z3.sat:
            metadata['termination'] = str(status)
            metadata['reason'] = solver.reason_unknown() if status == z3.unknown else ''
            metadata['complete_for_fixed_template'] = status == z3.unsat
            break
        model = solver.model()
        g = fixed.copy()
        g.add_edges_from(uv for uv, x in variables.items() if z3.is_true(model.eval(x)))
        assert all(g.degree(v) == 3 for v in g) and nx.is_connected(g)
        code = nx.to_graph6_bytes(g, header=False).decode().strip()
        candidate = destination/'candidate.g6'
        candidate.write_text(code+'\n')
        raw = subprocess.check_output([oracle, str(candidate)], text=True).split()
        assert raw[0] == code
        good = list(map(int, raw[1:]))
        optimum = max(mask.bit_count() for mask in good)
        if optimum < best:
            best = optimum
            (destination/'best.json').write_text(json.dumps({'graph6': code, 'cind': best,
                                                           'edges': sorted(g.edges)}, indent=2)+'\n')
        large = [mask for mask in good if mask.bit_count() >= n//2]
        if not large:
            metadata['candidate_counterexample'] = {'graph6': code, 'exact_oracle_cind': optimum}
            metadata['termination'] = 'candidate requires independent verification'
            save()
            raise RuntimeError(f'Candidate counterexample: {destination}')
        new = 0
        for mask in large:
            if mask in cuts:
                continue
            chosen = {v for v in range(n) if mask >> v & 1}
            required = []
            for v in chosen:
                fixed_degree = sum(u in chosen for u in fixed[v])
                terms = [(x, 1) for (a, b), x in variables.items()
                         if (a == v and b in chosen) or (b == v and a in chosen)]
                if terms:
                    required.append(z3.PbEq(terms, 2-fixed_degree))
                else:
                    required.append(z3.BoolVal(fixed_degree == 2))
            # A genuine counterexample must make this subset fail to be good.
            assert all(z3.is_true(model.eval(term)) for term in required)
            solver.add(z3.Not(z3.And(required)))
            cuts.add(mask)
            new += 1
        assert new > 0
        records.append({'iteration': len(records), 'cind': optimum, 'best': best,
                        'new_cuts': new, 'cuts': len(cuts),
                        'elapsed_seconds': round(time.monotonic()-start, 3)})
        print(seed, cycles, records[-1], flush=True)
        save()
    else:
        metadata['termination'] = 'wall-time limit'
    save()
    print('FINISHED', seed, cycles, metadata.get('termination'), 'best', best, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, default=120)
    parser.add_argument('--seed', type=int, default=20261105)
    parser.add_argument('--cycles', type=int, nargs='+', default=[11])
    parser.add_argument('--cases', type=int, default=4)
    parser.add_argument('--theta', type=int, nargs=3)
    parser.add_argument('--barbell', type=int, nargs=2)
    parser.add_argument('--oracle', default='tmp/cubic_round3/enumerate_large')
    parser.add_argument('--output', type=Path, default=Path('tmp/cubic_round5/planted'))
    args = parser.parse_args()
    for i in range(args.cases):
        search(args.cycles, args.seed+i, args.seconds, args.oracle, args.output,
               args.theta, args.barbell)
