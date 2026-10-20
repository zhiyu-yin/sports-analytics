"""Focused new-path checks: census registration, immutable cache, identities and audit."""
import csv,json,hashlib,random,unittest
from collections import Counter
from pathlib import Path
from phase2d.runtime import ROOT,D,SPEC,bindings,manifest,verify
from phase2d.sources import choose_usable,canonical_url
from phase2d.names import name_key,without_suffix

def rows(path):
    with path.open() as f:return list(csv.DictReader(f))
class Phase2DTests(unittest.TestCase):
    def test_fixed_all_remaining_order_and_spec_hash(self):
        ordered=sorted(SPEC['remaining_sorted'],key=lambda t:int(t['team_id']));random.Random(20240220).shuffle(ordered)
        self.assertEqual(ordered,SPEC['ordered_teams']);self.assertEqual([len(b) for b in SPEC['batches']],[6,6,5])
        selected=[t['team'] for t in ordered];self.assertEqual(len(set(selected)),17)
        self.assertFalse(set(selected)&set(SPEC['completed_prediction_teams']))
        self.assertTrue(json.loads((D/'registration/commit_receipt.json').read_text())['registration_commit'].startswith('0091efc'))
        verify()
    def test_stage1_counts_and_available_opportunities(self):
        s=json.loads((D/'stage1/summary.json').read_text());self.assertEqual((s['events'],s['events_with_main_opportunities']),(19,17))
        rr=rows(D/'stage1/available_opportunities.csv');self.assertEqual(Counter(r['extra_lag_days'] for r in rr),{'0':57,'1':52})
        self.assertTrue(all(0<float(r['lead_days_lower'])<=float(r['lead_days_upper'])<=14 for r in rr))
    def test_failure_does_not_override_later_success(self):
        fail=dict(usable=False,retrieved_at='2024-01-01',receipt_id='denied')
        success=dict(usable=True,retrieved_at='2024-01-02',receipt_id='valid')
        newer=dict(usable=True,retrieved_at='2024-01-03',receipt_id='new')
        self.assertEqual(choose_usable([fail,newer,success]),success)
        self.assertIsNone(choose_usable([fail]))
        self.assertEqual(canonical_url('HTTPS://WWW.NBA.COM/news/a/#frag'),'https://www.nba.com/news/a')
    def test_global_plan_and_actual_dedup_budget(self):
        rr=rows(D/'dry_run_request_plan.csv');self.assertEqual(len(rr),len({r['canonical_url'] for r in rr}))
        self.assertEqual(Counter(r['state'] for r in rr)['genuinely_new_request'],125)
        actual=[json.loads(l) for l in (D/'source_manifest.jsonl').read_text().splitlines()]
        self.assertEqual(len(actual),len({canonical_url(r['url']) for r in actual}))
        self.assertEqual(sum(r.get('scope')=='core' for r in actual),SPEC['budgets']['core_new_http'])
        self.assertLessEqual(sum(r.get('scope')=='supplement' for r in actual),SPEC['budgets']['supplement_new_http'])
        self.assertTrue(all('2023-12-04'<=r['date']<='2024-04-14' for r in actual))
    def test_nested_bindings_restore_even_on_exception(self):
        import phase2a.prepare as p,phase2a.surveillance as s,phase2b.build as b,phase2b.clocks as clocks,phase2c.pipeline as c
        def snapshot():return (p.ROOT,p.canonical,s.ROOT,b.D,b.random,b.canonical,clocks.book_clocks,c.D,c.manifest)
        original=snapshot();before=manifest()
        with self.assertRaisesRegex(RuntimeError,'unwind'):
            with bindings():
                self.assertEqual(manifest(),before);self.assertEqual(b.canonical('Butler III, Jimmy'),b.canonical('Butler, Jimmy'));raise RuntimeError('unwind')
        self.assertEqual(snapshot(),original)
        with bindings():pass
        self.assertEqual(snapshot(),original)
    def test_suffix_alias_preserves_full_identity(self):
        self.assertEqual(name_key('Butler III, Jimmy'),name_key('Butler, Jimmy'))
        self.assertEqual(name_key('Payton II, Gary'),name_key('Payton, Gary'))
        self.assertNotEqual(name_key('Porter Jr., Otto'),name_key('Porter, Jontay'))
        self.assertNotEqual(name_key('Williams, Jalen'),name_key('Williams, Jaylin'))
        self.assertEqual(without_suffix('Nance Jr.'),'Nance')
        obs=rows(D/'batch3/tables/status_observations.csv');self.assertTrue(any(r['player_id']=='202710' for r in obs))
    def test_suffix_before_after_semantic_impact_without_label_changes(self):
        r=rows(D/'tables/suffix_repair_count_impact.csv')
        for batch in ['1','2','3']:
            for lag in ['0','1']:
                a,b=[x for x in r if x['batch']==batch and x['extra_lag_days']==lag]
                for k in ['included','positive','negative','outcome_unknown']:self.assertEqual(a[k],b[k])
        impact=rows(D/'tables/suffix_repair_row_impact.csv');self.assertTrue(impact)
        self.assertFalse(any('absence_run_onset_ge10' in r['changed_fields'].split(';') for r in impact))
        self.assertFalse(any(r['changed_fields']=='retrospective_ascertainment_at' for r in impact))
    def test_distinct_medical_conditions_do_not_shift_original_anchor(self):
        ev={e['player_id']+'_'+e['anchor_date']:e for e in rows(D/'batch2/tables/events.csv')+rows(D/'batch3/tables/events.csv')}
        for k in ['1641727_2024-01-15','203897_2024-01-20','1629006_2024-03-03','1629639_2024-02-26']:
            self.assertEqual(ev[k]['severity'],'unknown')
        self.assertEqual(ev['1626196_2024-02-13']['severity'],'positive')
        self.assertGreaterEqual(int(ev['1626196_2024-02-13']['confirmed_same_episode_games']),10)
    def test_cumulative_counts_actual_overlap_and_opportunities(self):
        rr=rows(D/'tables/scope_results.csv')
        for lag,expected in [('0',(7108,115,6560,433,32)),('1',(6862,109,6329,424,31))]:
            union=next(r for r in rr if r['scope']=='combined_30_team_development' and r['extra_lag_days']==lag)
            self.assertEqual(tuple(int(union[k]) for k in ['included','positive','negative','outcome_unknown','events_with_eligible_prediction']),expected)
            self.assertEqual(int(union['team_count']),30);self.assertEqual(int(union['distinct_qualifying_events']),37)
            self.assertEqual(int(union['included']),sum(int(r['included']) for r in rr if r['scope']!='combined_30_team_development' and r['extra_lag_days']==lag))
            self.assertEqual(sum(int(r['positive_rows']) for r in rows(D/'tables/knowledge_summary.csv') if r['extra_lag_days']==lag),expected[1])
        overlap=rows(D/'tables/cross_batch_actual_game_overlap.csv');self.assertTrue(overlap)
        self.assertFalse(any(r['involves_positive']=='True' and r['same_original_anchor']=='False' for r in overlap))
        inv=rows(D/'tables/event_inventory.csv');self.assertEqual(len(inv),37);self.assertEqual(len({r['player_id'] for r in inv}),36)
    def test_full_registered_source_coverage_and_raw_receipts(self):
        coverage=rows(D/'tables/source_coverage.csv');self.assertEqual(len(coverage),17)
        for r in coverage:
            self.assertEqual(r['expected_team_games'],r['pages_obtained']);self.assertEqual(r['pages_obtained'],r['books_obtained']);self.assertEqual(r['books_obtained'],r['full_recaps']);self.assertEqual(r['dated_query_days'],'63')
        raw=[json.loads(p.read_text()) for p in (ROOT/'data/raw/phase2d/searches').glob('*.json')];self.assertEqual(sum(len(r['queries']) for r in raw),804);self.assertTrue(all(r['status']=='fulfilled' and r['response'] for r in raw))
    def test_pending_human_packet_and_seeded_source_rereads(self):
        packet=rows(D/'tables/human_review_packet.csv');self.assertEqual(sum(r['role']=='confirmed_positive_event' for r in packet),37);self.assertEqual(sum(r['role']=='seeded_negative_row' for r in packet),170)
        self.assertTrue(all(not r['accept_amend_reject'] and not r['reviewer_name'] and r['source_urls'] and r['exact_locators'] for r in packet))
        for i,n in [(1,60),(2,60),(3,50)]:
            negative=rows(D/f'batch{i}/tables/negative_sample_review.csv');audit=rows(D/f'batch{i}/tables/negative_original_source_audit.csv')
            self.assertEqual(len(negative),n);self.assertEqual(set(r['seed'] for r in negative),{'20240220'})
            self.assertEqual(set(Counter((r['team'],r['extra_lag_days']) for r in negative).values()),{5})
            self.assertEqual({r['row_id'] for r in negative},{r['row_id'] for r in audit});self.assertTrue(all(r['all_original_PID_and_book_name_checks_passed']=='True' for r in audit))
    def test_no_retrospective_evidence_leaks_and_ranges(self):
        for i in [1,2,3]:
            for r in rows(D/f'batch{i}/tables/cohort_all_roster_candidates.csv'):self.assertEqual(r['prospective_uses_retrospective_outcome_evidence'],'False')
            for r in rows(D/f'batch{i}/tables/row_outcomes.csv'):self.assertEqual(r['historical_label_known_at'],'');self.assertEqual(r['historical_training_cutoff_usable'],'False')
        for r in rows(D/'tables/identification_ranges.csv'):
            self.assertAlmostEqual(float(r['lower']),int(r['positive'])/int(r['included']));self.assertAlmostEqual(float(r['upper']),(int(r['positive'])+int(r['unknown']))/int(r['included']))
        self.assertEqual(hashlib.sha256((ROOT.parents[2]/'README.md').read_bytes()).hexdigest(),'b9a0a38563ece5c86d466e6f1f38b5378890981cec4c0ff965c1dd373ecc6992')
if __name__=='__main__':unittest.main()
