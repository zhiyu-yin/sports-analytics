import unittest,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import stage2_analysis as a
from stage2_models import fit_bb,hc0,effect
from stage2_validation import validate
class Stage2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.all,cls.d,cls.frozen=a.load(); cls.result=json.loads((a.E/'primary_robustness_result.json').read_text()); cls.loo=pd.read_csv(a.E/'loo_player_results.csv'); cls.m=a.glm(cls.d)
 def test_01_frozen_inputs(self): self.assertEqual(len(self.all),311); self.assertEqual(len(self.d),299); self.assertEqual(self.d.fta.sum(),42587)
 def test_02_frozen_stage1(self): self.assertEqual(float(self.m.params[a.PRIMARY]),self.frozen['models']['M2']['beta'])
 def test_03_prior_unchanged(self):
  prior=json.loads((a.E/'prior_preservation_manifest.json').read_text()); self.assertTrue(all(a.sha(ROOT/p)==h for p,h in prior.items()))
 def test_04_exact_formula(self):
  self.assertEqual(self.m.model.exog_names,['const',a.PRIMARY,a.H]+['position_'+c for c in sorted(self.d.position.unique())[1:]])
 def test_05_quasi_formula(self):
  phi=self.m.pearson_chi2/self.m.df_resid
  self.assertEqual(self.result['quasi']['beta'],self.result['stage1_M2']['beta'])
  self.assertAlmostEqual(self.result['quasi']['se'],self.m.bse[a.PRIMARY]*np.sqrt(phi),14)
 def test_06_hc0(self): np.testing.assert_allclose(hc0(self.m,self.d.ftm,self.d.fta),a.glm(self.d,cov_type='HC0').cov_params(),rtol=2e-7,atol=1e-9)
 def test_07_bb_numerical_validation(self): self.assertTrue(validate()['passed'])
 def test_08_bb_determinism(self):
  fit=fit_bb(a.design(self.d),self.d.ftm,self.d.fta,self.m.params)
  self.assertEqual(effect(fit['beta'],fit['cov'])['beta'],self.result['beta_binomial']['beta'])
  self.assertEqual(fit['rho'],self.result['beta_binomial']['dispersion_or_overdispersion'])
 def test_09_loo_count_unique(self):
  self.assertEqual(len(self.loo),299); self.assertEqual(self.loo.removed_id.nunique(),299); self.assertEqual(set(self.loo.removed_id.astype(str)),set(self.d.player_id.astype(str)))
 def test_10_loo_exact_removal(self):
  for row in self.loo.itertuples():
   sub=self.d[self.d.player_id.astype(str)!=str(row.removed_id)]
   self.assertEqual(len(sub),row.n); self.assertEqual(len(sub),298); self.assertEqual(sub.fta.sum(),row.FTA)
 def test_11_loo_frozen_exposure_and_formula(self):
  for row in self.loo.itertuples():
   sub=self.d[self.d.player_id.astype(str)!=str(row.removed_id)]
   self.assertEqual(';'.join(a.design(sub).columns),row.design_columns)
   pd.testing.assert_series_equal(sub[a.PRIMARY],self.d.loc[sub.index,a.PRIMARY])
 def test_12_all_loo_refits(self):
  for row in self.loo.itertuples():
   sub=self.d[self.d.player_id.astype(str)!=str(row.removed_id)]
   self.assertAlmostEqual(a.glm(sub).params[a.PRIMARY],row.beta,14)
 def test_13_failures_visible(self):
  self.assertIn('error',self.loo); self.assertEqual(int((~self.loo.converged).sum()),self.result['loo']['failed']); self.assertEqual(self.result['loo']['failed'],0)
 def test_14_singleton(self): self.assertEqual(self.result['exclude_unknown']['n'],298); self.assertEqual(self.result['exclude_unknown']['FTA'],42520)
 def test_15_high_leverage_exact(self):
  r=self.result['high_leverage']; self.assertEqual(r['n'],257); self.assertEqual(r['removed_players'],42)
  ids=set(map(str,r['removed_ids'])); self.assertEqual(self.d[~self.d.player_id.astype(str).isin(ids)].fta.sum(),r['FTA'])
 def test_16_position_map(self):
  mapping=a.PLAN['group_map']; self.assertEqual(set(mapping),set(self.d.position)); self.assertEqual(set(mapping.values()),{'Guard','Wing','Big','Unknown'})
  shuffled=self.d.assign(ftm=0); pd.testing.assert_frame_equal(a.design(self.d,group=True),a.design(shuffled,group=True))
 def test_17_thresholds_secondary(self):
  df=pd.read_csv(a.E/'fta_threshold_robustness.csv'); self.assertEqual(set(df.threshold),{50,100}); self.assertEqual(set(df.analysis),{'secondary'}); self.assertEqual(set(df.n),{203,145})
 def test_18_alternate_secondary(self):
  df=pd.read_csv(a.E/'alternate_exposure_robustness.csv'); self.assertEqual(set(df.exposure),{'wingspan_advantage','wingspan_ratio'}); self.assertEqual(set(df.analysis),{'secondary'}); self.assertEqual(self.result['primary_exposure'],'residual_wingspan')
 def test_19_probability_contrast(self):
  r=self.result['probability_contrasts']; self.assertEqual(r['quasi']['difference'],self.frozen['marginal_contrast']['difference']); self.assertAlmostEqual(r['quasi']['se']/r['Stage1_binomial']['se'],np.sqrt(self.m.pearson_chi2/self.m.df_resid),12)
 def test_20_no_geometric_refit(self):
  source=(ROOT/'scripts/stage2_analysis.py').read_text(); self.assertNotIn('geometry(',source); self.assertNotIn('sm.OLS',source)
 def test_21_code_and_plan_hash(self):
  self.assertEqual(a.sha(a.E/'analysis_plan.json'),self.result['plan_hash'])
  for name,h in self.result['code_hashes'].items(): self.assertEqual(a.sha(ROOT/'scripts'/name),h)
 def test_22_correction_contained(self):
  old=json.loads((a.E/'implementation_error_first_freeze.json').read_text())
  for k in self.result:
   if k not in ['high_leverage','code_hashes']: self.assertEqual(old[k],self.result[k])
 def test_23_report_freeze_order(self):
  report=ROOT/'docs/stage2_robust_inference.md'; self.assertLess((a.E/'primary_robustness_result.json').stat().st_mtime,report.stat().st_mtime); self.assertIn(a.STATEMENT,report.read_text())
if __name__=='__main__': unittest.main(verbosity=2)
