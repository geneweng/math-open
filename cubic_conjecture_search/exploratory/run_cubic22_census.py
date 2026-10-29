"""Generate disjoint geng shards and retain a good-set witness for every graph."""
import concurrent.futures
import json
import subprocess
import time
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
DATA=REPO/'cubic_conjecture_search/round30_data'
TMP=REPO/'tmp/cubic_round30'
START=time.monotonic()


def run(shard):
    out=DATA/f'certificates-{shard}.txt.gz'
    with (TMP/f'geng-{shard}.log').open('wb') as gl, (TMP/f'search-{shard}.log').open('wb') as sl, out.open('wb') as cert:
        gen=subprocess.Popen(['geng','-c','-d3','-D3','-X0','-x3200','22',f'{shard}/64'],stdout=subprocess.PIPE,stderr=gl)
        search=subprocess.Popen([str(TMP/'census'),'22',str(DATA/f'exceptions-{shard}.txt')],stdin=gen.stdout,stdout=subprocess.PIPE,stderr=sl)
        gen.stdout.close()
        compress=subprocess.Popen(['gzip'],stdin=search.stdout,stdout=cert)
        search.stdout.close()
        codes=[compress.wait(),search.wait(),gen.wait()]
    if any(codes):raise RuntimeError(f'shard {shard} exit codes {codes}')
    print('COMPLETE SHARD',shard,'elapsed',round(time.monotonic()-START,1),flush=True)
    return dict(shard=shard,exit_codes=codes)


def main():
    # Shard zero is the separately recorded pilot run, with identical X/x.
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(run,i):i for i in range(1,64)}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            (DATA/'generation_progress.json').write_text(json.dumps(sorted(results,key=lambda r:r['shard']),indent=2)+'\n')
    print('ALL REMAINING SHARDS COMPLETE',flush=True)


if __name__=='__main__':main()
