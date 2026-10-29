"""Independently check every certificate and audit all 64 generation shards.

Pass --watch while generation is active. Completeness relies on geng's
documented isomorph-free generation and disjoint res/mod partitioning.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'round30_data'
TMP=ROOT.parent/'tmp/cubic_round30'


def main():
    TMP.mkdir(parents=True,exist_ok=True)
    subprocess.run(['clang++','-O3','-std=c++17',str(ROOT/'exploratory/check_cubic_census.cpp'),
                    '-o',str(TMP/'check')],check=True)
    watch='--watch' in sys.argv;done={};start=time.monotonic()
    while len(done)<64:
        available={0}
        progress=DATA/'generation_progress.json'
        if progress.exists():
            try:available.update(r['shard'] for r in json.loads(progress.read_text()))
            except json.JSONDecodeError:pass
        for shard in sorted(available-set(done)):
            cert=DATA/f'certificates-{shard}.txt.gz'
            logs=DATA/'generation_logs'
            if not (logs/f'geng-{shard}.log').exists():logs=TMP
            gl=(logs/f'geng-{shard}.log').read_text();sl=(logs/f'search-{shard}.log').read_text()
            gen=re.search(r'>Z (\d+) graphs generated',gl)
            search=re.search(r'COMPLETE count (\d+) sharp (\d+)',sl)
            assert gen and search and 'X0x3200' in gl and f'class={shard}/64' in gl
            assert gen[1]==search[1]
            assert (DATA/f'exceptions-{shard}.txt').read_text()==''
            unzip=subprocess.Popen(['gzip','-dc',str(cert)],stdout=subprocess.PIPE)
            checker=subprocess.run([str(TMP/'check'),'22'],stdin=unzip.stdout,capture_output=True,text=True)
            unzip.stdout.close();assert unzip.wait()==0 and checker.returncode==0,checker.stderr
            (DATA/f'check-{shard}.txt').write_text(checker.stdout)
            lines=checker.stdout.splitlines();assert lines[0]==f'COUNT {gen[1]}'
            histogram={int(z.split()[1]):int(z.split()[2]) for z in lines[1:]}
            assert sum(histogram.values())==int(gen[1]) and min(histogram)>=12
            done[shard]=dict(shard=shard,count=int(gen[1]),witness_sizes=histogram,
                             sha256=hashlib.sha256(cert.read_bytes()).hexdigest(),
                             gzip_bytes=cert.stat().st_size)
            print('CHECKED',shard,'cumulative',sum(r['count'] for r in done.values()),flush=True)
        if len(done)==64:break
        if not watch:raise RuntimeError('Generation incomplete; no complete census claimed')
        if time.monotonic()-start>7200:raise RuntimeError('Generation wait exceeded two hours')
        time.sleep(2)
    total=sum(r['count'] for r in done.values());assert total==7319447
    histogram=Counter()
    for r in done.values():histogram.update(r['witness_sizes'])
    result=dict(original_conjecture='unresolved',order=22,graphs=total,shards=64,
                minimum_certified_size=min(histogram),witness_sizes=dict(histogram),
                generator='nauty 2.9.3 geng -c -d3 -D3 -X0 -x3200 22 r/64',
                published_count_source='https://houseofgraphs.org/Cubic',
                scope='Every retained witness independently degree-checked, including cubicity '
                      'and connectivity. Enumeration completeness relies on geng; all 64 shard '
                      'counts agree with generator logs and total agrees with the published census.',
                records=[done[i] for i in range(64)])
    (ROOT/'round30_census_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('COMPLETE CENSUS VERIFIED',total,flush=True)


if __name__=='__main__':main()
