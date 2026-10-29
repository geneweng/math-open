"""CEGIS search for a counterexample to the ORIGINAL induced-cycle bound.

Seek an odd-order graph Q, with one degree-two root and all other degrees
three, with root-out optimum B <= b and root-in optimum A <= |Q|-1-b,
where b <= (|Q|-1)/2. Joining two copies gives a cubic counterexample.
A timeout is UNKNOWN. All candidates also receive the full doubling test.
The bounded search fixes the root neighbours and a labelled edge-distance
from a previously verified seed; it is not a census of rooted graphs.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_round12 import decode


def good_masks(adj, threshold):
    """Enumerate good vertex subsets, using degree propagation, not SAT."""
    n = len(adj)
    a = [sum(1 << u for u in ns) for ns in adj]
    full = (1 << n) - 1
    out = []

    def visit(yes, no):
        if n - no.bit_count() < threshold:
            return
        while True:
            old = yes, no
            unknown = full ^ (yes | no)
            for v, ns in enumerate(a):
                if no >> v & 1:
                    continue
                selected = (yes & ns).bit_count()
                free = ns & unknown
                if selected > 2 or selected + free.bit_count() < 2:
                    if yes >> v & 1:
                        return
                    no |= 1 << v
                elif yes >> v & 1:
                    if selected == 2:
                        no |= free
                    elif selected + free.bit_count() == 2:
                        yes |= free
                if yes & no:
                    return
                unknown = full ^ (yes | no)
            if old == (yes, no):
                break
        if n - no.bit_count() < threshold:
            return
        if not unknown:
            if yes.bit_count() >= threshold:
                out.append(yes)
            return
        vertices = [v for v in range(n) if unknown >> v & 1]
        v = max(vertices, key=lambda v: ((a[v] & yes).bit_count(),
                                        -(a[v] & unknown).bit_count(), -v))
        visit(yes | (1 << v), no)
        visit(yes, no | (1 << v))

    visit(0, 0)
    return out


def encode(a):
    n = len(a)
    assert n < 63
    bits = [int(u in a[v]) for v in range(1, n) for u in range(v)]
    bits += [0] * (-len(bits) % 6)
    return chr(n + 63) + ''.join(chr(63 + sum(bits[i+j] << (5-j)
        for j in range(6))) for i in range(0, len(bits), 6))


def run(args):
    import z3

    start = time.monotonic()
    rows = json.loads(args.seed_file.read_text())['search']['exact_checks']
    rows = [r for r in rows if ord(r['graph6'][0])-63 == args.order]
    row = min(rows, key=lambda r: (r['A_count'] + r['B_count'], r['graph6']))
    a, _ = decode(row['graph6'])
    root = row['root']
    order = [root] + sorted(a[root])
    order += [v for v in range(len(a)) if v not in order]
    rename = {v: i for i, v in enumerate(order)}
    seed = [{rename[u] for u in a[v]} for v in order]
    n = len(seed)
    bound_b = args.root_out_bound if args.root_out_bound is not None else (n-1)//2
    bound_a = n-1-bound_b
    assert 0 <= bound_b <= (n-1)//2
    threshold = min(bound_a, bound_b)+1
    variables = {(u, v): z3.Bool(f'e{u}_{v}') for v in range(1, n)
                 for u in range(v)}
    edge = lambda u, v: variables[min(u, v), max(u, v)]
    solver = z3.SolverFor('QF_FD')
    solver.set(timeout=args.query_ms, random_seed=2026102814)
    for v in range(n):
        solver.add(z3.PbEq([(edge(u, v), 1) for u in range(n) if u != v],
                           2 if v == 0 else 3))
    for v in range(1, n):
        solver.add(edge(0, v) == (v in (1, 2)))
    reference = [edge(u, v) for v in range(n) for u in seed[v] if u < v]
    if args.radius is not None:
        solver.add(z3.PbGe([(x, 1) for x in reference],
                           len(reference) - args.radius))
    cuts = set()

    def forbid(mask):
        assert mask.bit_count() >= threshold
        assert mask.bit_count() > (bound_a if mask & 1 else bound_b)
        if mask in cuts:
            return
        vertices = [v for v in range(n) if mask >> v & 1]
        solver.add(z3.Not(z3.And([z3.PbEq([(edge(u, v), 1)
            for u in vertices if u != v], 2) for v in vertices])))
        cuts.add(mask)

    for mask in good_masks(seed, threshold):
        if mask.bit_count() > (bound_a if mask & 1 else bound_b):
            forbid(mask)
    initial_cuts = len(cuts)
    records = []
    status_text = 'iteration_limit'
    for iteration in range(args.iterations):
        if time.monotonic()-start > args.seconds:
            status_text = 'wall_time_limit'
            break
        status = solver.check()
        if status != z3.sat:
            status_text = str(status)
            print('STOP', status_text,
                  solver.reason_unknown() if status == z3.unknown else '', flush=True)
            break
        model = solver.model()
        a = [set() for _ in range(n)]
        for (u, v), x in variables.items():
            if z3.is_true(model.eval(x)):
                a[u].add(v)
                a[v].add(u)
        assert all(len(ns) == (2 if v == 0 else 3) for v, ns in enumerate(a))
        all_masks = good_masks(a, 0)
        optimum_a = max((s.bit_count() for s in all_masks if s & 1), default=-1000)
        optimum_b = max(s.bit_count() for s in all_masks if not s & 1)
        masks = [s for s in all_masks if s.bit_count() > (bound_a if s & 1 else bound_b)]
        record = dict(iteration=iteration, graph6=encode(a),
                      forbidden_size_threshold=threshold,
                      root_in_optimum=optimum_a, root_out_optimum=optimum_b,
                      doubled_optimum=max(2*optimum_b, optimum_a+optimum_b),
                      large_good_set_count=len(masks),
                      witness=max(masks, key=int.bit_count, default=0),
                      largest_good_set=max(map(int.bit_count, all_masks)))
        records.append(record)
        if max(2*optimum_b, optimum_a+optimum_b) < n:
            status_text = 'COUNTEREXAMPLE_CANDIDATE'
            break
        assert masks
        before = len(cuts)
        for mask in masks:
            forbid(mask)
        assert len(cuts) > before
        print('candidate', iteration, 'large_sets', len(masks), 'cuts', len(cuts),
              'seconds', round(time.monotonic()-start, 2), flush=True)
        args.output.write_text(json.dumps(dict(records=records, status='running'), indent=2))
    result = dict(original_conjecture_resolved=False, order=n, root=0,
                  seed_graph6=encode(seed), removed_edge_radius=args.radius,
                  root_in_bound=bound_a, root_out_bound=bound_b,
                  fixed_root_neighbours=[1, 2], initial_cuts=initial_cuts,
                  total_cuts=len(cuts), status=status_text, records=records,
                  elapsed_seconds=round(time.monotonic()-start, 3))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print('DONE', status_text, 'candidates', len(records), 'cuts', len(cuts), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--order', type=int, default=25)
    p.add_argument('--radius', type=int)
    p.add_argument('--root-out-bound', type=int)
    p.add_argument('--iterations', type=int, default=200)
    p.add_argument('--seconds', type=int, default=300)
    p.add_argument('--query-ms', type=int, default=20000)
    p.add_argument('--seed-file', type=Path,
                   default=Path('cubic_conjecture_search/round13_verification.json'))
    p.add_argument('--output', type=Path, required=True)
    run(p.parse_args())
