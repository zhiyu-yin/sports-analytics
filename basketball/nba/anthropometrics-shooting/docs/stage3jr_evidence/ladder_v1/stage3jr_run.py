"""Ordered failed-only retry, uniform full rerun, decision, then scientific summary."""
from stage3jr_solver import *
import sys

def retry():
 p=protocol();assert read(E/'preflight_test_summary.json')['passed'];assert not (E/'failed_retry_summary.json').exists();bundle=inputs();out=[]
 save('retry_start.json',dict(started_at=now(),protocol_sha256=sha(E/'numerical_protocol.json')))
 for i,rep in enumerate(p['failed_first']):
  s=sample(bundle,rep);starts=np.load(M/f'reference_{rep:04d}.npz')['theta'];r,fit=polish(s,starts)
  (M/f'retry_{rep:04d}_diagnostics.json').write_text(json.dumps(clean(r),indent=2)+'\n')
  if fit is not None:np.savez(M/f'retry_{rep:04d}.npz',**fit)
  row={k:v for k,v in r.items() if k!='attempts'};row.update(replicate=rep,sample_sha256=s['sample_sha256']);out.append(row)
  if (i+1)%25==0:print('Failed-only retry',i+1,'/299; unresolved',sum(not x['passed'] for x in out),flush=True)
 pd.DataFrame(out).to_csv(E/'failed_replicate_retry_results.csv',index=False);fail=sum(not x['passed'] for x in out)
 save('failed_retry_summary.json',dict(completed_at=now(),original_failures=299,repaired=299-fail,remaining_failures=fail,eligible_for_full_rerun=fail<=20,uniform_algorithm='Exact frozen R0 + per-start R1/R2/R3 polishing',beta_distribution_summarized=False))
 print('Failed-only retry:',299-fail,'repaired;',fail,'remaining',flush=True)

def full():
 p=protocol();assert read(E/'failed_retry_summary.json')['eligible_for_full_rerun'];assert not (E/'full_bootstrap_results.csv').exists()
 save('final_algorithm_receipt.json',dict(frozen_at=now(),protocol_sha256=sha(E/'numerical_protocol.json'),algorithm='Entire unchanged deterministic R0/R1/R2/R3 procedure; same for every sample',code_hashes=p['code_hashes'],selection_basis='Frozen before retry; full rerun authorized by numeric failure count only'))
 bundle=inputs();historical=pd.read_csv(J/'j2_player_bootstrap.csv',usecols=['replicate','status','beta']).set_index('replicate');out=[];comparison=[]
 for rep in range(1,2001):
  s=sample(bundle,rep);r0=reference(s,prefix='full_reference');assert r0['status']==historical.loc[rep,'status'],f'R0 reproduction mismatch {rep}'
  original=np.load(M/f'full_reference_{rep:04d}.npz');r,fit=polish(s,original['theta'])
  (M/f'full_{rep:04d}_diagnostics.json').write_text(json.dumps(clean(dict(reference=r0,remediated=r)),indent=2)+'\n')
  if fit is not None:np.savez(M/f'full_{rep:04d}.npz',**fit)
  row={k:v for k,v in r.items() if k!='attempts'};row.update(replicate=rep,sample_sha256=s['sample_sha256'],original_status=r0['status']);out.append(row)
  if r0['status']=='PASS' and fit is not None:
   old_b=float(original['beta'][1]);saved_b=float(historical.loc[rep,'beta']);assert abs(old_b-saved_b)<1e-10
   best=min(r0['attempts'],key=lambda a:-a['log_likelihood'])
   comparison.append(dict(replicate=rep,beta_absolute_difference=abs(float(fit['beta'][1])-old_b),loglik_absolute_difference=abs(r['log_likelihood']-best['log_likelihood']),score_absolute_difference=abs(r['best_score_max']-best['score_max']),old_replay_beta_difference=abs(old_b-saved_b)))
  if rep%50==0:print('Uniform full rerun',rep,'/2000; failures',sum(not x['passed'] for x in out),flush=True)
 pd.DataFrame(out).to_csv(E/'full_bootstrap_results.csv',index=False)
 pd.DataFrame(comparison).to_csv(E/'old_vs_new_successful_fit_comparison.csv',index=False)
 c=pd.DataFrame(comparison);v=dict(compared=len(c),max_absolute_beta_difference=float(c.beta_absolute_difference.max()),max_log_likelihood_difference=float(c.loglik_absolute_difference.max()),max_score_difference=float(c.score_absolute_difference.max()),max_old_success_replay_beta_difference=float(c.old_replay_beta_difference.max()))
 v['passed']=bool(v['compared']==1701 and v['max_absolute_beta_difference']<=1e-5 and v['max_log_likelihood_difference']<=1e-7 and v['max_score_difference']<=.0011)
 save('old_vs_new_successful_fit_comparison.json',dict(**v,completed_at=now(),interpretation='Score differences primarily reflect polishing toward zero; coefficient/loglik agreement evaluated separately.'))
 save('full_execution_receipt.json',dict(completed_at=now(),samples=2000,failed=sum(not x['passed'] for x in out),uniform_algorithm=True,scientific_summary_generated=False))
 print('Full uniform rerun complete',flush=True)

