"""Frozen 5000-draw prior check; no outcome matching or coefficient exports."""
from stage3f_common import *
from stage3f_model import build,pm

def main():
 p=protocol();assert not (E/'prior_predictive_summary.json').exists();started=now();d=fixed_data();results={}
 for candidate in ['F1','F2']:
  with build(candidate):prior=pm.sample_prior_predictive(draws=5000,random_seed=20260928,var_names=['mu_FTA','pi_hurdle','mu_accuracy_all','alpha_FTA'],compile_kwargs={'mode':'FAST_COMPILE'})
  mu=prior.prior.mu_FTA.values.reshape(5000,-1);pi=prior.prior.pi_hurdle.values.reshape(5000,-1);alpha=prior.prior.alpha_FTA.values.reshape(5000,1);acc=prior.prior.mu_accuracy_all.values.reshape(5000,-1)
  rate=mu/(-np.expm1(-alpha*np.log1p(mu/alpha)))/d.games_played.to_numpy();base=mu/d.games_played.to_numpy();rng=np.random.default_rng(20260928);counts=np.empty(mu.shape,dtype=np.int64)
  for start in range(0,5000,50):
   sl=slice(start,start+50);positive=ztnb_random(mu[sl],alpha[sl],rng);counts[sl]=rng.binomial(1,pi[sl])*positive
  zeros=(counts==0).mean(axis=1);extreme=float(((zeros<.001)|(zeros>.5)).mean());rate_fail=float((rate>100).mean());huge=float((counts>1000000).mean());q=[.01,.05,.25,.5,.75,.95,.99,.999]
  result=dict(draws=5000,seed=20260928,positive_rate_quantiles=dict(zip(map(str,q),np.quantile(rate,q).tolist())),base_rate_quantiles=dict(zip(map(str,q),np.quantile(base,q).tolist())),total_FTA_quantiles=dict(zip(map(str,q),np.quantile(counts,q).tolist())),maximum_FTA=int(counts.max()),fraction_positive_rate_over_100=rate_fail,fraction_total_FTA_over_1000000=huge,zero_fraction_95_interval=np.quantile(zeros,[.025,.975]).tolist(),zero_fraction_median=float(np.median(zeros)),zero_fraction_extreme_mass=extreme,zero_fraction_below_001_mass=float((zeros<.001).mean()),zero_fraction_above_50_mass=float((zeros>.5).mean()),finite=bool(np.isfinite(mu).all() and np.isfinite(pi).all() and np.isfinite(acc).all()),accuracy_fraction_below_001=float((acc<.01).mean()),accuracy_fraction_above_099=float((acc>.99).mean()),numeric_pass=bool(rate_fail<=.01 and huge<=.001 and extreme<=.9 and np.isfinite(rate).all()))
  results[candidate]=result;save(candidate.lower()+'_prior_predictive.json',result);print(candidate,'numeric prior pass',result['numeric_pass'],flush=True)
  del prior,mu,pi,alpha,acc,rate,base,counts
 save('prior_predictive_summary.json',dict(started_at=started,completed_at=now(),protocol_sha256=sha(E/'model_protocol.json'),candidates=results,numeric_pass=all(v['numeric_pass'] for v in results.values()),wide_range_review='PENDING',passed=False,status='AWAITING_PROSPECTIVE_WIDE_RANGE_REVIEW'))
if __name__=='__main__':main()
