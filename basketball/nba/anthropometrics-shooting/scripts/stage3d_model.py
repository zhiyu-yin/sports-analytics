"""Fixed candidate models. No scientific exposure summaries are exported."""
import argparse
import numpy as np
import pymc as pm
import pytensor.tensor as pt
from stage3d_protocol import *

def design():
 p=protocol();d=fixed_data();ids=sorted(d.player_id.unique(),key=int);index={x:i for i,x in enumerate(ids)}
 idx=d.player_id.map(index).to_numpy(dtype=int);pos=d.combine_position.fillna('unknown').replace('','unknown')
 Xp=np.column_stack([(pos==x).to_numpy(dtype=float) for x in p['positions'] if x!='C'])
 Xs=np.column_stack([(d.season==x).to_numpy(dtype=float) for x in p['seasons'] if x!=p['season_reference']])
 return d,ids,idx,Xp,Xs,d.residual_wingspan.to_numpy(),d.height_wo_shoes_inches.to_numpy()-p['height_center'],np.log1p(d.fta.to_numpy())-p['log1p_FTA_center']

def build(candidate):
 assert candidate in ['D1','D2','D3'];d,ids,idx,Xp,Xs,rw,h,volume=design();positive=np.flatnonzero(d.fta.to_numpy()>0);p=protocol()
 coords=dict(player=ids,position=[x for x in p['positions'] if x!='C'],season=[x for x in p['seasons'] if x!=p['season_reference']],accuracy_row=list(range(len(positive))),opportunity_row=list(range(len(d))),effect=['accuracy','opportunity'])
 with pm.Model(coords=coords) as model:
  intercept=pm.Normal('beta_0',0,2.5)
  # Kept only in a future local trace; not exported to any adequacy artifact.
  sealed_slope=pm.Normal('beta_RW',0,.5)
  bh=pm.Normal('beta_H',0,.5);bp=pm.Normal('beta_position',0,1,dims='position');bs=pm.Normal('beta_season',0,1,dims='season')
  if candidate=='D3':
   chol,corr,sd=pm.LKJCholeskyCov('chol_cov',n=2,eta=2,sd_dist=pm.HalfNormal.dist(1,shape=2),compute_corr=True)
   z=pm.Normal('z_player',0,1,dims=('player','effect'));effects=pm.Deterministic('player_effects',pt.dot(z,chol.T),dims=('player','effect'))
   u=effects[:,0];v=effects[:,1];pm.Deterministic('corr_uv',corr[0,1]);pm.Deterministic('sigma_accuracy',sd[0]);pm.Deterministic('sigma_opportunity',sd[1])
   a0=pm.Normal('a_0',0,2.5);ar=pm.Normal('a_RW',0,.5);ah=pm.Normal('a_H',0,.5);ap=pm.Normal('a_position',0,1,dims='position');ase=pm.Normal('a_season',0,1,dims='season')
   alpha=pm.HalfNormal('alpha_FTA',5)
   log_rate=a0+ar*rw+ah*h+pt.dot(Xp,ap)+pt.dot(Xs,ase)+v[idx]
   # The validated GP offset has a fixed coefficient of one. No minute field.
   mu_fta=pm.Deterministic('mu_FTA',pt.exp(np.log(d.games_played.to_numpy())+log_rate),dims='opportunity_row')
   pm.NegativeBinomial('FTA_count',mu=mu_fta,alpha=alpha,observed=d.fta.to_numpy(dtype=int),dims='opportunity_row')
  else:
   sigma=pm.HalfNormal('sigma_player',1);z=pm.Normal('z_player',0,1,dims='player');u=pm.Deterministic('u_player',sigma*z,dims='player')
  eta=intercept+sealed_slope*rw+bh*h+pt.dot(Xp,bp)+pt.dot(Xs,bs)+u[idx]
  if candidate=='D1':eta=eta+pm.Normal('gamma_FTA',0,.5)*volume
  mu=pm.Deterministic('mu_accuracy',pm.math.sigmoid(eta[positive]),dims='accuracy_row')
  if candidate=='D2':
   g0=pm.Normal('gamma_0',3,2);gk=pm.Normal('gamma_k',0,.5);kappa=pm.Deterministic('kappa',pt.exp(g0+gk*volume[positive]),dims='accuracy_row')
  else:kappa=pm.Deterministic('kappa',pt.exp(pm.Normal('log_kappa',3,2)))
  pm.BetaBinomial('FTM_count',n=d.fta.to_numpy(dtype=int)[positive],alpha=mu*kappa,beta=(1-mu)*kappa,observed=d.ftm.to_numpy(dtype=int)[positive],dims='accuracy_row')
 return model

