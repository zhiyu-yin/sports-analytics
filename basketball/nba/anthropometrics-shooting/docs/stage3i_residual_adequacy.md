# Stage 3I — Residual Adequacy Diagnosis

**RESIDUAL ADEQUACY UNRESOLVED**. Scientific wingspan coefficient: **SEALED**.

I1 sampled reliably but did not repair the directional accuracy bias. I2 and I3 failed after their single allowed recoveries, leaving their predictive adequacy unassessed.

## 1. Stage 3H residual failures

Historical decisions remain permanent. Stage 3H remains SHARED-FACTOR ADEQUACY UNRESOLVED. I0 reuses exact saved H2 diagnostics and PPCs, with no refit or resimulation. The saved H2 sampler passed.

Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic directional pattern True.

Pass False; zero-frequency pass True; observed zero 3.327666%, predictive mean 3.343442%, 99% interval [2.428710%, 4.469638%]. Total-FTA quantile failures 2/5; positive-count failures 2/3; season totals below/above 99% 0/0.

positive_FTA_q25: observed 29.00, predictive mean 29.41, 99% [28.00, 31.00], outside False.

positive_FTA_q50: observed 79.00, predictive mean 73.42, 99% [70.00, 77.00], outside True.

positive_FTA_q75: observed 164.00, predictive mean 150.24, 99% [144.00, 156.25], outside True.

## 2. Stage 3I objective

Diagnose two preidentified residual failures separately and together: nonlinear within-player opportunity in accuracy, and independent persistent count-specific heterogeneity. This is model-adequacy work. I1 and I2 are diagnostic only; I3 is the only eligible model. All three were frozen before any prior simulation or fit; no I4 exists.

## 3. Scientific firewall

The scientific wingspan coefficient remains SEALED. No sign, location, uncertainty, odds ratio, probability, contrast, plot or correlation is exported or used for selection. Only anonymous convergence information enters aggregate sampler gates. Decision code accepts typed Booleans only. Traces remain local and Git-ignored.

## 4. Frozen panel

Exactly 4,117 player-seasons, 857 players, 13 seasons, 469,099 FTA, 3,980 positive rows and 137 zero rows. SHA256 `1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871`. All rows enter the hurdle; positive rows enter count and accuracy likelihoods. No 2013–14, threshold, player exclusion, residualization refit, recoding, MIN or additional confounder.

## 5. Hypothesis A: nonlinear within effect

The single H2 within slope may leave curvature in the conditional accuracy-volume relationship. A predeclared centered quadratic tests that hypothesis without splines, cubic terms, raw FTA or a between-player observed opportunity term.

## 6. Hypothesis B: count-specific heterogeneity

The shared opportunity factor may not capture all persistent positive-count variation. An independent standard-normal player residual c enters only positive counts. It is independent of o and e, with no additional correlation parameter.

## 7. I1 model

Exact H2 except theta_W*within is replaced by gamma_W1*zW + gamma_W2*qW. Frozen within values are unchanged. Equal-row sample SD (ddof=1) s_W=0.2650297801192153; zW=w/s_W; qW=zW²−0.9997571046878795. The quadratic mean is 3.45e-17. Scaling uses every accounting row, including zero FTA, and no FTM outcome. All opportunity and latent components remain H2.

## 8. I2 model

Exact H2 linear accuracy term theta_W*within and shared structure, plus sigma_count_resid*c_i in positive-count log mean. c_i~Normal(0,1) independently of o/e. The hurdle remains lambda_h*o. Accuracy effect remains sigma_accuracy*(rho_AO*o+sqrt(1−rho_AO²)*e). Positive counts retain coefficient-one log(GP), original fixed terms and exact Stage 3F zero-truncated NB.

## 9. I3 combined model

Exactly I1 accuracy plus I2 count residual; unchanged H2 hurdle and shared accuracy/opportunity structure. The three candidates were independently predeclared. I1/I2 sampler or PPC failure does not block I3. I3 sampler failure ends the stage. No model or prior was changed after simulation.

## 10. Priors

gamma_W1 and gamma_W2 independently Normal(0,0.25), on standardized bases; sigma_count_resid HalfNormal(0.5); c_i Normal(0,1). I2 theta_W Normal(0,0.5). All other H2 priors remain exact: accuracy intercept Normal(0,2.5), exposure/height Normal(0,0.5), position/season Normal(0,1), log kappa Normal(3,2); positive intercept Normal(log(2),1), exposure/height Normal(0,0.15), position Normal(0,0.35), season Normal(0,0.25), log alpha Normal(log(2),1); hurdle intercept Normal(logit(0.95),1), exposure/height Normal(0,0.25), position Normal(0,0.5), season Normal(0,0.35). Shared priors: o/e independent Normal(0,1), sigma_accuracy HalfNormal(1), sigma_opportunity HalfNormal(0.5), lambda_h Normal(0,1), rho_AO Uniform(−1,1).

