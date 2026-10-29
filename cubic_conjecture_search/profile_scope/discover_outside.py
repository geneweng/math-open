import networkx as nx,random,json,time
from pathlib import Path
p=Path('cubic_conjecture_search');B=[x['profile'] for x in json.loads((p/'ring_closure/invariant.json').read_text())['invariant']];N=-1000000;rng=random.Random(20261029);start=time.time();checked=0
for trial in range(12000):
 b=rng.choice([2,4,6,8,10,12]);stubs=[v for v in range(b) for _ in range(3)];rng.shuffle(stubs);pairs=list(zip(stubs[::2],stubs[1::2]));g=nx.Graph();g.add_nodes_from(range(b));nextv=b
 for u,v in pairs:
  length=3 if u==v else rng.choice([1,1,2,3]);length=max(length,2) if g.has_edge(u,v) else length
  path=[u]+list(range(nextv,nextv+length-1))+[v];nextv+=length-1;g.add_edges_from(zip(path,path[1:]))
 if not nx.is_connected(g):continue
 es=sorted(tuple(sorted(e)) for e in g.edges());idx={e:i for i,e in enumerate(es)};basis=[]
 for cy in nx.cycle_basis(g):basis.append(sum(1<<idx[tuple(sorted(e))] for e in zip(cy,cy[1:]+cy[:1])))
 profiles=[[N]*5 for _ in es];F=0
 for z in range(1<<len(basis)):
  if z:F^=basis[(z&-z).bit_length()-1]
  S=0
  for i,(u,v) in enumerate(es):
   if F>>i&1:S|=(1<<u)|(1<<v)
  bad=[i for i,(u,v) in enumerate(es) if not(F>>i&1) and S>>u&1 and S>>v&1];score=(S&((1<<b)-1)).bit_count()-b//2
  if len(bad)==1:profiles[bad[0]][3]=max(profiles[bad[0]][3],score)
  elif not bad:
   for i,(u,v) in enumerate(es):
    state=4 if F>>i&1 else 2*(S>>u&1)+(S>>v&1);profiles[i][state]=max(profiles[i][state],score)
 checked+=1
 for e,profile in zip(es,profiles):
  if not any(all(x<=y for x,y in zip(q,profile)) for q in B):
   out=dict(core_graph6=nx.to_graph6_bytes(g,header=False).decode().strip(),branches=b,core_order=len(g),edge=e,profile=profile,checked=checked,trial=trial,elapsed=time.time()-start)
   (p/'profile_scope/outside_cone.json').write_text(json.dumps(out,indent=2)+'\n');print('OUTSIDE',json.dumps(out),flush=True);raise SystemExit
 if time.time()-start>45:print('LIMIT',checked,flush=True);break
else:print('NO OUTSIDE',checked,time.time()-start,flush=True)
