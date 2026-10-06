# Stage 3D-R — Opportunity Prior Calibration and Adequacy

**ADEQUACY UNRESOLVED — D3 FAILS**. Prior calibration: **PRIOR CALIBRATION PASSED**. Selected future model: **NONE**. Stage 3E authorized: **False**. The scientific wingspan coefficient remains sealed; no scientific replication conclusion is made.

## 1. Historical Stage 3D prior failure

Stage 3D permanently remains ADEQUACY UNRESOLVED — D3 FAILS PRIOR-PREDICTIVE PREREQUISITE. Its original opportunity prior placed approximately 9.3% of mean rates above 100 attempts/game and generated extreme season-count tails. No Stage 3D candidate posterior existed. Stage 3C also permanently remains EXECUTION FAIL — PRIMARY PPC ADEQUACY GATE FAILED. Neither historical decision has been overwritten.

The D0 comparison reuses its saved 1,000-replicate PPC without refitting. Its saved global count omits rate mean, which was not available in that artifact; the D0 global count therefore has a narrower basis than the new candidates. Its saved pooled-rate and four-bin failures remain independently decisive.

## 2. Why a prospective prior amendment is justified

The user authorized one new opportunity-prior specification to address gross scale behavior before any D3 posterior had been fitted. The likelihood and informative-opportunity hypothesis are unchanged. The dated amendment was frozen at 2026-09-29T01:21:52.192578+00:00 with SHA256 `8e273a702e0a811f53f97e0d42cf64133f57e0fc210bc97f578b4cbf4a7635b8`. All prior artifacts are protected by hashes.

## 3. Why this is not posterior/result-driven tuning

No D3 scientific coefficient, latent correlation or posterior predictive result existed before this amendment. Prior constants came directly from the authorized natural-rate specification, not observed FTA quantiles or an optimization of posterior fit. The sole amended prior was simulated once with the frozen seed; no second amendment was made. Sampling and adequacy decisions do not use the scientific effect's location, direction, uncertainty or probability.

## 4. Rate-scale prior interpretation

The opportunity linear predictor excluding log(GP) is log expected FTA/game. The new baseline log rate is Normal(log(2),1): median 2 FTA/game and approximate 95% interval [0.282, 14.199], before covariates/player effects. A log-rate increment of 0.15 multiplies rate by 1.162; a player-effect SD of 0.5 corresponds to a one-SD multiplier of 1.649. The tighter priors are more regularizing than the original log-scale priors; they reduce exponentiated tail dispersion.

## 5. New frozen opportunity priors

Intercept Normal(log(2),1); raw residual-exposure and centered-height slopes Normal(0,0.15); position effects Normal(0,0.35); season effects Normal(0,0.25); opportunity SD HalfNormal(0.5). Log alpha_FTA ~ Normal(log(2),1), alpha_FTA=exp(log alpha_FTA). This one-to-one transform preserves the NB2 likelihood, whose variance is mu+mu²/alpha, but deliberately changes its prior from HalfNormal(5) to lognormal.

Accuracy priors remain exactly frozen: intercept Normal(0,2.5), exposure/height slopes Normal(0,0.5), original position/season terms Normal(0,1), accuracy SD HalfNormal(1), log precision Normal(3,2). LKJ eta remains 2. D1/D2 priors and models are unchanged. No prior was modified after simulation or sampling.

## 6. Prior predictive results

5,000 draws; seed 20260928. Implied FTA/game mean-rate quantiles: Q1=0.0882, Q5=0.2302, Q25=0.8323, Q50=1.9804, Q75=4.7028, Q95=17.2014, Q99=45.7534, Q99.9=150.6615. Fractions above 20, 50 and 100/game: 3.987656%, 0.851644%, 0.224790%.

Simulated season FTA quantiles: Q1=0.00, Q5=1.00, Q25=16.00, Q50=61.00, Q75=196.00, Q95=944.00, Q99=2,896.00, Q99.9=10,956.00. Maximum simulated season count=1,468,920; maximum implied rate=8,404.37/game. Fraction above one million season attempts=0.0000145737%. Extreme tails remain possible; a gross-gate pass is not a claim of a tightly realistic prior. Descriptive extra thresholds do not determine release.

