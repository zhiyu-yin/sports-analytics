"""Fixed-sample, cross-team and evidence-path checks; no model execution."""
import unittest,json,hashlib,csv,sys
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from phase2a.sampling import draw,SEED
from phase2a.prepare import resolve_inactive_reason
from phase2a.report_parser import valid_team_name
from phase2a.build import knowledge,positive_event_knowledge
from phase1d.logic import label_events
from injury_warning.rules import utc
D=ROOT/'phase2a'
def rows(name):
    with (D/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
class SamplingAndSources(unittest.TestCase):
    def test_fixed_ids_seed_and_sampling_implementation(self):
        p=D/'registration/sample_v1.json';r=json.loads(p.read_text());self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),p.with_suffix('.sha256').read_text().strip());self.assertEqual(SEED,r['seed']);self.assertEqual(len(r['frame']),29);self.assertNotIn('1610612738',{t['team_id'] for t in r['frame']});self.assertEqual(draw(r['frame']),r['selected']);self.assertEqual(draw(list(reversed(r['frame']))),r['selected']);self.assertEqual(hashlib.sha256((D/'sampling.py').read_bytes()).hexdigest(),r['sampling_code_sha256']);self.assertEqual({t['team'] for t in r['selected']},{'CLE','DEN','DET','ORL','PHI','SAS'})
    def test_historical_checkpoint_preserved(self):
        for p,h in json.loads((D/'registration/prior_checkpoint_hashes.json').read_text()).items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
    def test_sources_unique_bounded_and_search_receipts_real(self):
        req=json.loads((D/'request_catalog.json').read_text());self.assertEqual(len(req),len({r['source_id'] for r in req}));self.assertTrue(all('2023-12-04'<=r['date']<='2024-04-14' for r in req))
        q=json.loads((D/'search_ledger.json').read_text());self.assertEqual(len([v for v in q if v['team'] in {'CLE','DEN','DET','ORL','PHI','SAS'}]),378)
        for v in q:
            if (ROOT/v['raw_file']).exists():self.assertEqual(hashlib.sha256((ROOT/v['raw_file']).read_bytes()).hexdigest(),v['sha256'])
            self.assertEqual(v['status'],'fulfilled')
    def test_digit_team_and_same_family_do_not_corrupt_reports(self):
        self.assertTrue(valid_team_name('Philadelphia76ers'));self.assertFalse(valid_team_name('20240101'))
        inactive=[dict(personId=1,familyName='Mobley')];entries=[('Mobley','Injury/Illness - Left Knee; Surgery')]
        self.assertIsNone(resolve_inactive_reason('2','Mobley',inactive,entries));self.assertEqual(resolve_inactive_reason('1','Mobley',inactive,entries),entries[0][1]);self.assertIsNone(resolve_inactive_reason('1','Mobley',inactive+[dict(personId=2,familyName='Mobley')],entries))
        reports=json.loads((D/'parsed_reports.json').read_text());self.assertTrue(any(s['team']=='Philadelphia76ers' and s['state']=='complete' for r in reports for s in r['sections']))