def reproduce():
 protocol();bundle=inputs();out=[]
 for rep in [1,9,13]:
  s=sample(bundle,rep);reference(s,prefix='replay_reference');r,fit=polish(s,np.load(M/f'replay_reference_{rep:04d}.npz')['theta']);saved=np.load(M/f'full_{rep:04d}.npz');assert r['passed'];error=float(np.max(np.abs(saved['beta']-fit['beta'])));assert error<1e-10
  out.append(dict(replicate=rep,sample_sha256=s['sample_sha256'],max_coefficient_difference=error))
 save('reproduction_check.json',dict(passed=True,completed_at=now(),checks=out))

def decision():
 p=protocol();rows=pd.read_csv(E/'full_bootstrap_results.csv');schedule=pd.read_csv(J/'j2_complete_sample_schedule.csv');assert rows.replicate.tolist()==list(range(1,2001));assert rows.sample_sha256.tolist()==schedule.sample_sha256.tolist();fail=int((~rows.passed).sum())
 history=read(E/'prior_preservation_manifest.json')
 for f,h in history.items():assert sha(ROOT/f)==h,f
 compare=read(E/'old_vs_new_successful_fit_comparison.json');reproduction=read(E/'reproduction_check.json');numeric=bool(fail<=20 and compare['passed'] and reproduction['passed'])
 save('stage3jr_decision.json',dict(classification='NUMERICAL REMEDIATION PASS' if numeric else 'NUMERICAL REMEDIATION UNRESOLVED',decision_at=now(),failed=fail,successful=2000-fail,samples=2000,original_Stage3J_execution='FAIL',original_Stage3J_failures=299,original_score_tolerance=.001,score_tolerance_unchanged=True,likelihood_unchanged=True,formula_unchanged=True,samples_unchanged=True,J1_unchanged=True,uniform_algorithm=True,comparison_pass=compare['passed'],reproduction_pass=reproduction['passed'],summary_authorized=bool(numeric and fail==0),summary_policy='Never exclude failed samples from interval; require 2000/2000 finite estimates to publish full-sample percentile',protocol_sha256=sha(E/'numerical_protocol.json'),final_algorithm_sha256=sha(E/'final_algorithm_receipt.json'),full_results_sha256=sha(E/'full_bootstrap_results.csv'),historical_artifacts=len(history)))
 save('decision_freeze_receipt.json',dict(frozen_at=now(),sha256=sha(E/'stage3jr_decision.json')))
 print('Numerical acceptance decision frozen; failures',fail,flush=True)

def summary():
 protocol();assert sha(E/'stage3jr_decision.json')==read(E/'decision_freeze_receipt.json')['sha256'];d=read(E/'stage3jr_decision.json')
 if not d['summary_authorized']:
  save('full_bootstrap_summary.json',dict(status='WITHHELD',failed=d['failed'],reason='Numerical acceptance incomplete or at least one missing bootstrap estimate; no successful-only interval'));return
 values=np.array([np.load(M/f'full_{rep:04d}.npz')['beta'][1] for rep in range(1,2001)]);assert np.isfinite(values).all()
 # Separate release CSV preserves the numeric-only full-results hash in the decision.
 rows=pd.read_csv(E/'full_bootstrap_results.csv');rows['beta_RW']=values;rows.to_csv(E/'released_bootstrap_coefficients.csv',index=False)
 s=dict(status='RELEASED_AFTER_NUMERICAL_DECISION',generated_at=now(),decision_sha256=sha(E/'stage3jr_decision.json'),replicates=2000,successful=2000,failed=0,mean=float(values.mean()),SD=float(values.std(ddof=1)),percentile_CI=np.quantile(values,[.025,.975],method='linear').tolist(),fraction_beta_negative=float((values<0).mean()),percentile_method='linear',J2_secondary_only=True)
 save('full_bootstrap_summary.json',s);print(json.dumps(s),flush=True)
if __name__=='__main__':{'retry':retry,'full':full,'reproduce':reproduce,'decision':decision,'summary':summary}[sys.argv[1]]()
