import csv,hashlib,json,sys,unittest
from pathlib import Path
from datetime import timedelta
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from phase1c.logic import (decision,ordering,add_elapsed,eligibility,confirmed_run_bounds,
    public_outcomes,row_outcome,features,in_window)
from injury_warning.rules import utc

T='2024-01-03T12:00:00-05:00'


class Phase1CRules(unittest.TestCase):
    def test_noon_after_bounded_end_no_exact_seconds_needed(self):
        self.assertTrue(ordering('2024-01-02T21:28:00-06:00',T))
        self.assertFalse(ordering(T,T))
        self.assertFalse(ordering(None,T))
        self.assertEqual(decision('2024-01-02'),T)

    def test_elapsed_horizon_and_local_day_lag_across_dst(self):
        t=decision('2024-03-09')
        self.assertEqual((utc(add_elapsed(t,days=14))-utc(t)).total_seconds(),14*86400)
        self.assertEqual(decision('2024-03-09',1),'2024-03-11T12:00:00-04:00')

    def test_in_game_exclusion_and_no_future_at_boundary(self):
        state,_=eligibility(appeared=True,member=True,time_ordered=True,covered=True,explicit_disqualifiers=['new_injury_in_index_game'])
        self.assertEqual(state,'excluded')
        self.assertFalse(in_window(T,'2024-01-02T00:00:00-05:00','2024-01-02T23:59:59-05:00'))
        self.assertFalse(in_window(T,T,T))

    def test_retrospective_prevalence_never_changes_prospective_membership(self):
        state,_=eligibility(appeared=True,member=True,time_ordered=True,covered=True,explicit_disqualifiers=[])
        e=dict(episode_id='old',onset_lower='2024-01-01T00:00:00Z',onset_upper='2024-01-02T00:00:00Z',primary='positive')
        label,_,prev=row_outcome(T,[e],'primary',surveillance=True,followup=True)
        self.assertEqual(state,'included');self.assertEqual(label,'negative');self.assertEqual(prev,['old'])

    def test_uncertain_onset_straddles_window(self):
        e=dict(episode_id='interval',onset_lower='2024-01-03T00:00:00-05:00',onset_upper='2024-01-04T00:00:00-05:00',primary='positive')
        self.assertEqual(row_outcome(T,[e],'primary',surveillance=True,followup=True)[0],'unknown')

    def test_ten_game_run_and_interruptions(self):
        good=dict(category='injury',appeared=False,same_episode_supported=True)
        non=dict(category='rest',appeared=False,same_episode_supported=False)
        self.assertEqual(confirmed_run_bounds([good]*10,True),(10,10))
        self.assertEqual(confirmed_run_bounds([good]*4+[non]+[good]*6,True),(6,11))
        self.assertEqual(confirmed_run_bounds([dict(good,same_episode_supported=False)]*10,True),(0,10))
        with self.assertRaises(ValueError):confirmed_run_bounds([dict(good,appeared=True)],True)

    def test_proxy_strict_boundaries_and_censored_documented_lower_bound(self):
        args=dict(run_lower=0,run_upper=3,span_lower=28,span_upper=28,continuity_supported=True)
        self.assertEqual(public_outcomes(**args),('negative','negative'))
        self.assertEqual(public_outcomes(**dict(args,run_lower=10,run_upper=10)),('positive','negative'))
        self.assertEqual(public_outcomes(**dict(args,span_lower=29,span_upper=None))[1],'positive')
        self.assertEqual(public_outcomes(**dict(args,run_upper=None,span_lower=None,span_upper=None)),('unknown','unknown'))
        self.assertEqual(public_outcomes(**dict(args,run_lower=10,run_upper=None,continuity_supported=False))[0],'unknown')

    def test_unknown_coverage_and_trade_followup(self):
        self.assertEqual(row_outcome(T,[],'primary',surveillance=False,followup=True)[0],'unknown')
        self.assertEqual(row_outcome(T,[],'primary',surveillance=True,followup=True,transferred=True)[0],'unknown')
        self.assertEqual(row_outcome(T,[],'primary',surveillance=True,followup=True)[0],'negative')

    def test_lag_rebuilds_windows_and_inputs(self):
        logs=[dict(game_id='index',minutes=20,end_upper='2024-01-02T22:00:00-05:00',assumed_available_at='2024-01-03T04:00:00-05:00'),
              dict(game_id='next',minutes=30,end_upper='2024-01-03T22:00:00-05:00',assumed_available_at='2024-01-04T04:00:00-05:00')]
        a=features(logs,decision('2024-01-02'),history_complete=True,baseline_complete=True)
        b=features(logs,decision('2024-01-02',1),history_complete=True,baseline_complete=True)
        self.assertEqual(a['minutes_7d'],20);self.assertEqual(b['minutes_7d'],50)
        self.assertNotEqual(add_elapsed(decision('2024-01-02'),days=14),add_elapsed(decision('2024-01-02',1),days=14))
        self.assertIsNone(features(logs,T,history_complete=False,baseline_complete=False)['minutes_28d'])
        self.assertIsNone(a['past_mean_minutes_per_appearance'])
        self.assertEqual(b['past_mean_minutes_per_appearance'],20)


