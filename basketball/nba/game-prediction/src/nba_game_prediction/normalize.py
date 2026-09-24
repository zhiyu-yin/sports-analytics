"""Normalize source records; never calculate predictors or silently repair rows."""
from datetime import datetime
import json
import math
import re

import pandas as pd

from .ingest import SEASON, SEASON_TYPE, extract_table
from .seasons import get_scope

COUNTS = ['pts','fgm','fga','fg3m','fg3a','ftm','fta','oreb','dreb','reb','ast','stl','blk','tov','pf']
IDENTITY = ['season','season_type','source_season_id','game_id','game_date','team_id',
            'team_name','team_abbreviation','matchup','is_home','opponent_team_abbreviation','wl']
TEAM_COLUMNS = IDENTITY + COUNTS + ['plus_minus','source_row']


def parse_matchup(matchup, team_abbreviation):
    """Exact provider grammar, including validation of the row's own identity."""
    if not isinstance(matchup, str):
        raise ValueError('MATCHUP must be a string')
    match = re.fullmatch(r'([A-Z]{2,3}) (vs\.|@) ([A-Z]{2,3})', matchup)
    if not match or match[1] != team_abbreviation or match[1] == match[3]:
        raise ValueError(f'Invalid or inconsistent MATCHUP: {matchup!r}')
    return match[2] == 'vs.', match[3]


def integer(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Expected numeric integer')
    if not math.isfinite(value) or value != int(value) or value < 0:
        raise ValueError('Expected nonnegative finite integer')
    return int(value)


def normalize(body, *, season=SEASON):
    get_scope(season)
    headers, raw_rows = extract_table(body)
    normalized = []
    for index, values in enumerate(raw_rows):
        raw = dict(zip(headers, values))
        errors, warnings = [], []
        gid = raw.get('GAME_ID')
        if not isinstance(gid, str) or not re.fullmatch(r'\d{10}', gid):
            errors.append('invalid_game_id')
        row = dict.fromkeys(TEAM_COLUMNS)
        row.update(season=season, season_type=SEASON_TYPE,
                   source_season_id=raw.get('SEASON_ID'),
                   game_id=gid if isinstance(gid, str) and gid else f'<invalid:{index}>',
                   team_name=raw.get('TEAM_NAME'), team_abbreviation=raw.get('TEAM_ABBREVIATION'),
                   matchup=raw.get('MATCHUP'), wl=raw.get('WL'), source_row=index)
        for col in ['team_name','team_abbreviation']:
            if not isinstance(row[col], str) or not row[col].strip():
                errors.append('missing_' + col)
        try:
            date = raw['GAME_DATE']
            if not isinstance(date, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
                raise ValueError('Expected YYYY-MM-DD')
            row['game_date'] = datetime.strptime(date, '%Y-%m-%d')
        except (ValueError, KeyError, TypeError):
            errors.append('invalid_game_date')
        try:
            row['team_id'] = integer(raw.get('TEAM_ID'))
            if row['team_id'] == 0:
                errors.append('invalid_team_id')
        except ValueError:
            errors.append('invalid_team_id')
        try:
            row['is_home'], row['opponent_team_abbreviation'] = parse_matchup(raw.get('MATCHUP'), raw.get('TEAM_ABBREVIATION'))
        except ValueError:
            errors.append('invalid_matchup')
        if raw.get('WL') not in ('W', 'L'):
            errors.append('not_completed_or_invalid_wl')
        for col in COUNTS:
            val = raw.get(col.upper())
            if val is None and col != 'pts':
                warnings.append('missing_optional_' + col)
                continue
            try:
                row[col] = integer(val)
            except ValueError:
                errors.append('invalid_' + col)
        pm = raw.get('PLUS_MINUS')
        if pm is None:
            warnings.append('missing_optional_plus_minus')
        elif isinstance(pm, bool) or not isinstance(pm, (int,float)) or not math.isfinite(pm):
            warnings.append('invalid_plus_minus')
        else:
            row['plus_minus'] = float(pm)
        row.update(_errors=errors, _warnings=warnings, _observed=json.dumps(raw, sort_keys=True, default=str))
        normalized.append(row)
    df = pd.DataFrame(normalized)
    for col in COUNTS + ['team_id','source_row']:
        df[col] = df[col].astype('Int64')
    for col in ['season','season_type','source_season_id','game_id','team_name','team_abbreviation','matchup','opponent_team_abbreviation','wl']:
        df[col] = df[col].astype('string')
    df['game_date'] = pd.to_datetime(df['game_date'])
    df['is_home'] = df['is_home'].astype('boolean')
    df['plus_minus'] = df['plus_minus'].astype('Float64')
    return df
