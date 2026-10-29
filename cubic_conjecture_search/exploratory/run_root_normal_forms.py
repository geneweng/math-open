import concurrent.futures,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'cubic_conjecture_search/round33_data';BIN=ROOT/'tmp/cubic_round33/root_normal_forms'
def run(n):
    with (DATA/f'geng-{n}.log').open('wb') as gl,(DATA/f'search-{n}.log').open('wb') as sl,(DATA/f'certificates-{n}.txt.gz').open('wb') as out:
        gen=subprocess.Popen(['geng','-c','-d3','-D3',str(n)],stdout=subprocess.PIPE,stderr=gl)
        solve=subprocess.Popen([str(BIN)],stdin=gen.stdout,stdout=subprocess.PIPE,stderr=sl);gen.stdout.close()
        zipproc=subprocess.Popen(['gzip','-1'],stdin=solve.stdout,stdout=out);solve.stdout.close()
        codes=[zipproc.wait(),solve.wait(),gen.wait()]
    if any(codes):raise RuntimeError((n,codes))
    print('COMPLETE',n,flush=True);return {'order':n,'exit_codes':codes}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(run,range(4,21,2)))
    (DATA/'generation.json').write_text(json.dumps(rows,indent=2)+'\n')
