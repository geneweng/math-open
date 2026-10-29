"""Independently check all retained order-22 edge-boundary certificates.
Input completeness is inherited by exact row comparison with round 30.
"""
import concurrent.futures,gzip,hashlib,itertools,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round32_data';OLD=ROOT/'round30_data';TMP=ROOT.parent/'tmp/cubic_round32'

def check(i):
    while True:
        p=DATA/'generation_progress.json'
        try:done={r['shard'] for r in json.loads(p.read_text())}
        except (FileNotFoundError,json.JSONDecodeError):done=set()
        if i in done:break
        time.sleep(1)
    path=DATA/f'certificates-{i}.txt.gz'
    dec=subprocess.Popen(['gzip','-dc',str(path)],stdout=subprocess.PIPE)
    checked=subprocess.run([str(TMP/'check_edge_half')],stdin=dec.stdout,capture_output=True,text=True);dec.stdout.close()
    assert dec.wait()==0 and checked.returncode==0,(i,checked.stderr)
    fields=checked.stdout.split();assert fields[::2]==['GRAPHS','EXPLICIT','IMPLICIT']
    graphs,explicit,implicit=map(int,fields[1::2]);assert explicit+implicit==33*graphs
    with gzip.open(path,'rb') as new,gzip.open(OLD/f'certificates-{i}.txt.gz','rb') as old:
        compared=0
        for a,b in itertools.zip_longest(new,old):
            assert a is not None and b is not None
            assert b' '.join(a.split()[:2])+b'\n'==b,(i,compared)
            compared+=1
    assert compared==graphs
    log=(DATA/f'search-{i}.log').read_text().splitlines()[-1].split()
    assert log[:2]==['COMPLETE','graphs'] and int(log[2])==graphs and int(log[4])==explicit
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    row=dict(shard=i,graphs=graphs,explicit_edge_masks=explicit,implicit_edge_masks=implicit,sha256=digest)
    (DATA/f'check-{i}.json').write_text(json.dumps(row)+'\n')
    print('VERIFIED',i,graphs,flush=True);return row

def main():
    subprocess.run(['clang++','-O3','-std=c++17',str(ROOT/'exploratory/check_edge_half.cpp'),'-o',str(TMP/'check_edge_half')],check=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,range(64)))
    graphs=sum(r['graphs'] for r in rows);explicit=sum(r['explicit_edge_masks'] for r in rows);implicit=sum(r['implicit_edge_masks'] for r in rows)
    assert graphs==7319447 and explicit+implicit==241541751
    result=dict(original_conjecture='unresolved',order=22,graphs=graphs,parent_edge_records=explicit+implicit,
                explicit_edge_masks=explicit,implicit_edge_masks=implicit,shards=rows,
                consequence='Every symmetric or mixed bridge join of two edge-subdivision rooted fragments from connected simple cubic order-22 parents satisfies the original half bound (order 46). Equivalently, this covers all connected rooted 23-vertex fragments whose root has two nonadjacent neighbours.',
                limitation='Not a census of order-46 cubic graphs. Rooted fragments with adjacent root neighbours are outside this result. Completeness of the source census relies on nauty geng; every new row is matched exactly to the source.')
    (ROOT/'round32_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('COMPLETE',graphs,explicit,implicit,flush=True)

def check_mixed_joins():
    # Construct actual 46-vertex cubic joins and check selected degrees directly.
    import random
    from verify_round12 import decode
    pool=[]
    for shard in range(64):
        with gzip.open(DATA/f'certificates-{shard}.txt.gz','rt') as f:
            for line in itertools.islice(f,16):
                fields=line.split();a,es=decode(fields[0]);mask=int(fields[1]);extra=iter(map(int,fields[2:]));out={}
                for i,(u,v) in enumerate(es):
                    if mask>>u&1 and mask>>v&1:out[i]=next(extra)
                pool.append((fields[0],a,es,mask,out))
    rng=random.Random(320032);hist={};records=[]
    for _ in range(2048):
        rows=[rng.choice(pool),rng.choice(pool)];indices=[rng.randrange(33),rng.randrange(33)]
        active=[indices[j] in rows[j][4] for j in range(2)]
        choose_in=max((j for j in range(2) if active[j]),key=lambda j:rows[j][3].bit_count(),default=-1)
        whole=[set() for _ in range(46)];selected=set()
        for j,(_,adj,es,mask,out) in enumerate(rows):
            edge=es[indices[j]];root=23*j+22
            for v,ns in enumerate(adj):
                for u in ns:
                    if {u,v}!=set(edge):whole[23*j+v].add(23*j+u)
            for v in edge:whole[root].add(23*j+v);whole[23*j+v].add(root)
            chosen=(mask|(1<<22)) if j==choose_in else (out[indices[j]] if active[j] else mask)
            selected.update(23*j+v for v in range(23) if chosen>>v&1)
        whole[22].add(45);whole[45].add(22)
        assert all(len(ns)==3 for ns in whole)
        assert len(selected)>=23 and all(len(whole[v]&selected)==2 for v in selected)
        hist[len(selected)]=hist.get(len(selected),0)+1
        records.append(dict(parents=[r[0] for r in rows],edges=[rows[j][2][indices[j]] for j in range(2)],selected=sorted(selected)))
    result=dict(checked_mixed_joins=len(records),order=46,witness_size_histogram=hist,scope='Direct check of explicit mixed-join witnesses; arbitrary mixed joins in the certified family follow from the proved bridge formula.')
    (DATA/'mixed_join_witnesses.json').write_text(json.dumps(records)+'\n')
    (ROOT/'round32_mixed_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('MIXED JOINS VERIFIED',len(records),hist,flush=True)

if __name__=='__main__':
    main()
    check_mixed_joins()
