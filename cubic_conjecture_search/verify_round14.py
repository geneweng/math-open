"""Independent checks of finite strictness census and rooted synthesis.

This does not prove or disprove the unrestricted induced-cycles conjecture.
The census relies on the existing geng input lists for isomorphism coverage.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

from verify_round12 import decode, connected_cubic, check_set
from verify_bridge_reduction import franklin, graph, good_sets

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'round14_data'


def cycle_space_good_sets(a):
    """All good sets via a spanning-forest binary cycle basis."""
    n = len(a)
    es = [(u,v) for v in range(n) for u in sorted(a[v]) if u<v]
    position = {e:i for i,e in enumerate(es)}
    parent = [-1]*n
    depth = [0]*n
    pe = [0]*n
    tree = set()
    components = 0
    for root in range(n):
        if parent[root]>=0:
            continue
        components += 1
        parent[root] = root
        queue = [root]
        for v in queue:
            for u in sorted(a[v]):
                if parent[u]>=0:
                    continue
                parent[u] = v
                depth[u] = depth[v]+1
                pe[u] = position[min(u,v),max(u,v)]
                tree.add(pe[u])
                queue.append(u)
    basis = []
    for i,(u,v) in enumerate(es):
        if i in tree:
            continue
        mask = 1<<i
        while u!=v:
            if depth[u]<depth[v]:
                u,v=v,u
            mask ^= 1<<pe[u]
            u = parent[u]
        basis.append(mask)
    assert len(basis)==len(es)-n+components
    incidence = [sum(1<<i for i,e in enumerate(es) if v in e) for v in range(n)]
    adj = [sum(1<<u for u in ns) for ns in a]
    good = {0}
    factor = 0
    for step in range(1,1<<len(basis)):
        factor ^= basis[(step & -step).bit_length()-1]
        selected = sum(1<<v for v in range(n) if factor & incidence[v])
        if all((selected & ns).bit_count()==2 for v,ns in enumerate(adj)
               if selected>>v&1):
            good.add(selected)
    return good


def strict_census():
    inputs = [ROOT/'round8_data/cubic_through18.g6', ROOT/'round9_data/cubic20.g6']
    counts = Counter()
    exact = []
    sentinel = object()
    with inputs[0].open() as first, inputs[1].open() as second, \
            gzip.open(DATA/'tight_census.txt.gz','rt') as certificates:
        codes = itertools.chain(first, second)
        for source, row in itertools.zip_longest(codes,certificates,fillvalue=sentinel):
            assert source is not sentinel and row is not sentinel
            code,score_s,witness_s,flag_s = row.split()
            assert source.strip()==code
            score,witness,flag = map(int,(score_s,witness_s,flag_s))
            a,_ = decode(code)
            n = len(a)
            connected_cubic(a)
            assert 0<=witness<1<<n
            selected = [v for v in range(n) if witness>>v&1]
            assert len(selected)==score
            check_set(a,selected,n//2)
            assert flag in (0,1)
            if flag:
                brute = list(good_sets(a))
                optimum = max(map(len,brute))
                assert score==optimum==n//2
                maxima = [s for s in brute if len(s)==optimum]
                assert all(any(u in s and v in s for s in maxima)
                           for v in range(n) for u in a[v] if u<v)
                exact.append(dict(graph6=code,order=n,optimum=optimum,
                                  maximum_set_count=len(maxima),
                                  every_edge_in_some_maximum=True))
            else:
                assert score>=n//2+1
            counts[n]+=1
    expected = {4:1,6:2,8:5,10:19,12:85,14:509,16:4060,18:41301,20:510489}
    assert dict(counts)==expected
    assert len(exact)==1 and exact[0]['graph6']=='K??FEaKR@oE_'
    # Explicit relabeling verifies the identification without an isomorphism package.
    relabel = [0,1,4,5,8,9,2,3,10,11,6,7]
    a,_ = decode(exact[0]['graph6'])
    f = franklin()
    assert sorted(relabel)==list(range(12))
    assert all({relabel[u] for u in a[v]}==f[relabel[v]] for v in range(12))
    return dict(graphs=sum(counts.values()),by_order=dict(counts),exact=exact,
                strict_witnesses=sum(counts.values())-len(exact),
                coverage_dependency='Existing geng input lists, compared row by row')


def synthesis_records():
    all_results = []
    for path in sorted(DATA.glob('synthesis*.json')):
        result = json.loads(path.read_text())
        assert result['status']!='running'
        seed,_ = decode(result['seed_graph6'])
        n = result['order']
        seed_edges = {(u,v) for v in range(n) for u in seed[v] if u<v}
        a_bound = result.get('root_in_bound',(n-1)//2)
        b_bound = result.get('root_out_bound',(n-1)//2)
        checked = []
        for row in result['records']:
            a,_ = decode(row['graph6'])
            assert len(a)==n and a[0]=={1,2}
            assert all(len(ns)==(2 if v==0 else 3) for v,ns in enumerate(a))
            es = {(u,v) for v in range(n) for u in a[v] if u<v}
            removed = len(seed_edges-es)
            if result['removed_edge_radius'] is not None:
                assert removed<=result['removed_edge_radius']
            masks = cycle_space_good_sets(a)
            inside = [s for s in masks if s&1]
            outside = [s for s in masks if not s&1]
            wa = max(inside,key=int.bit_count,default=0)
            wb = max(outside,key=int.bit_count)
            A = wa.bit_count() if inside else -1000
            B = wb.bit_count()
            forbidden = [s for s in masks if s.bit_count()>(a_bound if s&1 else b_bound)]
            assert len(forbidden)==row['large_good_set_count']
            assert row['witness'] in forbidden
            assert max(map(int.bit_count,masks))==row['largest_good_set']
            if 'root_in_optimum' in row:
                assert (A,B)==(row['root_in_optimum'],row['root_out_optimum'])
                assert max(2*B,A+B)==row['doubled_optimum']
            assert max(2*B,A+B)>=n, 'ORIGINAL COUNTEREXAMPLE CANDIDATE'
            full = [ns.copy() for ns in a]+[{n+u for u in ns} for ns in a]
            full[0].add(n)
            full[n].add(0)
            assert all(len(ns)==3 for ns in full)
            if A+B>2*B:
                chosen = wa | (wb<<n)
            else:
                chosen = wb | (wb<<n)
            check_set(full,[v for v in range(2*n) if chosen>>v&1],n)
            checked.append(dict(graph6=row['graph6'],A=A,B=B,
                                doubled_optimum=max(2*B,A+B),
                                full_cubic_witness=chosen,removed_edges=removed))
        all_results.append(dict(source=path.name,status=result['status'],
                                candidates=len(checked),root_in_bound=a_bound,
                                root_out_bound=b_bound,checks=checked))
    return all_results


def triangle_profiles():
    cases = 0
    rows = (ROOT/'round8_data/cubic_through18.g6').read_text().splitlines()
    rows = [code for code in rows if ord(code[0])-63<=10]
    rows.append('K??FEaKR@oE_')
    for code in rows:
        a,es = decode(code)
        n = len(a)
        masks = cycle_space_good_sets(a)
        for u,v in es:
            deleted = [ns.copy() for ns in a]
            deleted[u].remove(v)
            deleted[v].remove(u)
            B = max(map(int.bit_count,cycle_space_good_sets(deleted)))
            T = max((s.bit_count() for s in masks if s>>u&1 and s>>v&1),default=-1000)
            C = max(s.bit_count() for s in masks if not (s>>u&1 or s>>v&1))
            h = [ns.copy() for ns in deleted]+[set(),set(),set()]
            for x,y in [(u,n),(n,n+1),(n+1,v),(n,n+2),(n+1,n+2)]:
                h[x].add(y)
                h[y].add(x)
            adj = [sum(1<<x for x in ns) for ns in h]
            branch_mask = (1<<(n+2))-1
            best = 0
            # All vertex subsets, independently of the cycle-space calculation.
            for s in range(1<<(n+3)):
                score = (s & branch_mask).bit_count()
                if score<=best:
                    continue
                if all((ns&s).bit_count()==2 for x,ns in enumerate(adj) if s>>x&1):
                    best = score
            assert best==max(B,T+2,C+2)
            assert best>=n//2+1
            cases += 1
    return dict(indexed_edge_expansions=cases,base_graphs=len(rows),
                verification='All vertex subsets of each expanded graph')


def crosscheck_oracle():
    sys.path.insert(0,str(ROOT/'exploratory'))
    from rooted_synthesis import good_masks
    count = 0
    for n in range(1,6):
        pairs = list(itertools.combinations(range(n),2))
        for mask in range(1<<len(pairs)):
            a = graph(n,[e for i,e in enumerate(pairs) if mask>>i&1])
            if max(map(len,a))>3:
                continue
            brute = {sum(1<<v for v in s) for s in good_sets(a)}
            assert set(good_masks(a,0))==brute
            threshold = (n+1)//2
            assert set(good_masks(a,threshold))=={s for s in brute if s.bit_count()>=threshold}
            assert cycle_space_good_sets(a)==brute
            count += 1
    return dict(labelled_subcubic_graphs=count,maximum_order=5)


if __name__=='__main__':
    started = time.monotonic()
    result = dict(original_conjecture_resolved=False,strict_census=strict_census(),
                  synthesis=synthesis_records(),oracle_crosscheck=crosscheck_oracle(),
                  triangle_profiles=triangle_profiles())
    result['elapsed_seconds'] = round(time.monotonic()-started,3)
    result['data_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(DATA.iterdir()) if p.is_file()}
    (ROOT/'round14_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='synthesis'},indent=2))
    print('Synthesis checks',[(r['source'],r['candidates'],r['status']) for r in result['synthesis']])
