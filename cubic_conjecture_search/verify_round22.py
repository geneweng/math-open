"""Independent local enumeration, path/cycle DP, and full-graph witness checks."""
import json,itertools
from collections import Counter
from pathlib import Path
from verify_round12 import decode
from verify_bridge_reduction import graph,edges,franklin,cap
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'round22_data';K={(0,0),(0,1),(1,0),(2,2)}

def local(a,ports):
 values={};witnesses={}
 for mask in range(1<<len(a)):
  selected={v for v in range(len(a)) if mask>>v&1}
  if any(len(set(a[v])&selected) not in ([1,2] if v in ports else [2]) for v in selected):continue
  state=''.join(str(3-len(set(a[p])&selected)) if p in selected else '0' for p in ports)
  value=2*len(selected)-len(a)
  if value>values.get(state,-10000):values[state]=value;witnesses[state]=selected
 return values,witnesses

def expand(library,choices,pairs,states):
 a=[];ports=[]
 for rid in choices:
  r=library[rid];base,_=decode(r['graph6']);old=[v for v in range(len(base)) if v!=r['removed']];mp={v:len(a)+i for i,v in enumerate(old)}
  a.extend([{mp[u] for u in base[v] if u in mp} for v in old]);ports.extend(mp[v] for v in r['ports'])
 counts=Counter(x for pair in pairs for x in pair);assert counts==Counter({v:1 for v in range(3*len(choices))})
 for x,y in pairs:
  assert x//3!=y//3
  u,v=ports[x],ports[y];assert u!=v and v not in a[u];a[u].add(v);a[v].add(u)
 assert all(len(ns)==3 for ns in a)
 return a

def main():
 d=json.loads((DATA/'exception_decomposition.json').read_text());components=d['components']
 source,_=decode(d['source_graph6']);removed=d['removed'];seen_labels=set()
 for c in components:
  labels=c['source_labels'];assert not seen_labels&set(labels);seen_labels.update(labels)
  mp={v:i for i,v in enumerate(labels)}
  assert c['adjacency']==[sorted(mp[u] for u in source[v] if u!=removed) for v in labels]
  assert set(c['ports'])=={mp[v] for v in source[removed] if v in mp}
 assert seen_labels==set(range(len(source)))-{removed}
 q=graph(14,[e for e in edges(franklin()) if e!=(2,4)]+[(2,12),(12,13),(13,4)])
 for c in components:
  a=c['adjacency'];canonical=q if len(a)==14 else cap();mp=c['canonical_mapping'];assert set(mp)==set(range(len(a)))
  assert all(set(a[mp[v]])=={mp[u] for u in canonical[v]} for v in range(len(a)))
  f,w=local(a,c['ports']);assert f==c['values']
 assert next(c['values'] for c in components if c['order']==14)=={'00':-2,'11':2,'22':2}
 assert next(c['values'] for c in components if c['order']==13)=={'0':-1,'1':1}
 # Independent transfer computation for all paths/cycles through length 100.
 qstates=[(0,0,-2),(1,1,2),(2,2,2)];pstates=[(0,-1),(1,1)];checks=0
 for length in range(101):
  if length==0:path=max(x+y for a,x in pstates for b,y in pstates if (a,b) in K)
  else:
   dp={j:score+max(w for t,w in pstates if (t,a) in K) for j,(a,b,score) in enumerate(qstates) if any((t,a) in K for t,w in pstates)}
   for _ in range(1,length):
    dp={j:score+max(dp[i] for i in dp if (qstates[i][1],a) in K) for j,(a,b,score) in enumerate(qstates) if any((qstates[i][1],a) in K for i in dp)}
   path=max(value+w for i,value in dp.items() for t,w in pstates if (qstates[i][1],t) in K)
  assert path==0;checks+=1
  if length>=2:
   best=-10000
   for first,(_,_,value) in enumerate(qstates):
    dp={first:value}
    for _ in range(1,length):
     dp={j:score+max(dp[i] for i in dp if (qstates[i][1],a) in K) for j,(a,b,score) in enumerate(qstates) if any((qstates[i][1],a) in K for i in dp)}
    best=max(best,max((v for i,v in dp.items() if (qstates[i][1],qstates[first][0]) in K),default=-10000))
   assert best==2*length;checks+=1
 data=json.loads((DATA/'assemblies.json').read_text());statuses=Counter();orders=[];surpluses=[];uniform_formula=0
 for r in data['records']:
  statuses[r['status']]+=1
  if 'witness' not in r:continue
  a=expand(data['library'],r['choices'],r['pairs'],r['states']);s=set(r['witness'])
  assert len(s)==len(r['witness']) and all(0<=v<len(a) for v in s)
  assert all(len(a[v]&s)==2 for v in s)
  assert 2*len(s)-len(a)==r['score']>=0
  orders.append(len(a));surpluses.append(r['score'])
  if r.get('uniform') and data['library'][r['choices'][0]]['values'][0]==-3:
   # Components of the actual graph are paths or rings of Q fragments,
   # with P caps at the path ends. Cycle components contain no cap vertices.
   seen=set();cyclic_q=0;offset=0;cap_vertices=set()
   lib=data['library'][r['choices'][0]];base,_=decode(lib['graph6']);old=[v for v in range(len(base)) if v!=lib['removed']]
   psource=next(c['source_labels'] for c in components if c['order']==13)
   for _ in r['choices']:
    cap_vertices.update(offset+old.index(v) for v in psource);offset+=len(old)
   for v in range(len(a)):
    if v in seen:continue
    comp={v};todo=[v];seen.add(v)
    while todo:
     for u in a[todo.pop()]-seen:seen.add(u);comp.add(u);todo.append(u)
    if not comp&cap_vertices:assert len(comp)%14==0;cyclic_q+=len(comp)//14
   assert r['score']==2*cyclic_q;uniform_formula+=1
 result=dict(original_conjecture_resolved=False,local_subsets_enumerated=2**14+2**13,path_cycle_transfer_checks=checks,
   assembly_records=len(data['records']),status_counts=dict(statuses),full_graph_witnesses_checked=len(orders),
   order_range=[min(orders),max(orders)],minimum_witness_doubled_surplus=min(surpluses),uniform_formula_checks=uniform_formula,
   limitation='General mixed-assembly optimum claims are solver reports; positive witnesses are independently checked. Local tables and the path/cycle formula are independently verified.')
 (ROOT/'round22_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
