"""Explicit supplementary C-only sources via the existing Phase2B cache fetcher."""
from concurrent.futures import ThreadPoolExecutor
import json,time
from .pipeline import D,ROOT,RawRoot,manifest
SOURCES={
'c_vezenkov_return':('2024-03-31','https://www.foxsports.com/nba/aleksandar-vezenkov-player'),
'c_rose_return':('2024-02-02','https://www.foxsports.com/nba/derrick-rose-player?p=3'),
'c_rose_march_coach':('2024-03-29','https://sports.yahoo.com/two-key-memphis-grizzlies-reserves-194839213.html')}
class ReviewRoot(RawRoot):
    def __truediv__(self,key):return ROOT/key.replace('data/raw/phase2b','data/raw/phase2c')
def acquire():
    import phase2b.acquire as prior
    old=prior.ROOT;sm=manifest();prior.ROOT=ReviewRoot();started=time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(prior.fetch,[q for q in SOURCES.items() if q[0] not in sm]))
    finally:prior.ROOT=old
    with (D/'source_manifest.jsonl').open('a') as f:
        for x in r:x['kind']='news';x['C_only']=True;f.write(json.dumps(x)+'\n')
    print([(x['source_id'],x['status']) for x in r],round(time.monotonic()-started,2))
if __name__=='__main__':acquire()
