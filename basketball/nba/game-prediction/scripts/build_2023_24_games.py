"""Build Stage 1A identity/outcome tables. Default mode is strictly cache-only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import pandas as pd
from nba_game_prediction.ingest import retrieve, extract_table
from nba_game_prediction.normalize import normalize
from nba_game_prediction.validate import validate_and_pair


def write_json(path, obj):
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Allow one source request only if no valid full-season cache exists')
    args = parser.parse_args()
    body, provenance, cached = retrieve(ROOT/'data/raw/2023-24', allow_network=args.fetch)
    columns, rows = extract_table(body)
    raw = pd.DataFrame(rows, columns=columns)
    normalized = normalize(body)
    teams, games, anomalies = validate_and_pair(normalized)
    reject = anomalies[anomalies['severity']=='reject']
    warnings = anomalies[anomalies['severity']=='warning']
    paths = ROOT/'data/interim'
    paths.mkdir(parents=True, exist_ok=True)
    (ROOT/'data/processed').mkdir(parents=True, exist_ok=True)
    artifacts = {
        'team_games_2023_24.parquet': teams,
        'games_2023_24.parquet': games,
        'game_outcomes_2023_24.parquet': games[['game_id','home_pts','away_pts','home_win']].copy(),
        'game_anomalies_2023_24.parquet': anomalies,
    }
    for name, frame in artifacts.items():
        path = paths/name
        temp = path.with_suffix('.parquet.tmp')
        frame.to_parquet(temp, index=False, engine='pyarrow')
        temp.replace(path)
    quality = {
        'season':'2023-24', 'season_type':'Regular Season',
        'raw_sha256':provenance['sha256'],
        'retrieved_team_game_rows':len(raw), 'raw_unique_game_ids':int(raw['GAME_ID'].nunique(dropna=True)),
        'accepted_team_game_rows':len(teams),'accepted_games':len(games),
        'rejected_games':int(reject['game_id'].nunique()),
        'anomalous_games':int(anomalies['game_id'].nunique()),
        'warning_games':int(warnings['game_id'].nunique()),
        'anomaly_rows':len(anomalies),
        'reasons':{str(k):int(v) for k,v in anomalies['reason'].value_counts().sort_index().items()},
        'earliest_game_date':str(normalized['game_date'].min().date()),
        'latest_game_date':str(normalized['game_date'].max().date()),
        'raw_team_count':int(raw['TEAM_ID'].nunique()),
        'raw_missing_counts':{str(k):int(v) for k,v in raw.isna().sum().items()},
        'accepted_team_missing_counts':{str(k):int(v) for k,v in teams.isna().sum().items()},
        'duplicate_team_game_rows_extra':int(normalized.duplicated(['game_id','team_id']).sum()),
        'duplicate_team_game_rows_involved':int(normalized.duplicated(['game_id','team_id'],keep=False).sum()),
        'raw_game_group_sizes':{str(k):int(v) for k,v in normalized.groupby('game_id').size().value_counts().sort_index().items()},
        'accepted_home_rows':int(teams['is_home'].sum()),
        'accepted_away_rows':int((~teams['is_home']).sum()),
        'accepted_games_per_team':{str(k):int(v) for k,v in teams.groupby('team_abbreviation').size().items()},
        'scope_observations':{
            'source_season_id_counts':{str(k):int(v) for k,v in raw['SEASON_ID'].value_counts(dropna=False).items()},
            'game_id_prefix_counts':{str(k):int(v) for k,v in raw['GAME_ID'].astype(str).str[:3].value_counts().items()},
            'cup_championship_date_rows':int((normalized['game_date']==pd.Timestamp('2023-12-09')).sum()),
            'all_star_game_date_rows':int((normalized['game_date']==pd.Timestamp('2024-02-18')).sum()),
            'outside_regular_season_date_rows':int(((normalized['game_date']<pd.Timestamp('2023-10-24')) | (normalized['game_date']>pd.Timestamp('2024-04-14'))).sum()),
        },
        'count_expectation_note':'30 teams / 82 games each / 1230 total are contextual clues, not acceptance gates.',
        'validation_policy':'Reject identity/scope/pairing/score/basic-count errors; plus-minus and missing optional fields are explicit warnings.',
    }
    write_json(paths/'data_quality_2023_24.json', quality)
    manifest = {
        'raw_provenance':provenance,
        'output_sha256':{name:sha256((paths/name).read_bytes()).hexdigest() for name in artifacts},
        'code_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src/nba_game_prediction').glob('*.py'))},
        'build_script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'requirements_sha256':sha256((ROOT/'requirements.txt').read_bytes()).hexdigest(),
        'quality_sha256':sha256((paths/'data_quality_2023_24.json').read_bytes()).hexdigest(),
    }
    write_json(paths/'build_manifest_2023_24.json', manifest)
    print(json.dumps({'cache_used':cached,**{k:quality[k] for k in ['retrieved_team_game_rows','raw_unique_game_ids','accepted_games','rejected_games','anomalous_games','reasons']}},indent=2))
    return 0 if len(games) else 2


if __name__ == '__main__':
    raise SystemExit(main())
