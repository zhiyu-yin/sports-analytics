from pathlib import Path
import sys,unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_logistic import fixture
from nba_game_prediction import boosting as b
from nba_game_prediction.policy import TRAIN,VALIDATION
from nba_game_prediction.features import GAME_FEATURES
from nba_game_prediction.modeling_data import add_frozen_elo,load_modeling_data,FROZEN
from nba_game_prediction.stage4 import baseline_regression,BASELINES
ROOT=Path(__file__).resolve().parents[1]
class BoostingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=fixture(count=20);cls.train=cls.data[cls.data.season.isin(TRAIN)].copy();cls.val=cls.data[cls.data.season.eq(VALIDATION)].copy();cls.p=b.GRID[0]
        cls.fits=b.fit_final(cls.data,{m:cls.p for m in b.MODELS})
    def test_fresh_estimators(self):
        made=[];original=b.new_estimator
        def factory(p):
            x=original(p);made.append(x);return x
        with patch.object(b,'new_estimator',side_effect=factory):b.select_hgb(self.data,grid=(self.p,))
        self.assertEqual(len(made),10);self.assertEqual(len({id(x) for x in made}),10)
    def test_future_fold_mutation(self):
        d=self.data.drop(columns=['elo_logit','raw_elo_probability']).copy();mask=d.season.eq('2022-23');d.loc[mask,'home_win']=~d.loc[mask,'home_win'];d=add_frozen_elo(d)
        for m in b.MODELS:
            x,_=b.fold_prediction(self.data,m,self.p,'2018-19');y,_=b.fold_prediction(d,m,self.p,'2018-19');assert_frame_equal(x,y,check_exact=True)
    def test_external_targets_cannot_select(self):
        d=self.data.copy();d['home_win']=d.home_win.astype('boolean');d.loc[d.season.eq(VALIDATION),'home_win']=pd.NA
        x,g,_=b.select_hgb(self.data,grid=b.GRID[:2]);y,h,_=b.select_hgb(d,grid=b.GRID[:2]);self.assertEqual(x,y);assert_frame_equal(g,h,check_exact=True)
    def test_final_training_only(self):
        d=self.data.copy();d.loc[d.season.eq(VALIDATION),GAME_FEATURES]=99999;d.loc[d.season.eq(VALIDATION),'home_win']=False
        other=b.fit_final(d,{m:self.p for m in b.MODELS})
        for m in b.MODELS:
            self.assertEqual(other[m].training_seasons,TRAIN);self.assertEqual(other[m].training_games,len(self.train));np.testing.assert_array_equal(b.predict(other[m],self.val),b.predict(self.fits[m],self.val))
    def test_validation_cannot_fit(self):
        with self.assertRaises(ValueError):b.fit_model(self.val,b.D,self.p)
    def test_sealed_fit_and_prediction(self):
        for season in ['2024-25','2025-26']:
            d=self.val.assign(season=season)
            for operation in [lambda:b.fit_model(d,b.D,self.p),lambda:b.predict(self.fits[b.D],d),lambda:b.select_hgb(d),lambda:b.fit_final(d,{m:self.p for m in b.MODELS})]:
                with self.assertRaises(ValueError):operation()
    def test_sealed_before_file_access(self):
        for season in ['2024-25','2025-26']:
            with patch('pandas.read_parquet',side_effect=AssertionError('data touched')):
                with self.assertRaises(ValueError):load_modeling_data(Path('/nonexistent'),[season])
    def test_exact_D_allowlist(self):self.assertEqual(list(b.matrix(self.data,b.D)),GAME_FEATURES)
    def test_exact_E_allowlist(self):self.assertEqual(list(b.matrix(self.data,b.E)),GAME_FEATURES+['elo_logit'])
    def test_unknown_and_identity_columns_excluded(self):
        d=self.data.assign(unknown_numeric=999,home_score=100,away_score=90)
        for m in b.MODELS:
            self.assertFalse(set(['home_win','home_team_id','away_team_id','game_date','season','game_id','unknown_numeric','home_score','away_score'])&set(b.matrix(d,m)));assert_frame_equal(b.matrix(d,m),b.matrix(self.data,m))
    def test_shuffle_predictions(self):
        d=self.train.sample(frac=1,random_state=2);d=d[d.columns[::-1]]
        v=self.val.sample(frac=1,random_state=3)
        for m in b.MODELS:
            fit=b.fit_model(d,m,self.p)
            a=pd.Series(b.predict(fit,v),index=v.game_id).sort_index();z=pd.Series(b.predict(self.fits[m],self.val),index=self.val.game_id).sort_index();np.testing.assert_array_equal(a,z)
    def test_native_nan_no_imputation(self):
        with patch('sklearn.impute.SimpleImputer.fit',side_effect=AssertionError('imputer called')),patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('scaler called')):
            for m in b.MODELS:
                x=b.matrix(self.train,m);self.assertTrue(x.isna().any().any());self.assertEqual(len(x),len(self.train))
                f=b.fit_model(self.train,m,self.p);self.assertEqual(f.estimator.n_features_in_,len(b.MODELS[m]));self.assertTrue(np.isfinite(b.predict(f,self.val)).all());self.assertEqual(len(b.predict(f,self.val)),len(self.val))
    def test_frozen_elo_reject_retune(self):
        raw=self.data.drop(columns=['elo_logit','raw_elo_probability'])
        for k in FROZEN:
            p=dict(FROZEN);p[k]+=1
            with self.assertRaises(ValueError):add_frozen_elo(raw,p)
    def test_elo_target_and_future_pregame(self):
        raw=self.data.drop(columns=['elo_logit','raw_elo_probability']).copy();i=50;raw.loc[i,'home_win']=not raw.loc[i,'home_win'];new=add_frozen_elo(raw)
        np.testing.assert_array_equal(self.data.elo_logit.iloc[:i+1],new.elo_logit.iloc[:i+1]);self.assertNotEqual(self.data.elo_logit.iloc[i+1],new.elo_logit.iloc[i+1])
    def test_missing_elo_rejected(self):
        with self.assertRaises(ValueError):b.matrix(self.data.assign(elo_logit=np.nan),b.E)
    def test_parameters_reject_invalid(self):
        for key,values in {'learning_rate':[0,-1,.2,np.nan,True],'max_leaf_nodes':[0,2,8,True],'l2_regularization':[-1,2,np.inf,True]}.items():
            for v in values:
                p=dict(self.p);p[key]=v
                with self.assertRaises(ValueError):b.new_estimator(p)
    def test_parameters_reject_early_stopping_unknown(self):
        for k,v in [('early_stopping',True),('max_iter',100),('random_state',1),('loss','other'),('unknown',1)]:
            with self.assertRaises(ValueError):b.new_estimator(dict(self.p,**{k:v}))
    def test_fixed_parameters_and_grid(self):
        self.assertEqual(len(b.GRID),27)
        for p in b.GRID:
            est=b.new_estimator(p)
            for k,v in b.FIXED.items():self.assertEqual(est.get_params()[k],v)
    def test_invalid_grid(self):
        for grid in [(),(self.p,self.p),({'learning_rate':.5,'max_leaf_nodes':7,'l2_regularization':0},)]:
            with self.assertRaises(ValueError):b.select_hgb(self.data,grid=grid)
    def test_exact_baselines(self):
        pred=pd.read_parquet(ROOT/'data/processed/stage3_predictions_2023_24.parquet');self.assertTrue(baseline_regression(ROOT,pred)['passed'])
    def test_all_baseline_array_mismatches_stop(self):
        pred=pd.read_parquet(ROOT/'data/processed/stage3_predictions_2023_24.parquet')
        for col in BASELINES.values():
            d=pred.copy();d.loc[0,col]+=1e-8
            with self.assertRaises(ValueError):baseline_regression(ROOT,d)
    def test_baseline_metric_mismatch_stops(self):
        pred=pd.read_parquet(ROOT/'data/processed/stage3_predictions_2023_24.parquet');original=pd.read_csv
        def changed(*a,**kw):
            d=original(*a,**kw);d.loc[d.model.eq('features_plus_elo_logistic'),'log_loss']+=1e-8;return d
        with patch('pandas.read_csv',side_effect=changed):
            with self.assertRaises(ValueError):baseline_regression(ROOT,pred)
    def test_sealed_evaluation(self):
        from nba_game_prediction.metrics import evaluate
        for s in ['2024-25','2025-26']:
            with self.assertRaises(ValueError):evaluate(self.val.assign(season=s,probability=.5),'probability')
if __name__=='__main__':unittest.main()
