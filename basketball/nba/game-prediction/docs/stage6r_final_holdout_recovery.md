# Stage 6R — Final holdout recovery

**Part A PASS; transport recovery PASS; final evaluation STOPPED on structural validation**

## 1. Original Stage 6 stop

The original attempt at 2026-09-24T20:22:51.077353+00:00 failed during TLS construction. Its report, authorization, ledger, timestamps, tracebacks and executor remain byte-identical. This recovery is a second physical-access attempt, not the first.

## 2. Why no final performance was exposed

The original attempt received no HTTP response or body, decoded no final outcomes, and created no final predictions or metrics. Stage 6R did receive and structurally decode final outcomes, but stopped before model scoring. No final model ranking or individual prediction errors were exposed.

## 3. Explicit recovery authorization

The exact Stage 6R request is preserved in authorization.txt (SHA-256 8337cbd0b269ad28750d1c04fbdfb9f5304a613c514fd0e840613cbc0f5e2a2c). It authorizes transport-only repair, independent TLS proof, and one conditional recovery execution. It explicitly requires stopping on an integrity anomaly and prohibits silent repair or subset scoring.

## 4. TLS root cause

The startup .pth imports nba_game_prediction and replaces socket.socket with BlockedSocket before SSL initialization. ssl.SSLSocket then inherits BlockedSocket. The Stage 6 request-local rebinding of socket.socket leaves that MRO unchanged. A network-free reproduction confirms that SSL construction still raises with and without the local rebinding. tls_root_cause.json records class identities and inheritance.

## 5. Transport-only fix

A dedicated -I -S child imports SSL/socket before loading the unchanged project guard. It grants a single-use, authorization-bound capability only during acquisition. Part B permits exactly the maintained NBA LeagueGameLog endpoint and frozen parameters, with no redirects/proxies/retries, domain-restricted DNS and audited resolved-IP port-443 connections. The block is restored at revocation and the child exits. Ordinary development remains blocked. All recovery code is additive; no historical/scientific code changed. See transport_recovery_design.md and recovery_code_manifest.json.

## 6. Part A TLS preflight

PASS: 169 tests = 138 existing development + 20 Stage 6 synthetic + 11 transport regression tests, zero failures/errors/skips. A local HTTPS server completed real DNS/socket/TLS/HTTP with certificate verification. Tests reject missing, wrong and consumed capabilities, Part B without its gate/ledger, and NBA access in Part A; prove no stale SSL inheritance and fail-closed revocation. No final-season data were accessed during Part A.

## 7. Scientific freeze regression

The exact Stage 5A freeze, seven candidates, Model C C=.01 and 33-input allowlist, frozen Elo K20/H50/alpha.50, original 2015–16..2022–23 training, saved estimators, frozen metric/calibration source and date-cluster bootstrap are unchanged. The saved estimators reproduced all seven probability vectors and all reported metrics exactly for both 2023–24 and 2024–25 (1,230 games each), with zero fits and unchanged estimator state. All 313 snapshotted files remain unchanged.

## 8. Recovery ledger

recovery_opening_ledger.json links hashes for original authorization/ledger/acquisition failure/execution stop and new authorization/checkpoint/Part A gate. original_attempt_status=stopped_before_response; recovery_reason=TLS transport integration defect; scientific_protocol_changed=false; model_recipe_changed=false; final_outcome_previously_decoded=false; final_performance_previously_exposed=false. The worker durably recorded access immediately before its NBA call.

Access: 2026-09-24T20:49:56.599524+00:00

Response: 2026-09-24T20:49:56.815677+00:00

First outcome decode: 2026-09-24T20:49:56.949550+00:00

Aggregate persistence: not reached.

## 9. Final-season acquisition

Transport succeeded: HTTP 200, nba_api 1.11.4, LeagueGameLog NBA team Regular Season 2025–26. Raw text was preserved before transformation: 391,239 UTF-8 bytes, SHA-256 c82453a22995e14a8b0b4a2c49a566e8463dc4ce30561f66111067652f901651. response_schema.json records 29 source columns and 2,460 rows, linked to the recovery checkpoint. Only one recovery request occurred; later work used the cached response. The capability was revoked successfully.

## 10. Season validation

Observed 2,460 team-game rows, 1,230 unique games, 30 teams, 82 games per team, dates 2025-10-21 through 2026-04-12. No normalized field missingness. The unchanged validator accepted 1,225 games and rejected five solely for not_one_home_and_one_away: both rows use @. No complete-season validation pass is claimed. The 1,225-game subset was not scored.

