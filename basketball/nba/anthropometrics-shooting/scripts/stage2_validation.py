"""Independent numerical checks before interpreting beta-binomial regression."""
import numpy as np
import pandas as pd
from scipy.stats import betabinom,binom,beta as beta_dist
from scipy.integrate import quad
from scipy.optimize._numdiff import approx_derivative
from scipy.special import expit
import statsmodels.api as sm
from stage2_models import logpmf,objective,fit_bb,valid_counts

def validate():
    y=np.array([0,1,4,7,20]); n=np.array([5,5,10,10,20]); mu=np.array([.2,.5,.7,.8,.9]); k=12.
    ref=betabinom.logpmf(y,n,mu*k,(1-mu)*k)
    error=float(np.max(abs(logpmf(y,n,mu,k)-ref))); assert error<1e-11
    integral=quad(lambda p:binom.pmf(4,10,p)*beta_dist.pdf(p,3.4,8.6),0,1,epsabs=1e-12)[0]
    quadrature_error=abs(np.exp(logpmf(np.array([4]),np.array([10]),np.array([3.4/12]),12))[0]-integral); assert quadrature_error<1e-10
    limit=float(np.max(abs(logpmf(y,n,mu,1e7)-binom.logpmf(y,n,mu)))); assert limit<5e-5
    variances=[float(betabinom.var(100,.7*(1/rho-1),.3*(1/rho-1))) for rho in [.001,.01,.1]]; assert all(np.diff(variances)>0)
    rng=np.random.default_rng(20260928); ns=5000; x=pd.DataFrame({'const':np.ones(ns),'exposure':rng.normal(size=ns),'height':rng.normal(size=ns)})
    truth=np.array([.8,-.25,.2]); trials=rng.integers(20,201,ns); mu=expit(x.to_numpy()@truth); k=25.
    probs=rng.beta(mu*k,(1-mu)*k); makes=rng.binomial(trials,probs)
    initial=sm.GLM(np.column_stack([makes,trials-makes]),x,family=sm.families.Binomial()).fit().params
    fitted=fit_bb(x,makes,trials,initial)
    recovery_z=(fitted['beta']-truth)/np.sqrt(np.diag(fitted['cov'])); assert (abs(recovery_z)<4).all()
    assert abs(np.log(fitted['kappa']/k))/fitted['log_kappa_se']<4
    theta=np.r_[truth,np.log(k)]; numeric=approx_derivative(lambda t:objective(t,x.to_numpy(),makes,trials)[0],theta,method='3-point').ravel(); analytic=objective(theta,x.to_numpy(),makes,trials)[1]
    score_error=float(np.max(abs(numeric-analytic))); assert score_error<.005
    try: fit_bb(x.iloc[:100],makes[:100],trials[:100],initial,maxiter=0)
    except RuntimeError: failure_detected=True
    else: raise AssertionError('failure not detected')
    for yy,nn in [([2],[1]),([-1],[5]),([.5],[5])]:
        try: valid_counts(yy,nn)
        except ValueError: pass
        else: raise AssertionError('invalid counts accepted')
    return dict(passed=True,scipy_logpmf_max_error=error,independent_mixture_quadrature_error=float(quadrature_error),binomial_limit_max_logpmf_error=limit,variance_increases=variances,synthetic_seed=20260928,synthetic_n=ns,true_beta=truth.tolist(),estimated_beta=fitted['beta'].tolist(),recovery_z=recovery_z.tolist(),true_kappa=k,estimated_kappa=fitted['kappa'],analytic_score_max_error=score_error,forced_failure_detected=failure_detected,probability_range=[fitted['min_mu'],fitted['max_mu']],hessian_step_relative_difference=fitted['hessian_step_relative_difference'],starts=fitted['attempts'])
if __name__=='__main__':
    import json
    from stage1_analysis import ROOT
    result=validate(); (ROOT/'docs/stage2_evidence/beta_binomial_validation.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
