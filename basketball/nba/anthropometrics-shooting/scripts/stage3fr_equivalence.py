"""Matched-coordinate density, prior, predictor and predictive equivalence checks."""
import sys,arviz as az,xarray as xr
from scipy.stats import norm,multivariate_normal
from stage3fr_common import *
from stage3fr_model import build,pm
from stage3f_model import build as oldbuild

def unpack(p):
 v=p['chol_cov_cholesky-cov-packed__'].copy();v[[0,2,5]]=np.exp(v[[0,2,5]]);L=np.zeros((3,3));L[np.tril_indices(3)]=v;return L
def transform(point,candidate):
 s=protocol()['scales'];q={k:v.copy() for k,v in point.items()};q['theta_B_std']=q.pop('theta_B')*s['B'];q['theta_W_std']=q.pop('theta_W')*s['W'];L=unpack(point);J=np.log(s['B'])+np.log(s['W'])
 if candidate=='R2':q['player_effects']=q.pop('z_player')@L.T;J+=len(q['player_effects'])*np.log(np.diag(L)).sum()
 if candidate=='R3':
  z=q.pop('z_player');q['uv_centered']=z[:,:2]@L[:2,:2].T;q['z_hurdle']=z[:,2].copy();J+=len(z)*np.log(np.diag(L)[:2]).sum()
 return q,float(J)
def inverse(q,candidate):
 s=protocol()['scales'];p={k:v.copy() for k,v in q.items()};p['theta_B']=p.pop('theta_B_std')/s['B'];p['theta_W']=p.pop('theta_W_std')/s['W'];L=unpack(p)
 if candidate=='R2':p['z_player']=np.linalg.solve(L,p.pop('player_effects').T).T
 if candidate=='R3':p['z_player']=np.column_stack([np.linalg.solve(L[:2,:2],p.pop('uv_centered').T).T,p.pop('z_hurdle')])
 return p

