"""Frozen noncentered PyMC model; scientific summaries are separate from sampling."""
import argparse,time
import numpy as np,pandas as pd
import pymc as pm,pytensor.tensor as pt,arviz as az
from stage3c_setup import *
KEY=['beta_0','beta_RW','beta_H','position_effect','season_effect','sigma_player','log_kappa','kappa','rho']
def protocol():
 p=read(E/'model_protocol.json');assert sha(E/'model_protocol.json')==read(E/'protocol_freeze_receipt.json')['sha256'];return p

def data(kind):
 d,receipt=panel(kind);p=protocol();d.combine_position=d.combine_position.fillna('unknown').replace('','unknown');ids=sorted(d.player_id.unique(),key=int);positions=sorted(d.combine_position.unique());seasons=sorted(d.season.unique());positive=d[d.fta>0].copy();positive['source_row']=positive.index
 assert (d.ftm<=d.fta).all() and (d.ftm>=0).all()
 info=dict(player_ids=ids,positions=positions,seasons=seasons,position_nonreference=[x for x in positions if x!=p['position_reference']],season_nonreference=[x for x in seasons if x!=p['season_reference']])
 lookup={x:i for i,x in enumerate(ids)};idx=positive.player_id.map(lookup).to_numpy(dtype=int)
 Xp=np.column_stack([(positive.combine_position==x).to_numpy(dtype=float) for x in info['position_nonreference']]);Xs=np.column_stack([(positive.season==x).to_numpy(dtype=float) for x in info['season_nonreference']]);rw=positive.residual_wingspan.to_numpy();h=positive.height_wo_shoes_inches.to_numpy()-p['height_center']
 return d,positive,info,idx,Xp,Xs,rw,h

def build(kind,prior=False):
 d,y,info,idx,Xp,Xs,rw,h=data(kind)
 coords={'player':info['player_ids'],'position':info['position_nonreference'],'season_effect_level':info['season_nonreference'],'observation':list(range(len(y)))}
 with pm.Model(coords=coords) as model:
  b0=pm.Normal('beta_0',0,2.5);br=pm.Normal('beta_RW',0,.5);bh=pm.Normal('beta_H',0,.5)
  bp=pm.Normal('position_effect',0,1,dims='position');bs=pm.Normal('season_effect',0,1,dims='season_effect_level')
  sig=pm.HalfNormal('sigma_player',1);z=pm.Normal('z_player',0,1,dims='player');u=pm.Deterministic('u_player',sig*z,dims='player')
  lk=pm.Normal('log_kappa',3,2);k=pm.Deterministic('kappa',pt.exp(lk));pm.Deterministic('rho',1/(1+k))
  eta=b0+br*rw+bh*h+pt.dot(Xp,bp)+pt.dot(Xs,bs)+u[idx];mu=pm.math.sigmoid(eta)
  if prior:pm.Deterministic('mu',mu,dims='observation')
  pm.BetaBinomial('FTM',n=y.fta.to_numpy(dtype=int),alpha=mu*k,beta=(1-mu)*k,observed=y.ftm.to_numpy(dtype=int),dims='observation')
 return model

def prior_check():
 assert not list(M.glob('*_trace.nc'))
 p=protocol();model=build('primary',True)
 with model:prior=pm.sample_prior_predictive(draws=p['prior_predictive']['draws'],var_names=['mu'],random_seed=20260928)
 mu=prior.prior.mu.values.ravel();low=float((mu<.01).mean());high=float((mu>.99).mean());ok=bool(np.isfinite(mu).all() and low<=.25 and high<=.25)
 out=dict(completed_at=now(),protocol_sha256=sha(E/'model_protocol.json'),draws=1000,implied_mu_quantiles={str(q):float(np.quantile(mu,q)) for q in [.001,.01,.025,.1,.25,.5,.75,.9,.975,.99,.999]},fraction_below_001=low,fraction_above_099=high,all_finite=bool(np.isfinite(mu).all()),acceptable=ok,interpretation='Broad weakly informative support, not a calibrated population FT distribution; gate assesses boundary pathologies only.',observed_association_examined=False)
 save('prior_predictive_summary.json',out);print(json.dumps(out,indent=2));assert ok,'STOP: prior predictive pathology; no fitting authorized'

def progress_callback(trace,draw):
 if (draw.draw_idx+1)%500==0:print(f'chain={draw.chain} iteration={draw.draw_idx+1} tuning={draw.tuning}',flush=True)

