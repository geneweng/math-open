"""Extend the retained order-22 census with checkable edge-boundary witnesses."""
import concurrent.futures,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'cubic_conjecture_search/round32_data'
OLD=ROOT/'cubic_conjecture_search/round30_data'
BIN=ROOT/'tmp/cubic_round32/edge_half'

def run(i):
    with (DATA/f'search-{i}.log').open('wb') as log,(DATA/f'certificates-{i}.txt.gz').open('wb') as out:
        source=subprocess.Popen(['gzip','-dc',str(OLD/f'certificates-{i}.txt.gz')],stdout=subprocess.PIPE)
        search=subprocess.Popen([str(BIN)],stdin=source.stdout,stdout=subprocess.PIPE,stderr=log);source.stdout.close()
        compress=subprocess.Popen(['gzip','-1'],stdin=search.stdout,stdout=out);search.stdout.close()
        codes=[compress.wait(),search.wait(),source.wait()]
    if any(codes):raise RuntimeError(f'shard {i} failure {codes}')
    return dict(shard=i,exit_codes=codes)

def main():
    start=time.monotonic();rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(run,range(64)):
            rows.append(r);(DATA/'generation_progress.json').write_text(json.dumps(rows,indent=2)+'\n')
            print('COMPLETE',r['shard'],'seconds',round(time.monotonic()-start,1),flush=True)
    print('ALL COMPLETE',flush=True)
if __name__=='__main__':main()
