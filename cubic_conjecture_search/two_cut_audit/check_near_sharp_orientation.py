import json,networkx as nx,itertools
from pathlib import Path
raw=json.loads(Path('cubic_conjecture_search/extremal_audit/near_sharp_profiles.json').read_text());records=[];NEG=-1000000
for row in raw:
 g=nx.from_graph6_bytes(row['graph6'].encode());n=len(g);es=sorted(tuple(sorted(e)) for e in g.edges());lookup={e:i for i,e in enumerate(es)};adj=[sum(1<<u for u in g[v]) for v in g];scores=[[0,NEG,NEG,NEG,NEG] for e in es]
 for mask in range(1,1<<n):
  todo=mask;bad=[];ok=True
  while todo:
   bit=todo&-todo;todo-=bit;v=bit.bit_length()-1;d=(mask&adj[v]).bit_count()
   if d<2:ok=False;break
   if d==3:
    bad.append(v)
    if len(bad)>2:ok=False;break
  if not ok:continue
  size=mask.bit_count()
  if not bad:
   for i,(u,v) in enumerate(es):
    k=((mask>>u&1)<<1)|(mask>>v&1);k=4 if k==3 else k;scores[i][k]=max(scores[i][k],size)
  elif len(bad)==2 and tuple(bad) in lookup:
   i=lookup[tuple(bad)];scores[i][3]=max(scores[i][3],size)
 for e,sc in zip(es,scores):records.append(dict(graph6=row['graph6'],ports=e,order=n,maximum=row['maximum'],profile=sc))
print('records',len(records),flush=True)
def join(a,b):return max([a[4]+b[4]]+[a[i]+b[j] for i in range(4) for j in range(4) if not i&j])
for A in records:
 a=A['profile'];af=a.copy();af[1],af[2]=af[2],af[1]
 for B in records:
  b=B['profile'];x,y=join(a,b),join(af,b)
  if x!=y:
   out=dict(A=A,B=B,parallel=x,crossed=y);Path('cubic_conjecture_search/two_cut_audit/port_orientation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit
print('no orientation-sensitive pair')
