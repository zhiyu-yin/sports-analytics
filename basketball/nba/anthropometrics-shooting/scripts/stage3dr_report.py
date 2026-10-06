"""Report only frozen adequacy and explicitly permitted mechanism results."""
from stage3dr_common import *
import csv
def fmt(x):
 if 'mean' not in x:return x.get('status','UNAVAILABLE')+'; '+x.get('reason','')
 return f"mean {x['mean']:.6f}, median {x['median']:.6f}, SD {x['SD']:.6f}, 95% equal-tail CrI [{x['CI95'][0]:.6f}, {x['CI95'][1]:.6f}]"
def sampler(d):
 return f"max R-hat {d['max_rhat']:.6f}; minimum bulk/tail ESS {d['min_bulk_ESS']:.1f}/{d['min_tail_ESS']:.1f}; divergences {d['divergences']}; max-depth hits {d['max_depth_hits']}; minimum BFMI {min(d['BFMI']):.3f}; sampler pass {d.get('sampler_pass',False)}"
def ppc(x):
 if x.get('replicates',0)==0:return x.get('status','NOT_RUN')+' — '+x.get('reason','')
 return f"pooled-rate 99% pass {x['pooled_rate_99_pass']}; global failures {x['global_metrics_99_fail_count']}; season failures {x['season_rate_99_fail_count']}/13; FTA-bin failures {x['FTA_bin_99_fail_count']}/5; systematic low/high pattern {x['systematic_volume_pattern']}; conditional gate pass {x['gate_pass']}"
