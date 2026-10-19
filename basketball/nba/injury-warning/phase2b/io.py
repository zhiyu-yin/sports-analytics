"""Isolated Phase 2B outputs; Phase 2A raw cache and registrations are read-only."""
import csv,json
from injury_warning.pilot_io import ROOT
from phase2a.acquire import manifest,read,registration
from phase2a.prepare import TEAM_LABELS
D=ROOT/'phase2b'
def rows(name):
    with (D/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def write(name,records,fields=None):
    records=list(records);p=D/'tables';p.mkdir(exist_ok=True)
    fields=fields or list(dict.fromkeys(k for r in records for k in r)) or ['row_id']
    with (p/(name+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
def initialize():
    import shutil,hashlib
    hashes=json.loads((D/'registration/preserved_hashes.json').read_text())
    for name,h in hashes.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    (D/'tables').mkdir(exist_ok=True)
    for name in ['player_games','players','game_timing']:shutil.copyfile(ROOT/'phase2a/tables'/(name+'.csv'),D/'tables'/(name+'.csv'))
    for n in ['membership_review_ranges.json','episode_adjudications.json','recap_adjudications.json','parsed_reports.json','search_ledger.json']:shutil.copyfile(ROOT/'phase2a'/n,D/n)
if __name__=='__main__':initialize()

def verify_review_sources():
    """Fail closed when evidence used for new continuity assertions is unavailable."""
    import hashlib,re
    for p in (D/'registration').glob('*_v1.json'):
        h=p.with_suffix('.sha256')
        assert h.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h.read_text().strip(),p.name
    sm={r['source_id']:r for r in json.loads((D/'source_manifest.json').read_text())}
    expected={'p2b_strawther_return':['13 consecutive','cleared to play'],'p2b_cissoko_serial':['JANUARY 23, 2024','left ankle sprain','fifth game in a row'],'p2b_knox_waiver':['2024-02-09','waived'],'p2b_korkmaz_waiver':['2024-02-09','waived'],'p2b_nance_10day':['10-day'],'p2b_nance_2way':['2024-02-19','Two-Way']}
    for sid,need in expected.items():
        r=sm[sid];assert r['status']=='obtained',sid
        b=(ROOT/r['raw_file']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'],sid
        text=b.decode();assert all(s in text for s in need),sid
