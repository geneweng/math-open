import json
import random
import sys
from pathlib import Path

import networkx as nx
sys.path.insert(0,'cubic_conjecture_search/exploratory')
from weighted_oracle import test


def replace(base,choices,rng):
    result=nx.Graph();ports={};offset=0
    for v in base:
        graph=nx.from_graph6_bytes(choices[v].encode());deleted=rng.randrange(len(graph))
        ns=list(graph[deleted]);rng.shuffle(ns)
        graph.remove_node(deleted);mapping={u:offset+i for i,u in enumerate(graph)}
        result=nx.compose(result,nx.relabel_nodes(graph,mapping))
        for neighbor,old in zip(base[v],ns):ports[v,neighbor]=mapping[old]
        offset+=len(graph)
    result.add_edges_from((ports[u,v],ports[v,u]) for u,v in base.edges())
    return result


if __name__=='__main__':
    rng=random.Random(20261027);codes=json.loads(Path(__file__).with_name('critical_weighted_graphs.json').read_text())
    codes=codes['8']+codes['10']+codes['12'];records=[]
    for trial in range(120):
        base=nx.complete_graph(4) if trial<80 else nx.complete_bipartite_graph(3,3)
        choices=[rng.choice(codes) for v in base]
        g=replace(base,choices,rng)
        r=test(g);r['trial']=trial;r['order']=len(g)
        r['graph6']=nx.to_graph6_bytes(g,header=False).decode().strip();records.append(r)
        if trial%10==0 or r['status']!='no_weighted_violation':print(r,flush=True)
        Path('tmp/cubic_continue/weighted_assembly_results.json').write_text(json.dumps(records,indent=2))
        if r['status']=='weighted_counterexample':break
