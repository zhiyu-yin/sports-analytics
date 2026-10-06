"""Stage 3J-R numerical equivalence and immutable-input tests A-T."""
import sys,os,unittest,inspect
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from stage3jr_solver import *
FINAL=os.environ.get('STAGE3JR_FINAL')=='1'
class TestStage3JR(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=protocol();cls.bundle=inputs()
 def test_A_Stage3J_artifacts_unchanged(self):
  for f,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/f),h,f)
 def test_B_panel_hash(self):self.assertEqual(sha(PANEL),PH)
 def test_C_sample_hashes(self):
  schedule=pd.read_csv(J/'j2_complete_sample_schedule.csv');draws=self.bundle[3]
  for draw,digest in zip(draws,schedule.sample_sha256):self.assertEqual(hashlib.sha256(draw.astype('<i8').tobytes()).hexdigest(),digest)
 def test_D_same_2000_samples(self):self.assertEqual(self.bundle[3].shape,(2000,857));self.assertFalse(self.p['new_samples'])
 def test_E_same_likelihood(self):self.assertTrue(read(E/'likelihood_validation.json')['passed']);self.assertEqual(sha(ROOT/'scripts/stage2_models.py'),read(E/'input_receipt.json')['old_likelihood_sha256'])
 def test_F_same_formula(self):self.assertEqual(self.p['formula'],read(J/'analysis_protocol.json')['formula'])
 def test_G_same_counts(self):
  d=self.bundle[0];self.assertEqual(len(d),4117);self.assertEqual(int(d.fta.sum()),469099);self.assertEqual(int(d.ftm.sum()),360001);self.assertEqual(int((d.fta>0).sum()),3980)
 def test_H_same_residual(self):
  d=self.bundle[0];np.testing.assert_array_equal(d.residual_wingspan,d.wingspan_inches-(4.574910520685837+1.0013410045156863*d.height_wo_shoes_inches))
 def test_I_no_penalty(self):self.assertEqual(self.p['new_statistical_terms'],[]);self.assertIn('no penalty or regularization',self.p['likelihood'])
 def test_J_no_tolerance_relaxation(self):
  self.assertEqual(SCORE_GATE,.001);a=self.p['acceptance'];self.assertEqual(a['absolute_score_max_strictly_less_than'],.001);self.assertTrue(a['all_three_starts']);self.assertEqual(a['likelihood_spread_max'],1e-5);self.assertEqual(a['max_covariance_diagonal_relative_difference'],.001)
 def test_K_gradient(self):self.assertTrue(read(E/'gradient_validation.json')['passed']);self.assertLess(read(E/'gradient_validation.json')['analytic_score_vs_central_difference_max_error'],1e-4)
 def test_L_scaling(self):self.assertTrue(read(E/'scaling_equivalence.json')['passed']);self.assertLess(read(E/'scaling_equivalence.json')['max_forward_inverse_error'],1e-12)
 def test_M_warm_start(self):
  self.assertIn('corresponding deterministic original R0 endpoint',self.p['warm_start_rule']);self.assertEqual(self.p['starts'],[10.,50.,200.])
  a=sample(self.bundle,9);b=sample(self.bundle,9);np.testing.assert_array_equal(a['initial'],b['initial']);np.testing.assert_array_equal(a['z'],b['z'])
 def test_N_numeric_selection_only(self):
  source=inspect.getsource(polish);self.assertIn('np.argmin(values)',source);self.assertNotIn("beta[1]",source);self.assertNotIn('sign(',source)
 def test_O_no_replacement(self):
  self.assertIn('never replace or drop',self.p['failure_policy'])
  if FINAL:
   r=pd.read_csv(E/'full_bootstrap_results.csv');self.assertEqual(r.replicate.tolist(),list(range(1,2001)));self.assertEqual(r.sample_sha256.tolist(),pd.read_csv(J/'j2_complete_sample_schedule.csv').sample_sha256.tolist())
 def test_P_uniform_algorithm(self):
  self.assertIn("for method in ['Newton-CG','hybr','trust-exact','lm']",inspect.getsource(polish))
  if FINAL:self.assertTrue(read(E/'full_execution_receipt.json')['uniform_algorithm']);self.assertEqual(read(E/'final_algorithm_receipt.json')['protocol_sha256'],sha(E/'numerical_protocol.json'))
 def test_Q_old_success_reproduce(self):
  self.assertTrue(read(E/'failure_summary.json')['reference_status_and_recorded_diagnostics_reproduced'])
  if FINAL:self.assertTrue(read(E/'old_vs_new_successful_fit_comparison.json')['passed']);self.assertTrue(read(E/'reproduction_check.json')['passed'])
 def test_R_summary_after_valid_gate(self):
  if FINAL:
   d=read(E/'stage3jr_decision.json');s=read(E/'full_bootstrap_summary.json');self.assertEqual(sha(E/'stage3jr_decision.json'),read(E/'decision_freeze_receipt.json')['sha256'])
   if s['status']=='RELEASED_AFTER_NUMERICAL_DECISION':self.assertEqual(d['failed'],0);self.assertLess(d['decision_at'],s['generated_at']);self.assertEqual(s['replicates'],2000)
  else:self.assertFalse((E/'stage3jr_decision.json').exists());self.assertFalse((E/'full_bootstrap_summary.json').exists())
 def test_S_J1_unchanged(self):self.assertEqual(sha(J/'primary_result.json'),read(E/'input_receipt.json')['primary_result_sha256']);self.assertEqual(read(J/'execution_decision.json')['execution'],'FAIL')
 def test_T_no_causal_wording(self):
  if FINAL:
   report=(ROOT/'docs/stage3jr_beta_binomial_numerical_remediation.md').read_text().lower();self.assertNotIn('causes',report);self.assertIn('no causal claim',report)
  else:self.assertIn('Numerical remediation only',self.p['purpose'])
if __name__=='__main__':unittest.main(verbosity=2)
