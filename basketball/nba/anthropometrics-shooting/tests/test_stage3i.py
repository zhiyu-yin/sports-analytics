import unittest,sys,inspect,ast,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3i_common import *
from stage3i_model import build,ztnb_logp
from stage3i_selection import decide
from stage3d_model import design
import stage3i_model,stage3f_model,stage3h_model
class Stage3I(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d,cls.ids,cls.idx,*_=design();cls.models={k:build(k) for k in ['I1','I2','I3']};cls.models['H2']=stage3h_model.build('H2');cls.p=protocol();cls.outputs={};cls.points={};cls.funcs={}
  for k,m in cls.models.items():
   p=m.initial_point();p['o_player']=np.linspace(-2,2,857);p['e_player']=np.zeros(857);p['sigma_accuracy_log__']=np.array(np.log(.7));p['sigma_opportunity_log__']=np.array(np.log(.4));p['lambda_h']=np.array(.5);p['rho_AO_interval__']=np.array(np.log(.65/.35))
   if 'c_player' in p:p['c_player']=np.linspace(1,-1,857);p['sigma_count_resid_log__']=np.array(np.log(.3))
   if 'gamma_W1' in p:p['gamma_W1']=np.array(.1);p['gamma_W2']=np.array(.02)
   if 'theta_W' in p:p['theta_W']=np.array(.2)
   fn=m.compile_fn(m.replace_rvs_by_values([m[x] for x in ['mu_accuracy_all','mu_FTA','pi_hurdle']]),inputs=m.value_vars,on_unused_input='ignore',mode='FAST_COMPILE')
   cls.funcs[k]=fn;cls.points[k]=p;cls.outputs[k]=fn(p)
 def test_A_history(self):
  for path,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/path),h,path)
  authorize()
  for c in ['i1','i2','i3']:
   f=E/(c+'_prior_predictive.json')
   if f.exists():self.assertLess(self.p['frozen_at'],read(f)['started_at'])
  for c,prev in [('i2','i1'),('i3','i2')]:
   f=E/(c+'_attempt1_sampling.json')
   if f.exists():
    self.assertTrue((E/(prev+'_diagnostics.json')).exists())
    if read(E/(prev+'_diagnostics.json')).get('sampler_pass'):self.assertLess(read(E/(prev+'_PPC_visual_review.json'))['reviewed_at'],read(f)['started_at'])
  for f in E.glob('*_sampling.json'):
   r=read(f);self.assertIn(r['attempt'],[1,2]);self.assertLess(self.p['frozen_at'],r['started_at'])
   for c in ['i1','i2','i3']:self.assertLess(read(E/(c+'_prior_predictive.json'))['completed_at'],r['started_at'])
   settings=self.p['sampling'].copy()
   if r['attempt']==2:settings.update(self.p['recovery'])
   self.assertEqual(r['settings'],settings)
 def test_B_panel(self):self.assertEqual(sha(PANEL),EXPECTED)
 def test_C_season(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_D_I0(self):
  for n,r in read(E/'i0_baseline_manifest.json')['files'].items():self.assertEqual(sha(ROOT/n),r['sha256']);self.assertEqual(sha(ROOT/r['copy']),r['sha256'])
  self.assertFalse(list(M.glob('i0*')))
 def test_E_within(self):
  self.assertEqual(self.p['decomposition_csv_sha256'],sha(ROOT/'docs/stage3f_evidence/opportunity_decomposition.csv'))
  np.testing.assert_array_equal(observed_within(self.d),decomposition(self.d.fta.to_numpy(),self.d.games_played.to_numpy(),self.idx)[1])
 def test_F_basis(self):
  w=observed_within(self.d);b=read(E/'within_quadratic_basis.json');self.assertEqual(b['s_W'],w.std(ddof=1));z,q=quadratic_basis(w)
  np.testing.assert_array_equal(z,w/w.std(ddof=1));np.testing.assert_array_equal(q,z*z-np.mean(z*z))
  d=self.d.copy();d.ftm=0;np.testing.assert_array_equal(quadratic_basis(observed_within(d)),[z,q]);self.assertNotIn('ftm',inspect.getsource(quadratic_basis))
 def test_G_center(self):self.assertLess(abs(quadratic_basis(observed_within(self.d))[1].mean()),1e-14)
 def test_H_no_between(self):
  for m in self.models.values():self.assertNotIn('theta_B',m.named_vars)
 def test_I_accuracy_only(self):
  for j in [1,2]:np.testing.assert_array_equal(self.outputs['I1'][j],self.outputs['H2'][j])
  from scipy.special import logit
  z,q=quadratic_basis(observed_within(self.d));np.testing.assert_allclose(logit(self.outputs['I1'][0])-logit(self.outputs['H2'][0]),.1*z+.02*q-.2*observed_within(self.d),atol=1e-13)
 def test_J_count_only(self):
  for j in [0,2]:np.testing.assert_array_equal(self.outputs['I2'][j],self.outputs['H2'][j])
  np.testing.assert_allclose(self.outputs['I2'][1]/self.outputs['H2'][1],np.exp(.3*self.points['I2']['c_player'][self.idx]))
 def test_K_independence(self):
  from pytensor.graph.basic import ancestors
  for k in ['I2','I3']:
   m=self.models[k];c=m['c_player'];self.assertEqual(type(c.owner.op).__name__,'NormalRV')
   self.assertNotIn(m['o_player'],set(ancestors([c])));self.assertNotIn(m['e_player'],set(ancestors([c])))
   p=copy.deepcopy(self.points[k]);p['c_player']*=2;out=self.funcs[k](p)
   for j in [0,2]:np.testing.assert_array_equal(out[j],self.outputs[k][j])
 def test_L_correlations(self):
  for m in self.models.values():self.assertEqual({x.name for x in m.free_RVs if 'rho' in x.name or 'corr' in x.name},{'rho_AO'})
 def test_M_union(self):
  for j,k in [(0,'I1'),(1,'I2'),(2,'H2')]:np.testing.assert_array_equal(self.outputs['I3'][j],self.outputs[k][j])
  for c in ['I1','I3']:
   for n in ['gamma_W1','gamma_W2']:
    rv=self.models[c][n];self.assertEqual(type(rv.owner.op).__name__,'NormalRV');self.assertEqual(float(rv.owner.inputs[-1].eval()),.25)
  for c in ['I2','I3']:self.assertEqual(float(self.models[c]['sigma_count_resid'].owner.inputs[-1].eval()),.5)
 def test_N_no_I4(self):
  self.assertEqual(self.p['candidate_order'],['I1','I2','I3']);self.assertEqual(set(self.p['candidates']),{'I1','I2','I3'});self.assertEqual(self.p['eligible_candidates'],['I3'])
  with self.assertRaises(AssertionError):build('I4')
 def test_O_hurdle(self):
  for m in self.models.values():np.testing.assert_array_equal(m['any_FTA'].tag.observations.eval(),(self.d.fta.to_numpy()>0).astype(int))
 def test_P_positive(self):
  mask=self.d.fta.to_numpy()>0;self.assertEqual(mask.sum(),3980)
  for m in self.models.values():
   np.testing.assert_array_equal(m['positive_FTA'].tag.observations.eval(),self.d.fta.to_numpy()[mask]);np.testing.assert_array_equal(m['FTM_count'].tag.observations.eval(),self.d.ftm.to_numpy()[mask])
 def test_Q_offset(self):
  np.testing.assert_allclose(self.outputs['I1'][1],self.d.games_played.to_numpy()*2*np.exp(.4*self.points['I1']['o_player'][self.idx]));self.assertEqual(self.p['GP_offset_coefficient'],1)
 def test_R_no_MIN(self):
  attrs={n.attr for n in ast.walk(ast.parse(inspect.getsource(build))) if isinstance(n,ast.Attribute)};self.assertFalse(attrs&{'MIN','minutes','seconds'})
 def test_S_no_threshold(self):self.assertEqual(len(self.d),4117);self.assertEqual(int(self.d.fta.sum()),469099);self.assertEqual(int((self.d.fta==0).sum()),137)
 def test_T_no_exclusion(self):self.assertEqual(len(self.ids),857)
 def test_U_no_confounder(self):
  base={v.name for v in self.models['H2'].free_RVs};mods={'I1':(base-{'theta_W'})|{'gamma_W1','gamma_W2'},'I2':base|{'c_player','sigma_count_resid'},'I3':(base-{'theta_W'})|{'gamma_W1','gamma_W2','c_player','sigma_count_resid'}}
  for k,n in mods.items():self.assertEqual({v.name for v in self.models[k].free_RVs},n)
  for k in ['I1','I2','I3']:
   for rv in self.models[k].free_RVs:
    if rv.name not in base:continue
    old=self.models['H2'][rv.name];self.assertEqual(type(rv.owner.op),type(old.owner.op))
    for x,y in zip(rv.owner.inputs[-2:],old.owner.inputs[-2:]):np.testing.assert_array_equal(x.eval(),y.eval())
 def test_V_ZTNB(self):
  self.assertIs(ztnb_logp,stage3f_model.ztnb_logp);d=read(ROOT/'docs/stage3f_evidence/likelihood_validation.json');self.assertLess(d['maximum_error_scipy'],1e-7);self.assertLess(d['maximum_error_native'],1e-7)
 def test_W_firewall(self):
  import stage3i_sampling
  s=inspect.getsource(stage3i_sampling);self.assertIn("kind='diagnostics'",s);self.assertNotIn('plot_trace',s);self.assertNotIn('plot_rank',s)
  for f in E.glob('*_diagnostics.json'):
   d=read(f)
   if d.get('sampler_pass'):self.assertTrue(d['sealed_parameter_sampler_pass'])
  for c in ['i1','i2','i3']:
   f=E/(c+'_diagnostics.json')
   if f.exists() and read(f).get('sampler_pass') is False:
    for suffix in ['conditional_accuracy_ppc','joint_opportunity_ppc']:
     r=read(E/(c+'_'+suffix+'.json'));self.assertEqual(r['status'],'WITHHELD_FAILED_SAMPLER_GATE');self.assertIsNone(r['gate_pass'])
    if c in ['i2','i3']:self.assertEqual(read(E/(c+'_count_residual_parameter.json'))['status'],'WITHHELD_FAILED_SAMPLER_GATE')
 def test_X_exports(self):
  for f in list(E.glob('*.json'))+list(E.glob('*.csv'))+([ROOT/'docs/stage3i_residual_adequacy.md'] if (ROOT/'docs/stage3i_residual_adequacy.md').exists() else []):
   if f.name=='prior_preservation_manifest.json':
    for h in read(f).values():self.assertRegex(h,r'^[0-9a-f]{64}$')
    continue
   self.assertNotIn('beta_RW',f.read_text(),str(f));self.assertNotIn('OR_RW',f.read_text(),str(f))
 def test_Y_selection(self):
  import stage3i_selection
  s=inspect.getsource(stage3i_selection)
  for word in ['beta_RW','arviz','open(','read(']:self.assertNotIn(word,s)
  with self.assertRaises(TypeError):decide(1,True,True,True)
  for sampler in [True,False]:
   for a in [True,False]:
    for o in [True,False]:
     r=decide(sampler,a,o,True);self.assertEqual(r['classification_code'],('A' if a and o else 'B' if o else 'C' if a else 'D') if sampler else 'D')
 def test_Z_gates(self):
  old=read(ROOT/'docs/stage3h_evidence/model_protocol.json');self.assertEqual(self.p['PPC'],old['PPC']);self.assertEqual(self.p['positive_count_gate'],old['positive_count_gate'])
  for c in ['i1','i2','i3']:
   for kind in ['conditional_accuracy','joint_opportunity']:
    f=E/(c+'_'+kind+'_ppc.json')
    if f.exists() and 'status' not in read(f):
     d=read(f);self.assertEqual(d['replicates'],2000);self.assertEqual(d['seed'],20260930)
     if kind=='joint_opportunity':self.assertTrue(d['generated_within_recomputed'])
 def test_AA_authorization(self):
  for s in [True,False]:
   for a in [True,False]:
    for o in [True,False]:
     for f in [True,False]:
      r=decide(s,a,o,f);self.assertEqual(r['stage3g_authorized'],s and a and o and f);self.assertFalse(r['scientific_effect_release_authorized']);self.assertFalse(r['stage3g_executed'])
  if (E/'stage3i_decision.json').exists():
   d=read(E/'stage3i_decision.json');a=read(E/'stage3g_authorization.json');self.assertEqual(a['authorized'],d['classification_code']=='A');self.assertFalse(a['scientific_effect_release_authorized']);self.assertFalse(a['executed']);self.assertEqual(a['decision_sha256'],sha(E/'stage3i_decision.json'))
if __name__=='__main__':unittest.main()
