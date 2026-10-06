# Stage 3F-R — F2 Identification and Reparameterization

**IDENTIFICATION UNRESOLVED — NO EQUIVALENT F2 PARAMETERIZATION PASSES SAMPLER**. Scientific parameter: **SEALED**. No causal claim or scientific replication claim is made.

## 1. Historical F2 sampler failure

Stage 3F permanently remains STRUCTURAL ADEQUACY UNRESOLVED. Its F2 recovery had maximum R-hat 1.115705, minimum bulk ESS 28.77, and minimum tail ESS 54.36 for its major-parameter gate. Stage 3C, Stage 3D and Stage 3D-R failures remain unchanged. Stage 3E remains NOT AUTHORIZED. Existing trace diagnostics are reused; no historical model is refitted or decision relabeled.

## 2. Objective

Diagnose fixed-effect, covariance and latent-effect geometry and test only scientifically equivalent computational coordinates for F2. R1 scales the two opportunity terms with exactly transformed priors. R2 centers the same multivariate latent distribution. R3, conditionally eligible after R1/R2 failure, uses a proved mixed representation. No R4, changed conditioning set, narrowed prior, predictor addition/removal, or eligible-model simplification is allowed.

## 3. Scientific firewall

The scientific wingspan coefficient is never plotted, correlated with other posterior parameters, or summarized. It contributes an anonymous sampler-pass Boolean and internal aggregate convergence checks only. Diagnostic models cannot become scientific models. Selection uses ordered eligible-model sampler Booleans and frozen PPC Booleans, not scientific-effect location or direction. Permitted failed-chain geometry is explicitly distinguished from valid posterior inference.

## 4. Failed-trace diagnosis

Both saved original F2 attempts were audited. The recovery's worst blocks are accuracy–positive opportunity correlation (R-hat 1.115705, bulk ESS 28.77), between-opportunity slope (R-hat 1.110817, bulk ESS 29.74), player effects (maximum R-hat 1.102644), standardized player effects (1.101512), and accuracy–hurdle correlation (1.095655). Accuracy SD also misses the ESS gate. The within-opportunity term is not a dominant poor-mixing block.

The failed chains show movement correlation between theta_B and corr(u,v) of -0.970780, with corr(u,h) -0.874009, with accuracy SD 0.450190, and with accuracy intercept 0.073950. These describe the available failed trajectories, not a trustworthy converged posterior correlation estimate. No correlation involving the sealed coefficient was computed for publication.

All scalar non-sealed global and latent convergence results are in failed_f2_parameter_diagnostics.csv; block summaries and chain mean normalized ranks are saved separately. Theta_W has R-hat 1.000400, bulk ESS 16,578.79 and tail ESS 12,111.04. Theta_B mean normalized ranks span 0.368–0.572 across chains, while theta_W spans 0.491–0.507. Rank separation diagnoses incomplete mixing without publishing failed original-unit slope estimates. Neither rank separation nor a trace excursion proves distinct modes.

Absolute covariance correlations exceed 0.95 in 4.400% of the failed recovery draws for the positive-opportunity/hurdle pair, but not for the two accuracy pairs. No marginal SD draw falls below 0.05 or above 3. These findings do not support a simple SD-to-zero funnel as the sole explanation. Scale–latent-RMS correlations are saved as funnel indicators; persistent coupling is more evident than a uniquely diagnosed funnel.

![Failed convergence](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3fr_figures/01_failed_convergence.png>)
![Permitted geometry](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3fr_figures/02_permitted_correlations.png>)

## 5. Predictor identification audit

Exactly 4,117 player-seasons, 857 players, 13 seasons and 469,099 FTA; panel SHA256 `1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871`. No rows or players were removed. The frozen FTA/GP decomposition and its zero rows were reused unchanged. No FTM or FT-percentage association was calculated for this design audit.

