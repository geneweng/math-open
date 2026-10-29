"""Independent boundary-formula and canonical-root certificate checks."""
import concurrent.futures,gzip,hashlib,json,re,subprocess
from pathlib import Path
from verify_round12 import decode
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round33_data';TMP=ROOT.parent/'tmp/cubic_round33'
COUNTS={4:1,6:2,8:5,10:19,12:85,14:509,16:4060,18:41301,20:510489}

def profile(a,r):
    masks=[sum(1<<v for v in ns) for ns in a];A=-1000000;B=C=0;closed=(1<<r)|masks[r]
    for s in range(1<<len(a)):
        if all((masks[v]&s).bit_count()==2 for v in range(len(a)) if s>>v&1):
            k=s.bit_count()
            if s>>r&1:A=max(A,k)
            else:B=max(B,k)
            if not(s&closed):C=max(C,k)
    return A,B,C

def expand(a,r):
    n=len(a);u,v=sorted(a[r]);b=[ns.copy() for ns in a]+[set(),set()]
    b[u].remove(r);b[v].remove(r);b[r]=set()
    for x,y in [(u,n),(n,n+1),(n+1,v),(r,n),(r,n+1)]:b[x].add(y);b[y].add(x)
    return b,r

def diamond(a,r):
    n=len(a);b=[ns.copy() for ns in a]+[set() for _ in range(4)]
    # New root n, triangle n,n+1,n+2; shared external neighbour n+3.
    for x,y in [(n,n+1),(n,n+2),(n+1,n+2),(n+1,n+3),(n+2,n+3),(n+3,r)]:b[x].add(y);b[y].add(x)
    return b,n

def formula_checks():
    cases=0
    for n in (4,6,8):
        codes=subprocess.check_output(['geng','-cq','-d3','-D3',str(n)],text=True).split()
        for code in codes:
            a,es=decode(code)
            for u,v in es:
                q=[ns.copy() for ns in a]+[{u,v}];q[u].remove(v);q[v].remove(u);q[u].add(n);q[v].add(n)
                A,B,C=profile(q,n);first,r=expand(q,n);p1=profile(first,r)
                assert p1==(C+3,max(B,A+1),B)
                second,r2=expand(first,r);p2=profile(second,r2)
                assert p2==(B+3,max(B,A+1,C+4),max(B,A+1))
                d=max(2*B,A+B);d2=max(2*p2[1],p2[0]+p2[1]);assert d<len(q) or d2>=len(second)
                h=(len(q)-1)//2
                if d>=len(q):assert (max(2*p1[1],p1[0]+p1[1])<len(first))==(B==h+1 and A<=h and C<=h-2)
                diam,dr=diamond(q,n);dp=profile(diam,dr);M=max(A,B)
                assert dp==(M+3,max(B+3,M),M)
                ext,er=expand(diam,dr);ep=profile(ext,er)
                assert ep[0]==M+3 and ep[1]==M+4
                cases+=1
    result=dict(exhaustive_rooted_inputs=cases,checks_per_input=['one expansion','two expansions','diamond extension','expanded diamond'],original_conjecture='unresolved')
    (ROOT/'round33_formula_verification.json').write_text(json.dumps(result,indent=2)+'\n');print('FORMULAS VERIFIED',cases,flush=True)

def check(n):
    p=DATA/f'certificates-{n}.txt.gz';dec=subprocess.Popen(['gzip','-dc',str(p)],stdout=subprocess.PIPE)
    proc=subprocess.run([str(TMP/'check_root_normal_forms'),str(n)],stdin=dec.stdout,capture_output=True,text=True);dec.stdout.close()
    assert dec.wait()==0 and proc.returncode==0,(n,proc.stderr)
    fields=proc.stdout.split();assert fields[::2]==['GRAPHS','TESTS'];graphs,tests=map(int,fields[1::2])
    assert graphs==COUNTS[n] and tests==3*n*graphs
    log=(DATA/f'search-{n}.log').read_text().splitlines()[-1].split();assert log==['COMPLETE',str(graphs),str(tests)]
    gen=(DATA/f'geng-{n}.log').read_text();assert re.search(r'>Z '+str(graphs)+r' graphs generated',gen)
    row=dict(order=n,graphs=graphs,rooted_tests=tests,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    print('CHECKED',n,graphs,tests,flush=True);return row

def main():
    subprocess.run(['clang++','-O3','-std=c++17',str(ROOT/'exploratory/check_root_normal_forms.cpp'),'-o',str(TMP/'check_root_normal_forms')],check=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,COUNTS))
    previous=json.loads((ROOT/'round32_verification.json').read_text());assert previous['graphs']==7319447
    # Require unchanged independently verified order-22 boundary certificates.
    for r in previous['shards']:
        p=ROOT/'round32_data'/f"certificates-{r['shard']}.txt.gz"
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
    result=dict(original_conjecture='unresolved',base_graphs=sum(r['graphs'] for r in rows),canonical_root_tests=sum(r['rooted_tests'] for r in rows),orders=rows,
                inherited_order22='All round32 certificate hashes match their independent verification record.',
                consequence='By the proved root normal form, every connected rooted fragment of order at most 23 has a symmetric double meeting half. All mixed joins of such fragments meet half. Every bridged counterexample has order at least 30.',
                limitation='Does not resolve bridgeless graphs or larger rooted obstructions. Census completeness relies on nauty geng.')
    (ROOT/'round33_verification.json').write_text(json.dumps(result,indent=2)+'\n');print('CANONICAL CHECKS COMPLETE',result['canonical_root_tests'],flush=True)
if __name__=='__main__':
    import sys
    if '--formulas' in sys.argv:formula_checks()
    else:main()
