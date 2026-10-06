"""Deterministic numerical polishing of the unchanged three-start J2 objective."""
from stage3jr_common import *
from stage3jr_validation import information
from scipy.optimize import minimize,root
SCORE_GATE=1e-3

def accepted(opt,s):
 value,score=old.objective(opt.x,s['z'],s['y'],s['n'])
 return bool(opt.success and np.isfinite(value) and np.isfinite(score).all() and np.max(np.abs(score))<SCORE_GATE and -9.99<opt.x[-1]<15.99)
def polish(s,starts):
 z,y,n=s['z'],s['y'],s['n'];solutions=[];attempts=[]
 for k,start in zip([10.,50.,200.],starts):
  success=None
  # Always apply numerical polishing, including to endpoints that previously passed.
  for method in ['Newton-CG','hybr','trust-exact','lm']:
   if method in ['hybr','lm']:
    opt=root(lambda t:old.objective(t,z,y,n)[1],start,jac=lambda t:information(t,z,y,n),method=method,options=({'xtol':1e-10,'maxfev':500} if method=='hybr' else {'ftol':1e-12,'xtol':1e-12,'gtol':1e-12,'maxiter':500}))
   else:
    options={'maxiter':200,'xtol':1e-10} if method=='Newton-CG' else {'maxiter':200,'gtol':1e-7}
    opt=minimize(old.objective,start,args=(z,y,n),jac=True,hess=information,method=method,options=options)
   value,score=old.objective(opt.x,z,y,n);ok=accepted(opt,s)
   attempts.append(dict(start_kappa=k,method=method,success=bool(opt.success),status=int(opt.status),message=str(opt.message),iterations=int(getattr(opt,'nit',-1)),function_evaluations=int(opt.nfev),log_likelihood=-float(value),score_max=float(np.max(np.abs(score))),accepted=ok))
   if ok:success=opt;break
  if success is None:return dict(passed=False,reason='No ladder method passes unchanged optimizer/score/boundary gate',attempts=attempts),None
  solutions.append(success)
 values=[old.objective(o.x,z,y,n)[0] for o in solutions];spread=float(np.ptp(values));distance=float(np.max(np.ptp(np.array([o.x for o in solutions]),axis=0)))
 if spread>1e-5:return dict(passed=False,reason='Three starts disagree in likelihood',attempts=attempts,likelihood_spread=spread),None
 if distance>1e-4:return dict(passed=False,reason='Near-equal likelihood but differing parameters: identification flag',attempts=attempts,parameter_spread=distance),None
 best=solutions[int(np.argmin(values))];theta=best.x;H=old.hessian(theta,z,y,n);eigen=np.linalg.eigvalsh(H)
 if not np.isfinite(H).all() or eigen.min()<=0:return dict(passed=False,reason='Nonpositive or nonfinite observed information',attempts=attempts),None
 joint_cov=np.linalg.inv(H);T=s['T'];cov=T@joint_cov[:-1,:-1]@T.T
 H2=old.hessian(theta,z,y,n,step=5e-5);cov2=T@np.linalg.inv(H2)[:-1,:-1]@T.T;difference=float(np.max(np.abs(np.diag(cov2)/np.diag(cov)-1)))
 if not np.isfinite(cov).all() or difference>1e-3:return dict(passed=False,reason='Covariance nonfinite or Hessian step instability',attempts=attempts),None
 beta=T@theta[:-1];scores=[float(np.max(np.abs(old.objective(o.x,z,y,n)[1]))) for o in solutions]
 return dict(passed=True,reason='',attempts=attempts,log_likelihood=-min(values),score_max=max(scores),best_score_max=float(np.max(np.abs(old.objective(theta,z,y,n)[1]))),likelihood_spread=spread,parameter_spread=distance,min_information_eigenvalue=float(eigen.min()),information_condition=float(eigen.max()/eigen.min()),hessian_step_relative_difference=difference,finite_covariance=True,kappa=float(np.exp(theta[-1])),methods='|'.join(str(a['method']) for a in attempts if a['accepted'])),dict(theta=theta,beta=beta,cov=cov)
def protocol():
 p=read(E/'numerical_protocol.json');assert sha(E/'numerical_protocol.json')==read(E/'numerical_freeze_receipt.json')['sha256']
 for name,h in p['code_hashes'].items():assert sha(ROOT/name)==h,name
 return p