Row-weighted sample SDs (ddof=1): between 0.435494386763124, within 0.265029780119215. Global between centering remains the original equal-unique-player center; it is not recentered by rows. Player counts by observed seasons: one 112, two 147, three–four 221, five or more 377. All 112 single-season players have within=0. Actual variation is supplied by 743 players and 4001 observations. Distribution quantiles and complete predictor-only correlations, including height and residual-wingspan predictors, are saved in the audit artifacts.

![Predictor distributions](</Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/anthropometrics-shooting/docs/stage3fr_figures/03_predictor_distributions.png>)

## 6. Fixed-effect conditioning

Accuracy design rank 30 of 30; raw condition number 106.674128; standardized condition number 8.292982. All singular values are saved. There is no exact aliasing or severe standardized near-collinearity. The larger raw condition number partly reflects units and sparse category indicators. Height and point-guard encoding correlate approximately −0.651. Original position and season coding and references remain unchanged. No column was dropped or orthogonalized.

## 7. DIAG-A accuracy-only result

Attempt 2: sampler pass True; maximum R-hat 1.002870; minimum bulk ESS 1764.31; minimum tail ESS 2925.06; divergences 0; tree-depth hits 0; BFMI 0.683, 0.634, 0.706, 0.711; finite covariance True.

Initial run: Attempt 1: sampler pass False; maximum R-hat 1.013485; minimum bulk ESS 324.36; minimum tail ESS 925.27; divergences 0; tree-depth hits 0; BFMI 0.695, 0.715, 0.633, 0.740; finite covariance True.

This retains the complete F2 accuracy predictor and its original priors, with a HalfNormal(1) accuracy SD and a non-centered univariate player intercept. It omits opportunity likelihoods solely to diagnose computation. It cannot authorize inference or become selected F2.

## 8. DIAG-B independent-covariance result

Attempt 1: sampler pass True; maximum R-hat 1.005937; minimum bulk ESS 885.84; minimum tail ESS 1379.37; divergences 0; tree-depth hits 0; BFMI 0.610, 0.713, 0.597, 0.689; finite covariance True.

Initial run: Attempt 1: sampler pass pending visual review; maximum R-hat 1.005937; minimum bulk ESS 885.84; minimum tail ESS 1379.37; divergences 0; tree-depth hits 0; BFMI 0.610, 0.713, 0.597, 0.689; finite covariance True.

This retains all F2 likelihoods and marginal SD priors but fixes cross-effect correlations to zero for diagnosis only. This altered model is never eligible for selection or scientific reporting.

## 9. DIAG-C opportunity-only result

Attempt 2: sampler pass True; maximum R-hat 1.004846; minimum bulk ESS 1244.97; minimum tail ESS 2351.19; divergences 0; tree-depth hits 0; BFMI 0.670, 0.707, 0.699, 0.710; finite covariance True.

Initial run: Attempt 1: sampler pass False; maximum R-hat 1.016494; minimum bulk ESS 418.20; minimum tail ESS 1066.35; divergences 0; tree-depth hits 0; BFMI 0.721, 0.645, 0.746, 0.666; finite covariance True.

Only the Bernoulli hurdle and exact zero-truncated NB likelihood enter. No accuracy outcome enters its likelihood. Its two-dimensional opportunity correlation uses LKJ eta=2.5, which is the marginal pair distribution induced by the original three-dimensional LKJ eta=2; marginal SD priors are unchanged. This is a diagnostic submodel, not an eligible replacement for full F2.

## 10. Source of poor geometry

DIAG-A and DIAG-B pass while original F2 failed, implicating coupling through the correlated three-dimensional player structure (case B). All three diagnostic submodels pass, reinforcing coupled joint posterior geometry as the dominant issue (case D). Exact predictor scaling alone did not repair the sampler. Fully centered R2 also had inadequate BFMI after recovery. R3's initial mixed representation restored BFMI above the threshold but still failed R-hat and ESS, distinguishing energy exploration from complete convergence. This comparison does not prove structural nonidentifiability or isolate a unique causal source of the geometry.

The failed-chain coupling and the outcome-free design audit distinguish posterior geometry from predictor-matrix rank. A computational pass does not prove full statistical identification or predictive adequacy. Conclusions here concern sampling under the frozen model, not causality.

