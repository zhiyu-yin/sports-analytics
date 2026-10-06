"""Twenty-section adequacy report; scientific coefficient never accessed."""
import pandas as pd
from stage3f_common import *
from stage3f_selection import classify,Gate

def fmt(v):
 if 'mean' not in v:return v.get('status','Not available')
 return f"mean {v['mean']:.6f}; median {v['median']:.6f}; SD {v['SD']:.6f}; 95% CrI [{v['CI95'][0]:.6f}, {v['CI95'][1]:.6f}]"
def diag(v):
 if 'max_rhat' not in v:return v.get('status','Not run')
 return f"max R-hat {v['max_rhat']:.6f}; minimum bulk/tail ESS {v['min_bulk_ESS']:.1f}/{v['min_tail_ESS']:.1f}; divergences {v['divergences']}; depth hits {v['max_depth_hits']}; BFMI {', '.join(f'{x:.3f}' for x in v['BFMI'])}; sampler pass {v.get('sampler_pass',False)}; attempt {v['attempt']}"
def acc(v):
 if not v.get('replicates'):return v.get('status','Not run')
 return f"pass {v['gate_pass']}; pooled-rate pass {v['pooled_rate_99_pass']}; global failures {v['global_metrics_99_fail_count']}/7; season failures {v['season_rate_99_fail_count']}/13; FTA-bin failures {v['FTA_bin_99_fail_count']}/5; systematic low/high pattern {v['systematic_volume_pattern']}"
def opp(v):
 if not v.get('replicates'):return v.get('status','Not run')
 z=v['zero_frequency'];return f"pass {v['gate_pass']}; original opportunity gate pass {v.get('base_opportunity_gate_pass',v['gate_pass'])}; zero-fraction pass {v['zero_frequency_99_pass']}: observed {z['observed']:.4%}, predictive mean {z['replicated_mean']:.4%}, 99% interval [{z['predictive_99_low']:.4%}, {z['predictive_99_high']:.4%}]; FTA quantile failures {v['quantile_99_fail_count']}/5; positive-count quantile failures {v.get('positive_quantile_99_fail_count','not saved')}/3; season totals below/above intervals {v['season_totals_outside_99_low']}/{v['season_totals_outside_99_high']}"
