"""Independent exhaustive checks of triangle identities and positive lifts."""
import json,subprocess
from pathlib import Path
from verify_round12 import decode
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round23_data'
def good(a,s):return all(len(a[v]&s)==2 for v in s)
def sets(a):
 n=len(a);masks=[sum(1<<u for u in ns) for ns in a];out=[]
 for s in range(1<<n):
  if all((s&masks[v]).bit_count()==2 for v in range(n) if s>>v&1):out.append(s)
 return out

def expand(a,v):
 n=len(a);h=[s.copy() for s in a]+[set(),set()];ns=sorted(a[v]);new=[v,n,n+1]
 for u in ns:h[u].remove(v)
 h[v]=set()
 for x,u in zip(new,ns):h[x].add(u);h[u].add(x)
 for x in new:
  for y in new:
   if x!=y:h[x].add(y)
 return h,new,ns

def main():
 bases=0;cases=0
 for n in [4,6,8,10]:
  lines=subprocess.check_output(['geng','-cq','-d3','-D3',str(n)],text=True).splitlines()
  for code in lines:
   a,_=decode(code);gs=sets(a);deleted={}
   for v in range(n):
    for u in a[v]:
     if u<v:continue
     b=[s.copy() for s in a];b[u].remove(v);b[v].remove(u);deleted[v,u]=sets(b)
   for v in range(n):
    B=max(s.bit_count() for s in gs if not(s>>v&1))
    closed=(1<<v)|sum(1<<u for u in a[v]);C=max(s.bit_count() for s in gs if not s&closed)
    D=max((s.bit_count() for u in a[v] for s in deleted[min(u,v),max(u,v)] if s>>v&1),default=-10000)
    h,_,_=expand(a,v);actual=max(s.bit_count() for s in sets(h));assert actual==max(B,C+3,D+1);cases+=1
   bases+=1
 recs=json.loads((DATA/'partitions.json').read_text());lifts=0;orders=[]
 for r in recs:
  a,_=decode(r['graph6']);x=r['colours'];q=len(a)
  if r['kind']=='doubled_cap':
   root=r['root'];a=[s.copy() for s in a]+[{u+q for u in s} for s in a]
   a[root].add(root+q);a[root+q].add(root);x=x+[1-t for t in x]
  n=len(a);assert all(len(ns)==3 for ns in a)
  S={v for v in range(n) if x[v]};T=set(range(n))-S
  assert len(S)==len(T)==n//2 and good(a,S) and good(a,T);orders.append(n)
  for v in range(n):
   h,new,ns=expand(a,v);base=S if v in S else T
   selected=(base-{v})|{w for w,u in zip(new,ns) if u in base}
   assert len(selected)==n//2+1 and good(h,selected);lifts+=1
 # Independently evaluate the proposed critical-star shortcut's small failure.
 code='M???FBOq@KF?D_B_?';a,_=decode(code);gs=sets(a);maximum=max(s.bit_count() for s in gs);profiles=[]
 for v in range(len(a)):
  for u in a[v]:
   if u<v:continue
   b=[s.copy() for s in a];b[u].remove(v);b[v].remove(u);ms=sets(b);best=max(ms,key=int.bit_count)
   profiles.append(dict(edge=[v,u],maximum=best.bit_count(),witness=[j for j in range(len(a)) if best>>j&1]))
 stars=[v for v in range(len(a)) if all(next(r['maximum'] for r in profiles if r['edge']==sorted([u,v]))>maximum for u in a[v])]
 assert stars and maximum==8
 result=dict(original_conjecture_resolved=False,small_base_graphs=bases,exhaustive_triangle_identities=cases,
  complementary_partition_records=len(recs),source_order_range=[min(orders),max(orders)],explicit_triangle_lifts=lifts,
  critical_star_auxiliary_example=dict(graph6=code,order=len(a),maximum=maximum,vertices=stars,edge_profiles=profiles),
  limitation='The critical-star example refutes only an auxiliary shortcut and satisfies the original bound.')
 (ROOT/'round23_verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='critical_star_auxiliary_example'}));print('critical star vertices',stars)
if __name__=='__main__':main()
