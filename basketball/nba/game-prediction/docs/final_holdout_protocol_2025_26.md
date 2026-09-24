# Final 2025–26 holdout protocol

**FROZEN — NOT YET EXECUTED**

Stage 5A is protocol/infrastructure work only. No 2025–26 schedule, identity, feature, outcome, prediction or performance information has been accessed. This document grants no opening authorization.

## 1. Scientific hypothesis
The predeclared confirmatory question is whether frozen features_plus_elo_logistic retains lower probability loss than frozen raw Elo on the final untouched 2025–26 season. Directional replication requires negative mean differences for both primary losses. A mixed direction is a mixed result; secondary metrics cannot override it. No significance-based success rule is claimed.

## 2. Confirmatory Model C
The single primary confirmatory candidate is `features_plus_elo_logistic`, Stage 3 Model C. Its identity and complete recipe/allowlist hashes are recorded in `stage5a_evidence/final_holdout_freeze.json`. It was selected before final-holdout opening; another candidate cannot become the primary after observing results.

## 3. Primary benchmark Elo
The primary benchmark is `raw_elo`. Rating initialization remains 1500, probability scale 400, K=20, designated-home H=50 and offseason alpha=0.50. Predict before the target-game update, then update only from binary completed-game outcomes. No margin-of-victory or venue adjustment is introduced.

## 4. Frozen recipes
Model C receives exactly the existing ordered 32 basketball pregame features plus frozen elo_logit. Logistic settings remain C=0.01, L2, lbfgs, max_iter=5000, tol=1e-4 and random_state=0. Training-fitted median imputation with missingness indicators precedes StandardScaler and the estimator. Elo-logit arithmetic and clipping remain unchanged. No target score, identity, new feature, feature subset or neutral-site flag enters its matrix.

The seven recipes, including native-missing HGB D/E, remain exactly those in the unchanged Stage 4A candidate freeze. Saved Stage 5 fitted objects remain frozen and hashed; Stage 5A does not load or fit them. No family, seed, hyperparameter, preprocessing or calibration change is permitted based on Stage 5 evidence.

## 5. Frozen training policy
All logistic/HGB fitted statistical parameters remain based on 2015–16 through 2022–23 only. Neither 2023–24 nor 2024–25 is added to coefficient/preprocessing training. Use the saved frozen estimators after integrity checks; do not refit during Stage 5A.

Elo is an online state model: its parameters remain fixed while ratings evolve from completed earlier games. A future separately authorized executor may carry this fixed state chronologically through completed 2023–24 and 2024–25 before the first 2025–26 prediction, and then update only after each completed holdout game. This changes state, not the learned statistical recipe. Rolling feature definitions, warmup retention and season resets are unchanged. Stage 5A performs no such replay.

## 6. Primary metrics
Exactly log loss and Brier score, using the frozen metric implementation. Binary log loss uses natural logs and clips probabilities only within its logarithms to [1e-15, 1−1e-15]. Brier uses original probabilities. All candidates must share exactly the same validated game set; reject missing/nonfinite values rather than dropping rows. Prioritize these two losses in the final conclusion.

## 7. Secondary metrics
Accuracy uses p>=0.5 for a home-win decision. ROC-AUC uses the existing rank/tie implementation and is explicitly undefined for a single outcome class. Fixed-bin calibration/ECE, average predicted probability, observed designated-home win rate, bin counts and populated-bin counts are descriptive. They do not replace the primary losses.

## 8. Primary comparison
`features_plus_elo_logistic minus raw_elo`: report delta_log_loss, delta_brier, delta_accuracy and delta_roc_auc. Negative log-loss/Brier differences favor Model C. The target remains P(designated home team wins). Preserve this direction and comparison even if another frozen model performs better on a secondary measure.

## 9. Prior 2023–24 / 2024–25 evidence
Frozen 2023–24 development-validation differences were −0.0054648466903319814 log loss and −0.002743510327393839 Brier. Frozen 2024–25 pre-holdout differences were −0.008501549491097049 and −0.003929011660068954. These already-observed results remain evidence, not permission to tune. Report each season with its role separately; do not pool them with the final holdout. The final question is a new-season directional replication, not equality of magnitudes or a claim that games are independent.

## 10. Uncertainty method
Freeze paired per-game differences, loss_ModelC−loss_Elo, separately for log loss and Brier, using the identical clipping/formulas. Report the per-game mean, median and interquartile range. Preserve paired differences internally for the final evaluation artifact, without inspecting individual errors before aggregate persistence.

Use a calendar-date cluster bootstrap: 10,000 replicates; random seed 0; numpy.random.default_rng(0), PCG64, with the dependency checkpoint recorded in the freeze. Sort G unique game dates chronologically. In each replicate draw G date indices uniformly with replacement, keeping every game on each sampled date together and repeating an entire date cluster when sampled multiple times. Use the same draw for both loss differences. Calculate each replicate's game-weighted mean as total sampled paired-loss sums divided by total sampled game counts; do not average unweighted daily means or resample games independently.

