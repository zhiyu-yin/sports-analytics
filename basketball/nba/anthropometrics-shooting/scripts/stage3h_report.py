"""Report only whitelisted, gate-approved adequacy artifacts."""
from stage3h_common import *
def get(n):return read(E/n) if (E/n).exists() else {}
def diagnostic(d):
 if not d:return 'Pending.'
 if 'max_rhat' not in d:return d.get('status','Not assessed')
 status=('sampler pass '+str(d['sampler_pass'])) if 'sampler_pass' in d else ('numeric gate '+str(d['numeric_gate_pass'])+'; visual review in the final diagnostic record')
 return f"Attempt {d['attempt']}; {status}; max R-hat {d['max_rhat']:.6f}; minimum bulk ESS {d['min_bulk_ESS']:.2f}; minimum tail ESS {d['min_tail_ESS']:.2f}; divergences {d['divergences']}; tree-depth hits {d['max_depth_hits']}; BFMI {', '.join(f'{v:.3f}' for v in d['BFMI'])}; finite covariance {d['finite_covariance']}."
def ppc(d,kind):
 if not d:return 'Not assessed yet.'
 if 'status' in d:return d['status']+'. Unassessed predictive adequacy, not an observed PPC failure.'
 if kind=='accuracy':return f"Pass {d['gate_pass']}; pooled pass {d['pooled_rate_99_pass']}; global failures {d['global_metrics_99_fail_count']}/7; season failures {d['season_rate_99_fail_count']}/13; FTA-bin failures {d['FTA_bin_99_fail_count']}/5; systematic volume pattern {d['systematic_volume_pattern']}."
 z=d['zero_frequency'];s=f"Pass {d['gate_pass']}; zero-FTA pass {d['zero_frequency_99_pass']}; observed {100*z['observed']:.4f}%, predictive mean {100*z['replicated_mean']:.4f}%, 99% interval [{100*z['predictive_99_low']:.4f}%, {100*z['predictive_99_high']:.4f}%]. Total-FTA quantile failures {d['quantile_99_fail_count']}/5; positive-count failures {d['positive_quantile_99_fail_count']}/3; season totals below/above 99% intervals {d['season_totals_outside_99_low']}/{d['season_totals_outside_99_high']}."
 for r in d['positive_quantiles']:s+=f"\n\n{r['metric']}: observed {r['observed']:.2f}, predictive mean {r['replicated_mean']:.2f}, 99% interval [{r['predictive_99_low']:.2f}, {r['predictive_99_high']:.2f}], outside {r['outside_99']}."
 return s
def parameters(key):
 d=get(key+'_latent_factor_parameters.json')
 if not d or 'status' in d:return 'Withheld: no valid sampler for this candidate.'
 out=[]
 for k in ['rho_AO','lambda_h','sigma_opportunity','sigma_accuracy','alpha_FTA','kappa']:
  v=d[k];out.append(f"| {k} | {v['mean']:.6f} | {v['median']:.6f} | {v['SD']:.6f} | [{v['CI95'][0]:.6f}, {v['CI95'][1]:.6f}] |")
 w=get('h2_within_parameter.json') if key=='h2' else {}
 if 'theta_W' in w:
  v=w['theta_W'];out.append(f"| theta_W | {v['mean']:.6f} | {v['median']:.6f} | {v['SD']:.6f} | [{v['CI95'][0]:.6f}, {v['CI95'][1]:.6f}] |")
 return '| Parameter | Mean | Median | SD | 95% CrI |\n|---|---:|---:|---:|---|\n'+'\n'.join(out)
