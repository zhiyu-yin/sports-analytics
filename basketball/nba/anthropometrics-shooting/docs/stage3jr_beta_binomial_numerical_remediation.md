# Stage 3J-R — Beta-Binomial Bootstrap Numerical Remediation

**NUMERICAL REMEDIATION PASS**. Historical Stage 3J remains EXECUTION FAIL; J1 is unchanged.

## 1. Why Stage 3J failed execution

Historical Stage 3J remains **EXECUTION FAIL**: 299 of 2,000 J2 bootstrap fits failed its frozen numerical gates. Its J2 interval was withheld. This new numerical-remediation decision does not overwrite that historical decision, J1, any earlier sensitivity, or prior model-development failures. All 1406 protected historical artifacts remain byte-identical.

## 2. What remains scientifically unchanged

J2 remains a fixed-effect grouped beta-binomial: FTM_it ~ BetaBinomial(FTA_it, μ_it, κ), logit(μ_it)=intercept + residual wingspan + barefoot height + original combine position + season; ρ=1/(1+κ). The same likelihood, estimand, categorical coding, residualization, rows and counts are used. There is no new predictor, penalty, prior, regularization term, player random effect, opportunity variable, FTA predictor or MIN predictor.

Primary panel: 4,117 player-seasons, 857 accounting players, 3,980 positive-FTA rows and 469,099 FTA; 2013–14 excluded. SHA256 `1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871`. Residual wingspan remains wingspan−(4.574910520685837+1.0013410045156863×barefoot height), inches. J1 was not refitted or reinterpreted; its preserved primary-result SHA256 is `79b8f461efcc61e0a6e3ff33728fa0d0019839aae03b9809d530f8c9b6906e02`.

## 3. Original 299 bootstrap failures

All 299 failed samples were replayed with the exact original Stage 2 function and original starts, before remedy implementation. Additional function evaluations, score norms, κ, coefficient norms, rank, conditioning, category absence, separation indicators, boundaries and information diagnostics were recorded. The existing logs lacked some of these fields; the new fields are explicitly reference-replay diagnostics, not invented historical log entries. All recorded historical start outcomes, likelihoods and maximum scores reproduced.

The comparison set was 100 evenly spaced replicate indices among the 1,701 historical successes, fixed before diagnostic replay. Full old-success agreement later covers all 1,701. Per-replicate diagnostics appear in `failed_replicate_diagnostics.csv`; all three starts appear in `reference_start_diagnostics.csv` and individual raw diagnostic JSONs.

## 4. Failure diagnosis

| group | replicates | score_only | optimizer_termination | score_failure | Hessian_failure | boundary | nonfinite | separation_like | absent_category |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FAIL | 299 | 294 | 5 | 296 | 0 | 0 | 0 | 0 | 129 |
| PASS | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 |

The 299 failures comprise 294 score-only failures and five optimizer-termination failures; two of the latter also miss the score gate. Three-start likelihoods differ by at most 1.2e-09 among failed samples despite rejection. The maximum absolute score is 0.0039277884 against the strict <0.001 criterion. Neither nonpositive information, active precision boundaries, nonfinite evaluations nor separation-like fitted probabilities was detected.

Raw design condition ranges [4763.8476947655745, 5918.7587781990305] for failures and [4769.475874224481, 5630.419968965229] for the success comparison set. Existing standardization reduces these to [7.43141240154617, 9.513727507259453] and [7.574372486502838, 9.482291808951254], respectively. Missing dummy categories occur in both groups and retain the frozen deterministic rank-reduction rule. These diagnostics implicate stopping/finite-precision behavior rather than demonstrated likelihood nonidentification; they do not prove global uniqueness in every conceivable parameter region.

## 5. Frozen numerical remediation protocol

The original R0 already used an analytic gradient and predictor scaling. Neither is presented as a new statistical remedy. The first frozen numerical ladder polished all three R0 endpoints with Newton-CG, then deterministic hybr score-solving and trust-exact fallbacks. It repaired 295/299, leaving 4 solver-status failures. That complete trial, protocol, source and raw results are preserved under `ladder_v1/`.