def main():
 r=read(E/'model_adequacy_decision.json');a=amendment();prior=read(E/'amended_prior_predictive.json');gate=read(E/'prior_gate_decision.json');d={k:read(E/(k+'_diagnostics.json')) for k in ['d1','d2','d3']};cp={k:read(E/('d3_conditional_accuracy_ppc.json' if k=='d3' else k+'_ppc_summary.json')) for k in d};joint=read(E/'d3_joint_opportunity_ppc.json');corr=read(E/'d3_random_effect_correlation.json');g1=read(E/'d1_attempt_volume_parameter.json');g2=read(E/'d2_dispersion_parameter.json');test=read(E/'test_summary.json') if (E/'test_summary.json').exists() else {};p=protocol()
 jointtext=(f"Joint gate pass {joint['gate_pass']}; zero-frequency 99% pass {joint['zero_frequency_99_pass']}; quantile failures {joint['quantile_99_fail_count']}/5; season totals below/above 99% intervals {joint['season_totals_outside_99_low']}/{joint['season_totals_outside_99_high']}." if joint.get('replicates',0) else joint.get('status','NOT_RUN'))
 jointtable=''
 positiontable=''
 if joint.get('replicates',0):
  jointtable='| Opportunity metric | Observed | Replicated mean | 99% predictive interval | Outside 99% |\n|---|---:|---:|---|---|\n'
  for v in [joint['zero_frequency']]+joint['quantiles']:
   jointtable+=f"| {v['metric']} | {v['observed']:.6f} | {v['replicated_mean']:.6f} | [{v['predictive_99_low']:.6f}, {v['predictive_99_high']:.6f}] | {v['outside_99']} |\n"
  with (E/'d3_joint_PPC_metrics.csv').open() as f:metrics={v['metric']:v for v in csv.DictReader(f)}
  positiontable='Descriptive position checks (not additional gates):\n\n| Position | Observed mean FTA | Predictive mean FTA | Observed zero % | Predictive zero % | Zero % 99% interval |\n|---|---:|---:|---:|---:|---|\n'
  for name,z in metrics.items():
   if not(name.startswith('position_') and name.endswith('_zero_fraction')):continue
   label=name.removeprefix('position_').removesuffix('_zero_fraction');m=metrics['position_'+label+'_mean']
   positiontable+=f"| {label} | {float(m['observed']):.2f} | {float(m['replicated_mean']):.2f} | {float(z['observed'])*100:.3f} | {float(z['replicated_mean'])*100:.3f} | [{float(z['predictive_99_low'])*100:.3f}, {float(z['predictive_99_high'])*100:.3f}] |\n"
 bins=''
 if cp['d3'].get('replicates'):
  bins='| FTA bin | Observed FT% | Replicated mean FT% | 99% predictive interval | Outside 99% | MCSE of mean, pp |\n|---|---:|---:|---|---|---:|\n'
  for b in cp['d3']['bin_checks']:bins+=f"| {b['metric'].removeprefix('FTA_').removesuffix('_pooled')} | {b['observed']*100:.4f} | {b['replicated_mean']*100:.4f} | [{b['predictive_99_low']*100:.4f}, {b['predictive_99_high']*100:.4f}] | {b['outside_99']} | {b['MCSE_mean']*100:.5f} |\n"
 rhotext='; '.join(f"FTA {n}: {fmt(x)}" for n,x in g2.get('rho_at_FTA',{}).items()) or 'Not released because the candidate sampler gate failed.'
 text=f'''# Stage 3D-R — Opportunity Prior Calibration and Adequacy

**{r['classification']}**. Prior calibration: **{gate['classification']}**. Selected future model: **{r['selected_future_model']}**. Stage 3E authorized: **{r['stage3e_authorized']}**. The scientific wingspan coefficient remains sealed; no scientific replication conclusion is made.

## 1. Historical Stage 3D prior failure

Stage 3D permanently remains ADEQUACY UNRESOLVED — D3 FAILS PRIOR-PREDICTIVE PREREQUISITE. Its original opportunity prior placed approximately 9.3% of mean rates above 100 attempts/game and generated extreme season-count tails. No Stage 3D candidate posterior existed. Stage 3C also permanently remains EXECUTION FAIL — PRIMARY PPC ADEQUACY GATE FAILED. Neither historical decision has been overwritten.

The D0 comparison reuses its saved 1,000-replicate PPC without refitting. Its saved global count omits rate mean, which was not available in that artifact; the D0 global count therefore has a narrower basis than the new candidates. Its saved pooled-rate and four-bin failures remain independently decisive.

## 2. Why a prospective prior amendment is justified

The user authorized one new opportunity-prior specification to address gross scale behavior before any D3 posterior had been fitted. The likelihood and informative-opportunity hypothesis are unchanged. The dated amendment was frozen at {a['frozen_at']} with SHA256 `{sha(E/'opportunity_prior_amendment.json')}`. All prior artifacts are protected by hashes.

## 3. Why this is not posterior/result-driven tuning

No D3 scientific coefficient, latent correlation or posterior predictive result existed before this amendment. Prior constants came directly from the authorized natural-rate specification, not observed FTA quantiles or an optimization of posterior fit. The sole amended prior was simulated once with the frozen seed; no second amendment was made. Sampling and adequacy decisions do not use the scientific effect's location, direction, uncertainty or probability.

## 4. Rate-scale prior interpretation

The opportunity linear predictor excluding log(GP) is log expected FTA/game. The new baseline log rate is Normal(log(2),1): median 2 FTA/game and approximate 95% interval [{a['rate_interpretation']['baseline_95_interval'][0]:.3f}, {a['rate_interpretation']['baseline_95_interval'][1]:.3f}], before covariates/player effects. A log-rate increment of 0.15 multiplies rate by {a['rate_interpretation']['per_unit_multiplier_at_015']:.3f}; a player-effect SD of 0.5 corresponds to a one-SD multiplier of {a['rate_interpretation']['opportunity_SD_05_multiplier']:.3f}. The tighter priors are more regularizing than the original log-scale priors; they reduce exponentiated tail dispersion.

## 5. New frozen opportunity priors

Intercept Normal(log(2),1); raw residual-exposure and centered-height slopes Normal(0,0.15); position effects Normal(0,0.35); season effects Normal(0,0.25); opportunity SD HalfNormal(0.5). Log alpha_FTA ~ Normal(log(2),1), alpha_FTA=exp(log alpha_FTA). This one-to-one transform preserves the NB2 likelihood, whose variance is mu+mu²/alpha, but deliberately changes its prior from HalfNormal(5) to lognormal.

Accuracy priors remain exactly frozen: intercept Normal(0,2.5), exposure/height slopes Normal(0,0.5), original position/season terms Normal(0,1), accuracy SD HalfNormal(1), log precision Normal(3,2). LKJ eta remains 2. D1/D2 priors and models are unchanged. No prior was modified after simulation or sampling.

## 6. Prior predictive results

5,000 draws; seed 20260928. Implied FTA/game mean-rate quantiles: {', '.join(f"Q{float(q)*100:g}={v:.4f}" for q,v in prior['implied_rate_quantiles'].items())}. Fractions above 20, 50 and 100/game: {prior['fraction_rate_above_20']:.6%}, {prior['fraction_rate_above_50']:.6%}, {prior['fraction_rate_above_100']:.6%}.

Simulated season FTA quantiles: {', '.join(f"Q{float(q)*100:g}={v:,.2f}" for q,v in prior['simulated_FTA_quantiles'].items())}. Maximum simulated season count={prior['maximum_simulated_FTA']:,}; maximum implied rate={prior['maximum_implied_rate']:,.2f}/game. Fraction above one million season attempts={prior['fraction_simulated_above_1000000']:.10%}. Extreme tails remain possible; a gross-gate pass is not a claim of a tightly realistic prior. Descriptive extra thresholds do not determine release.

## 7. Prior gate decision

Both unchanged gates passed: mean-rate mass above 100/game≤1%, and simulated season-count mass above one million≤0.1%. Values were finite. The unchanged accuracy prior also remains broad, with lower/upper near-boundary fractions {prior['accuracy_prior_check']['fraction_below_001']:.4%}/{prior['accuracy_prior_check']['fraction_above_099']:.4%}. The prior decision was frozen before D1/D2/D3 sampling began. No observed FTA quantile was used to choose priors.

## 8. D1 diagnostic result

D1 adds centered log(1+FTA) only as a diagnostic accuracy-mean term. Four chains, 1,500 tuning and 1,500 retained draws each, target acceptance 0.95. {sampler(d['d1'])}. Mean-volume parameter: {fmt(g1)}. Conditional accuracy assessment: {ppc(cp['d1'])}.

D1 changes the conditioning set and cannot become the future scientific model. No recovery for D1 was authorized by the frozen plan; a failed ESS threshold is not rounded into a pass.

## 9. D2 diagnostic result

D2 keeps the accuracy mean and makes log precision linear in centered log(1+FTA). Four chains, 1,500 tuning and 1,500 retained draws each, target acceptance 0.95. {sampler(d['d2'])}. Dispersion-volume parameter: {fmt(g2)}. Representative rho summaries: {rhotext}

Conditional accuracy assessment: {ppc(cp['d2'])}. D2 remains diagnostic only, regardless of its performance. No scientific coefficient is extracted for comparison.

## 10. D3 joint model

The opportunity model is negative binomial with log(GP) fixed at coefficient one, the same frozen raw residual exposure, centered height, original position and season terms, and a player opportunity intercept. The accuracy model is beta-binomial for FTM out of observed positive FTA with the unchanged covariates and player accuracy intercept. Realized FTA is not added to the D3 accuracy mean.

Player accuracy/opportunity effects remain non-centered bivariate normal through LKJCholeskyCov. All 4,117 accounting rows enter opportunity; 3,980 positive-FTA rows enter accuracy. GP is positive and validated against the preserved official audit; no minutes are used. The 13-season primary panel excludes 2013–14, retains all 857 players and 469,099 FTA, and matches SHA256 `{EXPECTED}`. The height center and log-volume center remain {p['height_center']:.14f} and {p['log1p_FTA_center']:.15f}.

## 11. D3 sampler diagnostics

{sampler(d['d3'])}. Final attempt={d['d3']['attempt']}. Initial plan: four chains × 2,000 tuning and 2,000 retained, target acceptance 0.95, seed 20260928. Only the frozen generic D3 recovery may increase these to 4,000/4,000 and 0.99; every attempt is retained. No statistical structure or prior changed for recovery.

Numerical gates include every major accuracy/opportunity position and season term, dispersion, both SDs and latent correlation. The sealed coefficient contributes anonymous rank/convergence checks only. Its raw trace, location and scale are not published. Visual mixing and energy reviews accompany any sampler pass. Compiled D3 gradients matched the reference at the initial point within rtol=atol=1e-8; PyMC NUTS remains the sampler.

## 12. Conditional accuracy PPC

{ppc(cp['d3'])}. The conditional assessment uses exactly 2,000 predictive replications with observed FTA fixed and the joint posterior. The gate fails for pooled rate outside 99%, ≥3 global metrics outside 99%, ≥5 of 13 season rates outside 99%, ≥2 of five FTA bins outside 99%, or the frozen opposite low/high-volume pattern beyond Monte Carlo uncertainty.

Global metrics: rate mean, SD, Q05, Q50, Q95, zero fraction and perfect fraction. Within-player repeated-season variability is checked separately. The pattern rule compares bin predictive-mean bias with 2.576 times MCSE, using 40 consecutive batches of 50 replications in chain-major order. Predictive intervals and Monte Carlo uncertainty have different roles and are not interchanged.

{bins}

![Frozen-bin accuracy checks](<{ROOT}/docs/stage3dr_figures/01_FTA_bin_accuracy.png>)

## 13. Joint opportunity PPC

{jointtext} This simulation first generates attempts, then makes conditional on generated attempts and the same correlated player draw. It is distinct from the conditional accuracy release gate. Frozen opportunity failure rules: zero frequency outside 99%; at least three of five count quantiles outside 99%; or at least five season totals outside 99% in the same direction. Original-position count distributions and joint makes/rates are descriptive additional checks, not alternative selection criteria. Detailed zero-frequency, quantile, season and position metrics are saved in the joint evidence table.

{jointtable}

{positiontable}

## 14. Latent opportunity–accuracy correlation

{fmt(corr)}. P(corr_uv>0)={corr.get('P_positive','UNAVAILABLE')}, estimated as the fraction of retained draws above zero; a value of one is Monte Carlo resolution, not mathematical certainty. A positive value means that greater persistent opportunity-per-game tendency accompanies greater persistent accuracy tendency under this model; a negative value means the opposite. This is an associational latent parameter. No causal claim is made. A correlation result does not override failed predictive or sampler gates.

## 15. Model-adequacy decision

Frozen at {r['frozen_at']}: **{r['classification']}**. Future model={r['selected_future_model']}. The selection function receives only typed Boolean gate records; permitted mechanism summaries are appended after the selection calculation, not supplied to it. D1/D2 cannot authorize future inference. No scientific-effect summary, p-value, AIC, WAIC or LOO determines selection. No D4, spline, hurdle, zero-inflation, interaction or new covariate was introduced.

## 16. Stage 3E authorization

Authorization={r['stage3e_authorized']}; scientific parameter status={r['scientific_parameter_status']}. This is a recorded future-stage decision, not execution of Stage 3E. The scientific wingspan coefficient remains sealed in local ignored traces; no effect sign, mean, median, SD, interval, odds ratio, probability or wingspan contrast appears in this report or the comparison/decision artifacts.

## 17. Remaining limitations

Gross prior calibration does not prove model adequacy. D1 directly conditions on realized attempts and changes interpretation. The joint model assumes the specified count families, linear predictors and bivariate player-effect distribution; a persistent correlation need not represent within-player opportunity/accuracy dependence. Measurement coverage remains approximately 51%–67%, with selection into combine measurement, NBA survival and playing opportunity uncorrected. Scientific time-invariant exposure identification remains between-player and is not causally identified. No model has been chosen by its scientific coefficient.

> {p['minute_limitation']}

## 18. Reproducibility

Reuse of the pinned Stage 3C environment introduces no package changes. Amendment, panel and code hashes, prior timing, all sampler settings, traces and diagnostic/PPC artifacts are recorded in the manifest. Posterior traces are Git-ignored and contain sealed parameters needed for computation. Predictive code obtains probabilities from compiled model deterministics rather than exporting the scientific slope. Only explicitly permitted volume/dispersion/correlation parameters receive summaries.

Run order: setup once; amended prior check; candidate fitting and numerical diagnostics; visual diagnostic review; conditional/joint PPC; adequacy decision freeze; report; final verification. Historical scripts were not rerun. Verification tests: {test.get('tests_passed','pending')}/{test.get('tests_run','pending')}. Saved-trace predictive replay is recorded separately. Tests distinguish code/provenance correctness from model adequacy. No FTA threshold filtering, full-panel fit, new confounder, causal claim, commit, push or Stage 3E execution occurred.
'''
 (ROOT/'docs/stage3dr_opportunity_prior_and_adequacy.md').write_text(text)
if __name__=='__main__':main()
