"""A-Y implementation and completed-artifact checks; prefit uses synthetic fits only."""
import unittest,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from stage3j_core import *
from scipy.special import expit
from scipy.stats import betabinom
from stage2_models import logpmf,objective
FINAL=os.environ.get('STAGE3J_FINAL')=='1'
class TestStage3J(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=protocol();cls.d=load();cls.full=load(True)
  rng=np.random.default_rng(94321);G=80;idx=np.repeat(np.arange(G),4);rw=np.repeat(rng.normal(size=G),4);height=np.repeat(rng.normal(77,3,size=G),4)
  cls.x=pd.DataFrame(dict(Intercept=np.ones(len(idx)),rw=rw,height=height));cls.n=rng.integers(10,100,len(idx));cls.y=rng.binomial(cls.n,expit(-1+.2*rw+.02*height));cls.g=idx
  cls.m,_,_=glm(cls.x,cls.y,cls.n)
 def test_A_historical_unchanged(self):
  for f,h in read(E/'prior_preservation_manifest.json').items():self.assertEqual(sha(ROOT/f),h,f)
 def test_B_primary_hash(self):self.assertEqual(sha(PANEL),PH)
 def test_C_full_hash(self):self.assertEqual(sha(FULL),FH)
 def test_D_development_excluded(self):self.assertNotIn('2013-14',set(self.d.season))
 def test_E_residual_exact(self):
  for d in [self.d,self.full]:np.testing.assert_array_equal(d.residual_wingspan,d.wingspan_inches-(4.574910520685837+1.0013410045156863*d.height_wo_shoes_inches))
 def test_F_formula(self):
  self.assertEqual(self.p['formula'],FORMULA);x=design(self.d,self.p);self.assertEqual(list(x.columns[:3]),['Intercept','residual_wingspan','height_wo_shoes_inches']);self.assertEqual(x.shape[1],28)
  self.assertEqual(self.p['position_reference'],'C');self.assertEqual(self.p['season_reference'],'2010-11')
 def test_G_no_random_effect(self):self.assertFalse(self.p['random_effects']);self.assertFalse(any('player' in s for s in design(self.d,self.p).columns))
 def test_H_no_opportunity_model(self):self.assertFalse(self.p['opportunity_model'])
 def test_I_no_FTA_predictor(self):self.assertFalse(any('fta' in s.lower() for s in design(self.d,self.p).columns))
 def test_J_no_MIN_predictor(self):self.assertFalse(any('min' in s.lower() for s in design(self.d,self.p).columns))
 def test_K_no_new_confounders(self):self.assertEqual(self.p['predictors'],['intercept','residual_wingspan','height_wo_shoes_inches','original_combine_position','season'])
 def test_L_player_clustering(self):self.assertEqual(self.p['cluster'],'player_id');self.assertEqual(counts(self.d)['contributing_players'],835)
 def test_M_grouped_counts(self):
  np.testing.assert_array_equal(self.m.model.n_trials,self.n)
  for d in [self.d,self.full]:self.assertTrue(((d.ftm%1==0)&(d.fta%1==0)&(d.ftm>=0)&(d.fta>=0)).all())
  np.testing.assert_array_equal(self.m.model.endog,self.y/self.n)
 def test_N_makes_no_more_than_attempts(self):self.assertTrue((self.d.ftm<=self.d.fta).all());self.assertTrue((self.full.ftm<=self.full.fta).all())
 def test_O_zero_accounting(self):self.assertEqual(len(self.d),4117);self.assertEqual(int((self.d.fta==0).sum()),137);self.assertEqual(len(self.d[self.d.fta>0]),3980)
 def test_P_independent_sandwich(self):
  c,parts,v=validate_cov(self.m,self.y,self.n,self.g);self.assertTrue(v['passed']);self.assertAlmostEqual(parts['correction'],80/79*319/317)
  # Two independent copies of every cluster halve uncorrected variance; merging IDs does not.
  x=pd.concat([self.x,self.x],ignore_index=True);y=np.tile(self.y,2);n=np.tile(self.n,2);m,_,_=glm(x,y,n)
  independent_ids=np.r_[self.g,self.g+80];merged=np.tile(self.g,2)
  cc=cov_cluster(m,independent_ids,False);cm=cov_cluster(m,merged,False)
  np.testing.assert_allclose(cc,cov_cluster(self.m,self.g,False)/2,rtol=1e-7,atol=1e-9);np.testing.assert_allclose(cm,2*cc,rtol=1e-7,atol=1e-9)
  w=np.repeat(np.linspace(.2,1,80),4);mw,_,_=glm(self.x,self.y,self.n,w);validate_cov(mw,self.y,self.n,self.g,w)
  np.testing.assert_allclose(mw.model.score_obs(mw.params),np.asarray(self.x)*(w*(self.y-self.n*np.asarray(mw.fittedvalues)))[:,None],atol=1e-10)
  hw=sandwich(mw,self.y,self.n,self.g,w)[1]['bread'];np.testing.assert_allclose(np.linalg.inv(hw),-mw.model.hessian(mw.params),rtol=1e-9,atol=1e-7)
  if FINAL:self.assertTrue(read(E/'j1_cluster_validation.json')['passed'])
 def test_Q_player_sampling(self):
  layout=player_layout(self.d);rows,instances,draws=draw_clusters(layout,np.random.default_rng(20260930));self.assertEqual(len(draws),857);self.assertLess(len(np.unique(draws)),857);self.assertEqual(len(np.unique(instances)),857)
 def test_R_full_clusters_seed_and_failure_policy(self):
  layout=player_layout(self.d);a=draw_clusters(layout,np.random.default_rng(20260930));b=draw_clusters(layout,np.random.default_rng(20260930))
  for aa,bb in zip(a,b):np.testing.assert_array_equal(aa,bb)
  rows,instances,draws=a
  for j,g in enumerate(draws):np.testing.assert_array_equal(rows[instances==j],layout[1][g])
  self.assertEqual(self.p['bootstrap']['interval'],'95% percentile numpy quantile method=linear');self.assertEqual(self.p['bootstrap']['replicates'],2000)
  fixture=pd.DataFrame(dict(status=['PASS','FAIL','PASS'],beta=[-1,np.nan,1]));s=boot_summary(fixture,1);self.assertEqual(s['failed'],1);self.assertEqual(s['replicates'],3);np.testing.assert_allclose(s['percentile_CI'],[-.95,.95])
  if FINAL:
   for tag in ['j1','j2']:
    f=pd.read_csv(E/(tag+'_player_bootstrap.csv'));self.assertEqual(f.replicate.tolist(),list(range(1,2001)));self.assertTrue((f.loc[f.status=='PASS','draws']==857).all());s=read(E/(tag+'_bootstrap_summary.json'));recomputed=boot_summary(f,s['seed']);np.testing.assert_allclose([s['mean'],s['SD'],*s['percentile_CI'],s['fraction_beta_negative']],[recomputed['mean'],recomputed['SD'],*recomputed['percentile_CI'],recomputed['fraction_beta_negative']],rtol=1e-12,atol=1e-14);self.assertEqual(s['failed'],recomputed['failed']);self.assertLessEqual(s['failed'],20)
   self.assertTrue(read(E/'bootstrap_reproduction.json')['passed'])
 def test_S_primary_before_sensitivities(self):
  self.assertIn('immutable primary_result',self.p['ordering'])
  if FINAL:self.assertLess(read(E/'primary_result.json')['frozen_at'],read(E/'sensitivities_start.json')['started_at'])
  else:
   self.assertFalse((E/'primary_result.json').exists())
   with self.assertRaises((FileNotFoundError,AssertionError)):authorize(True)
 def test_T_J2_secondary_and_likelihood(self):
  self.assertEqual(self.p['interpretation']['primary'],'J1 always; no secondary replacement')
  y=np.array([0,4,8]);n=np.array([10,10,10]);mu=np.array([.2,.4,.7]);k=30
  np.testing.assert_allclose(logpmf(y,n,mu,k),betabinom.logpmf(y,n,mu*k,(1-mu)*k),atol=1e-10)
  # Exercise unchanged three-start BB wrapper on synthetic extra-binomial data.
  rng=np.random.default_rng(174);x=pd.DataFrame(dict(Intercept=np.ones(1000),rw=rng.normal(size=1000),height=rng.normal(size=1000)));mu=expit(x@np.array([.8,-.2,.1]));n=rng.integers(20,100,1000);y=rng.binomial(n,rng.beta(mu*25,(1-mu)*25));m,xx,_=glm(x,y,n);fit=fit_bb(xx,y,n,np.asarray(m.params));self.assertTrue(fit['converged']);self.assertLess(abs(fit['beta'][1]+.2),.1)
  if FINAL:self.assertFalse(read(E/'j2_beta_binomial_result.json')['primary'])
 def test_U_first_season_selection(self):
  first=self.d.sort_values(['player_id','season'],kind='stable').drop_duplicates('player_id');changed=self.d.copy();changed['ftm']=0;changed['fta']=0;other=changed.sort_values(['player_id','season'],kind='stable').drop_duplicates('player_id')
  pd.testing.assert_frame_equal(first[['player_id','season']],other[['player_id','season']]);self.assertEqual(len(first),857)
  if FINAL:
   saved=pd.read_csv(E/'j3_selected_first_seasons.csv',dtype={'player_id':str});self.assertEqual(set(zip(saved.player_id,saved.season)),set(zip(first.player_id.astype(str),first.season)))
 def test_V_thresholds(self):
  self.assertEqual(self.p['sensitivities']['J6'],[50,100])
  if FINAL:self.assertEqual(pd.read_csv(E/'j6_fta_thresholds.csv').threshold.tolist(),[50,100])
 def test_W_no_post_result_tuning(self):
  protocol();self.assertEqual(sha(E/'j4_weight_semantics.md'),self.p['J4_weight_note_sha256'])
  if FINAL:
   self.assertEqual(sha(E/'primary_result.json'),read(E/'primary_freeze_receipt.json')['sha256']);self.assertLess(self.p['frozen_at'],read(E/'implementation_test_summary.json')['finished_at']);self.assertLess(read(E/'implementation_test_summary.json')['finished_at'],read(E/'j1_execution_start.json')['started_at'])
 def test_X_full_after_primary(self):
  self.assertIn('after primary freeze',self.p['sensitivities']['full'])
  if FINAL:self.assertLess(read(E/'primary_result.json')['frozen_at'],read(E/'full_panel_start.json')['started_at'])
  else:self.assertFalse((E/'full_panel_secondary_result.json').exists())
 def test_Y_associational_interpretation(self):
  self.assertTrue(self.p['interpretation']['no_causal_claim']);self.assertIn('between players',self.p['estimand'])
  if FINAL:
   s=read(E/'scientific_interpretation.json');self.assertFalse(s['causal']);self.assertNotIn('causes',s['main_text'].lower());self.assertIn('association',s['main_text'].lower())
if __name__=='__main__':unittest.main(verbosity=2)
