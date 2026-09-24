# DRAFT — 2024–25 pre-holdout protocol

**NOT YET EXECUTED. Stage 4A does not authorize opening.**

A separate explicit user decision must authorize a single opening. Verify the candidate freeze and protected artifact hashes first. The seven candidates are constant_home_prior, raw_elo, basketball_features_logistic, elo_logistic, features_plus_elo_logistic, basketball_features_hgb and features_plus_elo_hgb. The existing leading candidate is features_plus_elo_logistic, based only on frozen development evidence.

Primary comparison: **features_plus_elo_logistic versus raw_elo**. Report all seven candidates on exactly the same eligible 2024–25 games for transparency. Primary metrics: existing log loss and Brier score. Secondary: accuracy, ROC-AUC and existing fixed-bin calibration; no fitted calibrator. Define differences as candidate minus reference, with negative probability-loss differences favorable. Do not claim statistical significance from point estimates alone.

Keep the existing feature allowlists, missing-value mechanisms, frozen Elo K=20/H=50/alpha=0.50 and all selected estimator parameters. Estimator training remains 2015–16 through 2022–23. If persisted fitted estimators are unavailable, a separately authorized execution may reconstruct them deterministically using only that frozen training history, then hash/freeze them BEFORE opening 2024–25 labels. No re-selection, refitting on 2023–24, or recalculation of development performance is part of this protocol. Pregame Elo may carry forward through completed prior seasons and update only after each completed game. Rolling season features use strictly earlier completed games, with unchanged season resets and warmup retention.

The later authorized executor must introduce a narrowly scoped one-time opening boundary, not a force flag in normal development tests. It must verify source/code/recipe hashes, chronological pregame order and common game coverage, produce predictions and evaluate the frozen candidate set exactly once, and preserve an immutable opening ledger and outputs. Fail closed on unexpected data or provenance; do not silently rerun an opened evaluation. A recovery policy must be agreed before opening.

After opening: no tuning, feature changes, model-family additions, candidate expansion or calibration fitting if 2024–25 is to retain its pre-holdout meaning. Any change invalidates this planned protocol and must be disclosed; an already opened season cannot become unseen again. 2025–26 remains the final untouched holdout and is not authorized by this draft.

Stage 4A's documented historical exception remains in the record: legacy structural tests previously read 2024–25 outcomes, but did not produce model performance. Hardening does not erase that history or claim the source labels were never previously processed.
