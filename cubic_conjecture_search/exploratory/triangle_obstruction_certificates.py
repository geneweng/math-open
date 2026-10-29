"""Construct complementary good-set certificates for previously sharp records."""
import gzip,json,sys
from pathlib import Path
from ortools.sat.python import cp_model
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_round12 import decode
ROOT=Path(__file__).resolve().parents[1];records=[]
def partition(a,root=None):
 m=cp_model.CpModel();x=[m.new_bool_var(str(v)) for v in range(len(a))]
 for v in range(len(a)):m.add(sum(x[u] for u in a[v])==(2*x[v] if v==root else 1+x[v]))
 sol=cp_model.CpSolver();sol.parameters.num_search_workers=1;status=sol.solve(m)
 assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE)
 return [sol.value(t) for t in x]
codes=set()
for fn in ['descent_best.txt.gz','large_best.txt.gz']:
 for line in gzip.open(ROOT/'round18_data'/fn,'rt'):
  r=line.split();n=ord(r[0][0])-63
  if int(r[1])==n//2:codes.add(r[0])
for code in sorted(codes):
 a,_=decode(code);records.append(dict(kind='cubic',graph6=code,colours=partition(a)))
for r in json.loads((ROOT/'round13_verification.json').read_text())['search']['exact_checks']:
 a,_=decode(r['graph6']);q=len(a)
 if max(2*r['B'],r['A']+r['B'])==q:
  records.append(dict(kind='doubled_cap',graph6=r['graph6'],root=r['root'],colours=partition(a,r['root'])))
(ROOT/'round23_data/partitions.json').write_text(json.dumps(records,indent=2)+'\n');print('records',len(records))
