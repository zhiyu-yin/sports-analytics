"""Bounded 2023-24 transfer and deliberately selected fixture acquisition."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,urllib.request,csv
from injury_warning.pilot_io import ROOT,now
from phase1c.sources import manifest as prior_manifest,read as prior_read
D=ROOT/'phase1d'; CACHE=ROOT/'data/raw/phase1d'
def manifest():
    m=prior_manifest()
    if (D/'source_manifest.jsonl').exists():m.update({r['source_id']:r for r in map(json.loads,(D/'source_manifest.jsonl').read_text().splitlines())})
    return m

def read(sid):
    if sid in prior_manifest():return prior_read(sid)
    r=manifest()[sid]
    if r['status']!='obtained':return None
    b=(ROOT/r['raw_file']).read_bytes()
    assert hashlib.sha256(b).hexdigest()==r['sha256']
    return b

def schedule():
    base=ROOT.parent/'game-prediction/data/raw/2023-24'
    m=json.loads((base/'leaguegamelog_full_20260924T020737Z_45ca3b50.manifest.json').read_text());b=(base/m['raw_file']).read_bytes();assert hashlib.sha256(b).hexdigest()==m['sha256']
    raw=json.loads(b);rs=raw['resultSets'][0];records=[dict(zip(rs['headers'],v)) for v in rs['rowSet']]
    return [dict(game_id=r['GAME_ID'],game_date=r['GAME_DATE'][:10],team=r['TEAM_ABBREVIATION'],matchup=r['MATCHUP']) for r in records]

def catalog():
    s=schedule();selected=[]
    for r in s:
        d=r['game_date'];t=r['team'];role=None
        if t=='MEM' and '2024-02-08'<=d<='2024-04-14':role='transfer_Stevens'
        if t=='POR' and '2024-02-09'<=d<='2024-04-14':role='transfer_Banton'
        if t=='NYK' and d in ['2024-01-01','2024-01-13','2024-01-25','2024-01-27','2024-01-29']:role='fixture_Randle'
        if t=='CHA' and ('2023-11-10'<=d<='2023-11-28' or '2023-11-28'<=d<='2024-01-12'):role='fixture_Ball'
        if role:selected.append(dict(r,role=role))
    (D/'target_schedule.json').write_text(json.dumps(selected,indent=2)+'\n')
    req={}
    for g in selected:
        a,b=(g['matchup'].split(' @ ') if ' @ ' in g['matchup'] else g['matchup'].split(' vs. ')[::-1]);gid=g['game_id'];d=g['game_date']
        for kind,url in [('page',f'https://www.nba.com/game/{a.lower()}-vs-{b.lower()}-{gid}/box-score'),('book',f'https://statsdmz.nba.com/pdfs/{d.replace("-","")}/{d.replace("-","")}_{a}{b}_book.pdf')]:
            req[kind+'_'+gid]=dict(source_id=kind+'_'+gid,kind=kind,date=d,url=url)
    # Baseline and decision-day snapshot probes for selected fixture index dates.
    from datetime import date,timedelta
    indices=[g for g in selected if g['role'].startswith('fixture') and (g['team']=='NYK' or g['game_date']<='2023-11-26')]
    for g in indices:
        for offset in (0,1,2):
            d=(date.fromisoformat(g['game_date'])+timedelta(days=offset)).isoformat();sid='report_'+d+'_11AM';req[sid]=dict(source_id=sid,kind='report',date=d,url=f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{d}_11AM.pdf')
    (D/'request_catalog.json').write_text(json.dumps(list(req.values()),indent=2)+'\n');return list(req.values())+ (json.loads((D/'supplemental_requests.json').read_text()) if (D/'supplemental_requests.json').exists() else [])

def request(r):
    assert '2023-11-01'<=r['date']<='2024-04-14'
    receipt=dict(r,retrieved_at=now(),publication_at=None,evidence_category='C_until_explicit_B_assumption')
    try:
        with urllib.request.urlopen(urllib.request.Request(r['url'],headers={'User-Agent':'NBAInjuryFeasibilityResearch/0.1'}),timeout=22) as res:b=res.read(12000001);assert res.url==r['url'];receipt['http_status']=res.status
        assert len(b)<=12000000
        if r['kind'] in {'report','book'}:assert b.startswith(b'%PDF-')
        h=hashlib.sha256(b).hexdigest();CACHE.mkdir(parents=True,exist_ok=True);p=CACHE/(h+('.html' if r['kind'] in {'page','news'} else '.pdf'));p.write_bytes(b);receipt.update(status='obtained',sha256=h,raw_file=str(p.relative_to(ROOT)),bytes=len(b))
    except Exception as exc:receipt.update(status='failed',error=str(exc))
    return receipt

def acquire():
    m=manifest();todo=[r for r in catalog() if r['source_id'] not in m]
    with ThreadPoolExecutor(max_workers=4) as pool,(D/'source_manifest.jsonl').open('a') as f:
        for r in pool.map(request,todo):f.write(json.dumps(r)+'\n');f.flush()
    from collections import Counter
    print(Counter(r['status'] for r in manifest().values() if r['source_id'] in {x['source_id'] for x in todo}))
if __name__=='__main__':acquire()
