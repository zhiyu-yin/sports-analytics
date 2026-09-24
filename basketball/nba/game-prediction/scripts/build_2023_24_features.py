"""Offline-only Stage 1B build from checksum-verified Stage 1A Parquet inputs."""
from datetime import datetime,timezone
from importlib.metadata import version
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.feature_io import load_inputs,digest
from nba_game_prediction.features import build_features,feature_dictionary,FEATURES,GAME_FEATURES,VERSION


def json_file(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def main():
    # All provenance and structural checks finish BEFORE any output is written.
    teams,games,outcomes,input_hashes=load_inputs(ROOT)
    tf,gf=build_features(teams,games,outcomes)
    evidence=ROOT/'docs/stage1b_evidence'
    evidence.mkdir(parents=True,exist_ok=True)
    output_paths=[ROOT/'data/interim/team_pregame_features_2023_24.parquet',ROOT/'data/processed/game_features_2023_24.parquet']
    for path,frame in zip(output_paths,[tf,gf]):
        path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_suffix('.parquet.tmp')
        frame.to_parquet(temp,index=False,engine='pyarrow');temp.replace(path)
    dictionary=ROOT/'docs/stage1b_feature_dictionary.csv'
    feature_dictionary().to_csv(dictionary,index=False,lineterminator='\n')
    quality={
        'definition_version':VERSION,'team_rows':len(tf),'game_rows':len(gf),
        'team_count':int(tf.team_id.nunique()),'team_features':FEATURES,'game_features':GAME_FEATURES,
        'team_missing_counts':{c:int(tf[c].isna().sum()) for c in FEATURES},
        'game_missing_counts':{c:int(gf[c].isna().sum()) for c in GAME_FEATURES},
        'team_rows_missing_last_5':int(tf.win_pct_last_5.isna().sum()),
        'team_rows_missing_last_10':int(tf.win_pct_last_10.isna().sum()),
        'team_rows_missing_rest':int(tf.rest_days.isna().sum()),
        'game_rows_missing_either_last_5':int(gf[['home_win_pct_last_5','away_win_pct_last_5']].isna().any(axis=1).sum()),
        'game_rows_missing_either_last_10':int(gf[['home_win_pct_last_10','away_win_pct_last_10']].isna().any(axis=1).sum()),
        'game_rows_missing_either_rest':int(gf[['home_rest_days','away_rest_days']].isna().any(axis=1).sum()),
        'same_team_date_duplicates':int(teams.duplicated(['team_id','game_date']).sum()),
        'early_games_dropped':0,'imputation_performed':False,
        'negative_rest_rows':int(tf.rest_days.lt(0).sum()),
        'back_to_back_team_rows':int(tf.is_back_to_back.sum()),
        'team_schema':{c:str(t) for c,t in tf.dtypes.items()},
        'game_schema':{c:str(t) for c,t in gf.dtypes.items()},
    }
    json_file(evidence/'feature_quality.json',quality)
    # Compact complete lineage: row i uses only this team's entries [:i].
    lineage=[]
    for tid,t in tf.groupby('team_id',sort=True):
        t=t.sort_values('game_date')
        lineage.append({'team_id':int(tid),'team_abbreviation':str(t.team_abbreviation.iloc[0]),
                        'games':[{'game_id':str(r.game_id),'game_date':r.game_date.strftime('%Y-%m-%d')} for r in t.itertuples()]})
    json_file(evidence/'team_history_lineage.json',{'rule':'For target at position i, season history is [:i], last n is [max(0,i-n):i], schedule uses earlier dates only. Full rolling window required.','teams':lineage})
    outputs=output_paths+[dictionary,evidence/'feature_quality.json',evidence/'team_history_lineage.json']
    codes=[ROOT/'src/nba_game_prediction'/name for name in ['features.py','schedule.py','feature_io.py']]+[Path(__file__)]
    manifest={'definition_version':VERSION,'build_timestamp_utc':datetime.now(timezone.utc).isoformat(),
              'input_sha256':input_hashes,'source_code_sha256':{str(p.relative_to(ROOT)):digest(p) for p in codes},
              'output_sha256':{str(p.relative_to(ROOT)):digest(p) for p in outputs},
              'row_counts':{'team_features':len(tf),'game_features':len(gf)},
              'output_schema':{'team_features':quality['team_schema'],'game_features':quality['game_schema']},
              'versions':{p:version(p) for p in ['pandas','numpy','pyarrow']},
              'contract_sha256':digest(ROOT/'docs/stage1b_availability_contract.md'),
              'determinism':'Data/dictionary/quality/lineage deterministic; build timestamp intentionally varies.'}
    json_file(evidence/'build_manifest.json',manifest)
    print(json.dumps({k:quality[k] for k in ['team_rows','game_rows','team_rows_missing_last_5','team_rows_missing_last_10','team_rows_missing_rest','game_rows_missing_either_last_5','game_rows_missing_either_last_10','game_rows_missing_either_rest']},indent=2))


if __name__=='__main__':main()
