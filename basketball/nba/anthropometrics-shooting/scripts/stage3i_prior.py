"""Prospective prior screen, with no coefficient draws exported."""
from stage3i_common import *
from stage3i_model import build,pm

def run(candidate):
 authorize();assert not list(M.glob('*trace.nc'))
 target=E/(candidate.lower()+'_prior_predictive.json');assert not target.exists()
 started=now();d=fixed_data()
 with build(candidate):prior=pm.sample_prior_predictive(draws=5000,random_seed=20260930,var_names=['mu_FTA','pi_hurdle','mu_accuracy_all','alpha_FTA'],compile_kwargs={'mode':'FAST_COMPILE'})
 mu=prior.prior.mu_FTA.values.reshape(5000,-1);pi=prior.prior.pi_hurdle.values.reshape(5000,-1);alpha=prior.prior.alpha_FTA.values.reshape(5000,1);acc=prior.prior.mu_accuracy_all.values.reshape(5000,-1)
 rate=mu/(-np.expm1(-alpha*np.log1p(mu/alpha)))/d.games_played.to_numpy();rng=np.random.default_rng(20260930);counts=np.empty(mu.shape,dtype=np.int64)
 for start in range(0,5000,50):
  sl=slice(start,start+50);counts[sl]=rng.binomial(1,pi[sl])*ztnb_random(mu[sl],alpha[sl],rng)
 zeros=(counts==0).mean(axis=1);extreme=float(((zeros<.001)|(zeros>.5)).mean());rate_fail=float((rate>100).mean());huge=float((counts>1000000).mean());low=float((acc<.01).mean());high=float((acc>.99).mean());finite=bool(np.isfinite(rate).all() and np.isfinite(pi).all() and np.isfinite(acc).all());q=[.01,.05,.25,.5,.75,.95,.99,.999]
 result=dict(candidate=candidate,started_at=started,completed_at=now(),draws=5000,seed=20260930,positive_rate_quantiles=dict(zip(map(str,q),np.quantile(rate,q).tolist())),total_FTA_quantiles=dict(zip(map(str,q),np.quantile(counts,q).tolist())),maximum_FTA=int(counts.max()),fraction_positive_rate_over_100=rate_fail,fraction_total_FTA_over_1000000=huge,zero_fraction_95_interval=np.quantile(zeros,[.025,.975]).tolist(),zero_fraction_median=float(np.median(zeros)),zero_fraction_extreme_mass=extreme,accuracy_fraction_below_001=low,accuracy_fraction_above_099=high,accuracy_probability_quantiles=dict(zip(map(str,q),np.quantile(acc,q).tolist())),finite=finite,numeric_pass=bool(rate_fail<=.01 and huge<=.001 and extreme<=.9 and finite and low<=.25 and high<=.25),wide_range_review='PENDING',passed=False,scientific_parameter_summary_exported=False)
 save(target.name,result);print(candidate,'prior numeric pass',result['numeric_pass'],flush=True)
if __name__=='__main__':
 import sys
 run(sys.argv[1])
