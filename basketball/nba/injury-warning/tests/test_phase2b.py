"""Source-backed regression coverage for the fixed development audit."""
import unittest,json,hashlib,csv
from datetime import datetime,timedelta
from injury_warning.pilot_io import ROOT
from phase2b.io import D,rows
from phase2b.clocks import parse_clock,endpoints
from phase2b.knowledge import knowledge,positive_event_knowledge,COMPLETIONS
from phase2b.segments import maximal_segments,adjudicate_segments,SEGMENTS

class Phase2BTests(unittest.TestCase):
    def test_source_named_clocks_and_utc_rollover(self):
        r={x['game_id']:x for x in rows('all_acquired_game_clock_audit')}
        self.assertEqual(r['0022300686']['start_lower'],'2024-02-01T22:16:00-05:00')
        self.assertEqual(r['0022300463']['end_upper'],'2024-01-03T00:40:00-05:00')
        self.assertEqual(r['0022300527']['end_upper'],'2024-01-11T16:43:00-05:00')
        self.assertEqual(r['0022300527']['book_end_raw'],'10:42 PM')
        lo,hi,_=parse_clock('End (12:39 AM EST)','2024-01-02','2024-01-03T03:00:00Z')
        self.assertEqual(lo,'2024-01-03T00:39:00-05:00')
        self.assertEqual(datetime.fromisoformat(hi)-datetime.fromisoformat(lo),timedelta(minutes=1))
    def test_literal_utc_not_eastern_and_ambiguous_unknown(self):
        lo,_,_=parse_clock('End (5:39 AM UTC)','2024-01-03','2024-01-03T03:00:00Z')
        self.assertEqual(lo,'2024-01-03T05:39:00+00:00')
        p={'game':{'gameTimeUTC':'2024-01-03T03:00:00Z'},'playByPlay':{'actions':[{'actionType':'period','subType':'end','period':4,'description':'End (5:39 AM UTC)'}]}}
        self.assertEqual(endpoints(p,'2024-01-03')[3][0],lo)
        self.assertEqual(parse_clock('End (9:39 PM)','2024-01-02')[:2],(None,None))
    def test_stale_est_label_requires_verified_source_semantics(self):
        r=next(x for x in rows('all_acquired_game_clock_audit') if x['game_id']=='0022301093')
        self.assertIn('EST',r['start_raw']);self.assertEqual(r['start_lower'],'2024-04-02T19:36:00-04:00')
        literal,_,_=parse_clock(r['start_raw'],r['game_date'],r['scheduled_start_utc'])
        self.assertNotEqual(datetime.fromisoformat(literal),datetime.fromisoformat(r['start_lower']))
        for r in rows('all_acquired_game_clock_audit'):
            self.assertLessEqual(abs(float(r['page_minus_book_end_minutes'])),1)
    def test_history_retention_status_expiry_and_supersession(self):
        obs=[dict(player_id='x',team='DET',target_game_date='2024-01-20',category='injury',status='Out',observation_id='prior',B_available_at='2024-01-20T12:00:00-05:00')]
        k=knowledge('2024-02-20T12:00:00-05:00','x',obs,[])
        self.assertTrue(k['ever_known_injury_history_B']);self.assertFalse(k['recent_known_symptoms_28d_B']);self.assertFalse(k['current_status_observation_ids'])
        self.assertEqual(k['expired_status_observation_ids'],'prior')
        obs += [dict(obs[0],target_game_date='2024-02-21',B_available_at='2024-02-20T11:00:00-05:00',observation_id='new'),dict(obs[0],target_game_date='2024-02-21',B_available_at='2024-02-20T11:30:00-05:00',status='Available',observation_id='available')]
        k=knowledge('2024-02-20T12:00:00-05:00','x',obs,[])
        self.assertEqual(k['current_status_observation_ids'],'available');self.assertEqual(k['explicit_superseding_available_ids'],'available')
        self.assertTrue(k['ever_known_injury_history_B'])
    def test_completion_expires_current_game_without_erasing_history(self):
        key=('FAKE','2024-01-20');COMPLETIONS[key]='2024-01-20T10:00:00-05:00'
        o=dict(player_id='x',team='FAKE',target_game_date='2024-01-20',category='injury',status='Out',observation_id='o',B_available_at='2024-01-20T09:00:00-05:00')
        try:
            k=knowledge('2024-01-20T12:00:00-05:00','x',[o],[]);self.assertFalse(k['current_status_observation_ids']);self.assertTrue(k['ever_known_injury_history_B'])
        finally:COMPLETIONS.pop(key)
    def test_event_specific_disclosure_and_future_evidence(self):
        s=dict(player_id='x',kind='acute',event_game_id='old',signal_id='s',B_available_at='2024-01-01T10:00:00-05:00')
        t='2024-01-02T12:00:00-05:00'
        self.assertFalse(knowledge(t,'x',[],[s])['acute_known_B'])
        self.assertFalse(positive_event_knowledge(t,'x',[],[s],[{'acute_event_game_ids':'other'}])['acute_known_B'])
        self.assertTrue(positive_event_knowledge(t,'x',[],[s],[{'acute_event_game_ids':'old'}])['acute_known_B'])
        self.assertFalse(knowledge(t,'x',[],[dict(s,B_available_at='2024-01-03T00:00:00-05:00')])['ever_known_injury_history_B'])
        for r in rows('row_outcomes'):
            if r['absence_run_onset_ge10']!='positive':self.assertEqual(r['acute_known_B'],'False')
    def test_stewart_both_lags_history_persists(self):
        rr=[r for r in rows('cohort_all_roster_candidates') if r['player_id']=='1630191' and r['index_game_date']=='2024-01-28']
        self.assertEqual(len(rr),2)
        self.assertTrue(all(r['ever_known_injury_history_B']=='True' and r['group_B']=='symptom_or_history_known' for r in rr))
    def test_maximal_segments_never_add_across_conflict(self):
        def game(n,category):return dict(game_id=str(n),game_date='2024-01-01',category=category,roster_observed=True,coverage='page_and_book')
        g=[game(i,'injury') for i in range(6)]+[game(6,'unknown')]+[game(i,'injury') for i in range(7,13)]
        self.assertEqual([len(x) for x in maximal_segments(g)],[6,6])
    def test_source_qualifying_subruns_and_uncertain_anchor(self):
        ev={r['player_id']+'_'+r['anchor_date']:r for r in rows('events')}
        self.assertEqual(ev['1631124_2024-01-05']['confirmed_same_episode_games'],'13')
        self.assertEqual(ev['1631321_2024-01-10']['confirmed_same_episode_games'],'10')
        self.assertEqual(ev['1630191_2024-01-31']['longest_injury_only_segment'],'4')
        self.assertEqual(ev['203496_2024-01-02']['severity'],'unknown')
        self.assertEqual(ev['203496_2024-01-02']['anchor_date'],'2024-01-02')
        self.assertEqual(ev['203496_2024-01-02']['anchor_identity_uncertain'],'True')
        seg=[r for r in rows('injury_segments') if r['player_id']=='203496' and r['threshold_met']=='True']
        self.assertTrue(seg);self.assertEqual(seg[0]['original_anchor_supported'],'False')
    def test_matching_diagnosis_alone_and_closed_short_upper_bound(self):
        def game(n,observed=True):return dict(game_id=str(n),game_date='2024-01-01',category='injury',roster_observed=observed,coverage='page_and_book',page_source='p',reason_source='b')
        def event():return dict(event_id='test',player_id='test',player_name='Test',anchor_date='2024-01-01',return_date='2024-02-01',left_censored_start=False,contract_gap_in_run=False,severity='unknown',confirmed_same_episode_games=0,continuity_supported=False)
        before=len(SEGMENTS)
        try:
            e=event();adjudicate_segments(e,[game(i) for i in range(10)])
            self.assertEqual(e['severity'],'unknown');self.assertFalse(e['qualifying_segment_established'])
            e=event();adjudicate_segments(e,[game(1,False)])
            self.assertEqual(e['severity'],'negative');self.assertEqual(e['possible_run_upper'],1)
            e=event();e['left_censored_start']=True;adjudicate_segments(e,[game(1,False)])
            self.assertEqual(e['severity'],'unknown')
        finally:del SEGMENTS[before:]

    def test_membership_waivers_remove_speculative_games_no_zero_fill(self):
        sp=rows('membership_spells')
        for pid,team in [('1628995','UTA'),('1627788','IND')]:self.assertEqual(next(r for r in sp if r['player_id']==pid and r['team']==team)['end'],'2024-02-08')
        n=[r for r in sp if r['player_id']=='1631250'];self.assertEqual(len(n),2)
        self.assertEqual(n[1]['start'],'2024-02-19')
        f=[r for r in rows('features_B') if r['player_id']=='1631250'];self.assertTrue(all(r['history_complete']=='False' for r in f))
    def test_both_lag_rebuild_counts_and_feature_invariance(self):
        rr=[r for r in rows('before_after') if r['version']=='after_phase2b']
        self.assertEqual([(r['included'],r['positive'],r['negative'],r['outcome_unknown']) for r in rr],[('1425','11','1285','129'),('1359','11','1224','124')])
        self.assertTrue(all(r['changed_feature_rows']=='0' for r in rr))
        change=[r for r in rows('changed_rows') if r['table']=='row_outcomes' and 'absence_run_onset_ge10' in r['changed_fields']]
        self.assertEqual(len(change),3)
        self.assertTrue(all(r['old_value'] and r['new_value'] and r['reason'] and r['supporting_source_or_rule'] for r in change))
    def test_prior_outputs_and_raw_source_checksums(self):
        for name,h in json.loads((D/'registration/preserved_hashes.json').read_text()).items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),h,name)
        for r in json.loads((D/'source_manifest.json').read_text()):
            if r['status']=='obtained':self.assertEqual(hashlib.sha256((ROOT/r['raw_file']).read_bytes()).hexdigest(),r['sha256'])
        s=json.loads((D/'legacy_rebuild_summary.json').read_text());self.assertTrue(s['boston_labels_identical']);self.assertTrue(s['fixture_labels_and_eligibility_identical'])

if __name__=='__main__':unittest.main()
