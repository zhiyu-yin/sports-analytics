"""Stage 1D: explicit reconciliation, immutable evidence, complete history."""
from pathlib import Path
import sys,json,unittest
import pandas as pd
from pandas.testing import assert_frame_equal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nba_game_prediction.ingest import retrieve
from nba_game_prediction.normalize import normalize
from nba_game_prediction.validate import validate_and_pair
from nba_game_prediction.reconciliation import load_approved,apply_reconciliation
from nba_game_prediction.stage1d import protected
from nba_game_prediction.features import build_features,FEATURES
ROOT=Path(__file__).resolve().parents[1]
class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.norm=normalize(retrieve(ROOT/'data/raw/2024-25',season='2024-25')[0],season='2024-25')
        cls.approved=load_approved(ROOT)
        cls.fixed,cls.applied=apply_reconciliation(cls.norm,cls.approved)
        cls.teams,cls.games,cls.anomalies=validate_and_pair(cls.fixed,season='2024-25')
        cls.tf,cls.gf=build_features(cls.teams,cls.games,cls.games[['game_id','home_pts','away_pts','home_win']].copy())
    def test_A_raw_immutability(self):
        protected(ROOT)
        baseline=self.norm.copy(deep=True);apply_reconciliation(self.norm,self.approved)
        assert_frame_equal(baseline,self.norm,check_exact=True);protected(ROOT)
    def test_B_explicit_only(self):
        fixed,applied=apply_reconciliation(self.norm,self.approved.iloc[:0])
        _,g,a=validate_and_pair(fixed,season='2024-25')
        self.assertEqual(len(g),1225);self.assertEqual(a.game_id.nunique(),5);self.assertEqual(applied,[])
    def test_C_authoritative_mapping(self):
        for row in self.approved.itertuples():
            g=self.games.set_index('game_id').loc[row.game_id]
            self.assertEqual(g.home_team_id,row.reconciled_home_team_id);self.assertEqual(g.away_team_id,row.reconciled_away_team_id)
    def test_D_reciprocal_validation(self):
        self.assertEqual(len(self.games),1230);self.assertTrue(self.anomalies.empty)
        self.assertTrue(self.teams.groupby('game_id').is_home.sum().eq(1).all())
        self.assertTrue(self.teams.groupby('team_id').size().eq(82).all())
    def test_E_outcome_preservation(self):
        cols=['game_id','team_id','pts','wl','matchup','_observed']
        assert_frame_equal(self.norm[cols],self.fixed[cols],check_exact=True)
    def test_F_full_history_restoration(self):
        for tid,t in self.teams.groupby('team_id'):
            t=t.sort_values('game_date');f=self.tf[self.tf.team_id.eq(tid)].sort_values('game_date')
            self.assertEqual(f.games_played_before.tolist(),list(range(82)))
            for i in range(5,len(t)):
                self.assertEqual(f.iloc[i].pts_for_avg_last_5,float(t.iloc[i-5:i].pts.mean()))
                self.assertEqual(f.iloc[i].win_pct_last_5,float(t.iloc[i-5:i].wl.eq('W').mean()))
    def test_G_future_reconciliation_invariance(self):
        cutoff=pd.Timestamp('2025-01-25')
        n=self.norm[self.norm.game_date.lt(cutoff)].copy()
        a=self.approved[pd.to_datetime(self.approved.game_date).lt(cutoff)]
        fixed,_=apply_reconciliation(n,a);t,g,_=validate_and_pair(fixed,season='2024-25')
        tf,gf=build_features(t,g,g[['game_id','home_pts','away_pts','home_win']].copy())
        for old,new in [(tf,self.tf),(gf,self.gf)]:assert_frame_equal(old,new[new.game_date.lt(cutoff)].reset_index(drop=True),check_exact=True)
    def test_H_no_earlier_season_regression(self):
        protected(ROOT)
        report=json.loads((ROOT/'docs/stage1d_evidence/regression_pre_2024_25.json').read_text())
        self.assertTrue(report['passed']);self.assertEqual(len(report['comparisons']),45)
        for old,new in [('stage1c_game_features_multiseason.parquet','data/processed/game_features_multiseason.parquet'),('stage1c_game_outcomes_multiseason.parquet','data/interim/game_outcomes_multiseason.parquet')]:
            f=pd.read_parquet(ROOT/new)
            assert_frame_equal(pd.read_parquet(ROOT/'data/interim'/old),f[f.season.ne('2024-25')].reset_index(drop=True),check_exact=True)
    def test_I_unresolved_source_fails(self):
        for confidence in ['unresolved','conflicted']:
            a=self.approved.copy();a.loc[a.index[0],'confidence']=confidence
            with self.assertRaisesRegex(ValueError,'Unresolved/conflicted'):apply_reconciliation(self.norm,a)
    def test_J_neutral_context_not_feature(self):
        context=pd.read_parquet(ROOT/'data/interim/game_context_2024_25.parquet')
        self.assertEqual(int(context.neutral_site.sum()),5)
        self.assertEqual(set(context.loc[context.neutral_site,'game_id']),set(self.applied))
        self.assertNotIn('neutral_site',self.gf);self.assertNotIn('neutral_site',FEATURES)
        self.assertTrue(self.approved.neutral_site.all());self.assertFalse(self.approved.ordinary_home_arena.any())
    def test_wrong_date_fails(self):
        a=self.approved.copy();a.loc[a.index[0],'game_date']='2024-11-03'
        with self.assertRaisesRegex(ValueError,'date mismatch'):apply_reconciliation(self.norm,a)
    def test_wrong_raw_label_fails(self):
        a=self.approved.copy();a.loc[a.index[0],'raw_team_1_matchup']='MIA vs. WAS'
        with self.assertRaisesRegex(ValueError,'Raw matchup'):apply_reconciliation(self.norm,a)
    def test_duplicate_evidence_fails(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):apply_reconciliation(self.norm,pd.concat([self.approved,self.approved]))
    def test_other_validation_errors_not_repaired(self):
        n=self.norm.copy();idx=n[n.game_id.eq(self.approved.iloc[0].game_id)].index[0];n.loc[idx,'pts']=999
        with self.assertRaisesRegex(ValueError,'only the reviewed'):apply_reconciliation(n,self.approved)
if __name__=='__main__':unittest.main()