Report descriptive standard error as the sample standard deviation (ddof=1) of the 10,000 replicate means. Report approximate percentile 95% intervals using the 2.5th and 97.5th quantiles, numpy.quantile(method="linear"). Label them **date-clustered descriptive bootstrap intervals**. These are not formal proof of independence-adjusted significance: clustering by date does not remove across-date or team dependence. No p-values or multiplicity-adjusted significance claim is planned for the two primary losses. Do not tune using intervals or switch methods after seeing them.

Reject missing/nonfinite paired losses/dates, duplicate game keys, or fewer than two date clusters. Stop and disclose instead of substituting a post-opening method. `uncertainty_protocol.json` is the machine-readable specification. No bootstrap implementation has been enabled or run in Stage 5A.

## 11. Calibration method
Use the existing ten fixed bins [0,.1), [.1,.2), …, [.9,1], retaining empty bins. Compute the unchanged count-weighted absolute bin error (ECE). Primary figure/tables compare raw Elo and Model C; all-seven descriptive tables may also be reported. No isotonic, Platt, temperature or other calibration fitting is allowed. Sparse-bin and bin-dependence limitations must be reported.

## 12. Seven-model transparency policy
Report constant_home_prior, raw_elo, basketball_features_logistic, elo_logistic, features_plus_elo_logistic, basketball_features_hgb and features_plus_elo_hgb. Model C is the confirmatory candidate and Elo the primary benchmark. The remaining five are secondary descriptive comparisons. Do not conceal poor results or select a new winner by changing the metric. Candidate expansion invalidates this freeze and requires a separately documented protocol; an opened holdout cannot become unseen again.

## 13. Final opening ledger requirements
`stage5a_evidence/final_opening_ledger.schema.json` is a schema only, not an executed ledger. Future Stage 6 must record explicit user authorization and its timestamp/hash; authorized season 2025–26; this protocol hash; confirmatory and benchmark hashes; code/dependency hashes; metric definitions; uncertainty specification; expected dataset scope; first physical data access timestamp; first outcome decode timestamp; and aggregate-result persistence timestamp. Access timestamps are not populated in Stage 5A.

Expected scope is the full validated NBA regular season under the existing canonical pairing and designated-home contract, excluding postseason and non-regular-season exhibition/championship records. No actual 2025–26 schedule, game count, date range or completeness status is known/validated by Stage 5A. Stage 6 must specify and validate scope under explicit authorization before scoring; an integrity failure stops, not selects a convenient subset.

The future ledger must exist before any physical final-season access, including schedule/identity requests, and record the access boundary durably before invoking its reader. The first outcome decode must be separately recorded. A completed opening cannot be represented later as still sealed. Deterministic reproduction is not independent evidence.

## 14. No-post-opening-tuning rule
No change to C, Elo, HGB, seed, features, missingness, preprocessing, model family, training window, metric definitions, bootstrap/calibration policy, game inclusion or candidate set after opening. No favorable-game selection or outlier removal. No fitting using 2024–25 or the final holdout. Individual-game inspection is deferred until aggregate metrics are persisted; subsequent error analysis is descriptive post-holdout work and cannot justify a claim of unchanged untouched-holdout confirmation after model changes.

## 15. Bug policy
Before opening: fix the bug, rerun infrastructure checks and create an explicitly versioned re-freeze. After observing final-holdout aggregate performance: STOP, preserve evidence and document the issue. Do not quietly fix and rerun as pristine final-holdout evidence. Any corrected analysis must be labeled accordingly and separately authorized. A failure after physical access but before aggregate performance also requires a documented recovery decision, not an automatic restart.

## 16. 2025–26 access prohibition
2025–26 remains physically untouched. Normal commands and the Stage 5 capability continue to reject its schedule, identities, features, outcomes, predictions and metrics before data access. Stage 5A creates protocol/config/schema and verification only, with no final-holdout executor or generic force flag. The protocol document's filename refers to the season; reading this fixed documentation artifact is not accessing season data. The old data guard is preserved unchanged.

## 17. Stage 6 execution procedure
Only after separate explicit Stage 6 authorization: verify this final freeze, all prior artifacts, saved estimators, exact metric source and dependencies; implement and preflight a narrowly scoped one-time executor and the frozen bootstrap specification on synthetic inputs; create the authorization ledger before any final-season access; acquire/validate the authorized season without recipe changes; generate the whole season's frozen predictions with pregame chronology; persist all aggregate metrics, primary deltas, descriptive date-clustered intervals and calibration; then optionally perform labeled descriptive error analysis. Preserve all seven candidates and separate season roles. Any replay must reproduce the already-opened frozen results and must not be counted as independent confirmation.

Stage 5A does not execute any of these Stage 6 actions. The next step is review and an explicit authorization decision. No commit or push is part of this stage.
