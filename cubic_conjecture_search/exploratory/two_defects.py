from pathlib import Path
import json
import networkx as nx
records=[];total=0
for n in (4,6,8,10,12,14,16):
 for code in Path(f'tmp/cubic_full/cubic{n}.g6').read_text().splitlines():
  g=nx.from_graph6_bytes(code.encode());a=[sum(1<<u for u in g[v])for v in g];full=(1<<n)-1;near=[];perfect=False
  for s in range(1,1<<(n-1)):
   cross=[(a[v] & (full^s if s>>v&1 else s)).bit_count()for v in range(n)]
   if max(cross)>1:continue
   missing=[v for v,d in enumerate(cross)if d==0]
   if not missing:perfect=True;break
   if len(missing)==2:near.append((s,missing))
  total+=1
  if near and not perfect:
   rec={'graph6':code,'order':n,'near_partitions':near};records.append(rec);print('NO PERFECT EXTENSION',rec,flush=True)
   Path('tmp/cubic_round4/two_defect_obstructions.json').write_text(json.dumps(records,indent=2))
   if len(records)>=5:raise SystemExit
 print('checked',n,total,flush=True)
