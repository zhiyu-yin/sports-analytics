# Stage 6R2 — Final holdout completion

**Execution PASS. Directional replication: REPLICATED.**

## 1. Stage 6 original TLS stop

The initial Stage 6 attempt failed during SSL socket construction before receiving an NBA response, decoding a final outcome or producing any final prediction/metric. The original report, ledger, failure trace, code and timestamps remain unchanged.

## 2. Stage 6R transport success

Stage 6R repaired the transport using an isolated SSL-before-policy subprocess. Its one LeagueGameLog request returned HTTP 200 at 2026-09-24T20:49:56.815677+00:00. The unchanged raw snapshot contains 2,460 team-game rows and 1,230 games. SHA-256: `c82453a22995e14a8b0b4a2c49a566e8463dc4ce30561f66111067652f901651`.

## 3. Stage 6R structural-validation stop

The validator accepted 1,225 games and rejected exactly five with two away-style MATCHUP labels. It stopped before final features or model scoring. The original anomaly artifacts, recovery ledger, source-access/response/outcome-decode timestamps and stopped report remain intact. Source outcomes were already structurally decoded; final model performance was still unexposed.

## 4. Stage 6R2 authorization

The exact request is preserved in `stage6r2_evidence/authorization.txt`, SHA-256 `37c3d5e554cb9fe0d246d8651497e5105dfe04320a4d3046f6de33266945a00e`. It authorizes only authoritative reconciliation of the five IDs and conditional completion of the unchanged scientific protocol. This is a documented continuation, not the first physical access to the season. No training, tuning, model/feature change, recalibration, commit or push was authorized or performed.

## 5. Five anomaly cases

| game_id | date | raw_MATCHUP | home | away | venue | city | neutral |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0022500147 | 2025-11-01 | DAL @ DET / DET @ DAL | DET | DAL | Arena CDMX | Mexico City | True |
| 0022500578 | 2026-01-15 | ORL @ MEM / MEM @ ORL | ORL | MEM | Uber Arena | Berlin | True |
| 0022500602 | 2026-01-18 | ORL @ MEM / MEM @ ORL | MEM | ORL | The O2 Arena | London | True |
| 0022501229 | 2025-12-13 | NYK @ ORL / ORL @ NYK | ORL | NYK | T-Mobile Arena | Las Vegas | True |
| 0022501230 | 2025-12-13 | SAS @ OKC / OKC @ SAS | OKC | SAS | T-Mobile Arena | Las Vegas | True |

Raw row order is retained only for traceability. No designation is inferred from row order, game ID, abbreviation order, venue likelihood, score or winner.

## 6. Official designation evidence