## 7. Prior gate decision

Both unchanged gates passed: mean-rate mass above 100/game≤1%, and simulated season-count mass above one million≤0.1%. Values were finite. The unchanged accuracy prior also remains broad, with lower/upper near-boundary fractions 9.7081%/10.0282%. The prior decision was frozen before D1/D2/D3 sampling began. No observed FTA quantile was used to choose priors.

## 8. D1 diagnostic result

D1 adds centered log(1+FTA) only as a diagnostic accuracy-mean term. Four chains, 1,500 tuning and 1,500 retained draws each, target acceptance 0.95. max R-hat 1.009949; minimum bulk/tail ESS 373.7/789.3; divergences 0; max-depth hits 0; minimum BFMI 0.684; sampler pass False. Mean-volume parameter: WITHHELD_FAILED_SAMPLER_GATE; Minimum bulk ESS below 400; posterior exists but no reportable mechanism summary. Conditional accuracy assessment: NOT_RUN_FAILED_SAMPLER_GATE — A failed sampler cannot pass adequacy; no D1 recovery authorized.

D1 changes the conditioning set and cannot become the future scientific model. No recovery for D1 was authorized by the frozen plan; a failed ESS threshold is not rounded into a pass.

## 9. D2 diagnostic result

D2 keeps the accuracy mean and makes log precision linear in centered log(1+FTA). Four chains, 1,500 tuning and 1,500 retained draws each, target acceptance 0.95. max R-hat 1.009845; minimum bulk/tail ESS 412.6/904.3; divergences 0; max-depth hits 0; minimum BFMI 0.688; sampler pass True. Dispersion-volume parameter: mean -0.137855, median -0.137443, SD 0.107884, 95% equal-tail CrI [-0.360354, 0.064679]. Representative rho summaries: FTA 5: mean 0.003930, median 0.003682, SD 0.001527, 95% equal-tail CrI [0.001654, 0.007574]; FTA 25: mean 0.004589, median 0.004499, SD 0.001060, 95% equal-tail CrI [0.002789, 0.006938]; FTA 75: mean 0.005218, median 0.005203, SD 0.000654, 95% equal-tail CrI [0.004013, 0.006567]; FTA 200: mean 0.005929, median 0.005920, SD 0.000387, 95% equal-tail CrI [0.005190, 0.006711]; FTA 400: mean 0.006533, median 0.006507, SD 0.000630, 95% equal-tail CrI [0.005366, 0.007865]

Conditional accuracy assessment: pooled-rate 99% pass False; global failures 3; season failures 0/13; FTA-bin failures 4/5; systematic low/high pattern True; conditional gate pass False. D2 remains diagnostic only, regardless of its performance. No scientific coefficient is extracted for comparison.

## 10. D3 joint model

The opportunity model is negative binomial with log(GP) fixed at coefficient one, the same frozen raw residual exposure, centered height, original position and season terms, and a player opportunity intercept. The accuracy model is beta-binomial for FTM out of observed positive FTA with the unchanged covariates and player accuracy intercept. Realized FTA is not added to the D3 accuracy mean.

Player accuracy/opportunity effects remain non-centered bivariate normal through LKJCholeskyCov. All 4,117 accounting rows enter opportunity; 3,980 positive-FTA rows enter accuracy. GP is positive and validated against the preserved official audit; no minutes are used. The 13-season primary panel excludes 2013–14, retains all 857 players and 469,099 FTA, and matches SHA256 `1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871`. The height center and log-volume center remain 77.53028004667445 and 4.030428177092034.

## 11. D3 sampler diagnostics

max R-hat 1.007504; minimum bulk/tail ESS 1040.4/2270.5; divergences 0; max-depth hits 0; minimum BFMI 0.589; sampler pass True. Final attempt=1. Initial plan: four chains × 2,000 tuning and 2,000 retained, target acceptance 0.95, seed 20260928. Only the frozen generic D3 recovery may increase these to 4,000/4,000 and 0.99; every attempt is retained. No statistical structure or prior changed for recovery.

