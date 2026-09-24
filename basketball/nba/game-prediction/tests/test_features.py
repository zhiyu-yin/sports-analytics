"""Synthetic fixtures and explicit temporal invariants; no live API dependencies."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.features import build_features,FEATURES,GAME_FEATURES,DIFFERENCES,feature_dictionary
from nba_game_prediction.schedule import schedule_features
from nba_game_prediction.feature_io import verified_bytes


def fixture(count=12, ids=(1,2), start=1, dates=None):
    """Artificial history: first team's differentials +1,-2,+3,-4,... ."""
    dates=list(pd.date_range('2023-11-01',periods=count)) if dates is None else list(pd.to_datetime(dates))
    game_rows,team_rows=[],[]
    for i,date in enumerate(dates):
        gid=f'00223{start+i:05d}'
        a_pts=100+2*i;diff=(i+1)*(1 if i%2==0 else -1);b_pts=a_pts-diff
        h,a=(ids if i%2==0 else tuple(reversed(ids)))
        points={ids[0]:a_pts,ids[1]:b_pts}
        game=dict(season='2023-24',season_type='Regular Season',game_id=gid,game_date=date,
                  home_team_id=h,home_team_name=f'Team {h}',home_team_abbreviation=f'T{h}',
                  away_team_id=a,away_team_name=f'Team {a}',away_team_abbreviation=f'T{a}',
                  home_pts=points[h],away_pts=points[a],home_win=points[h]>points[a])
        game_rows.append(game)
        for tid,other in [(h,a),(a,h)]:
            team_rows.append(dict(season=game['season'],season_type=game['season_type'],game_id=gid,game_date=date,
                                  team_id=tid,team_name=f'Team {tid}',team_abbreviation=f'T{tid}',
                                  is_home=tid==h,opponent_team_abbreviation=f'T{other}',
                                  pts=points[tid],wl='W' if points[tid]>points[other] else 'L',
                                  fgm=30,fga=70,fg3m=5,fg3a=20,ftm=10,fta=12,oreb=8,dreb=25,reb=33,
                                  ast=20,stl=3,blk=2,tov=12,pf=18,plus_minus=999))
    games=pd.DataFrame(game_rows);teams=pd.DataFrame(team_rows)
    return teams,games,games[['game_id','home_pts','away_pts','home_win']].copy()


def mutate(data,gid):
    t,g,y=[v.copy(deep=True) for v in data]
    idx=g.game_id.eq(gid);g.loc[idx,'home_pts']=77;g.loc[idx,'away_pts']=155;g.loc[idx,'home_win']=False
    for side,home,pts,wl in [('home',True,77,'L'),('away',False,155,'W')]:
        mask=t.game_id.eq(gid)&t.is_home.eq(home)
        t.loc[mask,'pts']=pts;t.loc[mask,'wl']=wl
        for col in ['fgm','fga','fg3m','fg3a','ftm','fta','oreb','dreb','reb','ast','stl','blk','tov','pf','plus_minus']:
            t.loc[mask,col]=12345
    y=g[['game_id','home_pts','away_pts','home_win']].copy()
    return t,g,y


def subset(data,cutoff):
    t,g,_=data;g=g[g.game_date<=cutoff].copy();t=t[t.game_id.isin(g.game_id)].copy()
    return t,g,g[['game_id','home_pts','away_pts','home_win']].copy()


