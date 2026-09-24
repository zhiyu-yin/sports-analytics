from pathlib import Path
import sys,unittest
from unittest.mock import patch
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.elo import Parameters,probability,regress,replay,select_parameters,fit_constant,TRAIN
from nba_game_prediction.evaluation import load_games,verify_inputs
from nba_game_prediction.metrics import evaluate,calibration

def fixture(seasons=('2022-23','2023-24'),count=4):
    rows=[]
    for season in seasons:
        for i,date in enumerate(pd.date_range(season[:4]+'-12-26',periods=count)):
            rows.append(dict(season=season,game_id='002'+season[2:4]+f'{i+1:05d}',game_date=date,home_team_id=1 if i%2==0 else 2,away_team_id=2 if i%2==0 else 1,home_win=i%3!=0))
    return pd.DataFrame(rows)
class EloTests(unittest.TestCase):
    def setUp(self):self.data=fixture();self.params=Parameters(20,75,.75)
    def test_A_prediction_before_update(self):
        a=replay(self.data,self.params)
        for row in a.itertuples():
            self.assertEqual(row.predicted_home_probability,probability(row.home_rating_before,row.away_rating_before,75))
            self.assertAlmostEqual(row.rating_delta,20*(row.home_win-row.predicted_home_probability))
        self.assertEqual(a.iloc[0].home_rating_before,1500)
    def test_B_target_mutation(self):
        changed=self.data.copy();changed.loc[1,'home_win']=not changed.loc[1,'home_win']
        a=replay(self.data,self.params);b=replay(changed,self.params)
        assert_frame_equal(a.iloc[:2][['home_rating_before','away_rating_before','predicted_home_probability']],b.iloc[:2][['home_rating_before','away_rating_before','predicted_home_probability']],check_exact=True)
        self.assertNotEqual(a.iloc[2].predicted_home_probability,b.iloc[2].predicted_home_probability)
    def test_C_future_mutation(self):
        changed=self.data.copy();changed.loc[6,'home_win']=not changed.loc[6,'home_win']
        assert_frame_equal(replay(self.data,self.params).iloc[:6],replay(changed,self.params).iloc[:6],check_exact=True)
    def test_D_shuffle(self):
        assert_frame_equal(replay(self.data,self.params),replay(self.data.sample(frac=1,random_state=4),self.params),check_exact=True)
    def test_E_zero_sum(self):
        a=replay(self.data,self.params)
        for row in a.itertuples():self.assertAlmostEqual(row.home_rating_before+row.away_rating_before,row.home_rating_after+row.away_rating_after,places=12)
    def test_F_probability_bounds(self):
        a=replay(self.data,self.params);self.assertTrue(a.predicted_home_probability.between(0,1,inclusive='neither').all())
    def test_G_equal_no_advantage(self):self.assertEqual(probability(1500,1500,0),.5)
    def test_H_advantage_direction(self):self.assertGreater(probability(1500,1500,75),.5)
    def test_I_season_regression(self):
        a=replay(self.data,self.params);end=a.iloc[3];start=a.iloc[4]
        state={end.home_team_id:end.home_rating_after,end.away_team_id:end.away_rating_after}
        self.assertEqual(start.home_rating_before,1500+.75*(state[start.home_team_id]-1500))
        self.assertEqual(start.away_rating_before,1500+.75*(state[start.away_team_id]-1500))
        self.assertEqual(regress(1700,0),1500);self.assertEqual(regress(1700,1),1700)
    def test_J_parameter_isolation(self):
        data=fixture(TRAIN+('2023-24',));changed=data.copy();changed['home_win']=changed.home_win.astype('boolean');changed.loc[changed.season.eq('2023-24'),'home_win']=pd.NA
        grid={'K':[10,20],'H':[0,75],'alpha':[.5,1.]}
        a,ga,fa=select_parameters(data,grid);b,gb,fb=select_parameters(changed,grid)
        self.assertEqual(a,b);assert_frame_equal(ga,gb,check_exact=True);assert_frame_equal(fa,fb,check_exact=True)
    def test_K_preholdout_guard(self):
        sealed=fixture(('2024-25',));sealed['p']=.5
        for fn in [lambda:evaluate(sealed,'p'),lambda:calibration(sealed,'p'),lambda:replay(sealed,self.params),lambda:select_parameters(sealed),lambda:fit_constant(sealed)]:
            with self.assertRaisesRegex(ValueError,'sealed'):fn()
    def test_L_holdout_before_access(self):
        with patch('nba_game_prediction.evaluation.verify_inputs',side_effect=AssertionError('Must not access data')):
            for season in ['2024-25','2025-26']:
                with self.assertRaisesRegex(ValueError,'sealed'):load_games('/does/not/exist',[season])
    def test_same_team_date_guard(self):
        d=self.data.copy();d.loc[1,'game_date']=d.loc[0,'game_date']
        with self.assertRaisesRegex(ValueError,'Same-team/date'):replay(d,self.params)
    def test_game_id_not_time_order(self):
        d=self.data.copy();ids=list(reversed(d.loc[:3,'game_id'].tolist()));d.loc[:3,'game_id']=ids
        self.assertEqual(replay(d,self.params).predicted_home_probability.tolist(),replay(self.data,self.params).predicted_home_probability.tolist())
    def test_scores_and_features_unused(self):
        d=self.data.copy();d['home_pts']=99999;d['away_pts']=-999;d['home_win_pct_last_5']=.999
        assert_frame_equal(replay(d,self.params),replay(self.data,self.params),check_exact=True)
    def test_invalid_parameters(self):
        for args in [(0,75,.75),(20,75,1.01),(20,-1,.75),(20,float('nan'),.5)]:
            with self.assertRaises(ValueError):Parameters(*args)
    def test_nonbinary_outcome_rejected(self):
        d=self.data.copy();d['home_win']=2
        with self.assertRaises(ValueError):replay(d,self.params)
    def test_constant_training_only(self):
        d=fixture();p=fit_constant(d)
        self.assertEqual(p['training_games'],4);self.assertEqual(p['training_home_wins'],2);self.assertEqual(p['p_home_train'],.5)
        d['home_win']=d.home_win.astype('boolean');d.loc[d.season.eq('2023-24'),'home_win']=pd.NA;self.assertEqual(fit_constant(d),p)
        d.loc[0,'home_win']=True;self.assertEqual(fit_constant(d)['p_home_train'],.75)
    def test_real_validation_constant_and_sealed_outputs(self):
        root=Path(__file__).resolve().parents[1]
        p=pd.read_parquet(root/'data/processed/stage2_predictions_2023_24.parquet')
        a=pd.read_parquet(root/'data/interim/stage2_elo_game_log.parquet')
        self.assertEqual(set(p.season),{'2023-24'});self.assertEqual(len(p),1230)
        self.assertEqual(p.constant_probability.nunique(),1)
        self.assertNotIn('2024-25',set(a.season));self.assertFalse(set(p)&{'home_pts','away_pts'})
    def test_loader_projection_and_sealed_label_exclusion(self):
        root=Path(__file__).resolve().parents[1]
        original=pd.read_parquet
        with patch('nba_game_prediction.evaluation.pd.read_parquet',wraps=original) as reader:
            loaded=load_games(root,TRAIN)
        self.assertEqual(len(loaded),9519)
        for call in reader.call_args_list:
            columns=call.kwargs['columns']
            self.assertFalse(set(columns)&{'home_pts','away_pts','home_win_pct_last_5'})
            if 'home_win' in columns:
                self.assertEqual(call.kwargs['filters'],[('season','in',list(TRAIN))])
    def test_provenance_failure_before_dataframe_access(self):
        root=Path(__file__).resolve().parents[1]
        with patch('nba_game_prediction.evaluation.digest',return_value='corrupt'),patch('nba_game_prediction.evaluation.pd.read_parquet',side_effect=AssertionError('Must stop before data read')):
            with self.assertRaisesRegex(ValueError,'provenance mismatch'):verify_inputs(root)
if __name__=='__main__':unittest.main()
