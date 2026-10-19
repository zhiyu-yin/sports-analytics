"""Roster-only cache discovery to target prior-team and destination-team evidence."""
from collections import defaultdict
import json
from injury_warning.longitudinal import parse_game_page,minutes
from .acquire import D,manifest,read,registration

def discover():
    sm=manifest();teams={t['team'] for t in registration()['selected']};obs=defaultdict(list);names={};candidates=set()
    for sid,r in sm.items():
        if not sid.startswith('page_') or r['status']!='obtained' or not '2023-12-04'<=r.get('date','')<='2024-04-14':continue
        g,_=parse_game_page(read(sid,sm))
        for team in [g['homeTeam'],g['awayTeam']]:
            t=team['teamTricode']
            for p in team['players']+team['inactives']:
                pid=str(p['personId']);names[pid]=p['firstName']+' '+p['familyName'];played=(minutes(p.get('statistics',{}).get('minutes')) or 0)>0;obs[pid].append(dict(team=t,date=r['date'],source_id=sid,appeared=played))
                if t in teams and '2024-01-01'<=r['date']<='2024-02-18' and played:candidates.add(pid)
    review=[]
    for pid in sorted(candidates):
        own=[x for x in obs[pid] if x['team'] in teams];start=min(x['date'] for x in own);end=max(x['date'] for x in own);other=[x for x in obs[pid] if x['team'] not in teams]
        if start>'2023-12-08' or end<'2024-04-10' or len({x['team'] for x in own})>1:
            review.append(dict(player_id=pid,player_name=names[pid],sampled_teams=sorted({x['team'] for x in own}),first_sampled_roster=start,last_sampled_roster=end,other_team_rosters={t:[min(x['date'] for x in other if x['team']==t),max(x['date'] for x in other if x['team']==t)] for t in sorted({x['team'] for x in other})}))
    (D/'roster_discovery.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps(review,indent=2))
if __name__=='__main__':discover()
