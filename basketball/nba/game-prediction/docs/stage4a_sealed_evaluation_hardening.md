# Stage 4A — Sealed evaluation hardening

## 1. Objective
Infrastructure-only hardening: normal development tests and supported project commands must not decode real 2024–25 outcomes or access any 2025–26 data. No models were trained, replayed, selected, predicted or evaluated. No new 2023–24 metrics were calculated. Existing Stage 2–4 scientific results and artifacts remain frozen.

## 2. Stage 4 strict-exit issue
Stage 4 completed its modeling comparison, but its legacy structural test suite reread cached real 2024–25 scores/WL. This prevented an unqualified strict pass. Stage 4A changes current development access policy; it does not erase or reinterpret the historical access. Frozen Stage 3 `features_plus_elo_logistic` remains the leading candidate on previously recorded development evidence.

## 3. Exact legacy accesses discovered
The preimplementation `stage4a_evidence/sealed_access_audit.csv` records the source audit, with two subsequently added entry-point rows. Primary violations were `tests/test_reconciliation.py::setUpClass` (raw real 2024–25 cache retrieval, normalization, pairing and feature history), all tests sharing that class fixture, and `test_H_no_earlier_season_regression` (whole combined outcome table loaded before removing sealed rows). `test_J_neutral_context_not_feature` made a broad context read; it needed metadata only.

Other routes: `ingest.read_cache/retrieve`, `multiseason.acquire/build_season_games/build_multi`, `stage1d.build`, and the historical multi-season/reconciliation build scripts admitted sealed input under the old structural scope. `feature_io.load_inputs` used anonymous byte buffers, losing source identity at the decoder boundary, although its actual files were 2023–24. The old quarantine test broadly read an outcome-free feature snapshot. Existing modeling loaders used projected targets and positive season filters, but mixed Parquet row groups still warranted stronger isolation. The single-season build and legacy network-check script were also audited and hardened. No real sealed labels were opened during this audit.

## 4. Why those accesses were not model leakage
The historical Stage 1D tests exercised source preservation, pairing and rolling-history integrity; no 2024–25 model predictions, metrics, calibration, selection or fitting were produced. Nevertheless, reading real outcomes violated the later strict development contract. This distinction is documented rather than used to excuse the violation. All Stage 1D historical documents, evidence, manifests and reports remain byte-identical.

## 5. New sealed-data contract
`sealed_data_policy.json` was written before implementation. 2015–16 through 2023–24 are open historical data; 2024–25 outcomes are sealed; 2025–26 is forbidden entirely. Outcome values include winners, scores, W/L, box scores, margins and embedded observed payloads. Outcome-free identity/context access requires an explicit allowlist. Unknown columns, broad sealed reads, outcome-based filters, anonymous decoder sources and unsupported requests fail before decoding. There is no force flag.

Opaque SHA-256 streaming is allowed for integrity and returns only a digest, never decoded values or bytes to callers. This is distinct from an outcome read. Registered data hashes are checked before decoder access. A change in protected input content stops access.

## 6. Test refactoring
The 14 reconciliation tests now operate on synthetic data. Existing ingestion, feature and multi-season structural tests remain in normal discovery; the quarantine check now projects only season and inspects schema metadata separately. Five historical model-execution test modules (95 tests) are preserved byte-for-byte under `tests_archived/model_execution/`, outside ordinary discovery. This includes synthetic model fits and real benchmark metric recalculation, neither of which is permitted in infrastructure-only Stage 4A. They were not executed. The original real-data reconciliation module is also preserved verbatim under `tests_archived/historical_real_data/`; its logic is covered by current synthetic replacements.

Normal discovery has no skipped tests and does not silently omit tests at runtime. The archived categories and their restrictions are explicit in `tests_archived/README.md`. No historical reproduction escape hatch is provided.

## 7. Synthetic fixture strategy
The new history has 12 invented games, fake teams 9000001/9000002, abbreviations AAA/BBB, synthetic source provenance and generated scores/WL. One pair is deliberately `AAA @ BBB` / `BBB @ AAA`; a synthetic approved neutral-site mapping designates BBB home. A test-local registry contains only the fake teams. Game IDs follow parser syntax but use a clearly synthetic high sequence, and no real results populate the fixture.

Tests prove explicit-only application, reciprocal pairing, unchanged input, only `is_home` changing, preserved raw matchup and synthetic scores/WL, retained neutral flag, conflicts/duplicates/date mismatches/unrelated errors failing, complete subsequent rolling history and future reconciliation invariance. Production numerical feature definitions and reconciliation rules are unchanged.

## 8. Outcome-loader guard
`sealed_access.load_outcomes(seasons, purpose, columns)` rejects sealed/forbidden seasons before file construction, cache access or pandas reads. Permitted targets are read from separate existing open-season files with explicit columns. Mixed outcome containers are metadata-only even with positive season filters: this avoids relying on predicate pushdown to avoid decoding sealed row groups.

The shared policy also wraps pandas and supported Arrow readers, ordinary built-in/file/pathlib reads, and raw ingestion. Direct Arrow dataset/ParquetFile construction on protected containers is denied because later reads could ignore projection. Historical Stage 1D and sealed multi-season rebuilds stop before processing/writing. Model entry points and sklearn fit/predict methods are disabled for this infrastructure stage without changing saved recipes or results.

## 9. Column-projection policy
Allowed sealed metadata is enumerated in the policy and code: season/type, game/date/team identities, designation/matchup and approved neutral/venue context. Scores, W/L, observed payloads and derived feature values cannot enter a sealed identity request. Filters themselves cannot reference outcome fields or request 2025–26. Broad mixed reads fail closed. Feature reads for open seasons require explicit positive season bounds; target reads use physically separate open files.

