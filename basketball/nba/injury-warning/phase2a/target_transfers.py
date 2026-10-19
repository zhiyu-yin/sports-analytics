"""Targeted ranges derived from observed roster transitions, never new prediction teams."""
from collections import defaultdict
import json
from .acquire import D,schedule

# Day-resolution trades from official 2023-24 tracker; later contracts use observed
# roster bounds and remain uncertain where the signing/waiver gap is unverified.
SPECS={
'1626166':[('MIL','2023-12-04','2024-02-07'),('PHI','2024-02-08','2024-04-14')],
'1627741':[('IND','2023-12-04','2024-02-07'),('PHI','2024-02-08','2024-04-14')],
'1628420':[('DET','2023-12-04','2024-02-06'),('MIN','2024-02-07','2024-04-14')],
'1628963':[('DET','2023-12-04','2024-01-13'),('WAS','2024-01-14','2024-04-14')],
'1630587':[('DET','2023-12-04','2024-01-13'),('WAS','2024-01-14','2024-04-14')],
'1628972':[('MIN','2023-12-04','2024-02-06'),('DET','2024-02-07','2024-04-14')],
'1629003':[('MIN','2023-12-04','2024-02-06'),('DET','2024-02-07','2024-03-01'),('NYK','2024-03-05','2024-04-14')],
'1630201':[('TOR','2023-12-04','2023-12-29'),('NYK','2023-12-30','2024-02-07'),('DET','2024-02-08','2024-04-14')],
'1630531':[('PHI','2023-12-04','2024-02-07'),('BOS','2024-02-08','2024-04-14')],
'1631323':[('UTA','2023-12-04','2024-02-07'),('DET','2024-02-08','2024-04-14')],
'201976':[('PHI','2023-12-04','2024-02-07'),('MIL','2024-02-08','2024-04-14')],
'202692':[('DET','2023-12-04','2024-02-07'),('NYK','2024-02-08','2024-04-14')],
'202694':[('PHI','2023-12-04','2024-02-07'),('SAS','2024-02-08','2024-02-29'),('CLE','2024-03-18','2024-04-14')],
'202711':[('DET','2023-12-04','2024-02-07'),('NYK','2024-02-08','2024-04-14')],
'203095':[('NYK','2023-12-04','2024-02-07'),('DET','2024-02-08','2024-04-14')],
'203926':[('SAS','2023-12-04','2024-02-07'),('IND','2024-02-08','2024-04-14')],
'201568':[('WAS','2023-12-04','2024-01-13'),('DET','2024-01-14','2024-02-08'),('MIL','2024-02-21','2024-04-14')],
'203488':[('WAS','2023-12-04','2024-01-13'),('DET','2024-01-14','2024-02-27'),('OKC','2024-03-02','2024-04-14')],
'1631254':[('MEM','2023-12-04','2023-12-17'),('PHI','2023-12-23','2024-03-01'),('UTA','2024-03-11','2024-04-14')],
'1641787':[('MEM','2024-01-30','2024-02-08'),('DET','2024-02-13','2024-04-14')],
'1629603':[('SAS','2024-01-01','2024-02-29'),('NYK','2024-03-14','2024-04-14')],
# Retrieve receiving-team evidence even when the player may have been waived
# before appearing. Unobserved roster games remain gaps, never injury absences.
'1628995':[('DET','2023-12-04','2024-02-07'),('UTA','2024-02-08','2024-02-10')],
'1627788':[('PHI','2023-12-04','2024-02-07'),('IND','2024-02-08','2024-02-10')],
'1627863':[('PHI','2023-12-04','2024-02-07'),('DET','2024-02-08','2024-02-08')],
}

def target():
    selected={r['team'] for r in json.loads((D/'registration/sample_v1.json').read_text())['selected']};spells=[];wanted=defaultdict(set);ss=schedule();lookup={(r['team'],r['game_id']):r for r in ss}
    for pid,seq in SPECS.items():
        for team,start,end in seq:
            spells.append(dict(player_id=pid,team=team,start=start,end=end,date_basis='official trade day plus observed roster bounds; later signing/waiver gaps not assumed complete',source_id='p2_trade_tracker' if len(seq)<=2 and start<='2024-02-08' else 'p2_trade_tracker; game roster locators in player_games',historical_availability='C; no automatic B departure exclusion'))
            if team not in selected:
                for g in ss:
                    if g['team']==team and start<=g['game_date']<=end:wanted[(team,g['game_id'])].add(pid)
    games=[dict(lookup[k],player_ids=sorted(v),scope='targeted_cross_team_only') for k,v in wanted.items()];(D/'membership_review_ranges.json').write_text(json.dumps(spells,indent=2)+'\n');(D/'targeted_team_games.json').write_text(json.dumps(games,indent=2)+'\n');req={}
    for g in games:
        a,b=g['matchup'].split(' @ ') if ' @ ' in g['matchup'] else g['matchup'].split(' vs. ')[::-1];gid=g['game_id'];ds=g['game_date'].replace('-','')
        for kind,url in [('page',f'https://www.nba.com/game/{a.lower()}-vs-{b.lower()}-{gid}/box-score'),('book',f'https://statsdmz.nba.com/pdfs/{ds}/{ds}_{a}{b}_book.pdf')]:req[kind+'_'+gid]=dict(source_id=kind+'_'+gid,date=g['game_date'],kind=kind,url=url)
    req['p2_trade_tracker']=dict(source_id='p2_trade_tracker',date='2024-03-13',kind='news',url='https://www.nba.com/news/2023-24-nba-trade-tracker')
    for sid,day,url in [('p2_lofton_uta','2024-03-11','https://www.nba.com/jazz/news/utah-jazz-sign-kenneth-lofton-jr'),('p2_muscala_okc','2024-03-02','https://www.nba.com/thunder/news/release-muscala-240302'),('p2_january_trade','2024-01-14','https://www.nba.com/wizards/news/wizards-acquire-bagley-iii-livers-from-detroit'),('p2_three_team','2024-02-08','https://www.nba.com/pacers/news/indiana-pacers-complete-three-team-trade')]:req[sid]=dict(source_id=sid,date=day,kind='news',url=url)
    
    for sid,day,url in [('p2_livers_update','2024-02-26','https://www.nba.com/wizards/news/wizards-injury-update-13'),('p2_melton_return','2024-02-23','https://www.hoopsrumors.com/2024/02/sixers-deanthony-melton-returns-after-lengthy-absence.html'),('p2_gary_return','2024-02-03','https://www.hoopsrumors.com/2024/02/magic-notes-suggs-banchero-harris.html')]:req[sid]=dict(source_id=sid,date=day,kind='news',url=url)
    req['report_2024-02-13_06PM']=dict(source_id='report_2024-02-13_06PM',date='2024-02-13',kind='report',url='https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-02-13_06PM.pdf')
    (D/'targeted_requests.json').write_text(json.dumps(list(req.values()),indent=2)+'\n');print('targeted team games',len(games),'reviewed player transitions',len(SPECS))
if __name__=='__main__':target()
