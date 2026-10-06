"""Protocol, data, model, diagnostic and immutable-result tests for Stage 3C."""
import unittest,sys,json
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3c_setup import E,M,F,read,sha,panel,INTERPRETATION
from stage3c_model import data,protocol,KEY,build
class Stage3C(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=protocol();cls.d,cls.receipt=panel('primary');cls.full,cls.fr=panel('full')
 def test_A_authorization(self):self.assertTrue(read(ROOT/'docs/stage3b_evidence/part_b_authorization.json')['part_b_authorized'])
 def test_B_historical_failure(self):self.assertEqual(read(ROOT/'docs/stage3_evidence/multi_season_source_validation.json')['part_A_source_gate'],'BLOCKED')
 def test_C_unresolved_precision_preserved(self):
  self.assertEqual(read(ROOT/'docs/stage3a_evidence/stage3a_decision.json')['stage3a_classification'],'UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE')
  for path,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/path),h,path)
 def test_D_primary_hash(self):self.assertEqual(self.receipt['sha256'],'1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871')
 def test_E_full_hash(self):self.assertEqual(self.fr['sha256'],'5306ffd228fb71b34b174d18cf86e351b6fa48598579e4f49935078239662978')
 def test_F_primary_exclusion(self):self.assertNotIn('2013-14',set(self.d.season));self.assertEqual(self.d.season.nunique(),13)
 def test_G_full_development(self):self.assertIn('2013-14',set(self.full.season));self.assertEqual(self.full.season.nunique(),14)
 def test_H_frozen_residualization(self):
  self.assertEqual(self.p['residualization'],{'intercept':4.574910520685837,'slope':1.0013410045156863,'refitted':False});np.testing.assert_array_equal(self.d.residual_wingspan,self.d.wingspan_inches-(4.574910520685837+1.0013410045156863*self.d.height_wo_shoes_inches))
 def test_I_fixed_vectors(self):
  for field in ['combine_year','combine_position','height_wo_shoes_inches','wingspan_inches','residual_wingspan']:self.assertTrue((self.d.groupby('player_id')[field].nunique()==1).all())
 def test_J_no_future_measurement(self):self.assertTrue((self.d.combine_year<=self.d.first_observed_season.str[:4].astype(int)).all())
 def test_K_count_bounds(self):self.assertTrue(((self.d.ftm>=0)&(self.d.ftm<=self.d.fta)&(self.d.fta%1==0)&(self.d.ftm%1==0)).all())
 def test_L_zero_attempts(self):
  d,y,*_=data('primary');self.assertEqual(len(d),4117);self.assertEqual(len(y),3980);self.assertEqual((d.fta==0).sum(),137);self.assertEqual(int(y.fta.sum()),469099);self.assertEqual(d.player_id.nunique(),857);self.assertTrue((y.fta>0).all())
 def test_M_exact_model_terms(self):
  self.assertEqual(self.p['predictors'],['residual_wingspan','centered_height','original_combine_position','season','player_random_intercept']);model=build('primary');self.assertEqual(set(x.name for x in model.free_RVs),{'beta_0','beta_RW','beta_H','position_effect','season_effect','sigma_player','z_player','log_kappa'});self.assertEqual(type(model.observed_RVs[0].owner.op).__name__,'BetaBinomialRV')
 def test_N_no_FTA_predictor(self):self.assertNotIn('FTA',self.p['predictors']);self.assertIn('n=FTA',self.p['likelihood'])
 def test_O_no_minutes_predictor(self):self.assertFalse(any('minute' in x.lower() for x in self.p['predictors']))
 def test_P_no_new_confounder(self):self.assertFalse(set(self.p['predictors'])&{'age','experience','team'})
 def test_Q_priors_before_fitting(self):
  self.assertEqual(sha(E/'model_protocol.json'),read(E/'protocol_freeze_receipt.json')['sha256']);self.assertEqual(self.p['priors']['beta_RW'],['Normal',0,.5]);self.assertEqual(self.p['priors']['log_kappa'],['Normal',3,2])
  for p in E.glob('*_sampling.json'):self.assertLess(self.p['frozen_at'],read(p)['started_at'])
  self.assertTrue(read(E/'prior_predictive_summary.json')['acceptable'])
 def test_R_noncentered_indexing(self):
  d,y,info,idx,*_=data('primary');self.assertEqual(list(np.array(info['player_ids'])[idx]),list(y.player_id));self.assertEqual(info['player_ids'],sorted(d.player_id.unique(),key=int));self.assertIn('sigma_player*z_player',self.p['random_effect']);index=pd.read_csv(E/'primary_player_index.csv',dtype={'player_id':str});self.assertEqual(list(index.player_id),info['player_ids'])
 def test_S_positive_shapes(self):
  for kind in (['primary','full'] if read(E/'primary_replication_result.json')['scientifically_reportable'] else ['primary']):
   p=read(E/f'{kind}_posterior_predictive_summary.json');self.assertGreater(p['minimum_alpha'],0);self.assertGreater(p['minimum_beta'],0)
 def test_T_kappa_rho(self):
  import arviz as az
  result=read(E/'primary_replication_result.json');post=az.from_netcdf(M/f"primary_attempt{result['attempt']}_trace.nc").posterior
  np.testing.assert_allclose(post.kappa,np.exp(post.log_kappa),rtol=1e-14);np.testing.assert_allclose(post.rho,1/(1+post.kappa),rtol=1e-14);np.testing.assert_allclose(post.u_player,post.sigma_player.values[:,:,None]*post.z_player.values,rtol=1e-14)
 def test_U_diagnostics(self):
  for kind in (['primary','full'] if read(E/'primary_replication_result.json')['scientifically_reportable'] else ['primary']):
   d=read(E/f'{kind}_diagnostics.json');self.assertTrue(d['numeric_gate_pass']);self.assertLessEqual(d['max_rhat'],1.01);self.assertGreaterEqual(d['min_bulk_ESS'],400);self.assertGreaterEqual(d['min_tail_ESS'],400);self.assertEqual(d['divergences'],0);self.assertGreaterEqual(min(d['BFMI_by_chain']),.3);self.assertTrue(d['finite_covariance']);self.assertTrue(d['visual_review']['chains_mix'])
 def test_V_freeze_before_full(self):
  p=read(E/'primary_replication_result.json');f=read(E/'full_panel_result.json')
  if not p['scientifically_reportable']:
   self.assertEqual(f['status'],'NOT_RUN_PRIMARY_PPC_FAILED');self.assertFalse(f['model_fitted']);self.assertFalse(list(E.glob('full_attempt*_sampling.json')))
   from stage3c_model import fit
   with self.assertRaises(AssertionError):fit('full')
   return
  self.assertLess(p['frozen_at'],f['frozen_at'])
  for file in E.glob('full_attempt*_sampling.json'):self.assertLess(p['frozen_at'],read(file)['started_at']);self.assertEqual(read(file)['primary_freeze_sha256'],sha(E/'primary_replication_result.json'))
 def test_W_no_stage3d(self):
  expected={'primary','full'} if read(E/'primary_replication_result.json')['scientifically_reportable'] else {'primary'}
  self.assertFalse(self.p['stage3d_authorized']);self.assertEqual({read(p)['kind'] for p in E.glob('*_sampling.json')},expected);self.assertFalse(any('stage3d' in p.name for p in E.iterdir()))
 def test_X_associational_interpretation(self):
  self.assertEqual(self.p['interpretation'],INTERPRETATION);self.assertIn('does not identify a causal effect',INTERPRETATION);self.assertIn('associations',INTERPRETATION)
 def test_Y_primary_exact_replay(self):
  self.assertTrue(read(E/'reproduction_check.json')['primary_exact_saved_trace_replay'])
  if read(E/'primary_replication_result.json')['scientifically_reportable']:self.assertTrue(read(E/'reproduction_check.json')['full_exact_saved_trace_replay'])
  self.assertTrue(read(E/'reproduction_check.json')['sampler_reproduction_passed'])
 def test_Z_PPC_and_minute_limitation(self):
  primary=read(E/'primary_replication_result.json')
  self.assertEqual(primary['scientifically_reportable'],not primary['PPC']['serious_failure_by_frozen_rule'] and primary['PPC']['visual_review']['acceptable'])
  if not primary['scientifically_reportable']:self.assertFalse(read(E/'full_panel_result.json')['scientifically_reportable'])
  report=(ROOT/'docs/stage3c_primary_hierarchical_replication.md').read_text();self.assertIn(self.p['minute_limitation'],report);self.assertIn(INTERPRETATION,report)
if __name__=='__main__':unittest.main()
