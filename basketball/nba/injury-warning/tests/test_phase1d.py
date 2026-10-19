"""Definition-derived counterexamples and independently sourced integration checks."""
import unittest,sys,json,csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from phase1d.logic import label_events,absence_runs,applicable_schedule
from phase1d.build import verify
from phase1c.logic import eligibility,features
T='2024-01-03T12:00:00-05:00'
def event(**kw):
    return dict(dict(event_id='event',clinical_lower='2024-01-05T15:00:00-05:00',clinical_upper='2024-01-05T16:00:00-05:00',run_lower='2024-02-01T19:00:00-05:00',run_upper='2024-02-01T19:01:00-05:00',severity='positive',continuity_supported=True),**kw)
def game(i,appeared=False,category='injury',**kw):
    return dict(dict(player_id='p',game_id=str(i),game_date='2024-01-'+str(i).zfill(2),appeared=appeared,category=category,roster_observed=True,coverage='page_and_book',page_source='page_'+str(i),reason_source='book_'+str(i)),**kw)
class Definitions(unittest.TestCase):
    def test_unrelated_late_event_cannot_contaminate_early_window(self):
        e=event(clinical_lower='2024-04-10T12:00:00-04:00',clinical_upper='2024-04-10T13:00:00-04:00',severity='unknown')
        self.assertEqual(label_events(T,[e],'clinical')[0],'negative')
    def test_early_documented_injury_can_precede_play_and_late_absence(self):
        e=event();appearances=[game(7,True),game(12,True)]
        self.assertTrue(all(g['appeared'] for g in appearances))
        self.assertEqual(label_events(T,[e],'clinical')[0],'positive')
        self.assertEqual(label_events(T,[e],'run')[0],'negative')
        self.assertEqual(e['clinical_lower'],'2024-01-05T15:00:00-05:00')
    def test_return_ends_run_without_recovery_or_new_clinical_lower_bound(self):
        r=absence_runs([game(3,True),game(4),game(5),game(6,True),game(7),game(8,True)])
        self.assertEqual([e['possible_run_upper'] for e in r],[2,1])
        self.assertTrue(all(e['clinical_lower'] is None for e in r))
        self.assertEqual(r[0]['return_game_id'],'6')
    def test_unknown_clinical_lower_does_not_become_last_appearance(self):
        e=event(clinical_lower=None,clinical_upper='2024-04-12T20:00:00-04:00',severity='unknown')
        self.assertEqual(label_events(T,[e],'clinical')[0],'unknown')
        self.assertEqual(label_events(T,[e],'run')[0],'negative')
    def test_straddling_horizon_and_common_attribution_requirement(self):
        e=event(run_lower='2024-01-17T11:00:00-05:00',run_upper='2024-01-17T13:00:00-05:00')
        self.assertEqual(label_events(T,[e],'run')[0],'unknown')
        self.assertEqual(label_events(T,[event(continuity_supported=False)],'clinical')[0],'unknown')
    def test_mixed_unknown_and_censored_runs_not_positive(self):
        r=absence_runs([game(3,True)]+[game(i,category='unknown' if i==4 else 'injury') for i in range(4,15)]+[game(15,True)])
        self.assertEqual(r[0]['severity'],'unknown');self.assertEqual(r[0]['anchor_attribution'],'unknown')
        self.assertEqual(absence_runs([game(4)])[0]['severity'],'unknown')
        left=absence_runs([game(1),game(2,True)])[0]
        self.assertIsNone(left['run_lower']);self.assertIsNone(left['possible_run_upper'])
        self.assertEqual(label_events(T,[left],'run')[0],'negative')
    def test_transfer_actual_schedule_and_incomplete_roster_followup(self):
        s=applicable_schedule([game(4),game(8)],[game(7,True),game(9)],'2024-01-07')
        self.assertEqual([r['game_id'] for r in s],['4','7','9'])
        r=absence_runs([game(4,roster_observed=False),game(5,True)])
        self.assertEqual(r[0]['severity'],'unknown')
        self.assertEqual(label_events(T,[],'run',followup=False)[0],'unknown')
    def test_outcome_evidence_does_not_change_eligibility_or_features(self):
        args=dict(appeared=True,member=True,time_ordered=True,covered=True,explicit_disqualifiers=[])
        before=eligibility(**args);f=features([],T,history_complete=False,baseline_complete=False)
        label_events(T,[event()],'clinical')
        self.assertEqual(eligibility(**args),before);self.assertEqual(features([],T,history_complete=False,baseline_complete=False),f)
