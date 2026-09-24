"""Multi-season invariants, using synthetic histories and immutable cached regression."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_features import fixture,mutate
from nba_game_prediction.features import build_features,FEATURES
from nba_game_prediction.seasons import get_scope,date_in_scope
from nba_game_prediction.ingest import retrieve
from nba_game_prediction.normalize import normalize
from nba_game_prediction.validate import validate_and_pair
from nba_game_prediction.multiseason import regression_2023,verify_protected,combine_validated
ROOT=Path(__file__).resolve().parents[1]
def history(season):
    data=fixture()
    for f in data:
        f['game_id']=f.game_id.str.replace('00223','002'+season[2:4],regex=False)
        if 'season' in f:f['season']=season
        if 'game_date' in f:f['game_date']=f.game_date+pd.DateOffset(years=int(season[:4])-2023)
    return data
def joined(a,b):return tuple(pd.concat([x,y],ignore_index=True) for x,y in zip(a,b))
class MultiSeasonTests(unittest.TestCase):
    def setUp(self):self.a=history('2022-23');self.b=history('2023-24')
    def test_A_season_reset(self):
        tf,_=build_features(*joined(self.a,self.b));first=tf[tf.games_played_before.eq(0)]
        self.assertEqual(len(first),4)
        cols=['season_win_pct_before','rest_days']+[f for f in FEATURES if '_last_5' in f or '_last_10' in f]
        self.assertTrue(first[cols].isna().all().all())
        self.assertTrue(first.games_last_7_days.eq(0).all())
    def test_B_prior_season_mutation(self):
        a=build_features(*joined(self.a,self.b));b=build_features(*joined(mutate(self.a,self.a[1].iloc[-1].game_id),self.b))
        for x,y in zip(a,b):assert_frame_equal(x[x.season.eq('2023-24')],y[y.season.eq('2023-24')],check_exact=True)
    def test_C_future_season_mutation(self):
        a=build_features(*joined(self.a,self.b));b=build_features(*joined(self.a,mutate(self.b,self.b[1].iloc[0].game_id)))
        for x,y in zip(a,b):assert_frame_equal(x[x.season.eq('2022-23')],y[y.season.eq('2022-23')],check_exact=True)
    def test_D_shuffle(self):
        data=joined(self.a,self.b)
        for x,y in zip(build_features(*data),build_features(*(f.sample(frac=1,random_state=7) for f in data))):assert_frame_equal(x,y,check_exact=True)
    def test_E_separate_and_combined_equal(self):
        a=build_features(*self.a);b=build_features(*self.b);both=build_features(*joined(self.a,self.b))
        for x,y,z in zip(a,b,both):assert_frame_equal(pd.concat([x,y],ignore_index=True),z,check_exact=True)
    def test_E_mislabeled_season_stops(self):
        data=joined(self.a,self.b);data[0].loc[0,'season']='2023-24'
        with self.assertRaises(ValueError):build_features(*data)
    def test_E_wrong_date_stops(self):
        self.a[0].loc[0,'game_date']=pd.Timestamp('2024-11-01')
        with self.assertRaises(ValueError):build_features(*self.a)
    def test_F_exact_2023_regression(self):
        body,_,_=retrieve(ROOT/'data/raw/2023-24',season='2023-24')
        t,g,_=validate_and_pair(normalize(body));y=g[['game_id','home_pts','away_pts','home_win']].copy();tf,gf=build_features(t,g,y)
        self.assertTrue(regression_2023(ROOT,dict(team_games=t,games=g,game_outcomes=y,team_pregame_features=tf,game_features=gf))['passed'])
        verify_protected(ROOT)
    def test_holdout_rejected_before_cache_or_network(self):
        with patch('nba_game_prediction.ingest.read_cache',side_effect=AssertionError('Cache must not be inspected')):
            with self.assertRaises(ValueError):retrieve(ROOT/'data/raw/2025-26',season='2025-26',allow_network=True)
    def test_special_season_scope(self):
        s=get_scope('2019-20');self.assertIsNone(s.games_per_team)
        self.assertTrue(date_in_scope(pd.Timestamp('2020-08-14'),s));self.assertFalse(date_in_scope(pd.Timestamp('2020-08-15'),s));self.assertFalse(date_in_scope(pd.Timestamp('2020-04-01'),s))
        self.assertEqual(get_scope('2020-21').games_per_team,72)
    def test_real_quarantine_has_no_features(self):
        import json
        m=json.loads((ROOT/'docs/stage1c_evidence/multiseason_build_manifest.json').read_text())
        self.assertNotIn('2024-25',m['validated_seasons'])
        f=pd.read_parquet(ROOT/'data/interim/stage1c_game_features_multiseason.parquet',columns=['season'])
        self.assertFalse(f.season.eq('2024-25').any())
        import pyarrow.parquet as pq
        schema=pq.read_schema(ROOT/'data/interim/stage1c_game_features_multiseason.parquet')
        self.assertFalse(set(schema.names)&{'home_pts','away_pts','home_win','wl','pts'})
if __name__=='__main__':unittest.main()