class LeakageTests(unittest.TestCase):
    def test_A_target_mutation_invariance(self):
        data=fixture();gid=data[1].iloc[10].game_id
        t1,g1=build_features(*data);t2,g2=build_features(*mutate(data,gid))
        assert_frame_equal(t1[t1.game_id.eq(gid)],t2[t2.game_id.eq(gid)],check_exact=True)
        assert_frame_equal(g1[g1.game_id.eq(gid)],g2[g2.game_id.eq(gid)],check_exact=True)
        self.assertFalse(g1.iloc[11:][GAME_FEATURES].equals(g2.iloc[11:][GAME_FEATURES]))

    def test_B_future_append_invariance(self):
        data=fixture();cutoff=data[1].iloc[7].game_date
        t1,g1=build_features(*subset(data,cutoff));t2,g2=build_features(*data)
        assert_frame_equal(t1,t2[t2.game_date<=cutoff].reset_index(drop=True),check_exact=True)
        assert_frame_equal(g1,g2[g2.game_date<=cutoff].reset_index(drop=True),check_exact=True)

    def test_C_future_mutation_invariance(self):
        data=fixture();cutoff=data[1].iloc[7].game_date
        t1,g1=build_features(*data);t2,g2=build_features(*mutate(data,data[1].iloc[10].game_id))
        assert_frame_equal(t1[t1.game_date<=cutoff],t2[t2.game_date<=cutoff],check_exact=True)
        assert_frame_equal(g1[g1.game_date<=cutoff],g2[g2.game_date<=cutoff],check_exact=True)

    def test_D_first_game_missingness(self):
        tf,_=build_features(*fixture())
        first=tf[tf.games_played_before.eq(0)]
        self.assertEqual(len(first),2)
        self.assertTrue(first[['season_win_pct_before','rest_days']+[f for f in FEATURES if '_last_5' in f or '_last_10' in f]].isna().all().all())
        self.assertTrue(first.is_back_to_back.eq(0).all());self.assertTrue(first.games_last_7_days.eq(0).all())

    def test_E_exact_windows(self):
        tf,_=build_features(*fixture());a=tf[tf.team_id.eq(1)].reset_index(drop=True)
        self.assertTrue(a.loc[:4,'win_pct_last_5'].isna().all())
        self.assertTrue(a.loc[:9,'win_pct_last_10'].isna().all())
        self.assertEqual(a.loc[5,'win_pct_last_5'],3/5)
        self.assertEqual(a.loc[5,'point_diff_avg_last_5'],3/5)
        self.assertEqual(a.loc[10,'win_pct_last_5'],2/5)
        self.assertEqual(a.loc[10,'win_pct_last_10'],5/10)
        self.assertEqual(a.loc[10,'point_diff_avg_last_5'],-8/5)
        self.assertEqual(a.loc[10,'point_diff_avg_last_10'],-5/10)
        self.assertEqual(a.loc[10,'pts_for_avg_last_10'],109)
        self.assertEqual(a.loc[10,'pts_against_avg_last_10'],109.5)
        self.assertEqual(a.loc[10,'pts_for_avg_last_5'],114)
        self.assertEqual(a.loc[10,'pts_against_avg_last_5'],115.6)
        self.assertEqual(a.loc[5,'season_win_pct_before'],3/5)

    def test_F_team_isolation(self):
        original=fixture();other=fixture(ids=(3,4),start=100)
        joined=tuple(pd.concat([a,b],ignore_index=True) for a,b in zip(original,other))
        modified=joined
        for gid in other[1].game_id:modified=mutate(modified,gid)
        t1,g1=build_features(*original);t2,g2=build_features(*modified)
        assert_frame_equal(t1,t2[t2.team_id.isin([1,2])].reset_index(drop=True),check_exact=True)
        assert_frame_equal(g1,g2[g2.game_id.isin(g1.game_id)].reset_index(drop=True),check_exact=True)

    def test_G_shuffled_input(self):
        data=fixture();a=build_features(*data);b=build_features(*(d.sample(frac=1,random_state=42).reset_index(drop=True) for d in data))
        for x,y in zip(a,b):assert_frame_equal(x,y,check_exact=True)

    def test_H_same_date_ambiguity(self):
        data=fixture(dates=['2023-11-01','2023-11-01'])
        with self.assertRaisesRegex(ValueError,'Same-date ambiguity'):build_features(*data)

    def test_seven_day_left_inclusive_current_excluded(self):
        sf=schedule_features(pd.to_datetime(['2023-11-01','2023-11-02','2023-11-07','2023-11-08','2023-11-09']))
        self.assertEqual(sf.games_last_7_days.tolist(),[0,1,2,3,3])
        self.assertEqual(sf.rest_days.iloc[1:].tolist(),[0,4,0,0])
        self.assertEqual(sf.is_back_to_back.tolist(),[0,1,0,1,1])

    def test_rest_jan1_to_jan3(self):
        sf=schedule_features(pd.to_datetime(['2024-01-01','2024-01-03']))
        self.assertEqual(sf.rest_days.iloc[1],1);self.assertEqual(sf.is_back_to_back.iloc[1],0)

    def test_home_minus_away_differences(self):
        _,g=build_features(*fixture())
        for dest,source in DIFFERENCES.items():
            pd.testing.assert_series_equal(g[dest],g['home_'+source]-g['away_'+source],check_names=False,check_exact=True)

    def test_no_outcome_columns_and_dictionary_complete(self):
        t,g=build_features(*fixture());d=feature_dictionary()
        for frame in [t,g]:
            self.assertFalse(set(frame)&{'pts','wl','home_pts','away_pts','home_win','plus_minus','fgm','point_diff'})
            self.assertTrue(frame.columns.is_unique)
        self.assertEqual(set(d[d.table.eq('game_features')].feature_name),set(GAME_FEATURES))
        self.assertEqual(set(d[d.table.eq('team_pregame_features')].feature_name),set(FEATURES))

    def test_plus_minus_and_box_scores_ignored(self):
        data=fixture();changed=tuple(d.copy() for d in data)
        for col in ['plus_minus','fgm','tov','reb']:changed[0][col]=-999999
        for a,b in zip(build_features(*data),build_features(*changed)):assert_frame_equal(a,b,check_exact=True)

    def test_outcome_inconsistency_stops(self):
        t,g,y=fixture();y.loc[0,'home_pts']=999
        with self.assertRaisesRegex(ValueError,'Canonical/outcome mismatch'):build_features(t,g,y)

    def test_missing_opponent_stops(self):
        t,g,y=fixture()
        with self.assertRaisesRegex(ValueError,'two team rows'):build_features(t.iloc[1:],g,y)

    def test_mismatched_identity_stops(self):
        t,g,y=fixture();t.loc[0,'team_name']='Wrong'
        with self.assertRaisesRegex(ValueError,'identity mismatch'):build_features(t,g,y)

    def test_duplicate_game_column_stops(self):
        t,g,y=fixture();g=pd.concat([g,g[['game_id']]],axis=1)
        with self.assertRaisesRegex(ValueError,'Duplicate input column'):build_features(t,g,y)

    def test_provenance_corruption_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'snapshot';p.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'provenance mismatch'):verified_bytes(p,'0'*64)

    def test_no_network_needed(self):
        with patch('socket.socket',side_effect=AssertionError('Network forbidden')):
            self.assertEqual(len(build_features(*fixture())[1]),12)


if __name__=='__main__':unittest.main()
