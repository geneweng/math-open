"""Exact rational proposals for cubes of edge-triangle markings.

P is forced marked, Q is forced unmarked. Every Eulerian state used has
all its chords in P. Its cut probabilities p certify the whole cube when
sum_P(1-p) + sum_Q p + sum_free min(p,1-p) >= n/2.
Numerical optimization only proposes coefficients; Fraction checks accept.
This is not a proof of the unrestricted induced cycles conjecture.
"""
from fractions import Fraction
import json
from pathlib import Path

from triangle_subset_synthesis import decode, states


def certificate(code, marked, unmarked):
    from ortools.linear_solver import pywraplp
    a, es = decode(code)
    assert not marked & unmarked
    candidates = [s for s in states(a, es) if not s[1] & ~marked]
    lp = pywraplp.Solver.CreateSolver('GLOP')
    lam = [lp.NumVar(0, 1, f'l{i}') for i in range(len(candidates))]
    lp.Add(sum(lam) == 1)
    objective = []
    for i in range(len(es)):
        p = sum(l for s, l in zip(candidates, lam) if s[2] >> i & 1)
        if marked >> i & 1:
            objective.append(1-p)
        elif unmarked >> i & 1:
            objective.append(p)
        else:
            y = lp.NumVar(0, .5, f'y{i}')
            lp.Add(y <= p)
            lp.Add(y <= 1-p)
            objective.append(y)
    lp.Maximize(sum(objective))
    assert lp.Solve() == lp.OPTIMAL
    terms = [(s, Fraction(l.solution_value()).limit_denominator(1000000))
             for s, l in zip(candidates, lam) if l.solution_value() > 1e-9]
    assert sum(c for s, c in terms) == 1 and all(c > 0 for s, c in terms)
    probs = [sum((c for s, c in terms if s[2] >> i & 1), Fraction())
             for i in range(len(es))]
    total = sum(1-p if marked >> i & 1 else p if unmarked >> i & 1
                else min(p, 1-p) for i, p in enumerate(probs))
    assert total >= Fraction(len(a), 2)
    return dict(graph6=code, marked=marked, unmarked=unmarked,
                cut_total=str(total), terms=[dict(r=s[0], x=s[1], cut=s[2],
                    factor=s[3], coefficient=str(c)) for s, c in terms])


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    code = (root/'round15_data/tight_large_bases.g6').read_text().splitlines()[-1]
    a, es = decode(code)
    assert len(a) == 26
    bridge = es.index((12, 25))
    rows = [certificate(code, 0, 1 << bridge),
            certificate(code, 1 << bridge, 0)]
    output = root/'round16_data/conditioned_cut_certificates.json'
    output.write_text(json.dumps(rows, indent=2)+'\n')
    print(json.dumps(dict(cubes=len(rows), terms=[len(r['terms']) for r in rows],
                         totals=[r['cut_total'] for r in rows], output=str(output))))
