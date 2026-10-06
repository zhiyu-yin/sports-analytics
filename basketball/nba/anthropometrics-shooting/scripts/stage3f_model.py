"""Predeclared hurdle plus within/between models; scientific slope protected."""
import pymc as pm,pytensor.tensor as pt
from stage3d_model import design
from stage3f_common import *
def ztnb_logp(value,mu,alpha):
 log_zero=-alpha*pt.log1p(mu/alpha)
 return pt.switch(value>=1,pm.logp(pm.NegativeBinomial.dist(mu=mu,alpha=alpha),value)-pt.log(-pt.expm1(log_zero)),-np.inf)

def build(candidate):
 assert candidate in ['F1','F2'];d,ids,idx,Xp,Xs,rw,height,_=design();p=original();positive=np.flatnonzero(d.fta.to_numpy()>0)
 coords=dict(player=ids,position=[x for x in p['positions'] if x!='C'],season=[x for x in p['seasons'] if x!=p['season_reference']],row=np.arange(len(d)),positive_row=np.arange(len(positive)),effect=['accuracy','positive_opportunity','hurdle'])
 with pm.Model(coords=coords) as model:
  b0=pm.Normal('beta_0',0,2.5);br=pm.Normal('beta_RW',0,.5);bh=pm.Normal('beta_H',0,.5);bp=pm.Normal('beta_position',0,1,dims='position');bs=pm.Normal('beta_season',0,1,dims='season')
  chol,corr,sd=pm.LKJCholeskyCov('chol_cov',n=3,eta=2,sd_dist=pm.HalfNormal.dist(sigma=np.array([1.,.5,1.]),shape=3),compute_corr=True)
  z=pm.Normal('z_player',0,1,dims=('player','effect'));effects=pm.Deterministic('player_effects',pt.dot(z,chol.T),dims=('player','effect'));u,v,h=effects[:,0],effects[:,1],effects[:,2]
  for i,name in enumerate(['accuracy','positive_opportunity','hurdle']):pm.Deterministic('sigma_'+name,sd[i])
  for i,j,name in [(0,1,'uv'),(0,2,'uh'),(1,2,'vh')]:pm.Deterministic('corr_'+name,corr[i,j])
  a0=pm.Normal('a_0',np.log(2),1);ar=pm.Normal('a_RW',0,.15);ah=pm.Normal('a_H',0,.15);ap=pm.Normal('a_position',0,.35,dims='position');ase=pm.Normal('a_season',0,.25,dims='season')
  alpha=pm.Deterministic('alpha_FTA',pt.exp(pm.Normal('log_alpha_FTA',np.log(2),1)))
  log_rate=a0+ar*rw+ah*height+pt.dot(Xp,ap)+pt.dot(Xs,ase)+v[idx]
  mu=pm.Deterministic('mu_FTA',pt.exp(np.log(d.games_played.to_numpy())+log_rate),dims='row')
  c0=pm.Normal('c_0',np.log(.95/.05),1);cr=pm.Normal('c_RW',0,.25);ch=pm.Normal('c_H',0,.25);cp=pm.Normal('c_position',0,.5,dims='position');cs=pm.Normal('c_season',0,.35,dims='season')
  pi=pm.Deterministic('pi_hurdle',pm.math.sigmoid(c0+cr*rw+ch*height+pt.dot(Xp,cp)+pt.dot(Xs,cs)+h[idx]),dims='row')
  pm.Bernoulli('any_FTA',p=pi,observed=(d.fta.to_numpy()>0).astype(int),dims='row')
  pm.CustomDist('positive_FTA',mu[positive],alpha,logp=ztnb_logp,observed=d.fta.to_numpy(dtype=int)[positive],dims='positive_row')
  eta=b0+br*rw+bh*height+pt.dot(Xp,bp)+pt.dot(Xs,bs)+u[idx]
  if candidate=='F2':
   between,within,_,_=decomposition(d.fta.to_numpy(),d.games_played.to_numpy(),idx)
   eta=eta+pm.Normal('theta_B',0,.5)*between+pm.Normal('theta_W',0,.5)*within
  acc=pm.Deterministic('mu_accuracy_all',pm.math.sigmoid(eta),dims='row');kappa=pm.Deterministic('kappa',pt.exp(pm.Normal('log_kappa',3,2)))
  pm.BetaBinomial('FTM_count',n=d.fta.to_numpy(dtype=int)[positive],alpha=acc[positive]*kappa,beta=(1-acc[positive])*kappa,observed=d.ftm.to_numpy(dtype=int)[positive],dims='positive_row')
 return model
