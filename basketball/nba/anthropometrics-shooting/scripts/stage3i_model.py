"""New shared-opportunity structure, not an F2 reparameterization."""
import pymc as pm,pytensor.tensor as pt
from stage3d_model import design
from stage3i_common import *
from stage3f_model import ztnb_logp
def build(candidate):
 assert candidate in ['I1','I2','I3'];d,ids,idx,Xp,Xs,rw,height,_=design();p=original();positive=np.flatnonzero(d.fta.to_numpy()>0)
 coords=dict(player=ids,position=[x for x in p['positions'] if x!='C'],season=[x for x in p['seasons'] if x!=p['season_reference']],row=np.arange(len(d)),positive_row=np.arange(len(positive)))
 with pm.Model(coords=coords) as model:
  b0=pm.Normal('beta_0',0,2.5);br=pm.Normal('beta_RW',0,.5);bh=pm.Normal('beta_H',0,.5);bp=pm.Normal('beta_position',0,1,dims='position');bs=pm.Normal('beta_season',0,1,dims='season')
  o=pm.Normal('o_player',0,1,dims='player');e=pm.Normal('e_player',0,1,dims='player')
  sa=pm.HalfNormal('sigma_accuracy',1);so=pm.HalfNormal('sigma_opportunity',.5);lh=pm.Normal('lambda_h',0,1);rho=pm.Uniform('rho_AO',-1,1)
  u=pm.Deterministic('accuracy_effect',sa*(rho*o+pt.sqrt(1-rho**2)*e),dims='player')
  v=pm.Deterministic('positive_effect',so*o,dims='player');h=pm.Deterministic('hurdle_effect',lh*o,dims='player')
  a0=pm.Normal('a_0',np.log(2),1);ar=pm.Normal('a_RW',0,.15);ah=pm.Normal('a_H',0,.15);ap=pm.Normal('a_position',0,.35,dims='position');ase=pm.Normal('a_season',0,.25,dims='season')
  alpha=pm.Deterministic('alpha_FTA',pt.exp(pm.Normal('log_alpha_FTA',np.log(2),1)))
  log_rate=a0+ar*rw+ah*height+pt.dot(Xp,ap)+pt.dot(Xs,ase)+v[idx]
  if candidate in ['I2','I3']:
   c=pm.Normal('c_player',0,1,dims='player');sc=pm.HalfNormal('sigma_count_resid',.5)
   count=pm.Deterministic('count_residual_effect',sc*c,dims='player');log_rate=log_rate+count[idx]
  mu=pm.Deterministic('mu_FTA',pt.exp(np.log(d.games_played.to_numpy())+log_rate),dims='row')
  c0=pm.Normal('c_0',np.log(.95/.05),1);cr=pm.Normal('c_RW',0,.25);ch=pm.Normal('c_H',0,.25);cp=pm.Normal('c_position',0,.5,dims='position');cs=pm.Normal('c_season',0,.35,dims='season')
  pi=pm.Deterministic('pi_hurdle',pm.math.sigmoid(c0+cr*rw+ch*height+pt.dot(Xp,cp)+pt.dot(Xs,cs)+h[idx]),dims='row')
  pm.Bernoulli('any_FTA',p=pi,observed=(d.fta.to_numpy()>0).astype(int),dims='row')
  pm.CustomDist('positive_FTA',mu[positive],alpha,logp=ztnb_logp,observed=d.fta.to_numpy(dtype=int)[positive],dims='positive_row')
  eta=b0+br*rw+bh*height+pt.dot(Xp,bp)+pt.dot(Xs,bs)+u[idx]
  if candidate=='I2':eta=eta+pm.Normal('theta_W',0,.5)*observed_within(d)
  else:
   z,q=quadratic_basis(observed_within(d));eta=eta+pm.Normal('gamma_W1',0,.25)*z+pm.Normal('gamma_W2',0,.25)*q
  acc=pm.Deterministic('mu_accuracy_all',pm.math.sigmoid(eta),dims='row');kappa=pm.Deterministic('kappa',pt.exp(pm.Normal('log_kappa',3,2)))
  pm.BetaBinomial('FTM_count',n=d.fta.to_numpy(dtype=int)[positive],alpha=acc[positive]*kappa,beta=(1-acc[positive])*kappa,observed=d.ftm.to_numpy(dtype=int)[positive],dims='positive_row')
 return model
