"""Independent scalar checks and reviewable real-data worked examples; offline."""
from datetime import timedelta
import json
import math
from pathlib import Path
import sys

import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.feature_io import load_inputs
from nba_game_prediction.features import FEATURES


def scalar_expected(prior,current_date):
    n=len(prior)
    expected={'games_played_before':n,'season_win_pct_before':sum(r['win'] for r in prior)/n if n else None,
              'rest_days':(current_date-prior[-1]['date']).days-1 if n else None,
              'games_last_7_days':sum(current_date-timedelta(days=7)<=r['date']<current_date for r in prior)}
    expected['is_back_to_back']=int(expected['rest_days']==0)
    for window in [5,10]:
        last=prior[-window:]
        for name,key in [('win_pct','win'),('point_diff_avg','point_diff'),('pts_for_avg','pts_for'),('pts_against_avg','pts_against')]:
            expected[f'{name}_last_{window}']=sum(r[key] for r in last)/window if n>=window else None
    return expected


def main():
    teams,games,outcomes,_=load_inputs(ROOT)
    tf=pd.read_parquet(ROOT/'data/interim/team_pregame_features_2023_24.parquet')
    gf=pd.read_parquet(ROOT/'data/processed/game_features_2023_24.parquet')
    results={(r.game_id,int(r.team_id)):r for r in tf.itertuples()}
    scores=games.set_index('game_id')
    sequence={};comparisons=0
    for tid,t in teams.groupby('team_id',sort=True):
        t=t.sort_values('game_date');prior=[]
        sequence[int(tid)]=[]
        for r in t.itertuples():
            expected=scalar_expected(prior,r.game_date)
            got=results[(r.game_id,int(tid))]
            for col in FEATURES:
                value=getattr(got,col);answer=expected[col]
                if answer is None:assert pd.isna(value),(r.game_id,tid,col,value,answer)
                else:assert not pd.isna(value) and math.isclose(float(value),float(answer),rel_tol=0,abs_tol=1e-12),(r.game_id,tid,col,value,answer)
                comparisons+=1
            assert all(p['date']<r.game_date for p in prior)
            sequence[int(tid)].append({'row':r,'expected':expected,'prior':list(prior)})
            g=scores.loc[r.game_id]
            against=int(g.away_pts if r.is_home else g.home_pts)
            prior.append({'game_id':r.game_id,'date':r.game_date,'opponent':r.opponent_team_abbreviation,
                          'pts_for':int(r.pts),'pts_against':against,'point_diff':int(r.pts)-against,'win':int(r.wl=='W')})
    # Exact output identities and target-table separation.
    identity=['season','season_type','game_id','game_date','home_team_id','home_team_name','home_team_abbreviation','away_team_id','away_team_name','away_team_abbreviation']
    pd.testing.assert_frame_equal(gf[identity],games.sort_values(['game_date','game_id']).reset_index(drop=True)[identity])
    lakers=sequence[1610612747]
    b2b=next(x for x in lakers[10:] if x['expected']['is_back_to_back']==1)
    dense=max((x for seq in sequence.values() for x in seq[10:]),key=lambda x:x['expected']['games_last_7_days'])
    choices=[('season_opener',lakers[0]),('sixth_game',lakers[5]),('eleventh_game',lakers[10]),('back_to_back',b2b),('dense_recent_schedule',dense)]
    manual=[]
    for label,x in choices:
        r=x['row'];prior=x['prior'];expected=x['expected'];n=len(prior)
        source=[dict(v,date=v['date'].strftime('%Y-%m-%d')) for v in prior]
        calculations={}
        for window in [5,10]:
            last=prior[-window:]
            if n<window:
                calculations[str(window)]={'status':f'missing: only {n} prior games, requires {window}'}
            else:
                calculations[str(window)]={
                    'game_ids':[p['game_id'] for p in last],
                    'win_pct_arithmetic':f"{sum(p['win'] for p in last)} / {window} = {expected[f'win_pct_last_{window}']}",
                    'point_diff_arithmetic':f"({' + '.join(str(p['point_diff']) for p in last)}) / {window} = {expected[f'point_diff_avg_last_{window}']}",
                    'points_for_arithmetic':f"{sum(p['pts_for'] for p in last)} / {window} = {expected[f'pts_for_avg_last_{window}']}",
                    'points_against_arithmetic':f"{sum(p['pts_against'] for p in last)} / {window} = {expected[f'pts_against_avg_last_{window}']}",
                }
        manual.append({'case':label,'team':r.team_abbreviation,'team_id':int(r.team_id),'target_game_id':r.game_id,
                       'target_date':r.game_date.strftime('%Y-%m-%d'),'all_prior_games':source,
                       'last_7_days_game_ids':[p['game_id'] for p in prior if r.game_date-timedelta(days=7)<=p['date']<r.game_date],
                       'features_independently_checked':expected,'rolling_arithmetic':calculations,
                       'rest_arithmetic':f"({r.game_date.strftime('%Y-%m-%d')} - {prior[-1]['date'].strftime('%Y-%m-%d')}).days - 1 = {expected['rest_days']}" if n else 'missing: no prior season game',
                       'matched_output':True})
    output={'method':'Independent Python list slicing, sums and calendar arithmetic; no rolling/shift implementation reused.',
            'all_team_feature_scalar_comparisons':comparisons,'all_comparisons_passed':True,
            'all_game_identities_match_stage1a':True,'manual_examples':manual}
    (ROOT/'docs/stage1b_evidence/manual_checks.json').write_text(json.dumps(output,indent=2)+'\n')
    for m in manual:print(json.dumps({k:m[k] for k in ['case','team','target_game_id','target_date','features_independently_checked','rolling_arithmetic','rest_arithmetic']}))
    print(f'Passed {comparisons} independent scalar comparisons.')


if __name__=='__main__':main()
