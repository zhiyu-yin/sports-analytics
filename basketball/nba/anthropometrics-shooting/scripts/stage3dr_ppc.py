"""Effect-blind predictive checks and permitted mechanism summaries."""
import argparse
import pandas as pd,arviz as az
from stage3dr_model import build,pm
from stage3dr_common import *
from stage3d_selection import accuracy_gate,opportunity_gate,systematic_volume_pattern
from stage3c_results import predictive_metrics

def metric_summary(observed,replicates):
 rows=[]
 for name,value in observed.items():
  v=np.array([r[name] for r in replicates]);lo,hi=np.quantile(v,[.005,.995]);mcse=float(v.reshape(40,50).mean(axis=1).std(ddof=1)/np.sqrt(40))
  rows.append(dict(metric=name,observed=float(value),replicated_mean=float(v.mean()),predictive_99_low=float(lo),predictive_99_high=float(hi),outside_99=bool(value<lo or value>hi),MCSE_mean=mcse))
 return rows

def opportunity_metrics(n,d):
 out=dict(FTA_mean=float(n.mean()),FTA_SD=float(n.std(ddof=1)),FTA_zero_fraction=float((n==0).mean()))
 for q in [.25,.5,.75,.9,.95]:out[f'FTA_q{int(100*q)}']=float(np.quantile(n,q))
 for kind,col in [('season','season'),('position','combine_position')]:
  for level in sorted(d[col].unique()):
   v=n[(d[col]==level).to_numpy()];prefix=f'{kind}_{level}_';out[prefix+'total']=float(v.sum());out[prefix+'zero_fraction']=float((v==0).mean());out[prefix+'mean']=float(v.mean());out[prefix+'SD']=float(v.std(ddof=1)) if len(v)>1 else 0.
   for q in [.25,.5,.75,.9,.95]:out[prefix+f'q{int(100*q)}']=float(np.quantile(v,q))
 return out

