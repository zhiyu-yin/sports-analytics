"""Transparent pregame features. Outcome series are shifted before aggregation."""
import numpy as np
import pandas as pd
from .schedule import schedule_features
from .seasons import get_scope, date_in_scope

VERSION = '1.0.0'
KEYS = ['season','season_type','game_id','game_date']
GAME_IDENTITIES = KEYS + [s+'_'+k for s in ['home','away'] for k in ['team_id','team_name','team_abbreviation']]
TEAM_IDENTITIES = KEYS + ['team_id','team_name','team_abbreviation','is_home','opponent_team_id','opponent_team_abbreviation']
FEATURES = ['games_played_before','season_win_pct_before','win_pct_last_5','win_pct_last_10',
            'point_diff_avg_last_5','point_diff_avg_last_10','pts_for_avg_last_5','pts_for_avg_last_10',
            'pts_against_avg_last_5','pts_against_avg_last_10','rest_days','is_back_to_back','games_last_7_days']
DIFFERENCES = {
    'season_win_pct_diff':'season_win_pct_before', 'win_pct_last_5_diff':'win_pct_last_5',
    'win_pct_last_10_diff':'win_pct_last_10','point_diff_last_5_diff':'point_diff_avg_last_5',
    'point_diff_last_10_diff':'point_diff_avg_last_10','rest_days_diff':'rest_days',
}
GAME_FEATURES = [s+'_'+f for s in ['home','away'] for f in FEATURES] + list(DIFFERENCES)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prepare_history(teams, games, outcomes):
    """Validate pairing and select only needed fields; no feature-time raw API reads."""
    for frame in (teams,games,outcomes):
        require(frame.columns.is_unique, 'Duplicate input column names')
    require(not teams.empty and not games.empty, 'Empty history')
    require(games['game_id'].is_unique and outcomes['game_id'].is_unique, 'Duplicate game/outcome key')
    require(not teams.duplicated(['game_id','team_id']).any(), 'Duplicate team-game')
    require(not teams.duplicated(['season','season_type','team_id','game_date']).any(), 'Same-date ambiguity: team has multiple games on a source date')
    require(set(teams.game_id)==set(games.game_id)==set(outcomes.game_id), 'Input game sets differ')
    require(len(teams)==2*len(games), 'Expected two team rows per game')
    require(games[GAME_IDENTITIES+['home_pts','away_pts','home_win']].notna().all().all(), 'Missing game identity/outcome')
    require(teams[KEYS+['team_id','team_name','team_abbreviation','is_home','opponent_team_abbreviation','pts','wl']].notna().all().all(), 'Missing team identity/outcome')
    require(teams['is_home'].isin([True,False]).all(), 'Invalid home indicator')
    for frame in (teams,games):
        require(frame.season_type.eq('Regular Season').all(), 'Only Regular Season is allowed')
        for season, season_rows in frame.groupby('season', dropna=False):
            scope = get_scope(season)
            require(season_rows.game_date.map(lambda d: date_in_scope(d, scope)).all(), 'Season label/date mismatch')
            require(season_rows.game_id.str.startswith(scope.game_prefix).all(), 'Season label/game ID mismatch')
            if 'source_season_id' in season_rows:
                require(season_rows.source_season_id.eq(scope.source_season_id).all(), 'Source season ID mismatch')
        require(pd.api.types.is_datetime64_any_dtype(frame.game_date), 'Dates must already be parsed')
        require(frame.game_date.dt.tz is None and frame.game_date.eq(frame.game_date.dt.normalize()).all(), 'Dates must have calendar-date semantics')
    ordered = games.sort_values('game_id').reset_index(drop=True)
    y = outcomes.sort_values('game_id').reset_index(drop=True)
    for col in ['game_id','home_pts','away_pts','home_win']:
        require(ordered[col].equals(y[col]), 'Canonical/outcome mismatch: '+col)
    require((games.home_team_id != games.away_team_id).all(), 'Repeated team in a game')
    for col in ['home_pts','away_pts']:
        require(pd.api.types.is_numeric_dtype(games[col]) and np.isfinite(games[col].astype(float)).all()
                and games[col].ge(0).all() and games[col].mod(1).eq(0).all(), 'Invalid final scores')
    require(games.home_pts.ne(games.away_pts).all(), 'Tied completed game')
    require(games.home_win.eq(games.home_pts.gt(games.away_pts)).all(), 'Outcome/score mismatch')
    parts = []
    for side,other,home in [('home','away',True),('away','home',False)]:
        expected = games[KEYS].copy()
        for col in ['team_id','team_name','team_abbreviation']:
            expected[col] = games[side+'_'+col]
        expected['is_home'] = home
        expected['opponent_team_id'] = games[other+'_team_id']
        expected['opponent_team_abbreviation'] = games[other+'_team_abbreviation']
        expected['_points_for'] = games[side+'_pts'].astype(float)
        expected['_points_against'] = games[other+'_pts'].astype(float)
        actual = teams[teams.is_home.eq(home)]
        require(len(actual)==len(games) and actual.game_id.is_unique, 'Not exactly one home/away vector per game')
        a = actual.sort_values('game_id').reset_index(drop=True)
        b = expected.sort_values('game_id').reset_index(drop=True)
        for col in KEYS+['team_id','team_name','team_abbreviation','opponent_team_abbreviation']:
            require(a[col].eq(b[col]).all(), 'Team/canonical identity mismatch: '+col)
        require(a.pts.astype(float).eq(b._points_for).all(), 'Team/canonical score mismatch')
        wins = b._points_for.gt(b._points_against)
        require(a.wl.eq(np.where(wins,'W','L')).all(), 'Team W/L mismatch')
        b['_win'] = wins.astype(float)
        b['_point_diff'] = b._points_for - b._points_against
        parts.append(b)
    return pd.concat(parts,ignore_index=True).sort_values(['season','season_type','team_id','game_date']).reset_index(drop=True)


