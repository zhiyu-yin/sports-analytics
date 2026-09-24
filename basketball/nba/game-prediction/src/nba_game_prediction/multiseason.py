"""Season-by-season ingestion, explicit completeness audit, and isolated features."""
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
from io import BytesIO
import json
from pathlib import Path
import time

import pandas as pd
from .ingest import retrieve, read_cache, extract_table
from .normalize import normalize
from .validate import validate_and_pair
from .features import build_features, FEATURES, GAME_FEATURES, VERSION, GAME_IDENTITIES
from .seasons import get_scope

BUILD_VERSION = '1C.1'


def digest(path):
    from .sealed_access import checksum
    return checksum(path)


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');temp.replace(path)


def save_table(path,frame):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.parquet.tmp')
    frame.to_parquet(temp,index=False,engine='pyarrow');temp.replace(path)


def verify_protected(root):
    path=root/'docs/stage1c_evidence/protected_2023_24_sha256.json'
    for relative,expected in json.loads(path.read_text()).items():
        if digest(root/relative)!=expected:
            raise ValueError(f'Protected 2023-24 artifact changed: {relative}; stop')


def regression_2023(root, tables):
    paths={
        'team_games':'data/interim/team_games_2023_24.parquet',
        'games':'data/interim/games_2023_24.parquet',
        'game_outcomes':'data/interim/game_outcomes_2023_24.parquet',
        'team_pregame_features':'data/interim/team_pregame_features_2023_24.parquet',
        'game_features':'data/processed/game_features_2023_24.parquet',
    }
    checks=[]
    for name,relative in paths.items():
        reference=pd.read_parquet(root/relative)
        pd.testing.assert_frame_equal(tables[name],reference,check_exact=True)
        buffer=BytesIO();tables[name].to_parquet(buffer,index=False,engine='pyarrow')
        checksum=sha256(buffer.getvalue()).hexdigest()
        if checksum!=digest(root/relative):raise ValueError('2023-24 serialization regression: '+name)
        checks.append({'table':name,'value_dtype_equal':True,'sha256_equal':True,'sha256':checksum})
    return {'passed':True,'used_existing_raw_cache':True,'comparisons':checks}


def acquire(root,season,fetch):
    """Cache corruption is fatal; only a source request failure may be retried."""
    from .sealed_access import require_seasons
    require_seasons([season], 'raw outcomes')
    folder=root/'data/raw'/season
    cached=read_cache(folder,season=season)
    if cached:return *cached,True
    if not fetch:raise FileNotFoundError(f'No cached source for {season}')
    for attempt in range(2):
        time.sleep(3 if attempt==0 else 10)
        try:return retrieve(folder,season=season,allow_network=True)
        except RuntimeError:
            if attempt==1:raise


def audit_scope(raw,normalized,teams,games,anomalies,season):
    scope=get_scope(season)
    counts=teams.groupby('team_id').size()
    rejected=anomalies.loc[anomalies.severity.eq('reject')]
    warnings=anomalies.loc[anomalies.severity.eq('warning')]
    problems=[]
    if len(counts)!=30:problems.append('not_30_teams')
    if len(rejected):problems.append('rejected_games_break_history')
    if teams.empty or teams.game_date.min()!=pd.Timestamp(scope.start) or teams.game_date.max()!=pd.Timestamp(scope.end):
        problems.append('season_date_endpoints_incomplete')
    if scope.games_per_team is not None and not counts.eq(scope.games_per_team).all():
        problems.append('documented_games_per_team_not_met')
    if normalized.duplicated(['team_id','game_date']).any():
        raise ValueError(f'Same-team/date ambiguity in {season}; stop before features')
    bubble_counts={}
    if scope.bubble_start:
        bubble=teams[teams.game_date.ge(pd.Timestamp(scope.bubble_start))]
        bubble_counts={str(k):int(v) for k,v in bubble.groupby('team_id').size().items()}
        # NBA's published historical total + documented 22 teams × 8 seeding games.
        if len(games)!=1059 or not counts.between(63,75).all():problems.append('restart_season_count_mismatch')
        if len(bubble_counts)!=22 or set(bubble_counts.values())!={8}:problems.append('seeding_games_incomplete')
    detail={
        'season':season,'configuration':asdict(scope),'completeness_issues':problems,
        'games_per_team':{str(k):int(v) for k,v in counts.items()},
        'games_per_team_distribution':{str(k):int(v) for k,v in counts.value_counts().sort_index().items()},
        'raw_column_null_counts':{c:int(v) for c,v in raw.isna().sum().items()},
        'source_season_ids':raw.SEASON_ID.astype(str).value_counts().to_dict(),
        'source_game_prefixes':raw.GAME_ID.astype(str).str[:5].value_counts().to_dict(),
        'anomaly_reasons':{str(k):int(v) for k,v in anomalies.reason.value_counts().items()},
        'bubble_team_counts':bubble_counts,
        'cup_championship_date_rows':int(normalized.game_date.eq(pd.Timestamp(scope.cup_final)).sum()) if scope.cup_final else 0,
        'within_season_team_identity_map':teams[['team_id','team_name','team_abbreviation']].drop_duplicates().sort_values('team_id').to_dict('records'),
    }
    quality={
        'season':season,'team_game_rows':len(raw),'unique_games':int(raw.GAME_ID.nunique()),
        'number_of_teams':len(counts),'min_games_per_team':int(counts.min()) if len(counts) else None,
        'max_games_per_team':int(counts.max()) if len(counts) else None,
        'first_game_date':normalized.game_date.min().strftime('%Y-%m-%d'),
        'last_game_date':normalized.game_date.max().strftime('%Y-%m-%d'),
        'accepted_games':len(games),'rejected_games':int(rejected.game_id.nunique()),
        'warning_count':len(warnings),'warning_games':int(warnings.game_id.nunique()),
        'raw_null_count':int(raw.isna().sum().sum()),'feature_rows':0,
        'last5_missing_game_rows':None,'last10_missing_game_rows':None,
        'regression_status':'pending' if season=='2023-24' else 'not_applicable',
        'status':'quarantined' if problems else 'validated',
    }
    return quality,detail


