"""Diagnose frozen J2 optimizer failures without changing or replacing any fit."""
from stage3j_core import *
from stage2_models import objective,hessian

def main():
 p=authorize(True)
 f=pd.read_csv(E/'j2_player_bootstrap.csv');fail=f[f.status=='FAIL'];assert len(fail)>20
 # The exact original estimator, unchanged, to persist its otherwise delayed result.
 d=load();positive=d[d.fta>0];m,x,_=glm(design(positive,p),positive.ftm,positive.fta)
 fit=fit_bb(x,positive.ftm,positive.fta,np.asarray(m.params),maxiter=3000)
 save('j2_original_fit_audit.json',dict(beta=fit['beta'][1],odds_ratio=np.exp(fit['beta'][1]),kappa=fit['kappa'],rho=fit['rho'],attempts=fit['attempts'],converged=True,**counts(d),status='Original fit valid; bootstrap uncertainty awaiting completion / numerical gate',same_frozen_estimator=True,recorded_at=now()),True)
 # Read errors only; no repair, no extra RNG draws, no coefficient selection.
 import ast
 failures=[]
 for _,row in fail.iterrows():
  error=row.error;item=dict(replicate=int(row.replicate),error=error)
  if 'BB convergence failure: ' in error:
   # Error string is repr(RuntimeError(message)); only parse literal data.
   message=ast.literal_eval(error[len('RuntimeError('):-1])
   attempts=ast.literal_eval(message.split('BB convergence failure: ',1)[1])
   item.update(all_optimizer_success=all(a['success'] for a in attempts),max_score=max(a['score_max'] for a in attempts),likelihood_spread=max(a['negative_log_likelihood'] for a in attempts)-min(a['negative_log_likelihood'] for a in attempts))
  failures.append(item)
 # Analytic likelihood derivative check at fixed synthetic parameters; no optimizing change.
 rng=np.random.default_rng(901);x=np.column_stack([np.ones(4000),rng.normal(size=(4000,3))]);n=rng.integers(10,500,4000);mu=1/(1+np.exp(-x@np.array([1.,-.1,.2,.1])));y=rng.binomial(n,rng.beta(mu*30,(1-mu)*30));theta=np.array([1.,-.1,.2,.1,np.log(30.)]);value,grad=objective(theta,x,y,n)
 numeric=[]
 for j in range(len(theta)):
  delta=np.zeros(len(theta));delta[j]=1e-5
  numeric.append((objective(theta+delta,x,y,n)[0]-objective(theta-delta,x,y,n)[0])/2e-5)
 error=float(np.max(np.abs(grad-numeric)))
 save('j2_numerical_investigation.json',dict(recorded_at=now(),replicates_seen=len(f),failures_seen=len(fail),frozen_score_threshold=.001,diagnosis='Absolute score rejection after relative objective convergence in larger repeated-season bootstrap samples; near-identical start likelihoods do not override the frozen all-start score gate.',synthetic_4000_row_gradient_max_absolute_error=error,optimizer_or_tolerance_changed=False,failed_replicates_replaced=False,interval_action='Withhold J2 bootstrap interval if final failure count exceeds 20. Primary result remains immutable. No recovery tuning authorized in frozen Stage 3J.',examples=failures[:10]),True)
 print('Numerical audit saved; no optimizer or model change',flush=True)
if __name__=='__main__':main()
