"""Only five exact official schedule objects and explicit factual fields."""
import json
IDS=('0022500147','0022500578','0022500602','0022501229','0022501230')
def extract_facts(body):
 obj=json.loads(body)
 schedules=[v for v in obj.values() if isinstance(v,dict) and 'gameDates' in v]
 if len(schedules)!=1:raise ValueError('Ambiguous schedule container')
 league=schedules[0]
 if str(league['leagueId'])!='00' or str(league['seasonYear'])!='2025-26':raise ValueError('Unexpected league/season')
 facts=[]
 for day in league['gameDates']:
  for game in day['games']:
   if game.get('gameId') not in IDS:continue
   f={k:game[k] for k in ['gameId','gameDateEst','gameCode','arenaName','arenaCity']}
   f['gameDate']=day['gameDate'];f['isNeutral']=game.get('isNeutral')
   for side in ['homeTeam','awayTeam']:f[side]={k:game[side][k] for k in ['teamId','teamTricode']}
   facts.append(f)
 if sorted(f['gameId'] for f in facts)!=list(IDS):raise ValueError('Missing/duplicate official game IDs')
 return sorted(facts,key=lambda f:f['gameId'])
