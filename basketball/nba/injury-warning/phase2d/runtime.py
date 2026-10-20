"""Scoped reuse of audited algorithms, global immutable cache, finite activity budgets."""
import csv,json,hashlib,time,sys,subprocess,os
from pathlib import Path
from contextlib import contextmanager
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from injury_warning.pilot_io import ROOT,now
from .audit import D,write as csvwrite
from .sources import canonical_url,catalog
SPEC=json.loads((D/'registration/scope_v1.json').read_text());BATCH=int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 1

def bd(n=None):return D/('batch'+str(n or BATCH))
def rows(name):
    with (bd()/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def write(name,records,fields=None):
    rr=list(records)
    if name=='roster_inventory':rr=[r for r in rr if r['team'] in {t['team'] for t in SPEC['batches'][BATCH-1]}]
    if name=='negative_sample_review':rr=[dict(r,seed=20240220) for r in rr]
    if name=='events':
        limits=json.loads((bd()/'identity_limitations.json').read_text()) if (bd()/'identity_limitations.json').exists() else {}
        rr=[dict(r,source_phase='phase2d_batch'+str(BATCH),continuity_review_note=(r.get('continuity_review_note','')+' '+limits.get(r['player_id']+'_'+r['anchor_date'],'' )).strip()) for r in rr]
    p=bd()/'tables'/(name+'.csv');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(dict.fromkeys(k for r in rr for k in r)) or ['row_id']);w.writeheader();w.writerows(rr)
