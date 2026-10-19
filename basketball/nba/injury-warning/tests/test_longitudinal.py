import csv,hashlib,json,unittest
from pathlib import Path
from injury_warning.longitudinal import (resolve_name,member_on,absence_category,
    report_player_state,point_status,end_minute,minutes,later_noon)

ROOT=Path(__file__).resolve().parents[1]


class LongitudinalRules(unittest.TestCase):
    def test_roster_entry_exit_uncertainty(self):
        self.assertEqual(member_on('2024-02-06','2024-02-07','2024-02-08'),'not_member')
        self.assertEqual(member_on('2024-02-07','2024-02-07','2024-02-08'),'unknown')
        self.assertEqual(member_on('2024-02-08','2024-02-07','2024-02-08'),'member')
        self.assertEqual(member_on('2024-02-07','2023-12-01','2023-12-01','2024-02-07','2024-02-08'),'unknown')
        self.assertEqual(member_on('2024-02-08','2023-12-01','2023-12-01','2024-02-07','2024-02-08'),'not_member')

    def test_duplicate_names_are_not_identifiers(self):
        p=[dict(player_id='1',player_name='Alex Smith',family_name='Smith',first_name='Alex'),dict(player_id='2',player_name='Alex Smith',family_name='Smith',first_name='Alex')]
        self.assertIsNone(resolve_name('Alex Smith',p))
        self.assertIsNone(resolve_name('Smith',p))
        self.assertEqual(resolve_name('Smith, Alex',p[:1]),'1')

    def test_reason_not_prefix_controls_attribution(self):
        self.assertEqual(absence_category('Injury/Illness - N/a; Illness'),'illness')
        self.assertEqual(absence_category('Injury/Illness - Left Ankle; Injury Management'),'injury')
        self.assertEqual(absence_category('DND - Injury/Illness - Right Shoulder; Dislocated'),'injury')
        self.assertEqual(absence_category('Rest'),'rest')
        self.assertEqual(absence_category("DNP - Coach's Decision"),'coaching')
        self.assertEqual(absence_category(''),'unknown')

    def test_missing_report_distinct_from_not_listed(self):
        self.assertEqual(report_player_state('missing_report',False),'missing_report')
        self.assertEqual(report_player_state('not_yet_submitted',False),'not_yet_submitted')
        self.assertEqual(report_player_state('complete',False),'absent_from_complete_report')
        self.assertEqual(report_player_state('complete',True),'listed')

    def test_publication_and_scope_prevent_future_or_stale_status(self):
        o=dict(report_at='2024-01-03T10:30:00-05:00',status='Available',reason='-',publication_verified=False,target_game_date='2024-01-03')
        self.assertEqual(point_status(o,'2024-01-03T12:00:00-05:00')[0],'unknown')
        self.assertEqual(point_status(dict(o,publication_verified='False'),'2024-01-03T12:00:00-05:00')[0],'unknown')
        self.assertEqual(point_status(dict(o,publication_verified=True),'2024-01-03T12:00:00-05:00')[0],'available')
        self.assertEqual(point_status(dict(o,publication_verified=True),'2024-01-03T09:00:00-05:00')[0],'unknown')
        self.assertEqual(point_status(dict(o,publication_verified=True,target_game_date='2024-01-02'),'2024-01-03T12:00:00-05:00')[0],'unknown')

    def test_end_minute_is_interval_not_start_or_exact_second(self):
        a=[dict(actionType='period',subType='end',period=4,actionNumber=500,description='End of 4th Period (9:27 PM CST)')]
        lo,hi,_=end_minute(a,'2024-01-02')
        self.assertEqual(lo,'2024-01-02T21:27:00-06:00')
        self.assertEqual(hi,'2024-01-02T21:28:00-06:00')
        self.assertEqual(end_minute([],'2024-01-02')[:2],(None,None))
        self.assertEqual(later_noon('2024-01-02'),'2024-01-03T12:00:00-05:00')

    def test_explicit_source_minutes_normalization(self):
        self.assertEqual(minutes('33:60'),34)
        self.assertIsNone(minutes(''))
        with self.assertRaises(ValueError):minutes('33:99')


class PilotEvidenceIntegrity(unittest.TestCase):
    def read(self,name):
        with (ROOT/'pilot/tables'/name).open() as f:return list(csv.DictReader(f))

    def test_registration_unchanged(self):
        p=ROOT/'pilot/registration/design.json'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),p.with_suffix('.sha256').read_text().strip())

    def test_cohort_has_all_listed_members_and_no_external_cases(self):
        preds=self.read('prediction_timestamps.csv');games=self.read('player_games.csv')
        expected={(r['game_id'],r['player_id']) for r in games if r['phase']=='pilot'}
        actual={(r['game_id'],r['player_id']) for r in preds}
        self.assertTrue(expected <= actual)
        extras=[r for r in preds if (r['game_id'],r['player_id']) not in expected]
        self.assertTrue(all(r['roster_membership']=='uncertain_transaction_day' for r in extras))
        self.assertEqual(len(preds),len(actual))
        self.assertTrue(all(r['primary_label']=='unknown' and r['secondary_label']=='unknown' for r in preds))
        self.assertTrue(all(not r['immediate_prediction_at'] for r in preds))

    def test_status_identity_resolution_and_source_links(self):
        sources={json.loads(line)['source_id'] for line in (ROOT/'pilot/source_manifest.jsonl').read_text().splitlines()}
        for o in self.read('status_observations.csv'):
            self.assertTrue(o['player_id'])
            self.assertIn(o['source_id'],sources)
            self.assertFalse(o['publication_at'])

    def test_original_audit_preserved_and_review_not_independent(self):
        with (ROOT/'audit/candidates.csv').open() as f:old=list(csv.DictReader(f))
        queue=self.read('user_review_queue.csv')
        self.assertEqual({r['candidate_id'] for r in old},{r['case_id'] for r in queue})
        self.assertTrue(all(r['independent_human_review']=='not_done' for r in queue))
