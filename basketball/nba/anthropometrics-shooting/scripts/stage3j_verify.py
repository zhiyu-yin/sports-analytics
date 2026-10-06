"""Final verification preserves the observed failed J2 numerical gate."""
from stage3j_core import *
import io,unittest,os,contextlib

def main():
 p=authorize(True);os.environ['STAGE3J_FINAL']='1';sys.path.insert(0,str(ROOT/'tests'))
 import test_stage3j
 test_stage3j.FINAL=True
 suite=unittest.defaultTestLoader.loadTestsFromModule(test_stage3j);stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (E/'test_run.txt').write_text(stream.getvalue())
 failed_names=[x.id() for x,_ in result.failures];error_names=[x.id() for x,_ in result.errors]
 save('test_summary.json',dict(tests=result.testsRun,passed=result.testsRun-len(result.failures)-len(result.errors),failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),failed_tests=failed_names,error_tests=error_names,finished_at=now(),all_passed=result.wasSuccessful()))
 # Artifact checks are independent of the bootstrap numerical success criterion.
 required=['analysis_protocol.json','panel_verification.json','j1_model_coefficients.csv','j1_cluster_covariance.json','j1_cluster_validation.json','j1_player_bootstrap.csv','j1_bootstrap_summary.json','primary_result.json','j2_beta_binomial_result.json','j2_player_bootstrap.csv','j2_bootstrap_summary.json','j3_first_season_result.json','j4_player_balanced_result.json','j5_leave_one_season_out.csv','j6_fta_thresholds.csv','alternate_exposures.csv','full_panel_secondary_result.json','residual_diagnostics_by_fta_bin.csv','selection_coverage_by_season.csv','test_run.txt','test_summary.json']
 for n in required:assert (E/n).is_file(),n
 assert sha(E/'selection_coverage_by_season.csv')==sha(ROOT/'docs/stage3_evidence/selection_coverage_by_season.csv')
 j=read(E/'primary_result.json');j2=read(E/'j2_beta_binomial_result.json');assert j2['ci_low'] is None and j2['ci_high'] is None and not j2['bootstrap_interval_reportable']
 f=pd.read_csv(E/'j5_leave_one_season_out.csv');assert len(f)==13 and sorted(f.omitted_season)==p['seasons'];assert f.converged.all()
 coefficients=pd.read_csv(E/'j1_model_coefficients.csv');assert len(coefficients)==28;rw=coefficients[coefficients.term=='residual_wingspan'].iloc[0];assert abs(rw.beta-j['beta'])<1e-14
 for tag,seed in [('j1',20260930),('j2',20260931)]:
  boot=pd.read_csv(E/(tag+'_player_bootstrap.csv'));assert len(boot)==2000;assert boot.replicate.tolist()==list(range(1,2001));assert set(boot.status)<= {'PASS','FAIL'};assert boot.loc[boot.status=='FAIL','error'].notna().all()
  summary=read(E/(tag+'_bootstrap_summary.json'));actual=boot_summary(boot,seed)
  assert summary['failed']==actual['failed'];np.testing.assert_allclose([summary['mean'],summary['SD'],*summary['percentile_CI']],[actual['mean'],actual['SD'],*actual['percentile_CI']],rtol=1e-12,atol=1e-14)
 # Exact protocol audit: only timestamp/test file hash changed during prefit correction.
 original=read(E/'preflight_initial_analysis_protocol.json');final=read(E/'analysis_protocol.json')
 for item in [original,final]:item.pop('frozen_at');item['frozen_code'].pop('tests/test_stage3j.py')
 assert original==final
 assert failed_names==['test_stage3j.TestStage3J.test_R_full_clusters_seed_and_failure_policy'] and not error_names,'Unexpected verification failure'
 report=ROOT/'docs/stage3j_simplified_multiseason_inference.md';assert sum(x.startswith('## ') for x in report.read_text().splitlines())==27
 save('artifact_verification.json',dict(passed=True,required_artifacts_checked=len(required),historical_artifacts_verified=len(read(E/'prior_preservation_manifest.json')),protocol_scientific_fields_unchanged=True,primary_result_unchanged=True,coverage_exact_copy=True,J2_invalid_interval_withheld=True,all_4000_scheduled_replicates_recorded=True,all_13_season_omissions_recorded=True,report_sections=27,verified_at=now()))
 save('execution_decision.json',dict(execution='FAIL',tests=25,tests_passed=24,reason='J2 player-bootstrap exceeds frozen numerical failure cap; its interval is withheld. J1 and every other required sensitivity completed.',primary_J1_execution='PASS',J1_bootstrap_failures=0,J2_bootstrap_failures=j2['bootstrap']['failed'],scientific_direction_not_a_gate=True,post_result_model_tuning=False,decision_at=now()))
 print(stream.getvalue());print('Stage 3J FAIL: J2 numerical bootstrap gate; primary J1 PASS',flush=True)
if __name__=='__main__':main()
