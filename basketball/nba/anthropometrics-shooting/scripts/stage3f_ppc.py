"""Fixed conditional accuracy and joint hurdle predictive checks."""
import argparse,pandas as pd,arviz as az
from scipy.special import logit,expit
from stage3f_common import *
from stage3f_model import build,pm
from stage3d_model import design
from stage3dr_ppc import metric_summary,opportunity_metrics
from stage3d_selection import accuracy_gate,opportunity_gate,systematic_volume_pattern
from stage3c_results import predictive_metrics

def op_metrics(n,d):
 out=opportunity_metrics(n,d);positive=n[n>0]
 assert len(positive)>0
 for q in [.25,.5,.75]:out['positive_FTA_q'+str(int(100*q))]=float(np.quantile(positive,q))
 out['positive_FTA_mean']=float(positive.mean());out['positive_FTA_SD']=float(positive.std(ddof=1))
 return out

def run(candidate,attempt):
 authorize();key=candidate.lower();diag=read(E/f'{key}_attempt{attempt}_diagnostics.json');visual=read(E/f'{key}_attempt{attempt}_visual_review.json');assert diag['numeric_gate_pass'] and visual['chains_mix'] and visual['energy_acceptable']
 diag.update(visual_review=visual,sampler_pass=True);save(key+'_diagnostics.json',diag)
 trace=az.from_netcdf(M/f'{key}_attempt{attempt}_trace.nc');post=trace.posterior
 allowed=['a_0','a_RW','a_H','a_position','a_season','c_0','c_RW','c_H','c_position','c_season','sigma_accuracy','sigma_positive_opportunity','sigma_hurdle','alpha_FTA','kappa']
 rows=[]
 for name in allowed:
  arr=post[name].values.reshape(post.sizes['chain']*post.sizes['draw'],-1)
  for j in range(arr.shape[1]):rows.append(dict(parameter=name if arr.shape[1]==1 else name+'['+str(post[name].coords[post[name].dims[-1]].values[j])+']',**summary(arr[:,j])))
 pd.DataFrame([{**r,'CI95_low':r['CI95'][0],'CI95_high':r['CI95'][1]} for r in rows]).drop(columns='CI95').to_csv(E/(key+'_opportunity_parameters.csv'),index=False)
 save(key+'_random_effect_correlations.json',{name:dict(**summary(post[name].values),P_positive=float((post[name].values>0).mean())) for name in ['corr_uv','corr_uh','corr_vh']})
 if candidate=='F2':save('f2_between_within_parameters.json',{name:summary(post[name].values) for name in ['theta_B','theta_W']})
 index=np.linspace(0,post.sizes['draw']-1,500,dtype=int)
 with build(candidate) as model:det=pm.compute_deterministics(post.isel(draw=index),var_names=['mu_accuracy_all','mu_FTA','pi_hurdle','kappa'],model=model,progressbar=False,compile_kwargs={'mode':'NUMBA'})
 mu=det.mu_accuracy_all.values.reshape(2000,-1);mean=det.mu_FTA.values.reshape(2000,-1);pi=det.pi_hurdle.values.reshape(2000,-1);k=det.kappa.values.reshape(-1);alpha=post.alpha_FTA.isel(draw=index).values.reshape(-1)
 d,_,idx,*_=design();d.combine_position=d.combine_position.fillna('unknown').replace('','unknown');n=d.fta.to_numpy(dtype=int);gp=d.games_played.to_numpy();mask=n>0;y=d.loc[mask].copy();obs=y.ftm.to_numpy(dtype=int);observed=predictive_metrics(obs,n[mask],y);observed['rate_mean']=float((obs/n[mask]).mean());observed_op=op_metrics(n,d);observed_op.update(joint_pooled_FT_rate=float(d.ftm.sum()/n.sum()),joint_total_FTM=float(d.ftm.sum()))
 if candidate=='F2':
  b,w,_,_=decomposition(n,gp,idx);tb=post.theta_B.isel(draw=index).values.reshape(-1);tw=post.theta_W.isel(draw=index).values.reshape(-1)
 rng=np.random.default_rng(20260929);rep=[];joint=[]
 for i in range(2000):
  acc=mu[i,mask];yr=rng.binomial(n[mask],rng.beta(acc*k[i],(1-acc)*k[i]));r=predictive_metrics(yr,n[mask],y);r['rate_mean']=float((yr/n[mask]).mean());rep.append(r)
  nr=rng.binomial(1,pi[i])*ztnb_random(mean[i],alpha[i],rng);joint_mu=mu[i]
  if candidate=='F2':
   rb,rw,_,_=decomposition(nr,gp,idx);joint_mu=expit(logit(mu[i])+tb[i]*(rb-b)+tw[i]*(rw-w))
  makes=rng.binomial(nr,rng.beta(joint_mu*k[i],(1-joint_mu)*k[i]));r=op_metrics(nr,d);r.update(joint_pooled_FT_rate=float(makes.sum()/nr.sum()),joint_total_FTM=float(makes.sum()));joint.append(r)
 cr=metric_summary(observed,rep);jr=metric_summary(observed_op,joint);pd.DataFrame(cr).to_csv(E/(key+'_conditional_PPC_metrics.csv'),index=False);pd.DataFrame(jr).to_csv(E/(key+'_joint_PPC_metrics.csv'),index=False)
 lookup={r['metric']:r for r in cr};bins=[lookup['FTA_'+label+'_pooled'] for _,_,label in BINS];fields=dict(pooled_rate_99_pass=not lookup['pooled_rate']['outside_99'],global_metrics_99_fail_count=sum(lookup[x]['outside_99'] for x in protocol()['PPC']['global_metrics']),season_rate_99_fail_count=sum(r['outside_99'] for r in cr if r['metric'].startswith('season_')),season_count=13,FTA_bin_99_fail_count=sum(r['outside_99'] for r in bins),systematic_volume_pattern=systematic_volume_pattern([r['observed'] for r in bins],[r['replicated_mean'] for r in bins],[r['MCSE_mean'] for r in bins]))
 review=read(E/(key+'_PPC_visual_review.json')) if (E/(key+'_PPC_visual_review.json')).exists() else 'PENDING'
 save(key+'_conditional_accuracy_ppc.json',dict(candidate=candidate,replicates=2000,seed=20260929,**fields,gate_pass=accuracy_gate(**fields),pooled_rate=lookup['pooled_rate'],bin_checks=bins,metrics_outside_99=[r['metric'] for r in cr if r['outside_99']],visual_review=review))
 lookup={r['metric']:r for r in jr};seas=[r for r in jr if r['metric'].startswith('season_') and r['metric'].endswith('_total')];fields=dict(zero_frequency_99_pass=not lookup['FTA_zero_fraction']['outside_99'],quantile_99_fail_count=sum(lookup['FTA_q'+str(q)]['outside_99'] for q in [25,50,75,90,95]),season_totals_outside_99_low=sum(r['observed']<r['predictive_99_low'] for r in seas),season_totals_outside_99_high=sum(r['observed']>r['predictive_99_high'] for r in seas),season_count=13);positive=[lookup['positive_FTA_q'+str(q)] for q in [25,50,75]];pfail=sum(r['outside_99'] for r in positive)
 save(key+'_joint_opportunity_ppc.json',dict(candidate=candidate,replicates=2000,seed=20260929,**fields,positive_quantile_99_fail_count=pfail,positive_quantiles=positive,base_opportunity_gate_pass=opportunity_gate(**fields),gate_pass=bool(opportunity_gate(**fields) and pfail<2),zero_frequency=lookup['FTA_zero_fraction'],quantiles=[lookup['FTA_q'+str(q)] for q in [25,50,75,90,95]],season_totals=seas,F2_generated_decomposition_recomputed=candidate=='F2',visual_review=review))
 print(candidate,'conditional',accuracy_gate(**{k:v for k,v in read(E/(key+'_conditional_accuracy_ppc.json')).items() if k in ['pooled_rate_99_pass','global_metrics_99_fail_count','season_rate_99_fail_count','season_count','FTA_bin_99_fail_count','systematic_volume_pattern']}),'joint',read(E/(key+'_joint_opportunity_ppc.json'))['gate_pass'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('candidate',choices=['F1','F2']);p.add_argument('--attempt',type=int,default=1);a=p.parse_args();run(a.candidate,a.attempt)