class CohortEvidence(unittest.TestCase):
    def test_exactly_six_panels_and_shared_game_decisions_not_duplicated(self):
        co=rows('cohort_all_roster_candidates');self.assertEqual({r['team'] for r in co},{'CLE','DEN','DET','ORL','PHI','SAS'});self.assertEqual(len(co),len({r['row_id'] for r in co}));self.assertEqual(len(co),len({(r['index_game_id'],r['player_id'],r['extra_lag_days']) for r in co}));self.assertTrue(all('2024-01-01'<=r['index_game_date']<='2024-02-18' for r in co));self.assertTrue(all(r['prospective_uses_retrospective_outcome_evidence']=='False' for r in co))
        self.assertTrue(any(r['team']=='DET' and r['player_id']=='1627863' and r['role'].startswith('transaction_only') for r in rows('roster_inventory')))
    def test_funnel_never_discards_unknown_rows(self):
        for r in rows('team_results'):
            self.assertEqual(int(r['candidate_appearances']),sum(int(r[k]) for k in ['included','excluded','eligibility_unknown']));self.assertEqual(int(r['included']),sum(int(r[k]) for k in ['positive','negative','outcome_unknown']))
        self.assertTrue(any(r['absence_run_onset_ge10']=='unknown' for r in rows('row_outcomes')))
    def test_appearance_inventory_and_features_outcomes_separate(self):
        co={r['row_id'] for r in rows('cohort_all_roster_candidates') if r['B_state']=='included'};self.assertEqual(co,{r['row_id'] for r in rows('row_outcomes')});self.assertEqual(co,{r['row_id'] for r in rows('features_B')});self.assertEqual(rows('features_A'),[])
        self.assertTrue(all(not r['historical_label_known_at'] and r['historical_training_cutoff_usable']=='False' for r in rows('row_outcomes')))
    def test_cross_team_history_past_only_and_missing_not_zero_filled(self):
        rr=rows('features_B');self.assertTrue(any(';' in r['input_teams'] and r['history_complete']=='True' for r in rr))
        for r in rr:
            if r['max_input_assumed_available_at']:self.assertLessEqual(utc(r['max_input_assumed_available_at']),utc(r['decision_at']))
            if r['history_complete']=='False':self.assertEqual(r['minutes_28d'],'');self.assertTrue(r['missing_history_reason'])
    def test_cross_team_positive_actual_dest_schedule(self):
        es=[r for r in rows('events') if r['player_id']=='1630587' and r['anchor_date']=='2024-01-24'];self.assertEqual(len(es),1);e=es[0];self.assertEqual(e['severity'],'positive');self.assertEqual(e['anchor_team'],'WAS');self.assertEqual(e['sampled_origin_team'],'DET');gg=[g for g in rows('event_game_evidence') if g['event_id']==e['event_id']];self.assertTrue(all(g['team']=='WAS' for g in gg));self.assertTrue(any(r['team']=='DET' and e['event_id'] in r['event_ids'] for r in rows('positive_knowledge_review')))
    def test_positive_attribution_actual_ten_consecutive_games_no_appearance(self):
        members=defaultdict(list)
        for r in rows('event_game_evidence'):members[r['event_id']].append(r)
        for e in rows('events'):
            if e['severity']!='positive':continue
            self.assertEqual(e['continuity_supported'],'True');self.assertTrue(e['continuity_source_ids']);streak=best=0
            for g in members[e['event_id']]:
                self.assertEqual(g['appeared'],'False')
                if g['category']=='injury' and g['roster_observed']=='True':streak+=1;best=max(best,streak)
                else:streak=0
            self.assertGreaterEqual(best,10);self.assertGreaterEqual(int(e['confirmed_same_episode_games']),10)
        es=rows('events');self.assertEqual(len(es),len({e['event_id'] for e in es}))
    def test_rows_share_one_event_and_zero_eligible_events_remain_inventory(self):
        counts=Counter(e for r in rows('positive_knowledge_review') if r['extra_lag_days']=='0' for e in r['event_ids'].split(';'));self.assertTrue(any(v>1 for v in counts.values()))
        ev=rows('event_prediction_coverage');self.assertTrue(any(r['player_id']=='203496' and r['has_eligible_preceding_prediction']=='False' and r['broad_onset_period']=='True' for r in ev))
        cov=next(r for r in rows('events') if r['player_id']=='203496' and r['anchor_date']=='2024-01-02');self.assertEqual(cov['severity'],'unknown');self.assertIn('illness',cov['mixed_categories'])
    def test_all_potential_severities_reviewed_and_negative_sample_per_team(self):
        self.assertEqual({r['event_id'] for r in rows('events') if r['severity']!='negative'},{r['event_id'] for r in rows('detailed_event_reviews')});n=rows('negative_sample_review');self.assertEqual(len(n),60);self.assertTrue(all(v>=5 for v in Counter((r['team'],r['extra_lag_days']) for r in n).values()));self.assertTrue(all(r['source_sequence_check']=='True' for r in n))
        for r in n:self.assertNotIn('positive',r['event_severities'].split(';'));self.assertNotIn('unknown',r['event_severities'].split(';'))
    def test_knowledge_is_predecision_and_not_preinjury_claim(self):
        sig=dict(player_id='p',kind='acute',B_available_at='2024-01-04T01:00:00-05:00',signal_id='s')
        self.assertEqual(knowledge('2024-01-03T12:00:00-05:00','p',[],[sig])['group_B'],'no_signal_found_under_searched_process');self.assertEqual(knowledge('2024-01-04T12:00:00-05:00','p',[],[sig])['group_B'],'acute_already_disclosed')
        prior=dict(sig,event_game_id='old',B_available_at='2024-01-02T01:00:00-05:00');new=dict(acute_event_game_ids='new')
        self.assertEqual(positive_event_knowledge('2024-01-03T12:00:00-05:00','p',[],[prior],[new])['group_B'],'symptom_or_history_known')
        p=rows('positive_knowledge_review');self.assertTrue(any(r['group_B']=='acute_already_disclosed' for r in p));self.assertTrue(all(r['group_A']=='knowledge_timing_unresolved' for r in p))
    def test_actual_positive_negative_exclusion_and_unresolved_paths(self):
        co=rows('cohort_all_roster_candidates');self.assertTrue(any(r['player_id']=='203954' and r['index_game_date']=='2024-01-30' and r['B_state']=='excluded' for r in co));oo=rows('row_outcomes');self.assertTrue(any(r['player_id']=='203954' and r['absence_run_onset_ge10']=='positive' for r in oo));self.assertTrue(any(r['team']=='CLE' and r['absence_run_onset_ge10']=='negative' for r in oo));self.assertTrue(any(r['team']=='DEN' and r['absence_run_onset_ge10']=='unknown' for r in oo))
if __name__=='__main__':unittest.main()
