# Stage 3H — Shared Opportunity Latent Factor Model

**SHARED-FACTOR ADEQUACY UNRESOLVED**. Scientific wingspan coefficient: **SEALED**. No causal claim or multi-season replication claim is made.

Both H1 and H2 passed their initial sampler gates without recovery, but both failed conditional accuracy and joint opportunity PPCs. H2 reduced FTA-bin interval failures from three to zero while the frozen systematic directional-bias rule remained failed. The shared structure is computationally usable under these priors, but it does not establish predictive adequacy or prove that the original latent dimensions were redundant. The old F2 identification failure is unchanged.

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

Exactly 4,117 player-seasons, 857 players, 13 seasons and 469,099 FTA. SHA256 `1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871`. All 4,117 rows enter the hurdle; 3,980 positive-FTA rows enter the count and accuracy likelihoods, with all 137 zero rows retained in the accounting panel. The panel, residualization, anthropometrics, original categories and references are unchanged. No 2013–14, secondary panel, FTA threshold, player exclusion, MIN or new confounder is used.

## 7. H1 model

For each player, o and e are independent Normal(0,1). The accuracy effect is u=sigma_accuracy*(rho_AO*o+sqrt(1-rho_AO²)*e). Its variance is sigma_accuracy² and Corr(u,o)=rho_AO. Positive opportunity uses sigma_opportunity*o; sigma_opportunity>0 anchors the factor sign. Hurdle opportunity uses lambda_h*o; lambda_h is allowed either sign. The hurdle has Bernoulli any-FTA likelihood; positive counts use the exact Stage 3F zero-truncated NB; accuracy uses the original beta-binomial. All original fixed adjustment terms remain. GP is a coefficient-one log exposure offset only for positive counts. H1 accuracy contains no realized opportunity predictor.

## 8. H2 model

H2 adds only theta_W*within to H1 accuracy. The observed within values are read directly from the frozen Stage 3F decomposition, verified equal to the original calculation. There is no between-player term. H2 is predeclared and can run only when H1 samples reliably but fails a PPC. H1 sampler failure ends the ladder; a complete H1 pass also stops it. There is no H3.

## 9. Priors

Accuracy: intercept Normal(0,2.5), exposure/height Normal(0,0.5), positions/seasons Normal(0,1), log kappa Normal(3,2). Positive count: intercept Normal(log(2),1), exposure/height Normal(0,0.15), positions Normal(0,0.35), seasons Normal(0,0.25), log alpha Normal(log(2),1). Hurdle: intercept Normal(logit(0.95),1), exposure/height Normal(0,0.25), positions Normal(0,0.5), seasons Normal(0,0.35). New latent priors: sigma_opportunity HalfNormal(0.5), sigma_accuracy HalfNormal(1), lambda_h Normal(0,1), rho_AO Uniform(-1,1). H2 theta_W Normal(0,0.5). Software support transforms do not alter the induced uniform correlation prior. No prior tuning followed simulation.

## 10. Prior predictive checks

H1: 5,000 draws, seed 20260930; pass True; positive mean-rate mass >100/game 0.255186%; season-count mass >1,000,000 0.00003886%; zero-fraction 95% interval [0.01360213747874666, 0.34200267184843325]; extreme zero mass 0.1600%; accuracy near-zero/near-one masses 9.7098%/9.7543%; finite True. H2: 5,000 draws, same seed; pass True; positive-rate tail 0.240287%; season-count tail 0.00003401%; zero-fraction 95% interval [0.01360213747874666, 0.34200267184843325]; accuracy near-zero/near-one masses 9.7240%/9.7703%. No prior adjustment.

Frozen gross limits are ≤1% positive conditional mean rates above 100/game, ≤0.1% simulated player-season counts above one million, ≤90% combined zero-fraction mass below 0.1% or above 50%, finite probabilities and ≤25% accuracy mass in either tail below 0.01 or above 0.99 (the existing broad Stage 3D accuracy screen). Broad zero-range review does not fit prior constants to observed outcomes. Passing is a gross-scale prerequisite, not predictive adequacy.

## 11. H1 sampler diagnostics

Attempt 1; sampler pass True; max R-hat 1.003632; minimum bulk ESS 1298.76; minimum tail ESS 2479.56; divergences 0; tree-depth hits 0; BFMI 0.603, 0.622, 0.702, 0.639; finite covariance True.

Initial: Attempt 1; numeric gate True; visual review in the final diagnostic record; max R-hat 1.003632; minimum bulk ESS 1298.76; minimum tail ESS 2479.56; divergences 0; tree-depth hits 0; BFMI 0.603, 0.622, 0.702, 0.639; finite covariance True.

Four chains, seed 20260930, 2,000 warmup and 2,000 retained per chain, target acceptance 0.95. Exactly one unchanged-model recovery at 4,000/4,000 and 0.99 is allowed. Gates: max R-hat≤1.01, bulk/tail ESS≥400, BFMI≥0.3, zero divergences/depth hits, finite covariance and acceptable visual mixing. Every native latent o/e scalar and induced player effect is checked alongside fixed and structural globals. Anonymous scientific-parameter convergence must also pass. Backend gradients are checked before fitting.