def main():
 p=protocol();decision=get('stage3h_decision.json');t=get('test_summary.json');h1=get('h1_diagnostics.json');h2=get('h2_diagnostics.json');pr=get('h1_prior_predictive.json');comparison='Not generated until the new decision is frozen.'
 if decision:
  import pandas as pd
  rows=pd.read_csv(E/'model_adequacy_comparison.csv').fillna('unassessed');comparison='| Candidate | Sampler | Accuracy PPC | Opportunity PPC | Latent dimensions/player |\n|---|---|---|---|---|\n'+'\n'.join('| '+' | '.join(str(r[k]) for k in ['candidate','sampler_pass','accuracy_pass','opportunity_pass','latent_dimensions_per_player'])+' |' for _,r in rows.iterrows())
 prior='Pending.' if not pr else f"H1: 5,000 draws, seed 20260930; pass {pr['passed']}; positive mean-rate mass >100/game {pr['fraction_positive_rate_over_100']:.6%}; season-count mass >1,000,000 {pr['fraction_total_FTA_over_1000000']:.8%}; zero-fraction 95% interval {pr['zero_fraction_95_interval']}; extreme zero mass {pr['zero_fraction_extreme_mass']:.4%}; accuracy near-zero/near-one masses {pr['accuracy_fraction_below_001']:.4%}/{pr['accuracy_fraction_above_099']:.4%}; finite {pr['finite']}."
 pr2=get('h2_prior_predictive.json')
 if pr2:prior+=f" H2: 5,000 draws, same seed; pass {pr2['passed']}; positive-rate tail {pr2['fraction_positive_rate_over_100']:.6%}; season-count tail {pr2['fraction_total_FTA_over_1000000']:.8%}; zero-fraction 95% interval {pr2['zero_fraction_95_interval']}; accuracy near-zero/near-one masses {pr2['accuracy_fraction_below_001']:.4%}/{pr2['accuracy_fraction_above_099']:.4%}. No prior adjustment."
 figures=''
 if decision:
  for name,title in [('01_accuracy_comparison','Accuracy PPC comparison'),('02_opportunity_PPC','Opportunity checks'),('03_rho_AO','Latent association'),('04_latent_loadings','Latent loadings')]:
   if (F/(name+'.png')).exists():figures+=f'\n\n![{title}](<{F}/{name}.png>)'
  if (F/'05_theta_W.png').exists():figures+=f'\n\n![Within adequacy parameter](<{F}/05_theta_W.png>)'
 opportunity_results='\n\n'.join(c+': '+ppc(get(c.lower()+'_joint_opportunity_ppc.json'),'opportunity') for c in ['H1','H2'] if get(c.lower()+'_diagnostics.json'))
 accuracy_results='\n\n'.join(c+': '+ppc(get(c.lower()+'_conditional_accuracy_ppc.json'),'accuracy') for c in ['H1','H2'] if get(c.lower()+'_diagnostics.json'))
 replay=get('reproduction_check.json')
 conclusion=('Both H1 and H2 passed their initial sampler gates without recovery, but both failed conditional accuracy and joint opportunity PPCs. H2 reduced FTA-bin interval failures from three to zero while the frozen systematic directional-bias rule remained failed. The shared structure is computationally usable under these priors, but it does not establish predictive adequacy or prove that the original latent dimensions were redundant. The old F2 identification failure is unchanged.') if decision.get('classification_code')=='D' and decision.get('H1_sampler') and decision.get('H2_sampler') else ''
 h2_parameters=('H2 permitted summaries:\n\n'+parameters('h2')) if h2 else ''
 text=f'''# Stage 3H — Shared Opportunity Latent Factor Model

**{decision.get('classification','IN PROGRESS')}**. Scientific wingspan coefficient: **SEALED**. No causal claim or multi-season replication claim is made.

{conclusion}

## 1. Historical F2 identification failure

Stage 3C remains EXECUTION FAIL — primary PPC inadequacy; Stage 3D and Stage 3D-R remain ADEQUACY UNRESOLVED; Stage 3F remains STRUCTURAL ADEQUACY UNRESOLVED. Stage 3F-R remains IDENTIFICATION UNRESOLVED — NO EQUIVALENT F2 PARAMETERIZATION PASSES SAMPLER. All three exact-equivalent candidates failed after their single recoveries. Stage 3E remains NOT AUTHORIZED. The earlier Stage 3G authorization records remain unchanged, and Stage 3G has not been started.

## 2. Stage 3H motivation

The frozen design has rank 30/30 and standardized condition number 8.29 (raw 106.7). Severe standardized collinearity was not identified. Accuracy-only, opportunity-only and independent-effect diagnostics converged. The full F2 structure mixed poorly, particularly the between-opportunity term, accuracy–opportunity correlations and player effects. Within-opportunity mixing was comparatively good. This motivates testing a different persistent latent structure, not claiming proven structural nonidentifiability.

## 3. Why a shared opportunity factor is proposed

Old F1 had a strong positive opportunity/hurdle relationship. A single standardized persistent opportunity tendency may represent both any-FTA and positive-count processes. This is a statistical latent-factor hypothesis. It is not observed talent, aggressiveness, star status or skill, and has no causal or psychological interpretation.

## 4. Difference from F2

This is a NEW structural model, not an F2 reparameterization or exact-equivalent prior transformation. The observed between-player accuracy term is removed deliberately. Old F1/F2 used three latent player coordinates, three marginal SDs and three pairwise correlations. H1/H2 use two independent standard-normal coordinates per player: one shared opportunity factor and one accuracy residual, with four structural parameters (two scales, a signed hurdle loading and an accuracy–opportunity correlation). Thus 2,571 latent coordinates become 1,714 for 857 players. H1 removes both realized-opportunity slopes; H2 restores only the within slope. A one-factor opportunity process imposes a lower-dimensional dependence structure: the two latent opportunity effects are proportional, with correlation equal to the sign of lambda_h when that loading is nonzero. This restriction applies to latent effects, not perfectly correlated observed hurdle/count outcomes.

## 5. Scientific firewall

The scientific exposure coefficient is never summarized, plotted or correlated with other parameters. It contributes only anonymous convergence information. Its sign, location, uncertainty, odds ratio and probability are unavailable to model selection, prior adjustment or PPC interpretation. Selection receives only Boolean sampler/PPC outcomes. All raw traces stay local and Git-ignored.

## 6. Fixed panel

Exactly 4,117 player-seasons, 857 players, 13 seasons and 469,099 FTA. SHA256 `{EXPECTED}`. All 4,117 rows enter the hurdle; 3,980 positive-FTA rows enter the count and accuracy likelihoods, with all 137 zero rows retained in the accounting panel. The panel, residualization, anthropometrics, original categories and references are unchanged. No 2013–14, secondary panel, FTA threshold, player exclusion, MIN or new confounder is used.

## 7. H1 model

For each player, o and e are independent Normal(0,1). The accuracy effect is u=sigma_accuracy*(rho_AO*o+sqrt(1-rho_AO²)*e). Its variance is sigma_accuracy² and Corr(u,o)=rho_AO. Positive opportunity uses sigma_opportunity*o; sigma_opportunity>0 anchors the factor sign. Hurdle opportunity uses lambda_h*o; lambda_h is allowed either sign. The hurdle has Bernoulli any-FTA likelihood; positive counts use the exact Stage 3F zero-truncated NB; accuracy uses the original beta-binomial. All original fixed adjustment terms remain. GP is a coefficient-one log exposure offset only for positive counts. H1 accuracy contains no realized opportunity predictor.

## 8. H2 model

H2 adds only theta_W*within to H1 accuracy. The observed within values are read directly from the frozen Stage 3F decomposition, verified equal to the original calculation. There is no between-player term. H2 is predeclared and can run only when H1 samples reliably but fails a PPC. H1 sampler failure ends the ladder; a complete H1 pass also stops it. There is no H3.

## 9. Priors

Accuracy: intercept Normal(0,2.5), exposure/height Normal(0,0.5), positions/seasons Normal(0,1), log kappa Normal(3,2). Positive count: intercept Normal(log(2),1), exposure/height Normal(0,0.15), positions Normal(0,0.35), seasons Normal(0,0.25), log alpha Normal(log(2),1). Hurdle: intercept Normal(logit(0.95),1), exposure/height Normal(0,0.25), positions Normal(0,0.5), seasons Normal(0,0.35). New latent priors: sigma_opportunity HalfNormal(0.5), sigma_accuracy HalfNormal(1), lambda_h Normal(0,1), rho_AO Uniform(-1,1). H2 theta_W Normal(0,0.5). Software support transforms do not alter the induced uniform correlation prior. No prior tuning followed simulation.

## 10. Prior predictive checks

{prior}

Frozen gross limits are ≤1% positive conditional mean rates above 100/game, ≤0.1% simulated player-season counts above one million, ≤90% combined zero-fraction mass below 0.1% or above 50%, finite probabilities and ≤25% accuracy mass in either tail below 0.01 or above 0.99 (the existing broad Stage 3D accuracy screen). Broad zero-range review does not fit prior constants to observed outcomes. Passing is a gross-scale prerequisite, not predictive adequacy.

## 11. H1 sampler diagnostics

{diagnostic(h1)}

Initial: {diagnostic(get('h1_attempt1_diagnostics.json'))}

Four chains, seed 20260930, 2,000 warmup and 2,000 retained per chain, target acceptance 0.95. Exactly one unchanged-model recovery at 4,000/4,000 and 0.99 is allowed. Gates: max R-hat≤1.01, bulk/tail ESS≥400, BFMI≥0.3, zero divergences/depth hits, finite covariance and acceptable visual mixing. Every native latent o/e scalar and induced player effect is checked alongside fixed and structural globals. Anonymous scientific-parameter convergence must also pass. Backend gradients are checked before fitting.

## 12. H1 conditional accuracy PPC

{ppc(get('h1_conditional_accuracy_ppc.json'),'accuracy')}

Exactly 2,000 draws, seed 20260930, observed FTA fixed. The original pooled, seven-global, 13-season, five-FTA-bin and systematic low/high MCSE rules are unchanged. Bin limits are 1–9, 10–49, 50–99, 100–299 and 300+. Failure is pooled outside 99%, ≥3 global misses, ≥5 season misses, ≥2 bin misses, or the frozen systematic pattern beyond 2.576 MCSE (40 batches of 50).

## 13. H1 joint opportunity PPC

{ppc(get('h1_joint_opportunity_ppc.json'),'opportunity')}

Generate hurdle states, positive counts and then makes using the same posterior factor draw. Zero fraction, Q25/Q50/Q75/Q90/Q95, season totals, positive-count quartiles and descriptive position summaries reuse Stage 3F functions and gates. Joint failure is zero outside 99%, ≥3 total-count quantile misses, ≥5 season totals outside in the same direction, or ≥2 positive-count quartile misses. No new release metric is used.

## 14. H2 results if reached

{diagnostic(h2) if h2 else 'Not run yet.' if not decision else 'Not run: the frozen H1 stopping rule blocked H2.'}

{ppc(get('h2_conditional_accuracy_ppc.json'),'accuracy') if h2 else ''}

{ppc(get('h2_joint_opportunity_ppc.json'),'opportunity') if h2 else ''}

H2 uses the same sampler, seed and recovery limits. Its conditional PPC holds observed within fixed; its joint PPC recomputes within from generated FTA by the exact frozen function before generating FTM. H2 sampler failure is recorded as classification D under the explicit section-22 stopping rule, with numerical failure distinguished from observed PPC failure. A prior prerequisite failure also stops without posterior inference or retuning.

## 15. Latent opportunity–accuracy relation

H1 permitted summaries:

{parameters('h1')}

{h2_parameters}

rho_AO is an association between persistent latent opportunity and accuracy tendency under this model. lambda_h relates the factor to any-FTA log odds; sigma_opportunity is its positive-count log-rate loading. They are statistical constructs, not causal mechanisms. The within slope, if reportable, is in original log1p(FTA/GP) units and is associational.

## 16. Opportunity-process adequacy

{opportunity_results}

A zero-frequency pass alone cannot establish full opportunity adequacy; positive-count and season checks remain binding. Position checks are descriptive, not additional selection thresholds.

## 17. Accuracy-volume adequacy

{accuracy_results}

Predictive checks address the observed accuracy-volume discrepancy without using scientific-effect direction. Unassessed checks are never treated as passes or observed failures.

## 18. Comparison with F1/F2

{comparison}

This comparison is generated only after the new decision freezes and concerns sampler behavior, PPC adequacy and latent dimension only. Historical F2 posterior summaries remain withheld. No scientific coefficient comparison is made.
{figures}

## 19. Stage 3H classification

{decision.get('classification','Pending completion of the frozen ladder')}.

Reason: {decision.get('reason','Pending')}. Frozen candidate: {decision.get('selected_candidate') or 'None'}. A/B require complete sampler and both PPC passes; a prior or sampler failure never substitutes for evidence of predictive adequacy.

## 20. Stage 3G authorization

Authorized: {decision.get('stage3g_authorized',False)}. Purpose: ESTIMAND REVIEW ONLY. Scientific-effect release authorized: False. Stage 3G executed: False. Only H1 or H2 complete adequacy passes can authorize this later review; old authorization records are not overwritten.

## 21. Scientific estimand caveat

Even H1 changes assumptions about persistent player heterogeneity and requires estimand review. H2 additionally conditions accuracy on realized within-player opportunity. Predictive adequacy is not scientific-effect authorization. The scientific coefficient remains sealed.

## 22. Selection limitations

Combine participation, anthropometric availability, NBA survival, shooting opportunity, between-player identification and measurement error remain limitations. Shared latent factors do not correct sample selection. These are in-sample conditional checks for observed players, not independent replication or out-of-sample validation. No causal claim is made.

## 23. Reproducibility

Protocol frozen {p['frozen_at']}; SHA256 `{sha(E/'model_protocol.json')}`. The pinned Stage 3C environment is reused without installation. Original zero-truncated NB implementation and its 150-point numerical validation are reused. Frozen model, prior, sampler, PPC, selection and inherited dependencies are hash-guarded. A pre-simulation provenance-path typo was corrected before any prior simulation or posterior fit, with the original preflight protocol preserved; no model, prior or gate changed. Traces are local and Git-ignored. Tests {t.get('tests_passed','pending')}/{t.get('tests_run','pending')}; historical artifacts unchanged {t.get('historical_artifacts_unchanged','pending')}. Saved-trace PPC replay: {replay.get('status','pending')}; decision unchanged: {replay.get('decision_unchanged','pending')}. No additional MCMC is used for replay. No commit, push or Stage 3G execution occurred.
'''
 (ROOT/'docs/stage3h_shared_opportunity_factor.md').write_text(text)
if __name__=='__main__':main()