| Game ID | Date | Source matchups |
| --- | --- | --- |
| 0022500147 | 2025-11-01 | DAL @ DET / DET @ DAL |
| 0022500578 | 2026-01-15 | ORL @ MEM / MEM @ ORL |
| 0022500602 | 2026-01-18 | ORL @ MEM / MEM @ ORL |
| 0022501229 | 2025-12-13 | NYK @ ORL / ORL @ NYK |
| 0022501230 | 2025-12-13 | SAS @ OKC / OKC @ SAS |

No designated-home team was inferred. These may involve special-site scheduling, but venue status and official designations were not established by this request. structural_review_cases.json omits scores and winners; structural_anomalies.csv retains the original diagnostic provenance.

## 11. Frozen prediction protocol

Not executed on the final season. The unchanged executor would build exactly 32 season-reset pregame features, check prefix invariance, load saved estimators, and advance frozen Elo state chronologically with prediction before result update. Structural score/WL decoding necessarily preceded validation and was honestly timestamped. No new predictor, neutral-site feature or refit was introduced.

## 12. Seven candidate metrics

Unavailable for all seven frozen candidates: constant_home_prior, raw_elo, basketball_features_logistic, elo_logistic, features_plus_elo_logistic, basketball_features_hgb, features_plus_elo_hgb. No final predictions or metrics artifacts were fabricated. n_games scored is zero for this execution; this is not an estimate of the season size.

## 13. Primary Model C vs Elo comparison

Final delta log loss, delta Brier, delta accuracy and delta ROC-AUC are unavailable because full-season validation failed before scoring.

## 14. Directional replication result

NOT EVALUATED. This is neither replicated, mixed nor not replicated. Those labels require valid final predictions and both primary loss deltas.

## 15. Date-cluster bootstrap

Not executed. The unchanged specification remains 10,000 paired calendar-date cluster replicates, seed 0, default_rng(0), game-weighted means, shared date draws, ddof=1 SE and linear 2.5%/97.5% quantiles. No final intervals or zero-inclusion statements exist. Synthetic reference checks passed; no p-values or method changes.

## 16. Calibration

Not executed on final data. No final ECE, mean probability, bin counts or model rankings are available. The frozen ten-bin implementation remains unchanged, and no calibrator was fitted.

## 17. Three-season confirmation

Previously observed evidence remains distinct from the unevaluated final season. No pooling. cross_season_confirmation.csv contains exact historical values and blank final metrics with explicit stopped status.

```csv
split,status,raw_elo_log_loss,model_c_log_loss,delta_log_loss,raw_elo_brier,model_c_brier,delta_brier,raw_elo_accuracy,model_c_accuracy,delta_accuracy,raw_elo_auc,model_c_auc,delta_auc
2023-24 development validation,previously evaluated,0.6155777658316821,0.6101129191413501,-0.0054648466903319814,0.21410659526134396,0.21136308493395012,-0.002743510327393839,0.6495934959349593,0.6422764227642277,-0.007317073170731603,0.71141613570013,0.721586187056492,0.010170051356362064
2024-25 pre-holdout,previously evaluated,0.6144999514315425,0.6059984019404454,-0.008501549491097049,0.2133222404089072,0.20939322874883826,-0.003929011660068954,0.6609756097560976,0.6682926829268293,0.007317073170731714,0.7167986912117749,0.7286182851996621,0.011819593987887234
2025-26 final holdout,not evaluated: five unresolved home/away pairs,,,,,,,,,,,,
```

## 18. Reproducibility

Final-data replay was not performed because no complete evaluation exists. replay_verification.json records not performed and independent_confirmation=false. Historical prediction/metric reproduction and synthetic deterministic persistence passed; neither is a final-holdout test.

## 19. Limitations

The source count and per-team coverage pass, but five designated-home ambiguities block the canonical target/feature/Elo contract. MATCHUP alone cannot establish their official home designation. The TLS fix is an application-level capability, not an OS defense against deliberate policy bypass. Final outcomes are now structurally decoded and cannot again be called untouched; final performance remains unexposed.

## 20. Recovery status

Part A PASS; transport recovery PASS; final evaluation STOPPED on structural validation. Original failed Stage 6 evidence preserved; no fits, tuning, feature/model changes, recalibration, individual-error inspection, commits or pushes. See completion_status.json and final_verification.json. Required evaluation-only CSVs/parquet were intentionally not generated without a valid whole-season dataset.

## 21. Post-holdout next steps

Review the five both-away cases before further work. Proposed next scope: separately authorize an authoritative NBA schedule/designation lookup for these exact game IDs, preserve its raw provenance, and propose an explicit reconciliation table under the existing Stage 1D philosophy. Do not infer home status from winners, scores or model performance; do not add a neutral-site predictor. If approved and all five identities reconcile without other changes, a separately documented continuation can validate all 1,230 cached games before any scoring. No additional NBA lookup, correction or evaluation was performed in Stage 6R. This stop follows the user’s Stage 6R sections 10 and 12.
