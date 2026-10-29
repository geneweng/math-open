"""All bipartite two-defect templates with |T|=|S|+2.

The core of T is a theta with three odd paths or two even cycles joined
by an odd path. Remaining components of S and T are even cycles.
No claim of isomorphism-free enumeration is made for their completions.
"""
import argparse
import json
import math
from pathlib import Path


def partitions(total, minimum=4):
    if total == 0:
        yield ()
    for first in range(minimum, total + 1, 2):
        for rest in partitions(total - first, first):
            yield (first,) + rest


def templates(order):
    assert order % 4 == 2 and order >= 10
    s = order // 2 - 1
    t = s + 2
    for sc in partitions(s):
        for core_size in range(6, t + 1, 2):
            for tc in partitions(t - core_size):
                for p in range(1, core_size, 2):
                    for q in range(max(p, 3), core_size, 2):
                        r = core_size + 1 - p - q
                        if r >= q and r % 2:
                            yield sc, 0, (p, q, r), tc
                for p in range(4, core_size, 2):
                    for q in range(p, core_size, 2):
                        r = core_size + 1 - p - q
                        if r >= 1 and r % 2:
                            yield sc, 1, (p, q, r), tc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('order', type=int)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    rows = []
    metadata = []
    for sc, kind, core, tc in templates(args.order):
        rows.append(' '.join(map(str, (len(sc), *sc, kind, *core, len(tc), *tc))))
        h = sum(sc) // 2
        cases = math.factorial(h) * math.factorial(h - (len(sc) == 1))
        metadata.append(dict(S_cycles=sc, core='theta' if kind == 0 else 'barbell',
                             core_lengths=core, T_cycles=tc, expected_cases=cases))
    args.output.write_text('\n'.join(rows) + '\n')
    args.output.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(dict(order=args.order, templates=len(rows),
                         expected_cases=sum(row['expected_cases'] for row in metadata))))


if __name__ == '__main__':
    main()