def prior_check(candidate):
 p=protocol();outpath=E/(candidate.lower()+'_prior_predictive.json');assert not outpath.exists()
 assert not list(M.glob('*posterior*')),'Prior checks precede any posterior sampling'
 variables=['mu_accuracy','kappa']
 if candidate=='D3':variables+=['mu_FTA','FTA_count','alpha_FTA','chol_cov_corr','chol_cov_stds']
 started=now()
 with build(candidate):
  prior=pm.sample_prior_predictive(draws=p['prior_predictive']['draws'],var_names=variables,random_seed=p['prior_predictive']['seed'],compile_kwargs={'mode':'FAST_COMPILE'})
 mu=prior.prior.mu_accuracy.values;lo=float((mu<.01).mean());hi=float((mu>.99).mean());finite=bool(np.isfinite(mu).all())
 accuracy=dict(finite=finite,fraction_below_001=lo,fraction_above_099=hi,quantiles={str(q):float(np.quantile(mu,q)) for q in [.001,.01,.025,.25,.5,.75,.975,.99,.999]},acceptable=finite and lo<=.25 and hi<=.25)
 output=dict(candidate=candidate,started_at=started,completed_at=now(),protocol_sha256=sha(E/'model_adequacy_protocol.json'),model_code_sha256=sha(Path(__file__)),draws=2000,seed=20260928,accuracy=accuracy,posterior_fitted=False,scientific_parameter_status='SEALED_PENDING_STAGE3E')
 if candidate=='D3':
  d=fixed_data();mean_count=prior.prior.mu_FTA.values;counts=prior.prior_predictive.FTA_count.values;rate=mean_count/d.games_played.to_numpy();corr=prior.prior.chol_cov_corr.values;sd=prior.prior.chol_cov_stds.values
  count_finite=bool(np.isfinite(counts).all() and np.isfinite(mean_count).all());nonnegative=bool((counts>=0).all() and (counts%1==0).all());rate_tail=float((rate>100).mean());count_tail=float((counts>1000000).mean());gate=p['prior_predictive']['opportunity_gate']
  opportunity=dict(all_finite=count_finite,nonnegative_integer=nonnegative,fraction_implied_rate_over_100_per_game=rate_tail,fraction_simulated_count_over_1000000=count_tail,implied_rate_quantiles={str(q):float(np.quantile(rate,q)) for q in [.5,.9,.95,.99,.999]},simulated_count_quantiles={str(q):float(np.quantile(counts,q)) for q in [.25,.5,.75,.9,.95,.99,.999]},maximum_simulated_count=int(counts.max()),maximum_implied_rate=float(rate.max()),acceptable=count_finite and nonnegative and rate_tail<=gate['max_fraction_implied_rate_over_100_per_game'] and count_tail<=gate['max_fraction_simulated_count_over_1000000'])
  output['opportunity']=opportunity;output['random_effect_prior_validation']=dict(correlation_symmetric=bool(np.allclose(corr,np.swapaxes(corr,-1,-2))),correlation_diagonal_one=bool(np.allclose(np.diagonal(corr,axis1=-2,axis2=-1),1)),minimum_eigenvalue=float(np.linalg.eigvalsh(corr).min()),all_SD_positive=bool((sd>0).all()),all_alpha_FTA_positive=bool((prior.prior.alpha_FTA.values>0).all()))
  output['acceptable']=accuracy['acceptable'] and opportunity['acceptable']
  # Predictive values and prior covariance draws only; no coefficient samples exported.
  np.savez_compressed(M/'d3_prior_predictive_checks.npz',mu_FTA=mean_count,FTA=counts,correlation=corr,SD=sd)
 else:output['acceptable']=accuracy['acceptable']
 save(outpath.name,output);print(json.dumps(output,indent=2))
 return output['acceptable']

def authorize_posterior():
 checks=[read(E/(k.lower()+'_prior_predictive.json')) for k in ['D1','D2','D3']]
 if not all(x['acceptable'] for x in checks):raise RuntimeError('STOP: prior predictive gate failed; no outcome posterior fitting authorized')

def fit(candidate):
 authorize_posterior();settings=protocol()['candidates'][candidate]['sampling'];path=M/(candidate.lower()+'_posterior.nc');assert not path.exists()
 record=dict(candidate=candidate,started_at=now(),settings=settings,protocol_sha256=sha(E/'model_adequacy_protocol.json'),status='RUNNING');save(candidate.lower()+'_sampling_attempt1.json',record)
 try:
  with build(candidate):
   trace=pm.sample(draws=settings['draws'],tune=settings['tune'],chains=4,cores=4,target_accept=settings['target_accept'],random_seed=settings['seed'],nuts_sampler='pymc',mp_ctx='spawn',blas_cores=1,compile_kwargs={'mode':'NUMBA'},progressbar=False,idata_kwargs={'log_likelihood':False})
  trace.to_netcdf(path);record.update(status='COMPLETE',trace_sha256=sha(path),completed_at=now())
 except Exception as ex:record.update(status='FAILED',error=repr(ex));raise
 finally:save(candidate.lower()+'_sampling_attempt1.json',record)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['prior','fit']);a.add_argument('candidate',choices=['D1','D2','D3']);args=a.parse_args()
 prior_check(args.candidate) if args.action=='prior' else fit(args.candidate)
