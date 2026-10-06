"""Frozen amended opportunity priors; unchanged candidate likelihoods."""
import numpy as np
import pymc as pm
import pytensor.tensor as pt
from stage3d_model import design
from stage3dr_common import *

def build(candidate):
 assert candidate in ['D1','D2','D3'];d,ids,idx,Xp,Xs,rw,h,volume=design();positive=np.flatnonzero(d.fta.to_numpy()>0);p=protocol()
 coords=dict(player=ids,position=[x for x in p['positions'] if x!='C'],season=[x for x in p['seasons'] if x!=p['season_reference']],accuracy_row=list(range(len(positive))),opportunity_row=list(range(len(d))),effect=['accuracy','opportunity'])
 with pm.Model(coords=coords) as model:
  intercept=pm.Normal('beta_0',0,2.5)
  # Kept only in a future local trace; not exported to any adequacy artifact.
  sealed_slope=pm.Normal('beta_RW',0,.5)
  bh=pm.Normal('beta_H',0,.5);bp=pm.Normal('beta_position',0,1,dims='position');bs=pm.Normal('beta_season',0,1,dims='season')
  if candidate=='D3':
   chol,corr,sd=pm.LKJCholeskyCov('chol_cov',n=2,eta=2,sd_dist=pm.HalfNormal.dist(sigma=np.array([1.,.5]),shape=2),compute_corr=True)
   z=pm.Normal('z_player',0,1,dims=('player','effect'));effects=pm.Deterministic('player_effects',pt.dot(z,chol.T),dims=('player','effect'))
   u=effects[:,0];v=effects[:,1];pm.Deterministic('corr_uv',corr[0,1]);pm.Deterministic('sigma_accuracy',sd[0]);pm.Deterministic('sigma_opportunity',sd[1])
   a0=pm.Normal('a_0',np.log(2),1);ar=pm.Normal('a_RW',0,.15);ah=pm.Normal('a_H',0,.15);ap=pm.Normal('a_position',0,.35,dims='position');ase=pm.Normal('a_season',0,.25,dims='season')
   alpha=pm.Deterministic('alpha_FTA',pt.exp(pm.Normal('log_alpha_FTA',np.log(2),1)))
   log_rate=a0+ar*rw+ah*h+pt.dot(Xp,ap)+pt.dot(Xs,ase)+v[idx]
   # The validated GP offset has a fixed coefficient of one. No minute field.
   mu_fta=pm.Deterministic('mu_FTA',pt.exp(np.log(d.games_played.to_numpy())+log_rate),dims='opportunity_row')
   pm.NegativeBinomial('FTA_count',mu=mu_fta,alpha=alpha,observed=d.fta.to_numpy(dtype=int),dims='opportunity_row')
  else:
   sigma=pm.HalfNormal('sigma_player',1);z=pm.Normal('z_player',0,1,dims='player');u=pm.Deterministic('u_player',sigma*z,dims='player')
  eta=intercept+sealed_slope*rw+bh*h+pt.dot(Xp,bp)+pt.dot(Xs,bs)+u[idx]
  if candidate=='D1':eta=eta+pm.Normal('gamma_FTA',0,.5)*volume
  mu_all=pm.Deterministic('mu_accuracy_all',pm.math.sigmoid(eta),dims='opportunity_row')
  mu=pm.Deterministic('mu_accuracy',mu_all[positive],dims='accuracy_row')
  if candidate=='D2':
   g0=pm.Normal('gamma_0',3,2);gk=pm.Normal('gamma_k',0,.5);kappa=pm.Deterministic('kappa',pt.exp(g0+gk*volume[positive]),dims='accuracy_row')
  else:kappa=pm.Deterministic('kappa',pt.exp(pm.Normal('log_kappa',3,2)))
  pm.BetaBinomial('FTM_count',n=d.fta.to_numpy(dtype=int)[positive],alpha=mu*kappa,beta=(1-mu)*kappa,observed=d.ftm.to_numpy(dtype=int)[positive],dims='accuracy_row')
 return model