The maintained nba_api 1.11.4 [NBA ScheduleLeagueV2 source](https://stats.nba.com/stats/scheduleleaguev2?LeagueID=00&Season=2025-26) returned explicit homeTeam/awayTeam identities for each exact game ID. Retrieval UTC: 2026-09-24T20:59:20.823884+00:00. Parameters: LeagueID=00, Season=2025-26. Original response-text SHA-256: `ba9324d0ed5633b2d655d3937e375f3fe0919f778ee4d00670f27d3a2ab53b4e`. Retained factual-extract SHA-256: `ef78491eca2879483a084e39225e717139a443ecc735a965472fad2dbf7fd3ba`.

Each record independently matches both raw team IDs, tricodes and date; explicit home/away fields agree with the official gameCode. All five mappings are authoritative, with no missing or conflicting designation in the inspected source. No search snippets were used.

The endpoint has only season-level parameters, so its 4,435,106-byte JSON response was received transiently. Only the five records’ gameId, gameDate, gameDateEst, gameCode, home/away team ID/tricode, arenaName, arenaCity and isNeutral were retained in official_schedule_facts.json. Scores, records, standings, winners and unrelated game fields were not selected or used for mapping. The manifest distinguishes full-response checksum from selected-fact checksum.

## 7. Reconciliation table

Separate artifacts: `data/interim/home_away_reconciliation_2025_26.parquet` and `docs/stage6r2_evidence/home_away_reconciliation_2025_26.csv`. Every row includes the original two team IDs/MATCHUP strings, official sides, neutral/venue context, source URL, retrieval time, checksum, authoritative confidence and reason.

The Stage 1D application function is reused with only its fixed season literal changed to 2025–26. Normal validation runs before reconciliation, the exact five home/away-only anomalies are required, a copied normalized frame receives changes only to is_home, and unchanged full validation runs afterward. Exact frame comparisons prove all other columns—including MATCHUP, _observed, scores and W/L—unchanged. Unknown IDs, conflicting evidence, duplicate mappings and unrelated errors fail closed. The generic parser was not changed.

## 8. Neutral-site findings

**Observed:** NBA explicitly marks all five inspected games isNeutral=true, with Mexico City, Berlin, London and Las Vegas venue metadata shown above.

**Inference:** both-away formatting appears associated with these neutral-site games in this snapshot, consistent with the earlier season’s observed pattern. This does not establish the provider’s cause or a generic rule. Only the five requested IDs were retained; this work does not establish a complete neutral-site inventory. Neutral status remains context, never a V1 predictor or an Elo adjustment.

## 9. Complete final-season validation

PASS: 2,460 accepted team rows, 1,230 unique accepted games, 30 registered teams, 82 games per team, 2025-10-21 through 2026-04-12, zero rejected games and zero warnings. Counts agree with the preserved source; no rows were manufactured or dropped to force coverage.

The unchanged checks cover unique team-game keys, exactly two distinct teams, one designated home/away, reciprocal opponents, same dates, complementary W/L, score validity, scoring arithmetic, rebound totals, existing plus-minus policy and season/game-ID scope. Reconciliation restores the full season rather than scoring the prior 1,225-game subset.

## 10. Frozen feature generation

PASS: 1,230 pregame vectors with exactly 32 basketball features, V1 version 1.0.0. Season history resets; NaN warmup is retained for the frozen model preprocessing. Prefix recomputation is exactly invariant. Flipping internally consistent last-date results leaves every pregame vector unchanged, including the changed games. No neutral-site, availability, injury, odds, travel or new rolling/rest input is added. Frozen elo_logit is appended only for the existing recipes.

## 11. Scientific freeze verification

The exact Stage 5A protocol/freeze, all seven recipes, ordered feature lists, preprocessing, saved-estimator hash, metric/calibration source, uncertainty protocol, dependency versions and historical code verify unchanged immediately before scoring. Model C remains C=.01, L2, lbfgs, max_iter5000, tol1e-4, seed0 with training-fitted median imputation plus indicators and StandardScaler.

Statistical training remains 2015–16 through 2022–23 only. Saved A/B/C/D/E estimators are loaded, never fitted; their state is asserted identical before/after each prediction pass. Elo remains initial1500, scale400, K20, H50, alpha.50, with completed-game chronological state through 2023–24 and 2024–25 and then pregame prediction before each final-season update. No margin or neutral-site adjustment. All 360 protected files remain unchanged.

## 12. Continuation ledger

`final_evaluation_continuation_ledger.json` links the original Stage 6 authorization/TLS stop, Stage 6R authorization/recovery ledger/retrieval/structural stop, new authorization, official source/facts, reconciliation, feature and test evidence. It records final_performance_previously_exposed=false, scientific_protocol_changed=false, model_recipe_changed=false and final_source_outcomes_already_structurally_decoded=true.

Ledger created: 2026-09-24T21:06:41.222816+00:00

First final model-scoring boundary, immediately before unchanged Elo replay: 2026-09-24T21:06:41.511097+00:00

All aggregate outputs durably persisted: 2026-09-24T21:06:41.754631+00:00

Completed after exact replay: 2026-09-24T21:06:48.749812+00:00. No individual prediction error analysis was performed.

## 13. Seven candidate metrics

| model | n_games | log_loss | brier_score | accuracy | roc_auc |
| --- | --- | --- | --- | --- | --- |
| constant_home_prior | 1230 | 0.687769 | 0.247312 | 0.554472 | 0.500000 |
| raw_elo | 1230 | 0.604644 | 0.208328 | 0.674797 | 0.730759 |
| basketball_features_logistic | 1230 | 0.613116 | 0.212169 | 0.666667 | 0.718899 |
| elo_logistic | 1230 | 0.605077 | 0.208519 | 0.683740 | 0.730759 |
| features_plus_elo_logistic | 1230 | 0.601923 | 0.207053 | 0.676423 | 0.731559 |
| basketball_features_hgb | 1230 | 0.606716 | 0.209259 | 0.679675 | 0.727900 |
| features_plus_elo_hgb | 1230 | 0.605318 | 0.208655 | 0.678049 | 0.729457 |

All seven cover exactly the same 1,230-game set. Model C has the lowest final log loss and Brier score among these frozen candidates. That ranking is descriptive; Model C was already the confirmatory candidate.

## 14. Primary Model C vs Elo result

| comparison | delta_log_loss | delta_brier | delta_accuracy | delta_roc_auc | directional_replication_status |
| --- | --- | --- | --- | --- | --- |
| features_plus_elo_logistic vs raw_elo | -0.002721 | -0.001274 | 0.001626 | 0.000800 | replicated |

Negative deltas favor Model C on both primary losses. Accuracy and AUC improvements are secondary and do not determine the confirmatory direction.

## 15. Directional replication

**REPLICATED:** delta log loss = −0.002720808358490867 and delta Brier = −0.0012742071699871071, both negative under the predeclared rule. No magnitude threshold or significance rule was added. The final improvement is smaller than the previously observed validation/pre-holdout differences, without changing the interpretation rule.

## 16. Date-cluster bootstrap

| metric | observed_mean_difference | median_difference | q25_difference | q75_difference | bootstrap_mean | bootstrap_standard_error | ci_lower_2_5 | ci_upper_97_5 | includes_zero |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| log_loss | -0.002720808 | -0.011956671 | -0.075453875 | 0.060697147 | -0.002710102 | 0.003660226 | -0.009862573 | 0.004315241 | True |
| brier_score | -0.001274207 | -0.004363585 | -0.031971090 | 0.027230397 | -0.001273591 | 0.001593054 | -0.004441080 | 0.001792523 | True |

**Date-clustered descriptive bootstrap intervals:** 1,230 paired games across 164 calendar dates, 10,000 replicates, seed0, numpy.random.default_rng(0)/PCG64, whole-date clusters, shared draws for both metrics and game-weighted means. SE uses ddof=1; interval and per-game quartiles use linear quantiles. Both 95% descriptive intervals include zero. No p-values or definitive statistical-significance claim. Date clustering does not eliminate team or across-date dependence. Small machine-precision differences between the average paired loss and subtraction of separately averaged losses reflect floating-point reduction order.

## 17. Calibration

| model | fixed_bin_ece | populated_bins | bins_below_30 | mean_predicted_probability | observed_designated_home_win_rate |
| --- | --- | --- | --- | --- | --- |
| raw_elo | 0.026942 | 9 | 2 | 0.565775 | 0.554472 |
| features_plus_elo_logistic | 0.028290 | 10 | 2 | 0.557949 | 0.554472 |

| bin | raw_elo_count | model_c_count |
| --- | --- | --- |
| [0.0,0.1) | 0 | 1 |
| [0.1,0.2) | 14 | 32 |
| [0.2,0.3) | 65 | 101 |
| [0.3,0.4) | 141 | 129 |
| [0.4,0.5) | 226 | 197 |
| [0.5,0.6) | 226 | 218 |
| [0.6,0.7) | 270 | 248 |
| [0.7,0.8) | 190 | 183 |
| [0.8,0.9) | 93 | 107 |
| [0.9,1.0] | 5 | 14 |

Raw Elo has slightly lower fixed-bin ECE (0.026942 vs Model C 0.028290). Model C’s mean probability (0.557949) is closer to the observed designated-home win rate (0.554472) than Elo’s (0.565775). C therefore has smaller aggregate mean bias, but not uniformly better calibration. Elo populates nine bins, C ten; each has two populated bins below 30 games. Empty bins are retained; sparse tails are noisy and ECE is bin-dependent. No recalibration.

All seven descriptive calibration summaries:

| model | fixed_bin_ece | populated_bins | bins_below_30 | mean_predicted_probability | observed_designated_home_win_rate |
| --- | --- | --- | --- | --- | --- |
| constant_home_prior | 0.016702 | 1 | 0 | 0.571173 | 0.554472 |
| raw_elo | 0.026942 | 9 | 2 | 0.565775 | 0.554472 |
| basketball_features_logistic | 0.030462 | 10 | 3 | 0.558044 | 0.554472 |
| elo_logistic | 0.035034 | 9 | 2 | 0.573074 | 0.554472 |
| features_plus_elo_logistic | 0.028290 | 10 | 2 | 0.557949 | 0.554472 |
| basketball_features_hgb | 0.028096 | 9 | 2 | 0.557630 | 0.554472 |
| features_plus_elo_hgb | 0.034452 | 9 | 2 | 0.557403 | 0.554472 |

## 18. Three-season confirmation

| split | raw_elo_log_loss | model_c_log_loss | delta_log_loss | raw_elo_brier | model_c_brier | delta_brier | raw_elo_accuracy | model_c_accuracy | raw_elo_auc | model_c_auc | delta_accuracy | delta_auc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2023-24 development validation | 0.615578 | 0.610113 | -0.005465 | 0.214107 | 0.211363 | -0.002744 | 0.649593 | 0.642276 | 0.711416 | 0.721586 | -0.007317 | 0.010170 |
| 2024-25 pre-holdout | 0.614500 | 0.605998 | -0.008502 | 0.213322 | 0.209393 | -0.003929 | 0.660976 | 0.668293 | 0.716799 | 0.728618 | 0.007317 | 0.011820 |
| 2025-26 final holdout | 0.604644 | 0.601923 | -0.002721 | 0.208328 | 0.207053 | -0.001274 | 0.674797 | 0.676423 | 0.730759 | 0.731559 | 0.001626 | 0.000800 |

The primary direction favors C in each season. 2023–24 is development validation, 2024–25 is previously opened pre-holdout evidence, and 2025–26 is the frozen final performance evaluation completed through documented structural recovery. They are not pooled or represented as one untouched test.

## 19. Tests

**178 tests passed before first final scoring**, zero failures/errors/skips: 138 unchanged development, 20 Stage 6 synthetic and 20 Stage 6R2 tests. They cover requested A–N: exact approved IDs/stored evidence, only canonical designation changes, unchanged MATCHUP/scores/WL, unknown/conflicted rejection, full-season gate, no fits, exact saved estimators, primary deltas, independent frozen bootstrap reference, prior-evidence hashes and ledger-before-scoring. Runtime checks additionally enforce 1,230-game/seven-model coverage, feature invariance, unchanged estimator state, final provenance and exact replay.

The new schedule transport separately passed a real local certificate-verified HTTPS/TLS exchange and duplicate-capability rejection before lookup. The older Stage 6R transport tests/evidence are preserved, not rerun into old files. A pre-scoring synthetic test reference initially differed at ~1e-14 due to a two-column reduction order; only the reference was corrected to per-metric reduction. No production/scientific implementation changed.

## 20. Reproducibility

One deterministic replay used only cached LeagueGameLog bytes, stored official facts, the explicit reconciliation and saved estimators. It made zero network or fit calls and reproduced all 14 prediction/metric/primary-delta/bootstrap/calibration/cross-season artifacts byte-for-byte. The replay is not independent confirmation. No continuation rerun or model change occurred after results became visible. Full predictions with home_win and seven probabilities—but no final scores—are in `data/processed/stage6r2_predictions_2025_26.parquet`.

## 21. Limitations

One final season is limited evidence. Descriptive intervals include zero, and calendar-date clustering does not remove all dependence. Fixed-bin ECE depends on sparse bins. Official schedule metadata shares an NBA publisher with LeagueGameLog; it provides a separate authoritative representation, not an independent organization or a provider root-cause diagnosis. Schedule lookup is retrospective and does not establish original publication timestamps. Source outcomes were structurally decoded before performance evaluation; this cannot be called never-accessed data. The documented frozen recipes remained unchanged throughout, and no individual prediction errors were inspected. Future outcome-informed development must be labeled development; it cannot make this season unseen again.

## 22. Final scientific conclusion

Execution succeeds: all five designations are authoritative, the complete season validates, the frozen seven-candidate evaluation completes with zero fits, all prior artifacts remain unchanged, and deterministic replay is exact.

Model C directionally replicates its lower log loss and Brier score versus frozen raw Elo on 2025–26. Both descriptive bootstrap intervals include zero, so this result is not presented as definitive statistical-significance evidence. C also has the lowest two losses among the seven frozen candidates, descriptively. Its calibration picture is mixed: slightly higher ECE but smaller mean bias.

Keep this confirmatory result and its artifacts frozen. Any later investigation of temporal drift, sparse-bin calibration, team dependence or individual errors should be explicitly labeled post-holdout descriptive analysis, with no claim of a new independent test. No tuning, statistical refit, feature/model change, commit or push occurred.
