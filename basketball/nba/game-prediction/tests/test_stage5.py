"""Stage 5 preflight: only synthetic targets, metadata, hashes and mocked reads."""
import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch,Mock
import numpy as np
import pandas as pd
from nba_game_prediction import sealed_access as a
from nba_game_prediction.stage5_access import Session,verify_recipes,verify_artifacts,frozen_runtime,NAMES,PRIMARY,IDENTITY,exclusive_json
from nba_game_prediction.stage5 import fit_frozen,prediction_frame,assert_coverage,results
ROOT=Path(__file__).resolve().parents[1]
def synthetic(n=1230,season='2024-25'):
    d=pd.DataFrame(dict(season=[season]*n,game_id=[f'002249{i:04d}' for i in range(n)],game_date=pd.date_range('2024-11-01',periods=n),home_team_id=[1]*n,away_team_id=[2]*n,home_win=np.arange(n)%2==0))
    for col in NAMES.values():d[col]=.55
    return d
class Stage5Tests(unittest.TestCase):
    def state(self,phase='reconstruct'):
        s=object.__new__(Session);s.root=ROOT;s.e=ROOT/'docs/stage5_evidence';s.phase=phase;s.fit_calls=[];s.training_model=None;s.decode_calls=0;s.mode='open';s.ledger_path=Path('/nonexistent/synthetic-ledger');return s
    def test_candidate_set_exact(self):self.assertEqual(verify_recipes(ROOT)[0]['candidates'],list(NAMES))
    def test_recipes_exact(self):
        f,s2,s3,s4=verify_recipes(ROOT);self.assertEqual(s2['parameters'],dict(K=20.,H=50.,alpha=.5));self.assertEqual(set(s3['C_by_model'].values()),{.01});self.assertEqual(s4['parameters_by_model']['features_plus_elo_hgb']['max_leaf_nodes'],7)
    def test_all_protected_artifacts_unchanged(self):self.assertTrue(verify_artifacts(ROOT))
    def test_preopening_rejects_sealed(self):
        with self.assertRaises(a.SealedAccessError):self.state().check_seasons(['2024-25'])
    def test_only_2024_authorized_after_opening(self):
        s=self.state('opened');s.check_seasons(['2024-25'])
        for season in ['2025-26','2026-27']:
            with self.assertRaises(a.SealedAccessError):s.check_seasons([season])
    def test_final_holdout_before_reader_even_with_session(self):
        s=self.state('opened');raw=Mock(side_effect=AssertionError('read'))
        with s.activate():
            with self.assertRaises(a.SealedAccessError):a.decoder(raw,'parquet')(ROOT/'data/raw/2025-26/test.parquet',columns=['game_id'])
        raw.assert_not_called()
    def test_only_two_exact_source_paths(self):
        s=self.state('opened')
        self.assertFalse(s.admit_read(ROOT/'data/interim/reconciled/games_2024_25.parquet',['home_pts'],None))
        with self.assertRaises(a.SealedAccessError):s.admit_read(ROOT/'data/interim/reconciled/game_outcomes_2024_25.parquet',['home_pts'],None)
    def test_postopening_fit_rejected(self):
        s=self.state('opened');s.training_model='features_plus_elo_logistic';est=type('LogisticRegression',(),{})();fit=Mock()
        with self.assertRaises(RuntimeError):s.model_call(fit,'fit',est,np.zeros((9519,1)),np.zeros(9519))
        fit.assert_not_called()
    def test_replay_fit_rejected(self):
        s=self.state('replay');fit=Mock();est=type('HistGradientBoostingClassifier',(),{})()
        with self.assertRaises(RuntimeError):s.model_call(fit,'fit',est,np.zeros((9519,1)),np.zeros(9519))
        fit.assert_not_called()
    def test_training_window_rejects_2024_rows(self):
        with self.assertRaises(ValueError):fit_frozen(None,None,synthetic(),{}, {})
    def test_unapproved_family_rejected(self):
        with self.assertRaises(RuntimeError):self.state().model_call(Mock(),'fit',type('RandomForestClassifier',(),{})(),None,None)
    def test_exact_coverage(self):
        assert_coverage(synthetic())
        for d in [synthetic(1229),synthetic().assign(season='2025-26'),synthetic().assign(home_pts=100)]:
            with self.assertRaises(ValueError):assert_coverage(d)
    def test_score_columns_excluded_from_matrices(self):
        s=self.state('opened');rt=frozen_runtime(ROOT,s)
        from nba_game_prediction.features import GAME_FEATURES
        d=synthetic(2).assign(elo_logit=0.,home_pts=100,away_pts=90)
        for c in GAME_FEATURES:d[c]=np.nan
        for m in list(NAMES)[2:]:
            x=rt.boosting.matrix(d,m) if m.endswith('_hgb') else rt.modeling_data.matrix(d,m)
            self.assertFalse(set(x)&{'home_pts','away_pts','home_win','game_id'});self.assertEqual(list(x),verify_recipes(ROOT)[0]['recipes'][m]['features'])
    def test_primary_comparison_fixed(self):self.assertEqual(PRIMARY,('features_plus_elo_logistic','raw_elo'))
    def test_ledger_created_before_first_decode(self):
        s=self.state('armed')
        with tempfile.TemporaryDirectory() as t:
            s.e=Path(t);s.ledger_path=s.e/'preholdout_opening_ledger.json'
            exclusive_json(s.e/'protected_before.json',{'data/interim/reconciled/game_outcomes_2024_25.parquet':'synthetic-hash'})
            exclusive_json(s.ledger_path,dict(status='authorized_not_decoded'))
            with patch('nba_game_prediction.stage5_access.access.checksum',return_value='synthetic-hash'):
                self.assertTrue(s.admit_read(ROOT/'data/interim/reconciled/game_outcomes_2024_25.parquet',['game_id','home_win'],None))
            ledger=json.loads(s.ledger_path.read_text());self.assertEqual(ledger['status'],'opened');self.assertTrue(ledger['first_outcome_decode_started_at_utc']);self.assertTrue((s.e/'first_outcome_decode.json').exists())
    def test_no_ledger_no_decode(self):
        s=self.state('armed')
        with self.assertRaises(FileNotFoundError):s.admit_read(ROOT/'data/interim/reconciled/game_outcomes_2024_25.parquet',['game_id','home_win'],None)
    def test_second_decode_rejected(self):
        s=self.state('opened');s.decode_calls=1
        with self.assertRaises(RuntimeError):s.admit_read(ROOT/'data/interim/reconciled/game_outcomes_2024_25.parquet',['game_id','home_win'],None)
    def test_runtime_numerical_sources_exact(self):
        before=json.loads((ROOT/'docs/stage4a_evidence/implementation_code_before.json').read_text())
        for p in (ROOT/'docs/stage5_evidence/frozen_source').glob('*.py'):self.assertEqual(a.checksum(p),before['src/nba_game_prediction/'+p.name])
