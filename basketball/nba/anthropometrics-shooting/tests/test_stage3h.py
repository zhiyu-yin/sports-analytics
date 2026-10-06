import unittest,sys,inspect,ast,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3h_common import *
from stage3h_model import build,ztnb_logp
from stage3h_selection import Gates,next_candidate,decide
from stage3d_model import design
import stage3h_model,stage3f_model
class Stage3H(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d,cls.ids,cls.idx,*_=design();cls.models={k:build(k) for k in ['H1','H2']};cls.p=protocol()
  m=cls.models['H1'];cls.point=m.initial_point();cls.point['o_player']=np.linspace(-2,2,857);cls.point['e_player']=np.zeros(857);cls.point['sigma_accuracy_log__']=np.array(np.log(.7));cls.point['sigma_opportunity_log__']=np.array(np.log(.4));cls.point['lambda_h']=np.array(.5);cls.point['rho_AO_interval__']=np.array(np.log(.65/.35))
  cls.fun=m.compile_fn(m.replace_rvs_by_values([m[k] for k in ['accuracy_effect','positive_effect','hurdle_effect','mu_FTA']]),inputs=m.value_vars,on_unused_input='ignore',mode='FAST_COMPILE');cls.outputs=cls.fun(cls.point)
 def test_A_preservation(self):
  for path,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/path),h,path)
  for path,h in self.p['frozen_code'].items():self.assertEqual(sha(ROOT/path),h,path)
  for f in E.glob('*_sampling.json'):
   d=read(f);prior=read(E/(d['candidate'].lower()+'_prior_predictive.json'));self.assertTrue(prior['passed']);self.assertLess(self.p['frozen_at'],prior['started_at']);self.assertLess(prior['completed_at'],d['started_at']);self.assertLessEqual(d['attempt'],2)
 def test_B_panel(self):self.assertEqual(sha(PANEL),EXPECTED)
 def test_C_season(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_D_residualization(self):
  self.assertEqual(self.p['decomposition_csv_sha256'],sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv'))
  np.testing.assert_array_equal(observed_within(self.d),decomposition(self.d.fta.to_numpy(),self.d.games_played.to_numpy(),self.idx)[1])
 def test_E_no_between(self):
  for m in self.models.values():self.assertNotIn('theta_B',m.named_vars)
  self.assertNotIn('theta_W',self.models['H1'].named_vars);self.assertIn('theta_W',self.models['H2'].named_vars)
 def test_F_one_factor(self):
  for m in self.models.values():self.assertEqual({v.name for v in m.free_RVs if m.named_vars_to_dims.get(v.name)==('player',)},{'o_player','e_player'})
 def test_G_anchor(self):
  m=self.models['H1'];self.assertEqual(type(m['sigma_opportunity'].owner.op).__name__,'HalfNormalRV');np.testing.assert_allclose(self.outputs[1],.4*self.point['o_player'])
 def test_H_shared(self):np.testing.assert_allclose(self.outputs[2],.5*self.point['o_player'])
 def test_I_correlation(self):
  np.testing.assert_allclose(self.outputs[0],.7*.3*self.point['o_player'])
  for rho in [-.99,-.5,0,.5,.99]:
   L=np.array([[1,0],[rho,np.sqrt(1-rho*rho)]]);C=L@L.T;self.assertAlmostEqual(C[0,1],rho);np.testing.assert_allclose(np.diag(C),1)
 def test_J_covariance(self):
  for rho in np.linspace(-.999,.999,101):self.assertGreater(np.linalg.eigvalsh([[1,rho],[rho,1]]).min(),0)
  self.assertEqual(type(self.models['H1']['rho_AO'].owner.op).__name__,'UniformRV')
 def test_K_hurdle_rows(self):
  for m in self.models.values():np.testing.assert_array_equal(m['any_FTA'].tag.observations.eval(),(self.d.fta.to_numpy()>0).astype(int))
 def test_L_positive_rows(self):
  mask=self.d.fta.to_numpy()>0
  self.assertEqual(mask.sum(),3980)
  for m in self.models.values():
   np.testing.assert_array_equal(m['positive_FTA'].tag.observations.eval(),self.d.fta.to_numpy()[mask]);np.testing.assert_array_equal(m['FTM_count'].tag.observations.eval(),self.d.ftm.to_numpy()[mask])
 def test_M_offset(self):
  np.testing.assert_allclose(self.outputs[3],self.d.games_played.to_numpy()*2*np.exp(.4*self.point['o_player'][self.idx]));self.assertEqual(self.p['GP_offset_coefficient'],1)
 def test_N_no_minutes(self):
  attrs={n.attr for n in ast.walk(ast.parse(inspect.getsource(build))) if isinstance(n,ast.Attribute)};self.assertFalse(attrs&{'MIN','minutes','seconds'})
 def test_O_exact_ZTNB(self):
  self.assertIs(ztnb_logp,stage3f_model.ztnb_logp);d=read(ROOT/'docs/stage3f_evidence/likelihood_validation.json');self.assertLess(d['maximum_error_scipy'],1e-7);self.assertLess(d['maximum_error_native'],1e-7)
 def test_P_order(self):
  self.assertEqual(self.p['candidate_order'],['H1','H2']);self.assertIsNone(next_candidate(Gates(False)));self.assertEqual(next_candidate(Gates(True,False,True)),'H2')
  if (E/'h2_attempt1_sampling.json').exists():
   self.assertTrue(read(E/'h1_diagnostics.json')['sampler_pass']);self.assertFalse(read(E/'h1_conditional_accuracy_ppc.json')['gate_pass'] and read(E/'h1_joint_opportunity_ppc.json')['gate_pass'])
 def test_Q_H1_pass_stops(self):
  self.assertIsNone(next_candidate(Gates(True,True,True)))
  with self.assertRaises(AssertionError):decide(Gates(True,True,True),Gates(True))
 def test_R_no_H3(self):
  self.assertEqual(set(self.p['candidates']),{'H1','H2'})
  with self.assertRaises(AssertionError):build('H3')
 def test_S_firewall(self):
  import stage3h_sampling
  s=inspect.getsource(stage3h_sampling);self.assertIn("kind='diagnostics'",s);self.assertNotIn('plot_trace',s);self.assertNotIn('plot_rank',s)
  for f in E.glob('*_diagnostics.json'):
   d=read(f)
   if d.get('sampler_pass'):self.assertTrue(d['sealed_parameter_sampler_pass'])
 def test_T_no_exports(self):
  for f in list(E.glob('*.json'))+list(E.glob('*.csv'))+([ROOT/'docs/stage3h_shared_opportunity_factor.md'] if (ROOT/'docs/stage3h_shared_opportunity_factor.md').exists() else []):
   if f.name=='prior_preservation_manifest.json':
    for h in read(f).values():self.assertRegex(h,r'^[0-9a-f]{64}$')
    continue
   self.assertTrue('beta_RW' not in f.read_text(),str(f));self.assertTrue('OR_RW' not in f.read_text(),str(f))
 def test_U_boolean_selection(self):
  import stage3h_selection
  s=inspect.getsource(stage3h_selection);self.assertNotIn('beta_RW',s);self.assertNotIn('arviz',s);self.assertNotIn('open(',s)
  with self.assertRaises(TypeError):Gates(1)
 def test_V_no_threshold(self):self.assertEqual(len(self.d),4117);self.assertEqual(int(self.d.fta.sum()),469099);self.assertEqual(int((self.d.fta==0).sum()),137)
 def test_W_no_player_removal(self):self.assertEqual(len(self.ids),857)
 def test_X_no_confounder(self):
  expected={'beta_0','beta_RW','beta_H','beta_position','beta_season','o_player','e_player','sigma_accuracy','sigma_opportunity','lambda_h','rho_AO','a_0','a_RW','a_H','a_position','a_season','log_alpha_FTA','c_0','c_RW','c_H','c_position','c_season','log_kappa'}
  self.assertEqual({v.name for v in self.models['H1'].free_RVs},expected);self.assertEqual({v.name for v in self.models['H2'].free_RVs},expected|{'theta_W'})
 def test_Y_PPC_gates(self):
  old=read(ROOT/'docs/stage3f_evidence/model_protocol.json');p=copy.deepcopy(self.p['PPC']);p['seed']=old['PPC']['seed'];self.assertEqual(p,old['PPC']);self.assertEqual(self.p['positive_count_gate'],old['positive_count_gate'])
  for c in ['h1','h2']:
   for kind in ['conditional_accuracy','joint_opportunity']:
    f=E/(c+'_'+kind+'_ppc.json')
    if f.exists() and 'status' not in read(f):
     d=read(f);self.assertEqual(d['replicates'],2000);self.assertEqual(d['seed'],20260930)
     if kind=='joint_opportunity':self.assertEqual(d['generated_within_recomputed'],c=='h2')
 def test_Z_authorization(self):
  cases=[decide(Gates(False)),decide(Gates(True,True,True))]
  for a in [False,True]:
   for b in [False,True]:
    for s in [False,True]:cases.append(decide(Gates(True,False,False),Gates(s,a,b)))
  for r in cases:self.assertEqual(r['stage3g_authorized'],r['classification_code'] in ['A','B']);self.assertFalse(r['scientific_effect_release_authorized']);self.assertFalse(r['stage3g_executed'])
  if (E/'stage3h_decision.json').exists():
   d=read(E/'stage3h_decision.json');a=read(E/'stage3g_authorization.json');self.assertEqual(a['authorized'],d['classification_code'] in ['A','B']);self.assertFalse(a['scientific_effect_release_authorized']);self.assertFalse(a['executed']);self.assertEqual(a['decision_sha256'],sha(E/'stage3h_decision.json'))
if __name__=='__main__':unittest.main()
