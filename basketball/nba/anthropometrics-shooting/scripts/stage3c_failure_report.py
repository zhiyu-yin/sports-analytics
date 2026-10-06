"""Report the frozen model-adequacy failure without promoting it to replication evidence."""
from stage3c_setup import *
def fmt(s):return f"mean {s['mean']:.6f}; median {s['median']:.6f}; SD {s['SD']:.6f}; 95% equal-tail CrI [{s['CI95'][0]:.6f}, {s['CI95'][1]:.6f}]"
def main():
 r=read(E/'primary_replication_result.json');assert not r['scientifically_reportable']
 p=read(E/'model_protocol.json');a=read(E/'primary_panel_model_data_summary.json');d=r['diagnostics'];v=r['variance_components'];c=r['probability_contrast'];pp=r['PPC'];prior=read(E/'prior_predictive_summary.json');rep=read(E/'reproduction_check.json') if (E/'reproduction_check.json').exists() else {};tests=read(E/'test_summary.json') if (E/'test_summary.json').exists() else {}
 text=f'''# Stage 3C — Primary Multi-Season Hierarchical Replication

**Execution: FAIL — primary posterior predictive adequacy gate failed.** The sampler passed its numerical and visual diagnostics. Successful sampling does not establish model adequacy. The primary record is frozen with `scientifically_reportable=false`; all coefficient and contrast summaries below are **diagnostic descriptions of the failed model**, not an accepted replication conclusion. The secondary full-panel fit was not run. No specification or gate was changed to obtain a desired association.

## 1. Audit/provenance chain

Stage 0B froze eligibility and geometry; Stage 0C validated historical anthropometrics; Stage 1/2 developed the single-season association. Original Stage 3 remains BLOCKED under its original minute rule. Stage 3A remains UNRESOLVED about internal NBA minute precision. Stage 3B prospectively amended the source-release protocol and authorized this first multi-season inference. A SHA256 preservation manifest and final tests verify that prior artifacts remain unchanged; historical failures were not rewritten as successes.

## 2. Stage 3B authorization

Verified `part_b_authorized=true` and linked gate/receipt hashes before fitting. Primary panel SHA256: `{r['panel_hash']}`. Full panel SHA256: `5306ffd228fb71b34b174d18cf86e351b6fa48598579e4f49935078239662978`. Both match Stage 3B. No panel rebuild, measurement-vector change or shooting-data recollection occurred.

## 3. Scientific objective

Evaluate whether the negative 2013–14 residual-wingspan association generalizes across other available seasons while representing repeated players, season effects, persistent player heterogeneity and extra-binomial variability. The intended replication assessment remains unresolved because the frozen model-adequacy gate failed.

{INTERPRETATION}

## 4. Primary replication population

13 seasons; 4,117 player-seasons; 857 players; 469,099 FTA. **2013–14 is excluded.** The likelihood contains 3,980 positive-FTA rows with no minimum-FTA threshold. The 137 zero-FTA rows remain in population accounting. All 857 players remain deterministically indexed, including 22 with no attempts in the primary panel; those 22 random effects have prior information only. Repeated player-seasons are not independent players.

## 5. Frozen residual-wingspan exposure

Residual wingspan = observed wingspan − (4.574910520685837 + 1.0013410045156863 × barefoot height), in inches. The Stage 1 transformation was reused exactly and not refitted. Height center = {p['height_center']:.14f} inches, the outcome-independent primary unique-player mean. Residual inches remain uncentered, retaining zero. Original combine position labels, including hybrids, remain separate; missing/blank maps to unknown. Reference position is C; reference season is {p['season_reference']}.

## 6. Hierarchical beta-binomial model

FTM_it ~ BetaBinomial(n=FTA_it, alpha=mu_it×kappa, beta=(1−mu_it)×kappa).

logit(mu_it) = beta_0 + beta_RW×residual_wingspan_i + beta_H×centered_height_i + position_effect_i + season_effect_t + u_i.

Non-centered player effects: z_i ~ Normal(0,1); u_i=sigma_player×z_i. kappa=exp(log_kappa); rho=1/(1+kappa). FTA is the denominator only. There are no minutes, age, experience, team or other new predictors. No alternate model family was substituted.

## 7. Identification interpretation

Residual wingspan, height and position are time-invariant. The wingspan coefficient is identified by **between-player variation**, conditional on the hierarchical random-effects assumptions. Repeated seasons do not create within-player exposure identification. Random intercepts do not control all player ability or remove all omitted player characteristics. A player fixed-effects model cannot separately estimate this time-invariant exposure and was not attempted as a substitute.

## 8. Priors

Frozen at {p['frozen_at']}, before prior simulation and fitting: beta_0 ~ Normal(0,2.5); beta_RW and beta_H ~ Normal(0,0.5); each nonreference position and season effect ~ Normal(0,1); sigma_player ~ HalfNormal(1); log_kappa ~ Normal(3,2). No statistical prior, formula, exposure or covariate was changed after seeing a posterior.

## 9. Prior predictive check

1,000 prior draws. Fraction mu<0.01: {prior['fraction_below_001']:.6f}; mu>0.99: {prior['fraction_above_099']:.6f}. Quantiles 2.5%, 25%, 50%, 75%, 97.5%: {', '.join(f"{prior['implied_mu_quantiles'][str(q)]:.6f}" for q in [.025,.25,.5,.75,.975])}. All values were finite. These broad priors passed the predeclared gross-boundary screen (neither tail above 25%); this is not a claim that the prior closely represents NBA FT rates. No observed exposure association was examined to tune the prior.

## 10. MCMC diagnostics

Four PyMC NUTS chains; 2,000 tuning and 2,000 retained draws each (8,000 retained total); target_accept=0.95; seed=20260928. Maximum R-hat={d['max_rhat']:.6f}; minimum bulk ESS={d['min_bulk_ESS']:.2f}; minimum tail ESS={d['min_tail_ESS']:.2f}; divergences={d['divergences']}; maximum-tree-depth hits={d['max_treedepth_hits']}; minimum BFMI={min(d['BFMI_by_chain']):.3f}. Key fixed-effect/variance covariance is finite. Every position and season coefficient was included in the diagnostic gate. Trace densities overlap, trace bands are stationary, and energy distributions overlap without an obvious pathological pattern. No diagnostic recovery run was needed.

Two initial launches failed with fork-related macOS crashes/EOFError; a subsequent uncompiled run was interrupted after a measured slow gradient. None produced an inspected posterior. Spawned workers and validated [PyTensor NUMBA compilation](https://pytensor.readthedocs.io/en/latest/library/compile/mode.html) resolved these computational issues while retaining the exact model and PyMC NUTS sampler. The compiled initial-point gradient matched the reference within rtol=atol=1e-8. Every failed/interrupted attempt is preserved. No prior-stage environment was changed.

## 11. Primary beta_RW result — diagnostic only

{fmt(r['beta_RW'])}, in log odds per residual inch. The median is negative and the interval excludes zero. Estimated P(beta_RW<0)={r['P_beta_RW_negative']:.6f}: all 8,000 retained draws were negative. This empirical estimate does not establish literal certainty. The result is conditional on a model that failed its PPC gate and must not be presented as successful scientific replication.

![Diagnostic coefficient posterior; PPC failed](stage3c_figures/primary_01_beta_RW.png)

## 12. OR interpretation — diagnostic only

OR per residual inch: {fmt(r['OR_per_residual_inch'])}. This is a conditional odds ratio under the failed model, not a percentage-point change or causal effect.

## 13. Q25/Q75 probability contrast — diagnostic only

Primary accounting player-season quantiles: Q25={c['Q25_inches']:.6f}, Q75={c['Q75_inches']:.6f} residual inches. Repeated seasons contribute their observed frequency. Each draw retains observed height, original position, season and fitted player random effect, replaces only residual wingspan, and averages equally across 3,980 positive-FTA rows.

Q25 probability: {fmt(c['conditional']['Q25'])}. Q75 probability: {fmt(c['conditional']['Q75'])}. Difference Q75−Q25, in percentage points: **{fmt(c['conditional']['difference_percentage_points'])}**. Empirical P(difference<0)=1.000000.

The optional u=0 reference-player difference is {fmt(c['zero_random_effect_reference_player']['difference_percentage_points'])} percentage points. It is not a population average marginalized over new-player heterogeneity. Both are adjusted model-based association contrasts; neither overcomes the PPC failure or establishes causality. Synthetic predictor combinations can also involve extrapolation.

![Diagnostic conditional contrast; PPC failed](stage3c_figures/primary_02_contrast.png)

## 14. Player heterogeneity

Sigma_player: {fmt(v['sigma_player'])} on the logit scale. At a hypothetical fixed baseline probability 0.75, ±1 posterior-median sigma gives approximately {v['probability_scale_at_reference_mu_075']['minus_one_sigma']['median']:.4f} and {v['probability_scale_at_reference_mu_075']['plus_one_sigma']['median']:.4f}. This illustrates model scale only. Individual random effects are neither ranked nor published.

## 15. Extra-binomial heterogeneity

Kappa: {fmt(v['kappa'])}. Rho: {fmt(v['rho'])}. Rho represents remaining player-season extra-binomial variation after the persistent player intercept. It is smaller than Stage 2's approximately 0.0299; longitudinal random intercepts can absorb some variation previously represented by single-season dispersion. This does not establish that the remaining model fits adequately.

## 16. Season effects

Saved in `stage3c_evidence/primary_season_effects.csv`, relative to {p['season_reference']}. These are adjustment terms, with no season-specific hypothesis search, significance ranking or season-varying wingspan slopes.

![Diagnostic season adjustments; PPC failed](stage3c_figures/primary_03_seasons.png)

## 17. Posterior predictive checks — FAILED

1,000 conditional beta-mixture/binomial replications, seed 20260929, retain observed FTA and fitted player effects. Observed makes/attempts = 360,001/469,099. Replicated mean makes = {pp['replicated_makes_summary']['mean']:.1f}; 95% predictive interval [{pp['replicated_makes_summary']['CI95'][0]:.1f}, {pp['replicated_makes_summary']['CI95'][1]:.1f}].

Observed pooled rate is **76.7431%**, compared with replicated mean **76.4326%**, 95% predictive interval **[76.1630%, 76.6794%]**, and 99% interval **[76.0937%, 76.7278%]**. Only 4/1,000 replicates reach or exceed the observed rate. The observed value lies just above the 99% bound (0.0153 percentage points above it); the finite-simulation boundary should not be exaggerated, but the predeclared rule is binding. No extra PPC draws or threshold changes were used to seek a pass.

The frozen serious-failure rule is pooled rate outside its 99% interval, OR at least three of six global rate-distribution metrics outside 99%, OR at least one-third of season pooled rates outside 99%. The pooled-rate condition triggers; two global metrics and zero season metrics are outside 99%.

Additional systematic discrepancies support concern beyond the narrow pooled boundary:

| Metric | Observed | Replicated mean |
|---|---:|---:|
| Pooled FT%, FTA 1–9 | 68.405% | 73.263% |
| Pooled FT%, FTA 10–49 | 71.528% | 73.651% |
| Pooled FT%, FTA 100–299 | 76.635% | 76.168% |
| Pooled FT%, FTA 300+ | 79.044% | 78.117% |
| Overall player-season rate Q95 | 91.028% | 93.059% |
| Fraction of player-seasons with perfect FT rate | 3.166% | 3.781% |

Each listed metric is outside its 99% predictive interval. FTA 50–99 Q95 also misses. Observed overall rate SD and mean within-player rate SD are above their 95% bounds but inside 99%; between-player pooled-rate SD is well represented. All season pooled rates fall inside 99% intervals. Complete intervals and tail fractions are in `primary_PPC_metrics.csv`.

The model overpredicts low-attempt rates and underpredicts high-attempt rates; this describes a model-check pattern, not a proven mechanism. FTA remains a denominator, with no new predictor added. These are conditional checks for observed players, not out-of-sample validation. **Stage 3C scientific inference is not yet adequate.**

![Primary posterior predictive checks](stage3c_figures/primary_04_PPC.png)

## 18. Comparison with Stage 1/2

This comparison was made only after the failed primary result was frozen at {r['frozen_at']}. Its diagnostic posterior median −0.040009 has the same negative direction and slightly greater absolute magnitude than Stage 1 M2 −0.03531 and Stage 2 beta-binomial −0.03771. This is descriptive numerical agreement, not accepted replication evidence. Different populations and models also limit direct equivalence. 2013–14 is development evidence; overlapping players mean that even an adequate cross-season analysis would not be an independent-player replication.

## 19. Secondary full-panel result

**Not run because the primary PPC gate failed.** The verified full panel contains 14 seasons, 4,428 player-seasons, 866 players and 511,686 FTA, including 2013–14. `full_panel_result.json` explicitly records `NOT_RUN_PRIMARY_PPC_FAILED`, with no invented coefficient. `full_panel_fixed_effects.csv` contains only its schema and no estimates. The fitting guard rejects a secondary run when the primary is not scientifically reportable. Any future full-panel result would include development evidence and would not be independent replication.

## 20. Selection limitation

Previously approved Stage 3 evidence gives approximately 51%–67% measurement coverage across seasons. No new outcome-based selection comparison was calculated. The hierarchy does not correct selection into combine participation, available anthropometrics, NBA survival or shooting opportunity. Random intercepts do not solve selection.

## 21. Stage 3B minute-display limitation

> {p['minute_limitation']}

## 22. What the model does NOT establish

{INTERPRETATION}

The immediate limitation is failed predictive adequacy, especially attempt-stratified calibration and rate tails. More generally, between-player identification relies on the random-effects structure, does not remove all persistent confounding, and remains limited by sample selection, measurement error, frozen geometric-fit uncertainty and informative opportunity. Neither successful sampling nor a negative coefficient overcomes these limitations.

## 23. Reproducibility

Python {r['software_environment']['python']}; PyMC {r['software_environment']['packages']['pymc']}; exact dependencies in `requirements-stage3c.txt`; pip check passed. Isolated environment and traces are locally Git-ignored under `models/stage3c/`. Protocol SHA256: `{r['model_protocol_hash']}`. The manifest records trace paths, byte sizes, hashes, software, code and evidence hashes.

The failed primary result is immutable. Exact saved-trace numerical/PPC replay: {rep.get('primary_exact_saved_trace_replay','pending')}. Separate same-seed primary sampler reproduction passed: {rep.get('sampler_reproduction_passed','pending')}; posterior arrays exactly equal in this environment: {rep.get('posterior_arrays_exact_in_same_environment','pending')}. Every key-parameter mean must agree within four combined MCSEs. This repeat validates computation and cannot repair the PPC failure; it never replaces the frozen primary result. No bit-identical guarantee is made for different software or hardware.

The freeze code was extended solely to record a failed-PPC artifact rather than requiring success. Replay retains the original analysis code hash and asserts equality of every other result field; both code hashes are recorded. No model, prior, diagnostic threshold or PPC threshold changed. Figures are labeled diagnostic because scientific reportability is false.

## 24. Stage 3C execution decision

**FAIL — PPC adequacy requirement not met.** Sampler convergence passed; scientific model adequacy did not. Verification tests passing does not override this failure. Tests passed: {tests.get('tests_passed','pending')}/{tests.get('tests_run','pending')}; final machine-readable decision is `stage3c_evidence/execution_status.json`. Guard tests verify that failure is preserved and full-panel fitting is blocked, rather than asserting that every scientific gate passed. Scientific sign is not an execution criterion.

## 25. Recommended next step

Review the frozen PPC failure before deciding whether to authorize a separately documented model-adequacy investigation. Do not present this coefficient as a validated multi-season replication. The model has not been changed to address the discrepancies. No full-panel fit, Stage 3D sensitivities, FTA-threshold refits, alternate exposures, grouped positions, new subgroups, season-varying slopes or new confounders were run. No causal conclusion, commit or push was made.
'''
 (ROOT/'docs/stage3c_primary_hierarchical_replication.md').write_text(text)
if __name__=='__main__':main()
