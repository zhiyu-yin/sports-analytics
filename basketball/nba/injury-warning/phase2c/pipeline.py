"""Batch bindings for the frozen Phase 2A/2B pipeline, without copying algorithms."""
from contextlib import contextmanager
from pathlib import Path
from collections import Counter
import csv,json,hashlib,sys,time
from injury_warning.pilot_io import ROOT,now
from phase2a.acquire import read
from phase1d.acquire import manifest as foundational_manifest
from phase1d.acquire import schedule
D=ROOT/'phase2c';CACHE=ROOT/'data/raw/phase2c'
# Names affect extraction scope only, never prediction-team selection.
TEAM_LABELS={'ATL':'AtlantaHawks','BOS':'BostonCeltics','BKN':'BrooklynNets','CHA':'CharlotteHornets','CHI':'ChicagoBulls','CLE':'ClevelandCavaliers','DAL':'DallasMavericks','DEN':'DenverNuggets','DET':'DetroitPistons','GSW':'GoldenStateWarriors','HOU':'HoustonRockets','IND':'IndianaPacers','LAC':'LAClippers','LAL':'LosAngelesLakers','MEM':'MemphisGrizzlies','MIA':'MiamiHeat','MIL':'MilwaukeeBucks','MIN':'MinnesotaTimberwolves','NOP':'NewOrleansPelicans','NYK':'NewYorkKnicks','OKC':'OklahomaCityThunder','ORL':'OrlandoMagic','PHI':'Philadelphia76ers','PHX':'PhoenixSuns','POR':'PortlandTrailBlazers','SAC':'SacramentoKings','SAS':'SanAntonioSpurs','TOR':'TorontoRaptors','UTA':'UtahJazz','WAS':'WashingtonWizards'}
def registration():
    p=D/'registration/sample_v1.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==p.with_suffix('.sha256').read_text().strip();r=json.loads(p.read_text())
    return dict(r,history_start=r['dates']['history_start'],followup_end=r['dates']['followup_end'])
def verify():
    for p in (D/'registration').glob('*_v1.json'):assert hashlib.sha256(p.read_bytes()).hexdigest()==p.with_suffix('.sha256').read_text().strip(),p.name
    for name,h in json.loads((D/'registration/preserved_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for r in json.loads((D/'review_sources.json').read_text()) if (D/'review_sources.json').exists() else []:
        m=manifest()[r['source_id']];assert m['status']=='obtained';b=read(r['source_id'],manifest());assert all(t.lower() in b.decode().lower() for t in r.get('required_fragments',[])),r['source_id']
def manifest():
    sm=foundational_manifest()
    # Explicit historical ledger paths must never follow a rebound module D.
    for r in map(json.loads,(ROOT/'phase2a/source_manifest.jsonl').read_text().splitlines()):sm[r['source_id']]=r
    for r in json.loads((ROOT/'phase2b/source_manifest.json').read_text()):sm[r['source_id']]=r
    if (D/'source_manifest.jsonl').exists():
        for r in map(json.loads,(D/'source_manifest.jsonl').read_text().splitlines()):sm.setdefault(r['source_id'],r)
    return sm
def rows(name):
    with (D/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def write(name,records,fields=None):
    rr=list(records)
    if name=='roster_inventory':rr=[r for r in rr if r['team'] in {x['team'] for x in registration()['selected']}]
    if name=='negative_sample_review':rr=[dict(r,seed=20240219) for r in rr]
    if name=='events':rr=[dict(r,source_phase='phase2c_frozen_pipeline') for r in rr]
    p=D/'tables';p.mkdir(exist_ok=True);fields=fields or list(dict.fromkeys(k for r in rr for k in r)) or ['row_id']
    with (p/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
class ReportDir:
    def __truediv__(self,key):return ROOT/'phase2a/report_parser.py' if key=='report_parser.py' else D/key
class RawRoot:
    def __fspath__(self):return str(ROOT)
    def __truediv__(self,key):return ROOT/key.replace('data/raw/phase2a','data/raw/phase2c')
@contextmanager
def bindings():
    import phase2a.acquire as a,phase2a.prepare as p,phase2a.surveillance as s,phase2a.discover as dis
    import phase2b.build as b,phase2b.segments as seg,phase2b.clocks as clock
    changes=[]
    def patch(mod,**kw):
        for k,v in kw.items():changes.append((mod,k,getattr(mod,k)));setattr(mod,k,v)
    patch(a,D=D,CACHE=CACHE,LEDGER=D/'source_manifest.jsonl',manifest=manifest,registration=registration)
    patch(p,D=D,ROOT=RawRoot(),manifest=manifest,registration=registration,rows=rows,write=write,TEAM_LABELS=TEAM_LABELS)
    patch(s,D=ReportDir(),ROOT=RawRoot(),manifest=manifest,FOLLOWUP_LABELS=TEAM_LABELS)
    patch(dis,D=D,manifest=manifest,registration=registration)
    patch(seg,D=D,write=write)
    patch(clock,D=D,manifest=manifest,rows=rows,write=write)
    patch(b,D=D,manifest=manifest,registration=registration,rows=rows,write=write,TEAM_LABELS=TEAM_LABELS,FOLLOWUP_LABELS=TEAM_LABELS,verify_review_sources=verify)
    # Same frozen draw mechanism; batch-specific review sample seed was registered.
    class BatchRandom:
        def __getattr__(self,name):return getattr(__import__('random'),name)
        def Random(self,seed):return __import__('random').Random(20240219 if seed==20240218 else seed)
    patch(b,random=BatchRandom())
    try:yield
    finally:
        for mod,k,v in reversed(changes):setattr(mod,k,v)
def acquire():
    import phase2a.acquire as a
    with bindings():a.acquire()
def invalidate_report_cache():
    p=D/'parsed_reports.json'
    if not p.exists():return
    sm=manifest();rr=json.loads(p.read_text());kept=[r for r in rr if r.get('raw_source_sha256')==sm.get(r['source_id'],{}).get('sha256','') and r.get('retrieval_status')==sm.get(r['source_id'],{}).get('status')]
    p.write_text(json.dumps(kept,indent=2)+'\n')
def prepare():
    invalidate_report_cache()
    import phase2a.prepare as p
    with bindings():p.prepare()
    refresh()
def refresh():
    import phase2a.surveillance as s
    with bindings():s.refresh()
    sm=manifest();p=D/'parsed_reports.json';rr=json.loads(p.read_text())
    for r in rr:r['raw_source_sha256']=sm[r['source_id']].get('sha256','')
    p.write_text(json.dumps(rr,indent=2)+'\n')
def candidates():
    import phase2b.build as b,phase2b.segments as seg
    with bindings():
        seg.SEGMENTS.clear()
        seq,_=b.sequences([b.norm(r) for r in rows('player_games')],{r['game_id']:r for r in rows('game_timing')},json.loads((D/'membership_review_ranges.json').read_text()),schedule())
        b.build_events(seq,{})
def build():
    import phase2b.build as b
    from phase2b.knowledge import COMPLETIONS
    COMPLETIONS.clear()
    with bindings():b.build()
def clocks():
    import phase2b.clocks as c
    with bindings():c.audit()
def discover():
    import phase2a.discover as d
    with bindings():d.discover()
if __name__=='__main__':globals()[sys.argv[1]]()
