"""Offline-only Stage 1D build; historical Stage 1C artifacts stay immutable."""
from pathlib import Path
import json
import pandas as pd
from .ingest import retrieve,extract_table
from .normalize import normalize
from .validate import validate_and_pair
from .features import build_features,VERSION
from .seasons import SCOPES
from .reconciliation import load_approved,apply_reconciliation
from .multiseason import digest,write_json,save_table,audit_scope,combine_validated,missingness,regression_2023,verify_protected


def protected(root):
    for path,expected in json.loads((root/'docs/stage1d_evidence/protected_before.json').read_text()).items():
        if digest(root/path)!=expected:raise ValueError('Earlier artifact changed: '+path)
    verify_protected(root)


def build(root):
    from .sealed_access import require_seasons
    require_seasons(['2024-25'], 'historical Stage 1D build')
    root=Path(root);e=root/'docs/stage1d_evidence';protected(root)
    approved=load_approved(root);results=[];qualities=[];comparisons=[];hashes={};miss=[];raw_hashes={}
    for season in SCOPES:
        body,meta,_=retrieve(root/'data/raw'/season,season=season)
        raw_hashes[season]=meta['sha256'];norm=normalize(body,season=season)
        applied=[]
        if season=='2024-25':norm,applied=apply_reconciliation(norm,approved)
        teams,games,anomalies=validate_and_pair(norm,season=season)
        cols,rows=extract_table(body)
        q,scope=audit_scope(pd.DataFrame(rows,columns=cols),norm,teams,games,anomalies,season)
        if q['status']!='validated':raise ValueError('Season remains quarantined: '+season+' '+str(scope['completeness_issues']))
        y=games[['game_id','home_pts','away_pts','home_win']].copy();tf,gf=build_features(teams,games,y)
        tables=dict(team_games=teams,games=games,game_outcomes=y,team_pregame_features=tf,game_features=gf)
        suffix=season.replace('-','_')
        if season!='2024-25':
            for name,frame in tables.items():
                path=root/(f'data/processed/seasons/{name}_{suffix}.parquet' if name=='game_features' else f'data/interim/seasons/{name}_{suffix}.parquet')
                pd.testing.assert_frame_equal(frame,pd.read_parquet(path),check_exact=True)
                comparisons.append({'season':season,'table':name,'values_dtypes_equal':True,'sha256':digest(path)})
            if season=='2023-24':write_json(e/'regression_2023_24.json',regression_2023(root,tables))
        else:
            for name,frame in dict(tables,game_anomalies=anomalies).items():
                path=root/f'data/interim/reconciled/{name}_{suffix}.parquet'
                save_table(path,frame);hashes[str(path.relative_to(root))]=digest(path)
            save_table(root/'data/processed/seasons/game_features_2024_25.parquet',gf)
            hashes['data/processed/seasons/game_features_2024_25.parquet']=digest(root/'data/processed/seasons/game_features_2024_25.parquet')
            write_json(e/'reconciliation_validation.json',{'admitted':True,'applied_game_ids':applied,'accepted_games':len(games),'team_rows':len(teams),'rejected_games':q['rejected_games'],'warnings':q['warning_count'],'games_per_team':scope['games_per_team'],'source_scores_wl_and_matchups_preserved':True,'full_scope_audit':scope})
        q.update(reconciled_games=len(applied),feature_rows=len(gf),neutral_site_known_count=5 if season=='2024-25' else (88 if season=='2019-20' else None),neutral_site_coverage='complete official schedule' if season=='2024-25' else ('bubble subset only; lower bound' if season=='2019-20' else 'not independently audited'),last5_missing_game_rows=int(gf[['home_win_pct_last_5','away_win_pct_last_5']].isna().any(axis=1).sum()),last10_missing_game_rows=int(gf[['home_win_pct_last_10','away_win_pct_last_10']].isna().any(axis=1).sum()),regression_status='exact_values_dtypes_sha256' if season!='2024-25' else 'newly_admitted')
        qualities.append(q);results.append(tables);miss.extend(missingness(season,tables))
        print(season,len(games),'reconciled',len(applied),flush=True)
    gf,y,maps=combine_validated(results)
    # Existing combined slices also match exactly before publishing the new total.
    for old,new in [('stage1c_game_features_multiseason.parquet',gf),('stage1c_game_outcomes_multiseason.parquet',y)]:
        pd.testing.assert_frame_equal(pd.read_parquet(root/'data/interim'/old),new[new.season.ne('2024-25')].reset_index(drop=True),check_exact=True)
    for relative,frame in [('data/processed/game_features_multiseason.parquet',gf),('data/interim/game_outcomes_multiseason.parquet',y)]:
        save_table(root/relative,frame);hashes[relative]=digest(root/relative)
    for name,frame in [('multiseason_quality_after_reconciliation.csv',pd.DataFrame(qualities)),('missingness_by_season.csv',pd.DataFrame(miss)),('team_identity_by_season.csv',maps)]:
        frame.to_csv(e/name,index=False);hashes[str((e/name).relative_to(root))]=digest(e/name)
    write_json(e/'regression_pre_2024_25.json',{'passed':True,'comparisons':comparisons,'prior_combined_slices_exact':True,'protected_files_unchanged':True})
    protected(root)
    code=list((root/'src/nba_game_prediction').glob('*.py'))+[root/'scripts/build_reconciled_multiseason.py']
    manifest={'build_version':'1D.1','feature_definition_version':VERSION,'admitted_seasons':list(SCOPES),'combined_games':len(gf),'raw_sha256':raw_hashes,'output_sha256':hashes,'code_sha256':{str(p.relative_to(root)):digest(p) for p in code},'requirements_sha256':digest(root/'requirements.txt'),'reconciliation_input_sha256':json.loads((e/'reconciliation_inputs_sha256.json').read_text()),'feature_schema':{c:str(d) for c,d in gf.dtypes.items()},'outcome_schema':{c:str(d) for c,d in y.dtypes.items()}}
    write_json(e/'build_manifest.json',manifest);return manifest
