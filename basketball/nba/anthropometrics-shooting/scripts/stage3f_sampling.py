"""Sampling and effect-blind convergence diagnostics."""
import argparse,time
import arviz as az
from stage3f_model import build,pm
from stage3f_common import *
def progress(trace,draw):
 if (draw.draw_idx+1)%500==0:print(f'chain={draw.chain} iteration={draw.draw_idx+1} tuning={draw.tuning}',flush=True)
def fit(candidate,attempt):
 authorize();a=protocol();s=a['sampling'].copy()
 if attempt==2:
  assert not read(E/f'{candidate.lower()}_attempt1_diagnostics.json')['numeric_gate_pass'];s.update({k:a['recovery'][k] for k in ['tune','draws','target_accept']})
 path=M/f'{candidate.lower()}_attempt{attempt}_trace.nc';assert not path.exists()
 record=dict(candidate=candidate,attempt=attempt,started_at=now(),settings=s,protocol_sha256=sha(E/'model_protocol.json'),model_code_sha256=sha(ROOT/'scripts/stage3f_model.py'),sampling_code_sha256=sha(Path(__file__)),status='RUNNING',backend='PyMC NUTS / PyTensor NUMBA / spawn / one BLAS thread')
 save(f'{candidate.lower()}_attempt{attempt}_sampling.json',record);start=time.monotonic()
 try:
  model=build(candidate)
  # Keep the scientific coefficient protected in the ignored trace only.
  names=[x.name for x in model.unobserved_RVs if not x.name.startswith('mu_') and x.name!='pi_hurdle']
  with model:
   idata=pm.sample(draws=s['draws'],tune=s['tune'],chains=4,cores=4,random_seed=s['seed'],target_accept=s['target_accept'],nuts_sampler='pymc',blas_cores=1,mp_ctx='spawn',compile_kwargs={'mode':'NUMBA'},callback=progress,progressbar=False,var_names=names,idata_kwargs={'log_likelihood':False})
  idata.to_netcdf(path);record.update(status='COMPLETE',completed_at=now(),elapsed_seconds=time.monotonic()-start,trace_sha256=sha(path),trace_bytes=path.stat().st_size)
 except Exception as ex:record.update(status='FAILED',error=repr(ex));raise
 finally:save(f'{candidate.lower()}_attempt{attempt}_sampling.json',record)
def diagnostic_keys(candidate):
 keys=['beta_0','beta_RW','beta_H','beta_position','beta_season','a_0','a_RW','a_H','a_position','a_season','c_0','c_RW','c_H','c_position','c_season','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','corr_uv','corr_uh','corr_vh','log_kappa','log_alpha_FTA']
 if candidate=='F2':keys+=['theta_B','theta_W']
 return keys
def diagnostics(candidate,attempt):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 idata=az.from_netcdf(M/f'{candidate.lower()}_attempt{attempt}_trace.nc');keys=diagnostic_keys(candidate)
 # kind=diagnostics deliberately excludes location, SD, intervals and probabilities.
 s=az.summary(idata,var_names=keys,kind='diagnostics',round_to='none');s=s[['ess_bulk','ess_tail','r_hat']];s.index=[x.replace('beta_RW','sealed_accuracy_parameter') for x in s.index];s.to_csv(E/f'{candidate.lower()}_attempt{attempt}_convergence.csv')
 values=np.concatenate([idata.posterior[k].values.reshape(idata.posterior.sizes['chain']*idata.posterior.sizes['draw'],-1) for k in keys],axis=1)
 finite=bool(np.isfinite(np.cov(values,rowvar=False)).all());bfmi=az.bfmi(idata).tolist();div=int(idata.sample_stats.diverging.sum());depth=int(idata.sample_stats.reached_max_treedepth.sum());rh=float(s.r_hat.max());bulk=float(s.ess_bulk.min());tail=float(s.ess_tail.min())
 out=dict(candidate=candidate,attempt=attempt,max_rhat=rh,min_bulk_ESS=bulk,min_tail_ESS=tail,BFMI=bfmi,divergences=div,max_depth_hits=depth,finite_covariance=finite,numeric_gate_pass=bool(rh<=1.01 and bulk>=400 and tail>=400 and min(bfmi)>=.3 and div==0 and depth==0 and finite),visual_review='PENDING',checked_at=now())
 save(f'{candidate.lower()}_attempt{attempt}_diagnostics.json',out)
 permitted=['corr_uv','corr_uh','corr_vh','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','log_alpha_FTA','log_kappa']+(['theta_B','theta_W'] if candidate=='F2' else [])
 az.plot_trace(idata,var_names=permitted);plt.tight_layout();plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_mechanism_trace.png',dpi=130);plt.close('all')
 az.plot_energy(idata);plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_energy.png',dpi=130);plt.close('all')
 # No plot of the scientific coefficient, including no rank plot in Stage 3F.
 for group,names in [('accuracy',['beta_0','beta_H','beta_position','beta_season']),('positive',['a_0','a_H','a_position','a_season']),('hurdle',['c_0','c_H','c_position','c_season'])]:
  az.plot_trace(idata,var_names=names,compact=True);plt.tight_layout();plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_{group}_adjustment_traces.png',dpi=130);plt.close('all')
 print(json.dumps(out,indent=2))
if __name__=='__main__':
 from pathlib import Path
 p=argparse.ArgumentParser();p.add_argument('action',choices=['fit','diagnostics']);p.add_argument('candidate',choices=['F1','F2']);p.add_argument('--attempt',type=int,default=1);a=p.parse_args();fit(a.candidate,a.attempt) if a.action=='fit' else diagnostics(a.candidate,a.attempt)
