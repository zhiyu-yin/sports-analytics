"""Access probes use spies/synthetic inputs; no sealed labels or model runs."""
import unittest,json,io,socket
from pathlib import Path
from unittest.mock import patch,Mock
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.dataset as ds
from nba_game_prediction import sealed_access as a
ROOT=Path(__file__).resolve().parents[1]
MIXED=ROOT/'data/interim/game_outcomes_multiseason.parquet'
class SealedAccessTests(unittest.TestCase):
    def test_sealed_loader_before_decoder(self):
        with patch('pandas.read_parquet',side_effect=AssertionError('physical read')):
            for c in ['home_win','home_pts','away_pts']:
                with self.assertRaises(a.SealedAccessError):a.load_outcomes(ROOT,['2024-25'],'test',[c])
    def test_holdout_before_decoder(self):
        with patch('pandas.read_parquet',side_effect=AssertionError('physical read')):
            with self.assertRaises(a.SealedAccessError):a.load_outcomes(ROOT,['2025-26'],'test')
            with self.assertRaises(a.SealedAccessError):a.load_identity(ROOT,['2025-26'])
    def test_identity_projection_only(self):
        read=pd.read_parquet
        with patch('pandas.read_parquet',wraps=read) as spy:
            d=a.load_identity(ROOT)
        self.assertEqual(list(d),['season','game_id','game_date','home_team_id','away_team_id']);self.assertEqual(len(d),1230)
        self.assertTrue(set(spy.call_args.kwargs['columns'])<=a.SAFE)
    def test_identity_rejects_labels_and_features(self):
        for c in ['home_win','home_pts','away_pts','wl','pts','home_win_pct_last_5','observed_values_json']:
            with self.assertRaises(a.SealedAccessError):a.load_identity(ROOT,columns=[c])
    def test_broad_pandas_read(self):
        with self.assertRaises(a.SealedAccessError):pd.read_parquet(MIXED)
    def test_broad_arrow_read(self):
        with self.assertRaises(a.SealedAccessError):pq.read_table(MIXED)
    def test_direct_arrow_objects(self):
        for factory in [pq.ParquetFile,ds.dataset]:
            with self.assertRaises(a.SealedAccessError):factory(MIXED)
    def test_outcome_columns_blocked_before_underlying(self):
        raw=Mock(side_effect=AssertionError('underlying decoder called'));reader=a.decoder(raw,'parquet')
        for col in ['home_win','home_pts','away_pts','wl','pts','other_unknown']:
            with self.assertRaises(a.SealedAccessError):reader(MIXED,columns=[col])
        raw.assert_not_called()
    def test_filtered_mixed_outcomes_still_not_decoded(self):
        with self.assertRaises(a.SealedAccessError):pd.read_parquet(MIXED,columns=['home_win'],filters=[('season','in',['2023-24'])])
    def test_filter_cannot_leak_outcomes(self):
        with self.assertRaises(a.SealedAccessError):pd.read_parquet(MIXED,columns=['game_id'],filters=[('home_win','==',True)])
    def test_holdout_filter_rejected(self):
        with self.assertRaises(a.SealedAccessError):pd.read_parquet(MIXED,columns=['game_id'],filters=[('season','==','2025-26')])
    def test_disjunction_cannot_bypass(self):
        filters=[[('season','==','2023-24')],[('season','==','2024-25')]]
        self.assertFalse(a.filters_open(filters))
        with self.assertRaises(a.SealedAccessError):pd.read_parquet(MIXED,columns=['home_win'],filters=filters)
    def test_open_outcome_loader_uses_separate_files(self):
        with patch('pandas.read_parquet',return_value=pd.DataFrame({'game_id':['synthetic'],'home_win':[True]})) as spy:
            d=a.load_outcomes(ROOT,['2022-23','2023-24'],'projection test')
        self.assertEqual(len(d),2)
        self.assertEqual([x.args[0].name for x in spy.call_args_list],['game_outcomes_2022_23.parquet','game_outcomes_2023_24.parquet'])
        for call in spy.call_args_list:self.assertEqual(call.kwargs['columns'],['game_id','home_win'])
    def test_raw_bytes_blocked(self):
        with self.assertRaises(a.SealedAccessError):(ROOT/'data/raw/2024-25/never-open.json').read_bytes()
    def test_builtin_open_blocked(self):
        with self.assertRaises(a.SealedAccessError):open(MIXED,'rb')
    def test_anonymous_buffer_blocked(self):
        with self.assertRaises(a.SealedAccessError):pd.read_parquet(io.BytesIO(b'not data'))
    def test_holdout_physical_and_checksum(self):
        p=ROOT/'data/raw/2025-26/nonexistent.json'
        with self.assertRaises(a.SealedAccessError):p.read_bytes()
        with self.assertRaises(a.SealedAccessError):a.checksum(p)
    def test_raw_retrieve_before_cache(self):
        from nba_game_prediction.ingest import retrieve,read_cache
        with patch('nba_game_prediction.ingest.read_cache',side_effect=AssertionError('cache touched')):
            for s in ['2024-25','2025-26']:
                with self.assertRaises(a.SealedAccessError):retrieve(ROOT/'data/raw'/s,season=s)
        with self.assertRaises(a.SealedAccessError):read_cache(ROOT/'data/raw/2024-25',season='2024-25')
    def test_historical_build_disabled(self):
        from nba_game_prediction.stage1d import build
        with self.assertRaises(a.SealedAccessError):build('/nonexistent')
    def test_multi_build_rejects_range_before_write(self):
        from nba_game_prediction.multiseason import build_multi
        with self.assertRaises(a.SealedAccessError):build_multi('/nonexistent',['2023-24','2024-25'])
    def test_network_blocked(self):
        with self.assertRaises(RuntimeError):socket.socket()
    def test_no_sklearn_fit(self):
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import HistGradientBoostingClassifier
        for cls in [LogisticRegression,HistGradientBoostingClassifier]:
            with self.assertRaises(RuntimeError):cls().fit(None,None)
    def test_model_builds_rejected_at_entry(self):
        from nba_game_prediction.stage3 import build as b3
        from nba_game_prediction.stage4 import build as b4
        for build in [b3,b4]:
            with self.assertRaises(RuntimeError):build('/nonexistent')
    def test_no_model_evaluation(self):
        from nba_game_prediction.metrics import evaluate,calibration
        for fn in [evaluate,calibration]:
            with self.assertRaises(RuntimeError):fn(None,None)
    def test_all_frozen_artifacts_unchanged(self):
        hashes=json.loads((ROOT/'docs/stage4a_evidence/protected_artifact_hashes_before.json').read_text())
        for p,h in hashes.items():self.assertEqual(a.checksum(ROOT/p),h,p)
    def test_archived_tests_byte_identical(self):
        old=json.loads((ROOT/'docs/stage4a_evidence/implementation_code_before.json').read_text())
        for p in (ROOT/'tests_archived').rglob('test_*.py'):
            expected=json.loads((ROOT/'docs/stage5a_evidence/code_checkpoint_before.json').read_text()) if p.name=='test_stage5.py' else old
            self.assertEqual(a.checksum(p),expected['tests/'+p.name])
    def test_stage4a_runner_has_no_model_calls(self):
        import ast
        path=ROOT/'src/nba_game_prediction/stage4a.py';tree=ast.parse(path.read_text())
        forbidden={'fit','predict','predict_proba','evaluate','calibration','select_hgb','select_logistic','replay'}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
                self.assertNotIn(name,forbidden)
    def test_candidate_freeze(self):
        c=json.loads((ROOT/'docs/stage4a_evidence/candidate_freeze.json').read_text());self.assertEqual(len(c['candidates']),7);self.assertEqual(c['leading_candidate'],'features_plus_elo_logistic')
        for p,h in c['artifact_sha256'].items():self.assertEqual(a.checksum(ROOT/p),h)
    def test_no_generic_override(self):
        with self.assertRaises(TypeError):a.load_outcomes(ROOT,['2024-25'],'test',force=True)
    def test_decoder_admits_only_requested_columns(self):
        raw=Mock(return_value='metadata');reader=a.decoder(raw,'parquet')
        self.assertEqual(reader(MIXED,columns=['season','game_id']),'metadata');self.assertEqual(raw.call_args.kwargs['columns'],['season','game_id'])