def build_season_games(root,season,fetch=False):
    root=Path(root);get_scope(season)
    body,meta,cached=acquire(root,season,fetch)
    columns,rows=extract_table(body);raw=pd.DataFrame(rows,columns=columns)
    normalized=normalize(body,season=season)
    teams,games,anomalies=validate_and_pair(normalized,season=season)
    outcomes=games[['game_id','home_pts','away_pts','home_win']].copy()
    quality,scope=audit_scope(raw,normalized,teams,games,anomalies,season)
    tables={'team_games':teams,'games':games,'game_outcomes':outcomes,'game_anomalies':anomalies}
    if quality['status']=='validated':
        tf,gf=build_features(teams,games,outcomes)
        tables.update(team_pregame_features=tf,game_features=gf)
        quality.update(feature_rows=len(gf),last5_missing_game_rows=int(gf[['home_win_pct_last_5','away_win_pct_last_5']].isna().any(axis=1).sum()),
                       last10_missing_game_rows=int(gf[['home_win_pct_last_10','away_win_pct_last_10']].isna().any(axis=1).sum()))
        if season=='2023-24':
            regression=regression_2023(root,tables)
            write_json(root/'docs/stage1c_evidence/regression_2023_24.json',regression)
            quality['regression_status']='exact_values_dtypes_sha256'
    suffix=season.replace('-','_');artifacts={}
    for name,frame in tables.items():
        relative=f'data/processed/seasons/game_features_{suffix}.parquet' if name=='game_features' else f'data/interim/seasons/{name}_{suffix}.parquet'
        save_table(root/relative,frame);artifacts[relative]=digest(root/relative)
    return tables,quality,scope,meta,artifacts


def missingness(season,tables):
    records=[]
    for label,frame,features in [('team',tables['team_pregame_features'],FEATURES),('game',tables['game_features'],GAME_FEATURES)]:
        for col in features:records.append({'season':season,'table':label,'feature':col,'missing_rows':int(frame[col].isna().sum()),'total_rows':len(frame)})
    return records


def combine_validated(results):
    features=pd.concat([t['game_features'] for t in results],ignore_index=True).sort_values(['season','game_date','game_id']).reset_index(drop=True)
    outcomes=pd.concat([t['games'][['season','game_id','home_pts','away_pts','home_win','game_date']] for t in results],ignore_index=True).sort_values(['season','game_date','game_id']).drop(columns='game_date').reset_index(drop=True)
    if not features.game_id.is_unique or not outcomes.game_id.is_unique:raise ValueError('Cross-season duplicate game ID')
    if not features.game_id.equals(outcomes.game_id) or not features.season.equals(outcomes.season):raise ValueError('Combined feature/outcome keys differ')
    if list(features)!=GAME_IDENTITIES+GAME_FEATURES:raise ValueError('Combined feature schema/outcome contamination')
    teams=pd.concat([t['team_games'] for t in results],ignore_index=True)
    maps=teams[['season','team_id','team_name','team_abbreviation']].drop_duplicates()
    if maps.duplicated(['season','team_id']).any() or maps.duplicated(['season','team_abbreviation']).any():raise ValueError('Ambiguous within-season identity mapping')
    ids=[set(t.team_id) for _,t in teams.groupby('season')]
    if any(s!=ids[0] for s in ids):raise ValueError('Team ID membership changed; explicit franchise review required')
    # Names may change across seasons; team_id remains the joining entity.
    return features,outcomes,maps.sort_values(['season','team_id']).reset_index(drop=True)