def verify():
    p=D/'registration/scope_v1.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==p.with_suffix('.sha256').read_text().strip()
    for name,h in json.loads((D/'registration/preserved_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name

def manifest():
    rr=json.loads((D/'global_receipts.json').read_text())
    with (D/'global_source_index.csv').open() as f:index=list(csv.DictReader(f))
    rid={r['receipt_id']:r for r in rr};selected={r['canonical_url']:rid[r['selected_receipt_id']] for r in index if r['selected_receipt_id']};fails={r['canonical_url']:r for r in rr if not r['usable']}
    p=D/'source_manifest.jsonl'
    new=[json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    for r in new:
        url=canonical_url(r['url'])
        if r['status']=='obtained':selected.setdefault(url,r)
        else:fails[url]=r
    sm={}
    for r in rr+new:sm[r['source_id']]=dict(selected.get(canonical_url(r['url']),fails.get(canonical_url(r['url']),r)))
    req,_=catalog([t['team'] for t in SPEC['remaining_sorted']])
    for f in sorted(D.glob('batch*/targeted_requests.json')):req+=json.loads(f.read_text())
    for r in req:
        url=canonical_url(r['url']);chosen=selected.get(url,fails.get(url))
        if chosen:sm[r['source_id']]=dict(chosen,source_id=r['source_id'],date=r['date'],kind=r['kind'])
    return sm

@contextmanager
def activity(operation):
    start=time.monotonic();state='failed'
    try:yield;state='completed'
    finally:
        p=D/'activity.jsonl'
        with p.open('a') as f:f.write(json.dumps(dict(operation=operation,batch=BATCH,ended_at=now(),elapsed_machine_seconds=round(time.monotonic()-start,4),status=state,independent_human_seconds=0,agent_activity_seconds=None,agent_instrumentation='operation wall time only, not exclusive cognitive labor'))+'\n')

@contextmanager
def bindings():
    import phase2c.pipeline as c
    changes=[]
    def patch(mod,**kw):
        for k,v in kw.items():changes.append((mod,k,getattr(mod,k)));setattr(mod,k,v)
    def registration():return dict(selected=SPEC['batches'][BATCH-1],history_start='2023-12-04',followup_end='2024-04-14')
    class RawRoot:
        def __fspath__(self):return str(ROOT)
        def __truediv__(self,key):return ROOT/key.replace('data/raw/phase2a','data/raw/phase2d/batch'+str(BATCH))
    patch(c,D=bd(),CACHE=ROOT/'data/raw/phase2d',manifest=manifest,registration=registration,verify=verify,rows=rows,write=write)
    try:
        with c.bindings():
            mark=len(changes)
            try:
                import phase2a.prepare as p,phase2a.surveillance as s,phase2b.build as b,phase2b.clocks as clocks
                from .clockcache import book_clocks
                patch(clocks,book_clocks=book_clocks)
                patch(p,ROOT=RawRoot());patch(s,ROOT=RawRoot())
                if os.environ.get('PHASE2D_SUFFIX_FIX','1')=='1':
                    from .names import name_key
                    patch(p,canonical=name_key);patch(b,canonical=name_key)
                class Random:
                    def Random(self,seed):return __import__('random').Random(20240220 if seed==20240218 else seed)
                patch(b,random=Random())
                yield c
            finally:
                for mod,k,v in reversed(changes[mark:]):setattr(mod,k,v)
                del changes[mark:]
    finally:
        for mod,k,v in reversed(changes):setattr(mod,k,v)

def initialize():
    bd().mkdir(exist_ok=True);(ROOT/'data/raw/phase2d'/('batch'+str(BATCH))).mkdir(parents=True,exist_ok=True)
    req,games=catalog([t['team'] for t in SPEC['batches'][BATCH-1]])
    (bd()/'team_schedule.json').write_text(json.dumps(games,indent=2)+'\n');(bd()/'request_catalog.json').write_text(json.dumps(list({r['source_id']:r for r in req}.values()),indent=2)+'\n')
    (bd()/'targeted_requests.json').write_text('[]\n') if not (bd()/'targeted_requests.json').exists() else None
    for f,default in [('membership_review_ranges.json',[]),('episode_adjudications.json',{}),('recap_adjudications.json',[]),('segment_reviews.json',{})]:
        p=bd()/f
        if not p.exists():p.write_text(json.dumps(default)+'\n')
    (bd()/'review_metadata.json').write_text(json.dumps(dict(retrospective_reviewed_at=now(),reviewer='Codex same agent; not human'))+'\n')

def acquire():
    verify();p=D/'source_manifest.jsonl';old=[json.loads(l) for l in p.read_text().splitlines()] if p.exists() else [];seen={canonical_url(r['url']) for r in json.loads((D/'global_receipts.json').read_text())}|{canonical_url(r['url']) for r in old}
    req,_=catalog([t['team'] for t in SPEC['remaining_sorted']]);req={canonical_url(r['url']):r for r in req};todo=[r for u,r in req.items() if u not in seen]
    assert len(old)+len(todo)<=SPEC['budgets']['core_new_http']+SPEC['budgets']['supplement_new_http']
    assert sum(r.get('scope')=='core' for r in old)+len(todo)<=SPEC['budgets']['core_new_http']
    import phase2a.acquire as a
    original=a.CACHE;a.CACHE=ROOT/'data/raw/phase2d'
    try:
        with activity('core_http_acquisition'),ThreadPoolExecutor(max_workers=6) as pool,p.open('a') as f:
            for r in pool.map(a.request,todo):f.write(json.dumps(r)+'\n');f.flush()
    finally:a.CACHE=original
    rr=[json.loads(l) for l in p.read_text().splitlines()];summary=dict(actual_http=len(rr),statuses=dict(Counter(r['status'] for r in rr)),bytes=sum(r.get('bytes',0) for r in rr),sum_request_seconds=sum(r.get('request_seconds',0) for r in rr),duplicate_canonical_requests=len(rr)-len({canonical_url(r['url']) for r in rr}),core_budget=SPEC['budgets']['core_new_http'])
    (D/'actual_usage.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

def prepare():
    initialize()
    with activity('parse_full_batch'),bindings() as c:c.prepare()
    from .searches import ledger
    (bd()/'search_ledger.json').write_text(json.dumps(ledger(),indent=2)+'\n')

def clocks():
    with activity('audit_all_source_clocks'),bindings() as c:c.clocks()
def candidates():
    with activity('candidate_event_sequences'),bindings() as c:c.candidates()
def build():
    with activity('build_full_batch'),bindings() as c:c.build()
def audit_negatives():
    with activity('seeded_negative_original_source_reread'),bindings():
        from phase2c.audit_negatives import audit
        audit()
def packet():
    with bindings():
        from phase2c.report import prepare_review
        sm=manifest();sources={sid:dict(url=r.get('url',''),sha256=r.get('sha256',''),status=r['status']) for sid,r in sm.items()}
        oo={r['row_id']:r for r in rows('row_outcomes')}
        co=[dict(r,**{k:v for k,v in oo.get(r['row_id'],{}).items() if k not in r}) for r in rows('cohort_all_roster_candidates')]
        prepare_review(co,rows('events'),sources)
        p=bd()/'human_review_packet.md'
        p.write_text(p.read_text().replace('all60','all'+str(len(rows('negative_sample_review')))))
if __name__=='__main__':globals()[sys.argv[1]]()
