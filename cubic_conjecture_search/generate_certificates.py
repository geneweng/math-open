"""Regenerate the finite search and exact fractional-cover certificates.

Requires nauty's geng, a C++ compiler, and OR-Tools. Floating-point linear
programming proposes coefficients; exact rational verification accepts them.
No solver status or floating-point tolerance is used as the final certificate.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

from ortools.linear_solver import pywraplp
from verify_certificates import graph6, has_bridge, verify


def fractional_cover(adj, masks):
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if solver is None:
        raise RuntimeError('OR-Tools GLOP solver is unavailable')
    columns = [solver.NumVar(0, solver.infinity(), str(mask)) for mask in masks]
    for v in range(len(adj)):
        constraint = solver.Constraint(1, solver.infinity())
        for mask, column in zip(masks, columns):
            if (mask >> v) & 1:
                constraint.SetCoefficient(column, 1)
    solver.Minimize(sum(columns))
    if solver.Solve() != solver.OPTIMAL:
        raise RuntimeError('fractional cover optimization did not finish optimally')
    cover = []
    for mask, column in zip(masks, columns):
        coefficient = Fraction(column.solution_value()).limit_denominator(100000)
        if coefficient:
            cover.append({'mask': mask, 'coefficient': str(coefficient)})
    total = sum((Fraction(e['coefficient']) for e in cover), Fraction(0))
    coverage = [sum((Fraction(e['coefficient']) for e in cover if (e['mask'] >> v) & 1), Fraction(0))
                for v in range(len(adj))]
    if total > 2 or any(c < 1 for c in coverage):
        raise RuntimeError('no exact cover of total weight at most two was obtained; '
                           'this is not itself a counterexample')
    return cover


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-order', type=int, default=16)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('certificates.json'))
    args = parser.parse_args()
    if args.max_order not in range(4, 21, 2):
        parser.error('--max-order must be even and between 4 and 20')
    geng = shutil.which('geng')
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not geng or not compiler:
        parser.error('geng and a C++ compiler are required')
    records = []
    with tempfile.TemporaryDirectory(prefix='cubic-certificates-') as scratch:
        scratch = Path(scratch)
        binary = scratch / 'enumerate_good_sets'
        subprocess.run([compiler, '-O3', '-std=c++17', str(Path(__file__).with_name('enumerate_good_sets.cpp')),
                        '-o', str(binary)], check=True)
        for n in range(4, args.max_order + 1, 2):
            graph_file = scratch / f'cubic{n}.g6'
            subprocess.run([geng, '-cq', '-d3', '-D3', str(n), str(graph_file)], check=True)
            with subprocess.Popen([str(binary), str(graph_file)], stdout=subprocess.PIPE, text=True) as process:
                for line in process.stdout:
                    fields = line.split()
                    code = fields[0]
                    masks = list(map(int, fields[1:]))
                    adj = graph6(code)
                    witness = max(masks, key=int.bit_count)
                    if 2 * witness.bit_count() < n:
                        raise RuntimeError(f'candidate counterexample {code}: independently verify it')
                    record = {'graph6': code, 'half_witness': witness,
                              'computed_maximum': witness.bit_count()}
                    if not has_bridge(adj):
                        record['fractional_cover'] = fractional_cover(adj, masks)
                    records.append(record)
                if process.wait() != 0:
                    raise RuntimeError('good-set enumeration failed')
            print(f'completed order {n}; {len(records)} graphs total', flush=True)
    data = {'scope': 'Finite computation; the general induced cycles conjecture remains unresolved.',
            'generator': 'nauty geng -cq -d3 -D3, even orders 4 through ' + str(args.max_order),
            'graphs': records}
    data['summary'] = verify(data)
    args.output.write_text(json.dumps(data, separators=(',', ':')) + '\n')
    print(json.dumps(data['summary'], indent=2))


if __name__ == '__main__':
    main()
