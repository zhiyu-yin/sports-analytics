# Stage 3F — Hurdle Opportunity and Within/Between Adequacy

**STRUCTURAL ADEQUACY UNRESOLVED**. Scientific coefficient status: **SEALED**. Scientific inference is not authorized. Stage 3G has not been started. No multi-season replication claim is made.

## 1. Historical adequacy failures

Stage 3C remains EXECUTION FAIL — PRIMARY PPC ADEQUACY GATE FAILED; Stage 3D remains ADEQUACY UNRESOLVED — D3 FAILS PRIOR-PREDICTIVE PREREQUISITE; Stage 3D-R remains ADEQUACY UNRESOLVED — D3 FAILS. Stage 3E remains NOT AUTHORIZED. F0 reuses the exact saved Stage 3D-R D3 diagnostics and 2,000-replicate PPC, without refitting. Its pooled accuracy passed, three bins failed, and the systematic volume pattern remained. Its observed zero fraction was 3.3277%, versus predictive mean 1.1800%; Q25/Q50/Q75 also failed. These artifacts are preserved by hashes.

## 2. Stage 3F objective

Separate whether attempts occur, how many occur once positive, persistent opportunity differences, and within-player opportunity deviations. The objective is conditional-distribution adequacy. Selection receives only typed gate booleans and never scientific-effect summaries. No causal claim is made.

## 3. Why zero FTA requires separate consideration

A single NB component ties its zero probability to its count mean and dispersion. A hurdle supplies a separate Bernoulli probability for any attempts and an exactly zero-truncated count distribution for positives. A better zero fit would establish improved predictive representation, not a distinct causal zero-generating mechanism.

## 4. Persistent and within-player opportunity

Persistent observed opportunity averages a player's log1p(FTA/GP) across their available seasons. A within-player deviation measures departure from that player's own average. These can have different conditional accuracy relationships. The decomposition uses no FTM information, but uses realized opportunity and therefore changes the accuracy conditioning set.

## 5. Fixed candidate ladder

Frozen at 2026-09-29T18:16:24.018168+00:00, before prior checks or fitting. F0 is the saved failed reference. F1 is the hurdle model with a joint three-dimensional player-effect structure and unchanged accuracy mean. F2 was independently predeclared as F1 plus between/within accuracy terms. No candidate was added or simplified after results.

Primary panel SHA256 `1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871`: 4,117 player-seasons, 857 players, 13 seasons, 469,099 FTA; 2013–14 excluded. The panel, anthropometrics, residual transformation, height center, position labels and seasonal coding were not rebuilt. All rows enter the hurdle; 3,980 positive-FTA rows enter the truncated count and accuracy likelihoods. No FTA threshold filtering or player exclusion occurred.

## 6. Hurdle model

Any-FTA Bernoulli logit contains an intercept, frozen residual exposure, centered height, original position/season terms, and hurdle player intercept. There is no GP offset in that component. Positive FTA follow a zero-truncated NB2 with coefficient-one log(GP) offset and corresponding fixed/player opportunity terms. GP is strictly positive; no MIN field enters the models.

Accuracy remains beta-binomial with the original adjustment variables and accuracy player intercept. Non-centered effects ordered accuracy/positive opportunity/hurdle use a 3×3 LKJCholeskyCov construction. No two-dimensional or independent-effects simplification was made.

