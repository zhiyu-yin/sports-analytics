# V1 reproduction and verification

Run commands from `basketball/nba/game-prediction/`. Keep the frozen tree intact.

## Safe current checks

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 stage7/verify_v1.py
```

The existing project virtualenv activates the development policy through `sports_analytics_development_policy.pth`. Ordinary discovery uses synthetic/safe fixtures and does not enable archived model-execution tests. The standalone verifier uses Python's standard library solely to hash files, inspect release Markdown links and compare presentation tables with already-published aggregate CSVs. It does not import project model code, decode raw/Parquet outcomes, load estimators, fit, predict or score. Using a standard interpreter for opaque checksums is an integrity operation, not a holdout-execution escape hatch.

Dependencies are pinned in [requirements.txt](../requirements.txt). A recreated environment also needs the documented [startup policy](stage4a_sealed_evaluation_hardening.md); installing requirements alone does not install that policy. Preserve its source checkpoint in the V1 manifest. Raw caches and derived data are excluded by the umbrella `.gitignore`; they may be absent from a published checkout. Exact source snapshots may need reacquisition, and revised responses will not necessarily match historical hashes. The verifier reports missing files rather than claiming a complete reproduction.

## Cached builds: historical reference only

The original open-season commands were:

```sh
.venv/bin/python scripts/build_2023_24_games.py
.venv/bin/python scripts/build_2023_24_features.py
```

The first defaults to cache-only, but writes Stage 1A outputs/manifests. The second is offline and enforces the historical Stage 1B provenance/requirements gate, which does not match later dependency/code checkpoints automatically. **Do not run either against this frozen release.** Reconstructing a historical build requires a disposable copy, the exact period-specific environment/code/input snapshot and explicit handling of these historical gates; do not weaken them to make current code pass. No cache rebuild is necessary for release verification.

The reconciled multiseason build `scripts/build_reconciled_multiseason.py` additionally includes protected 2024–25 data and is disabled under ordinary development policy. Older Stage 1C builds represent a superseded quarantine state. Their audit documents remain historical evidence, not current runnable instructions.

## Open historical development stages: archived entry points

For traceability, these were the original 2023–24 development commands:

```sh
.venv/bin/python scripts/run_stage2_baselines.py
.venv/bin/python scripts/run_stage3_logistic.py
.venv/bin/python scripts/run_stage4_boosting.py
```

They performed fitting/searches and wrote scientific artifacts at the time. They are intentionally disabled under the current execution boundary, even though 2015–16–2023–24 is open historical data. They are **not supported rerun commands for frozen V1**. A future independently authorized development environment must version its provenance and preserve V1; there is no recommended force flag or policy bypass. This restriction is a reproducibility limitation, not evidence that those runs were reproduced during finalization.

## Final-stage evidence

The one-time pre-holdout/final openings used authorization ledgers, exact recipe/data hashes and controlled infrastructure. Their preparation/opening capabilities are consumed. Keep [Stage 5](stage5_preholdout_evaluation.md) and [Stage 6R2](stage6r2_final_holdout_completion.md) outputs archived; do not rerun their executors or old verification scripts into existing evidence directories. The saved byte-identical replay is already the deterministic reproduction record. No final-stage or archived model tests are enabled by the commands above.

## Public checkout versus complete local archive

The Git release intentionally omits raw/interim/processed data, local virtualenv files and the opaque fitted estimator bundle (`docs/stage5_evidence/frozen_estimators.pkl`). The early `docs/stage0_evidence/recorded_*.json` response fixtures and `live_*.txt` response captures also remain local. They are source payloads even though stored outside `data/`. Their manifests, checksums and audit summaries remain published without changing historical references.

The exact hashes of these local-only artifacts remain in the V1 freeze manifest. Consequently, the full safe suite and `stage7/verify_v1.py` require the complete original local archive and guarded environment; a plain Git checkout alone will not pass them. Missing files are not a scientific regression or permission to bypass the guards. No serialized estimator is loaded merely to check integrity.

Stage 8 refreshed only presentation-document hashes in the V1 manifest. All scientific hashes and source checkpoints were retained. The original manifest and verification record remain archived. `stage7/build_docs.py` is the historical Stage 7 authoring helper; do not rerun it over the release polish.

Historical stage reports, execution ledgers and the Stage 0 probe retain original local paths as audit context. Reusable current entry points and public reproduction instructions use project-relative paths. No license has been assigned to original code in this release. NBA source-data ownership and redistribution rights are not granted by this repository; review source terms before any redistribution.