def build_features(teams, games, outcomes):
    history = prepare_history(teams,games,outcomes)
    frames = []
    for _,group in history.groupby(['season','season_type','team_id'],sort=True):
        group = group.sort_values('game_date').reset_index(drop=True)
        # The same-date guard means row predecessors are STRICTLY EARLIER dates.
        prior = group[['_win','_points_for','_points_against','_point_diff']].shift(1)
        result = group[TEAM_IDENTITIES].copy()
        result['games_played_before'] = pd.Series(np.arange(len(group)),dtype='Int64')
        result['season_win_pct_before'] = prior['_win'].expanding(min_periods=1).mean()
        for window in (5,10):
            for source,prefix in [('_win','win_pct'),('_point_diff','point_diff_avg'),
                                  ('_points_for','pts_for_avg'),('_points_against','pts_against_avg')]:
                result[f'{prefix}_last_{window}'] = prior[source].rolling(window=window,min_periods=window).mean()
        for col,series in schedule_features(group.game_date).items():
            result[col] = series
        frames.append(result[TEAM_IDENTITIES+FEATURES])
    team_features = pd.concat(frames,ignore_index=True).sort_values(['season','game_date','game_id','team_id']).reset_index(drop=True)
    for col in ['is_home']:team_features[col]=team_features[col].astype('boolean')
    game_features = games[GAME_IDENTITIES].copy()
    for side,home in [('home',True),('away',False)]:
        side_features = team_features.loc[team_features.is_home.eq(home),['game_id']+FEATURES]
        side_features = side_features.rename(columns={f:side+'_'+f for f in FEATURES})
        game_features = game_features.merge(side_features,on='game_id',how='left',validate='one_to_one')
    for name,source in DIFFERENCES.items():
        game_features[name]=game_features['home_'+source]-game_features['away_'+source]
    game_features = game_features[GAME_IDENTITIES+GAME_FEATURES].sort_values(['season','game_date','game_id']).reset_index(drop=True)
    require(len(game_features)==len(games) and game_features.game_id.is_unique, 'Game feature cardinality mismatch')
    require(len(team_features)==len(teams), 'Team feature cardinality mismatch')
    require(game_features.columns.is_unique and team_features.columns.is_unique, 'Duplicate feature columns')
    # Exact allowlists prevent accidental export of any target-game outcome columns.
    require(list(team_features)==TEAM_IDENTITIES+FEATURES, 'Unexpected team feature column')
    require(list(game_features)==GAME_IDENTITIES+GAME_FEATURES, 'Unexpected game feature column')
    return team_features,game_features


def feature_dictionary():
    availability = 'Prior completed games with game_date < target game_date; same-team/date duplicates forbidden'
    definitions = {
        'games_played_before':('Number of prior games in this regular season','games','season to date',0,'game_date'),
        'season_win_pct_before':('Prior wins divided by prior games; missing at opener','fraction','season to date',1,'wl (validated against paired scores)'),
        'rest_days':('Calendar days since previous game minus one; missing at opener','calendar days','previous game',1,'game_date'),
        'is_back_to_back':('1 when rest_days is zero, else 0; opener 0','binary indicator','previous game',0,'game_date'),
        'games_last_7_days':('Count prior games in [target date - 7 days, target date)','games','7 calendar days; left inclusive, right exclusive',0,'game_date'),
    }
    for n in (5,10):
        for prefix,desc,unit,source in [
            ('win_pct','Fraction of wins','fraction','wl (validated against paired scores)'),
            ('point_diff_avg','Mean points for minus points against','points per game','pts; opponent pts from paired canonical game'),
            ('pts_for_avg','Mean points scored','points per game','pts'),
            ('pts_against_avg','Mean opponent points','points per game','opponent pts from paired canonical game')]:
            definitions[f'{prefix}_last_{n}']=(desc+f' in previous {n} games',unit,f'{n} prior games',n,source)
    rows=[]
    for name in FEATURES:
        desc,unit,window,minimum,source=definitions[name]
        base=dict(description=desc,unit=unit,window=window,minimum_history=minimum,source_columns=source,availability_rule=availability,definition_version=VERSION)
        rows.append(dict(table='team_pregame_features',feature_name=name,**base))
        for side in ['home','away']:
            rows.append(dict(table='game_features',feature_name=side+'_'+name,**dict(base,description=side.title()+' team: '+desc)))
    for name,source in DIFFERENCES.items():
        desc,unit,window,minimum,_=definitions[source]
        if unit=='fraction':unit='fraction difference (1.0 = 100 percentage points)'
        rows.append(dict(table='game_features',feature_name=name,description='Home minus away '+source+'; missing if either side missing',
                         unit=unit,window=window,minimum_history=f'{minimum} prior games for each team',
                         source_columns='home_'+source+';away_'+source,availability_rule=availability,definition_version=VERSION))
    return pd.DataFrame(rows)
