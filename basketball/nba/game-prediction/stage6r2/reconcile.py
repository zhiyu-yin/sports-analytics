"""Five authoritative mappings; Stage 1D function unchanged except season literal."""
import inspect,json
import pandas as pd
import common as c
from schedule_facts import IDS
from nba_game_prediction import reconciliation as prior
r=c.r
SOURCE=inspect.getsource(prior.apply_reconciliation)
ADAPTED=SOURCE.replace("'2024-25'","'2025-26'")
ns={'pd':pd,'validate_and_pair':r.validate.validate_and_pair}
exec(compile(ADAPTED,__file__+':Stage1DSeasonOnlyOverlay','exec'),ns)
apply_stage1d=ns['apply_reconciliation']
SCOPE=r.seasons.SeasonScope('2025-26','2025-10-21','2026-04-12')

def facts():
 manifest=r.read_json(c.E/'official_schedule_source_manifest.json')
 p=c.E/'official_schedule_facts.json'
 if r.access.checksum(p)!=manifest['facts_sha256']:raise ValueError('Official facts changed')
 if manifest['endpoint']!='ScheduleLeagueV2' or manifest['http_status']!=200 or manifest['parameters']!={'LeagueID':'00','Season':'2025-26'} or manifest['url']!='https://stats.nba.com/stats/scheduleleaguev2?LeagueID=00&Season=2025-26':raise ValueError('Official provenance mismatch')
 values=r.read_json(p)
 if [f['gameId'] for f in values]!=list(IDS):raise ValueError('Official game ID set mismatch')
 return values,manifest

def mapping(normalized,values,manifest):
 if sorted(f['gameId'] for f in values)!=list(IDS):raise ValueError('Only five approved games')
 rows=[]
 for f in values:
  g=normalized[normalized.game_id.eq(f['gameId'])].sort_values('source_row')
  if len(g)!=2 or g.team_id.nunique()!=2:raise ValueError('Raw pair mismatch')
  date=f['gameDateEst'][:10]
  if not g.game_date.eq(pd.Timestamp(date)).all() or pd.Timestamp(f['gameDate']).date()!=pd.Timestamp(date).date():raise ValueError('Date conflict')
  h,a=f['homeTeam'],f['awayTeam']
  if h['teamId']==a['teamId'] or {h['teamId'],a['teamId']}!=set(g.team_id):raise ValueError('Official team identity conflict')
  for team in [h,a]:
   if not g.loc[g.team_id.eq(team['teamId']),'team_abbreviation'].eq(team['teamTricode']).all():raise ValueError('Official tricode conflict')
  if f['gameCode']!=date.replace('-','')+'/'+a['teamTricode']+h['teamTricode']:raise ValueError('Official gameCode conflict')
  if f['isNeutral'] is not None and not isinstance(f['isNeutral'],bool):raise ValueError('Nonboolean official neutral status')
  raw1,raw2=g.iloc[0],g.iloc[1]
  rows.append(dict(season='2025-26',game_id=f['gameId'],game_date=date,raw_team_1_id=int(raw1.team_id),raw_team_1_matchup=raw1.matchup,raw_team_2_id=int(raw2.team_id),raw_team_2_matchup=raw2.matchup,reconciled_home_team_id=h['teamId'],reconciled_home_team_abbreviation=h['teamTricode'],reconciled_away_team_id=a['teamId'],reconciled_away_team_abbreviation=a['teamTricode'],neutral_site=f['isNeutral'],arena_name=f['arenaName'],arena_city=f['arenaCity'],source='NBA ScheduleLeagueV2 explicit homeTeam/awayTeam',source_url=manifest['url'],source_retrieved_at_utc=manifest['retrieved_at_utc'],source_response_sha256=manifest['source_response_sha256'],confidence='authoritative',reason='not_one_home_and_one_away',notes='Explicit official designation; raw MATCHUP, scores and W/L preserved; neutral status not a predictor'))
 return pd.DataFrame(rows)

def reconcile(normalized,approved,values,manifest):
 expected=mapping(normalized,values,manifest)
 if sorted(approved.game_id)!=list(IDS):raise ValueError('Unknown/missing/duplicate reconciliation ID')
 pd.testing.assert_frame_equal(approved.sort_values('game_id').reset_index(drop=True),expected.sort_values('game_id').reset_index(drop=True),check_exact=True)
 with r.scope_overlay(SCOPE):result,applied=apply_stage1d(normalized,approved)
 pd.testing.assert_frame_equal(normalized.drop(columns='is_home'),result.drop(columns='is_home'),check_exact=True)
 return result,applied

def complete_validation(normalized,teams,games,anomalies):
 counts=teams.groupby('team_id').size()
 if len(normalized)!=2460 or normalized.game_id.nunique()!=1230 or len(teams)!=len(normalized) or len(games)!=1230 or set(games.game_id)!=set(normalized.game_id) or len(counts)!=30 or not counts.eq(82).all() or anomalies.severity.eq('reject').any():raise ValueError('Complete 1,230-game season required before scoring')
 if str(games.game_date.min().date())!=SCOPE.start or str(games.game_date.max().date())!=SCOPE.end:raise ValueError('Observed source date range changed')
 return dict(passed=True,team_game_rows=len(teams),accepted_games=len(games),unique_games=int(games.game_id.nunique()),teams=len(counts),games_per_team={str(k):int(v) for k,v in counts.items()},first_game_date=SCOPE.start,last_game_date=SCOPE.end,rejected_games=0,warnings=int(anomalies.severity.eq('warning').sum()),applied_game_ids=list(IDS),original_matchup_scores_wl_unchanged=True,only_canonical_is_home_changed=True,source_count_derived_from_cached_snapshot=True)

def build():
 body=c.cached_body()
 with r.scope_overlay(SCOPE):normalized=r.normalize.normalize(body,season='2025-26');_,_,before=r.validate.validate_and_pair(normalized,season='2025-26')
 rejects=before[before.severity.eq('reject')]
 if sorted(rejects.game_id)!=list(IDS) or set(rejects.reason)!={'not_one_home_and_one_away'}:raise ValueError('Known anomaly set changed')
 values,manifest=facts();approved=mapping(normalized,values,manifest);fixed,applied=reconcile(normalized,approved,values,manifest)
 with r.scope_overlay(SCOPE):teams,games,anomalies=r.validate.validate_and_pair(fixed,season='2025-26')
 proof=complete_validation(normalized,teams,games,anomalies)
 return approved,teams,games,anomalies,proof
