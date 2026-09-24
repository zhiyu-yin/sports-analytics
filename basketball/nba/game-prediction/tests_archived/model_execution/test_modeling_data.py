from pathlib import Path
import sys,json,unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_logistic import fixture
from nba_game_prediction.modeling_data import load_modeling_data,add_frozen_elo,verify_frozen,enforce_frozen,FROZEN
from nba_game_prediction.policy import TRAIN
from nba_game_prediction.metrics import evaluate
ROOT=Path(__file__).resolve().parents[1]
class ModelingDataTests(unittest.TestCase):
    def test_elo_logit_is_pregame_transform(self):
        d=fixture();np.testing.assert_array_equal(d.elo_logit,np.log(d.raw_elo_probability/(1-d.raw_elo_probability)))
    def test_target_mutation_own_logit(self):
        d=fixture(('2022-23',));a=d.drop(columns=['raw_elo_probability','elo_logit']).copy();a.loc[2,'home_win']=not a.loc[2,'home_win'];b=add_frozen_elo(a)
        self.assertEqual(d.loc[2,'elo_logit'],b.loc[2,'elo_logit']);self.assertNotEqual(d.loc[3,'elo_logit'],b.loc[3,'elo_logit'])
    def test_future_mutation_earlier_logit(self):
        d=fixture(('2022-23',));a=d.drop(columns=['raw_elo_probability','elo_logit']).copy();a.loc[8,'home_win']=not a.loc[8,'home_win'];b=add_frozen_elo(a)
        np.testing.assert_array_equal(d.loc[:7,'elo_logit'],b.loc[:7,'elo_logit'])
    def test_frozen_parameters_enforced(self):
        for key,value in [('K',30),('H',75),('alpha',.75)]:
            p=dict(FROZEN);p[key]=value
            with self.assertRaisesRegex(ValueError,'frozen'):enforce_frozen(p)
    def test_stage2_protected(self):self.assertEqual(verify_frozen(ROOT)['parameters'],FROZEN)
    def test_sealed_and_holdout_before_access(self):
        with patch('nba_game_prediction.modeling_data.verify_frozen',side_effect=AssertionError('Data access forbidden')):
            for season in ['2024-25','2025-26']:
                with self.assertRaisesRegex(ValueError,'sealed'):load_modeling_data('/nonexistent',[season])
    def test_loader_projection_filters(self):
        original=pd.read_parquet
        with patch('nba_game_prediction.modeling_data.pd.read_parquet',wraps=original) as reader:d=load_modeling_data(ROOT,TRAIN)
        self.assertEqual(len(d),9519)
        for call in reader.call_args_list:
            cols=call.kwargs['columns'];self.assertFalse(set(cols)&{'home_pts','away_pts'})
            if 'home_win' in cols:self.assertEqual(call.kwargs['filters'],[('season','in',list(TRAIN))])
    def test_provenance_failure_stops(self):
        with patch('nba_game_prediction.modeling_data.digest',return_value='bad'),patch('nba_game_prediction.modeling_data.pd.read_parquet',side_effect=AssertionError('No data read')):
            with self.assertRaisesRegex(ValueError,'provenance'):load_modeling_data(ROOT,TRAIN)
    def test_metrics_guard_sealed(self):
        d=pd.DataFrame({'season':['2024-25'],'home_win':[True],'p':[.5]})
        with self.assertRaisesRegex(ValueError,'sealed'):evaluate(d,'p')
    def test_validation_artifact_coverage(self):
        p=pd.read_parquet(ROOT/'data/processed/stage3_predictions_2023_24.parquet')
        self.assertEqual(p.shape,(1230,11));self.assertEqual(set(p.season),{'2023-24'});self.assertFalse(set(p)&{'home_pts','away_pts'})
        self.assertTrue(np.isfinite(p.filter(like='probability').to_numpy()).all());self.assertTrue(p.game_id.is_unique)
    def test_baselines_exact(self):
        p=pd.read_parquet(ROOT/'data/processed/stage3_predictions_2023_24.parquet');old=pd.read_parquet(ROOT/'data/processed/stage2_predictions_2023_24.parquet')
        np.testing.assert_array_equal(p.constant_probability,old.constant_probability);np.testing.assert_array_equal(p.raw_elo_probability,old.elo_probability)
        self.assertTrue(json.loads((ROOT/'docs/stage3_evidence/baseline_regression.json').read_text())['passed'])
    def test_metrics_exact_five_models_unsealed(self):
        t=pd.read_csv(ROOT/'docs/stage3_evidence/validation_metrics.csv');self.assertEqual(len(t),5);self.assertEqual(set(t.split),{'2023-24 validation'})
        self.assertTrue(t.n_games.eq(1230).all())
if __name__=='__main__':unittest.main()