Before any second retry or full rerun, a **prospective numerical-only amendment** added R4: scipy `root(method="lm")` applied to the same score equations. Selection was based only on numerical failure diagnostics; no wingspan coefficient distribution, interval or fraction negative was inspected. This was an amended numerical ladder, not an unchanged first-trial protocol.

Final uniform procedure: fresh original R0 from the same grouped-GLM start and κ starts 10, 50, 200; always polish each R0 endpoint with Newton-CG; if it fails the unchanged gate, try hybr, trust-exact, then LM, each from that same R0 endpoint. LM uses ftol=xtol=gtol=1e-12 and maxiter=500. Numerical LM damping is internal to solving score=0; it is not a penalty in the beta-binomial likelihood. Positive observed information and likelihood agreement remain required. The first accepted method per start is retained; the highest finite likelihood among all three accepted starts determines the solution. No cross-sample or scientific-direction warm-start selection occurs.

All original acceptance gates remain: optimizer success; maximum absolute score <0.001 **in the original Stage 2 standardized coordinates**; −9.99<log κ<15.99; all three starts accepted; likelihood spread≤1e-5; positive information; finite covariance; covariance-diagonal relative difference≤0.001 between Hessian steps 1e-4 and 5e-5. An additional parameter-spread flag of 1e-4 detects differing solutions at nearly equal likelihood; it does not relax an old gate. Final protocol SHA256 `bdbd3a4cdd1041ac76d4d2f17cf90e613412a23d2ef01484ab47254b0c0a48da`.

## 6. Likelihood / gradient validation

Unchanged Stage 2 log likelihood versus SciPy beta-binomial: maximum absolute difference 8e-11. Synthetic fixtures span κ=2,10,32,200 and grouped counts, including endpoint counts. Analytic score versus central finite differences (step 1e-5): maximum absolute difference 1.81e-06. Independent trigamma observed information versus finite differences of the original analytic score: maximum absolute difference 7.02e-07. Synthetic solver recovery and positive-information checks also pass. Final covariance gates continue to use the original validated Stage 2 numerical Hessian at its original two steps.

## 7. Scaling validation

The old sample-specific transformation is retained exactly. For raw design X, means m and SDs s (intercept unchanged), Z=(X−m)/s and β_raw=Tβ_scaled; log κ is unchanged. With block transform A=diag(T,1), g_scaled=Aᵀg_raw and H_scaled=AᵀH_rawA. No smaller gradient produced by new arbitrary scaling is substituted for the old acceptance score.

| max_loglik_difference | max_score_difference | max_information_difference | max_inverse_error |
| --- | --- | --- | --- |
| 3.6379788e-12 | 8.8562047e-11 | 1.9903382e-08 | 2.220446e-16 |

## 8. Retry results

First frozen ladder: 295 repaired, 4 unresolved. After the prospectively frozen numerical-only amendment, every one of the original 299 failed sample identities was retried: **299 repaired, 0 unresolved**. No failed sample was replaced. The final failed-only receipt preceded the full rerun. No coefficient distribution was summarized in either diagnostic trial.

## 9. Full 2,000-bootstrap reproduction

All 2,000 original samples were rerun with the same final algorithm, rather than combining old successes with repaired fits. Successful fits: **2000/2,000**; failures: **0/2,000**. Original seed remains 20260931; no new bootstrap sampling design or realization was introduced. Because historical files stored hashes rather than full draw vectors, the exact old PCG64 stream was reconstructed once and all 2,000 hashes verified before fitting. Cached draw vectors then drove fitting without any RNG calls. Every sample contains the same 857 player draws, duplicate instances and full retained season sets; zero rows remain in accounting.

Four independent spawned processes use single-thread numerical libraries and return results in replicate-index order. This changes scheduling only. Fixed-index sequential replay at samples 1,9,13 agrees within 1e-10. Accepted numerical methods across the 6,000 original starts: {'trust-exact': 51, 'hybr': 4474, 'Newton-CG': 1409, 'lm': 66}. Numeric-only full results are in `full_bootstrap_results.csv`; coefficients, if authorized, are released separately in `released_bootstrap_coefficients.csv` after the decision freeze.

## 10. Old vs new fit agreement