## 12. H1 conditional accuracy PPC

Pass False; pooled pass True; global failures 2/7; season failures 0/13; FTA-bin failures 3/5; systematic volume pattern True.

Exactly 2,000 draws, seed 20260930, observed FTA fixed. The original pooled, seven-global, 13-season, five-FTA-bin and systematic low/high MCSE rules are unchanged. Bin limits are 1–9, 10–49, 50–99, 100–299 and 300+. Failure is pooled outside 99%, ≥3 global misses, ≥5 season misses, ≥2 bin misses, or the frozen systematic pattern beyond 2.576 MCSE (40 batches of 50).

## 13. H1 joint opportunity PPC

Pass False; zero-FTA pass True; observed 3.3277%, predictive mean 3.3517%, 99% interval [2.4531%, 4.3238%]. Total-FTA quantile failures 2/5; positive-count failures 2/3; season totals below/above 99% intervals 0/0.

positive_FTA_q25: observed 29.00, predictive mean 29.39, 99% interval [28.00, 31.00], outside False.

positive_FTA_q50: observed 79.00, predictive mean 73.41, 99% interval [70.00, 77.00], outside True.

positive_FTA_q75: observed 164.00, predictive mean 150.14, 99% interval [144.00, 156.75], outside True.

Generate hurdle states, positive counts and then makes using the same posterior factor draw. Zero fraction, Q25/Q50/Q75/Q90/Q95, season totals, positive-count quartiles and descriptive position summaries reuse Stage 3F functions and gates. Joint failure is zero outside 99%, ≥3 total-count quantile misses, ≥5 season totals outside in the same direction, or ≥2 positive-count quartile misses. No new release metric is used.

## 14. H2 results if reached

Attempt 1; sampler pass True; max R-hat 1.004138; minimum bulk ESS 1400.68; minimum tail ESS 2732.45; divergences 0; tree-depth hits 0; BFMI 0.644, 0.690, 0.691, 0.677; finite covariance True.

Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic volume pattern True.

Pass False; zero-FTA pass True; observed 3.3277%, predictive mean 3.3434%, 99% interval [2.4287%, 4.4696%]. Total-FTA quantile failures 2/5; positive-count failures 2/3; season totals below/above 99% intervals 0/0.

positive_FTA_q25: observed 29.00, predictive mean 29.41, 99% interval [28.00, 31.00], outside False.

positive_FTA_q50: observed 79.00, predictive mean 73.42, 99% interval [70.00, 77.00], outside True.

positive_FTA_q75: observed 164.00, predictive mean 150.24, 99% interval [144.00, 156.25], outside True.

H2 uses the same sampler, seed and recovery limits. Its conditional PPC holds observed within fixed; its joint PPC recomputes within from generated FTA by the exact frozen function before generating FTM. H2 sampler failure is recorded as classification D under the explicit section-22 stopping rule, with numerical failure distinguished from observed PPC failure. A prior prerequisite failure also stops without posterior inference or retuning.

## 15. Latent opportunity–accuracy relation

H1 permitted summaries:

| Parameter | Mean | Median | SD | 95% CrI |
|---|---:|---:|---:|---|
| rho_AO | 0.388323 | 0.389259 | 0.041921 | [0.302878, 0.468101] |
| lambda_h | 1.149563 | 1.148456 | 0.123027 | [0.911707, 1.394517] |
| sigma_opportunity | 0.705651 | 0.705620 | 0.021483 | [0.664111, 0.748093] |
| sigma_accuracy | 0.384802 | 0.384523 | 0.013123 | [0.359726, 0.411271] |
| alpha_FTA | 5.679058 | 5.675119 | 0.164763 | [5.366648, 6.007537] |
| kappa | 168.870232 | 168.426288 | 10.885433 | [149.007485, 191.404049] |

H2 permitted summaries:

| Parameter | Mean | Median | SD | 95% CrI |
|---|---:|---:|---:|---|
| rho_AO | 0.383130 | 0.384059 | 0.042236 | [0.300124, 0.464807] |
| lambda_h | 1.155386 | 1.154959 | 0.124110 | [0.918814, 1.402505] |
| sigma_opportunity | 0.705910 | 0.705567 | 0.021639 | [0.665432, 0.749655] |
| sigma_accuracy | 0.387274 | 0.387052 | 0.013005 | [0.362481, 0.413470] |
| alpha_FTA | 5.675286 | 5.673589 | 0.164198 | [5.353704, 5.998771] |
| kappa | 197.131647 | 196.707338 | 13.052645 | [172.961792, 224.440482] |
| theta_W | 0.292061 | 0.291921 | 0.021422 | [0.250450, 0.334558] |