class Phase1CIntegrity(unittest.TestCase):
    def rows(self,name):
        with (ROOT/'phase1c/tables'/name).open() as f:return list(csv.DictReader(f))

    def test_historical_versions_unchanged(self):
        old=json.loads((ROOT/'phase1c/registration/historical_version_hashes.json').read_text())
        for path,digest in old.items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
        p=ROOT/'phase1c/registration/amendment_v1.json'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),p.with_suffix('.sha256').read_text().strip())

    def test_every_included_row_has_a_label_and_assumed_feature(self):
        cohort=self.rows('cohort_all_candidates.csv');included={r['row_id'] for r in cohort if r['B_state']=='included'}
        self.assertEqual(included,{r['row_id'] for r in self.rows('row_outcomes.csv')})
        self.assertEqual(included,{r['row_id'] for r in self.rows('features_assumption_B.csv')})
        self.assertFalse(self.rows('features_verified_A.csv'))
        for r in cohort:
            if r['B_state']=='included':
                self.assertEqual(r['appeared'],'True');self.assertEqual(r['game_end_ordering'],'True')
                self.assertEqual(r['B_baseline_report_checked'],'True');self.assertEqual(r['B_decision_day_report_checked'],'True')
                self.assertLessEqual(utc(r['stats_assumed_available_at']),utc(r['decision_at']))
        for r in self.rows('features_assumption_B.csv'):
            self.assertLessEqual(utc(r['max_input_assumed_available_at']),utc(r['decision_at']))
            self.assertEqual(r['retrospective_diagnoses_used'],'False')
        for r in self.rows('row_outcomes.csv'):self.assertFalse(r['historical_label_known_at'])

    def test_daily_search_calendar_includes_leap_day_and_final_boundary(self):
        from datetime import date,timedelta
        records=json.loads((ROOT/'phase1c/search_ledger.json').read_text())
        got={r['date'] for r in records}
        wanted=set();d=date(2024,1,1)
        while d<=date(2024,3,1):wanted.add(d.isoformat());d+=timedelta(days=1)
        self.assertEqual(got,wanted)
        self.assertIn('2024-02-29',got);self.assertIn('2024-03-01',got)

    def test_original_leads_mapped_once_without_new_injury_count_claim(self):
        mapping=self.rows('original_lead_mapping.csv')
        self.assertEqual(len(mapping),28);self.assertEqual(len({r['original_lead_id'] for r in mapping}),28)
        eps={r['episode_id']:r for r in self.rows('episode_candidates.csv')}
        self.assertTrue(all(r['episode_candidate_id'] in eps for r in mapping))
        self.assertTrue(any(r['clinical_episode_identity'].startswith('unresolved') for r in eps.values()))
        for e in eps.values():
            if e['left_censored_start']=='True':
                self.assertFalse(e['first_injury_missed_game'])
                self.assertEqual(e['primary_ge10'],'unknown')