## 11. R1 exact reparameterization

between_std=centered_between/sB and within_std=within/sW. theta_B_std=sB*theta_B and theta_W_std=sW*theta_W, with Normal(0,0.5*sB) and Normal(0,0.5*sW) priors. Dividing each coefficient by its predictor SD recovers the original coefficient. The two-coordinate Jacobian is sB*sW. Covariance, non-centered player effects, likelihoods, categorical coding and every other prior remain original F2.

## 12. R1 diagnostics

Attempt 2: sampler pass False; maximum R-hat 1.064270; minimum bulk ESS 76.72; minimum tail ESS 185.46; divergences 0; tree-depth hits 0; BFMI 0.717, 0.714, 0.665, 0.728; finite covariance True.

Initial run: Attempt 1: sampler pass False; maximum R-hat 1.153444; minimum bulk ESS 28.06; minimum tail ESS 176.04; divergences 0; tree-depth hits 0; BFMI 0.652, 0.761, 0.689, 0.749; finite covariance True.

Initial plan: four chains, 2,000 warmup and 2,000 retained draws each, target acceptance 0.95, seed 20260928. Only one recovery is allowed: 4,000/4,000 at 0.99. The same generic plan applies to R2/R3. DIAG models use 1,500/1,500 initially and a single 3,000/3,000 recovery. Recovery is triggered only by sampler failure.

## 13. R2 if needed

Attempt 2: sampler pass False; maximum R-hat 1.048366; minimum bulk ESS 90.26; minimum tail ESS 135.23; divergences 0; tree-depth hits 0; BFMI 0.035, 0.054, 0.049, 0.046; finite covariance True.

Initial run: Attempt 1: sampler pass False; maximum R-hat 1.139274; minimum bulk ESS 21.20; minimum tail ESS 66.39; divergences 0; tree-depth hits 0; BFMI 0.057, 0.032, 0.075, 0.019; finite covariance True.

R2 retains R1 scaling and samples player effects directly as MVNormal(0,L*L.T). The covariance prior is identical. From original standard coordinates, r=Lz; inverse z=L^(-1)r; forward latent Jacobian det(L) per player. The centered MVNormal log density plus N*log(det(L)) equals the original standard-normal latent log density. The covariance-coordinate transformation is unchanged.

## 14. R3 if needed

Attempt 2: sampler pass False; maximum R-hat 1.017671; minimum bulk ESS 209.11; minimum tail ESS 448.24; divergences 0; tree-depth hits 0; BFMI 0.869, 0.856, 0.811, 0.831; finite covariance True.

Initial run: Attempt 1: sampler pass False; maximum R-hat 1.109070; minimum bulk ESS 29.57; minimum tail ESS 209.60; divergences 0; tree-depth hits 0; BFMI 0.800, 0.882, 0.873, 0.820; finite covariance True.

A mixed representation was derived and frozen before any new posterior fit. It centers (u,v), keeping the conditional hurdle residual standard normal. For A=L[:2,:2], q=A*z[:2] and e=z2; h=L20*z0+L21*z1+L22*e. Inverse and Jacobian det(A) per player are documented in r3_equivalence_derivation.md. Native normalized densities account for this Jacobian; no extra density factor is added. The induced full latent distribution and all likelihoods remain exact F2. This does not project effects away from opportunity predictors or estimate a centering coefficient.

## 15. Equivalence verification

| Coordinates | Passed | Max density error | Max likelihood error | Max predictor error | Paired prior counts exact |
|---|---|---|---|---|---|
| R1 | True | 3.81e-09 | 0 | 1.55e-15 | True |
| R2 | True | 3.82e-09 | 0 | 1.55e-15 | True |
| R3 | True | 3.81e-09 | 0 | 2.13e-14 | True |

