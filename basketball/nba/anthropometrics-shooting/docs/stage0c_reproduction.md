# Stage 0C reproduction

Use the separate Python environment with Stage 0B's existing `pyarrow==21.0.0` dependency. No dependency or code change is required in NBA Game Prediction. The new module is `src/anthropometrics_shooting/stage0c.py`; old modules and frozen reports are unchanged.

From the anthropometrics subproject, with the original local data bundle present:

```sh
python3 scripts/build_stage0c.py
python3 scripts/test_stage0c.py
```

The tests run only `test_stage0c.py`, not earlier suites that read outcomes. Build checks preserved source hashes, regenerates Stage 0C evidence, compares reference membership against Stage 0B and uses a three-column candidate Parquet projection. Test finalization records the release decision and test hashes. Do not rerun `prepare_stage0c.py` over the existing declaration; it intentionally refuses replacement. The preparation timestamp and primary sample are already frozen.

Browser retrieval was necessary because command-line official API probes timed out. On `https://www.nba.com/stats/draft/combine-anthro`, select each season from 2000-01 through 2013-14, then 2019-20 for discrepancy review. Wait for the preceding table contents to be replaced, not merely for the season selector to change. Read the rendered DOM table, preserving selected season, page URL, header labels and all cell strings. Save each capture with a UTC timestamp. The audit used read-only browser DOM extraction, not fabricated API JSON or hidden application data.

Raw captures are under `data/raw/stage0c/browser_*.json`; the accepted 2001 capture ends `_verified.json`. The initial `browser_2001-02.json` is deliberately rejected because its table was stale. All accepted captures map uniquely by normalized same-year player name to the combine archive. Their hashes and accepted/rejected states are in `browser_capture_manifest.json`.

Do not overwrite these raw captures during a future refresh. Use a separate versioned audit directory and compare changes. The offline audit depends on the saved table snapshots and original local Stage 0/0B bundle, which are intentionally Git-ignored. It does not promise that future live pages will retain identical bytes or values.

A full reference-membership snapshot, normalized official measurements and source-wide comparison ledgers remain under `data/interim/stage0c_*`. Only selected comparisons and required compact evidence are in docs. No scientific residuals or model outputs are generated.
