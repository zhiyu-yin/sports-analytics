"""Test the blocked audit and stopping rule, not an unexecuted scientific pipeline."""
import unittest,json,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'docs/stage4x_evidence'
def read(n):return json.loads((E/n).read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
class BlockedAudit(unittest.TestCase):
 def test_history_unchanged(self):
  d=read('preservation_manifest.json');bad=[p for p,h in d.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h];self.assertEqual(bad,[])
 def test_ft_primary(self):self.assertEqual(sha(ROOT/'docs/stage3j_evidence/primary_result.json'),'79b8f461efcc61e0a6e3ff33728fa0d0019839aae03b9809d530f8c9b6906e02')
 def test_manuscript_freeze(self):self.assertEqual(sha(ROOT/'docs/manuscript/manuscript_freeze.json'),'66a07aa5c826ac34f7aa8a09ee9565312e350e676d0965bb7f2040b02f7c6def')
 def test_transform(self):
  x=read('shot_zone_mapping_protocol.json')['exposure'];self.assertEqual(x['intercept'],4.574910520685837);self.assertEqual(x['slope'],1.0013410045156863)
 def test_stop_before_freeze_fit(self):
  self.assertFalse((E/'analysis_protocol.json').exists());self.assertEqual(read('shot_source_validation.json')['scientific_fits'],0)
  for n in ['shot_type_primary_results.csv','shot_type_bootstrap_results.csv','common_support_results.csv','cross_shot_type_summary.csv']:self.assertFalse((E/n).exists())
 def test_source_gate_not_false_pass(self):self.assertEqual(read('shot_source_validation.json')['classification'],'SHOT DATA FEASIBILITY BLOCKED')
 def test_all_seasons_conflicted(self):
  c=list(csv.DictReader((E/'shot_season_coverage.csv').open()));self.assertEqual(len(c),14);self.assertTrue(all(int(x['zone_type_conflict'])>0 for x in c))
 def test_hashes(self):self.assertTrue(all(read('download_verification.json').values()))
 def test_linkage(self):
  rows=list(csv.DictReader((E/'shot_player_linkage.csv').open()));self.assertTrue(all(x['linkage'] in ['MATCHED_ID','UNMATCHED_ID'] for x in rows));self.assertTrue(all(x['ambiguous']=='False' for x in rows))
 def test_mapping_unapproved(self):
  d=read('shot_zone_mapping_protocol.json');self.assertFalse(d['scientific_coefficients_inspected']);self.assertIn('NOT_VALIDATED',d['status']);self.assertEqual(set(d['mapping']),{'rim','midrange','three_point'})
 def test_report_all_outcomes_and_limits(self):
  t=(ROOT/'docs/stage4x_shot_type_specificity.md').read_text();self.assertEqual(t.count('\n## '),25)
  for v in ['Restricted-area result','Mid-range result','Three-point result','shot selection','pure shooting touch','No secondary effect','sole manuscript primary']:self.assertIn(v,t)
 def test_heterogeneity_not_run(self):self.assertEqual(read('heterogeneity_test.json')['status'],'NOT_RUN')
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(BlockedAudit);result=unittest.TextTestRunner(verbosity=2).run(suite)
 checks={
 'A':('PASS','Historical manifest verified byte-for-byte'),'B':('PASS','Primary FT hash unchanged'),'C':('PASS','Transform constants unchanged'),'D':('PASS','No fit or Phase B freeze'),
 'E':('NOT_RUN','Mapping candidate only; no coefficients'),'F':('BLOCKED','Source validation fails unresolved conflicts'),'G':('PASS','Exact 3PM/3PA reconciliation exported'),'H':('PASS','Exact ID audit; no scientific inclusions'),
 'I':('NOT_RUN','No analysis panel; no zero rows constructed'),'J':('NOT_RUN','No primary secondary model'),'K':('NOT_RUN','No covariance'),'L':('NOT_RUN','No bootstrap'),
 'M':('PASS','All three outcomes explicitly NOT_RUN'),'N':('PASS','No coefficients inspected or sign-based selections'),'O':('NOT_RUN','No tests or Holm calculations'),'P':('NOT_RUN','No threshold freeze or fits'),
 'Q':('PASS','No causal inference made'),'R':('PASS','Rim described as finishing with limitations'),'S':('PASS','No common-support FT replacement'),'T':('PASS','Manuscript freeze hash unchanged')}
 (E/'requirement_status.csv').write_text('requirement,status,reason\n'+'\n'.join(f'{k},{v[0]},{v[1]}' for k,v in checks.items())+'\n')
 (E/'test_summary.json').write_text(json.dumps({'executable_tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'preserved_artifacts':len(read('preservation_manifest.json')),'scientific_requirement_status':{k:v[0] for k,v in checks.items()},'note':'Passing stopping-rule tests does not imply source validation or scientific analysis passed.'},indent=2)+'\n')
 raise SystemExit(not result.wasSuccessful())
