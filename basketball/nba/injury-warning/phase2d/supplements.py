"""Budgeted C-only continuity/membership supplements; same immutable receipt policy."""
import json,time
from .runtime import D,ROOT,SPEC,manifest,activity
from .sources import canonical_url
from phase2a import acquire as a

def fetch():
    req=json.loads((D/'supplement_requests.json').read_text());p=D/'source_manifest.jsonl';rr=[json.loads(l) for l in p.read_text().splitlines()];prior=json.loads((D/'global_receipts.json').read_text());seen={canonical_url(r['url']) for r in prior+rr};todo=[r for r in req if canonical_url(r['url']) not in seen]
    assert sum(r.get('scope')=='supplement' for r in rr)+len(todo)<=SPEC['budgets']['supplement_new_http']
    original=a.CACHE;a.CACHE=ROOT/'data/raw/phase2d'
    try:
        with activity('C_only_supplements'),p.open('a') as f:
            for q in todo:
                if q['url'].startswith('https://www.nba.com/'):
                    r=a.request(dict(q,scope='supplement'))
                else:
                    import phase2b.acquire as old
                    class RawRoot:
                        def __fspath__(self):return str(ROOT)
                        def __truediv__(self,key):return ROOT/key.replace('data/raw/phase2b','data/raw/phase2d')
                    original_root=old.ROOT;old.ROOT=RawRoot();start=time.monotonic()
                    try:r=old.fetch((q['source_id'],(q['date'],q['url'])))
                    finally:old.ROOT=original_root
                    r.update(kind='news',scope='supplement',request_seconds=time.monotonic()-start)
                f.write(json.dumps(r)+'\n');f.flush();print(r['source_id'],r['status'])
    finally:a.CACHE=original
if __name__=='__main__':fetch()
