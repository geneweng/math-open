#!/usr/bin/env python3
"""Independently check the round-nine finite obstruction certificates.

Uses vertex-path cycle enumeration, edge-parity recursion, and component
traversal from the standard-library verifier, not the C++ cycle-space/DSU
implementation. Checks every reported neutral case through order 20, but
does not independently repeat the full 556,471-graph census.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from verify_pseudoforest_repair import decode, cycles_of, odd_factors, statistics

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "round9_data"


def read_log(path):
    cases, summary = [], None
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "NEUTRAL":
            cases.append(dict(graph6=fields[1], factor=int(fields[2]),
                              isolated=int(fields[3])))
        elif fields[0] == "REPAIR_MOVES":
            assert "minimum_moves" not in cases[-1]
            cases[-1]["minimum_moves"] = int(fields[1])
        elif fields[0] == "DONE_FILE":
            summary = {k: int(v) for k, v in
                       (field.split("=") for field in fields[2:])}
        else:
            raise AssertionError(line)
    assert summary is not None and summary["flat_repairs"] == len(cases)
    assert all(c["minimum_moves"] == 2 for c in cases)
    return cases, summary


def connectivity(adj):
    n = len(adj)
    vertices = set(range(n))
    for size in (0, 1, 2):
        for removed in combinations(range(n), size):
            left = vertices - set(removed)
            todo = [left.pop()]
            while todo:
                for u in adj[todo.pop()] & left:
                    left.remove(u)
                    todo.append(u)
            if left:
                return size
    return 3  # A simple cubic graph has connectivity at most three.


def subset_histogram(adj):
    """All 2^n subsets, independent of odd-factor enumeration."""
    masks = [sum(1 << u for u in a) for a in adj]
    histogram = [0] * (len(adj) + 1)
    witness = 0
    for s in range(1 << len(adj)):
        left = s
        while left:
            bit = left & -left
            v = bit.bit_length() - 1
            if (masks[v] & s).bit_count() != 2:
                break
            left ^= bit
        else:
            histogram[s.bit_count()] += 1
            if s.bit_count() > witness.bit_count():
                witness = s
    return histogram, witness


def check_neutral_cases(cases):
    grouped = defaultdict(list)
    for case in cases:
        grouped[case["graph6"]].append(case)
    totals, results = Counter(), []
    for index, (code, group) in enumerate(grouped.items(), 1):
        n, edges, adj = decode(code)
        cycles = cycles_of(n, edges, adj)
        states = {f: statistics(n, edges, f) for f in odd_factors(n, edges)}
        assert len(states) == 1 << (n // 2 + 1)
        kappa = connectivity(adj)
        assert kappa >= 1
        girth = min(c.bit_count() for c in cycles)
        totals["graphs"] += 1
        totals["odd_factors_independently_enumerated"] += len(states)
        totals["simple_cycles_independently_enumerated"] += len(cycles)
        exact = None
        if kappa == 3:
            hist, witness = subset_histogram(adj)
            exact = dict(histogram=hist, maximum=witness.bit_count(),
                         witness=witness, subsets_checked=1 << n)
            totals["vertex_subsets_checked"] += 1 << n
        for case in group:
            f = case["factor"]
            initial = states[f]
            assert initial["pseudoforest"] and initial["isolated"] == case["isolated"] > 0
            neutral = []
            move_table = Counter()
            for c in cycles:
                after = states[f ^ c]
                if after["pseudoforest"]:
                    assert after["isolated"] >= initial["isolated"]
                    move_table[(after["edges"], after["isolated"])] += 1
                    if after["isolated"] == initial["isolated"]:
                        neutral.append(f ^ c)
            # Having exhausted every single cycle, one neutral move and one
            # improving move are both sufficient and necessary.
            path = None
            for middle in neutral:
                for c in cycles:
                    last = states[middle ^ c]
                    if last["pseudoforest"] and last["isolated"] < initial["isolated"]:
                        path = [f, middle, middle ^ c]
                        break
                if path:
                    break
            assert path is not None
            final = states[path[-1]]
            selected = set(final["leaves"]) if final["isolated"] == 0 else None
            if selected is not None:
                assert len(selected) >= n // 2
                assert all(len(adj[v] & selected) == 2 for v in selected)
            totals["neutral_factors"] += 1
            totals[f"connectivity_{kappa}"] += 1
            totals[f"initial_isolated_{initial['isolated']}"] += 1
            result = dict(graph6=code, factor=f, connectivity=kappa, girth=girth,
                          minimum_repair_moves=2, simple_cycles=len(cycles),
                          neutral_moves=len(neutral), repair_path=path,
                          initial_isolated=initial["isolated"], final_isolated=final["isolated"],
                          good_witness=sorted(selected) if selected is not None else None)
            if kappa == 3:
                result.update(initial=initial, exact=exact,
                              allowed_move_table=[[m, j, count] for (m, j), count in sorted(move_table.items())],
                              repair_path_statistics=[states[x] for x in path])
            results.append(result)
        if index % 50 == 0:
            print(f"Independently checked {index}/{len(grouped)} neutral-case graphs", flush=True)
    return dict(totals), results


def check_budget():
    code = "I?BeeOwM?"
    n, edges, adj = decode(code)
    states = {f: statistics(n, edges, f) for f in odd_factors(n, edges)}
    assert len(states) == 64
    bad = min((s["edges"] + s["isolated"], f) for f, s in states.items() if s["isolated"])
    good = min((s["edges"], f) for f, s in states.items() if not s["isolated"])
    assert (bad[0], good[0]) == (8, 9)
    paper_factor = states[9700]
    assert paper_factor["components"] == [(2, 1), (4, 3), (4, 3)]
    assert len(paper_factor["leaves"]) - paper_factor["isolated"] == 7
    hist, witness = subset_histogram(adj)
    assert witness.bit_count() == 6
    return dict(graph6=code, odd_factors_checked=len(states), min_h_bad=bad[0],
                min_h_good=good[0], bad_witness=bad[1], good_witness=good[1],
                histogram=hist, exact_c_ind=witness.bit_count(), vertex_subsets_checked=1 << n)


def triangle_expansion_case(code, v, expected_profile, expected_expanded):
    n, edges, adj = decode(code)
    profiles = [0, 0, 0, 0]  # A, B, C, D; D permits deletion of an edge at v.
    for s in range(1 << n):
        selected = {u for u in range(n) if s >> u & 1}
        if all(len(adj[u] & selected) == 2 for u in selected):
            if v in selected:
                profiles[0] = max(profiles[0], len(selected))
            else:
                profiles[1] = max(profiles[1], len(selected))
                if not selected & adj[v]:
                    profiles[2] = max(profiles[2], len(selected))
        if v in selected:
            for u in adj[v]:
                if all(len(adj[x] & selected) - int(u in selected and x in (u, v)) == 2
                       for x in selected):
                    profiles[3] = max(profiles[3], len(selected))
    expanded_edges = [e for e in edges if v not in e]
    ports = [v, n, n + 1]
    expanded_edges += list(zip(ports, sorted(adj[v])))
    expanded_edges += [(ports[i], ports[(i + 1) % 3]) for i in range(3)]
    expanded = [set() for _ in range(n + 2)]
    for a, b in expanded_edges:
        assert b not in expanded[a] and a != b
        expanded[a].add(b)
        expanded[b].add(a)
    assert all(len(a) == 3 for a in expanded)
    hist, witness = subset_histogram(expanded)
    assert profiles == expected_profile
    assert witness.bit_count() == max(profiles[3] + 1, profiles[1], profiles[2] + 3) == expected_expanded
    return dict(graph6=code, vertex=v, profile_ABCD=profiles, original_c_ind=max(profiles[:2]),
                expanded_edges=expanded_edges, expanded_histogram=hist,
                expanded_c_ind=witness.bit_count(), expanded_witness=witness,
                vertex_subsets_checked=(1 << n) + (1 << (n + 2)))


def check_triangle_expansion():
    # The first case detects the missing edge-deletion boundary state in the
    # discarded A+1 formula. The second is an actual failure of unit gain.
    return dict(formula="max(D+1,B,C+3)", cases=[
        triangle_expansion_case("I?`cmPoM?", 0, [6, 7, 4, 8], 9),
        triangle_expansion_case("K?ABE`Ke@gDO", 0, [7, 8, 5, 7], 8)])


def main():
    small, small_summary = read_log(DATA / "repair_through18_log.txt")
    large, large_summary = read_log(DATA / "repair20_log.txt")
    assert (small_summary["graphs"], len(small)) == (45982, 214)
    assert (large_summary["graphs"], len(large)) == (510489, 1234)
    small_totals, small_results = check_neutral_cases(small)
    large_totals, large_results = check_neutral_cases(large)
    assert small_totals.get("connectivity_3", 0) == 0
    assert (large_totals["connectivity_1"], large_totals["connectivity_2"],
            large_totals["connectivity_3"]) == (152, 1079, 3)
    assert (large_totals["initial_isolated_1"], large_totals["initial_isolated_2"]) == (1218, 16)
    assert all(c["girth"] == 3 for c in large_results)
    special = next(c for c in large_results if c["factor"] == 983379956
                   and c["graph6"] == "S??????o@_@_gCGoWCAD?Cg?X??WO?IG?")
    cpp = json.loads((DATA / "three_connected_trap_profile.jsonl").read_text())
    assert special["exact"]["histogram"] == cpp["histogram"]
    assert special["exact"]["maximum"] == cpp["maximum"] == 14
    assert (special["simple_cycles"], special["neutral_moves"]) == (664, 57)
    assert special["repair_path"] == [983379956, 983451959, 977257976]
    result = dict(general_conjecture_resolved=False,
                  scope="All 1,448 reported neutral factors through order 20 independently checked; full census not independently repeated.",
                  through18=dict(cpp_summary=small_summary, independent=small_totals, cases=small_results),
                  order20=dict(cpp_summary=large_summary, independent=large_totals, cases=large_results),
                  budget_obstruction=check_budget(),
                  triangle_expansion=check_triangle_expansion())
    result["input_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in
                              (DATA / "repair_through18_log.txt", DATA / "repair20_log.txt",
                               DATA / "three_connected_trap_profile.jsonl")}
    destination = ROOT / "round9_verification.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"through18": small_totals, "order20": large_totals,
                      "budget_obstruction": result["budget_obstruction"],
                      "output": str(destination)}, indent=2))


if __name__ == "__main__":
    main()
