"""Focused preparation invariants; no model or preprocessing fitting."""
import copy
import hashlib
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from phase3a.study import (D,ROOT,FEATURES,features,predictors,fold,config,validate_config,
                           verify_snapshot,read,timing_audit)


class Phase3ATests(unittest.TestCase):
    def test_allowlist_rejects_outcome_identity_and_acute_linkage(self):
        x={k:None for k in FEATURES}
        for forbidden in ('player_id','team','label','confirmed_same_episode_games','acute_known_B','event_ids'):
            with self.assertRaises(ValueError):predictors(dict(x,**{forbidden:1}))
        with self.assertRaises(ValueError):predictors({})
        with self.assertRaises(ValueError):predictors(dict(x,past_mean_minutes=float('nan')))

    def test_missing_coverage_never_zero_filled(self):
        r=dict(history_complete='False',recent_known_symptoms_28d_B='False',ever_known_injury_history_B='True')
        f=dict(past_mean_minutes_per_appearance='20',workload_change_7d='10',index_back_to_back='True')
        x=features(r,f)
        self.assertIsNone(x['past_mean_minutes']);self.assertIsNone(x['workload_change_minutes_7d'])
        self.assertIsNone(x['index_back_to_back']);self.assertEqual(x['recent_evidence_28d'],0)

    def test_legacy_knowledge_missing_not_false(self):
        x=features(dict(history_complete='True',B_symptom_informed='False'),{})
        self.assertIsNone(x['recent_evidence_28d']);self.assertIsNone(x['older_or_recent_history'])

    def test_config_fixed_and_no_fit_authorization(self):
        c=config();validate_config(c)
        changed=copy.deepcopy(c);changed['models']['M2']['features'].append('event_id')
        with self.assertRaises(AssertionError):validate_config(changed)
        self.assertFalse(c['fitting_authorized'])

    def test_refuses_even_explicit_fit_flag(self):
        p=subprocess.run([sys.executable,'-m','phase3a.study','--execute-fit'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('Fitting refused',p.stderr)

    def test_snapshot_and_prior_hashes(self):
        m=verify_snapshot();self.assertFalse(m['historical_files_modified'])
        self.assertEqual(m['correction_ledger'],[])
        self.assertIn('phase2d/result_hashes.json',m['files'])

    def test_grouping_transfers_and_related_runs(self):
        rows=read(D/'tables/analysis_rows.csv');assignments={}
        for r in rows:
            assignments.setdefault(r['player_id'],set()).add(r['fold'])
            self.assertEqual(int(r['fold']),fold(r['player_id']))
        self.assertTrue(all(len(v)==1 for v in assignments.values()))
        related=read(D/'tables/related_runs.csv');self.assertEqual(len(related),1)
        self.assertEqual(fold(related[0]['player_id']),fold('201565'))
        for f in range(5):
            train={r['player_id'] for r in rows if int(r['fold'])!=f}
            test={r['player_id'] for r in rows if int(r['fold'])==f}
            self.assertFalse(train & test)

    def test_timing_audit_fails_closed(self):
        row=dict(row_id='x',player_id='p',batch='Boston_prior',B_state='included',decision_at='2024-01-02T12:00:00-05:00')
        ff={'Boston_prior':{'x':dict(max_input_assumed_available_at='2024-01-03T12:00:00-05:00')}}
        with patch('phase3a.study.write'):
            with self.assertRaises(AssertionError):timing_audit([row],ff)
        ff['Boston_prior']['x']['max_input_assumed_available_at']='2024-01-01T12:00:00-05:00'
        with patch('phase3a.study.write'):timing_audit([row],ff)

    def test_reconciliation_and_unknowns(self):
        rows=read(D/'tables/reconciliation.csv')
        self.assertEqual([(int(r['included']),int(r['positive']),int(r['negative']),int(r['unknown'])) for r in rows],[(7108,115,6560,433),(6862,109,6329,424)])
        for r in rows:self.assertAlmostEqual(float(r['upper']),(int(r['positive'])+int(r['unknown']))/int(r['included']))

    def test_blinded_packet_no_answer_columns_or_decisions(self):
        cases=read(D/'review/first_pass/cases.csv');key=read(D/'review/answer_key.csv')
        self.assertEqual(len(cases),len(key));self.assertEqual(len({r['case_id'] for r in cases}),len(cases))
        self.assertFalse({'selection_role','original_severity','confidence','current_label','original_count'} & set(cases[0]))
        self.assertTrue(all(not r['reviewer_decision'] and not r['reviewer_identity'] for r in cases))
        summary=json.loads((D/'review/summary.json').read_text())
        self.assertEqual(summary['qualifying'],37);self.assertEqual(summary['negative'],30)
        self.assertEqual(len(summary['teams_in_negative_sample']),30);self.assertEqual(summary['independent_human_reviews'],0)
        self.assertGreater(summary['consequential_unknown'],0)

    def test_excerpt_budget_and_locators(self):
        totals={}
        batches={r['case_id']:r['batch'] for r in read(D/'review/answer_key.csv')}
        audit={(r['batch'],r['source_id']):r for r in read(D/'review/source_version_audit.csv')}
        for r in read(D/'review/first_pass/sources.csv'):
            expected=audit.get((batches[r['case_id']],r['source_id']))
            if expected:self.assertEqual(r['sha256'],expected['historical_sha256'])
            self.assertTrue(r['url']);self.assertTrue(r['locator'])
            totals[r['url']]=totals.get(r['url'],0)+len(r['short_excerpt'].split())
        self.assertTrue(all(n<=25 for n in totals.values()))
        for r in read(D/'review/first_pass/factual_timeline.csv'):
            self.assertTrue(r['locator']);self.assertTrue(r['page_url'])

    def test_memphis_sensitivity_denominators_and_folds(self):
        rows=read(D/'tables/analysis_rows.csv');mem={r['player_id'] for r in rows if r['team']=='MEM'}
        for s in read(D/'tables/fold_counts.csv'):
            selected=[r for r in rows if r['lag']==s['lag'] and (s['sensitivity']=='all' or r['player_id'] not in mem) and ((int(r['fold'])==int(s['fold']))==(s['role']=='test'))]
            self.assertEqual(len(selected),int(s['rows']))

    def test_artifact_hashes_and_no_estimators(self):
        for name,h in json.loads((D/'artifact_hashes.json').read_text()).items():
            self.assertEqual(hashlib.sha256((D/name).read_bytes()).hexdigest(),h,name)
        for p in D.glob('*.py'):
            self.assertNotIn('.fit(',p.read_text())
        status=json.loads((D/'dry_run.json').read_text());self.assertEqual(status['models_fitted'],0)
        self.assertEqual(status['preprocessing_fitted'],0);self.assertFalse(status['protected_periods_accessed'])

if __name__=='__main__':unittest.main()