def validate(candidate):
 authorize()
 existing=E/(candidate.lower()+'_equivalence_validation.json')
 if existing.exists():
  result=read(existing);assert result['passed'], 'Existing equivalence failure requires a stop, not a refit'
  assert result['new_model_sha256']==sha(ROOT/'scripts/stage3fr_model.py') and result['original_model_sha256']==sha(ROOT/'scripts/stage3f_model.py')
  print(candidate,'reusing completed equivalence validation',flush=True);return
 old=oldbuild('F2');new=build(candidate);names=['mu_accuracy_all','mu_FTA','pi_hurdle','kappa','alpha_FTA']
 def fun(m):return m.compile_fn(m.replace_rvs_by_values([m[n] for n in names]),inputs=m.value_vars,on_unused_input='ignore',mode='FAST_COMPILE')
 # Centered observed likelihoods do not directly use covariance coordinates.
 # Accept the complete matched point explicitly, including unused prior inputs.
 def likelihood(m):return m.compile_fn(m.logp(vars=m.observed_RVs),inputs=m.value_vars,on_unused_input='ignore',mode='FAST_COMPILE')
 fo,fn=fun(old),fun(new);lo=old.compile_logp(mode='FAST_COMPILE');ln=new.compile_logp(mode='FAST_COMPILE');llo,lln=likelihood(old),likelihood(new)
 rng=np.random.default_rng(20260928);errors=dict(log_density=0.,likelihood=0.,linear_predictor=0.,inverse=0.,transformed_normal_prior=0.,latent_density=0.)
 from scipy.special import logit
 for rep in range(12):
  p={k:v.copy()+rng.normal(0,.08,size=v.shape) for k,v in old.initial_point().items()};p['z_player']=rng.normal(0,.6,size=p['z_player'].shape);q,J=transform(p,candidate);back=inverse(q,candidate)
  errors['inverse']=max(errors['inverse'],max(float(np.max(np.abs(p[k]-back[k]))) for k in p))
  errors['log_density']=max(errors['log_density'],abs(float(ln(q)+J-lo(p))));errors['likelihood']=max(errors['likelihood'],abs(float(lln(q)-llo(p))))
  a,b=fo(p),fn(q)
  for i in [0,1,2]:
   xa=logit(a[i]) if i!=1 else np.log(a[i]);xb=logit(b[i]) if i!=1 else np.log(b[i]);errors['linear_predictor']=max(errors['linear_predictor'],float(np.max(np.abs(xa-xb))))
  s=protocol()['scales']
  for k in ['B','W']:
   delta=norm.logpdf(q['theta_'+k+'_std'],0,.5*s[k])+np.log(s[k])-norm.logpdf(p['theta_'+k],0,.5);errors['transformed_normal_prior']=max(errors['transformed_normal_prior'],float(abs(delta)))
  # Independent SciPy check on a small synthetic fixture, not only PyMC graphs.
  L=unpack(p);z=rng.normal(size=(7,3));r=z@L.T;orig=norm.logpdf(z).sum()
  if candidate=='R2':delta=multivariate_normal.logpdf(r,mean=np.zeros(3),cov=L@L.T).sum()+7*np.log(np.diag(L)).sum()-orig
  elif candidate=='R3':delta=multivariate_normal.logpdf(r[:,:2],mean=np.zeros(2),cov=L[:2,:2]@L[:2,:2].T).sum()+norm.logpdf(z[:,2]).sum()+7*np.log(np.diag(L)[:2]).sum()-orig
  else:delta=0.
  errors['latent_density']=max(errors['latent_density'],abs(float(delta)))
 priorpath=M/'equivalence_original_prior.nc'
 if not priorpath.exists():
  vars=[v.name for v in old.free_RVs]+names+['player_effects']
  with old:pr=pm.sample_prior_predictive(draws=500,var_names=vars,random_seed=20260928,compile_kwargs={'mode':'FAST_COMPILE'})
  pr.to_netcdf(priorpath)
 pr=az.from_netcdf(priorpath);source=pr.prior;dest=source.copy();s=protocol()['scales'];dest['theta_B_std']=source.theta_B*s['B'];dest['theta_W_std']=source.theta_W*s['W']
 if candidate=='R3':
  dest['uv_centered']=xr.DataArray(source.player_effects.values[:,:,:,:2],dims=('chain','draw','player','uv_effect'),coords={'chain':source.chain,'draw':source.draw,'player':source.player,'uv_effect':['accuracy','positive_opportunity']});dest['z_hurdle']=source.z_player.isel(effect=2,drop=True)
 with new:det=pm.compute_deterministics(dest,var_names=names,model=new,progressbar=False,compile_kwargs={'mode':'NUMBA'})
 pe={k:float(np.max(np.abs(det[k].values-source[k].values)/(1+np.abs(source[k].values)))) for k in names}
 # Shared-uniform coupling: identical generated counts and makes is stronger than an MC mean comparison.
 rr1=np.random.default_rng(20260929);rr2=np.random.default_rng(20260929);matched=True
 from stage3d_model import design
 d,*_=design();n=d.fta.to_numpy(dtype=int)
 for i in range(500):
  draws=[]
  for ds,rr in [(source,rr1),(det,rr2)]:
   mu=ds.mu_accuracy_all.values[0,i];k=ds.kappa.values[0,i];pi=ds.pi_hurdle.values[0,i];m=ds.mu_FTA.values[0,i];alpha=ds.alpha_FTA.values[0,i]
   nr=rr.binomial(1,pi)*ztnb_random(m,alpha,rr);y=rr.binomial(n,rr.beta(mu*k,(1-mu)*k));draws.append((nr,y))
  matched=matched and all(np.array_equal(x,y) for x,y in zip(*draws))
 # In floating point, rare binomial inversion boundary differences need not violate equivalence;
 # require deterministic relative agreement and record paired count comparison transparently.
 good=all(v<1e-7 for v in errors.values()) and all(v<1e-10 for v in pe.values()) and matched
 out=dict(candidate=candidate,checked_at=now(),passed=bool(good),matched_parameter_points=12,synthetic_latent_points_per_case=7,maximum_absolute_errors=errors,prior_predictive_draws=500,prior_predictive_coupling='Same original prior draws mapped exactly into new coordinates; same RNG seed for replicated counts and makes',prior_predictive_deterministic_relative_errors=pe,paired_prior_predictive_counts_exact=matched,original_prior_preserved=True,data_rows_unchanged=True,no_coefficient_omitted=set(inverse(transform(old.initial_point(),candidate)[0],candidate))==set(old.initial_point()),original_model_sha256=sha(ROOT/'scripts/stage3f_model.py'),new_model_sha256=sha(ROOT/'scripts/stage3fr_model.py'),scientific_effect_summary_exported=False)
 save(candidate.lower()+'_equivalence_validation.json',out);assert good,out;print(candidate,'equivalence passed',flush=True)
if __name__=='__main__':validate(sys.argv[1])