The positive log likelihood is log NB(y) minus log(1−P_NB(0)), for integer y≥1, with log P_NB(0)=−alpha×log1p(mu/alpha). The correction is evaluated as log(−expm1(log P_NB(0))) for stability. This matches the [documented PyMC hurdle probability mass function](https://www.pymc.io/projects/docs/en/v5.24.0/api/distributions/generated/pymc.HurdleNegativeBinomial.html). It was validated against both PyMC Truncated and independent SciPy calculations over 150 parameter/count combinations; exact truncated random draws were checked against analytic conditional means. Native Truncated's gradient took 5.407 seconds on the pinned NUMBA backend because of object-mode fallback. The transparent exact formula avoids that computational limitation; it is not ordinary NB fitted to positive rows.

## 7. Within/between decomposition

x=log1p(FTA/GP); between=mean(x) over each player's available seasons; within=x−between; centered_between=between−mean(between across unique players). Center=0.764259238110757. Each unique player receives equal weight for the global center; their available seasons receive equal weight within player. All 137 zero-FTA rows contribute x=0. Maximum absolute within-player mean=5.55e-16. Formula, data and code hashes were frozen before fitting.

F2 accuracy adds theta_B×centered_between and theta_W×within. Conditional PPC holds observed attempts and these covariates fixed. Joint PPC generates all hurdle/count outcomes, recomputes the decomposition from the generated panel including its zeros and unique-player center, then generates makes using the same posterior player-effect draw. This was predeclared; generated opportunity is not replaced by observed opportunity in the joint check.

## 8. Priors

Positive opportunity: intercept Normal(log(2),1), raw exposure/height slopes Normal(0,0.15), positions Normal(0,0.35), seasons Normal(0,0.25), log alpha Normal(log(2),1). Hurdle: intercept Normal(logit(0.95),1), exposure/height slopes Normal(0,0.25), positions Normal(0,0.5), seasons Normal(0,0.35). The 0.95 center was selected once from the user-specified domain prior; it was not estimated from observed zeros.

Marginal SDs are HalfNormal(1), HalfNormal(0.5), HalfNormal(1), ordered accuracy/positive opportunity/hurdle; LKJ eta=2. Accuracy intercept Normal(0,2.5), exposure/height Normal(0,0.5), position/season Normal(0,1), log precision Normal(3,2) remain unchanged. F2 theta_B and theta_W each have Normal(0,0.5) priors. No prior changed after simulation.

## 9. Prior predictive checks

Seed 20260928, 5,000 draws per candidate. Both checks passed before fitting:

- F1: 5,000 draws; positive conditional-rate mass >100/game 0.232276%; season-count mass >1,000,000 0.0000048579%; zero-fraction 95% interval [1.336%, 33.520%]; combined extreme zero-fraction mass 0.100%.
- F2: 5,000 draws; positive conditional-rate mass >100/game 0.237080%; season-count mass >1,000,000 0.0000000000%; zero-fraction 95% interval [1.336%, 33.520%]; combined extreme zero-fraction mass 0.100%.

The positive conditional mean is mu_NB/(1−P_NB(0)); its rate divides by GP. The underlying mu_NB/GP quantiles are also saved for comparison with Stage 3D-R. Frozen gross limits are ≤1% above 100 FTA/game and ≤0.1% simulated seasons above one million FTA. The zero-fraction distribution must have broad plausible spread and ≤90% combined mass below 0.1% or above 50%. The broad interval review did not compare priors to the observed zero percentage. Extreme count tails remain possible; this screen is not posterior adequacy.

## 10. F1 sampler and PPC

max R-hat 1.004523; minimum bulk/tail ESS 1026.5/2183.3; divergences 0; depth hits 0; BFMI 0.654, 0.697, 0.754, 0.685; sampler pass True; attempt 1.

Conditional accuracy: pass False; pooled-rate pass True; global failures 2/7; season failures 0/13; FTA-bin failures 3/5; systematic low/high pattern True.

Joint opportunity: pass False; original opportunity gate pass True; zero-fraction pass True: observed 3.3277%, predictive mean 3.3449%, 99% interval [2.4290%, 4.3478%]; FTA quantile failures 2/5; positive-count quantile failures 2/3; season totals below/above intervals 0/0.

F1 passes the zero-frequency check, but its added positive-count gate still fails; separating zeros therefore does not establish full opportunity adequacy.

Initial sampling: four chains, 2,000 tuning and 2,000 retained per chain, target_accept 0.95, seed 20260928. One generic recovery at 4,000/4,000 and 0.99 was permitted only for failed sampler diagnostics. No failed sampler contributes a PPC release pass.

## 11. F2 sampler and PPC

max R-hat 1.115705; minimum bulk/tail ESS 28.8/54.4; divergences 0; depth hits 0; BFMI 0.741, 0.712, 0.655, 0.687; sampler pass False; attempt 2.

F2 attempt 1 failed numerical convergence: max R-hat 1.166630, minimum bulk/tail ESS 17.2/51.6. The single predeclared recovery used four chains with 4,000 tuning and 4,000 retained draws at target acceptance 0.99, with unchanged model and priors. Its result is the final diagnostic record above.

Conditional accuracy: NOT_RUN_FAILED_SAMPLER_GATE.

Joint opportunity: NOT_RUN_FAILED_SAMPLER_GATE.

F2 uses the same sampling and recovery rules. Major fixed terms, dispersions, SDs and all three correlations enter the diagnostic gate. The scientific coefficient contributes only anonymous numerical convergence checks; it is never plotted or summarized. Compiled gradients matched reference gradients before fitting. Visual trace/energy reviews accompany sampler passes.

## 12. Between/within diagnostic parameters

Between-player theta_B: WITHHELD_FAILED_SAMPLER_GATE.

Within-player theta_W: WITHHELD_FAILED_SAMPLER_GATE.

No reportable opportunity slopes because F2 sampling failed. These are associational opportunity diagnostics under the specified model. Their intervals cannot override a predictive failure or establish scientific replication.

![Between and within parameters](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3f_figures/03_between_within_parameters.png>)

## 13. Random-effect correlations

- F1 corr_uv: mean 0.387711; median 0.387829; SD 0.040812; 95% CrI [0.307312, 0.466822].
- F1 corr_uh: mean 0.434950; median 0.437366; SD 0.098237; 95% CrI [0.236098, 0.620423].
- F1 corr_vh: mean 0.842794; median 0.849215; SD 0.071920; 95% CrI [0.686486, 0.961822].

F2 correlation summaries are withheld because its sampler failed the convergence gate. The reported F1 correlations cannot substitute for F2 estimates.

These describe remaining latent player propensities conditional on each model. F2 correlations condition additionally on the realized between/within terms, so their interpretation differs from F1. None is a causal mechanism estimate.

![Latent correlations](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3f_figures/04_random_effect_correlations.png>)

## 14. Accuracy adequacy comparison

| Candidate | Sampler pass | Accuracy pass | Joint opportunity pass | FTA-bin failures | Systematic pattern |
|---|---|---|---|---:|---|
| F0 | True | False | False | 3 | True |
| F1 | True | False | False | 3 | True |
| F2 | False | Not evaluated | Not evaluated | unassessed | unassessed |


| Candidate / FTA bin | Observed FT% | Predictive mean FT% | 99% interval | Outside |
|---|---:|---:|---|---|
| F0 / 1-9 | 68.4047 | 71.8640 | [68.8178, 74.6518] | True |
| F0 / 10-49 | 71.5284 | 73.2213 | [72.3840, 74.0327] | True |
| F0 / 50-99 | 74.4322 | 74.8113 | [74.1717, 75.4579] | False |
| F0 / 100-299 | 76.6353 | 76.2600 | [75.8322, 76.6685] | False |
| F0 / 300+ | 79.0442 | 78.2857 | [77.6150, 78.9307] | True |
| F1 / 1-9 | 68.4047 | 71.8591 | [69.0754, 74.5483] | True |
| F1 / 10-49 | 71.5284 | 73.2144 | [72.3805, 74.0291] | True |
| F1 / 50-99 | 74.4322 | 74.8200 | [74.1717, 75.4660] | False |
| F1 / 100-299 | 76.6353 | 76.2618 | [75.8688, 76.7063] | False |
| F1 / 300+ | 79.0442 | 78.2815 | [77.5886, 78.9258] | True |


Exactly 2,000 replications, seed 20260929. The unchanged gates fail on pooled rate outside 99%, ≥3 of seven global metrics outside 99%, ≥5 of 13 season rates outside 99%, ≥2 of five pooled FTA-bin rates outside 99%, or the frozen systematic opposite low/high bias pattern. Directional evidence uses bias beyond 2.576 MCSE, with 40 chain-major batches of 50 draws. Predictive intervals and MCSE serve different purposes. F0 is copied, not simulated again.

![Accuracy by FTA bin](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3f_figures/01_accuracy_FTA_bins.png>)

## 15. Opportunity adequacy comparison

| Candidate / positive-count quantile | Observed | Predictive mean | 99% interval | Outside |
|---|---:|---:|---|---|
| F1 / positive_FTA_q25 | 29.00 | 29.37 | [28.00, 31.00] | False |
| F1 / positive_FTA_q50 | 79.00 | 73.33 | [70.00, 77.00] | True |
| F1 / positive_FTA_q75 | 164.00 | 150.14 | [144.00, 157.00] | True |


The original joint gate fails if zero fraction lies outside 99%, ≥3 of five total-FTA quantiles lie outside 99%, or ≥5 season totals lie outside 99% in the same direction. The predeclared added hurdle gate fails if ≥2 of three positive-count quartiles miss 99%. F0 did not save positive-only quartile checks; those missing results are not invented. Overall, original-position and season-level opportunity metrics remain available in each joint CSV, including descriptive positive-count means/SDs.

![Zeros and positive counts](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3f_figures/02_zero_positive_count_PPC.png>)

## 16. Stage 3F classification

STRUCTURAL ADEQUACY UNRESOLVED. Frozen at 2026-09-29T20:11:46.418809+00:00 A complete F2 sampler/accuracy/opportunity pass with protocol/firewall checks resolves structural adequacy. A valid opportunity repair without accuracy repair, or F2 accuracy repair without opportunity repair, can be partial resolution. Failed F2 sampling ends unresolved. A PPC withheld for failed sampling is unassessed, not an observed predictive failure. Parameter magnitudes, signs, p-values and model-fit rankings are not decision inputs.

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

Tests passed: 22/22. Prior artifacts are hash-checked. Scientific-effect values are not used for candidate selection. No commit, push, new confounder, FTA threshold, full-panel fit, 2013–14 inclusion, or Stage 3G execution occurred.