def build_multi(root,seasons,fetch=False,allow_partial=False):
    from .sealed_access import require_seasons
    seasons=list(seasons);require_seasons(seasons, 'multi-season build')
    root=Path(root)
    for season in seasons:get_scope(season)
    if len(seasons)!=len(set(seasons)):raise ValueError('Duplicate requested season')
    verify_protected(root)
    evidence=root/'docs/stage1c_evidence';evidence.mkdir(parents=True,exist_ok=True)
    # Test the protected case first, even when building a different requested season.
    body,_,_=retrieve(root/'data/raw/2023-24',season='2023-24')
    t,g,_=validate_and_pair(normalize(body),season='2023-24');y=g[['game_id','home_pts','away_pts','home_win']].copy()
    tf,gf=build_features(t,g,y)
    write_json(evidence/'regression_2023_24.json',regression_2023(root,dict(team_games=t,games=g,game_outcomes=y,team_pregame_features=tf,game_features=gf)))
    quality=[];scopes=[];retrieval=[];all_tables=[];miss=[];hashes={};raw_hashes={};failed=[]
    for season in sorted(seasons):
        try:
            tables,q,scope,meta,outputs=build_season_games(root,season,fetch)
        except (RuntimeError,FileNotFoundError) as exc:
            # These are explicit acquisition failures. Integrity/leakage errors propagate.
            if not allow_partial:raise
            failed.append({'season':season,'status':'retrieval_failed','reason':str(exc)})
            quality.append({'season':season,'status':'retrieval_failed','regression_status':'not_applicable'})
            continue
        quality.append(q);scopes.append(scope);retrieval.append(meta);hashes.update(outputs)
        raw_hashes[f'data/raw/{season}/{meta["raw_file"]}']=meta['sha256']
        if q['status']!='validated':
            failed.append({'season':season,'status':'quarantined','reason':scope['completeness_issues']})
            if not allow_partial:raise ValueError(f'Season {season} quarantined: {scope["completeness_issues"]}')
            print(season,'quarantined',scope['completeness_issues'],flush=True)
            continue
        all_tables.append(tables);miss.extend(missingness(season,tables))
        print(season,'accepted',q['accepted_games'],'warnings',q['warning_count'],flush=True)
    if not all_tables:raise ValueError('No validated seasons; combined output not published')
    gf,outcomes,maps=combine_validated(all_tables)
    for relative,frame in [('data/processed/game_features_multiseason.parquet',gf),('data/interim/game_outcomes_multiseason.parquet',outcomes)]:
        save_table(root/relative,frame);hashes[relative]=digest(root/relative)
    for filename,frame in [('season_quality.csv',pd.DataFrame(quality)),('missingness_by_season.csv',pd.DataFrame(miss)),('team_identity_by_season.csv',maps)]:
        frame.to_csv(evidence/filename,index=False,lineterminator='\n');hashes[str((evidence/filename).relative_to(root))]=digest(evidence/filename)
    for filename,value in [('scope_audit.json',scopes),('retrieval_manifest.json',{'requested_seasons':seasons,'retrieved':retrieval,'failed_or_quarantined':failed})]:
        write_json(evidence/filename,value);hashes[str((evidence/filename).relative_to(root))]=digest(evidence/filename)
    verify_protected(root)
    codes=list((root/'src/nba_game_prediction').glob('*.py'))+list((root/'scripts').glob('build_*season*.py'))
    manifest={'build_version':BUILD_VERSION,'feature_definition_version':VERSION,'built_at_utc':datetime.now(timezone.utc).isoformat(),
              'requested_seasons':seasons,'validated_seasons':sorted(gf.season.unique().tolist()),'failed_or_quarantined':failed,
              'combined_games':len(gf),'feature_schema':{c:str(d) for c,d in gf.dtypes.items()},'outcome_schema':{c:str(d) for c,d in outcomes.dtypes.items()},
              'raw_sha256':raw_hashes,'source_code_sha256':{str(p.relative_to(root)):digest(p) for p in sorted(codes)},
              'requirements_sha256':digest(root/'requirements.txt'),'output_sha256':hashes,
              'versions':{p:version(p) for p in ['nba_api','pandas','numpy','pyarrow']},
              'policy':'Season-reset v1.0.0; strict by default, explicit allow-partial quarantines whole seasons; no holdout access.'}
    write_json(evidence/'multiseason_build_manifest.json',manifest)
    print('Combined',len(gf),'games from',len(all_tables),'validated seasons.',flush=True)
    return manifest
