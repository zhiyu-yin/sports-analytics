#!/usr/bin/env python3
"""Verify registration and development schedule, acquire explicit bounded sources."""
import argparse
from datetime import date,timedelta
import hashlib,json,csv
from pathlib import Path
from injury_warning.pilot_io import ROOT,retrieve


def schedule():
    registration=ROOT/'pilot/registration/design.json'
    if hashlib.sha256(registration.read_bytes()).hexdigest() != registration.with_suffix('.sha256').read_text().strip():
        raise ValueError('Registered design modified')
    design=json.loads(registration.read_text())
    source=ROOT.parent/'game-prediction/data/raw/2023-24'
    mpath=next(source.glob('leaguegamelog_full_*.manifest.json'))
    m=json.loads(mpath.read_text())
    if m['season']!='2023-24' or m['parameters']['PlayerOrTeam']!='T':raise ValueError('Wrong source')
    body=(source/m['raw_file']).read_bytes()
    if hashlib.sha256(body).hexdigest()!=m['sha256']:raise ValueError('Schedule hash mismatch')
    table=next(t for t in json.loads(body)['resultSets'] if t['name']=='LeagueGameLog')
    rows=[dict(zip(table['headers'],r)) for r in table['rowSet']]
    games=[]
    for g in rows:
        d=g['GAME_DATE'][:10]
        if str(g['TEAM_ID'])!=design['team_id'] or not design['history_start']<=d<=design['followup_end']:continue
        abbr=g['MATCHUP'][-3:];home='vs.' in g['MATCHUP']
        games.append(dict(game_id=g['GAME_ID'],game_date=d,home='BOS' if home else abbr,away=abbr if home else 'BOS',phase='history' if d<design['prediction_start'] else 'pilot' if d<=design['prediction_end'] else 'followup',source_id='local_2023_24_schedule',evidence_locator='LeagueGameLog row GAME_ID='+g['GAME_ID']+' TEAM_ID='+design['team_id']))
    games.sort(key=lambda g:(g['game_date'],g['game_id']))
    out=ROOT/'pilot/tables';out.mkdir(parents=True,exist_ok=True)
    with (out/'team_schedule.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(games[0]));w.writeheader();w.writerows(games)
    (ROOT/'pilot/schedule_provenance.json').write_text(json.dumps(dict(source_id='local_2023_24_schedule',url=m['url'],retrieved_at=m['retrieved_at_utc'],sha256=m['sha256'],publication_at=None,publication_precision='unverified_original_availability',local_manifest=str(mpath.relative_to(ROOT.parent.parent.parent.parent)),fields_used=['TEAM_ID','GAME_ID','GAME_DATE','MATCHUP'],notes='Only BOS records in registered development dates exported; no score/outcome fields retained.'),indent=2)+'\n')
    return games


def requests(games):
    result=[]
    def add(sid,url,kind,d,gid=''):
        result.append(dict(source_id=sid,url=url,kind=kind,date=d,game_id=gid))
    for g in games:
        gid=g['game_id'];d=g['game_date']
        add('box_'+gid,f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gid}.json','boxscore',d,gid)
        if g['phase']=='pilot':
            add('pbp_'+gid,f'https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{gid}.json','playbyplay',d,gid)
            for report_date,hour in [(d,'06PM'),((date.fromisoformat(d)+timedelta(days=1)).isoformat(),'11AM'),((date.fromisoformat(d)+timedelta(days=1)).isoformat(),'09AM')]:
                add('report_'+report_date+'_'+hour,f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{report_date}_{hour}.pdf','report',report_date)
    # Exact gamebook pattern verified by February 14 historical search result.
    for g in games:
        d=g['game_date'].replace('-','');add('book_'+g['game_id'],f"https://statsdmz.nba.com/pdfs/{d}/{d}_{g['away']}{g['home']}_book.pdf",'gamebook',g['game_date'],g['game_id'])
    for g in games:
        add('page_'+g['game_id'],f"https://www.nba.com/game/{g['away'].lower()}-vs-{g['home'].lower()}-{g['game_id']}/box-score",'game_page',g['game_date'],g['game_id'])
    for sid,url,d in [('tillman_trade','https://www.nba.com/celtics/news/press-release-20240207-boston-celtics-acquire-tillman','2024-02-07'),('springer_trade','https://www.nba.com/celtics/news/pressrelease-20240208-boston-celtics-acquire-springer','2024-02-08')]:add(sid,url,'team_release',d)
    add('roster_notes_may11','https://cdn.nba.com/teams/uploads/sites/1610612739/2024/05/240511-boscle-notes.pdf','team_notes','2024-05-11')
    return list({r['source_id']:r for r in result}.values())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fetch',action='store_true');p.add_argument('--probe',action='store_true');a=p.parse_args()
    games=schedule();rs=requests(games)
    if a.probe:
        rs=[r for r in rs if r['source_id'] in {'box_'+games[0]['game_id'],'box_'+next(g['game_id'] for g in games if g['phase']=='pilot'),'pbp_'+next(g['game_id'] for g in games if g['phase']=='pilot'),'report_2024-01-03_11AM','tillman_trade','springer_trade'} or r['kind']=='gamebook']
    (ROOT/'pilot/request_catalog.json').write_text(json.dumps(requests(games),indent=2)+'\n')
    rs=[r for r in rs if r['kind'] not in {'boxscore','playbyplay'} or r['source_id'] in __import__('injury_warning.pilot_io',fromlist=['manifest']).manifest()]
    print(json.dumps(dict(games=len(games),pilot_games=sum(g['phase']=='pilot' for g in games),retrieval=retrieve(rs,a.fetch)),indent=2))
