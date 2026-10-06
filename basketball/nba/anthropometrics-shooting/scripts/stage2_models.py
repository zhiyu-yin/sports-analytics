"""Validated beta-binomial regression and grouped-score sandwich helpers.

log f(y|n,mu,k) = log choose(n,y) + betaln(y+mu*k,n-y+(1-mu)*k)
                 - betaln(mu*k,(1-mu)*k).
Score obtained by differentiating betaln with digamma; observed information
by central differences of this analytic score. No hand-written optimizer.
"""
import numpy as np
from scipy.special import expit, betaln, gammaln, digamma
from scipy.optimize import minimize
from scipy.stats import norm

Z=norm.ppf(.975)
def valid_counts(y,n):
    y=np.asarray(y,float); n=np.asarray(n,float)
    if not (np.isfinite(y).all() and np.isfinite(n).all() and (y>=0).all() and (n>=y).all() and (n>0).all() and (y==np.floor(y)).all() and (n==np.floor(n)).all()): raise ValueError('invalid grouped counts')
    return y,n

def logpmf(y,n,mu,k):
    a=mu*k; b=(1-mu)*k
    return gammaln(n+1)-gammaln(y+1)-gammaln(n-y+1)+betaln(y+a,n-y+b)-betaln(a,b)

def objective(theta,x,y,n):
    mu=expit(x@theta[:-1]); k=np.exp(theta[-1]); a=mu*k; b=(1-mu)*k
    if not ((a>0).all() and (b>0).all()): return np.inf,np.full(len(theta),np.nan)
    common=digamma(k)-digamma(n+k)
    da=digamma(y+a)-digamma(a)+common
    db=digamma(n-y+b)-digamma(b)+common
    score_beta=x.T@((da-db)*k*mu*(1-mu))
    score_logk=np.sum(da*a+db*b)
    return -float(logpmf(y,n,mu,k).sum()),-np.r_[score_beta,score_logk]

def hessian(theta,x,y,n,step=1e-4):
    out=np.empty((len(theta),len(theta)))
    for j in range(len(theta)):
        delta=np.zeros(len(theta)); delta[j]=step*max(1,abs(theta[j]))
        out[:,j]=(objective(theta+delta,x,y,n)[1]-objective(theta-delta,x,y,n)[1])/(2*delta[j])
    return (out+out.T)/2

def fit_bb(x,y,n,start_beta,maxiter=3000):
    y,n=valid_counts(y,n); raw=np.asarray(x,float); names=list(x.columns) if hasattr(x,'columns') else [str(i) for i in range(raw.shape[1])]
    if np.linalg.matrix_rank(raw)!=raw.shape[1]: raise ValueError('singular design')
    means=raw.mean(axis=0); scales=raw.std(axis=0); means[0]=0; scales[0]=1
    z=(raw-means)/scales
    transform=np.diag(1/scales); transform[0,:]=-means/scales; transform[0,0]=1
    initial=np.linalg.solve(transform,np.asarray(start_beta))
    attempts=[]; candidates=[]
    for k in [10.,50.,200.]:
        opt=minimize(objective,np.r_[initial,np.log(k)],args=(z,y,n),jac=True,method='L-BFGS-B',bounds=[(None,None)]*raw.shape[1]+[(-10,16)],options={'maxiter':maxiter,'ftol':1e-14,'gtol':1e-7,'maxls':50})
        score=float(np.max(np.abs(objective(opt.x,z,y,n)[1])))
        ok=bool(opt.success and score<1e-3 and -9.99<opt.x[-1]<15.99)
        attempts.append(dict(start_kappa=k,success=bool(opt.success),accepted=ok,message=str(opt.message),negative_log_likelihood=float(opt.fun),score_max=score,iterations=int(opt.nit)))
        if ok: candidates.append(opt)
    if len(candidates)!=3: raise RuntimeError(f'BB convergence failure: {attempts}')
    if np.ptp([o.fun for o in candidates])>1e-5: raise RuntimeError('BB starts disagree')
    best=min(candidates,key=lambda o:o.fun); info=hessian(best.x,z,y,n)
    eigen=np.linalg.eigvalsh(info)
    if eigen.min()<=0: raise RuntimeError('BB nonpositive observed information')
    covariance=np.linalg.inv(info); beta=transform@best.x[:-1]; cov=transform@covariance[:-1,:-1]@transform.T
    h2=hessian(best.x,z,y,n,step=5e-5); c2=transform@np.linalg.inv(h2)[:-1,:-1]@transform.T
    relative=float(np.max(np.abs(np.diag(c2)/np.diag(cov)-1)))
    if relative>1e-3: raise RuntimeError('BB Hessian step instability')
    k=float(np.exp(best.x[-1])); rho=1/(1+k); ll=-float(best.fun)
    return dict(beta=beta,cov=cov,kappa=k,rho=rho,log_kappa_se=float(np.sqrt(covariance[-1,-1])),ll=ll,aic=-2*ll+2*len(best.x),converged=True,attempts=attempts,min_information_eigenvalue=float(eigen.min()),hessian_step_relative_difference=relative,names=names,min_mu=float(expit(raw@beta).min()),max_mu=float(expit(raw@beta).max()))

def effect(beta,cov,index=1,scale=1):
    b=float(beta[index])*scale; se=float(np.sqrt(cov[index,index]))*scale
    lo=b-Z*se; hi=b+Z*se
    return dict(beta=b,se=se,ci_low=lo,ci_high=hi,odds_ratio=float(np.exp(b)),or_low=float(np.exp(lo)),or_high=float(np.exp(hi)),p=float(2*norm.sf(abs(b/se))),ci_includes_zero=bool(lo<=0<=hi))

def hc0(m,y,n):
    x=m.model.exog; bread=np.asarray(m.cov_params()); scores=x*(np.asarray(y)-np.asarray(n)*m.fittedvalues.to_numpy())[:,None]
    return bread@scores.T@scores@bread
