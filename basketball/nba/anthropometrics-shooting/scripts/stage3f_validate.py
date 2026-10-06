"""Independent zero-truncated NB and backend validation, no posterior sampling."""
import time,itertools
import scipy.stats as st
import pytensor,pytensor.tensor as pt
from stage3f_model import build,ztnb_logp,pm
from stage3f_common import *
def main():
 E.mkdir(exist_ok=True)
 y=pt.dvector('y');mu=pt.dvector('mu');alpha=pt.dvector('alpha')
 custom=pytensor.function([y,mu,alpha],ztnb_logp(y,mu,alpha),mode='FAST_COMPILE')
 native=pytensor.function([y,mu,alpha],pm.logp(pm.Truncated.dist(pm.NegativeBinomial.dist(mu=mu,alpha=alpha),lower=1),y),mode='FAST_COMPILE')
 grid=np.array(list(itertools.product([1.,2.,10.,100.,1000.],[.01,.1,1.,10.,100.,1000.],[.05,.5,2.,10.,100.])))
 yy,mm,aa=grid.T;ref=st.nbinom.logpmf(yy,aa,aa/(aa+mm))-st.nbinom.logsf(0,aa,aa/(aa+mm));ours=custom(yy,mm,aa);built=native(yy,mm,aa)
 np.testing.assert_allclose(ours,ref,rtol=1e-9,atol=1e-9);np.testing.assert_allclose(ours,built,rtol=1e-9,atol=1e-9)
 rng=np.random.default_rng(20260928);random_checks=[]
 for m,a in [(.01,.5),(2.,2.),(20.,.5),(100.,10.)]:
  sample=ztnb_random(np.full(100000,m),a,rng);sf=-np.expm1(-a*np.log1p(m/a));expect=m/sf;second=(m+m*m/a+m*m)/sf;se=np.sqrt((second-expect*expect)/len(sample));assert abs(sample.mean()-expect)<6*se
  random_checks.append(dict(mu=m,alpha=a,mean=float(sample.mean()),expected_mean=expect,SE=se,minimum=int(sample.min())))
 out=dict(validated_at=now(),grid_points=len(grid),maximum_error_scipy=float(np.max(abs(ours-ref))),maximum_error_native=float(np.max(abs(ours-built))),formula='log NB(y;mu,alpha) - log(-expm1(-alpha*log1p(mu/alpha))), support integers y>=1',native_backend_limitation='Pinned PyMC 5.25.1 Truncated NB gradient used NUMBA object-mode ScalarLoop fallback: measured full-model warm gradient 5.40709 seconds. Exact closed-form zero CDF correction avoids this computational limitation, without changing likelihood.',native_documentation='https://www.pymc.io/projects/docs/en/v5.24.0/api/distributions/generated/pymc.HurdleNegativeBinomial.html',random_validation=random_checks,backend={})
 for candidate in ['F1','F2']:
  model=build(candidate);point=model.initial_point();t=time.monotonic();compiled=model.compile_dlogp(mode='NUMBA');gradient=compiled(point);t1=time.monotonic();compiled(point);duration=time.monotonic()-t1;reference=model.compile_dlogp(mode='FAST_COMPILE')(point);np.testing.assert_allclose(gradient,reference,rtol=1e-8,atol=1e-8)
  out['backend'][candidate]=dict(finite=bool(np.isfinite(gradient).all()),reference_gradient_equal=True,compile_and_first_seconds=t1-t,warm_gradient_seconds=duration)
 save('likelihood_validation.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
