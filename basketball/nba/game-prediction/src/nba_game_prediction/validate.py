"""Reject structurally invalid games; report nonauthoritative plus-minus conflicts."""
import json
import pandas as pd
from nba_api.stats.static.teams import get_teams
from .normalize import TEAM_COLUMNS
from .seasons import get_scope, date_in_scope

GAME_COLUMNS = ['season','season_type','game_id','game_date',
                'home_team_id','home_team_name','home_team_abbreviation',
                'away_team_id','away_team_name','away_team_abbreviation',
                'home_pts','away_pts','home_win']
ANOMALY_COLUMNS = ['game_id','severity','reason','observed_values_json']


def validate_and_pair(df, *, season="2023-24"):
    """Return accepted teams, games, all anomalies; each rejected game stays traceable."""
    scope = get_scope(season)
    registry = {t['id']: t['abbreviation'] for t in get_teams()}
    duplicate_ids = set(df.loc[df.duplicated(['game_id','team_id'], keep=False), 'game_id'])
    # A team ID/abbreviation must have a stable, unambiguous mapping in the dataset.
    conflicting_ids = set()
    for tid, team in df.dropna(subset=['team_id']).groupby('team_id'):
        if team['team_abbreviation'].nunique(dropna=False) != 1 or team['team_name'].nunique(dropna=False) != 1:
            conflicting_ids.add(tid)
    accepted_ids, games, anomalies = [], [], []
    for gid, group in df.groupby('game_id', sort=True, dropna=False):
        errors, warnings = set(), set()
        for _, row in group.iterrows():
            errors.update(row['_errors']); warnings.update(row['_warnings'])
            if pd.isna(row['source_season_id']) or row['source_season_id'] != scope.source_season_id or row['season'] != season or row['season_type'] != 'Regular Season':
                errors.add('out_of_scope_season_id')
            if not str(gid).startswith(scope.game_prefix):
                errors.add('out_of_scope_game_type_or_season')
            if pd.notna(row['game_date']) and not date_in_scope(row['game_date'], scope):
                errors.add('out_of_scope_date')
            # Championship date had no regular-season games; explicit extra-game guard.
            if scope.cup_final and row['game_date'] == pd.Timestamp(scope.cup_final):
                errors.add('cup_championship_date_requires_reconciliation')
            tid, abbr = row['team_id'], row['team_abbreviation']
            if pd.notna(tid) and (tid not in registry or pd.isna(abbr) or registry[tid] != abbr):
                errors.add('unknown_or_inconsistent_team_identity')
            if pd.notna(tid) and tid in conflicting_ids:
                errors.add('inconsistent_team_mapping')
            for made, attempts in [('fgm','fga'),('fg3m','fg3a'),('ftm','fta'),('fg3m','fgm'),('fg3a','fga')]:
                if pd.notna(row[made]) and pd.notna(row[attempts]) and row[made] > row[attempts]:
                    errors.add('invalid_box_score_counts')
            if all(pd.notna(row[k]) for k in ['pts','fgm','fg3m','ftm']):
                if row['pts'] != 2 * row['fgm'] + row['fg3m'] + row['ftm']:
                    errors.add('points_do_not_match_scoring_components')
            if all(pd.notna(row[k]) for k in ['oreb','dreb','reb']):
                if row['reb'] != row['oreb'] + row['dreb']:
                    errors.add('rebound_total_mismatch')
        if gid in duplicate_ids:
            errors.add('duplicate_team_game')
        if len(group) != 2:
            errors.add('not_exactly_two_rows')
        if group['team_id'].nunique() != 2:
            errors.add('not_two_distinct_teams')
        if group['game_date'].isna().any() or group['game_date'].nunique() != 1:
            errors.add('game_date_mismatch_or_missing')
        home = group[group['is_home'].fillna(False)]
        away = group[group['is_home'].eq(False).fillna(False)]
        if len(home) != 1 or len(away) != 1:
            errors.add('not_one_home_and_one_away')
        if len(home) == 1 and len(away) == 1:
            h, a = home.iloc[0], away.iloc[0]
            ids = [h['opponent_team_abbreviation'],a['team_abbreviation'],a['opponent_team_abbreviation'],h['team_abbreviation']]
            if any(pd.isna(v) for v in ids) or ids[0] != ids[1] or ids[2] != ids[3]:
                errors.add('nonreciprocal_opponents')
            if {h['wl'],a['wl']} != {'W','L'}:
                errors.add('noncomplementary_wl')
            if pd.notna(h['pts']) and pd.notna(a['pts']):
                if h['pts'] == a['pts']:
                    errors.add('tied_final_score')
                elif pd.isna(h['wl']) or pd.isna(a['wl']) or h['wl'] != ('W' if h['pts'] > a['pts'] else 'L') or a['wl'] != ('W' if a['pts'] > h['pts'] else 'L'):
                    errors.add('score_wl_mismatch')
                for team, opponent in [(h,a),(a,h)]:
                    if pd.notna(team['plus_minus']) and team['plus_minus'] != team['pts'] - opponent['pts']:
                        warnings.add('plus_minus_score_mismatch')
        observed = '[' + ','.join(group['_observed']) + ']'
        for severity, reasons in [('reject',errors),('warning',warnings)]:
            for reason in sorted(reasons):
                anomalies.append(dict(game_id=gid,severity=severity,reason=reason,observed_values_json=observed))
        if errors:
            continue
        accepted_ids.append(gid)
        record = {k:h[k] for k in ['season','season_type','game_id','game_date']}
        for side, team in [('home',h),('away',a)]:
            for col in ['team_id','team_name','team_abbreviation','pts']:
                record[side+'_'+col] = team[col]
        record['home_win'] = bool(h['pts'] > a['pts'])
        games.append(record)
    teams = df[df['game_id'].isin(accepted_ids)][TEAM_COLUMNS].sort_values(['game_date','game_id','is_home'],ascending=[True,True,False]).reset_index(drop=True)
    games = pd.DataFrame(games, columns=GAME_COLUMNS)
    for col in ['home_team_id','away_team_id','home_pts','away_pts']:
        games[col] = games[col].astype('Int64')
    games['home_win'] = games['home_win'].astype('boolean')
    games['game_date'] = pd.to_datetime(games['game_date'])
    for col in set(GAME_COLUMNS)-{'home_team_id','away_team_id','home_pts','away_pts','home_win','game_date'}:
        games[col] = games[col].astype('string')
    games = games.sort_values(['game_date','game_id']).reset_index(drop=True)
    anomalies = pd.DataFrame(anomalies, columns=ANOMALY_COLUMNS).astype('string')
    rejected_ids = set(anomalies.loc[anomalies['severity'] == 'reject', 'game_id'])
    assert not set(accepted_ids) & rejected_ids
    assert set(accepted_ids) | rejected_ids == set(df['game_id'])
    assert len(teams) == 2*len(games)
    assert games['game_id'].is_unique
    assert not teams.duplicated(['game_id','team_id']).any()
    return teams, games, anomalies