rho_AO is an association between persistent latent opportunity and accuracy tendency under this model. lambda_h relates the factor to any-FTA log odds; sigma_opportunity is its positive-count log-rate loading. They are statistical constructs, not causal mechanisms. The within slope, if reportable, is in original log1p(FTA/GP) units and is associational.

## 16. Opportunity-process adequacy

H1: Pass False; zero-FTA pass True; observed 3.3277%, predictive mean 3.3517%, 99% interval [2.4531%, 4.3238%]. Total-FTA quantile failures 2/5; positive-count failures 2/3; season totals below/above 99% intervals 0/0.

positive_FTA_q25: observed 29.00, predictive mean 29.39, 99% interval [28.00, 31.00], outside False.

positive_FTA_q50: observed 79.00, predictive mean 73.41, 99% interval [70.00, 77.00], outside True.

positive_FTA_q75: observed 164.00, predictive mean 150.14, 99% interval [144.00, 156.75], outside True.

H2: Pass False; zero-FTA pass True; observed 3.3277%, predictive mean 3.3434%, 99% interval [2.4287%, 4.4696%]. Total-FTA quantile failures 2/5; positive-count failures 2/3; season totals below/above 99% intervals 0/0.

positive_FTA_q25: observed 29.00, predictive mean 29.41, 99% interval [28.00, 31.00], outside False.

positive_FTA_q50: observed 79.00, predictive mean 73.42, 99% interval [70.00, 77.00], outside True.

positive_FTA_q75: observed 164.00, predictive mean 150.24, 99% interval [144.00, 156.25], outside True.

A zero-frequency pass alone cannot establish full opportunity adequacy; positive-count and season checks remain binding. Position checks are descriptive, not additional selection thresholds.

## 17. Accuracy-volume adequacy

H1: Pass False; pooled pass True; global failures 2/7; season failures 0/13; FTA-bin failures 3/5; systematic volume pattern True.

H2: Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic volume pattern True.

Predictive checks address the observed accuracy-volume discrepancy without using scientific-effect direction. Unassessed checks are never treated as passes or observed failures.

## 18. Comparison with F1/F2

| Candidate | Sampler | Accuracy PPC | Opportunity PPC | Latent dimensions/player |
|---|---|---|---|---|
| F1 | True | False | False | 3 |
| F2 | False | unassessed | unassessed | 3 |
| H1 | True | False | False | 2 |
| H2 | True | False | False | 2 |

This comparison is generated only after the new decision freezes and concerns sampler behavior, PPC adequacy and latent dimension only. Historical F2 posterior summaries remain withheld. No scientific coefficient comparison is made.


![Accuracy PPC comparison](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3h_figures/01_accuracy_comparison.png>)

![Opportunity checks](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3h_figures/02_opportunity_PPC.png>)

![Latent association](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3h_figures/03_rho_AO.png>)

![Latent loadings](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3h_figures/04_latent_loadings.png>)

![Within adequacy parameter](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3h_figures/05_theta_W.png>)

## 19. Stage 3H classification

SHARED-FACTOR ADEQUACY UNRESOLVED.

Reason: H2 predictive inadequacy. Frozen candidate: None. A/B require complete sampler and both PPC passes; a prior or sampler failure never substitutes for evidence of predictive adequacy.

## 20. Stage 3G authorization

Authorized: False. Purpose: ESTIMAND REVIEW ONLY. Scientific-effect release authorized: False. Stage 3G executed: False. Only H1 or H2 complete adequacy passes can authorize this later review; old authorization records are not overwritten.

## 21. Scientific estimand caveat

Even H1 changes assumptions about persistent player heterogeneity and requires estimand review. H2 additionally conditions accuracy on realized within-player opportunity. Predictive adequacy is not scientific-effect authorization. The scientific coefficient remains sealed.

## 22. Selection limitations

Combine participation, anthropometric availability, NBA survival, shooting opportunity, between-player identification and measurement error remain limitations. Shared latent factors do not correct sample selection. These are in-sample conditional checks for observed players, not independent replication or out-of-sample validation. No causal claim is made.

## 23. Reproducibility

Protocol frozen 2026-09-30T18:51:09.857430+00:00; SHA256 `82d16b186fae8f9038c9ae91b03053de42bc91b3d2b0abb244dff7ad7255b2cd`. The pinned Stage 3C environment is reused without installation. Original zero-truncated NB implementation and its 150-point numerical validation are reused. Frozen model, prior, sampler, PPC, selection and inherited dependencies are hash-guarded. A pre-simulation provenance-path typo was corrected before any prior simulation or posterior fit, with the original preflight protocol preserved; no model, prior or gate changed. Traces are local and Git-ignored. Tests 26/26; historical artifacts unchanged 1107. Saved-trace PPC replay: EXACT_SAVED_TRACE_PPC_REPLAY; decision unchanged: True. No additional MCMC is used for replay. No commit, push or Stage 3G execution occurred.
