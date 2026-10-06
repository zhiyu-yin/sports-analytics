"""Release guardrails; no association or exposure/outcome panel is loaded."""
import unittest,sys,json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3b_release import E,OLD,A,read,sha,evaluate_conditions,REQUIRED,LIMITATION,stage3_inventory
class Stage3BRelease(unittest.TestCase):
 def test_A_historical_failure_unchanged(self):
  for p,h in read(E/'historical_preservation_manifest.json').items():self.assertEqual(sha(ROOT/p),h,p)
  self.assertEqual(read(OLD/'multi_season_source_validation.json')['part_A_source_gate'],'BLOCKED');self.assertFalse(read(OLD/'execution_status.json')['part_A_pass'])
 def test_B_stage3a_unresolved_unchanged(self):
  self.assertEqual(read(A/'stage3a_decision.json')['stage3a_classification'],'UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE');self.assertFalse(read(A/'stage3a_decision.json')['amendment_applied'])
 def test_C_no_numeric_MIN_tolerance(self):
  p=read(E/'amended_source_validation_protocol.json');self.assertIsNone(p['season_decimal_MIN']['numeric_tolerance']);self.assertFalse(p['season_decimal_MIN']['numerical_equality_release_gate']);self.assertFalse(p['season_decimal_MIN']['mechanism_required'])
  def values(o):
   if isinstance(o,dict):
    for v in o.values():yield from values(v)
   elif isinstance(o,list):
    for v in o:yield from values(v)
   else:yield o
  self.assertFalse(any(type(v) in (float,int) for v in values(p)))
 def test_D_exact_count_gate_mandatory(self):
  p=read(E/'amended_source_validation_protocol.json')['primary_counts'];self.assertTrue(p['mandatory']);self.assertEqual(p['comparison'],'exact');self.assertEqual(set(p['fields']),{'FTM','FTA','3PM','3PA','GP'});self.assertEqual(p['unexplained_FTM_FTA_disagreement'],'blocks release')
  c=pd.read_csv(OLD/'shooting_census_crosscheck.csv');c=c[c.field.isin(['ftm','fta','fg3m','fg3a','games_played'])];self.assertEqual(len(c),7550);self.assertTrue((c.archive==c.official).all())
 def test_E_zero_DNP_distinction(self):
  g=pd.read_csv(A/'official_game_minute_crosscheck.csv',keep_default_na=False);d=g[g.match_status=='archive_DNP_not_in_official_appearance_log'];self.assertEqual(len(d),698);self.assertTrue((d.official_appearance_status=='missing').all());self.assertTrue((d.archive_appearance_status=='empty / DNP').all())
  z=pd.read_csv(A/'zero_minute_appearance_audit.csv');self.assertEqual(len(z),15);self.assertTrue((z.official_MIN_raw=='0:00').all());self.assertTrue((z.archive_MIN_raw=='0:00').all())
 def test_F_eligibility_mandatory(self):
  p=read(E/'amended_source_validation_protocol.json')['eligibility'];self.assertTrue(p['mandatory']);self.assertEqual(p['eligibility_change'],'blocks release')
  d=pd.read_csv(A/'season_eligibility_crosscheck.csv');self.assertEqual(len(d),1510);self.assertTrue(((d.archive_sum_seconds>0)==(d.official_display_seconds>0)).all())
 def test_G_candidate_hashes(self):
  prior=read(OLD/'panel_freeze.json');receipt=read(E/'panel_release_receipt.json');self.assertFalse(receipt['rebuild_performed'])
  for k,p in receipt['panels'].items():self.assertEqual(sha(ROOT/p['path']),prior['candidate_hashes'][k]);self.assertEqual(p['sha256'],prior['candidate_hashes'][k])
 def test_H_primary_exclusion_and_accounting(self):
  for k,expected in [('replication',(13,4117,857,469099)),('full',(14,4428,866,511686))]:
   p=read(E/'panel_release_receipt.json')['panels'][k];d=pd.read_parquet(ROOT/p['path'],columns=['season','player_id','fta']);self.assertEqual((d.season.nunique(),len(d),d.player_id.nunique(),d.fta.sum()),expected);self.assertEqual('2013-14' in set(d.season),k=='full')
 def test_I_authorization_requires_every_condition(self):
  good={k:True for k in REQUIRED};self.assertEqual(evaluate_conditions(good),'PASS UNDER AMENDED PROTOCOL')
  for k in REQUIRED:
   with self.subTest(gate=k):
    self.assertEqual(evaluate_conditions(good|{k:False}),'FAIL UNDER AMENDED PROTOCOL');self.assertEqual(evaluate_conditions({x:v for x,v in good.items() if x!=k}),'FAIL UNDER AMENDED PROTOCOL')
  gate=read(E/'amended_gate_decision.json');auth=read(E/'part_b_authorization.json');self.assertEqual(auth['part_b_authorized'],evaluate_conditions(gate['conditions'])=='PASS UNDER AMENDED PROTOCOL');self.assertEqual(auth['gate_sha256'],sha(E/'amended_gate_decision.json'));self.assertFalse(auth['part_b_started'])
 def test_J_no_Stage3_model_before_authorization(self):
  pre=read(E/'preauthorization_inventory.json');self.assertFalse(pre['unexpected_model_artifacts']);self.assertFalse(pre['historical_execution_status']['part_B_started']);self.assertFalse(pre['historical_panel_model_executed']);self.assertFalse(pre['stage3a_scientific_models_run']);self.assertFalse(stage3_inventory()['unexpected_model_artifacts'])
  timeline=read(E/'amendment_timeline.json');gate=read(E/'amended_gate_decision.json');auth=read(E/'part_b_authorization.json');self.assertLess(pre['checked_at'],timeline['stage3b_amendment']['frozen_at']);self.assertLess(timeline['stage3b_amendment']['frozen_at'],gate['evaluated_at']);self.assertLessEqual(gate['evaluated_at'],auth['authorized_at']);self.assertTrue(auth['no_association_before_authorization'])
 def test_K_frozen_protocol_and_limitation(self):
  self.assertEqual(sha(E/'amended_source_validation_protocol.json'),read(E/'amendment_timeline.json')['stage3b_amendment']['protocol_sha256']);self.assertEqual(read(E/'part_b_authorization.json')['mandatory_limitation'],LIMITATION);self.assertEqual(read(E/'amended_source_validation_protocol.json')['limitation_required_in_all_future_stage3_reports'],LIMITATION)
 def test_L_raw_evidence_and_quarantine(self):
  e=read(E/'evidence_reassessment.json');self.assertTrue(all(x['match'] for x in e['source_manifest_checks']));self.assertTrue(e['facts']['raw_game_strings_dates_sets_exact']);self.assertEqual(e['facts']['audited_appearances'],2861);self.assertEqual(e['facts']['quarantined_pairs'],39);self.assertEqual(e['facts']['quarantined_selected'],0);self.assertTrue(all(e['conditions'].values()))
if __name__=='__main__':unittest.main()
