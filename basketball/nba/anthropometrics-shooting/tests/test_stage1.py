import unittest, sys, json, inspect
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import stage1_analysis as a

class Stage1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.ref=a.inputs(); cls.d,cls.g=a.prepare(cls.raw,cls.ref)
        cls.pos=cls.d[cls.d.fta>0]; cls.models=[a.fit(cls.pos,i) for i in range(3)]
        cls.frozen=json.loads((a.E/'primary_result.json').read_text())
    def test_A_candidate_hash(self): self.assertEqual(a.sha(a.CAND),a.HASHES[0])
    def test_B_reference_hash(self): self.assertEqual(a.sha(a.REF),a.HASHES[1])
    def test_C_reference_only(self):
        self.assertEqual(self.g.nobs,960)
        np.testing.assert_allclose(self.g.model.endog,self.ref.wingspan_inches)
        np.testing.assert_allclose(self.g.model.exog[:,1],self.ref[a.H])
    def test_D_outcome_exclusion(self):
        augmented=self.ref.assign(ftm=999,fta=1000,position='SG',nba_survival=1)
        np.testing.assert_array_equal(a.geometry(augmented).params,self.g.params)
        self.assertEqual(self.g.model.exog_names,['const',a.H])
    def test_E_year(self): self.assertTrue((self.ref.combine_year<=2013).all())
    def test_F_primary(self): self.assertEqual(self.frozen['primary_exposure'],'residual_wingspan')
    def test_G_counts(self): self.assertTrue((self.d.ftm<=self.d.fta).all())
    def test_H_zero_accounting(self):
        self.assertEqual(len(self.d),311); self.assertEqual(len(self.pos),299); self.assertEqual((self.d.fta==0).sum(),12)
    def test_I_no_threshold(self):
        self.assertEqual(self.pos.fta.sum(),42587)
        self.assertEqual(self.models[0].nobs,len(self.d[self.d.fta>0]))
        self.assertTrue((self.pos.fta<50).any())
    def test_J_M0(self): self.assertEqual(self.models[0].model.exog_names,['const',a.PRIMARY])
    def test_K_M1(self): self.assertEqual(self.models[1].model.exog_names,['const',a.PRIMARY,a.H])
    def test_L_M2(self): self.assertEqual(self.models[2].model.exog_names,['const',a.PRIMARY,a.H]+['position_'+c for c in sorted(self.pos.position.unique())[1:]])
    def test_M_original_positions(self): pd.testing.assert_series_equal(self.d.position,self.raw.combine_position.replace('',np.nan).fillna('unknown'),check_names=False)
    def test_N_no_outcome_grouping(self):
        shuffled=self.pos.assign(ftm=self.pos.ftm.iloc[::-1].to_numpy(),fta=10000)
        pd.testing.assert_frame_equal(a.design(self.pos,2),a.design(shuffled,2))
    def test_O_secondary_is_secondary(self):
        alt=pd.read_csv(a.E/'alternate_exposure_sensitivity.csv'); self.assertEqual(set(alt.analysis),{'secondary'})
        self.assertEqual(set(alt.exposure),{'wingspan_advantage','wingspan_ratio'})
        self.assertTrue(all(v['exposure']==a.PRIMARY for v in self.frozen['models'].values()))
    def test_P_thresholds(self):
        t=pd.read_csv(a.E/'fta_threshold_sensitivity.csv'); self.assertEqual(t.threshold.tolist(),[50,100]); self.assertEqual(t.n.tolist(),[203,145]); self.assertEqual(set(t.analysis),{'secondary'})
    def test_Q_language(self):
        self.assertIn('does not identify a causal effect',a.STATEMENT)
        report=(ROOT/'docs/stage1_ft_residual_wingspan_analysis.md').read_text()
        self.assertIn(a.STATEMENT,report)
        for phrase in ['long arms hurt shooting','mechanical disadvantage proven','long wingspan causes poor touch']: self.assertNotIn(phrase,report.lower())
    def test_R_deterministic(self):
        for i,m in enumerate(self.models): self.assertEqual(a.effect(m),self.frozen['models'][f'M{i}'])
        q=[self.frozen['marginal_contrast'][k] for k in ['q25','q75']]
        p,_,_=a.marginal(self.models[2],self.pos,q)
        self.assertEqual(float(p[1]-p[0]),self.frozen['marginal_contrast']['difference'])
    def test_S_binomial_denominator(self):
        for m in self.models: np.testing.assert_array_equal(m.model.n_trials,self.pos.fta)
        self.assertTrue(all('fta' not in m.model.exog_names for m in self.models))
    def test_T_frozen_code(self): self.assertEqual(a.sha(a.__file__),self.frozen['code_hash'])
    def test_U_geometry_application(self): np.testing.assert_allclose(self.d[a.PRIMARY],self.d.wingspan_inches-self.g.params['const']-self.g.params[a.H]*self.d[a.H],atol=1e-13)
    def test_V_analysis_hash(self): self.assertEqual(a.sha(ROOT/'data/processed/stage1_ft_2013_14_analysis.parquet'),self.frozen['analysis_dataset_hash'])
if __name__=='__main__': unittest.main(verbosity=2)
