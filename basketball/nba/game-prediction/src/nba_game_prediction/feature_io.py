"""Local Stage 1A provenance gate; never imports ingestion/network functionality."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import pandas as pd


def digest(path):
    from .sealed_access import checksum
    return checksum(path)


def verified_bytes(path, expected):
    data=Path(path).read_bytes()
    if sha256(data).hexdigest()!=expected:
        raise ValueError(f'Stage 1A provenance mismatch: {path}; stop, do not regenerate inputs')
    return data


def load_inputs(root):
    root=Path(root);interim=root/'data/interim'
    manifest_path=interim/'build_manifest_2023_24.json'
    manifest=json.loads(manifest_path.read_text())
    frames={};hashes={}
    for name in ['team_games_2023_24.parquet','games_2023_24.parquet','game_outcomes_2023_24.parquet','game_anomalies_2023_24.parquet']:
        expected=manifest['output_sha256'][name]
        verified_bytes(interim/name,expected)
        frames[name]=pd.read_parquet(interim/name)
        hashes['data/interim/'+name]=expected
    qpath=interim/'data_quality_2023_24.json'
    quality=json.loads(verified_bytes(qpath,manifest['quality_sha256']))
    verified_bytes(root/'requirements.txt',manifest['requirements_sha256'])
    teams,games,outcomes,anomalies=[frames[n] for n in ['team_games_2023_24.parquet','games_2023_24.parquet','game_outcomes_2023_24.parquet','game_anomalies_2023_24.parquet']]
    conditions=[len(teams)==2460,len(games)==1230,len(outcomes)==1230,
                teams.game_id.nunique()==1230,games.game_id.is_unique,outcomes.game_id.is_unique,
                teams.team_id.nunique()==30,teams.groupby('team_id').size().eq(82).all(),
                anomalies.empty,quality['rejected_games']==0,quality['accepted_games']==1230,
                quality['accepted_team_game_rows']==2460,quality['raw_team_count']==30,
                manifest['raw_provenance']['season']=='2023-24',
                manifest['raw_provenance']['season_type']=='Regular Season']
    if not all(conditions):raise ValueError('Stage 1A snapshot counts/scope differ; stop')
    hashes.update({'data/interim/build_manifest_2023_24.json':digest(manifest_path),
                   'data/interim/data_quality_2023_24.json':manifest['quality_sha256'],
                   'requirements.txt':manifest['requirements_sha256']})
    return teams,games,outcomes,hashes
