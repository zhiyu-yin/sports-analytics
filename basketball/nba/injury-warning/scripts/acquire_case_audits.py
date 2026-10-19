#!/usr/bin/env python3
"""Acquire development-only evidence for six selected external case reviews, separate from pilot."""
import argparse,json,hashlib
from injury_warning.pilot_io import ROOT,retrieve

CASES=[
 dict(case_id='A01',team='PHI',name='Joel Embiid',onset='2024-01-30',first_missed='2024-02-01',return_date='2024-04-02',last_missed='2024-03-31'),
 dict(case_id='A02',team='NYK',name='Julius Randle',onset='2024-01-27',first_missed='2024-01-29',return_date='',last_missed='2024-04-14'),
 dict(case_id='A03',team='CHA',name='LaMelo Ball',onset='2023-11-26',first_missed='2023-11-28',return_date='2024-01-12',last_missed='2024-01-10'),
 dict(case_id='A04',team='GSW',name='Stephen Curry',onset='2024-03-07',first_missed='2024-03-09',return_date='2024-03-16',last_missed='2024-03-13'),
 dict(case_id='A22',team='BOS',name='Al Horford',onset='',first_missed='2024-01-05',return_date='2024-01-06',last_missed='2024-01-05'),
 dict(case_id='A09',team='HOU',name='Alperen Sengun',onset='2024-03-10',first_missed='2024-03-12',return_date='',last_missed='2024-04-14')]


def request_list():
    source=ROOT.parent/'game-prediction/data/raw/2023-24';mp=next(source.glob('leaguegamelog_full_*.manifest.json'));m=json.loads(mp.read_text());body=(source/m['raw_file']).read_bytes()
    if m['season']!='2023-24' or hashlib.sha256(body).hexdigest()!=m['sha256']:raise ValueError('Wrong development source')
    table=next(t for t in json.loads(body)['resultSets'] if t['name']=='LeagueGameLog');allrows=[dict(zip(table['headers'],r)) for r in table['rowSet']]
    requests=[];case_schedule=[]
    for case in CASES:
        for row in allrows:
            d=row['GAME_DATE'][:10]
            if row['TEAM_ABBREVIATION']!=case['team']:continue
            if not ((case['first_missed']<=d<=case['last_missed']) or d in {case['onset'],case['return_date']}):continue
            gid=row['GAME_ID'];home=case['team'] if 'vs.' in row['MATCHUP'] else row['MATCHUP'][-3:];away=row['MATCHUP'][-3:] if 'vs.' in row['MATCHUP'] else case['team']
            case_schedule.append(dict(case_id=case['case_id'],team=case['team'],game_id=gid,game_date=d,source_id='local_2023_24_schedule',evidence_locator='LeagueGameLog game/team row'))
            if d in {case['onset'],case['return_date'],case['first_missed']}:
                requests.append(dict(source_id='page_'+gid,kind='game_page',date=d,game_id=gid,url=f'https://www.nba.com/game/{away.lower()}-vs-{home.lower()}-{gid}/box-score'))
            if case['case_id'] in {'A02','A04','A09'} or d==case['first_missed']:
                day=d.replace('-','');requests.append(dict(source_id='book_'+gid,kind='gamebook',date=d,game_id=gid,url=f'https://statsdmz.nba.com/pdfs/{day}/{day}_{away}{home}_book.pdf'))
    (ROOT/'pilot/case_audit_selection.json').write_text(json.dumps(CASES,indent=2)+'\n')
    (ROOT/'pilot/case_team_games.json').write_text(json.dumps(case_schedule,indent=2)+'\n')
    (ROOT/'pilot/case_request_catalog.json').write_text(json.dumps(requests,indent=2)+'\n')
    return requests


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fetch',action='store_true');a=p.parse_args();print(json.dumps(retrieve(request_list(),a.fetch),indent=2))
