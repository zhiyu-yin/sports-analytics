"""Regression coverage for new batch bindings, provenance, deduplication and review."""
import csv,hashlib,json,unittest
from collections import Counter
from phase2c.pipeline import D,ROOT,bindings,manifest,registration,rows,verify
from phase2c.sampling import draw

class Phase2CTests(unittest.TestCase):
    def test_registered_frame_seed_and_frozen_spec(self):
        r=registration();self.assertEqual(len(r['frame']),23)
        self.assertEqual([x['team'] for x in draw(r['frame'])],['ATL','DAL','NYK','SAC','OKC','MEM'])
        self.assertEqual(draw(r['frame']),r['selected'])
        self.assertFalse(set(x['team'] for x in r['selected'])&{'BOS','CLE','DEN','DET','ORL','PHI','SAS'})
        self.assertEqual(hashlib.sha256((D/'sampling.py').read_bytes()).hexdigest(),r['sampling_code_sha256'])
        self.assertTrue(json.loads((D/'registration/commit_receipt.json').read_text())['sampling_commit'].startswith('f0cb534'))
        verify()
    def test_manifest_is_independent_of_batch_output_binding(self):
        a=manifest()
        import phase2a.acquire as acquisition
        old=acquisition.D
        with bindings():
            self.assertEqual(a,manifest())
            self.assertEqual(acquisition.D,D)
        self.assertEqual(acquisition.D,old)
        # The redundant fresh response had no period clocks; the frozen prior
        # page is retained and supplies the independently audited clock.
        source=a['page_0022301217']
        with (ROOT/'phase2a/source_manifest.jsonl').open() as f:prior={r['source_id']:r for r in map(json.loads,f)}
        self.assertEqual(source['sha256'],prior['page_0022301217']['sha256'])
        r=next(r for r in rows('all_acquired_game_clock_audit') if r['game_id']=='0022301217')
        self.assertTrue(r['end_upper'])
    def test_bindings_restore_even_on_exception(self):
        import phase2b.build as build
        old=(build.D,build.write,build.random)
        with self.assertRaises(RuntimeError):
            with bindings():raise RuntimeError('test unwind')
        self.assertEqual((build.D,build.write,build.random),old)
    def test_cached_report_provenance_matches_retained_raw_source(self):
        sm=manifest()
        for r in json.loads((D/'parsed_reports.json').read_text()):
            self.assertEqual(r['raw_source_sha256'],sm[r['source_id']].get('sha256',''))
            self.assertEqual(r['retrieval_status'],sm[r['source_id']]['status'])
        self.assertTrue(any(o['team']=='Philadelphia76ers' for r in json.loads((D/'parsed_reports.json').read_text()) for o in r['observations']))
    def test_exact_prediction_scope_no_fixture_rows(self):
        selected={r['team'] for r in registration()['selected']}
        for r in rows('cohort_all_roster_candidates'):
            self.assertIn(r['team'],selected)
            self.assertTrue('2024-01-01'<=r['index_game_date']<='2024-02-18')
            self.assertTrue(r['index_game_id'].startswith('00223'))
        self.assertTrue(all(r['team'] in selected for r in rows('roster_inventory')))
        self.assertTrue(any(r['player_id']=='201577' and r['team']=='SAC' for r in rows('contract_only_inventory')))
    def test_medical_review_rejects_opponents_and_suffix_collision(self):
        review={r['card_id']:r for r in rows('recap_candidate_adjudication')}
        self.assertEqual(review['107']['accepted_player_ids'],'') # opposing Cameron Johnson, not Keyontae
        self.assertEqual(review['225']['accepted_player_ids'],'1630198;1631114') # Isaiah Joe and Jalen, not Jaylin/Kenrich
        signals=json.loads((D/'recap_adjudications.json').read_text())
        self.assertTrue(any(r['player_id']=='203501' and r['source_game_id']=='0022300556' and r['kind']=='acute' for r in signals))
        self.assertFalse(any(r['player_id']=='1630314' and r['source_game_id']=='0022300472' for r in signals)) # Grant, not Brandon
    def test_actual_segments_common_identity_and_late_horizon(self):
        ev={r['player_id']+'_'+r['anchor_date']:r for r in rows('events')}
        self.assertEqual(ev['203944_2024-01-29']['confirmed_same_episode_games'],'36')
        self.assertEqual(ev['1630590_2024-02-14']['confirmed_same_episode_games'],'12')
        self.assertEqual(ev['201565_2024-03-01']['confirmed_same_episode_games'],'10')
        later=[r for r in rows('event_prediction_coverage') if r['player_id']=='201565' and r['anchor_date']=='2024-03-01']
        self.assertTrue(all(r['eligible_positive_rows']=='0' for r in later))
        # Closed mixed envelope does not count its coaching entries as medical.
        self.assertLess(int(ev['202083_2024-01-10']['longest_injury_only_segment']),10)
        self.assertNotEqual(ev['202083_2024-01-10']['severity'],'positive')
    def test_negative_sample_seed_and_all_teams_both_lags(self):
        r=rows('negative_sample_review');self.assertEqual(len(r),60)
        self.assertEqual(set(x['seed'] for x in r),{'20240219'})
        self.assertEqual(set(Counter((x['team'],x['extra_lag_days']) for x in r).values()),{5})
    def test_original_negative_source_path(self):
        audit=rows('negative_original_source_audit')
        self.assertEqual({r['row_id'] for r in audit},{r['row_id'] for r in rows('negative_sample_review')})
        for r in audit:
            self.assertGreater(int(r['source_games_reopened']),0)
            self.assertEqual(r['all_original_PID_and_book_name_checks_passed'],'True')
            self.assertEqual(r['independent_human_review'],'False')
            self.assertTrue(all(int(x)<10 for x in r['in_horizon_candidate_upper_bounds'].split(';') if x))

    def test_no_C_into_prospective_eligibility_or_knowledge(self):
        for r in rows('cohort_all_roster_candidates'):
            self.assertEqual(r['prospective_uses_retrospective_outcome_evidence'],'False')
            self.assertFalse(any(x.startswith('c_') for x in r['signal_ids'].split(';')))
        for r in rows('row_outcomes'):
            self.assertEqual(r['historical_label_known_at'],'');self.assertEqual(r['historical_training_cutoff_usable'],'False')
            if r['absence_run_onset_ge10']!='positive':self.assertEqual(r['acute_known_B'],'False')
    def test_canonical_union_preserves_events_and_decisions(self):
        r=rows('scope_results')
        for lag in ['0','1']:
            a=[x for x in r if x['extra_lag_days']==lag];union=next(x for x in a if x['scope']=='combined_development');parts=[x for x in a if x['scope']!='combined_development']
            self.assertEqual(int(union['included']),sum(int(x['included']) for x in parts))
            self.assertEqual(int(union['distinct_qualifying_events']),19)
            self.assertEqual(int(union['distinct_membership_inventory_players']),int(union['distinct_roster_players'])+2)
        e=rows('canonical_events');self.assertEqual(len(e),len({r['canonical_event_id'] for r in e}))
    def test_identification_ranges_and_pending_human_packet(self):
        for r in rows('missing_label_identification_ranges'):
            lo=float(r['lower_if_unknown_negative']);hi=float(r['upper_if_unknown_positive']);self.assertTrue(0<=lo<=hi<=1)
            self.assertAlmostEqual(lo,int(r['positive'])/int(r['included']))
        p=rows('human_review_packet');self.assertEqual(sum(r['role']=='confirmed_positive_event' for r in p),13)
        self.assertEqual(sum(r['role']=='seeded_negative_row' for r in p),60)
        self.assertTrue(all(r['source_urls'] and r['exact_locators'] and not r['accept_amend_reject'] and r['human_review_completed']=='False' for r in p))
    def test_bug_impact_and_wrong_year_source_rejection(self):
        r=rows('source_binding_before_after')
        for lag in ['0','1']:
            a,b=[x for x in r if x['extra_lag_days']==lag]
            for k in ['included','excluded','positive','negative','outcome_unknown','missing_history']:self.assertEqual(a[k],b[k])
        self.assertFalse(any(r['table']=='features_B' for r in rows('source_binding_row_impact')))
        self.assertTrue(rows('source_applicability_rejections'))
        costs=json.loads((D/'cost_and_quality.json').read_text());self.assertEqual(costs['redundant_http_requests_from_adapter_bug'],650)
        self.assertEqual(set(r['prior_status'] for r in rows('duplicate_request_receipts')),{'obtained'})
    def test_all_caches_checked_and_historical_outputs_preserved(self):
        self.assertEqual(len(rows('all_acquired_game_clock_audit')),889)
        self.assertTrue(all(r['end_upper'] for r in rows('all_acquired_game_clock_audit')))
        for p,h in json.loads((D/'registration/preserved_hashes.json').read_text()).items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
        root_readme=ROOT.parents[2]/'README.md'
        self.assertEqual(hashlib.sha256(root_readme.read_bytes()).hexdigest(),'b9a0a38563ece5c86d466e6f1f38b5378890981cec4c0ff965c1dd373ecc6992')

if __name__=='__main__':unittest.main()
