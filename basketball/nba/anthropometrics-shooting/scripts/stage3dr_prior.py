"""One amended prior check; only predictive quantities are exported."""
from stage3dr_model import build,pm
from stage3dr_common import *
def main():
 a=amendment();assert sha(ROOT/'scripts/stage3dr_model.py')==a['model_code_sha256'];assert not (E/'amended_prior_predictive.json').exists();started=now()
 with build('D3'):
  prior=pm.sample_prior_predictive(draws=5000,var_names=['mu_FTA','FTA_count','mu_accuracy'],random_seed=20260928,compile_kwargs={'mode':'FAST_COMPILE'})
 d=fixed_data();rate=prior.prior.mu_FTA.values/d.games_played.to_numpy();counts=prior.prior_predictive.FTA_count.values;mu=prior.prior.mu_accuracy.values
 q=[.01,.05,.25,.5,.75,.95,.99,.999];tail=float((rate>100).mean());huge=float((counts>1000000).mean());finite=bool(np.isfinite(rate).all() and np.isfinite(counts).all());passed=finite and tail<=.01 and huge<=.001
 out=dict(started_at=started,completed_at=now(),draws=5000,seed=20260928,amendment_sha256=sha(E/'opportunity_prior_amendment.json'),implied_rate_quantiles={str(x):float(np.quantile(rate,x)) for x in q},simulated_FTA_quantiles={str(x):float(np.quantile(counts,x)) for x in q},maximum_simulated_FTA=int(counts.max()),maximum_implied_rate=float(rate.max()),fraction_rate_above_20=float((rate>20).mean()),fraction_rate_above_50=float((rate>50).mean()),fraction_rate_above_100=tail,fraction_simulated_above_1000000=huge,all_finite=finite,accuracy_prior_check=dict(finite=bool(np.isfinite(mu).all()),fraction_below_001=float((mu<.01).mean()),fraction_above_099=float((mu>.99).mean())),prior_gate_pass=passed)
 save('amended_prior_predictive.json',out);save('prior_gate_decision.json',dict(classification='PRIOR CALIBRATION PASSED' if passed else 'PRIOR CALIBRATION FAILED',passed=passed,frozen_at=now(),prior_result_sha256=sha(E/'amended_prior_predictive.json'),amendment_sha256=sha(E/'opportunity_prior_amendment.json'),thresholds_unchanged=True))
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
