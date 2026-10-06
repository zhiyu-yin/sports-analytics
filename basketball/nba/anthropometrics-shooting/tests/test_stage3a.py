"""Factual provenance tests only; deliberately do not load an exposure/outcome panel."""
import unittest,json,sys,hashlib
from pathlib import Path
from decimal import Decimal
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from stage3a_audit import seconds,status,official_seasons,load_games,ORIGINAL
from stage3a_prepare import E,sha
class Stage3AMinutes(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.games=pd.read_csv(E/'official_game_minute_crosscheck.csv',dtype={'player_id':str,'game_id':str},keep_default_na=False)
  cls.rec=pd.read_csv(E/'minute_reconstruction_by_player_season.csv',dtype={'player_id':str})
  cls.sample=pd.read_csv(E/'minute_audit_sample_predeclared.csv',dtype={'player_id':str})
  cls.summary=json.loads((E/'game_level_reconciliation_summary.json').read_text())
 def test_01_exact_MM_SS(self):
  for raw,expected in [('12:04',724),('12:28',748),('0:00',0),('0:59',59),('41:15',2475)]:self.assertEqual(seconds(raw),Decimal(expected))
 def test_02_decimal_minutes(self):
  for raw,expected in [('12.4',744),('2758.4',165504),('0.01',Decimal('.6'))]:self.assertEqual(seconds(raw),Decimal(expected))
 def test_03_no_MM_dot_SS(self):
  self.assertNotEqual(seconds('12:04'),seconds('12.04'));self.assertNotEqual(seconds('12:28'),seconds('12.28'))
 def test_04_noncanonical_carry(self):
  self.assertEqual(seconds('23:60'),1440);self.assertEqual(seconds('0:60'),60)
  rows=self.games[self.games.official_game_MIN_raw.str.endswith(':60')];self.assertEqual(len(rows),8);self.assertTrue((rows.official_game_MIN_raw==rows.archive_game_MIN_raw).all())
 def test_05_parser_100_rows(self):
  d=pd.read_csv(E/'minute_parser_sample.csv',dtype=str);self.assertEqual(len(d),100)
  for r in d.itertuples():self.assertEqual(seconds(r.raw),Decimal(r.expected_seconds));self.assertEqual(Decimal(r.parsed_seconds),Decimal(r.stage3_parser_seconds));self.assertEqual(Decimal(r.roundtrip_seconds),Decimal(r.expected_seconds))
 def test_06_one_to_one(self):
  self.assertFalse(self.games.duplicated(['season','player_id','game_id']).any());self.assertEqual(len(self.rec),53)
  for p in (ROOT/'data/raw/stage3a').glob('games_*.json'):
   s,pid=p.stem.split('_')[1:];_,o=load_games(p,s,pid);self.assertEqual(len(o),len(set(o)))
 def test_07_regular_season_and_dates(self):
  self.assertTrue(self.games.game_id.str.startswith('002').all());self.assertEqual(set(self.games.season),{'2010-11','2016-17','2023-24'})
  self.assertTrue((self.games.loc[self.games.match_status=='matched_recorded_appearance','date_match']=='True').all())
 def test_08_no_silent_omission(self):
  self.assertTrue(self.rec.all_recorded_games_match.all());self.assertEqual(self.rec.official_missing_recorded_games.sum(),0);self.assertEqual(self.rec.archive_missing_recorded_games.sum(),0)
  self.assertTrue((self.rec.E_official_season_GP==self.rec.F_reconstructed_official_GP).all());self.assertTrue((self.rec.E_official_season_GP==self.rec.archive_recorded_GP).all());self.assertEqual(len(self.games),3559)
  self.assertEqual(self.rec.archive_DNP_rows.sum(),698);self.assertEqual(sum(self.games.match_status=='archive_DNP_not_in_official_appearance_log'),698)
 def test_09_game_seconds_exact(self):
  matched=self.games[self.games.match_status=='matched_recorded_appearance'];self.assertEqual(len(matched),2861);self.assertTrue((matched.official_game_MIN_raw==matched.archive_game_MIN_raw).all())
  self.assertTrue((matched.game_level_difference_seconds.astype(float)==0).all());self.assertTrue((self.rec.B_archive_sum_seconds==self.rec.D_official_game_sum_seconds).all())
 def test_10_zero_appearance_retained(self):
  z=pd.read_csv(E/'zero_minute_appearance_audit.csv',dtype={'game_id':str,'player_id':str});self.assertEqual(len(z),15);self.assertTrue((z.status=='official_recorded_zero_confirmed').all());self.assertTrue((z.official_GP==z.archive_recorded_GP).all())
  r=z[(z.player_id=='1626176')&(z.game_id=='0021601203')].iloc[0];self.assertEqual((r.official_MIN_raw,r.official_FTM,r.official_FTA,r.archive_positive_game_GP,r.archive_recorded_GP),('0:00',1,2,28,29))
 def test_11_DNP_not_zero_or_missing(self):
  self.assertIsNone(seconds(''));self.assertEqual(status(''),'empty / DNP');self.assertEqual(status('DNP - Coach\'s Decision'),'empty / DNP');self.assertEqual(status('0:00'),'recorded 0:00 appearance');self.assertEqual(status('',False),'missing')
  b=pd.read_csv(E/'official_boxscore_classification_crosscheck.csv');self.assertEqual(len(b),26);self.assertTrue(b.classification_match.all());self.assertEqual((b.official_status=='empty / DNP').sum(),5)
  d=self.games[self.games.match_status=='archive_DNP_not_in_official_appearance_log'];self.assertTrue((d.official_appearance_status=='missing').all());self.assertTrue((d.archive_appearance_status=='empty / DNP').all())
 def test_12_counts_unchanged_and_exact(self):
  census=pd.read_csv(ROOT/'docs/stage3_evidence/shooting_census_crosscheck.csv');ints=census[census.field.isin(['ftm','fta','fg3m','fg3a','games_played'])];self.assertEqual(len(ints),7550);self.assertTrue(ints.match.all());self.assertTrue((ints.archive==ints.official).all())
  counts=pd.read_csv(E/'official_game_count_sum_crosscheck.csv');self.assertEqual(len(counts),212);self.assertTrue(counts.match.all())
  a=pd.read_csv(E/'archive_minute_projection.csv',dtype=str,keep_default_na=False);src=json.loads((ROOT/'docs/stage0_evidence/shooting_archive_sources.json').read_text());cols=['season_year','gameId','personId','minutes','freeThrowsMade','freeThrowsAttempted']; raw=pd.concat([pd.read_csv(ROOT/r['raw_path'],usecols=cols,dtype=str,keep_default_na=False) for r in src]);raw=raw[raw.season_year.isin(['2010-11','2016-17','2023-24'])];raw.gameId=raw.gameId.str.zfill(10)
  pd.testing.assert_frame_equal(a[cols].reset_index(drop=True),raw[cols].reset_index(drop=True))
 def test_13_frozen_outcome_free_selection(self):
  freeze=json.loads((E/'sample_freeze.json').read_text());self.assertEqual(sha(E/'minute_audit_sample_predeclared.csv'),freeze['sha256']);self.assertFalse(freeze['prohibited_selection_variables_used']);self.assertEqual(set(freeze['selection_columns']),{'season','player_id','player_name','field','archive','official','match'})
  c=pd.read_csv(ROOT/'docs/stage3_evidence/shooting_census_crosscheck.csv',usecols=freeze['selection_columns'],dtype={'player_id':str});c=c[c.field=='minutes'].copy();c['minute_band']=c.groupby('season').archive.transform(lambda v:pd.qcut(v.rank(method='first'),3,labels=['low','medium','high']));c['key']=[hashlib.sha256(f'stage3a-minute-only-v1|{s}|{p}'.encode()).hexdigest() for s,p in zip(c.season,c.player_id)];pick=c.sort_values('key').groupby(['season','minute_band','match'],observed=True).head(2);expected=set(zip(pick.season,pick.player_id))|ORIGINAL
  self.assertEqual(set(zip(self.sample.season,self.sample.player_id)),expected);self.assertEqual(len(self.sample),39);self.assertGreaterEqual((self.sample.case_type=='within_original_tolerance').sum(),10);self.assertGreaterEqual((self.sample.case_type=='census_mismatch').sum()-4,10)
  self.assertEqual(set(self.sample.minute_band),{'low','medium','high'})
  for p in (ROOT/'data/raw/stage3a').glob('games_*.json'):self.assertGreater(json.loads(p.read_text())['retrieved_at'],freeze['frozen_at'])
 def test_14_no_max_derived_tolerance(self):
  d=json.loads((E/'stage3a_decision.json').read_text());q=json.loads((E/'minute_quantization_summary.json').read_text());self.assertIsNone(d['new_numeric_tolerance']);self.assertIsNone(q['new_acceptance_threshold']);self.assertFalse(d['amendment_applied']);self.assertFalse(d['amendment_recommended'])
 def test_15_Part_B_disabled(self):
  prior=json.loads((ROOT/'docs/stage3_evidence/execution_status.json').read_text());self.assertFalse(prior['part_B_started']);self.assertFalse(prior['part_A_pass']);d=json.loads((E/'stage3a_decision.json').read_text());self.assertEqual(d['stage3_part_B'],'DISABLED');self.assertFalse(d['scientific_models_run']);self.assertFalse(self.summary['scientific_association_inspected'])
 def test_16_all_prior_artifacts_unchanged(self):
  prior=json.loads((E/'prior_artifact_hashes.json').read_text());self.assertGreater(len(prior),400)
  for path,h in prior.items():self.assertEqual(sha(ROOT/path),h,path)
  failed=json.loads((ROOT/'docs/stage3_evidence/multi_season_source_validation.json').read_text());self.assertEqual(failed['part_A_source_gate'],'BLOCKED');self.assertEqual(len(failed['census_mismatches']),170)
 def test_17_quantization_not_symmetrized(self):
  d=pd.read_csv(E/'minute_difference_distribution.csv');self.assertEqual(dict(zip(d.difference_seconds,d.frequency)),{i:{-5:4,-4:9,4:88,5:43,6:14,7:8,8:4}.get(i,0) for i in range(-8,9)})
  q=json.loads((E/'minute_quantization_summary.json').read_text());self.assertFalse(q['symmetric']);self.assertTrue(q['all_on_integer_second_grid']);self.assertEqual(q['positive'],157)
 def test_18_eligibility_unchanged(self):
  e=pd.read_csv(E/'season_eligibility_crosscheck.csv');self.assertEqual(len(e),1510);self.assertFalse(e.eligibility_changed.any());self.assertTrue((e.archive_sum_seconds>0).all());self.assertTrue((e.official_display_seconds>0).all())
 def test_19_four_differences_and_separate_routes(self):
  d=self.rec[self.rec.original_failed_case];self.assertEqual(len(d),4);self.assertEqual(dict(zip(d.player_id,d.B_minus_C_seconds)),{'201942':4,'202083':4,'2772':6,'203552':4});self.assertTrue(d.A_archive_raw_season_MIN.isna().all());self.assertTrue((d.B_minus_D_seconds==0).all())
  h=pd.read_csv(E/'candidate_rounding_explanations.csv',dtype={'player_id':str});h=h[[ (s,p) in ORIGINAL for s,p in zip(h.season,h.player_id)]];self.assertFalse(h.one_decimal_season_round_compatible.any());self.assertTrue(h.unobserved_fractional_seconds_then_rounding_compatible.all());self.assertFalse(h.unobserved_fractional_seconds_mechanism_demonstrated.any())
if __name__=='__main__':unittest.main()