def fit(kind,recovery=False):
 p=protocol();assert read(E/'prior_predictive_summary.json')['acceptable']
 if kind=='full':assert (E/'primary_replication_result.json').exists() and read(E/'primary_replication_result.json')['scientifically_reportable']
 attempt=2 if recovery else 1;trace=M/f'{kind}_attempt{attempt}_trace.nc';assert not trace.exists()
 settings=p['sampling'].copy()
 if recovery:settings.update({k:p['recovery'][k] for k in ['tune','draws','target_accept']});assert not read(E/f'{kind}_attempt1_diagnostics.json')['numeric_gate_pass']
 d,y,info,*_=data(kind);pd.DataFrame({'player_index':range(len(info['player_ids'])),'player_id':info['player_ids']}).to_csv(E/f'{kind}_player_index.csv',index=False)
 record=dict(kind=kind,attempt=attempt,started_at=now(),settings=settings,protocol_sha256=sha(E/'model_protocol.json'),code_sha256=sha(Path(__file__)),panel_sha256=panel(kind)[1]['sha256'],status='RUNNING',primary_freeze_sha256=sha(E/'primary_replication_result.json') if kind=='full' else None,backend='PyTensor NUMBA; PyMC NUTS unchanged',environment_sha256=sha(E/'environment.json'))
 save(f'{kind}_attempt{attempt}_sampling.json',record);start=time.monotonic()
 try:
  model=build(kind)
  with model:
   idata=pm.sample(draws=settings['draws'],tune=settings['tune'],chains=4,cores=4,random_seed=20260928,target_accept=settings['target_accept'],nuts_sampler='pymc',blas_cores=1,mp_ctx='spawn',compile_kwargs={'mode':'NUMBA'},callback=progress_callback,progressbar=False,return_inferencedata=True,idata_kwargs={'log_likelihood':False})
  idata.to_netcdf(trace);record.update(status='COMPLETE',completed_at=now(),elapsed_seconds=time.monotonic()-start,trace_path=str(trace.relative_to(ROOT)),trace_sha256=sha(trace),trace_bytes=trace.stat().st_size)
 except Exception as ex:
  record.update(status='FAILED',completed_at=now(),error=repr(ex));raise
 finally:save(f'{kind}_attempt{attempt}_sampling.json',record)
 print(json.dumps({k:v for k,v in record.items() if k!='settings'},indent=2))

def diagnostics(kind,attempt):
 idata=az.from_netcdf(M/f'{kind}_attempt{attempt}_trace.nc');p=protocol();summ=az.summary(idata,var_names=KEY,kind='diagnostics',round_to='none');summ.to_csv(E/f'{kind}_attempt{attempt}_diagnostic_parameters.csv')
 values=np.concatenate([idata.posterior[v].values.reshape(8000 if attempt==1 else 16000,-1) for v in KEY],axis=1)
 rh=float(summ.r_hat.max());bulk=float(summ.ess_bulk.min());tail=float(summ.ess_tail.min());bfmi=az.bfmi(idata).tolist();div=int(idata.sample_stats.diverging.sum());depth=int(idata.sample_stats.reached_max_treedepth.sum()) if 'reached_max_treedepth' in idata.sample_stats else int((idata.sample_stats.tree_depth>=10).sum());finite=bool(np.isfinite(np.cov(values,rowvar=False)).all())
 ok=rh<=1.01 and bulk>=400 and tail>=400 and min(bfmi)>=.3 and div==0 and depth==0 and finite
 out=dict(kind=kind,attempt=attempt,max_rhat=rh,min_bulk_ESS=bulk,min_tail_ESS=tail,BFMI_by_chain=bfmi,divergences=div,max_treedepth_hits=depth,finite_covariance=finite,numeric_gate_pass=ok,visual_review='PENDING',scientific_summary_released=False,checked_at=now())
 save(f'{kind}_attempt{attempt}_diagnostics.json',out)
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 F.mkdir(exist_ok=True);az.plot_trace(idata,var_names=KEY,compact=True);plt.tight_layout();plt.savefig(F/f'{kind}_attempt{attempt}_trace_review.png',dpi=130);plt.close('all');az.plot_energy(idata);plt.savefig(F/f'{kind}_attempt{attempt}_energy.png',dpi=130);plt.close('all')
 print(json.dumps(out,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['prior','fit','diagnostics']);a.add_argument('--kind',choices=['primary','full'],default='primary');a.add_argument('--attempt',type=int,default=1);args=a.parse_args()
 if args.action=='prior':prior_check()
 elif args.action=='fit':fit(args.kind,args.attempt==2)
 else:diagnostics(args.kind,args.attempt)
