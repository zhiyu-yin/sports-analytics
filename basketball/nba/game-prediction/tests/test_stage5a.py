"""Static protocol/hash/schema and rejected-access tests only."""
import ast,json,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from nba_game_prediction import stage5a as p
from nba_game_prediction import sealed_access as a
class FinalProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.freeze=json.loads((p.E/'final_holdout_freeze.json').read_text())
    def test_candidate_recipe_exact(self):
        prior=json.loads((p.ROOT/'docs/stage4a_evidence/candidate_freeze.json').read_text());self.assertEqual(self.freeze['model_c_recipe'],prior['recipes']['features_plus_elo_logistic'])
    def test_elo_recipe_exact(self):self.assertEqual(self.freeze['raw_elo_recipe']['parameters'],dict(K=20.,H=50.,alpha=.5))
    def test_training_window(self):self.assertEqual(self.freeze['training_policy']['statistical_model_seasons'],p.TRAIN);self.assertFalse(self.freeze['training_policy']['refit_preholdout'])
    def test_primary_comparison(self):self.assertEqual(self.freeze['primary_comparison'],['features_plus_elo_logistic','raw_elo'])
    def test_primary_metrics(self):self.assertEqual(self.freeze['primary_metrics'],['log_loss','brier_score'])
    def test_metric_source_unchanged(self):
        spec=self.freeze['metrics_implementation'];self.assertEqual(a.checksum(p.ROOT/spec['path']),spec['sha256'])
    def test_calibration_fixed(self):self.assertEqual(self.freeze['calibration_implementation']['bins'],[i/10 for i in range(11)]);self.assertFalse(self.freeze['calibration_implementation']['fit_calibrator'])
    def test_bootstrap_protocol(self):
        u=self.freeze['uncertainty_protocol'];self.assertEqual(u['replicates'],10000);self.assertEqual(u['seed'],0);self.assertIn('calendar date',u['cluster']);self.assertTrue(u['paired']);self.assertIn('ddof=1',u['standard_error'])
    def test_seven_candidates(self):self.assertEqual(self.freeze['candidates'],p.CANDIDATES);self.assertEqual(len(p.CANDIDATES),7)
    def test_artifacts_unchanged(self):self.assertTrue(p.protected())
    def test_document_status(self):self.assertIn('FROZEN — NOT YET EXECUTED',p.protocol_bytes().decode())
    def test_no_enabled_executor(self):self.assertFalse(self.freeze['stage6_executor_enabled']);self.assertFalse(self.freeze['authorized_to_open']);self.assertFalse((p.ROOT/'scripts/run_stage6.py').exists())
    def test_ledger_schema_not_populated(self):
        schema=json.loads((p.E/'final_opening_ledger.schema.json').read_text())
        for n in ['first_physical_data_access_at_utc','first_outcome_decode_at_utc','aggregate_results_persisted_at_utc']:self.assertIsNone(schema['properties'][n]['default'])
        self.assertNotIn('first_physical_data_access_at_utc',schema)
    def test_holdout_rejected_before_reader(self):
        raw=Mock(side_effect=AssertionError('physical access'))
        with self.assertRaises(a.SealedAccessError):a.decoder(raw,'parquet')(p.ROOT/'data/raw/2025-26/forbidden.parquet',columns=['game_id'])
        raw.assert_not_called()
    def test_no_data_or_model_calls_in_protocol_module(self):
        tree=ast.parse(Path(p.__file__).read_text());forbidden={'read_parquet','load_outcomes','load_identity','fit','predict','predict_proba','evaluate','replay','calibration','frozen_runtime'}
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):self.assertNotIn(n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else '',forbidden)
    def test_metadata_reader_has_no_path_argument(self):
        with self.assertRaises(TypeError):p.protocol_bytes(p.ROOT/'data/raw/2025-26')
    def test_scope_not_inspected(self):self.assertIsNone(self.freeze['expected_scope']['observed_game_count']);self.assertIsNone(self.freeze['expected_scope']['observed_date_range'])
    def test_frozen_spec_reproduces(self):self.assertEqual(self.freeze,p.freeze_spec())
