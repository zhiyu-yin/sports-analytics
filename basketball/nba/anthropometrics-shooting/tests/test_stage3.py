import unittest,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from stage3_sources import E,sha
from stage3_panel import select_vectors
class Stage3PartA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=pd.read_parquet(ROOT/'data/processed/stage3_multiseason_ft_panel.parquet'); cls.r=pd.read_parquet(ROOT/'data/processed/stage3_primary_replication_panel.parquet'); cls.f=json.loads((E/'panel_freeze.json').read_text()); cls.g=json.loads((ROOT/'docs/stage1_evidence/residualization_model.json').read_text())
 def test_01_prior_all_hashes(self):
  prior=json.loads((E/'prior_preservation_manifest.json').read_text())
  for p,h in prior.items(): self.assertEqual(sha(ROOT/p),h,p)
 def test_02_versioned_corrections(self):
  c=pd.read_csv(E/'measurement_corrections.csv'); self.assertEqual(len(c),4); self.assertEqual(set(c.resolution),{'official_value_applied'}); self.assertTrue(c.source.str.startswith('https://www.nba.com/').all()); self.assertEqual(sha(E/'measurement_corrections.csv'),sha(ROOT/'data/interim/stage3_measurement_corrections.csv'))
 def test_03_no_future_measurements(self): self.assertTrue((self.p.combine_year<=self.p.first_observed_season.str[:4].astype(int)).all()); self.assertTrue((self.p.combine_year<=self.p.season.str[:4].astype(int)).all())
 def test_04_fixed_vectors(self):
  for f in ['combine_year','combine_position','height_wo_shoes_inches','wingspan_inches','residual_wingspan']: self.assertTrue((self.p.groupby('player_id')[f].nunique()==1).all())
 def test_05_frozen_transform(self): np.testing.assert_array_equal(self.p.residual_wingspan,self.p.wingspan_inches-(self.g['intercept']+self.g['slope']*self.p.height_wo_shoes_inches))
 def test_06_replication_excludes_development(self): self.assertNotIn('2013-14',set(self.r.season)); pd.testing.assert_frame_equal(self.r,self.p[self.p.season!='2013-14'].reset_index(drop=True))
 def test_07_full_includes_development_only_secondary(self): self.assertEqual((self.p.season=='2013-14').sum(),311)
 def test_08_exact_id_only(self): self.assertEqual(set(self.p.join_status),{'exact ID'}); self.assertTrue((self.p.player_id.astype(int)>0).all())
 def test_09_counts(self):
  for p in [self.p,self.r]: self.assertTrue((p.ftm<=p.fta).all()); self.assertTrue((p.ftm>=0).all()); self.assertTrue((p.fta%1==0).all()); self.assertFalse(p.duplicated(['player_id','season']).any())
 def test_10_zero_accounting(self): self.assertEqual((self.r.fta==0).sum(),137); self.assertTrue(self.r.loc[self.r.fta==0,'descriptive_ft_pct'].isna().all()); np.testing.assert_array_equal(self.r.likelihood_eligible,self.r.fta>0)
 def test_11_no_threshold(self): self.assertTrue(self.r.fta.between(1,49).any()); self.assertEqual(len(self.r),4117)
 def test_12_original_positions(self):
  vectors=pd.read_csv(ROOT/'data/interim/stage3_frozen_player_vectors.csv',dtype={'player_id':str},keep_default_na=False).set_index('player_id'); self.assertTrue((self.p.combine_position==self.p.player_id.map(vectors.combine_position.replace('','unknown'))).all())
 def test_13_outcome_free_selection(self):
  measurements=pd.DataFrame({'player_id':['1','1','1'],'combine_year':[2010,2012,2015],'height_wo_shoes_inches':[70,71,72],'wingspan_inches':[75,76,77]}); selected,_=select_vectors(measurements,{'1':'2013-14'}); self.assertEqual(selected.iloc[0].combine_year,2012)
 def test_14_gate_enforced(self):
  self.assertFalse(self.f['part_B_authorized']); self.assertFalse(self.f['part_A_pass']); self.assertFalse(self.f['model_executed']); self.assertFalse((E/'primary_replication_result.json').exists())
 def test_15_source_counts_all_match(self):
  d=pd.read_csv(E/'shooting_census_crosscheck.csv'); self.assertTrue(d[d.field!='minutes'].match.all()); self.assertTrue(pd.read_csv(E/'shooting_team_reconciliation.csv').match.all())
 def test_16_minutes_not_silently_accepted(self):
  d=pd.read_csv(E/'shooting_player_crosscheck.csv'); self.assertEqual((~d.match).sum(),4); self.assertEqual(set(d.loc[~d.match,'field']),{'minutes'}); self.assertEqual(json.loads((E/'multi_season_source_validation.json').read_text())['part_A_source_gate'],'BLOCKED')
 def test_17_hashes(self):
  for k,p in self.f['candidate_paths'].items(): self.assertEqual(sha(ROOT/p),self.f['candidate_hashes'][k])
 def test_18_zero_minute_counts(self):
  d=pd.read_parquet(ROOT/'data/interim/stage3_all_player_seasons.parquet'); x=d[(d.player_id=='1626176')&(d.season=='2016-17')].iloc[0]; self.assertEqual((x.ftm,x.fta,x.games_played),(21,29,29))
 def test_19_all_later_cohorts(self):
  valid=pd.read_csv(E/'later_combine_validation_by_year.csv'); self.assertEqual(valid.year.tolist(),list(range(2014,2023))); self.assertEqual(valid.unmatched_names.sum(),0)
 def test_20_protocol_predates_official_capture(self):
  protocol=E/'source_validation_protocol.json'; self.assertLess(protocol.stat().st_mtime,(ROOT/'data/raw/stage3/players_2010-11.json').stat().st_mtime)
if __name__=='__main__': unittest.main(verbosity=2)