class Evidence(unittest.TestCase):
    def rows(self,name,folder='phase1d'):
        with (ROOT/folder/'tables'/name).open() as f:return list(csv.DictReader(f))
    def test_preserved_outputs_and_registration(self):verify()
    def test_all_118_rows_audited_without_inventing_clinical_bounds(self):
        r=[r for r in self.rows('unknown_row_linkage_audit.csv') if r['extra_lag_days']=='0']
        self.assertEqual(len(r),118);self.assertEqual(len({r['row_id'] for r in r}),118)
        self.assertTrue(all(r['clinical_final']=='unknown' and not r['clinical_onset_lower'] and r['intervening_appearance_ids'] for r in r))
    def test_real_cases_actual_eligible_positive_and_endpoint_disagreement(self):
        r=self.rows('fixture_rows.csv')
        for case,index in [('A02','2024-01-25'),('A03','2023-11-22')]:
            a=[x for x in r if x['case_id']==case and x['index_game_date']==index]
            self.assertEqual(len(a),2)
            for x in a:
                self.assertEqual(x['eligibility_B'],'included');self.assertEqual(x['clinical_cohort_label'],'positive');self.assertEqual(x['run_cohort_label'],'positive')
                self.assertTrue(x['baseline_report_ids'] and x['decision_report_ids'] and x['dated_search_executed']=='True' and float(x['index_minutes'])>0)
        a=next(x for x in r if x['case_id']=='A03' and x['index_game_date']=='2023-11-12' and x['extra_lag_days']=='0')
        self.assertEqual((a['clinical_cohort_label'],a['run_cohort_label']),('positive','negative'))
        self.assertTrue(all(x['eligibility_B']=='excluded' for x in r if (x['case_id'],x['index_game_date']) in [('A02','2024-01-27'),('A03','2023-11-26')]))
        self.assertTrue(all(x['eligibility_B']=='unknown' for x in r if x['index_game_date']=='2023-11-18'))
    def test_positive_severity_reconciles_individual_game_evidence(self):
        events=self.rows('fixture_events.csv');evidence=self.rows('fixture_severity_evidence.csv')
        for e in events:
            ev=[v for v in evidence if v['case_id']==e['event_id'][:3]]
            self.assertGreaterEqual(len(ev),10);self.assertEqual(len(ev),int(e['confirmed_same_episode_games']))
            self.assertTrue(all('injury/illness' in v['value'].lower() for v in ev))
            self.assertTrue(e['continuity_source'] and e['onset_source'])
    def test_prospective_membership_features_fixtures_and_label_times_separated(self):
        old=self.rows('row_outcomes.csv','phase1c');new=self.rows('row_outcomes.csv')
        self.assertEqual({r['row_id'] for r in old},{r['row_id'] for r in new})
        self.assertTrue(all(not r['historical_label_known_at'] and r['prospective_inputs_unchanged']=='True' for r in new))
        self.assertTrue(all(r['fixture_in_Boston_counts']=='False' and r['outcome_evidence_in_eligibility']=='False' for r in self.rows('fixture_rows.csv')))
    def test_destination_schedule_complete_and_no_former_team_after_departure(self):
        r=self.rows('transfer_applicable_game_sequence.csv')
        self.assertTrue(all(x['team']!='BOS' for x in r if x['game_date']>=x['departure_date']))
        self.assertEqual(sum(x['team']=='MEM' for x in r),31);self.assertEqual(sum(x['team']=='POR' for x in r),31)
        self.assertTrue(all(x['roster_observed']=='True' for x in r))
if __name__=='__main__':unittest.main()