Known project sources are checked against the frozen input registry before decoding. Existing modeling loaders now call the reusable outcome boundary. Historical integrity checks may read only identity columns from combined outcome files. The access evidence records paths, projected columns and filters, never returned game values.

## 10. Access-spy results
Both verification runs use the guard from process startup, recording every admitted registered-table decoder request and every denial. The runner independently rejects any recorded sealed/mixed-container read whose columns exceed the metadata allowlist. Final evidence records zero admitted sealed-outcome reads and zero admitted holdout reads. Adversarial tests intentionally attempt prohibited requests and prove that underlying decoder/cache mocks are never reached; blocked attempts are expected, not successful reads.

The probes caught and fixed Python 3.10's cached `pathlib.Path.open` accessor, which otherwise bypassed an `io.open` replacement. Network socket creation is blocked. Ordinary Python startup in the project virtualenv uses `sports_analytics_development_policy.pth`; package import and the first discovery module provide additional activation. No model fit or performance evaluation ran; deliberate rejection probes stop at the guard.

## 11. Protected model-artifact verification
All 210 snapshotted data/historical evidence/model-output files are byte-identical before and after Stage 4A. Protection includes Stage 1D history; Stage 2 selected Elo/constant recipe, validation predictions and metrics; Stage 3 selected parameters, predictions, metrics and coefficients; Stage 4 selected HGB parameters, predictions and metrics; calibration/figure evidence and raw data. Any mismatch stops verification.

Code and current tests necessarily changed for hardening. Their before hashes, archived original modules, and current hashes are recorded separately. Historical manifests retain their original code hashes and are not rewritten to certify current code. Old model runners are intentionally disabled; a future authorized executor must use the Stage 4A provenance checkpoint and an explicitly revised execution boundary, not bypass historical hash failures.

## 12. Candidate freeze
`candidate_freeze.json` freezes exactly: constant_home_prior, raw_elo, basketball_features_logistic, elo_logistic, features_plus_elo_logistic, basketball_features_hgb and features_plus_elo_hgb. It records selected recipes, feature allowlists, missingness mechanisms, frozen Elo, original estimator training seasons and artifact hashes. `features_plus_elo_logistic` remains the current leading candidate; no unknown future performance is ranked. Any candidate/recipe/feature expansion invalidates the planned pre-holdout protocol and requires a new explicit decision and freeze.

## 13. Draft pre-holdout protocol
`preholdout_protocol_2024_25_draft.md` is clearly marked **NOT YET EXECUTED**. It proposes one separately authorized opening for all seven frozen candidates, with Model C versus raw Elo primary, log loss/Brier primary metrics, and accuracy/AUC/calibration secondary. No tuning, feature changes or family additions after opening. If fitted objects need reconstruction, that must use the original frozen training history before label opening. 2025–26 remains untouched. No opening executor or override has been enabled in this stage.

## 14. Test results
**102 normal development tests pass, zero failures/errors/skips.** This consists of 71 structural tests (including 14 synthetic reconciliation replacements), one startup-policy test and 30 access/freeze/infrastructure tests. The 95 archived model-execution tests are preserved but were not rerun; this is not a claim that all 166 historical tests executed in Stage 4A.

Run from the subproject:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/run_stage4a_verification.py
```

The first is the ordinary requested command. The second adds deterministic evidence, before/after protected hashes and an access audit. Both activate network/sealed-data/no-model guards. New checks cover loader rejection before physical reads, projection, broad reads, direct Arrow, outcome filters, positive-season predicates, raw/pathlib/built-in access, holdout, historical-build rejection, no model execution, frozen artifacts and candidate freeze.

## 15. Reproducibility
Two fresh-process Stage 4A verifications match in test identities/results, candidate freeze, access audit, protected hashes, draft protocol and build manifest. Runtime alone is omitted from deterministic test logs; no failures or test output are suppressed. Library/Python versions and current code hashes are recorded. The original interruption left only the contract/audit/hash snapshots; all 40 original source/test/script files and 210 artifacts matched on resume. This folder has no Git repository, so status/diff were unavailable; before/current hashes provide the change record. No commit or push occurred.

## 16. Remaining limitations
This guard prevents accidental access through the audited Python loaders, supported dataframe/Arrow APIs and normal project commands; it is not an OS sandbox against deliberate bypass, another interpreter, `-S`, native libraries or copied/renamed files. The project virtualenv startup file must be installed again if the environment is recreated. Current model execution is intentionally disabled; future authorization requires an explicit implementation/provenance change. Stage 1D and Stage 4 historical label access cannot be undone. Hardening establishes current-development isolation, not a claim that 2024–25 labels have never been processed. Checksums establish unchanged artifacts, not source correctness or external scientific validity.

## 17. Stage 4A exit criteria
PASS: normal guarded development tests decode no real sealed outcomes; 2024–25 performance remains unopened; 2025–26 is untouched; synthetic reconciliation/history checks pass; guards run before decoder/cache access; identity reads use explicit allowlists; Stage 1D history and Stage 2–4 outputs are unchanged; candidate set is formally frozen; the unexecuted draft exists; no model fitting, tuning, prediction or evaluation occurred. All required evidence is in `docs/stage4a_evidence/`.

## 18. Recommended next step
Review Stage 4A and decide whether to separately authorize the one-time 2024–25 opening. The frozen candidate/protocol checkpoint is ready for that decision. Do not open automatically. Any authorized execution must implement the narrow one-time boundary described in the draft, preserve its opening ledger and continue to prohibit all 2025–26 access.