Numerical gates include every major accuracy/opportunity position and season term, dispersion, both SDs and latent correlation. The sealed coefficient contributes anonymous rank/convergence checks only. Its raw trace, location and scale are not published. Visual mixing and energy reviews accompany any sampler pass. Compiled D3 gradients matched the reference at the initial point within rtol=atol=1e-8; PyMC NUTS remains the sampler.

## 12. Conditional accuracy PPC

pooled-rate 99% pass True; global failures 2; season failures 0/13; FTA-bin failures 3/5; systematic low/high pattern True; conditional gate pass False. The conditional assessment uses exactly 2,000 predictive replications with observed FTA fixed and the joint posterior. The gate fails for pooled rate outside 99%, ≥3 global metrics outside 99%, ≥5 of 13 season rates outside 99%, ≥2 of five FTA bins outside 99%, or the frozen opposite low/high-volume pattern beyond Monte Carlo uncertainty.

Global metrics: rate mean, SD, Q05, Q50, Q95, zero fraction and perfect fraction. Within-player repeated-season variability is checked separately. The pattern rule compares bin predictive-mean bias with 2.576 times MCSE, using 40 consecutive batches of 50 replications in chain-major order. Predictive intervals and Monte Carlo uncertainty have different roles and are not interchanged.

| FTA bin | Observed FT% | Replicated mean FT% | 99% predictive interval | Outside 99% | MCSE of mean, pp |
|---|---:|---:|---|---|---:|
| 1-9 | 68.4047 | 71.8640 | [68.8178, 74.6518] | True | 0.02884 |
| 10-49 | 71.5284 | 73.2213 | [72.3840, 74.0327] | True | 0.00670 |
| 50-99 | 74.4322 | 74.8113 | [74.1717, 75.4579] | False | 0.00629 |
| 100-299 | 76.6353 | 76.2600 | [75.8322, 76.6685] | False | 0.00301 |
| 300+ | 79.0442 | 78.2857 | [77.6150, 78.9307] | True | 0.00605 |


![Frozen-bin accuracy checks](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3dr_figures/01_FTA_bin_accuracy.png>)

## 13. Joint opportunity PPC

Joint gate pass False; zero-frequency 99% pass False; quantile failures 3/5; season totals below/above 99% intervals 0/0. This simulation first generates attempts, then makes conditional on generated attempts and the same correlated player draw. It is distinct from the conditional accuracy release gate. Frozen opportunity failure rules: zero frequency outside 99%; at least three of five count quantiles outside 99%; or at least five season totals outside 99% in the same direction. Original-position count distributions and joint makes/rates are descriptive additional checks, not alternative selection criteria. Detailed zero-frequency, quantile, season and position metrics are saved in the joint evidence table.

| Opportunity metric | Observed | Replicated mean | 99% predictive interval | Outside 99% |
|---|---:|---:|---|---|
| FTA_zero_fraction | 0.033277 | 0.011800 | [0.008016, 0.015789] | True |
| FTA_q25 | 25.000000 | 27.073000 | [26.000000, 29.000000] | True |
| FTA_q50 | 75.000000 | 70.156500 | [67.000000, 73.000000] | True |
| FTA_q75 | 160.000000 | 146.250000 | [140.000000, 152.005000] | True |
| FTA_q90 | 270.400000 | 261.152700 | [247.398000, 275.002000] | False |
| FTA_q95 | 373.200000 | 359.923000 | [336.997000, 384.006000] | False |


Descriptive position checks (not additional gates):