Each implemented eligible validation compares 12 perturbed matched points on the real design, independent SciPy latent-density fixtures, inverse transforms, coefficient-prior densities and all three deterministic predictors/likelihoods. Five hundred paired original-prior draws are mapped into new coordinates. Matching predictors and shared random streams yield paired identical opportunity counts and conditional makes, a stronger check than unpaired Monte Carlo mean agreement. Prior arrays remain protected locally; only numerical error checks are public. These checks preserve original-space priors, not merely similarly shaped priors.

## 16. Selected computational parameterization

None: no equivalent parameterization passed.

Selection follows R1, then R2 only after R1 failure, then predeclared R3 only after R2 failure. Numerical convergence requires maximum R-hat ≤1.01, minimum bulk/tail ESS ≥400, BFMI ≥0.3, zero unresolved divergences or tree-depth hits, finite covariance and acceptable visual mixing. Every native and induced latent scalar is checked, alongside major globals. The anonymous sealed check must also pass. No diagnostic model is selectable.



## 17. F2 PPC if sampler passed

Not run: no eligible equivalent sampler has passed. This is unassessed predictive adequacy, not an observed PPC failure.

The existing Stage 3F F2 PPC implementation is reused verbatim with only stage-local paths and the equivalent model builder substituted. If reached, exactly 2,000 replications use seed 20260929. Conditional prediction fixes observed FTA and decomposition. Joint prediction generates hurdle/count outcomes, recomputes the decomposition and unique-player center, then generates makes. The seven globals, 13 seasons, five FTA bins, systematic directional MCSE rule, zero fraction, total-count quantiles and added positive-count quartile gates remain unchanged. No new release metric is introduced.

## 18. Between/within parameters if reportable

Withheld: no eligible equivalent sampler has passed.

## 19. Random-effect correlations if reportable

Withheld until an eligible sampler passes.

## 20. Stage 3F-R classification

IDENTIFICATION UNRESOLVED — NO EQUIVALENT F2 PARAMETERIZATION PASSES SAMPLER.

The only outcomes are A: equivalent sampler and both PPCs pass; B: equivalent sampler passes but PPC fails; C: no equivalent sampler passes. Verification tests do not override failed scientific adequacy. Historical Stage 3F remains unresolved regardless of this new stage's outcome.

## 21. Stage 3G authorization

Authorized: False. Only classification A may authorize estimand review. No classification authorizes the sealed scientific coefficient's release. Stage 3G was not started. F2 still conditions on realized opportunity, and therefore differs from the original Stage 3C scientific conditioning set. Reparameterization changes none of F2's conditioning variables.

## 22. What remains unresolved

Predictive adequacy and scientific estimand validity are separate. A successful numerical representation does not remove selection, measurement, unbalanced-career or unobserved-factor limitations. Diagnostic restrictions on covariance cannot justify simplifying eligible F2. No causal claim is made. Opportunity diagnostic summaries, when available, are associational.

## 23. Reproducibility

Protocol frozen 2026-09-29T20:45:58.781129+00:00. Pinned Stage 3C environment reused without installation or modification. No prior report, trace or decision was overwritten. All new traces and prior arrays remain local and Git-ignored. Hashes cover frozen code, data, prior/decomposition inputs, attempts, equivalence checks, figures, tests and final outputs.

The user-reported usage-limit interruption was an infrastructure/session event, not a scientific gate. The diagnostic process remained alive; completed audits, R1 equivalence and DIAG-A attempt 1 were reused after integrity checks. No fit was restarted on resume. Full record: resume_after_usage_limit.md. No model, prior, threshold, data, draw budget or scientific rule changed because of the interruption.

R2's validator initially encountered an input-interface TypeError before an equivalence decision. The unfrozen checker was corrected to accept unused covariance inputs in the centered observed likelihood. The frozen model and all mathematical checks and tolerances remained unchanged; validation then passed. The original log and explanation are preserved in validator_input_handling_repair.md.

Tests: 23/23. Preserved historical artifacts: 948. No commit, push, Stage 3G execution, FTA threshold filtering, player removal, 2013–14 inclusion, MIN predictor or new confounder occurred.
