import json,time
from pathlib import Path
NEG=-1000000
p=Path('cubic_conjecture_search');gens=[]
for line in (p/'two_pole_profiles.txt').read_text().splitlines():
 f=line.split();v=tuple(NEG if int(x)==NEG else int(x)//2 for x in f[3:]);gens.append(dict(profile=v,source=f[:3],flip=False));rev=(v[0],v[2],v[1],v[3],v[4])
 if rev!=v:gens.append(dict(profile=rev,source=f[:3],flip=True))
gens.extend([dict(profile=(-1,NEG,NEG,1,1),source='theta_direct_edge',flip=False), dict(profile=(-1,NEG,1,NEG,1),source='theta_branch_internal',flip=False), dict(profile=(-1,1,NEG,NEG,1),source='theta_branch_internal',flip=True), dict(profile=(1,NEG,NEG,NEG,1),source='theta_internal_internal',flip=False), dict(profile=(-1,0,0,1,NEG),source='two_disjoint_P13_caps',flip=False), dict(profile=(0,NEG,NEG,NEG,0),source='completed_cycle_edge',flip=False)])
gens.extend([dict(profile=(-1,NEG,3,NEG,-1),source='outside_core_62',flip=False),dict(profile=(-1,3,NEG,NEG,-1),source='outside_core_62',flip=True)])
gens.extend([dict(profile=(-2,0,2,NEG,0),source='outside_core_64',flip=False),dict(profile=(-2,2,0,NEG,0),source='outside_core_64',flip=True)])
gens.append(dict(profile=(-1,1,1,NEG,0),source='outside_census_64',flip=False))
def add(x,y):return NEG if x==NEG or y==NEG else x+y
def comp(a,b):return tuple(max(add(a[2*i+j],b[2*k+l]) for j in range(2) for k in range(2) if not j*k) for i in range(2) for l in range(2))+(add(a[4],b[4]),)
def le(a,b):return all(x<=y for x,y in zip(a,b))
active={};todo=[];nodes=[];start=time.time();attempts=0
for i,g in enumerate(gens):
 v=g['profile']
 if any(le(a,v) for a in active):continue
 for a in list(active):
  if le(v,a):del active[a]
 j=len(nodes);nodes.append(dict(profile=v,word=[i]));active[v]=j;todo.append(j)
head=0
while head<len(todo):
 if time.time()-start>45 or len(nodes)>20000:break
 j=todo[head];head+=1;node=nodes[j];a=node['profile']
 if a not in active:continue
 for i,g in enumerate(gens):
  b=comp(a,g['profile']);attempts+=1
  if max(b[0],b[1],b[2],b[4])<0:
   (p/'profile_scope/negative_word.json').write_text(json.dumps(dict(generators=gens,profile=b,word=node['word']+[i]),indent=2)+'\n');print('NEGATIVE',b,node['word']+[i],flush=True);raise SystemExit
  if any(le(c,b) for c in active):continue
  for c in list(active):
   if le(b,c):del active[c]
  q=len(nodes);nodes.append(dict(profile=b,word=node['word']+[i]));active[b]=q;todo.append(q)
 if head%100==0:print('progress',head,len(nodes),len(active),flush=True)
complete=head==len(todo)
result=dict(generators=gens,complete=complete,attempts=attempts,elapsed=time.time()-start,nodes=len(nodes),invariant=[nodes[j] for j in active.values()])
(p/'profile_scope/census_invariant.json').write_text(json.dumps(result,indent=2)+'\n');print('DONE',complete,len(nodes),len(active),attempts,time.time()-start,flush=True)
