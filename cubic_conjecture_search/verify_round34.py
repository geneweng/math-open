"""Independent parent-profile identities and cycle-space audits of search candidates."""
import json,subprocess
from pathlib import Path
from verify_round12 import decode
from verify_round23 import sets
from verify_round33 import profile,expand
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round34_data';NEG=-1000000

def formulas():
    count=bridges=0
    for n in (4,6,8,10):
        for code in subprocess.check_output(['geng','-cq','-d3','-D3',str(n)],text=True).split():
            a,es=decode(code);gs=sets(a)
            for u,v in es:
                e=(1<<u)|(1<<v)
                T=max((s.bit_count() for s in gs if s&e==e),default=NEG)
                W=max(s.bit_count() for s in gs if not s&e)
                minus=[ns.copy() for ns in a];minus[u].remove(v);minus[v].remove(u)
                U=max(s.bit_count() for s in sets(minus))
                q=[ns.copy() for ns in minus]+[{u,v}];q[u].add(n);q[v].add(n)
                A,B,C=profile(q,n);assert (A,B,C)==((T+1 if T!=NEG else NEG),U,W)
                tri,r=expand(q,n);A1,B1,C1=profile(tri,r)
                assert (A1,B1,C1)==(W+3,max(U,T+2),U)
                seen={u};todo=[u]
                for x in todo:
                    for y in minus[x]-seen:seen.add(y);todo.append(y)
                if len(seen)<n:
                    pieces=[]
                    for verts,root in [(sorted(seen),u),(sorted(set(range(n))-seen),v)]:
                        ix={x:i for i,x in enumerate(verts)};p=[{ix[y] for y in minus[x]} for x in verts];pa,pb,_=profile(p,ix[root]);pieces.append((max(pa,pb),pb,len(p)))
                    assert T==NEG and U==sum(t[0] for t in pieces) and W==sum(t[1] for t in pieces)
                    if all(M+bb>=size for M,bb,size in pieces):
                        assert 2*B>=len(q) and max(2*B1,A1+B1)>=len(tri)
                    bridges+=1
                count+=1
    result=dict(exact_parent_edge_identities=count,bridge_cases=bridges,original_conjecture='unresolved')
    (ROOT/'round34_formula_verification.json').write_text(json.dumps(result,indent=2)+'\n');print('FORMULAS',result,flush=True)

def cycle_space_profile(a,r,collect=False):
    n=len(a);es=[(u,v) for v in range(n) for u in a[v] if u<v];incident=[[] for _ in a]
    for j,(u,v) in enumerate(es):incident[u].append((v,j));incident[v].append((u,j))
    parent=[-1]*n;pe=[-1]*n;dep=[0]*n;parent[0]=0;queue=[0];tree=set()
    for u in queue:
        for v,j in incident[u]:
            if parent[v]>=0:continue
            parent[v]=u;pe[v]=j;dep[v]=dep[u]+1;tree.add(j);queue.append(v)
    assert len(queue)==n
    basis=[]
    for j,(u,v) in enumerate(es):
        if j in tree:continue
        cycle={j};x,y=u,v
        while x!=y:
            if dep[x]>=dep[y]:cycle.add(pe[x]);x=parent[x]
            else:cycle.add(pe[y]);y=parent[y]
        basis.append(sorted(cycle))
    adj=[sum(1<<u for u in ns) for ns in a];closed=(1<<r)|adj[r]
    selected=0;on=[False]*len(es);degree=[0]*n;A=NEG;B=C=0;wa=wb=wc=0;goods=[]
    for k in range(1<<len(basis)):
        if k:
            bit=(k&-k).bit_length()-1
            for j in basis[bit]:
                delta=-1 if on[j] else 1;on[j]=not on[j]
                for v in es[j]:
                    degree[v]+=delta
                    if degree[v]:selected|=1<<v
                    else:selected&=~(1<<v)
        assert all(d in (0,2) for d in degree)
        if not all((adj[v]&selected).bit_count()==2 for v in range(n) if selected>>v&1):continue
        size=selected.bit_count()
        if collect:goods.append(selected)
        if selected>>r&1:
            if size>A:A=size;wa=selected
        elif size>B:B=size;wb=selected
        if not selected&closed and size>C:C=size;wc=selected
    result=dict(A=A,B=B,C=C,witnesses=dict(A=wa,B=wb,C=wc),cycle_vectors=1<<len(basis))
    if collect:result['good_masks']=goods
    return result