## 11. Prior predictive checks

I1: pass True; 5,000 draws, seed 20260930; rate >100/game mass 0.205883%; count >1,000,000 mass 0.00001943%; zero-fraction 95% [0.01360213747874666, 0.34200267184843325]; extreme-zero mass 0.1600%; accuracy tails below .01 / above .99 9.9151%/9.9495%; finite True.

I2: pass True; 5,000 draws, seed 20260930; rate >100/game mass 0.386514%; count >1,000,000 mass 0.00006315%; zero-fraction 95% [0.01360213747874666, 0.34200267184843325]; extreme-zero mass 0.1600%; accuracy tails below .01 / above .99 9.7240%/9.7703%; finite True.

I3: pass True; 5,000 draws, seed 20260930; rate >100/game mass 0.383240%; count >1,000,000 mass 0.00002915%; zero-fraction 95% [0.01360213747874666, 0.34200267184843325]; extreme-zero mass 0.1600%; accuracy tails below .01 / above .99 9.9151%/9.9495%; finite True.

All prior checks preceded all fits. Gates are unchanged: ≤1% positive conditional mean rates >100/game, ≤0.1% counts >one million, ≤90% combined extreme-zero mass, finite predictions, and ≤25% accuracy mass in either extreme tail. Broad zero-range review did not tune to outcomes. Gross prior passes do not establish adequacy.

## 12. I1 diagnostics and PPC

Attempt 1; sampler pass True; max R-hat 1.004110; minimum bulk/tail ESS 1505.70/2833.68; divergences 0; depth hits 0; BFMI 0.642, 0.649, 0.616, 0.627; finite covariance True.

Conditional accuracy: Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic directional pattern True.

Joint opportunity: Pass False; zero-frequency pass True; observed zero 3.327666%, predictive mean 3.342932%, 99% interval [2.428832%, 4.396405%]. Total-FTA quantile failures 2/5; positive-count failures 2/3; season totals below/above 99% 0/0.

positive_FTA_q25: observed 29.00, predictive mean 29.39, 99% [28.00, 31.00], outside False.

positive_FTA_q50: observed 79.00, predictive mean 73.40, 99% [70.00, 77.00], outside True.

positive_FTA_q75: observed 164.00, predictive mean 150.20, 99% [144.00, 157.00], outside True.

Within parameters:

| Parameter | Mean | Median | SD | 95% CrI |
|---|---:|---:|---:|---|
| gamma_W1 | 0.077918 | 0.077880 | 0.005503 | [0.067161, 0.088529] |
| gamma_W2 | -0.003364 | -0.003470 | 0.004055 | [-0.011401, 0.004712] |


Attempt 1 numeric gate True: R-hat 1.004110, bulk/tail ESS 1505.70/2833.68; divergences 0; depth hits 0.

## 13. I2 diagnostics and PPC

Attempt 2; sampler pass False; max R-hat 1.034235; minimum bulk/tail ESS 68.70/74.20; divergences 5; depth hits 0; BFMI 0.654, 0.689, 0.667, 0.697; finite covariance True.

Conditional accuracy: WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

Joint opportunity: WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

Count residual scale:

WITHHELD_FAILED_SAMPLER_GATE

Attempt 1 numeric gate False: R-hat 1.270951, bulk/tail ESS 14.94/94.09; divergences 1065; depth hits 0.

Attempt 2 numeric gate False: R-hat 1.034235, bulk/tail ESS 68.70/74.20; divergences 5; depth hits 0.

## 14. I3 diagnostics and PPC

Attempt 2; sampler pass False; max R-hat 1.028598; minimum bulk/tail ESS 148.29/160.36; divergences 0; depth hits 0; BFMI 0.670, 0.735, 0.698, 0.676; finite covariance True.

Conditional accuracy: WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

Joint opportunity: WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

Within parameters:

WITHHELD_FAILED_SAMPLER_GATE

Count residual scale:

WITHHELD_FAILED_SAMPLER_GATE

Attempt 1 numeric gate False: R-hat 1.746806, bulk/tail ESS 6.10/11.38; divergences 4404; depth hits 0.

Attempt 2 numeric gate False: R-hat 1.028598, bulk/tail ESS 148.29/160.36; divergences 0; depth hits 0.

## 15. Within curvature interpretation

The permitted quadratic summaries describe conditional association. A nonzero quadratic coefficient indicates that the linear within specification was incomplete under this model; it does not establish causal benefit from more attempts. Predictive repair requires the complete unchanged accuracy gate, including the directional MCSE rule.

