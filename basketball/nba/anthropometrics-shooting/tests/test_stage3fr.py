import unittest,sys,inspect,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3fr_common import *
from stage3fr_model import build
from stage3fr_equivalence import transform,inverse
from stage3f_model import build as original_build
from stage3d_model import design
from stage3fr_selection import Eligible,select,classify
import numpy as np
class Stage3FR(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d,cls.ids,cls.idx,*_=design();cls.p=protocol();cls.old=original_build('F2');cls.new=build('R1')
 def test_A_history(self):
  for n,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/n),h,n)
  for n,h in self.p['frozen_code'].items():self.assertEqual(sha(ROOT/n),h,n)
  for f in E.glob('*_sampling.json'):self.assertLess(self.p['frozen_at'],read(f)['started_at'])
 def test_B_panel(self):self.assertEqual(sha(PANEL),EXPECTED)
 def test_C_data(self):
  for name in ['any_FTA','positive_FTA','FTM_count']:np.testing.assert_array_equal(self.old[name].tag.observations.eval(),self.new[name].tag.observations.eval())
  self.assertEqual(sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv'),self.p['decomposition_csv_sha256'])
  self.assertEqual(read(E/'design_identification_audit.json')['scales'],self.p['scales'])
 def test_D_likelihood(self):
  for f in E.glob('r?_equivalence_validation.json'):self.assertLess(read(f)['maximum_absolute_errors']['likelihood'],1e-7);self.assertTrue(read(f)['passed'])
 def test_E_priors(self):
  self.assertEqual(sha(ROOT/'docs/stage3f_evidence/prior_protocol.json'),self.p['prior_protocol_sha256'])
  for f in E.glob('r?_equivalence_validation.json'):self.assertTrue(read(f)['original_prior_preserved']);self.assertTrue(read(f)['paired_prior_predictive_counts_exact'])
 def test_F_R1_inverse(self):
  p=self.old.initial_point();q,_=transform(p,'R1');back=inverse(q,'R1')
  for k in p:np.testing.assert_allclose(p[k],back[k],atol=1e-12)
 def test_G_predictors(self):self.assertLess(read(E/'r1_equivalence_validation.json')['maximum_absolute_errors']['linear_predictor'],1e-7)
 def test_H_R2_density(self):
  if (E/'r2_equivalence_validation.json').exists():self.assertLess(read(E/'r2_equivalence_validation.json')['maximum_absolute_errors']['log_density'],1e-7)
  else:self.assertTrue(read(E/'r1_diagnostics.json')['sampler_pass'])
 def test_I_R3_derivation(self):
  self.assertEqual(sha(E/'r3_equivalence_derivation.md'),self.p['r3_derivation_sha256'])
  if (E/'r3_attempt1_sampling.json').exists():
   self.assertFalse(read(E/'r1_diagnostics.json')['sampler_pass']);self.assertFalse(read(E/'r2_diagnostics.json')['sampler_pass']);self.assertTrue(read(E/'r3_equivalence_validation.json')['passed']);self.assertLess(self.p['frozen_at'],read(E/'r3_attempt1_sampling.json')['started_at'])
 def test_J_diagnostic_ineligible(self):
  for n in ['DIAG-A','DIAG-B','DIAG-C']:
   with self.assertRaises(ValueError):Eligible(n,True,True)
  opportunity=build('DIAG-C');self.assertEqual({v.name for v in opportunity.observed_RVs},{'any_FTA','positive_FTA'});self.assertNotIn('beta_RW',opportunity.named_vars);self.assertNotIn('theta_B',opportunity.named_vars)
 def test_K_covariance_preserved(self):
  self.assertIn('chol_cov',{r.name for r in self.new.free_RVs});self.assertIn('corr_uv',self.new.named_vars);self.assertIn('corr_uh',self.new.named_vars);self.assertIn('corr_vh',self.new.named_vars)
 def test_L_firewall(self):
  import stage3fr_sampling
  text=inspect.getsource(stage3fr_sampling);self.assertNotIn('plot_trace',text);self.assertNotIn('plot_rank',text);self.assertIn("kind='diagnostics'",text);self.assertIn('sealed_parameter_sampler_pass',text)
  for f in E.glob('*_diagnostics.json'):
   d=read(f)
   if d.get('sampler_pass'):self.assertTrue(d['sealed_parameter_sampler_pass'])
 def test_M_no_summary(self):
  for f in list(E.glob('*.json'))+list(E.glob('*.csv'))+[ROOT/'docs/stage3fr_f2_identification_reparameterization.md']:
   if f.name=='prior_preservation_manifest.json':
    # Historical filenames may name sealed parameters; their values are only hashes.
    for path,digest in read(f).items():
     self.assertRegex(digest,r'^[0-9a-f]{64}$');self.assertEqual(sha(ROOT/path),digest)
    continue
   contents=f.read_text()
   self.assertTrue('beta_RW' not in contents,str(f));self.assertTrue('OR_RW' not in contents,str(f))
 def test_N_selection(self):
  import stage3fr_selection
  s=inspect.getsource(stage3fr_selection);self.assertNotIn('open(',s);self.assertNotIn('beta_RW',s);self.assertNotIn('arviz',s);self.assertEqual(select([Eligible('R1',True,False),Eligible('R2',True,True)]),'R2')
 def test_O_threshold(self):self.assertEqual(len(self.d),4117);self.assertEqual(int(self.d.fta.sum()),469099)
 def test_P_players(self):self.assertEqual(len(self.ids),857)
 def test_Q_categories(self):
  for k in ['position','season']:self.assertEqual(tuple(self.old.coords[k]),tuple(self.new.coords[k]))
 def test_R_confounders(self):
  orig={v.name for v in self.old.free_RVs};new={v.name for v in self.new.free_RVs};self.assertEqual(new,(orig-{'theta_B','theta_W'})|{'theta_B_std','theta_W_std'})
 def test_S_excluded_season(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_T_no_MIN(self):
  attrs={n.attr for n in ast.walk(ast.parse(inspect.getsource(build))) if isinstance(n,ast.Attribute)};self.assertFalse(attrs&{'MIN','minutes','seconds'})
 def test_U_PPC_gates(self):
  old=read(ROOT/'docs/stage3f_evidence/model_protocol.json');self.assertEqual(self.p['PPC'],old['PPC']);self.assertEqual(self.p['positive_count_gate'],old['positive_count_gate'])
 def test_V_authorization(self):
  for selected in [None,'R1','R2','R3']:
   for a in [False,True]:
    for o in [False,True]:
     r=classify(selected,a,o,True);self.assertEqual(r['stage3g_authorized'],selected is not None and a and o);self.assertFalse(r['scientific_inference_authorized']);self.assertFalse(r['stage3g_executed'])
 def test_W_no_causal_claim(self):
  s=(ROOT/'docs/stage3fr_f2_identification_reparameterization.md').read_text();self.assertIn('No causal claim',s);self.assertIn('associational',s)
if __name__=='__main__':unittest.main()