def audit_search():
    raw=json.loads((DATA/'synthesis.json').read_text());records=[]
    seed,_=decode(raw['seed']);seed_edges={(u,v) for u in range(25) for v in seed[u] if u<v}
    seed_profile=cycle_space_profile(seed,0,True)
    forbidden=lambda s: (s&1 and s.bit_count()>=13) or (not s&1 and s.bit_count()>=14) or (not s&7 and s.bit_count()>=11)
    cuts={s for s in seed_profile.pop("good_masks") if forbidden(s)}
    assert len(cuts)==raw["initial_cuts"]
    seed_row=json.loads((DATA/'seed.json').read_text())
    assert all(seed_profile[k]==seed_row[k] for k in ('A','B','C'))
    for row in raw['records']:
        a,_=decode(row['graph6']);assert len(a)==25 and a[0]=={1,2} and 2 not in a[1]
        assert all(len(ns)==(2 if v==0 else 3) for v,ns in enumerate(a))
        seen={1};todo=[1]
        for x in todo:
            for y in a[x]-seen-{0}:seen.add(y);todo.append(y)
        assert len(seen)==24
        current={(u,v) for u in range(25) for v in a[u] if u<v}
        assert len(seed_edges-current)==len(current-seed_edges)<=raw['radius']
        for mask in row['violating_masks']:
            assert mask>>25==0 and all(sum(mask>>u&1 for u in a[v])==2 for v in range(25) if mask>>v&1)
            assert (mask&1 and mask.bit_count()>=13) or (not mask&1 and mask.bit_count()>=14) or (not mask&7 and mask.bit_count()>=11)
        for key,mask in row['witnesses'].items():
            if not mask:continue
            assert mask>>25==0 and all(sum(mask>>u&1 for u in a[v])==2 for v in range(25) if mask>>v&1)
            assert (mask&1) if key=='A' else not(mask&1)
            if key=='C':assert not(mask&7)
        p=cycle_space_profile(a,0,True)
        expected={s for s in p.pop("good_masks") if forbidden(s)}
        assert set(row["violating_masks"])==expected
        cuts.update(expected)
        for key in ('A','B','C'):assert p[key]<=row['upper_bounds'][key]
        A,B,C=p['A'],p['B'],p['C'];d0=max(2*B,A+B);bp=max(B,A+1);d1=max(2*bp,C+3+bp)
        records.append(dict(graph6=row['graph6'],profile=p,double_optimum=d0,expanded_double_optimum=d1))
        if d0<25 or d1<27:print('INDEPENDENT COUNTEREXAMPLE',row['graph6'],d0,d1,flush=True)
    assert len(cuts)==raw['total_cuts']
    out=dict(verified_exclusion_constraints=len(cuts),search_status=raw['status'],root_order=25,radius=raw['radius'],independently_audited_candidates=len(records),records=records,
             seed_profile=seed_profile,counterexamples=sum(r['double_optimum']<25 or r['expanded_double_optimum']<27 for r in records),
             scope='Exact cycle-space audit of recorded candidates only. Does not certify exhaustion of the labelled search domain.')
    (ROOT/'round34_search_verification.json').write_text(json.dumps(out,indent=2)+'\n');print('AUDITED',len(records),'counterexamples',out['counterexamples'],flush=True)
if __name__=='__main__':
    import sys
    if '--search' in sys.argv:audit_search()
    else:formulas()
