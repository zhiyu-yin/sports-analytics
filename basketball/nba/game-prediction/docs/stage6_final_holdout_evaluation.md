# Stage 6 — Final holdout evaluation

Status: **STOPPED**

Stop reason: RuntimeError: Development network blocked during TLS socket construction. The SSL socket class inherited the startup BlockedSocket class; replacing socket.socket only inside the request did not change that inherited base. This is an executor transport integration defect, not an NBA data-integrity failure. The mocked API preflight did not exercise real TLS construction. No response body or HTTP status was returned, and no outcome decode or final performance exposure occurred.

## 1. Scientific hypothesis

Does frozen Model C retain lower log loss and Brier score than raw Elo? Both deltas must be negative.

## 2. Explicit final authorization

The exact user authorization is preserved in stage6_evidence/authorization.txt.

## 3. Frozen confirmatory model

Stage 3 features_plus_elo_logistic: exactly 32 basketball features plus elo_logit; C=.01, L2, lbfgs, max_iter=5000, tol=1e-4, seed=0; saved training-fitted median imputation with indicators and StandardScaler.

## 4. Frozen benchmark

Raw Elo: initial1500, scale400, K20, H50, alpha.50; pregame predictions followed by binary-result updates.

## 5. Frozen training policy

Saved statistical estimators trained only on 2015–16 through 2022–23. Zero refits, tuning or model changes. Frozen Elo state may evolve through completed later seasons.

## 6. Pre-opening verification

Exact Stage 5A freeze, recipes, feature lists, metric/calibration source, dependencies, estimator hashes, historical code and all 275 protected artifacts verified before access. See preopening_verification.json.

## 7. Opening ledger

The durable schema-compatible final_opening_ledger.json precedes the physical access call. First access and first outcome decode are separate events; null means not reached.

## 8. Final-season acquisition and validation

The sole acquisition attempt began at 2026-09-24T20:22:51.077353+00:00. It failed during TLS construction before receiving an NBA response. See acquisition_failure.json and execution_stop.json. Zero final games were validated in this run; the actual season game count, date range, teams and structural completeness remain unknown. No validation.json or raw response was produced. Full season is required; no subset was scored.

## 9. Final prediction protocol

Unchanged canonical ingestion requires score/WL decode before structural validation and rolling features. The first decode boundary is recorded honestly. No individual prediction errors are inspected.

## 10. All seven candidate metrics

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 11. PRIMARY Model C vs Elo result

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 12. Three-season directional replication

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 13. Paired loss differences

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 14. Date-clustered bootstrap intervals

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 15. Calibration

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 16. Tests / preflight

158 tests passed before the attempt: 138 unchanged development tests and 20 Stage 6 synthetic preflight tests. Zero failures/errors. These tests establish the tested contracts, but did not establish real TLS compatibility; the acquisition failed despite passing preflight.

## 17. Reproducibility

No real replay was performed because acquisition did not complete. Synthetic output persistence was byte-identical across two runs. That is infrastructure testing, not final-season evidence. replay_verification.json explicitly records not performed.

## 18. Interpretation

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 19. Limitations

Calendar-date clustering does not remove across-date/team dependence. Calibration is bin-dependent. Historical source revision and pregame availability limitations persist.

## 20. Final status of confirmatory hypothesis

Not available: final evaluation did not complete. No replication or model-ranking claim can be made.

## 21. What can no longer be claimed/changed

After the recorded physical access attempt this run must not be described as never accessed. No silent restart, tuning, refit, recalibration or recipe change is allowed.

## 22. Recommended post-holdout analysis

Before any further access, obtain an explicit documented recovery decision for this failed attempt. The concrete proposed recovery is a narrowly scoped TLS-compatible transport exception, an offline TLS-construction regression test, a versioned executor checkpoint, and a new recovery ledger linked to the preserved original ledger. No retry, fix or recovery execution was performed. After a successful final evaluation, separately labeled descriptive analysis may examine temporal drift, calibration-bin stability and team dependence without changing this confirmatory experiment.

## Completion inventory

Completed: prior-state audit, exact freeze verification, authorization, additive executor, 158 passing pre-access tests, durable ledger, preserved failed acquisition and final integrity verification. Partial: executor transport and acquisition. Not started: real feature generation, predictions, scoring, bootstrap, calibration and deterministic final replay. See completion_status.json. No final metrics CSVs or prediction artifacts were fabricated.

All 275 historical scientific artifacts and 15 additional Stage 5A artifacts remain unchanged. Executor code is byte-identical to the pre-access checkpoint. No tuning, statistical refit, feature/model change, commit or push occurred. Git status/diff were unavailable because this project directory is not a Git repository.