def run(candidate,attempt):
 prefix=candidate.lower();diag=read(E/f'{prefix}_attempt{attempt}_diagnostics.json');visual=read(E/f'{prefix}_attempt{attempt}_visual_review.json');assert diag['numeric_gate_pass'] and visual['chains_mix'] and visual['energy_acceptable']
 diag['visual_review']=visual;diag['sampler_pass']=True;save(prefix+'_diagnostics.json',diag)
 trace=az.from_netcdf(M/f'{prefix}_attempt{attempt}_trace.nc');posterior=trace.posterior
 # Only explicitly permitted mechanism parameters receive summaries.
 if candidate=='D1':save('d1_attempt_volume_parameter.json',dict(parameter='gamma_FTA',**summary(posterior.gamma_FTA.values)))
 if candidate=='D2':
  g0=posterior.gamma_0.values.ravel();gk=posterior.gamma_k.values.ravel();center=protocol()['log1p_FTA_center']
  save('d2_dispersion_parameter.json',dict(parameter='gamma_k',**summary(gk),rho_at_FTA={str(n):summary(1/(1+np.exp(g0+gk*(np.log1p(n)-center)))) for n in [5,25,75,200,400]}))
 if candidate=='D3':
  corr=posterior.corr_uv.values;save('d3_random_effect_correlation.json',dict(parameter='corr_uv',**summary(corr),P_positive=float((corr>0).mean())))
  save('d3_opportunity_dispersion.json',dict(alpha_FTA=summary(posterior.alpha_FTA.values),sigma_opportunity=summary(posterior.sigma_opportunity.values),sigma_accuracy=summary(posterior.sigma_accuracy.values)))
 index=np.linspace(0,posterior.sizes['draw']-1,500,dtype=int)
 with build(candidate) as model:
  deterministic=pm.compute_deterministics(posterior.isel(draw=index),var_names=['mu_accuracy_all','kappa']+(['mu_FTA'] if candidate=='D3' else []),model=model,progressbar=False,compile_kwargs={'mode':'NUMBA'})
 # The scientific coefficient is consumed only inside the model's compiled prediction graph.
 mu=deterministic.mu_accuracy_all.values.reshape(2000,-1);kap=deterministic.kappa.values.reshape(2000,-1)
 d=fixed_data();d.combine_position=d.combine_position.fillna('unknown').replace('','unknown');mask=d.fta.to_numpy()>0;y=d.loc[mask].copy();n=y.fta.to_numpy(dtype=int);obs=y.ftm.to_numpy(dtype=int)
 observed=predictive_metrics(obs,n,y);observed['rate_mean']=float((obs/n).mean());rep=[];joint=[];rng=np.random.default_rng(20260929);minimum_alpha=np.inf;minimum_beta=np.inf
 if candidate=='D3':
  mean_FTA=deterministic.mu_FTA.values.reshape(2000,-1);alpha_FTA=posterior.alpha_FTA.isel(draw=index).values.reshape(-1)
 for i in range(2000):
  acc=mu[i,mask];k=kap[i];aa=acc*k;bb=(1-acc)*k;minimum_alpha=min(minimum_alpha,float(aa.min()));minimum_beta=min(minimum_beta,float(bb.min()));yp=rng.binomial(n,rng.beta(aa,bb));r=predictive_metrics(yp,n,y);r['rate_mean']=float((yp/n).mean());rep.append(r)
  if candidate=='D3':
   nr=rng.negative_binomial(alpha_FTA[i],alpha_FTA[i]/(alpha_FTA[i]+mean_FTA[i]));yr=rng.binomial(nr,rng.beta(mu[i]*k,(1-mu[i])*k));jr=opportunity_metrics(nr,d);jr['joint_pooled_FT_rate']=float(yr.sum()/nr.sum());jr['joint_total_FTM']=float(yr.sum());joint.append(jr)
 rows=metric_summary(observed,rep);pd.DataFrame(rows).to_csv(E/f'{prefix}_conditional_PPC_metrics.csv',index=False);lookup={r['metric']:r for r in rows};global_fail=sum(lookup[k]['outside_99'] for k in protocol()['PPC']['global_metrics']);season_fail=sum(r['outside_99'] for r in rows if r['metric'].startswith('season_'));bins=[lookup['FTA_'+label+'_pooled'] for _,_,label in BINS];bin_fail=sum(x['outside_99'] for x in bins);pattern=systematic_volume_pattern([x['observed'] for x in bins],[x['replicated_mean'] for x in bins],[x['MCSE_mean'] for x in bins])
 fields=dict(pooled_rate_99_pass=not lookup['pooled_rate']['outside_99'],global_metrics_99_fail_count=global_fail,season_rate_99_fail_count=season_fail,season_count=13,FTA_bin_99_fail_count=bin_fail,systematic_volume_pattern=pattern)
 out=dict(candidate=candidate,replicates=2000,seed=20260929,scope='Conditional accuracy at fixed observed attempts',**fields,gate_pass=accuracy_gate(**fields),pooled_rate=lookup['pooled_rate'],bin_checks=bins,metrics_outside_99=[r['metric'] for r in rows if r['outside_99']],minimum_alpha=minimum_alpha,minimum_beta=minimum_beta,visual_review=read(E/(prefix+'_PPC_visual_review.json')) if (E/(prefix+'_PPC_visual_review.json')).exists() else 'PENDING')
 save('d3_conditional_accuracy_ppc.json' if candidate=='D3' else prefix+'_ppc_summary.json',out)
 if candidate=='D3':
  observed_op=opportunity_metrics(d.fta.to_numpy(),d);observed_op.update(joint_pooled_FT_rate=float(d.ftm.sum()/d.fta.sum()),joint_total_FTM=float(d.ftm.sum()));jrows=metric_summary(observed_op,joint);pd.DataFrame(jrows).to_csv(E/'d3_joint_PPC_metrics.csv',index=False);look={r['metric']:r for r in jrows};qfails=sum(look['FTA_q'+str(q)]['outside_99'] for q in [25,50,75,90,95]);seas=[r for r in jrows if r['metric'].startswith('season_') and r['metric'].endswith('_total')];low=sum(r['observed']<r['predictive_99_low'] for r in seas);high=sum(r['observed']>r['predictive_99_high'] for r in seas)
  jf=dict(zero_frequency_99_pass=not look['FTA_zero_fraction']['outside_99'],quantile_99_fail_count=qfails,season_totals_outside_99_low=low,season_totals_outside_99_high=high,season_count=13)
  save('d3_joint_opportunity_ppc.json',dict(replicates=2000,seed=20260929,scope='Joint FTA then FTM generation; conditional accuracy gate kept separate',**jf,gate_pass=opportunity_gate(**jf),zero_frequency=look['FTA_zero_fraction'],quantiles=[look['FTA_q'+str(q)] for q in [25,50,75,90,95]],season_totals=seas,position_PPC_descriptive_only=True,minimum_mu_FTA=float(mean_FTA.min()),minimum_alpha_FTA=float(alpha_FTA.min()),visual_review=read(E/(prefix+'_PPC_visual_review.json')) if (E/(prefix+'_PPC_visual_review.json')).exists() else 'PENDING'))
 print(json.dumps(out,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('candidate',choices=['D1','D2','D3']);p.add_argument('--attempt',type=int,default=1);a=p.parse_args();run(a.candidate,a.attempt)
