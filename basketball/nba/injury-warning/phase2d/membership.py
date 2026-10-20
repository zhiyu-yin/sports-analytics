"""Actual all-cache roster spells and targeted other-team sequences; no zero fill."""
import json,time
from collections import defaultdict
from . import runtime as rt
from .runtime import ROOT,D,SPEC,bd,manifest,activity
from .sources import catalog
from injury_warning.longitudinal import parse_game_page
from phase2a.acquire import read
from phase1d.acquire import schedule

def target():
    sm=manifest();selected={t['team'] for t in SPEC['batches'][rt.BATCH-1]};ss=schedule();obs=defaultdict(dict);names={};index=set()
    with activity('membership_full_cache_roster_review'):
        for sid,r in sm.items():
            if not sid.startswith('page_') or r['status']!='obtained' or not '2023-12-04'<=r.get('date','')<='2024-04-14':continue
            g,_=parse_game_page(read(sid,sm));gid=str(g['gameId'])
            for t in [g['homeTeam'],g['awayTeam']]:
                for p in t['players']+t['inactives']:
                    pid=str(p['personId']);names[pid]=p['firstName']+' '+p['familyName'];obs[(pid,t['teamTricode'])][gid]=r['date']
                    if t['teamTricode'] in selected and '2024-01-01'<=r['date']<='2024-02-18':index.add(pid)
        # Reuse explicitly source-linked corrections. New raw roster intervals
        # are split at every missing expected-team roster, never extrapolated.
        explicit={}
        for ph in ['phase2b','phase2c']:
            pp=json.loads((ROOT/ph/'membership_review_ranges.json').read_text())
            for pid in {r['player_id'] for r in pp}:explicit[pid]=[r for r in pp if r['player_id']==pid]
        spells=[];targets=[];ledger=[]
        for pid in sorted(index):
            prior=explicit.get(pid)
            if prior:
                spells+=prior
            else:
                for (pp,team),seen in obs.items():
                    if pp!=pid:continue
                    games=sorted([g for g in ss if g['team']==team and '2023-12-04'<=g['game_date']<='2024-04-14'],key=lambda g:g['game_date']);block=[]
                    for g in games+[{}]:
                        if g.get('game_id') in seen:block.append(g)
                        elif block:
                            spells.append(dict(player_id=pid,team=team,start='2023-12-04' if block[0]['game_id']==games[0]['game_id'] else block[0]['game_date'],end=block[-1]['game_date'],date_basis='continuous actual observed game-roster block; split at missing roster; unverified inter-block contract/intraday boundary; no extrapolation',source_id=';'.join('page_'+x['game_id'] for x in [block[0],block[-1]]),historical_availability='C observed membership bounds; no B prospective exclusion'));block=[]
            own=[s for s in spells if s['player_id']==pid];ledger.append(dict(player_id=pid,player_name=names[pid],teams=sorted({s['team'] for s in own}),spells=own,boundary_review='Explicit prior dated evidence reused where available; otherwise conservative raw-roster blocks. Short/waiver/contract gaps retained unverified, not zero workload.'))
            for (pp,team),seen in obs.items():
                if pp!=pid or team in selected:continue
                for g in ss:
                    if g['team']==team and g['game_id'] in seen:targets.append(dict(g,player_ids=[pid],scope='targeted_actual_player_roster_only'))
        # Merge actual player requests for the same team/game.
        merged={}
        for g in targets:
            k=(g['team'],g['game_id'])
            if k not in merged:merged[k]=dict(g)
            else:merged[k]['player_ids']+=g['player_ids']
        (bd()/'membership_review_ranges.json').write_text(json.dumps(spells,indent=2)+'\n');(bd()/'targeted_team_games.json').write_text(json.dumps(list(merged.values()),indent=2)+'\n');(bd()/'membership_boundary_review.json').write_text(json.dumps(ledger,indent=2)+'\n')
        print('index inventory',len(index),'spells',len(spells),'target games',len(merged))
if __name__=='__main__':target()
