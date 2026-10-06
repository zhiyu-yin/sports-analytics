"""Stage 3D provenance, model graphs, firewall and mandatory-prior-stop tests."""
import unittest,sys,inspect,ast,itertools
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3d_protocol import *
from stage3d_model import build,design,authorize_posterior
from stage3d_selection import CandidateGate,select_future_model,accuracy_gate,opportunity_gate,systematic_volume_pattern

class Stage3D(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=fixed_data();cls.p=protocol();cls.decision=read(E/'model_adequacy_decision.json')
 def test_A_stage3c_failure_and_all_history_preserved(self):
  self.assertEqual(read(ROOT/'docs/stage3c_evidence/execution_status.json')['stage3c_execution'],'FAIL')
  for name,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/name),h,name)
 def test_B_primary_hash(self):self.assertEqual(sha(PANEL),EXPECTED)
 def test_C_development_season_absent(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_D_frozen_bins(self):self.assertEqual(self.p['bins'],[[1,9,'1-9'],[10,49,'10-49'],[50,99,'50-99'],[100,299,'100-299'],[300,None,'300+']])
 def test_E_definitions_frozen_before_simulation_no_fits(self):
  for k in ['d1','d2','d3']:
   prior=read(E/(k+'_prior_predictive.json'));self.assertLess(self.p['frozen_at'],prior['started_at']);self.assertEqual(prior['protocol_sha256'],sha(E/'model_adequacy_protocol.json'))
  self.assertFalse(list(M.glob('*posterior*')));self.assertFalse(list(E.glob('*sampling_attempt*')))
 def test_F_selection_firewall(self):
  source=inspect.getsource(select_future_model);self.assertNotIn('beta_RW',source);self.assertNotIn('read(',source);self.assertNotIn('open(',source)
  good=CandidateGate(True,True,True,True,True,True);gates={k:good for k in ['D0','D1','D2','D3']}
  with self.assertRaises(TypeError):CandidateGate(True,True,True,True,True,True,beta_RW={'mean':-1})
  gates['D3']={'sampler_pass':True,'beta_RW':{'mean':-1}}
  with self.assertRaises(TypeError):select_future_model(gates)
 def test_G_no_sealed_summaries_in_outputs(self):
  for name in ['model_adequacy_comparison.csv','model_adequacy_decision.json']:
   text=(E/name).read_text();self.assertNotIn('beta_RW',text);self.assertNotIn('OR_RW',text);self.assertNotIn('Q25/Q75',text)
  report=(ROOT/'docs/stage3d_attempt_volume_model_adequacy.md').read_text();self.assertNotIn('beta_RW',report);self.assertNotIn('OR_RW',report)
 def gates(self,winner):
  bad=CandidateGate(False,False,False,False,True,True);good=CandidateGate(True,True,True,True,True,True)
  return {k:good if k==winner else bad for k in ['D0','D1','D2','D3']}
 def test_H_D1_cannot_authorize(self):self.assertFalse(select_future_model(self.gates('D1'))['stage3e_authorized'])
 def test_I_D2_cannot_authorize(self):self.assertFalse(select_future_model(self.gates('D2'))['stage3e_authorized'])
 def test_J_only_D3_all_gates(self):
  self.assertTrue(select_future_model(self.gates('D3'))['stage3e_authorized'])
  for i in range(6):
   values=[True]*6;values[i]=False;g=self.gates('D3');g['D3']=CandidateGate(*values);self.assertFalse(select_future_model(g)['stage3e_authorized'])
  self.assertFalse(self.decision['stage3e_authorized']);self.assertEqual(self.decision['selected_future_model'],'NONE')
 def test_K_fixed_GP_offset(self):
  gp=read(E/'gp_offset_validation.json');self.assertEqual(gp['coefficient'],1);self.assertTrue(gp['GP_positive']);self.assertTrue(gp['log_GP_finite']);self.assertTrue(gp['official_GP_exact'])
  source=inspect.getsource(build);self.assertIn('np.log(d.games_played.to_numpy())+log_rate',source);self.assertFalse(any('GP' in x.name or 'gp' in x.name for x in build('D3').free_RVs))
 def test_L_no_minutes(self):
  tree=ast.parse(inspect.getsource(build));attributes={n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)};self.assertFalse(attributes&{'minutes','seconds','MIN'})
 def test_M_zero_rows_opportunity(self):
  model=build('D3');self.assertEqual(model['FTA_count'].tag.observations.eval().shape,(4117,));self.assertEqual((self.d.fta==0).sum(),137)
 def test_N_accuracy_positive_only(self):
  model=build('D3');self.assertEqual(model['FTM_count'].tag.observations.eval().shape,(3980,));self.assertEqual(len(model.coords['accuracy_row']),3980)
 def test_O_counts_valid(self):self.assertTrue(((self.d.ftm>=0)&(self.d.ftm<=self.d.fta)).all())
 def test_P_bivariate_index(self):
  d,ids,idx,*_=design();self.assertEqual(list(np.asarray(ids)[idx]),list(d.player_id));saved=pd.read_csv(E/'player_index.csv',dtype={'player_id':str});self.assertEqual(list(saved.player_id),ids);self.assertIn('pt.dot(z,chol.T)',inspect.getsource(build));self.assertEqual(build('D3').coords['effect'],('accuracy','opportunity'))
 def test_Q_prior_correlation_valid(self):
  x=np.load(M/'d3_prior_predictive_checks.npz');corr=x['correlation'];np.testing.assert_allclose(corr,np.swapaxes(corr,-1,-2));np.testing.assert_allclose(np.diagonal(corr,axis1=-2,axis2=-1),1);self.assertTrue((np.linalg.eigvalsh(corr)>0).all());self.assertTrue((x['SD']>0).all())
 def initial(self,model,names):
  outputs=model.replace_rvs_by_values([model[n] for n in names]);fn=model.compile_fn(outputs,inputs=model.value_vars,on_unused_input='ignore',mode='FAST_COMPILE');return fn(model.initial_point())
 def test_R_beta_binomial_shapes_valid_initial_point(self):
  for candidate in ['D1','D2','D3']:
   model=build(candidate);mu,k=self.initial(model,['mu_accuracy','kappa']);self.assertTrue((mu*k>0).all());self.assertTrue(((1-mu)*k>0).all())
 def test_S_negative_binomial_valid(self):
  model=build('D3');mu,a=self.initial(model,['mu_FTA','alpha_FTA']);self.assertTrue((mu>0).all());self.assertTrue(np.isfinite(mu).all());self.assertGreater(a,0)
 def test_T_gate_rules_and_prior_stop(self):
  for pooled,g,s,b,pattern in itertools.product([False,True],range(5),range(14),range(6),[False,True]):
   actual=accuracy_gate(pooled_rate_99_pass=pooled,global_metrics_99_fail_count=g,season_rate_99_fail_count=s,season_count=13,FTA_bin_99_fail_count=b,systematic_volume_pattern=pattern)
   self.assertEqual(actual,pooled and g<3 and s<5 and b<2 and not pattern)
  for z,q,low,high in itertools.product([False,True],range(6),range(6),range(6)):
   self.assertEqual(opportunity_gate(zero_frequency_99_pass=z,quantile_99_fail_count=q,season_totals_outside_99_low=low,season_totals_outside_99_high=high,season_count=13),z and q<3 and low<5 and high<5)
  self.assertTrue(systematic_volume_pattern([0]*5,[1,1,0,-1,-1],[.1]*5));self.assertFalse(systematic_volume_pattern([0]*5,[1,1,0,-1,-1],[1]*5))
  with self.assertRaises(RuntimeError):authorize_posterior()
  self.assertEqual(self.decision['stop_phase'],'PRIOR_PREDICTIVE')
 def test_U_no_threshold_filter(self):self.assertEqual(len(self.d),4117);self.assertEqual((self.d.fta>0).sum(),3980);self.assertEqual(int(self.d.fta.sum()),469099)
 def test_V_frozen_exposure(self):
  np.testing.assert_array_equal(self.d.residual_wingspan,self.d.wingspan_inches-(4.574910520685837+1.0013410045156863*self.d.height_wo_shoes_inches));self.assertFalse(self.p['frozen_exposure']['refitted'])
 def test_W_no_full_panel(self):self.assertEqual(PANEL.name,'stage3_primary_replication_panel.parquet');self.assertEqual(self.d.season.nunique(),13);self.assertFalse(any('full' in p.name for p in M.iterdir()))
 def test_X_no_scientific_interpretation(self):
  self.assertFalse(self.decision['scientific_effect_accessed']);self.assertEqual(self.decision['posterior_fits'],0);self.assertFalse(read(E/'stage3e_authorization.json')['stage3e_executed']);self.assertIn('No scientific replication claim',(ROOT/'docs/stage3d_attempt_volume_model_adequacy.md').read_text())
if __name__=='__main__':unittest.main()
