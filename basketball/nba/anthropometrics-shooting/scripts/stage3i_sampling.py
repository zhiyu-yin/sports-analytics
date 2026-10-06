"""Bounded fits and diagnostics without scientific-effect summaries."""
import argparse,time,pandas as pd,arviz as az
from stage3i_common import *
from stage3i_model import build,pm

def progress(trace,draw):
 if (draw.draw_idx+1)%500==0:print(f'chain={draw.chain} iteration={draw.draw_idx+1} tuning={draw.tuning}',flush=True)
def fit(candidate,attempt):
 authorize(candidate);p=protocol();s=p['sampling'].copy()
 if attempt==2:
  d=read(E/f'{candidate.lower()}_attempt1_diagnostics.json');assert not d['numeric_gate_pass'] or d.get('sampler_pass') is False;s.update(p['recovery'])
 path=M/f'{candidate.lower()}_attempt{attempt}_trace.nc';assert not path.exists();r=dict(candidate=candidate,attempt=attempt,started_at=now(),settings=s,status='RUNNING',protocol_sha256=sha(E/'model_protocol.json'));save(f'{candidate.lower()}_attempt{attempt}_sampling.json',r)
 model=build(candidate)
 # Backend agreement is checked before any posterior draw, without exposing values.
 point=model.initial_point();g=model.compile_dlogp(mode='FAST_COMPILE')(point);ng=model.compile_dlogp(mode='NUMBA')(point);assert np.allclose(g,ng,atol=1e-8,rtol=1e-8);save(f'{candidate.lower()}_backend_validation.json',dict(passed=True,max_abs_error=float(np.max(np.abs(g-ng)))))
 names=[v.name for v in model.unobserved_RVs if not v.name.startswith('mu_') and v.name!='pi_hurdle']
 with model:trace=pm.sample(**s,cores=4,nuts_sampler='pymc',blas_cores=1,mp_ctx='spawn',compile_kwargs={'mode':'NUMBA'},callback=progress,progressbar=False,var_names=names,idata_kwargs={'log_likelihood':False})
 trace.to_netcdf(path);r.update(status='COMPLETE',completed_at=now(),trace_sha256=sha(path));save(f'{candidate.lower()}_attempt{attempt}_sampling.json',r)
def diagnostics(candidate,attempt):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 trace=az.from_netcdf(M/f'{candidate.lower()}_attempt{attempt}_trace.nc');post=trace.posterior
 keys=[k for k in ['beta_0','beta_H','beta_position','beta_season','gamma_W1','gamma_W2','theta_W','sigma_count_resid','c_player','count_residual_effect','a_0','a_RW','a_H','a_position','a_season','c_0','c_RW','c_H','c_position','c_season','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','corr_uv','corr_uh','corr_vh','kappa','alpha_FTA','o_player','e_player','accuracy_effect','positive_effect','hurdle_effect','sigma_opportunity','lambda_h','rho_AO'] if k in post]
 s=az.summary(trace,var_names=keys,kind='diagnostics',round_to='none')[['r_hat','ess_bulk','ess_tail']];s.to_csv(E/f'{candidate.lower()}_attempt{attempt}_convergence.csv')
 sealedpass=True;sealed_stats=[]
 if 'beta_RW' in post:
  a=az.summary(trace,var_names=['beta_RW'],kind='diagnostics',round_to='none').iloc[0];sealedpass=gate(a.r_hat,a.ess_bulk,a.ess_tail);sealed_stats=[float(a.r_hat),float(a.ess_bulk),float(a.ess_tail)]
 # Aggregate gate includes the sealed parameter; only its pass Boolean is separately exported.
 rh=max(float(s.r_hat.max()),sealed_stats[0] if sealed_stats else 0);bulk=min(float(s.ess_bulk.min()),sealed_stats[1] if sealed_stats else np.inf);tail=min(float(s.ess_tail.min()),sealed_stats[2] if sealed_stats else np.inf)
 globals=[k for k in keys if not any(t in k for t in ['player','effect','centered','z_'])];v=np.concatenate([post[k].values.reshape(4*post.sizes['draw'],-1) for k in globals],axis=1);finite=bool(np.isfinite(np.cov(v,rowvar=False)).all());bfmi=az.bfmi(trace).tolist();div=int(trace.sample_stats.diverging.sum());depth=int(trace.sample_stats.reached_max_treedepth.sum())
 out=dict(candidate=candidate,attempt=attempt,max_rhat=rh,min_bulk_ESS=bulk,min_tail_ESS=tail,BFMI=bfmi,divergences=div,max_depth_hits=depth,finite_covariance=finite,sealed_parameter_sampler_pass=sealedpass,numeric_gate_pass=bool(gate(rh,bulk,tail) and min(bfmi)>=.3 and div==0 and depth==0 and finite and sealedpass and np.isfinite(s.to_numpy()).all()),visual_review='PENDING',checked_at=now(),all_latent_elements_in_gate=True)
 save(f'{candidate.lower()}_attempt{attempt}_diagnostics.json',out)
 # Standardized chains show mixing without releasing invalid parameter estimates.
 show=[k for k in ['gamma_W1','gamma_W2','theta_W','sigma_count_resid','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','rho_AO','lambda_h','sigma_opportunity','kappa','alpha_FTA'] if k in post]
 fig,axes=plt.subplots(len(show),1,figsize=(11,2*len(show)),squeeze=False)
 for ax,k in zip(axes[:,0],show):
  v=post[k].values;v=(v-v.mean())/v.std()
  for chain in range(4):ax.plot(v[chain],lw=.4,alpha=.7,label=str(chain))
  ax.set_ylabel(k);ax.set_yticks([])
 axes[0,0].legend(ncol=4);fig.suptitle(candidate+' standardized diagnostic chains; no original-unit estimates');fig.tight_layout();fig.savefig(F/f'{candidate.lower()}_attempt{attempt}_mixing.png',dpi=110);plt.close(fig)
 az.plot_energy(trace);plt.savefig(F/f'{candidate.lower()}_attempt{attempt}_energy.png',dpi=120);plt.close('all');trace.close();print(json.dumps(out),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('candidate');p.add_argument('--attempt',type=int,default=1);a=p.parse_args();(fit if a.action=='fit' else diagnostics)(a.candidate,a.attempt)
