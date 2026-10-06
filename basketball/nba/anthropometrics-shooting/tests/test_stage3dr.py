"""Prospective amendment, frozen gates and scientific-parameter firewall."""
import unittest,sys,inspect,ast
from unittest.mock import patch
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3dr_common import *
from stage3dr_model import build
from stage3dr_sampling import authorize
from stage3d_selection import CandidateGate,select_future_model
class Stage3DR(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a=amendment();cls.p=protocol();cls.d=fixed_data()
 def test_A_historical_failure(self):
  old=read(ROOT/'docs/stage3d_evidence/model_adequacy_decision.json');self.assertEqual(old['stop_phase'],'PRIOR_PREDICTIVE');self.assertEqual(old['posterior_fits'],0);self.assertFalse(old['stage3e_authorized'])
 def test_B_all_history_preserved(self):
  for name,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/name),h,name)
 def test_C_prospective_freeze(self):self.assertLess(self.a['frozen_at'],read(E/'amended_prior_predictive.json')['started_at']);self.assertEqual(sha(ROOT/'scripts/stage3dr_model.py'),self.a['model_code_sha256'])
 def test_D_no_previous_D3_posterior(self):self.assertTrue(self.a['no_D3_posterior_existed']);self.assertFalse(list((ROOT/'models/stage3d').glob('*posterior*')))
 def test_E_opportunity_priors(self):
  expected=dict(a_0=['Normal',float(np.log(2)),1],a_RW=['Normal',0,.15],a_H=['Normal',0,.15],a_position=['Normal',0,.35],a_season=['Normal',0,.25],sigma_opportunity=['HalfNormal',.5],log_alpha_FTA=['Normal',float(np.log(2)),1],alpha_FTA='exp(log_alpha_FTA)');self.assertEqual(self.a['new_opportunity_priors'],expected)
  model=build('D3')
  for key in ['a_0','a_RW','a_H','a_position','a_season','log_alpha_FTA']:
   prior=expected[key];self.assertAlmostEqual(float(model[key].owner.inputs[-2].eval()),prior[1]);self.assertAlmostEqual(float(model[key].owner.inputs[-1].eval()),prior[2])
 def test_F_accuracy_priors_unchanged(self):
  self.assertEqual(self.a['accuracy_priors'],self.p['candidates']['D3']['accuracy_priors']);self.assertEqual(self.a['sigma_accuracy'],['HalfNormal',1]);self.assertEqual(self.a['LKJ_eta'],2)
  model=build('D3')
  for key,mu,sd in [('beta_0',0,2.5),('beta_RW',0,.5),('beta_H',0,.5),('beta_position',0,1),('beta_season',0,1),('log_kappa',3,2)]:
   self.assertEqual(float(model[key].owner.inputs[-2].eval()),mu);self.assertEqual(float(model[key].owner.inputs[-1].eval()),sd)
 def test_G_likelihood_structure(self):
  model=build('D3');self.assertEqual([type(x.owner.op).__name__ for x in model.observed_RVs],['NegBinomialRV','BetaBinomialRV']);self.assertEqual(model['FTA_count'].tag.observations.eval().shape,(4117,));self.assertEqual(model['FTM_count'].tag.observations.eval().shape,(3980,));self.assertNotIn('gamma_FTA',model.named_vars);self.assertEqual(model.coords['effect'],('accuracy','opportunity'))
 def test_H_GP_offset(self):self.assertIn('np.log(d.games_played.to_numpy())+log_rate',inspect.getsource(build));self.assertEqual(read(E/'gp_offset_validation.json')['coefficient'],1)
 def test_I_no_minutes(self):
  attrs={n.attr for n in ast.walk(ast.parse(inspect.getsource(build))) if isinstance(n,ast.Attribute)};self.assertFalse(attrs&{'minutes','seconds','MIN'})
 def test_J_not_empirical_prior_calibration(self):
  self.assertTrue(self.a['no_observed_FTA_quantile_used']);source=(ROOT/'scripts/stage3dr_setup.py').read_text();self.assertNotIn('np.quantile(',source);self.assertNotIn('.quantile(',source)
 def test_K_prior_gates_unchanged(self):self.assertEqual(self.a['prior_gates'],self.p['prior_predictive']['opportunity_gate'])
 def test_L_prior_failure_blocks_fitting(self):
  with patch('stage3dr_sampling.read',return_value={'passed':False}):
   with self.assertRaises(AssertionError):authorize()
 def test_M_typed_selection_firewall(self):
  with self.assertRaises(TypeError):CandidateGate(True,True,True,True,True,True,beta_RW={'mean':1})
  with self.assertRaises(TypeError):select_future_model({k:{} for k in ['D0','D1','D2','D3']})
 def test_N_no_public_scientific_summary(self):
  for path in list(E.glob('*.json'))+list(E.glob('*.csv'))+[ROOT/'docs/stage3dr_opportunity_prior_and_adequacy.md']:
   if path.name=='prior_preservation_manifest.json':
    # Historical filenames may name a prior-stage figure; values must be hashes,
    # never coefficient summaries or copies of the historical scientific result.
    self.assertTrue(all(isinstance(v,str) and len(v)==64 for v in read(path).values()));continue
   text=path.read_text();self.assertNotIn('beta_RW',text,str(path));self.assertNotIn('OR_RW',text,str(path));self.assertNotIn('Q25/Q75',text,str(path))
 def test_O_diagnostic_models_cannot_authorize(self):
  good=CandidateGate(True,True,True,True,True,True);bad=CandidateGate(False,False,False,False,True,True)
  for key in ['D1','D2']:self.assertFalse(select_future_model({k:good if k==key else bad for k in ['D0','D1','D2','D3']})['stage3e_authorized'])
 def test_P_only_D3_all_gates(self):
  good=CandidateGate(True,True,True,True,True,True);gates={k:good for k in ['D0','D1','D2','D3']};self.assertTrue(select_future_model(gates)['stage3e_authorized'])
  for i in range(6):
   values=[True]*6;values[i]=False;gates['D3']=CandidateGate(*values);self.assertFalse(select_future_model(gates)['stage3e_authorized'])
 def test_Q_conditional_rules_unchanged(self):self.assertEqual(self.a['PPC'],self.p['PPC']);self.assertEqual(self.a['diagnostics'],self.p['diagnostics'])
 def test_R_joint_rules_unchanged(self):self.assertEqual(self.a['PPC']['joint_failure_rules'],self.p['PPC']['joint_failure_rules'])
 def test_S_2013_excluded(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_T_panel_hash(self):self.assertEqual(sha(PANEL),EXPECTED)
 def test_U_no_threshold(self):self.assertEqual(len(self.d),4117);self.assertEqual((self.d.fta>0).sum(),3980);self.assertEqual(self.d.fta.sum(),469099)
 def test_V_no_new_confounders(self):
  names={x.name for x in build('D3').free_RVs};self.assertEqual(names,{'beta_0','beta_RW','beta_H','beta_position','beta_season','chol_cov','z_player','a_0','a_RW','a_H','a_position','a_season','log_alpha_FTA','log_kappa'})
 def test_W_no_causal_interpretation(self):
  text=(ROOT/'docs/stage3dr_opportunity_prior_and_adequacy.md').read_text();self.assertIn('associational',text);self.assertIn('No causal claim',text);self.assertFalse(read(E/'stage3e_authorization.json')['stage3e_executed'])
if __name__=='__main__':unittest.main()
