"""Independent trigamma observed information and synthetic equivalence checks."""
from stage3jr_common import *
from scipy.special import polygamma
from scipy.stats import betabinom

def information(theta,x,y,n):
 mu=expit(x@theta[:-1]);k=np.exp(theta[-1]);a=mu*k;b=(1-mu)*k
 common=old.digamma(k)-old.digamma(n+k)
 da=old.digamma(y+a)-old.digamma(a)+common;db=old.digamma(n-y+b)-old.digamma(b)+common
 cross=polygamma(1,k)-polygamma(1,n+k)
 aa=polygamma(1,y+a)-polygamma(1,a)+cross;bb=polygamma(1,n-y+b)-polygamma(1,b)+cross
 u=k*mu*(1-mu)
 etaeta=u*u*(aa+bb-2*cross)+(da-db)*u*(1-2*mu)
 etak=u*(aa*a+cross*b-cross*a-bb*b+da-db)
 kk=aa*a*a+2*cross*a*b+bb*b*b+da*a+db*b
 h=np.empty((len(theta),len(theta)));h[:-1,:-1]=-x.T@(etaeta[:,None]*x);h[:-1,-1]=-x.T@etak;h[-1,:-1]=h[:-1,-1];h[-1,-1]=-kk.sum()
 return h

def main():
 rng=np.random.default_rng(630);x=np.column_stack([np.ones(600),rng.normal(size=600),rng.normal(77,3,600),rng.integers(0,2,600)]);n=rng.integers(1,500,600);y=rng.integers(0,n+1)
 means=x.mean(0);scales=x.std(0);means[0]=0;scales[0]=1;z=(x-means)/scales;T=np.diag(1/scales);T[0,:]=-means/scales;T[0,0]=1;A=np.eye(5);A[:-1,:-1]=T
 ge=[];he=[];lle=[];scale_ll=[];scale_g=[];scale_h=[];inverse=[]
 for k in [2.,10.,32.,200.]:
  theta=np.r_[np.array([.8,-.2,.1,.1]),np.log(k)];mu=expit(z@theta[:-1]);ll=-old.objective(theta,z,y,n)[0];ref=betabinom.logpmf(y,n,mu*k,(1-mu)*k).sum();lle.append(abs(ll-ref))
  numeric=[]
  for j in range(len(theta)):
   delta=np.zeros(len(theta));delta[j]=1e-5
   numeric.append((old.objective(theta+delta,z,y,n)[0]-old.objective(theta-delta,z,y,n)[0])/2e-5)
  grad=old.objective(theta,z,y,n)[1];ge.append(float(np.max(np.abs(grad-numeric))));H=information(theta,z,y,n);Hfd=old.hessian(theta,z,y,n,step=1e-5);he.append(float(np.max(np.abs(H-Hfd))))
  raw=A@theta;raw[-1]=theta[-1];v,g=old.objective(raw,x,y,n);scale_ll.append(abs(v+ll));scale_g.append(float(np.max(np.abs(A.T@g-grad))));scale_h.append(float(np.max(np.abs(A.T@information(raw,x,y,n)@A-H))));inverse.append(float(np.max(np.abs(np.linalg.solve(A,raw)-theta))))
 assert max(lle)<1e-8 and max(ge)<1e-4 and max(he)<1e-4
 assert max(scale_ll)<1e-8 and max(scale_g)<1e-7 and max(scale_h)<1e-6 and max(inverse)<1e-12
 save('likelihood_validation.json',dict(passed=True,fixture_seed=630,rows=600,kappas=[2,10,32,200],scipy_beta_binomial_loglik_max_error=max(lle),old_likelihood_unchanged=True,validated_at=now()))
 save('gradient_validation.json',dict(passed=True,analytic_score_vs_central_difference_max_error=max(ge),step=1e-5,trigamma_information_vs_score_difference_max_error=max(he),validated_at=now()))
 save('scaling_equivalence.json',dict(passed=True,scaling='Exactly existing Stage 2 sample-specific column centering/SD (intercept untouched); raw beta=T*scaled beta; log kappa unchanged; g_scaled=A.T*g_raw; H_scaled=A.T*H_raw*A',max_loglik_difference=max(scale_ll),max_score_difference=max(scale_g),max_hessian_difference=max(scale_h),max_forward_inverse_error=max(inverse),no_statistical_change=True,validated_at=now()))
 print('Likelihood, score, Hessian and scaling validation PASS',flush=True)
if __name__=='__main__':main()
