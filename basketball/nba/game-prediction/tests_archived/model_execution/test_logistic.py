from pathlib import Path
import sys,unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.features import GAME_FEATURES
from nba_game_prediction.policy import TRAIN,VALIDATION
from nba_game_prediction.modeling_data import matrix,MODELS,add_frozen_elo
from nba_game_prediction.logistic import fit_model,predict,fit_final,fitted_state,coefficients,new_pipeline
from nba_game_prediction.model_selection import select_logistic,fold_prediction
A='basketball_features_logistic';B='elo_logistic';C='features_plus_elo_logistic'
def fixture(seasons=TRAIN+(VALIDATION,),count=14):
    rng=np.random.default_rng(734);rows=[]
    for season in seasons:
        for i,date in enumerate(pd.date_range(season[:4]+'-12-26',periods=count)):
            row=dict(season=season,game_id='002'+season[2:4]+f'{i+1:05d}',game_date=date,home_team_id=1 if i%2 else 2,away_team_id=2 if i%2 else 1,home_win=bool(i%3))
            for name in GAME_FEATURES:
                value=float(rng.normal())
                if ('last_5' in name and i<5) or ('last_10' in name and i<10) or (('season_win_pct' in name or 'rest_days' in name) and i==0):value=np.nan
                row[name]=value
            rows.append(row)
    return add_frozen_elo(pd.DataFrame(rows))
class LogisticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=fixture();cls.train=cls.data[cls.data.season.isin(TRAIN)].copy();cls.val=cls.data[cls.data.season.eq(VALIDATION)].copy()
        cls.fits=fit_final(cls.train,{m:.1 for m in MODELS})
    def test_A_training_only_imputer(self):
        changed=self.data.copy();changed.loc[changed.season.eq(VALIDATION),GAME_FEATURES]=999999
        other=fit_final(changed,{m:.1 for m in MODELS})
        for m in MODELS:np.testing.assert_array_equal(self.fits[m].pipeline['imputer'].statistics_,other[m].pipeline['imputer'].statistics_)
    def test_B_training_only_scaler(self):
        changed=self.data.copy();changed.loc[changed.season.eq(VALIDATION),GAME_FEATURES]=-999999
        other=fit_final(changed,{m:.1 for m in MODELS})
        for m in MODELS:
            np.testing.assert_array_equal(self.fits[m].pipeline['scaler'].mean_,other[m].pipeline['scaler'].mean_)
            np.testing.assert_array_equal(self.fits[m].pipeline['scaler'].scale_,other[m].pipeline['scaler'].scale_)
    def test_C_validation_target_selection_and_coefficients(self):
        changed=self.data.copy();changed['home_win']=changed.home_win.astype('boolean');changed.loc[changed.season.eq(VALIDATION),'home_win']=pd.NA
        x,g,_,_=select_logistic(self.data,grid=(.01,.1));y,h,_,_=select_logistic(changed,grid=(.01,.1))
        self.assertEqual(x,y);assert_frame_equal(g,h,check_exact=True)
        fits1=fit_final(self.data,x);fits2=fit_final(changed,y)
        for m in MODELS:self.assertEqual(fitted_state(fits1[m]),fitted_state(fits2[m]))
    def test_D_future_fold_target_isolation(self):
        changed=self.data.drop(columns=['elo_logit','raw_elo_probability']).copy()
        mask=changed.season.eq('2022-23');changed.loc[mask,'home_win']=~changed.loc[mask,'home_win'];changed=add_frozen_elo(changed)
        for model in MODELS:
            p,_=fold_prediction(self.data,model,.1,'2018-19');q,_=fold_prediction(changed,model,.1,'2018-19')
            assert_frame_equal(p,q,check_exact=True)
    def test_E_fresh_pipeline_per_fold(self):
        made=[]
        def factory(c):
            p=new_pipeline(c);made.append(p);return p
        with patch('nba_game_prediction.logistic.new_pipeline',side_effect=factory):select_logistic(self.train,grid=(.1,))
        self.assertEqual(len(made),15)
        for component in ['imputer','scaler','logistic']:self.assertEqual(len({id(p[component]) for p in made}),15)
    def test_early_season_rows_retained(self):
        for m in MODELS:self.assertEqual(len(predict(self.fits[m],self.val)),len(self.val))
    def test_training_medians_and_indicators(self):
        imp=self.fits[A].pipeline['imputer'];x=matrix(self.train,A)
        np.testing.assert_array_equal(imp.statistics_,x.median().to_numpy())
        np.testing.assert_array_equal(imp.indicator_.features_,np.where(x.isna().any().to_numpy())[0])
    def test_no_target_imputation(self):
        x=self.val.drop(columns='home_win');np.testing.assert_array_equal(predict(self.fits[A],x),predict(self.fits[A],self.val))
    def test_missing_outcome_refused(self):
        d=self.train.copy();d['home_win']=d.home_win.astype('boolean');d.loc[d.index[0],'home_win']=pd.NA
        with self.assertRaisesRegex(ValueError,'targets'):fit_model(d,A,.1)
    def test_opener_finite(self):
        opener=self.val.iloc[[0]]
        for m in MODELS:self.assertTrue(np.isfinite(predict(self.fits[m],opener)).all())
    def test_probabilities_strict_bounds(self):
        for m in MODELS:
            p=predict(self.fits[m],self.val);self.assertTrue(((p>0)&(p<1)).all())
    def test_shuffle_and_coefficients_deterministic(self):
        d=self.train.sample(frac=1,random_state=18);v=self.val.sample(frac=1,random_state=91)
        for m in MODELS:
            f=fit_model(d,m,.1);self.assertEqual(fitted_state(f),fitted_state(self.fits[m]))
            p=pd.Series(predict(f,v),index=v.game_id).sort_index();q=pd.Series(predict(self.fits[m],self.val),index=self.val.game_id).sort_index()
            np.testing.assert_array_equal(p,q)
    def test_column_order_allowlist(self):
        d=self.val[list(reversed(self.val.columns))]
        for m in MODELS:
            self.assertEqual(list(matrix(d,m)),list(MODELS[m]));np.testing.assert_array_equal(predict(self.fits[m],d),predict(self.fits[m],self.val))
    def test_identity_exclusion(self):
        d=self.val.copy();d['home_team_id']=999999;d['away_team_id']=888888;d['game_id']='not a predictor';d['home_team_name']='Any team'
        for m in MODELS:np.testing.assert_array_equal(matrix(d,m),matrix(self.val,m))
    def test_target_and_unknown_numeric_exclusion(self):
        d=self.val.copy();d['home_win']=~d.home_win;d['home_pts']=999;d['away_pts']=0;d['unknown_number']=333
        for m in MODELS:np.testing.assert_array_equal(predict(self.fits[m],d),predict(self.fits[m],self.val))
    def test_B_and_C_exact_inputs(self):
        self.assertEqual(list(matrix(self.val,B)),['elo_logit']);self.assertEqual(list(matrix(self.val,C)),GAME_FEATURES+['elo_logit']);self.assertEqual(len(GAME_FEATURES),32)
    def test_fit_rejects_validation(self):
        with self.assertRaisesRegex(ValueError,'training seasons only'):fit_model(self.val,A,.1)
    def test_fit_rejects_sealed(self):
        d=self.train.copy();d['season']='2024-25'
        with self.assertRaisesRegex(ValueError,'sealed'):fit_model(d,A,.1)
    def test_predict_rejects_sealed(self):
        d=self.val.copy();d['season']='2024-25'
        with self.assertRaisesRegex(ValueError,'sealed'):predict(self.fits[A],d)
    def test_all_missing_feature_refused(self):
        d=self.train.copy();d[GAME_FEATURES[0]]=np.nan
        with self.assertRaisesRegex(ValueError,'All-missing'):fit_model(d,A,.1)
    def test_unknown_C_refused(self):
        with self.assertRaises(ValueError):new_pipeline(100.)
    def test_no_refit_on_predict(self):
        before=fitted_state(self.fits[C]);predict(self.fits[C],self.val);self.assertEqual(before,fitted_state(self.fits[C]))
    def test_coefficients_names_indicators(self):
        t=coefficients(self.fits[C]);self.assertIn('elo_logit',set(t.source_feature_name));self.assertTrue(t.is_missingness_indicator.any())
        self.assertEqual(len(t),len(self.fits[C].pipeline['logistic'].coef_[0]));self.assertTrue(t.absolute_coefficient.eq(t.standardized_coefficient.abs()).all())
    def test_infinite_feature_refused(self):
        d=self.val.copy();d[GAME_FEATURES[0]]=np.inf
        with self.assertRaises(ValueError):predict(self.fits[A],d)
if __name__=='__main__':unittest.main()
