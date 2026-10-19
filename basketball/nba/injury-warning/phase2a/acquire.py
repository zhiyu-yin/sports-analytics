"""Bounded, deduplicated, resumable selected-team 2023-24 public-source acquisition."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date,timedelta
from pathlib import Path
import json,hashlib,urllib.request,time
from injury_warning.pilot_io import ROOT,now
from phase1d.acquire import manifest as prior_manifest,read as prior_read,schedule
from .sampling import D
CACHE=ROOT/'data/raw/phase2a';LEDGER=D/'source_manifest.jsonl'

def registration():
    p=D/'registration/sample_v1.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==p.with_suffix('.sha256').read_text().strip()
    return json.loads(p.read_text())
def manifest():
    out=prior_manifest()
    if LEDGER.exists():out.update({r['source_id']:r for r in map(json.loads,LEDGER.read_text().splitlines())})
    return out

def read(sid,sm=None):
    sm=sm or manifest();r=sm[sid]
    if r['status']!='obtained':return None
    p=ROOT/r['raw_file'];b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'],sid
    return b

def catalog():
    reg=registration();teams={r['team'] for r in reg['selected']};games=[r for r in schedule() if r['team'] in teams and reg['history_start']<=r['game_date']<=reg['followup_end']]
    (D/'team_schedule.json').write_text(json.dumps(games,indent=2)+'\n');req={}
    for g in games:
        a,b=(g['matchup'].split(' @ ') if ' @ ' in g['matchup'] else g['matchup'].split(' vs. ')[::-1]);gid=g['game_id'];day=g['game_date'];ds=day.replace('-','')
        for kind,url in [('page',f'https://www.nba.com/game/{a.lower()}-vs-{b.lower()}-{gid}/box-score'),('book',f'https://statsdmz.nba.com/pdfs/{ds}/{ds}_{a}{b}_book.pdf')]:req[kind+'_'+gid]=dict(source_id=kind+'_'+gid,kind=kind,date=day,url=url)
        if '2024-01-01'<=day<='2024-02-18':
            sid='report_'+day+'_11PM';req[sid]=dict(source_id=sid,kind='report',date=day,url=f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{day}_11PM.pdf')
    day=date(2024,1,1)
    while day<=date(2024,3,3):
        ds=day.isoformat();sid='report_'+ds+'_11AM';req[sid]=dict(source_id=sid,kind='report',date=ds,url=f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{ds}_11AM.pdf');day+=timedelta(days=1)
    for r in json.loads((D/'targeted_requests.json').read_text()) if (D/'targeted_requests.json').exists() else []:req[r['source_id']]=r
    result=list(req.values());(D/'request_catalog.json').write_text(json.dumps(result,indent=2)+'\n');return result

def request(r):
    assert '2023-12-04'<=r['date']<='2024-04-14'
    assert r['url'].startswith(('https://www.nba.com/','https://statsdmz.nba.com/pdfs/','https://ak-static.cms.nba.com/referee/injury/','https://www.hoopsrumors.com/2024/02/'))
    receipt=dict(r,retrieved_at=now(),publication_at=None,evidence_category='C_until_explicit_B_assumption');start=time.monotonic()
    try:
        with urllib.request.urlopen(urllib.request.Request(r['url'],headers={'User-Agent':'NBAInjuryFeasibilityResearch/0.1'}),timeout=25) as res:b=res.read(12000001);assert res.url==r['url'];receipt['http_status']=res.status
        assert len(b)<=12000000
        if r['kind'] in {'book','report'}:assert b.startswith(b'%PDF-')
        h=hashlib.sha256(b).hexdigest();CACHE.mkdir(parents=True,exist_ok=True);p=CACHE/(h+('.pdf' if r['kind'] in {'book','report'} else '.html'));p.write_bytes(b);receipt.update(status='obtained',sha256=h,raw_file=str(p.relative_to(ROOT)),bytes=len(b))
    except Exception as exc:receipt.update(status='failed',error=str(exc))
    receipt['request_seconds']=round(time.monotonic()-start,3);return receipt

def acquire():
    sm=manifest();req=catalog();todo=[r for r in req if r['source_id'] not in sm];started=time.monotonic();n=0
    with ThreadPoolExecutor(max_workers=6) as pool,LEDGER.open('a') as f:
        for r in pool.map(request,todo):f.write(json.dumps(r)+'\n');f.flush();n+=1
    from collections import Counter
    summary=dict(request_catalog_unique=len(req),cached_reused=len(req)-len(todo),new_requests=len(todo),new_status=dict(Counter(r['status'] for r in map(json.loads,LEDGER.read_text().splitlines()))),last_acquisition_elapsed_seconds=round(time.monotonic()-started,2))
    (D/'acquisition_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':acquire()
