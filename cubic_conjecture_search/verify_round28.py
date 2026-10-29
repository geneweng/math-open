"""Reconstruct cyclic four-port assemblies and verify their good sets.

Transfer optimization is checked with Python integer dynamic programming;
every resulting whole-graph witness is checked by actual induced degrees.
"""
import itertools
import json
from pathlib import Path

from verify_round26 import read_rows
from verify_round12 import decode
from verify_round11 import graph6
from verify_bridge_reduction import edges, graph, good

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round28_data'
PERMS=list(itertools.permutations(range(4)))
STATES=[tuple(s//3**i%3 for i in range(4)) for s in range(81)]
MAPS=[[sum(z[p[i]]*3**i for i in range(4)) for z in STATES] for p in PERMS]


class Library:
    def __init__(self):
        self.raw=read_rows(ROOT/'round27_data/profiles.txt')
        self.reduced=json.loads((ROOT/'round27_data/canonical.json').read_text())['profiles']
        self.cache={}

    def item(self,index):
        if index in self.cache:return self.cache[index]
        r,p=divmod(index,24);reduced=self.reduced[r];raw=self.raw[reduced['row']]
        first=MAPS[PERMS.index(tuple(reduced['permutation']))];second=MAPS[p]
        mapping=[first[j] for j in second]
        f=[raw['values'][j] for j in mapping]
        ports=[raw['ports'][next(i for i in range(4) if mapping[3**j]==3**i)] for j in range(4)]
        transitions=[]
        for a in range(9):
            entries={}
            for state,val in enumerate(f):
                if val<=-1000000:continue
                digits=STATES[state]
                if not all((x==0 and y<=1) or (x==1 and y==0) or x==y==2
                           for x,y in zip((a%3,a//3),digits[:2])):continue
                b=state//9
                if b not in entries or val>entries[b][0]:entries[b]=(val,mapping[state])
            transitions.append(entries)
        a,_=decode(raw['code']);vs=sorted(set(range(len(a)))-set(raw['removed']))
        obj=dict(raw=raw,ports=ports,transitions=transitions,adj=a,vertices=vs)
        self.cache[index]=obj;return obj

    def optimize(self,word):
        best=None
        for start in range(9):
            dp={start:(0,[])}
            for idx in word:
                nxt={}
                for a,(value,path) in dp.items():
                    for b,(gain,source_state) in self.item(idx)['transitions'][a].items():
                        if b not in nxt or value+gain>nxt[b][0]:
                            nxt[b]=(value+gain,path+[source_state])
                dp=nxt
            if start in dp and (best is None or dp[start][0]>best[0]):best=dp[start]
        assert best is not None
        return best

    def build(self,word,source_states=None):
        es=[];ports=[];chosen=set();n=0
        for i,idx in enumerate(word):
            item=self.item(idx);vs=item['vertices'];ren={v:n+j for j,v in enumerate(vs)}
            es.extend((ren[u],ren[v]) for u,v in edges(item['adj']) if u in ren and v in ren)
            ports.append([ren[v] for v in item['ports']])
            if source_states is not None:
                mask=item['raw']['witnesses'][source_states[i]]
                chosen.update(ren[v] for v in vs if mask>>v&1)
            n+=len(vs)
        for i in range(len(word)):
            for j in range(2):es.append((ports[i][2+j],ports[(i+1)%len(word)][j]))
        a=graph(n,es);assert all(len(ns)==3 for ns in a)
        return a,chosen


def main():
    lib=Library();search=json.loads((DATA/'search.json').read_text());certs=[];sharp=[]
    seen=set()
    for i,r in enumerate(search['records']):
        value,states=lib.optimize(r['word'])
        assert value==r['doubled_surplus'] and value>=0
        a,chosen=lib.build(r['word'],states)
        assert good(a,chosen) and 2*len(chosen)-len(a)==value
        certs.append(dict(record=i,order=len(a),doubled_surplus=value,selected=sorted(chosen)))
        if value==0 and tuple(r['word']) not in seen:
            seen.add(tuple(r['word']))
            sharp.append(dict(record=i,word=r['word'],graph6=graph6(a),selected=sorted(chosen)))
    (DATA/'witnesses.json').write_text(json.dumps(certs,indent=2)+'\n')
    (DATA/'sharp.json').write_text(json.dumps(sharp,indent=2)+'\n')
    result=dict(original_conjecture='unresolved',verified_records=len(certs),
                distinct_sharp_words=len(sharp),min_order=min(r['order'] for r in certs),
                max_order=max(r['order'] for r in certs),
                coordinate_evaluations=search['coordinate_evaluations'],
                scope='All retained cyclic assemblies checked with independent integer DP '
                      'and direct whole-graph induced degrees. The search over assembly words is heuristic.')
    (ROOT/'round28_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