I1: the quadratic 95% interval includes zero, giving little evidence that simple quadratic curvature explains the residual pattern. The accuracy gate still fails; this is not a verified accuracy repair.

Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic directional pattern True.

WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

## 16. Positive-count residual interpretation

The scale measures unobserved count-specific persistent player variation. It is not usage, aggression, star quality, rim pressure, or a biological trait. A nonzero scale alone does not prove a repaired distribution. The predeclared descriptive checks are positive mean, SD and Q10/Q25/Q50/Q75/Q90/Q95, with no new release thresholds. Neither I2 nor I3 passed sampling, so their scale estimates, shape statistics and PPCs are withheld. Their required CSVs contain explicit withholding status only. Whether count-specific heterogeneity repairs Q50/Q75 therefore remains unassessed.

## 17. Accuracy-volume comparison

Exactly 2,000 replications, seed 20260930, observed FTA fixed. Same pooled rate, seven global metrics, 13 season rates and five bins. Failure rules: pooled outside 99%, ≥3 global misses, ≥5 season misses, ≥2 bin misses, or the frozen opposite low/high bias beyond 2.576 MCSE (40 batches of 50 in chain-major order).

I0: Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic directional pattern True.

I1: Pass False; pooled pass True; global failures 1/7; season failures 0/13; FTA-bin failures 0/5; systematic directional pattern True.

I2: WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

I3: WITHHELD_FAILED_SAMPLER_GATE; predictive adequacy unassessed.

![Accuracy comparison](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3i_figures/01_accuracy_comparison.png>)

## 18. Opportunity-distribution comparison

For sampler-valid candidates, the frozen joint simulation generates hurdle state, exact zero-truncated positive FTA, then makes using the same posterior latent draw. Generated within values use the exact frozen decomposition. The I1/I3 protocol specifies that generated z/q use the frozen observed-panel SD and quadratic center; conditional prediction holds observed bases fixed. The gate is unchanged: zero outside 99%, ≥3/5 total-count quantile misses, ≥5 season totals outside in the same direction, or ≥2/3 positive quartile misses. Position summaries and extra positive shape metrics are descriptive.

![Positive FTA comparison](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3i_figures/02_positive_FTA_distribution.png>)

![Within terms](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3i_figures/03_within_parameters.png>)

![Count residual](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3i_figures/04_count_residual.png>)

## 19. Stage 3I classification

RESIDUAL ADEQUACY UNRESOLVED. I3 sampler failed after its allowed recovery; PPC unassessed. Only I3 sampler and both PPC gates determine this classification after protocol/firewall verification. Invalid samplers have withheld PPCs, not fabricated predictive failures. No AIC, WAIC, LOO or scientific-effect information enters selection.

## 20. Stage 3G authorization

Authorized: False. Purpose: ESTIMAND REVIEW ONLY. Scientific-effect release authorized: False. Stage 3G executed: False.

## 21. Scientific estimand caveat

I3 conditions accuracy on realized within-player opportunity. Role, health, team context, ability, foul drawing, playing time and unmeasured factors may affect that opportunity. Predictive adequacy cannot establish that this conditioning set answers the scientific question. Any future estimand review remains separate from scientific-effect release.

## 22. Remaining limitations

These are in-sample checks for observed players. Selection into combine measurement, NBA survival, measurement error, unbalanced observed careers and unmeasured factors remain. The quadratic is deliberately limited; independent normal residuals and the count family remain assumptions. No causal claim or multi-season replication claim is made. Failure ends this stage without another candidate.

## 23. Reproducibility

Protocol frozen 2026-09-30T20:19:55.859102+00:00; SHA256 `7d449a74b7414cd21160c81bd1fb133fcc104676a4cfbd8777ffd8938c8f9e08`. Initial sampling: four chains, 2,000 tune/2,000 retained, target .95, seed 20260930. One generic recovery per model: 4,000/4,000, target .99, unchanged model/prior. Gates: R-hat≤1.01, bulk/tail ESS≥400, BFMI≥.3, no divergences/depth hits, finite covariance, acceptable visual mixing. All fixed effects, dispersions, latent o/e/c elements, scales and induced effects are checked; the scientific coefficient is anonymous only. Backend gradients match the reference before fitting. The pinned environment and exact validated Stage 3F likelihood are reused without installation. Tests 27/27; 1199 historical artifacts unchanged. Saved-trace I1 PPC replay matched every saved permitted parameter/PPC artifact exactly, without new MCMC; the decision hash remained unchanged. Final artifact hashes are recorded separately. No commit, push or Stage 3G execution.