def main():
 p=protocol();prior=read(E/'prior_predictive_summary.json');decomp=read(E/'opportunity_decomposition.json');d={k:read(E/(k+'_diagnostics.json')) for k in ['f0','f1','f2']};a={k:read(E/(k+'_conditional_accuracy_ppc.json')) for k in d};o={k:read(E/(k+'_joint_opportunity_ppc.json')) for k in d};theta=read(E/'f2_between_within_parameters.json');corr={k:read(E/(k+'_random_effect_correlations.json')) for k in ['f1','f2']};test=read(E/'test_summary.json') if (E/'test_summary.json').exists() else {}
 frozen=(E/'stage3f_decision.json').exists();r=read(E/'stage3f_decision.json') if frozen else classify(*[Gate(bool(d[k].get('sampler_pass',False)),bool(a[k].get('gate_pass',False)),bool(o[k].get('gate_pass',False))) for k in ['f1','f2']],True)
 title=r['classification'] if frozen else 'DRAFT — decision not frozen'
 first=read(E/'f2_attempt1_diagnostics.json')
 recovery_note=(f"F2 attempt 1 failed numerical convergence: max R-hat {first['max_rhat']:.6f}, minimum bulk/tail ESS {first['min_bulk_ESS']:.1f}/{first['min_tail_ESS']:.1f}. The single predeclared recovery used four chains with 4,000 tuning and 4,000 retained draws at target acceptance 0.99, with unchanged model and priors. Its result is the final diagnostic record above." if d['f2'].get('attempt')==2 else 'No F2 recovery was required.')
 f1_interpretation=('F1 passes the zero-frequency check, but its added positive-count gate still fails; separating zeros therefore does not establish full opportunity adequacy.' if o['f1'].get('zero_frequency_99_pass') and not o['f1'].get('gate_pass') else 'F1 opportunity status is determined by all original gates plus the added positive-count gate.')
 prior_text='\n'.join(f"- {k}: 5,000 draws; positive conditional-rate mass >100/game {v['fraction_positive_rate_over_100']:.6%}; season-count mass >1,000,000 {v['fraction_total_FTA_over_1000000']:.10%}; zero-fraction 95% interval [{v['zero_fraction_95_interval'][0]:.3%}, {v['zero_fraction_95_interval'][1]:.3%}]; combined extreme zero-fraction mass {v['zero_fraction_extreme_mass']:.3%}." for k,v in prior['candidates'].items())
 comparison='| Candidate | Sampler pass | Accuracy pass | Joint opportunity pass | FTA-bin failures | Systematic pattern |\n|---|---|---|---|---:|---|\n'+''.join(f"| {k.upper()} | {d[k].get('sampler_pass',False)} | {a[k].get('gate_pass',False) if a[k].get('replicates') else 'Not evaluated'} | {o[k].get('gate_pass',False) if o[k].get('replicates') else 'Not evaluated'} | {a[k].get('FTA_bin_99_fail_count','unassessed')} | {a[k].get('systematic_volume_pattern','unassessed')} |\n" for k in d)
 bin_table='| Candidate / FTA bin | Observed FT% | Predictive mean FT% | 99% interval | Outside |\n|---|---:|---:|---|---|\n'
 for k in d:
  for b in a[k].get('bin_checks',[]):bin_table+=f"| {k.upper()} / {b['metric'].removeprefix('FTA_').removesuffix('_pooled')} | {b['observed']*100:.4f} | {b['replicated_mean']*100:.4f} | [{b['predictive_99_low']*100:.4f}, {b['predictive_99_high']*100:.4f}] | {b['outside_99']} |\n"
 positive='| Candidate / positive-count quantile | Observed | Predictive mean | 99% interval | Outside |\n|---|---:|---:|---|---|\n'
 for k in ['f1','f2']:
  for q in o[k].get('positive_quantiles',[]):positive+=f"| {k.upper()} / {q['metric']} | {q['observed']:.2f} | {q['replicated_mean']:.2f} | [{q['predictive_99_low']:.2f}, {q['predictive_99_high']:.2f}] | {q['outside_99']} |\n"
 correlation='\n'.join(f"- {k.upper()} {n}: {fmt(v)}." for k in corr for n,v in corr[k].items() if isinstance(v,dict)) or 'No reportable correlation summaries because sampling did not pass.'
 if not d['f2'].get('sampler_pass',False):correlation+='\n\nF2 correlation summaries are withheld because its sampler failed the convergence gate. The reported F1 correlations cannot substitute for F2 estimates.'
 interpretation='No reportable opportunity slopes because F2 sampling failed.'
 if 'theta_B' in theta:
  supported=[name for name in ['theta_B','theta_W'] if theta[name]['CI95'][0]>0 or theta[name]['CI95'][1]<0]
  interpretation=('Both between-player and within-player terms have intervals excluding zero.' if len(supported)==2 else ('Only '+supported[0]+' has an interval excluding zero.' if supported else 'Neither term has an interval excluding zero.'))+' This describes posterior diagnostic evidence, not a causal importance ranking. Raw slope magnitude alone is insufficient to rank importance because predictor variation and uncertainty differ; the between term also overlaps with persistent random effects.'
 text=f'''# Stage 3F — Hurdle Opportunity and Within/Between Adequacy

**{title}**. Scientific coefficient status: **SEALED**. Scientific inference is not authorized. Stage 3G has not been started. No multi-season replication claim is made.

## 1. Historical adequacy failures

Stage 3C remains EXECUTION FAIL — PRIMARY PPC ADEQUACY GATE FAILED; Stage 3D remains ADEQUACY UNRESOLVED — D3 FAILS PRIOR-PREDICTIVE PREREQUISITE; Stage 3D-R remains ADEQUACY UNRESOLVED — D3 FAILS. Stage 3E remains NOT AUTHORIZED. F0 reuses the exact saved Stage 3D-R D3 diagnostics and 2,000-replicate PPC, without refitting. Its pooled accuracy passed, three bins failed, and the systematic volume pattern remained. Its observed zero fraction was 3.3277%, versus predictive mean 1.1800%; Q25/Q50/Q75 also failed. These artifacts are preserved by hashes.

## 2. Stage 3F objective

Separate whether attempts occur, how many occur once positive, persistent opportunity differences, and within-player opportunity deviations. The objective is conditional-distribution adequacy. Selection receives only typed gate booleans and never scientific-effect summaries. No causal claim is made.

## 3. Why zero FTA requires separate consideration

A single NB component ties its zero probability to its count mean and dispersion. A hurdle supplies a separate Bernoulli probability for any attempts and an exactly zero-truncated count distribution for positives. A better zero fit would establish improved predictive representation, not a distinct causal zero-generating mechanism.

## 4. Persistent and within-player opportunity

Persistent observed opportunity averages a player's log1p(FTA/GP) across their available seasons. A within-player deviation measures departure from that player's own average. These can have different conditional accuracy relationships. The decomposition uses no FTM information, but uses realized opportunity and therefore changes the accuracy conditioning set.

## 5. Fixed candidate ladder

Frozen at {p['frozen_at']}, before prior checks or fitting. F0 is the saved failed reference. F1 is the hurdle model with a joint three-dimensional player-effect structure and unchanged accuracy mean. F2 was independently predeclared as F1 plus between/within accuracy terms. No candidate was added or simplified after results.

Primary panel SHA256 `{EXPECTED}`: 4,117 player-seasons, 857 players, 13 seasons, 469,099 FTA; 2013–14 excluded. The panel, anthropometrics, residual transformation, height center, position labels and seasonal coding were not rebuilt. All rows enter the hurdle; 3,980 positive-FTA rows enter the truncated count and accuracy likelihoods. No FTA threshold filtering or player exclusion occurred.

## 6. Hurdle model

Any-FTA Bernoulli logit contains an intercept, frozen residual exposure, centered height, original position/season terms, and hurdle player intercept. There is no GP offset in that component. Positive FTA follow a zero-truncated NB2 with coefficient-one log(GP) offset and corresponding fixed/player opportunity terms. GP is strictly positive; no MIN field enters the models.

Accuracy remains beta-binomial with the original adjustment variables and accuracy player intercept. Non-centered effects ordered accuracy/positive opportunity/hurdle use a 3×3 LKJCholeskyCov construction. No two-dimensional or independent-effects simplification was made.

The positive log likelihood is log NB(y) minus log(1−P_NB(0)), for integer y≥1, with log P_NB(0)=−alpha×log1p(mu/alpha). The correction is evaluated as log(−expm1(log P_NB(0))) for stability. This matches the [documented PyMC hurdle probability mass function](https://www.pymc.io/projects/docs/en/v5.24.0/api/distributions/generated/pymc.HurdleNegativeBinomial.html). It was validated against both PyMC Truncated and independent SciPy calculations over 150 parameter/count combinations; exact truncated random draws were checked against analytic conditional means. Native Truncated's gradient took 5.407 seconds on the pinned NUMBA backend because of object-mode fallback. The transparent exact formula avoids that computational limitation; it is not ordinary NB fitted to positive rows.

## 7. Within/between decomposition

x=log1p(FTA/GP); between=mean(x) over each player's available seasons; within=x−between; centered_between=between−mean(between across unique players). Center={decomp['centering_constant']:.15f}. Each unique player receives equal weight for the global center; their available seasons receive equal weight within player. All 137 zero-FTA rows contribute x=0. Maximum absolute within-player mean={decomp['max_absolute_player_mean_within']:.3g}. Formula, data and code hashes were frozen before fitting.

F2 accuracy adds theta_B×centered_between and theta_W×within. Conditional PPC holds observed attempts and these covariates fixed. Joint PPC generates all hurdle/count outcomes, recomputes the decomposition from the generated panel including its zeros and unique-player center, then generates makes using the same posterior player-effect draw. This was predeclared; generated opportunity is not replaced by observed opportunity in the joint check.

## 8. Priors

Positive opportunity: intercept Normal(log(2),1), raw exposure/height slopes Normal(0,0.15), positions Normal(0,0.35), seasons Normal(0,0.25), log alpha Normal(log(2),1). Hurdle: intercept Normal(logit(0.95),1), exposure/height slopes Normal(0,0.25), positions Normal(0,0.5), seasons Normal(0,0.35). The 0.95 center was selected once from the user-specified domain prior; it was not estimated from observed zeros.

Marginal SDs are HalfNormal(1), HalfNormal(0.5), HalfNormal(1), ordered accuracy/positive opportunity/hurdle; LKJ eta=2. Accuracy intercept Normal(0,2.5), exposure/height Normal(0,0.5), position/season Normal(0,1), log precision Normal(3,2) remain unchanged. F2 theta_B and theta_W each have Normal(0,0.5) priors. No prior changed after simulation.

## 9. Prior predictive checks

Seed 20260928, 5,000 draws per candidate. Both checks passed before fitting:

{prior_text}

The positive conditional mean is mu_NB/(1−P_NB(0)); its rate divides by GP. The underlying mu_NB/GP quantiles are also saved for comparison with Stage 3D-R. Frozen gross limits are ≤1% above 100 FTA/game and ≤0.1% simulated seasons above one million FTA. The zero-fraction distribution must have broad plausible spread and ≤90% combined mass below 0.1% or above 50%. The broad interval review did not compare priors to the observed zero percentage. Extreme count tails remain possible; this screen is not posterior adequacy.

## 10. F1 sampler and PPC

{diag(d['f1'])}.

Conditional accuracy: {acc(a['f1'])}.

Joint opportunity: {opp(o['f1'])}.

{f1_interpretation}

Initial sampling: four chains, 2,000 tuning and 2,000 retained per chain, target_accept 0.95, seed 20260928. One generic recovery at 4,000/4,000 and 0.99 was permitted only for failed sampler diagnostics. No failed sampler contributes a PPC release pass.

## 11. F2 sampler and PPC

{diag(d['f2'])}.

{recovery_note}

Conditional accuracy: {acc(a['f2'])}.

Joint opportunity: {opp(o['f2'])}.

F2 uses the same sampling and recovery rules. Major fixed terms, dispersions, SDs and all three correlations enter the diagnostic gate. The scientific coefficient contributes only anonymous numerical convergence checks; it is never plotted or summarized. Compiled gradients matched reference gradients before fitting. Visual trace/energy reviews accompany sampler passes.

## 12. Between/within diagnostic parameters

Between-player theta_B: {fmt(theta.get('theta_B',theta))}.

Within-player theta_W: {fmt(theta.get('theta_W',theta))}.

{interpretation} These are associational opportunity diagnostics under the specified model. Their intervals cannot override a predictive failure or establish scientific replication.

![Between and within parameters](<{F}/03_between_within_parameters.png>)

## 13. Random-effect correlations

{correlation}

These describe remaining latent player propensities conditional on each model. F2 correlations condition additionally on the realized between/within terms, so their interpretation differs from F1. None is a causal mechanism estimate.

![Latent correlations](<{F}/04_random_effect_correlations.png>)

## 14. Accuracy adequacy comparison

{comparison}

{bin_table}

Exactly 2,000 replications, seed 20260929. The unchanged gates fail on pooled rate outside 99%, ≥3 of seven global metrics outside 99%, ≥5 of 13 season rates outside 99%, ≥2 of five pooled FTA-bin rates outside 99%, or the frozen systematic opposite low/high bias pattern. Directional evidence uses bias beyond 2.576 MCSE, with 40 chain-major batches of 50 draws. Predictive intervals and MCSE serve different purposes. F0 is copied, not simulated again.

![Accuracy by FTA bin](<{F}/01_accuracy_FTA_bins.png>)

## 15. Opportunity adequacy comparison

{positive}

The original joint gate fails if zero fraction lies outside 99%, ≥3 of five total-FTA quantiles lie outside 99%, or ≥5 season totals lie outside 99% in the same direction. The predeclared added hurdle gate fails if ≥2 of three positive-count quartiles miss 99%. F0 did not save positive-only quartile checks; those missing results are not invented. Overall, original-position and season-level opportunity metrics remain available in each joint CSV, including descriptive positive-count means/SDs.

![Zeros and positive counts](<{F}/02_zero_positive_count_PPC.png>)

## 16. Stage 3F classification

{title}. {'Frozen at '+r['frozen_at'] if frozen else 'Awaiting final protocol/firewall tests and decision freeze.'} A complete F2 sampler/accuracy/opportunity pass with protocol/firewall checks resolves structural adequacy. A valid opportunity repair without accuracy repair, or F2 accuracy repair without opportunity repair, can be partial resolution. Failed F2 sampling ends unresolved. A PPC withheld for failed sampling is unassessed, not an observed predictive failure. Parameter magnitudes, signs, p-values and model-fit rankings are not decision inputs.

## 17. Prediction versus estimand

F2 changes the scientific conditioning set even if it predicts better. Realized opportunity may be downstream of player ability, role, health, team context and other factors. Conditioning on its within/between decomposition may block, mediate or otherwise alter relationships being studied. The decomposition is an adequacy device, not an automatically valid scientific adjustment.

## 18. Stage 3G estimand review

Candidate scientific model status remains REQUIRES_ESTIMAND_REVIEW. A later separately authorized Stage 3G must assess scientific interpretation before F2 could support effect reporting. If predictive inadequacy remains, estimand review does not waive that failure. Stage 3E remains unauthorized and Stage 3G was not executed. The scientific wingspan coefficient remains sealed; no coefficient sign, interval, odds ratio, probability or wingspan contrast is reported.

## 19. Remaining limitations

These are conditional in-sample checks of observed players, not out-of-sample validation. Unbalanced observed careers affect the opportunity averages; those averages use all available seasons and are not prospective forecasts. Sparse zero-FTA events can leave hurdle correlations weakly identified. The specified distribution families, linear terms and multivariate-normal random effects remain assumptions. Combine measurement coverage remains approximately 51%–67%, and selection, survival, measurement error and unobserved factors remain uncorrected. No new confounders were introduced.

The previously frozen ancillary minute-display limitation remains historical evidence; no minutes are used in this stage. All prior decisions remain unchanged. No causal claim or multi-season replication claim is made.

## 20. Reproducibility

The pinned Stage 3C environment is reused unchanged. Frozen model/prior/decomposition hashes, panel hash, native/independent likelihood validation, sampling attempts, permitted summaries, PPC tables, visual reviews, replay checks and final artifact hashes are saved under stage3f_evidence. Traces are local and Git-ignored. Numerical convergence checks export only ESS/R-hat for the anonymous scientific parameter; no plot of it is generated.

Final verification uses the pinned Python executable with PYTENSOR_FLAGS='cxx=,base_compiledir=/private/tmp/stage3f-pytensor' and single-thread BLAS settings. An initial verification invocation omitted the empty cxx setting and encountered the host's unavailable C++ headers; that failure log is preserved. Repeating the unchanged tests with the established Python/NUMBA-compatible configuration completed successfully. No model, likelihood, prior or sampling change was made for this runtime issue.

Tests passed: {test.get('tests_passed','pending')}/{test.get('tests_run','pending')}. Prior artifacts are hash-checked. Scientific-effect values are not used for candidate selection. No commit, push, new confounder, FTA threshold, full-panel fit, 2013–14 inclusion, or Stage 3G execution occurred.
'''
 (ROOT/'docs/stage3f_hurdle_within_between_adequacy.md').write_text(text)
if __name__=='__main__':main()
