"""Frozen equivalent F2 coordinates and separately ineligible diagnostic submodels."""
import pymc as pm,pytensor.tensor as pt
from stage3d_model import design
from stage3f_model import ztnb_logp
from stage3fr_common import *
def build(candidate):
 assert candidate in ['DIAG-A','DIAG-B','DIAG-C','R1','R2','R3']
 d,ids,idx,Xp,Xs,rw,height,_=design();p=original();positive=np.flatnonzero(d.fta.to_numpy()>0);accuracy=candidate!='DIAG-C';opportunity=candidate!='DIAG-A'
 coords=dict(player=ids,position=[x for x in p['positions'] if x!='C'],season=[x for x in p['seasons'] if x!=p['season_reference']],row=np.arange(len(d)),positive_row=np.arange(len(positive)),effect=['accuracy','positive_opportunity','hurdle'],uv_effect=['accuracy','positive_opportunity'],op_effect=['positive_opportunity','hurdle'])
 with pm.Model(coords=coords) as model:
  if accuracy:
   b0=pm.Normal('beta_0',0,2.5);br=pm.Normal('beta_RW',0,.5);bh=pm.Normal('beta_H',0,.5);bp=pm.Normal('beta_position',0,1,dims='position');bs=pm.Normal('beta_season',0,1,dims='season')
  if candidate=='DIAG-A':
   sd=pm.HalfNormal('sigma_accuracy',1);z=pm.Normal('z_accuracy',0,1,dims='player');u=pm.Deterministic('accuracy_effect',sd*z,dims='player')
  elif candidate=='DIAG-B':
   sd=pt.stack([pm.HalfNormal('sigma_'+name,s) for name,s in zip(['accuracy','positive_opportunity','hurdle'],[1.,.5,1.])]);z=pm.Normal('z_player',0,1,dims=('player','effect'));effects=pm.Deterministic('player_effects',z*sd,dims=('player','effect'));u,v,h=effects[:,0],effects[:,1],effects[:,2]
  elif candidate=='DIAG-C':
   # The 2D marginal correlation from LKJ(3, eta=2) is LKJ(2, eta=2.5).
   chol,corr,sd=pm.LKJCholeskyCov('chol_cov',n=2,eta=2.5,sd_dist=pm.HalfNormal.dist(sigma=np.array([.5,1.]),shape=2),compute_corr=True);z=pm.Normal('z_opportunity',0,1,dims=('player','op_effect'));effects=pm.Deterministic('opportunity_effects',pt.dot(z,chol.T),dims=('player','op_effect'));v,h=effects[:,0],effects[:,1]
   pm.Deterministic('sigma_positive_opportunity',sd[0]);pm.Deterministic('sigma_hurdle',sd[1]);pm.Deterministic('corr_vh',corr[0,1])
  else:
   chol,corr,sd=pm.LKJCholeskyCov('chol_cov',n=3,eta=2,sd_dist=pm.HalfNormal.dist(sigma=np.array([1.,.5,1.]),shape=3),compute_corr=True)
   if candidate=='R1':
    z=pm.Normal('z_player',0,1,dims=('player','effect'));effects=pm.Deterministic('player_effects',pt.dot(z,chol.T),dims=('player','effect'))
   elif candidate=='R2':effects=pm.MvNormal('player_effects',mu=pt.zeros(3),chol=chol,dims=('player','effect'))
   else:
    uv=pm.MvNormal('uv_centered',mu=pt.zeros(2),chol=chol[:2,:2],dims=('player','uv_effect'));zh=pm.Normal('z_hurdle',0,1,dims='player')
    z0=uv[:,0]/chol[0,0];z1=(uv[:,1]-chol[1,0]*z0)/chol[1,1];h=chol[2,0]*z0+chol[2,1]*z1+chol[2,2]*zh
    effects=pm.Deterministic('player_effects',pt.stack([uv[:,0],uv[:,1],h],axis=1),dims=('player','effect'))
   u,v,h=effects[:,0],effects[:,1],effects[:,2]
   for i,name in enumerate(['accuracy','positive_opportunity','hurdle']):pm.Deterministic('sigma_'+name,sd[i])
   for i,j,name in [(0,1,'uv'),(0,2,'uh'),(1,2,'vh')]:pm.Deterministic('corr_'+name,corr[i,j])
  if opportunity:
   a0=pm.Normal('a_0',np.log(2),1);ar=pm.Normal('a_RW',0,.15);ah=pm.Normal('a_H',0,.15);ap=pm.Normal('a_position',0,.35,dims='position');ase=pm.Normal('a_season',0,.25,dims='season');alpha=pm.Deterministic('alpha_FTA',pt.exp(pm.Normal('log_alpha_FTA',np.log(2),1)))
   log_rate=a0+ar*rw+ah*height+pt.dot(Xp,ap)+pt.dot(Xs,ase)+v[idx];mu=pm.Deterministic('mu_FTA',pt.exp(np.log(d.games_played.to_numpy())+log_rate),dims='row')
   c0=pm.Normal('c_0',np.log(.95/.05),1);cr=pm.Normal('c_RW',0,.25);ch=pm.Normal('c_H',0,.25);cp=pm.Normal('c_position',0,.5,dims='position');cs=pm.Normal('c_season',0,.35,dims='season');pi=pm.Deterministic('pi_hurdle',pm.math.sigmoid(c0+cr*rw+ch*height+pt.dot(Xp,cp)+pt.dot(Xs,cs)+h[idx]),dims='row')
   pm.Bernoulli('any_FTA',p=pi,observed=(d.fta.to_numpy()>0).astype(int),dims='row');pm.CustomDist('positive_FTA',mu[positive],alpha,logp=ztnb_logp,observed=d.fta.to_numpy(dtype=int)[positive],dims='positive_row')
  if accuracy:
   between,within,_,_=decomposition(d.fta.to_numpy(),d.games_played.to_numpy(),idx)
   if candidate.startswith('R'):
    scales=read(E/'design_identification_audit.json')['scales'];tb=pm.Normal('theta_B_std',0,.5*scales['B']);tw=pm.Normal('theta_W_std',0,.5*scales['W']);pm.Deterministic('theta_B',tb/scales['B']);pm.Deterministic('theta_W',tw/scales['W']);oppterm=tb*(between/scales['B'])+tw*(within/scales['W'])
   else:oppterm=pm.Normal('theta_B',0,.5)*between+pm.Normal('theta_W',0,.5)*within
   eta=b0+br*rw+bh*height+pt.dot(Xp,bp)+pt.dot(Xs,bs)+u[idx]+oppterm;acc=pm.Deterministic('mu_accuracy_all',pm.math.sigmoid(eta),dims='row');kappa=pm.Deterministic('kappa',pt.exp(pm.Normal('log_kappa',3,2)))
   pm.BetaBinomial('FTM_count',n=d.fta.to_numpy(dtype=int)[positive],alpha=acc[positive]*kappa,beta=(1-acc[positive])*kappa,observed=d.ftm.to_numpy(dtype=int)[positive],dims='positive_row')
 return model
