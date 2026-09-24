"""Offline schema/pair checks for Stage 0 recorded samples, not a dataset builder."""
from pathlib import Path
import json, collections
root=Path(__file__).resolve().parent
p=root/'docs/stage0_evidence'
summary={}
for name in ['recorded_teamgamelog','recorded_leaguegamefinder']:
 t=json.loads((p/(name+'.json')).read_text())['resultSets'][0]
 rows=[dict(zip(t['headers'],r)) for r in t['rowSet']]
 summary[name]={'rows':len(rows),'columns':t['headers'],'null_counts':{k:sum(r[k] is None for r in rows) for k in t['headers']},'types':{k:sorted({type(r[k]).__name__ for r in rows}) for k in t['headers']},'examples':rows[:2]}
 if name.endswith('finder'):
  groups=collections.defaultdict(list)
  for r in rows: groups[r['GAME_ID']].append(r)
  structural=[]; score_conflicts=[]
  for gid,rs in groups.items():
   h=[r for r in rs if ' vs. ' in r['MATCHUP']]; a=[r for r in rs if ' @ ' in r['MATCHUP']]
   if len(rs)!=2 or len(h)!=1 or len(a)!=1: structural.append(gid); continue
   h,a=h[0],a[0]
   if h['TEAM_ID']==a['TEAM_ID'] or h['GAME_DATE']!=a['GAME_DATE'] or h['MATCHUP'].split(' vs. ')[1]!=a['TEAM_ABBREVIATION'] or a['MATCHUP'].split(' @ ')[1]!=h['TEAM_ABBREVIATION']: structural.append(gid)
   if h['PLUS_MINUS']!=h['PTS']-a['PTS'] or a['PLUS_MINUS']!=a['PTS']-h['PTS'] or (h['WL']=='W')!=(h['PTS']>a['PTS']) or {h['WL'],a['WL']}!={'W','L'}: score_conflicts.append({'game_id':gid,'rows':rs})
  summary[name].update(games=len(groups),structural_pair_failures=structural,score_conflicts=score_conflicts,duplicate_team_games=len(rows)-len({(r['GAME_ID'],r['TEAM_ID']) for r in rows}),date_min=min(r['GAME_DATE'] for r in rows),date_max=max(r['GAME_DATE'] for r in rows),teams=len({r['TEAM_ID'] for r in rows}))
for name,key in [('recorded_advanced','boxScoreAdvanced'),('recorded_four_factors','boxScoreFourFactors')]:
 g=json.loads((p/(name+'.json')).read_text())[key]
 summary[name]={'game_id':g['gameId'],'home_team_id':g['homeTeamId'],'away_team_id':g['awayTeamId'],'team_statistics':{t:g[t]['statistics'] for t in ['homeTeam','awayTeam']},'team_stat_null_count':sum(v is None for t in ['homeTeam','awayTeam'] for v in g[t]['statistics'].values())}
(p/'inspection_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Inspected four recorded response bodies; pairing conflicts are preserved in inspection_summary.json.')
