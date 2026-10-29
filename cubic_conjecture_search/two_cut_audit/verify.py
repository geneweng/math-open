"""Verify the endpoint-orientation example and its ring formula.

Local tables are independently enumerated over all vertex subsets.
Two 36-vertex optima are checked against saved cycle-space enumerations.
The general ring theorem is proved in RESULTS.txt, not by finite testing.
"""
import itertools
import json
from pathlib import Path
import sys
import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from verify_boundary_profiles import exact_table


def build(data, flags):
    h = nx.from_graph6_bytes(data['parent'].encode())
    u,v = data['ports']; h.remove_edge(u,v)
    n=len(h); k=len(flags); g=nx.Graph()
    g.add_nodes_from(range(n*k))
    for i in range(k):
        g.add_edges_from((a+n*i,b+n*i) for a,b in h.edges())
    for i in range(k):
        j=(i+1)%k
        right=(u if flags[i] else v)+n*i
        left=(v if flags[j] else u)+n*j
        g.add_edge(right,left)
    assert nx.is_connected(g) and all(d==3 for _,d in g.degree())
    return g


def transfer_optimum(flags):
    # Four closed boundary states; joining selected closed ports is forbidden.
    states=list(itertools.product((0,1),repeat=2))
    table=[9,9,11,11]
    def value(flag,state):
        left,right=state
        return table[2*right+left if flag else 2*left+right]
    best=8*len(flags)  # all-open channel
    for first in states:
        dp={first:value(flags[0],first)}
        for flag in flags[1:]:
            nxt={}
            for last,score in dp.items():
                for state in states:
                    if not(last[1] and state[0]):
                        nxt[state]=max(nxt.get(state,-1000000),score+value(flag,state))
            dp=nxt
        for last,score in dp.items():
            if not(last[1] and first[0]):best=max(best,score)
    return best


def main():
    data=json.loads((HERE/'orientation_family.json').read_text())
    table,witnesses=exact_table(data['parent'],data['ports'])
    assert table==[0,0,4,4,-2]
    assert [(x+18)//2 for x in table]==data['local_cardinalities']
    assert witnesses==data['local_witnesses']
    exact=[json.loads(l) for l in (HERE/'global_cycle_checks.jsonl').read_text().splitlines()]
    assert len(exact)==len(data['examples'])==2
    for example,result in zip(data['examples'],exact):
        g=build(data,example['flags'])
        code=nx.to_graph6_bytes(g,header=False).decode().strip()
        assert code==example['graph6']==result['graph6']
        assert result['maximum']==example['expected']==transfer_optimum(example['flags'])
        assert result['factors_checked']==524288
        mask=result['witness']; chosen={v for v in g if mask>>v&1}
        assert len(chosen)==result['maximum']
        assert all(len(set(g[v])&chosen)==2 for v in chosen)
    patterns=0
    for k in range(2,11):
        for flags in itertools.product((0,1),repeat=k):
            t=sum(flags[i]==1 and flags[(i+1)%k]==0 for i in range(k))
            assert transfer_optimum(flags)==11*k-2*t
            patterns+=1
    result=dict(local_subsets_checked=262144, exact_local_profile=data['local_cardinalities'],
                aggregate_profile=dict(U=11,T=8,W=9,parent_maximum=11),
                direct_36_vertex_optima=[r['maximum'] for r in exact],
                cyclic_orientation_patterns_checked=patterns,
                general_formula='c_ind=11*k-2*t; t counts preferred-port/preferred-port joins',
                original_conjecture='unresolved')
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
