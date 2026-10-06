"""Frozen panel, hurdle likelihood, opportunity decomposition, and effect firewall."""
import unittest,sys,inspect,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import numpy as np,pandas as pd
from stage3f_common import *
from stage3f_model import build,ztnb_logp
from stage3d_model import design
from stage3f_selection import Gate,classify
class Stage3F(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=protocol();cls.d,cls.ids,cls.idx,*_=design();cls.models={k:build(k) for k in ['F1','F2']}
 def test_A_history_preserved(self):
  for name,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/name),h,name)
  self.assertEqual(read(ROOT/'docs/stage3c_evidence/execution_status.json')['stage3c_execution'],'FAIL');self.assertEqual(read(ROOT/'docs/stage3d_evidence/model_adequacy_decision.json')['posterior_fits'],0);self.assertFalse(read(ROOT/'docs/stage3dr_evidence/model_adequacy_decision.json')['stage3e_authorized'])
 def test_B_panel_hash(self):self.assertEqual(sha(PANEL),EXPECTED)
 def test_C_excluded_season(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_D_frozen_before_fit(self):
  self.assertEqual(set(self.p['candidates']),{'F0','F1','F2'})
  for name,h in self.p['frozen_code'].items():self.assertEqual(sha(ROOT/name),h)
  for f in E.glob('*_sampling.json'):
   self.assertLess(self.p['frozen_at'],read(f)['started_at']);self.assertLess(read(E/'prior_gate_decision.json')['frozen_at'],read(f)['started_at'])
  self.assertEqual(sha(E/'prior_protocol.json'),self.p['prior_protocol_sha256'])
 def test_E_separate_hurdle(self):
  for m in self.models.values():self.assertEqual(type(m['any_FTA'].owner.op).__name__,'BernoulliRV');np.testing.assert_array_equal(m['any_FTA'].tag.observations.eval(),(self.d.fta.to_numpy()>0).astype(int))
 def test_F_true_truncation(self):
  from scipy.stats import nbinom
  y=np.array([1,2,5]);m=np.array([.1,2,10]);a=np.array([.5,2,3]);actual=ztnb_logp(y,m,a).eval();ref=nbinom.logpmf(y,a,a/(a+m))-nbinom.logsf(0,a,a/(a+m));np.testing.assert_allclose(actual,ref,atol=1e-9)
  self.assertEqual(ztnb_logp(np.array(0),2.,2.).eval(),-np.inf);v=read(E/'likelihood_validation.json');self.assertGreaterEqual(v['grid_points'],100);self.assertLess(v['maximum_error_scipy'],1e-8)
 def test_G_GP_offset_one(self):self.assertIn('np.log(d.games_played.to_numpy())+log_rate',inspect.getsource(build));self.assertTrue((self.d.games_played>0).all())
 def test_H_no_minutes(self):
  source=inspect.getsource(build);attrs={n.attr for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Attribute)};self.assertFalse(attrs&{'MIN','minutes','seconds'})
 def test_I_all_hurdle_rows(self):
  for m in self.models.values():self.assertEqual(m['any_FTA'].tag.observations.eval().shape,(4117,))
 def test_J_positive_count_rows(self):
  for m in self.models.values():np.testing.assert_array_equal(m['positive_FTA'].tag.observations.eval(),self.d.loc[self.d.fta>0,'fta'].to_numpy())
 def test_K_positive_accuracy_rows(self):
  for m in self.models.values():np.testing.assert_array_equal(m['FTM_count'].tag.observations.eval(),self.d.loc[self.d.fta>0,'ftm'].to_numpy())
 def test_L_decomposition_exact(self):
  b,w,c,u=decomposition(self.d.fta.to_numpy(),self.d.games_played.to_numpy(),self.idx);np.testing.assert_allclose(np.bincount(self.idx,weights=w)/np.bincount(self.idx),0,atol=1e-14);self.assertAlmostEqual(float((u-c).mean()),0);self.assertEqual(c,read(E/'opportunity_decomposition.json')['centering_constant'])
 def test_M_zero_retained(self):
  f=pd.read_csv(E/'opportunity_decomposition.csv');self.assertEqual(int((f.FTA==0).sum()),137);self.assertEqual(len(f),4117);np.testing.assert_allclose(f.loc[f.FTA==0,'centered_between']+f.loc[f.FTA==0,'within']+read(E/'opportunity_decomposition.json')['centering_constant'],0,atol=1e-14)
 def test_N_no_threshold(self):self.assertEqual(len(self.d),4117);self.assertEqual(int(self.d.fta.sum()),469099);self.assertEqual(int((self.d.fta>0).sum()),3980)
 def test_O_no_player_exclusion(self):self.assertEqual(len(self.ids),857)
 def test_P_no_new_confounders(self):
  base={'beta_0','beta_RW','beta_H','beta_position','beta_season','a_0','a_RW','a_H','a_position','a_season','c_0','c_RW','c_H','c_position','c_season','chol_cov','z_player','log_alpha_FTA','log_kappa'}
  for k,m in self.models.items():self.assertEqual({v.name for v in m.free_RVs},base|({'theta_B','theta_W'} if k=='F2' else set()))
 def test_Q_firewall(self):
  source=(ROOT/'scripts/stage3f_ppc.py').read_text();self.assertNotIn('beta_RW',source);self.assertNotIn('plot_rank', (ROOT/'scripts/stage3f_sampling.py').read_text())
 def test_R_no_public_scientific_summary(self):
  paths=list(E.glob('*.json'))+list(E.glob('*.csv'));report=ROOT/'docs/stage3f_hurdle_within_between_adequacy.md'
  if report.exists():paths.append(report)
  for path in paths:
   if path.name=='prior_preservation_manifest.json':self.assertTrue(all(len(h)==64 for h in read(path).values()));continue
   text=path.read_text();self.assertNotIn('beta_RW',text,str(path));self.assertNotIn('OR_RW',text,str(path));self.assertNotIn('Q25/Q75',text,str(path))
 def test_S_pure_selection(self):
  with self.assertRaises(TypeError):Gate(True,True,True,scientific_effect=1)
  import stage3f_selection
  source=inspect.getsource(stage3f_selection);self.assertNotIn('open(',source);self.assertNotIn('arviz',source);self.assertNotIn('beta_RW',source)
 def test_T_frozen_PPC_gates(self):
  self.assertEqual(self.p['PPC'],original()['PPC']);self.assertEqual(self.p['positive_count_gate'],dict(quantiles=[.25,.5,.75],fail_at_least=2,interval=.99))
 def test_U_no_automatic_science(self):
  good=Gate(True,True,True);r=classify(good,good,True);self.assertEqual(r['classification'],'STRUCTURAL ADEQUACY RESOLVED');self.assertFalse(r['scientific_inference_authorized']);self.assertFalse(r['stage3e_authorized']);self.assertFalse(r['stage3g_executed']);self.assertEqual(r['candidate_scientific_model_status'],'REQUIRES_ESTIMAND_REVIEW')
  self.assertEqual(classify(good,Gate(False,False,False),True)['classification'],'STRUCTURAL ADEQUACY UNRESOLVED')
  self.assertEqual(classify(Gate(True,False,True),Gate(True,False,False),True)['classification'],'STRUCTURAL ADEQUACY PARTIALLY RESOLVED')
  self.assertEqual(classify(Gate(True,False,False),Gate(True,True,False),True)['classification'],'STRUCTURAL ADEQUACY PARTIALLY RESOLVED')
  self.assertEqual(classify(good,good,False)['classification'],'STRUCTURAL ADEQUACY UNRESOLVED')
 def test_V_no_causal_claim(self):
  report=ROOT/'docs/stage3f_hurdle_within_between_adequacy.md'
  if not report.exists():self.skipTest('Final report not yet written')
  self.assertIn('No causal claim',report.read_text());self.assertIn('associational',report.read_text())
  self.assertEqual(self.p['candidate_scientific_model_status'],'REQUIRES_ESTIMAND_REVIEW')
if __name__=='__main__':unittest.main()
