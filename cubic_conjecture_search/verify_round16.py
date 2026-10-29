"""Independent integer/rational checks for continuation 16 (stdlib only).

Finite checks support the stated reductions and certificates. They do not
prove the original conjecture, which remains unresolved.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time

from verify_bridge_reduction import graph, edges, good, good_sets, cap, CAP_IN, CAP_OUT
from verify_round12 import decode, connected_cubic

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'round16_data'


def target(a):
    return sum(map(len, a))//2-len(a)


def score(a, s):
    return sum(len(a[v]) == 3 for v in s)


def induced(a, vertices):
    vertices = sorted(vertices)
    index = {v: i for i, v in enumerate(vertices)}
    return [{index[u] for u in a[v] if u in index} for v in vertices], vertices


def small_graphs(maximum):
    for n in range(1, maximum+1):
        possible = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            a = graph(n, [e for i, e in enumerate(possible) if mask >> i & 1])
            if max(map(len, a)) <= 3:
                yield a


def neighbourhood_identity():
    graphs = cases = lifts = reducible = 0
    for a in small_graphs(6):
        graphs += 1
        for s in good_sets(a):
            if not s:
                continue
            t = set().union(*(a[v] for v in s))-s
            b, old = induced(a, set(range(len(a)))-s-t)
            delta = sum(len(a[v])-1 for v in t)-sum(len(a[v]&t) for v in t)//2
            assert target(a)-target(b) == delta
            gain = score(a, s)
            reducible += gain >= delta
            for r in good_sets(b):
                lifted = s | {old[v] for v in r}
                assert good(a, lifted)
                assert score(a, lifted) >= score(b, r)+gain
                lifts += 1
            cases += 1
    return dict(labelled_subcubic_graphs=graphs, good_sets=cases,
                lifts=lifts, reducible_sets=reducible, maximum_order=6)


def house_lifts():
    counts = Counter()
    for outside in small_graphs(5):
        n = len(outside)
        for x in range(n):
            for y in range(x, n):
                if x == y:
                    if len(outside[x]) != 1:
                        continue
                    kind = 'equal'
                else:
                    if len(outside[x]) != 2 or len(outside[y]) != 2:
                        continue
                    kind = 'adjacent' if y in outside[x] else 'nonadjacent'
                u, v, a, b, w = range(n, n+5)
                h = graph(n+5, edges(outside)+[(u,v),(u,a),(a,b),(b,v),
                                              (a,w),(b,w),(u,x),(v,y)])
                if kind == 'nonadjacent':
                    reduced = graph(n, edges(outside)+[(x,y)])
                    old = list(range(n))
                    assert target(h)-target(reduced) == 2
                elif kind == 'adjacent':
                    reduced = outside
                    old = list(range(n))
                    assert target(h)-target(reduced) == 3
                else:
                    reduced, old = induced(outside, set(range(n))-{x})
                    assert target(h)-target(reduced) == 3
                counts[kind+'_graphs'] += 1
                for s in good_sets(reduced):
                    r = {old[z] for z in s}
                    if kind == 'nonadjacent':
                        added = {u,v} if x in r and y in r else {a,b,w}
                    elif kind == 'adjacent':
                        added = {u,a,b,v} if x not in r and y not in r else {a,b,w}
                    else:
                        added = {u,a,b,v}
                    lifted = r | added
                    assert good(h, lifted)
                    assert score(h, lifted)-score(reduced, s) >= target(h)-target(reduced)
                    counts[kind+'_lifts'] += 1
    assert all(counts[k+'_graphs'] for k in ('equal','adjacent','nonadjacent'))
    return dict(counts)


def cycle_chain_checks():
    counts = Counter()
    # The outside graph is K4. A loop uses one outside edge; a parallel
    # pair uses two. Removing those edges frees the required incidences.
    for loop in (False, True):
        choices = [(k, 0) for k in range(1, 13)] if loop else [
            (k, l) for k in range(9) for l in range(k, 9) if k+l >= 2]
        for k, l in choices:
            base = graph(4, [(0,2),(0,3),(1,2),(1,3),(2,3)])
            u = 4
            v = u if loop else 5
            n = 5 if loop else 6
            es = edges(base)+[(u,0)]
            if not loop:
                es.append((v,1))
            cycle = {u,v}
            tips = set()
            for length in ([k] if loop else [k,l]):
                last = u
                for j in range(length):
                    a,b,w = n,n+1,n+2
                    n += 3
                    es += [(last,a),(a,b),(a,w),(b,w)]
                    cycle.update((a,b));tips.add(w);last=b
                es.append((last,v))
            h = graph(n,es)
            assert good(h,cycle) and all(len(h[z]) == 3 for z in cycle)
            neighbours = set().union(*(h[z] for z in cycle))-cycle
            assert tips <= neighbours
            reduced, old = induced(h,set(range(n))-cycle-neighbours)
            assert target(h)-target(reduced) <= len(cycle)
            for s in good_sets(reduced):
                lifted = cycle | {old[z] for z in s}
                assert good(h,lifted)
                assert score(h,lifted)-score(reduced,s) >= target(h)-target(reduced)
                counts['lifts'] += 1
            counts['loop_configurations' if loop else 'parallel_configurations'] += 1
    return dict(counts)


def conditioned_certificates():
    rows = json.loads((DATA/'conditioned_cut_certificates.json').read_text())
    assert len(rows) == 2 and rows[0]['graph6'] == rows[1]['graph6']
    a, es = decode(rows[0]['graph6'])
    connected_cubic(a)
    n = len(a)
    assert n == 26
    bridge = es.index((12,25))
    assert [(r['marked'],r['unmarked']) for r in rows] == [(0,1<<bridge),(1<<bridge,0)]
    verified = []
    for row in rows:
        marked, unmarked = row['marked'], row['unmarked']
        assert not marked & unmarked
        probs = [Fraction() for e in es]
        total_mass = Fraction()
        for term in row['terms']:
            f = term['factor']
            assert 0 <= f < 1 << len(es)
            degree = [0]*n
            for i,(u,v) in enumerate(es):
                if f >> i & 1:
                    degree[u] += 1;degree[v] += 1
            assert all(d in (0,2) for d in degree)
            r = sum(1 << v for v,d in enumerate(degree) if d)
            x = cut = 0
            for i,(u,v) in enumerate(es):
                su, sv = bool(r >> u & 1), bool(r >> v & 1)
                if su and sv and not f >> i & 1:
                    x |= 1 << i
                if su != sv:
                    cut |= 1 << i
            assert (r,x,cut) == (term['r'],term['x'],term['cut'])
            assert not x & ~marked
            assert r.bit_count()-2*x.bit_count() == cut.bit_count()
            c = Fraction(term['coefficient'])
            assert c > 0
            total_mass += c
            for i in range(len(es)):
                if cut >> i & 1:
                    probs[i] += c
        assert total_mass == 1
        lower = sum(1-p if marked >> i & 1 else p if unmarked >> i & 1
                    else min(p,1-p) for i,p in enumerate(probs))
        assert lower == Fraction(row['cut_total']) == 13
        verified.append(dict(marked=marked,unmarked=unmarked,
                             terms=len(row['terms']),lower_bound=str(lower)))
    return dict(order=n,edge_count=len(es),cubes=verified,
                indexed_markings_covered=1<<len(es),
                scope='Exact certificate for all markings, not individual enumeration')


def rooted_cap_certificates():
    a = cap();es=edges(a)
    groups = {
        'out': [{4,6,7,8,9,10},{5,6,7,8,9,11},
                {0,1,2,8,10,11},{0,1,2,9,10,11}],
        'in': [{1,2,3,4,5,6,12},{0,2,3,4,5,7,12},
               {0,2,4,6,8,10,12},{1,2,4,7,9,11,12}],
    }
    output = {}; boundary_masks = {}
    for kind,sets in groups.items():
        assert len(sets) == 4
        for s in sets:
            assert good(a,s) and score(a,s) == 6
            assert (12 in s) == (kind == 'in')
        counts = [sum((u in s)!=(v in s) for s in sets) for u,v in es]
        assert max(counts) <= 2
        assert sum(counts) == 24
        boundary_masks[kind] = [sum(1 << i for i,(u,v) in enumerate(es)
                                   if (u in s)!=(v in s)) for s in sets]
        output[kind] = dict(sets=[sorted(s) for s in sets],coefficient='1/4',
                            cut_counts=counts,branch_score=6)
    (DATA/'rooted_cap_certificates.json').write_text(json.dumps(output,indent=2)+'\n')
    # Every zero-or-one pattern, using four explicitly checked states.
    for marked in range(1 << len(es)):
        for cuts in boundary_masks.values():
            assert max(6+2*(marked.bit_count()-(marked&c).bit_count())
                       for c in cuts) >= 6+marked.bit_count()
    # Build actual rooted graphs and full cubic doubles for all patterns
    # with at most two marked edges. This checks the lifting implementation.
    built = 0
    for size in range(3):
        for indices in itertools.combinations(range(len(es)),size):
            marked = sum(1 << i for i in indices)
            witnesses = {}
            for kind,sets in groups.items():
                chosen_index = max(range(4),key=lambda j:
                    6+2*(size-(marked&boundary_masks[kind][j]).bit_count()))
                s = sets[chosen_index].copy()
                h = [ns.copy() for ns in a];tips=[]
                for i in indices:
                    u,v = es[i];p=len(h);q=p+1;w=p+2
                    h.extend([set(),set(),set()]);tips.append(w)
                    h[u].remove(v);h[v].remove(u)
                    for x,y in ((u,p),(p,q),(q,v),(p,w),(q,w)):
                        h[x].add(y);h[y].add(x)
                    if u in s and v in s:s.update((p,q))
                    elif u not in s and v not in s:s.update((p,q,w))
                assert good(h,s) and score(h,s) >= 6+size
                for tip in tips:
                    offset=len(h)
                    h.extend([{offset+v for v in ns} for ns in a])
                    h[tip].add(offset+12);h[offset+12].add(tip)
                    s.update(offset+v for v in (CAP_OUT if tip in s else CAP_IN))
                assert len(h) == 13+16*size
                assert all(len(ns) == (2 if v == 12 else 3) for v,ns in enumerate(h))
                assert good(h,s) and (12 in s) == (kind == 'in')
                assert len(s) >= 6+8*size+(kind == 'in')
                witnesses[kind] = s
            order=len(h)
            doubled = [ns.copy() for ns in h]+[{order+v for v in ns} for ns in h]
            doubled[12].add(order+12);doubled[order+12].add(12)
            chosen = witnesses['in'] | {order+v for v in witnesses['out']}
            connected_cubic(doubled)
            assert good(doubled,chosen) and 2*len(chosen) >= len(doubled)
            built += 1
    return dict(root=12,states={kind:dict(terms=4,branch_score=6,
                maximum_cut_probability=str(Fraction(max(row['cut_counts']),4)))
                for kind,row in output.items()},marked_patterns=1<<len(es),
                rooted_pattern_checks=2*(1<<len(es)),full_cubic_witnesses=built,
                maximum_full_cubic_order=90)


if __name__ == '__main__':
    start=time.monotonic()
    result=dict(original_conjecture_resolved=False,
        neighbourhood_identity=neighbourhood_identity(), house_lifts=house_lifts(),
        cycle_chains=cycle_chain_checks(), conditioned_certificates=conditioned_certificates(),
        rooted_cap_certificates=rooted_cap_certificates())
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(DATA.iterdir()) if p.is_file()}
    (ROOT/'round16_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