| Position | Observed mean FTA | Predictive mean FTA | Observed zero % | Predictive zero % | Zero % 99% interval |
|---|---:|---:|---:|---:|---|
| C | 121.83 | 117.90 | 1.976 | 1.288 | [0.000, 2.767] |
| C-PF | 122.22 | 117.09 | 2.778 | 0.278 | [0.000, 1.852] |
| PF | 98.06 | 94.24 | 2.606 | 1.264 | [0.412, 2.195] |
| PF-C | 150.76 | 146.01 | 4.478 | 1.148 | [0.000, 2.985] |
| PF-SF | 100.48 | 95.14 | 3.509 | 1.418 | [0.000, 4.386] |
| PG | 129.60 | 126.33 | 3.472 | 1.342 | [0.417, 2.500] |
| PG-SG | 124.99 | 124.61 | 1.923 | 0.651 | [0.000, 2.564] |
| SF | 103.50 | 101.21 | 4.000 | 1.086 | [0.174, 2.087] |
| SF-PF | 127.41 | 123.99 | 1.493 | 0.676 | [0.000, 2.239] |
| SF-SG | 130.19 | 127.64 | 5.036 | 1.723 | [0.000, 4.317] |
| SG | 104.97 | 104.29 | 3.520 | 1.251 | [0.320, 2.240] |
| SG-PG | 106.37 | 104.20 | 1.149 | 0.214 | [0.000, 1.155] |
| SG-SF | 105.45 | 102.41 | 5.147 | 1.342 | [0.000, 2.941] |
| unknown | 200.50 | 152.49 | 0.000 | 0.013 | [0.000, 0.000] |


## 14. Latent opportunity–accuracy correlation

mean 0.392678, median 0.393736, SD 0.041538, 95% equal-tail CrI [0.308058, 0.471436]. P(corr_uv>0)=1.0, estimated as the fraction of retained draws above zero; a value of one is Monte Carlo resolution, not mathematical certainty. A positive value means that greater persistent opportunity-per-game tendency accompanies greater persistent accuracy tendency under this model; a negative value means the opposite. This is an associational latent parameter. No causal claim is made. A correlation result does not override failed predictive or sampler gates.

## 15. Model-adequacy decision

Frozen at 2026-09-29T01:51:05.263761+00:00: **ADEQUACY UNRESOLVED — D3 FAILS**. Future model=NONE. The selection function receives only typed Boolean gate records; permitted mechanism summaries are appended after the selection calculation, not supplied to it. D1/D2 cannot authorize future inference. No scientific-effect summary, p-value, AIC, WAIC or LOO determines selection. No D4, spline, hurdle, zero-inflation, interaction or new covariate was introduced.

## 16. Stage 3E authorization

Authorization=False; scientific parameter status=NOT_AUTHORIZED. This is a recorded future-stage decision, not execution of Stage 3E. The scientific wingspan coefficient remains sealed in local ignored traces; no effect sign, mean, median, SD, interval, odds ratio, probability or wingspan contrast appears in this report or the comparison/decision artifacts.

## 17. Remaining limitations

Gross prior calibration does not prove model adequacy. D1 directly conditions on realized attempts and changes interpretation. The joint model assumes the specified count families, linear predictors and bivariate player-effect distribution; a persistent correlation need not represent within-player opportunity/accuracy dependence. Measurement coverage remains approximately 51%–67%, with selection into combine measurement, NBA survival and playing opportunity uncorrected. Scientific time-invariant exposure identification remains between-player and is not causally identified. No model has been chosen by its scientific coefficient.

> Public NBA game-level minute displays and the archived game records agreed at the available whole-second resolution in the audited sample, while small discrepancies remained between summed game displays and NBA season-level decimal minute displays. Because season-level MIN was not the scientific outcome, exposure, or primary model predictor, and because shooting counts and analytical eligibility reconciled, the amended prospective validation protocol treated season-total MIN as an ancillary representation field rather than an exact numerical release gate. The internal NBA aggregation mechanism remains unknown.

## 18. Reproducibility

Reuse of the pinned Stage 3C environment introduces no package changes. Amendment, panel and code hashes, prior timing, all sampler settings, traces and diagnostic/PPC artifacts are recorded in the manifest. Posterior traces are Git-ignored and contain sealed parameters needed for computation. Predictive code obtains probabilities from compiled model deterministics rather than exporting the scientific slope. Only explicitly permitted volume/dispersion/correlation parameters receive summaries.

Run order: setup once; amended prior check; candidate fitting and numerical diagnostics; visual diagnostic review; conditional/joint PPC; adequacy decision freeze; report; final verification. Historical scripts were not rerun. Verification tests: 23/23. Saved-trace predictive replay is recorded separately. Tests distinguish code/provenance correctness from model adequacy. No FTA threshold filtering, full-panel fit, new confounder, causal claim, commit, push or Stage 3E execution occurred.
