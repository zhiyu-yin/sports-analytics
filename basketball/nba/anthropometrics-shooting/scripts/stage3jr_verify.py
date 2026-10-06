"""Final A-T tests plus complete artifact and gate checks."""
from stage3jr_solver import *
import io,unittest,os,sys

def main():
 protocol();os.environ['STAGE3JR_FINAL']='1';sys.path.insert(0,str(ROOT/'tests'));import test_stage3jr;test_stage3jr.FINAL=True
 stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_stage3jr))
 (E/'test_run.txt').write_text(stream.getvalue());save('test_summary.json',dict(passed=r.wasSuccessful(),tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped),finished_at=now(),log_sha256=sha(E/'test_run.txt')),immutable=False)
 assert r.wasSuccessful(),stream.getvalue()
 for f,h in read(E/'ladder_v1_preservation.json')['files'].items():assert sha(ROOT/f)==h,f
 final=read(E/'numerical_protocol.json');original=read(E/'ladder_v1/numerical_protocol.json');assert final['acceptance']==original['acceptance'];assert final['formula']==original['formula'];assert final['scaling']==original['scaling'];assert final['starts']==original['starts'];assert final['warm_start_rule']==original['warm_start_rule']
 assert final['frozen_at']<read(E/'retry_start.json')['started_at'];assert read(E/'failed_retry_summary.json')['completed_at']<read(E/'final_algorithm_receipt.json')['frozen_at'];assert read(E/'final_algorithm_receipt.json')['frozen_at']<read(E/'full_execution_receipt.json')['completed_at']
 rows=pd.read_csv(E/'full_bootstrap_results.csv');passed=rows[rows.passed];assert len(rows)==2000
 assert (passed.score_max<.001).all();assert (passed.likelihood_spread<=1e-5).all();assert (passed.min_information_eigenvalue>0).all();assert (passed.hessian_step_relative_difference<=.001).all();assert passed.finite_covariance.all();assert np.isfinite(passed.log_likelihood).all()
 assert ((np.log(passed.kappa)>-9.99)&(np.log(passed.kappa)<15.99)).all()
 count=0
 for rep in range(1,2001):
  raw=read(M/f'full_{rep:04d}_diagnostics.json');v=raw['remediated']
  if v['passed']:
   successful=[a for a in v['attempts'] if a['accepted']];assert len(successful)==3
   assert [a['start_kappa'] for a in successful]==[10.,50.,200.]
   assert all(a['success'] and a['score_max']<.001 for a in successful)
   count+=1
 decision=read(E/'stage3jr_decision.json');assert count==decision['successful'];assert sha(E/'full_bootstrap_results.csv')==decision['full_results_sha256']
 summary=read(E/'full_bootstrap_summary.json')
 if summary['status']=='RELEASED_AFTER_NUMERICAL_DECISION':
  b=pd.read_csv(E/'released_bootstrap_coefficients.csv');assert len(b)==2000 and b.beta_RW.notna().all();assert b.sample_sha256.tolist()==rows.sample_sha256.tolist()
  v=b.beta_RW.to_numpy();np.testing.assert_allclose([summary['mean'],summary['SD'],*summary['percentile_CI'],summary['fraction_beta_negative']],[v.mean(),v.std(ddof=1),*np.quantile(v,[.025,.975],method='linear'),(v<0).mean()],rtol=1e-12,atol=1e-14)
 report=ROOT/'docs/stage3jr_beta_binomial_numerical_remediation.md';assert sum(s.startswith('## ') for s in report.read_text().splitlines())==15
 required=['numerical_protocol.json','failed_replicate_diagnostics.csv','failure_summary.json','likelihood_validation.json','gradient_validation.json','scaling_equivalence.json','remediation_ladder.json','failed_replicate_retry_results.csv','failed_retry_summary.json','full_bootstrap_results.csv','full_bootstrap_summary.json','old_vs_new_successful_fit_comparison.json','stage3jr_decision.json','test_run.txt','test_summary.json']
 for n in required:assert (E/n).is_file(),n
 save('artifact_verification.json',dict(passed=True,verified_at=now(),historical_artifacts=len(read(E/'prior_preservation_manifest.json')),initial_numerical_trial_preserved=True,numerical_acceptance_unchanged_across_amendment=True,all_2000_original_sample_ids_present=True,all_6000_accepted_start_gates_verified=count==2000,required_outputs_checked=len(required),report_sections=15,summary_recomputed_without_dropping_draws=summary['status']=='RELEASED_AFTER_NUMERICAL_DECISION'),immutable=False)
 print(stream.getvalue());print('Final numerical and artifact verification PASS',flush=True)
if __name__=='__main__':main()
