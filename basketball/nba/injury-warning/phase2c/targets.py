"""Reviewed membership data and actual-team schedules; no new prediction teams."""
from collections import defaultdict
import json
from .pipeline import D,ROOT,registration,rows,schedule,manifest,read
NEWS=[
('c_knicks_dec_trade','2023-12-30','https://www.nba.com/news/raptors-knicks-trade-og-anunoby-rj-barrett'),
('c_dallas_trades','2024-02-08','https://www.nba.com/mavs/mavs-trades'),
('c_okc_trade','2024-02-08','https://www.nba.com/thunder/news/acquires-hayward-240208'),
('c_biyombo_waive','2024-01-10','https://www.nba.com/grizzlies/news/memphis-grizzlies-sign-vince-williams-jr-to-multi-year-contract'),
('c_biyombo_sign','2024-02-10','https://www.nba.com/news/thunder-sign-bismack-biyombo'),
('c_gilyard_sign','2024-03-02','https://www.nba.com/nets/news/brooklyn-nets-sign-jacob-gilyard-to-two-way-contract'),
('c_jemison_2way','2024-02-09','https://www.nba.com/grizzlies/news/memphis-grizzlies-sign-trey-jemison-to-two-way-contract'),
('c_hurt_10day','2024-01-29','https://www.nba.com/grizzlies/news/grizzlies-sign-matthew-hurt-to-10-day-contract'),
('c_taj_10day','2024-01-30','https://www.nba.com/knicks/news/knicks-sign-taj-gibson-to-10-day-contract'),
('c_toscano_10day','2024-01-09','https://www.nba.com/kings/news/kings-sign-juan-toscano-anderson-to-10-day-contract'),
('c_mills_waiver','2024-02-29','https://www.nba.com/news/hawks-waive-patty-mills'),
('c_mills_sign','2024-03-06','https://www.nba.com/heat/news/heat-sign-patty-mills'),
('c_poku_waiver','2024-02-23','https://www.nba.com/thunder/news/release-pokusevski-240223'),
('c_poku_sign','2024-02-28','https://www.nba.com/hornets/news/charlotte-hornets-sign-aleksej-pokusevski'),
('c_gilyard_waiver','2024-02-24','https://www.nba.com/grizzlies/news/memphis-grizzlies-sign-jordan-goodwin-to-two-way-contract'),
('c_jemison_was','2024-01-20','https://www.nba.com/wizards/news/wizards-sign-trey-jemison-to-10-day-contract'),
('c_mem_jan30','2024-01-30','https://www.nba.com/grizzlies/news/grizzlies-sign-tosan-evbuomwan-and-trey-jemison-to-10-day-contracts'),
('c_goodwin_10day','2024-02-13','https://www.nba.com/grizzlies/news/grizzlies-sign-jordan-goodwin-to-10-day-contract'),
('c_taj_waiver_REJECTED_WRONG_YEAR;last_observed_roster_only','2024-01-07','https://www.nba.com/knicks/news/knicks-waive-taj-gibson'),
('c_krejci_sign','2023-12-22','https://www.nba.com/hawks/news/atlanta-hawks-sign-forward-vit-krejci-to-two-way-contract'),
('c_brandon_sign','2023-12-28','https://www.nba.com/mavs/mavericks-sign-brandon-williams-to-two-way-contract'),
('c_stevens_trade','2024-02-07','https://www.nba.com/celtics/news/pressrelease-20240207-celtics-acquire-xavier-tillman-sr-from-memphis-grizzlies'),
]
# (team,start,end,source). Bounds not verified by a dated source use observed roster
# endpoints and explicitly remain incomplete; no endpoint is inferred from absence.
SPECS={
'1629656':[('NYK','2023-12-04','2024-02-07','p2_trade_tracker'),('DET','2024-02-08','2024-04-14','p2_trade_tracker')],
'203500':[('MEM','2023-12-04','2024-01-31','p2_trade_tracker'),('HOU','2024-02-01','2024-04-14','p2_trade_tracker')],
'203506':[('HOU','2023-12-04','2024-01-31','p2_trade_tracker'),('MEM','2024-02-01','2024-02-07','observed_roster;p2_trade_tracker;waiver_boundary_unverified')],
'1627853':[('NYK','2023-12-04','2024-02-07','p2_trade_tracker'),('DET','2024-02-08','2024-02-08','p2_trade_tracker;waiver_boundary_unverified')],
'1628384':[('TOR','2023-12-04','2023-12-29','c_knicks_dec_trade'),('NYK','2023-12-30','2024-04-14','c_knicks_dec_trade')],
'1630173':[('TOR','2023-12-04','2023-12-29','c_knicks_dec_trade'),('NYK','2023-12-30','2024-04-14','c_knicks_dec_trade')],
'1629023':[('CHA','2023-12-04','2024-02-07','c_dallas_trades'),('DAL','2024-02-08','2024-04-14','c_dallas_trades')],
'1629655':[('WAS','2023-12-04','2024-02-07','c_dallas_trades'),('DAL','2024-02-08','2024-04-14','c_dallas_trades')],
'1629684':[('DAL','2023-12-04','2024-02-07','c_dallas_trades'),('CHA','2024-02-08','2024-04-14','c_dallas_trades')],
'203552':[('DAL','2023-12-04','2024-02-07','c_dallas_trades'),('CHA','2024-02-08','2024-04-14','c_dallas_trades')],
'1626158':[('DAL','2023-12-04','2024-02-07','c_dallas_trades'),('WAS','2024-02-08','2024-04-14','c_dallas_trades')],
'1630544':[('OKC','2023-12-04','2024-02-07','c_okc_trade'),('CHA','2024-02-08','2024-04-14','c_okc_trade')],
'202722':[('OKC','2023-12-04','2024-02-07','c_okc_trade'),('CHA','2024-02-08','2024-04-14','c_okc_trade')],
'203995':[('OKC','2023-12-04','2024-02-07','c_okc_trade'),('CHA','2024-02-08','2024-04-14','c_okc_trade')],
'202330':[('CHA','2023-12-04','2024-02-07','c_okc_trade'),('OKC','2024-02-08','2024-04-14','c_okc_trade')],
'1630214':[('MEM','2023-12-04','2024-02-06','p2_trade_tracker'),('BOS','2024-02-07','2024-04-14','p2_trade_tracker')],
'1630205':[('BOS','2023-12-04','2024-02-06','p2_trade_tracker'),('MEM','2024-02-07','2024-04-14','p2_trade_tracker')],
'1631223':[('MEM','2023-12-04','2024-02-07','p2_trade_tracker'),('PHX','2024-02-08','2024-04-14','p2_trade_tracker')],
'1629139':[('PHX','2023-12-04','2024-02-07','p2_trade_tracker'),('MEM','2024-02-08','2024-04-14','p2_trade_tracker')],
'202687':[('MEM','2023-12-04','2024-01-09','c_biyombo_waive'),('OKC','2024-02-10','2024-04-14','c_biyombo_sign')],
'1631367':[('MEM','2023-12-04','2024-02-23','c_gilyard_actual'),('BKN','2024-03-02','2024-04-14','c_gilyard_sign')],
'1630197':[('OKC','2023-12-04','2024-02-22','c_poku_waiver'),('CHA','2024-02-28','2024-04-14','c_poku_actual')],
'201988':[('ATL','2023-12-04','2024-02-28','c_mills_waiver'),('MIA','2024-03-06','2024-04-14','c_mills_sign')],
'1641998':[('WAS','2024-01-20','2024-01-29','c_jemison_was'),('MEM','2024-01-30','2024-04-14','c_jemison_2way')],
'1630692':[('PHX','2023-12-04','2024-02-07','p2_trade_tracker'),('MEM','2024-02-13','2024-04-14','c_goodwin_10day;c_gilyard_waiver')],
'1630562':[('MEM','2024-01-29','2024-02-07','c_hurt_10day'),('MEM','2024-02-26','2024-03-06','observed_roster; second10day_confirmation_pending')],
'201959':[('NYK','2023-12-15','2024-01-06','observed_roster;c_taj_waiver_REJECTED_WRONG_YEAR;last_observed_roster_only'),('NYK','2024-01-30','2024-02-08','c_taj_10day'),('NYK','2024-02-10','2024-02-14','observed_roster; second10day_end_unverified'),('DET','2024-03-06','2024-04-14','observed_roster; subsequent_contract_continuity_unverified')],
'1629308':[('SAC','2023-12-15','2024-01-06','observed_roster;Jan7_waiver'),('SAC','2024-01-09','2024-01-18','c_toscano_10day')],
'1630249':[('ATL','2023-12-22','2024-04-14','c_krejci_sign')],
'1630314':[('DAL','2023-12-28','2024-04-14','c_brandon_actual')],
}
def target():
    selected={r['team'] for r in registration()['selected']};index=set()
    from injury_warning.longitudinal import parse_game_page
    sm=manifest()
    for g in json.loads((D/'team_schedule.json').read_text()):
        if not '2024-01-01'<=g['game_date']<='2024-02-18':continue
        page,_=parse_game_page(read('page_'+g['game_id'],sm))
        t=next(t for t in [page['homeTeam'],page['awayTeam']] if t['teamTricode']==g['team'])
        index.update(str(p['personId']) for p in t['players']+t['inactives'])
    # Reuse source-linked Phase2B membership for overlapping transfer players.
    prior=json.loads((ROOT/'phase2b/membership_review_ranges.json').read_text());spells=[r for r in prior if r['player_id'] in index and r['player_id'] not in SPECS]
    for pid,spec in SPECS.items():
        if pid not in index:continue
        for team,start,end,sid in spec:spells.append(dict(player_id=pid,team=team,start=start,end=end,date_basis='reviewed dated trade/signing/waiver; observed endpoints and unverified short-contract gaps explicitly indicated',source_id=sid,historical_availability='C membership adjudication; no retroactive B eligibility exclusion'))
    # Missing endpoints with failed sources are not promoted to verified membership.
    # All corresponding raw receipt states and gap ledger remain available.
    (D/'membership_review_ranges.json').write_text(json.dumps(spells,indent=2)+'\n');ss=schedule();wanted=defaultdict(set)
    for sp in spells:
        if sp['team'] not in selected:
            for g in ss:
                if g['team']==sp['team'] and sp['start']<=g['game_date']<=sp['end']:wanted[(g['team'],g['game_id'])].add(sp['player_id'])
    lookup={(g['team'],g['game_id']):g for g in ss};games=[dict(lookup[k],player_ids=sorted(v),scope='targeted_actual_player_history_followup') for k,v in wanted.items()];(D/'targeted_team_games.json').write_text(json.dumps(games,indent=2)+'\n')
    req={r['source_id']:r for r in json.loads((D/'targeted_requests.json').read_text())} if (D/'targeted_requests.json').exists() else {}
    for g in games:
        a,b=g['matchup'].split(' @ ') if ' @ ' in g['matchup'] else g['matchup'].split(' vs. ')[::-1];ds=g['game_date'].replace('-','');gid=g['game_id']
        for kind,url in [('page',f'https://www.nba.com/game/{a.lower()}-vs-{b.lower()}-{gid}/box-score'),('book',f'https://statsdmz.nba.com/pdfs/{ds}/{ds}_{a}{b}_book.pdf')]:req[kind+'_'+gid]=dict(source_id=kind+'_'+gid,date=g['game_date'],kind=kind,url=url)
    for sid,day,url in NEWS:req[sid]=dict(source_id=sid,date=day,kind='news',url=url)
    (D/'targeted_requests.json').write_text(json.dumps(list(req.values()),indent=2)+'\n');print('Targeted player/team game records:',len(games),'membership spells:',len(spells))
if __name__=='__main__':target()