| compared | max_absolute_beta_difference | max_log_likelihood_difference | max_score_difference | max_old_success_replay_beta_difference | passed |
| --- | --- | --- | --- | --- | --- |
| 1701 | 2.6930333e-08 | 2.910383e-10 | 0.00097854534 | 9.8879238e-17 | True |

Every previously successful sample was replayed with the exact old estimator to recover missing likelihood/score diagnostics, and its old exposure coefficient was checked against the original saved value (tolerance 1e-10). New-vs-old acceptance tolerances were fixed before retries: coefficient difference≤1e-5, log-likelihood difference≤1e-7, score difference≤0.0011. The score comparison is the absolute difference between the old and new maximum absolute score components; it measures movement toward a smaller gradient and should not be confused with changes in the coefficient. Comparison passed: True. No scientifically favorable solution was selected.

## 11. Final J2 bootstrap result if numerically valid

Only after numerical acceptance was frozen at 2026-10-01T01:34:09.631588+00:00, the full 2,000-value summary was generated at 2026-10-01T01:34:11.362737+00:00. **Mean β=-0.03395475; SD=0.00868294; 95% percentile interval [-0.05044245, -0.01701569]; fraction β<0=1.000000; failures=0.** NumPy linear percentile interpolation and SD ddof=1 remain unchanged. Every scheduled sample contributes; this is not a successful-only interval. The fraction is an empirical bootstrap summary, not a posterior probability.

The original full-sample J2 estimate is merely quoted from its unchanged Stage 3J record: β=-0.03342554, OR=0.96712692, κ=32.01931413, ρ=0.03028531. It was not refitted in this stage. J2 remains secondary; it cannot replace J1. The negative J2 bootstrap direction is consistent with the already-frozen J1 direction; this adds no new interpretation or modification of J1.

## 12. Stage 3J-R decision

**NUMERICAL REMEDIATION PASS**. The immutable acceptance record precedes release of any bootstrap distribution summary. Historical Stage 3J remains **EXECUTION FAIL**, unchanged. This stage concerns numerical reliability only; scientific sign or interval exclusion is not an acceptance criterion. The final test and build receipts verify preservation, exact samples, likelihood/scaling, all original gates, uniform execution and reproduction. Final A–T tests: 20/20 passed, zero failures/errors/skips.

## 13. Implications for manuscript robustness

The planned J2 bootstrap robustness uncertainty is now complete under the numerical remediation. J1 remains the primary association, with its original point estimate, CR1 covariance and player-bootstrap uncertainty unchanged. The planned numerical robustness package can be reported with this explicit remediation history; no historical failure is relabeled. No Stage 4 manuscript work was started.

## 14. Reproducibility

Existing `.venv` reused: Python 3.10.8, NumPy 2.2.6, SciPy 1.15.3, statsmodels 0.14.5. No package installation. Original inputs and historical artifacts are protected by the new preservation manifest; the initial ladder has its own preservation receipt. A reference-wrapper preflight correction removed an unnecessary scale/unscale round trip so original start arrays replay exactly; a test-only comment-matching correction was recorded before retries. Neither altered the likelihood, samples or numerical gates.

Workflow: `stage3jr_common.py` (protect/reconstruct), `stage3jr_diagnose.py` (R0 audit), `stage3jr_validation.py`, `stage3jr_freeze.py`, preflight tests, initial `stage3jr_run.py retry`; preserve that trial, freeze `stage3jr_amend.py`, repeat tests and `retry`; then `full`, `reproduce`, `decision`, `summary`, report and final verification. Frozen retry/full commands are not silent rerun commands; existing artifacts should be verified instead. The exact receipts/logs and code snapshots record both numerical versions. Final report path: `docs/stage3jr_beta_binomial_numerical_remediation.md`. Nothing was committed or pushed.

## 15. Remaining limitations

Numerical convergence does not establish a correct scientific mean model, causal identification, solved opportunity generation, absence of selection, or generalization to all NBA players. The historical attempt-volume misfit and measured-player selection remain. Residual wingspan is time invariant; J2 remains a between-player association with repeated outcomes and fixed reference geometry. The bootstrap conditions on the observed measurement and eligibility process. Three-start agreement and positive local information support numerical consistency, not a proof of a globally unique maximum. **No causal claim is made.**
