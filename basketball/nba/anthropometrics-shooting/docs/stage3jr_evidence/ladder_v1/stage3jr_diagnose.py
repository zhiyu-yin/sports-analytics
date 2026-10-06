"""Reference-only diagnostic replay before numerical remedy implementation."""
from stage3jr_common import *
import ast

def main():
 plan=read(E/'diagnostic_plan.json');bundle=inputs();oldrecords=pd.read_csv(J/'j2_player_bootstrap.csv',usecols=['replicate','status','error']).set_index('replicate');out=[];attempts=[]
 for index,rep in enumerate(plan['failed_replicates']+plan['successful_comparison_replicates']):
  s=sample(bundle,rep);r=reference(s);assert r['status']==oldrecords.loc[rep,'status'],f'R0 replay status changed {rep}'
  if r['status']=='FAIL':
   msg=ast.literal_eval(oldrecords.loc[rep,'error'][len('RuntimeError('):-1]);recorded=ast.literal_eval(msg.split(': ',1)[1])
   for a,b in zip(r['attempts'],recorded):
    assert a['optimizer_success']==b['success'];assert abs(a['log_likelihood']+b['negative_log_likelihood'])<1e-8;assert abs(a['score_max']-b['score_max'])<1e-8
  (M/f'diagnostic_{rep:04d}.json').write_text(json.dumps(clean(r),indent=2)+'\n')
  a=r['attempts'];worst=max(a,key=lambda a:a['score_max'])
  item=dict(replicate=rep,original_status=r['status'],sample_sha256=r['sample_sha256'],**worst,any_optimizer_termination_failure=any(not t['optimizer_success'] for t in a),score_tolerance_failure=any(not t['score_gate_pass'] for t in a),Hessian_failure=any(t['minimum_information_eigenvalue']<=0 for t in a),parameter_scaling_issue=False,likelihood_spread=float(np.ptp([t['log_likelihood'] for t in a])),all_starts_diagnostics_file=f'models/stage3jr/diagnostic_{rep:04d}.json')
  item['score_tolerance_only']=item['score_tolerance_failure'] and not item['any_optimizer_termination_failure'];out.append(item)
  attempts.extend([dict(replicate=rep,original_status=r['status'],**a) for a in r['attempts']])
  if (index+1)%25==0:print('Reference diagnostics',index+1,'/399',flush=True)
 df=pd.DataFrame(out);df[df.original_status=='FAIL'].to_csv(E/'failed_replicate_diagnostics.csv',index=False);df[df.original_status=='PASS'].to_csv(E/'successful_replicate_diagnostics.csv',index=False);pd.DataFrame(attempts).to_csv(E/'reference_start_diagnostics.csv',index=False)
 summary={}
 for status,g in df.groupby('original_status'):
  summary[status]=dict(n=len(g),optimizer_termination_failures=int(g.any_optimizer_termination_failure.sum()),score_failures=int(g.score_tolerance_failure.sum()),score_only=int(g.score_tolerance_only.sum()),Hessian_failures=int(g.Hessian_failure.sum()),boundary=int(g.boundary.sum()),nonfinite=int(g.nonfinite.sum()),separation_like=int(g.separation_like.sum()),absent_category=int(g.absent_category.sum()),raw_condition_range=[float(g.raw_condition.min()),float(g.raw_condition.max())],scaled_condition_range=[float(g.scaled_condition.min()),float(g.scaled_condition.max())],max_score=float(g.score_max.max()),max_likelihood_spread=float(g.likelihood_spread.max()),median_iterations=float(g.iterations.median()),kappa_range=[float(g.kappa.min()),float(g.kappa.max())])
 save('failure_summary.json',dict(completed_at=now(),original_failures=299,reference_status_and_recorded_diagnostics_reproduced=True,groups=summary,interpretation='Diagnose numerical termination/score criteria only. No exposure-coefficient distribution or sign used. Raw conditioning is reduced by the already-existing Stage 2 scaling; no separation or boundary inference from scientific coefficient direction.'))
 print(json.dumps(clean(summary)),flush=True)
if __name__=='__main__':main()
