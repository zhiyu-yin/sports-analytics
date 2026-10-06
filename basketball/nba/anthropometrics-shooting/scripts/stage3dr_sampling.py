"""Sampling and effect-blind convergence diagnostics."""
import argparse,time
import arviz as az
from stage3dr_model import build,pm
from stage3dr_common import *
def authorize():
 assert read(E/'prior_gate_decision.json')['passed'],'STOP: amended prior failed'
 assert sha(ROOT/'scripts/stage3dr_model.py')==amendment()['model_code_sha256']
def progress(trace,draw):
 if (draw.draw_idx+1)%500==0:print(f'chain={draw.chain} iteration={draw.draw_idx+1} tuning={draw.tuning}',flush=True)
def fit(candidate,attempt):
 authorize();a=amendment();s=a['sampling'][candidate].copy()
 if attempt==2:
  assert candidate=='D3' and not read(E/'d3_attempt1_diagnostics.json')['numeric_gate_pass'];s.update({k:a['D3_recovery'][k] for k in ['tune','draws','target_accept']})
 path=M/f'{candidate.lower()}_attempt{attempt}_trace.nc';assert not path.exists()
 record=dict(candidate=candidate,attempt=attempt,started_at=now(),settings=s,amendment_sha256=sha(E/'opportunity_prior_amendment.json'),model_code_sha256=sha(ROOT/'scripts/stage3dr_model.py'),sampling_code_sha256=sha(Path(__file__)),status='RUNNING',backend='PyMC NUTS / PyTensor NUMBA / spawn / one BLAS thread')
 save(f'{candidate.lower()}_attempt{attempt}_sampling.json',record);start=time.monotonic()
 try:
  model=build(candidate)
  # Keep the scientific coefficient protected in the ignored trace only.
  names=[x.name for x in model.unobserved_RVs if not x.name.startswith('mu_') and not(candidate=='D2' and x.name=='kappa')]
  with model:
   idata=pm.sample(draws=s['draws'],tune=s['tune'],chains=4,cores=4,random_seed=s['seed'],target_accept=s['target_accept'],nuts_sampler='pymc',blas_cores=1,mp_ctx='spawn',compile_kwargs={'mode':'NUMBA'},callback=progress,progressbar=False,var_names=names,idata_kwargs={'log_likelihood':False})
  idata.to_netcdf(path);record.update(status='COMPLETE',completed_at=now(),elapsed_seconds=time.monotonic()-start,trace_sha256=sha(path),trace_bytes=path.stat().st_size)
 except Exception as ex:record.update(status='FAILED',error=repr(ex));raise
 finally:save(f'{candidate.lower()}_attempt{attempt}_sampling.json',record)
def diagnostic_keys(candidate):
 keys=['beta_0','beta_RW','beta_H','beta_position','beta_season']
 if candidate=='D1':keys+=['sigma_player','log_kappa','kappa','gamma_FTA']
 if candidate=='D2':keys+=['sigma_player','gamma_0','gamma_k']
 if candidate=='D3':keys+=['a_0','a_RW','a_H','a_position','a_season','sigma_accuracy','sigma_opportunity','corr_uv','log_kappa','kappa','log_alpha_FTA','alpha_FTA']
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
 permitted=['gamma_FTA','sigma_player','log_kappa'] if candidate=='D1' else ['gamma_k','gamma_0','sigma_player'] if candidate=='D2' else ['corr_uv','sigma_accuracy','sigma_opportunity','log_alpha_FTA','log_kappa']
 az.plot_trace(idata,var_names=permitted);plt.tight_layout();plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_mechanism_trace.png',dpi=130);plt.close('all')
 az.plot_energy(idata);plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_energy.png',dpi=130);plt.close('all')
 # Rank histograms remove coefficient location and scale, including for the sealed variable.
 safe=idata.posterior[keys].rename({'beta_RW':'sealed_accuracy_parameter'})
 az.plot_rank(safe,var_names=['sealed_accuracy_parameter'],kind='bars');plt.tight_layout();plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_sealed_rank_mixing.png',dpi=130);plt.close('all')
 # Additional fixed-effect trace review excludes the sealed scientific slope.
 for group,names in [('accuracy',['beta_0','beta_H','beta_position','beta_season']),('opportunity',['a_0','a_H','a_position','a_season'])]:
  if group=='opportunity' and candidate!='D3':continue
  az.plot_trace(idata,var_names=names,compact=True);plt.tight_layout();plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_{group}_adjustment_traces.png',dpi=130);plt.close('all')
 print(json.dumps(out,indent=2))
if __name__=='__main__':
 from pathlib import Path
 p=argparse.ArgumentParser();p.add_argument('action',choices=['fit','diagnostics']);p.add_argument('candidate',choices=['D1','D2','D3']);p.add_argument('--attempt',type=int,default=1);a=p.parse_args();fit(a.candidate,a.attempt) if a.action=='fit' else diagnostics(a.candidate,a.attempt)
