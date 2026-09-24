# Stage 1C — Multi-season historical dataset

## 1. Objective

Extend the validated ingestion and pregame feature pipeline without changing Stage 1A checks or Stage 1B feature definitions. **Pass for the explicitly admitted nine-season subset, 2015–16 through 2023–24; the requested ten-season range is incomplete.** The combined dataset has 10,749 games. No models, Elo, performance metrics, betting odds, injury or player data were added. No 2025–26 outcome data was retrieved or inspected. No commit or push was performed.

## 2. Seasons attempted

2015–16, 2016–17, 2017–18, 2018–19, 2019–20, 2020–21, 2021–22, 2022–23, 2023–24 and 2024–25. The allowlist in `src/nba_game_prediction/seasons.py` rejects other seasons before cache access or network requests.

## 3. Seasons successfully retrieved

All ten requested seasons have checksummed raw caches. Nine new requests succeeded on their first attempts; the immutable 2023–24 snapshot was reused. Requests were serial with conservative spacing. Endpoint: `LeagueGameLog`, team mode, `SeasonType="Regular Season"`, explicit season. `stage1c_evidence/retrieval_manifest.json` records original timestamps, request duration/result, endpoint parameters, nba_api version, column schema, row count and response SHA-256. `acquisition_log.json` records this acquisition session and cache reuse.

## 4. Failed/incomplete seasons

There were no retrieval failures. **2024–25 is structurally incomplete after validation and quarantined in its entirety from feature generation and combination.** Its raw cache contains 1,230 games and 2,460 team rows, but five games have two away labels and no home label:

| Game ID | Date | Teams |
| --- | --- | --- |
| 0022400147 | 2024-11-02 | MIA / WAS |
| 0022400621 | 2025-01-23 | SAS / IND |
| 0022400633 | 2025-01-25 | IND / SAS |
| 0022401229 | 2024-12-14 | ATL / MIL |
| 0022401230 | 2024-12-14 | HOU / OKC |

Observed anomaly: `not_one_home_and_one_away`. No correction or inferred designation was applied. The accepted structural subset has 1,225 games, but removing the five games would make subsequent histories incomplete. Those 1,225 rows are retained only as audit-stage canonical/outcome tables; none are admitted to the analytical dataset. There is no 2024–25 feature artifact. See `data/interim/seasons/game_anomalies_2024_25.parquet` for original source values. The predeclared `build_policy.md` allows this only with explicit `--allow-partial`; strict mode stops. Future resolution requires a separately reviewed, provenance-preserving home/away reconciliation followed by a complete season rebuild. Neutral venue context alone does not authorize guessing a home side.

## 5. Generalized ingestion design

`ingest.py`, `normalize.py` and `validate.py` accept a season parameter while preserving the 2023–24 default and existing APIs. `multiseason.py` provides `build_season_games(root, season, fetch=False)` and `build_multi`. Two reusable CLIs serve all seasons. Raw responses are saved before transformation with immutable, exclusive file creation; existing caches must pass parameter/schema/checksum verification. No proxy rotation or bypass was used. Derived Stage 1C outputs are reproducibly replaced atomically; original Stage 1A/B artifacts are never overwritten.

All prior pairing, uniqueness, reciprocal identity, date, W/L, score, scoring-component and rebound checks remain active. Plus-minus discrepancies remain warnings. Rejections retain explicit source evidence. Scope checks use season-specific source IDs, ID prefixes and dates, including the restart gap. A complete accepted history is required before season features can be exported.

## 6. Generalized feature-engine design

Feature definition version remains **1.0.0**, build version **1C.1**. History is grouped by `(season, season_type, team_id)`, ordered by actual source calendar date. Outcome-derived series shift by one before expanding/rolling calculations. Windows require all five or ten prior games. Same-team/same-date ambiguity remains fatal. No GAME_ID ordering is used to determine history; it is only an output tie breaker between unrelated games. Team IDs are the entity keys; per-season identity maps are checked, and cross-season names are not assumed permanent.

The unchanged 13 team features are `games_played_before`, `season_win_pct_before`, `win_pct_last_5`, `win_pct_last_10`, `point_diff_avg_last_5`, `point_diff_avg_last_10`, `pts_for_avg_last_5`, `pts_for_avg_last_10`, `pts_against_avg_last_5`, `pts_against_avg_last_10`, `rest_days`, `is_back_to_back`, `games_last_7_days`. Game features contain home/away versions plus `season_win_pct_diff`, `win_pct_last_5_diff`, `win_pct_last_10_diff`, `point_diff_last_5_diff`, `point_diff_last_10_diff`, `rest_days_diff` (home minus away).

## 7. Season-reset policy

Every season starts with zero prior games for every team. Season win rate, rolling statistics and rest are missing at the opener; back-to-back and prior-seven-day counts are zero. Prior-season information and offseason priors are excluded. The 2019–20 suspension is inside one regular season, so it does not trigger a second reset: long rest remains the actual calendar gap, and rolling form continues within that season. Rest is elapsed dates minus one; prior-seven-day activity uses `[target_date - 7 days, target_date)`.

## 8. Per-season counts

Observed raw counts, canonical acceptance and admission to features are separate quantities. All seasons contain 30 teams, with stable team ID membership. The CSV's min/max games per team refer to structurally accepted rows (2024–25 is 80–82); its raw source has 82 rows per team. Every admitted game has exactly two team rows, one canonical row, one feature row and one separate outcome row.

| season | team_game_rows | unique_games | accepted_games | rejected_games | feature_rows | min_games_per_team | max_games_per_team | first_game_date | last_game_date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015-16 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2015-10-27 | 2016-04-13 |
| 2016-17 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2016-10-25 | 2017-04-12 |
| 2017-18 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2017-10-17 | 2018-04-11 |
| 2018-19 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2018-10-16 | 2019-04-10 |
| 2019-20 | 2118 | 1059 | 1059 | 0 | 1059 | 64 | 75 | 2019-10-22 | 2020-08-14 |
| 2020-21 | 2160 | 1080 | 1080 | 0 | 1080 | 72 | 72 | 2020-12-22 | 2021-05-16 |
| 2021-22 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2021-10-19 | 2022-04-10 |
| 2022-23 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2022-10-18 | 2023-04-09 |
| 2023-24 | 2460 | 1230 | 1230 | 0 | 1230 | 82 | 82 | 2023-10-24 | 2024-04-14 |
| 2024-25 | 2460 | 1230 | 1225 | 5 | 0 | 80 | 82 | 2024-10-22 | 2025-04-13 |

All warning counts are zero. The single raw null is the previously documented 2023–24 optional field; no required identity/outcome null was admitted. Exact per-column nulls and full per-team distributions are in `scope_audit.json`.

## 9. Special-season handling and scope audit

**Observed:** 2019–20 contains 1,059 games, 2,118 team rows, and 64–75 games per team. Its observed distribution is {'64': 1, '65': 4, '66': 2, '67': 1, '71': 2, '72': 10, '73': 8, '74': 1, '75': 1}. All 22 returning teams have exactly eight games from July 30 through August 14, 2020. No games appear in the configured suspension gap. **Source documentation:** the NBA describes eight seeding games over those dates, with play-in afterward ([restart announcement](https://pr.nba.com/seeding-games-awards/)). The NBA historical table reports 1,059 games ([historical total](https://www.nba.com/news/power-rankings-notebook-week-12-2022-23)). **Implementation:** total, bubble participation/counts and a conservative 63–75 per-team boundary are checked, without an 82-game assumption; the actual minimum is 64.

**Observed:** 2020–21 contains 1,080 games, 2,160 team rows, exactly 72 games per team, December 22 through May 16. **Source documentation:** the NBA specified a 72-game season and separate subsequent play-in ([format announcement](https://official.nba.com/nba-announces-structure-and-format-for-2020-21-season/)). **Implementation:** the 72-game expectation is explicit.

**Venue limitation:** bubble games have designated sides without normal home-court conditions. Other international/neutral games also occur; the supplied game log does not provide a dependable venue-neutrality indicator, so we do not infer a per-game neutral flag. In 2024–25, the documented Cup semifinals occurred December 14 ([Cup dates](https://www.nba.com/news/nba-unveils-new-logo-and-game-dates-for-emirates-nba-cup-2024)); the two corresponding source games fail home/away validation. No new neutral-site feature was added.

**Cup scope:** the 2023 and 2024 Cup finals are explicitly outside regular-season scope; neither final date contributes rows in these snapshots. Regular-season Cup games remain eligible when structural checks pass. Schedule-derived features describe eligible regular-season activity, not every physical appearance.

**Endpoint audit:** every raw season has its matching `2YYYY` source season ID and `002YY` game prefix; observed first/last dates match the configured boundaries. No preseason, playoff or play-in IDs/dates were observed. This supports consistent regular-season filtering in these snapshots, but 2024–25 demonstrates that scope filtering does not guarantee valid home/away fields. Non-leakage scope claims are bounded to the checked identifiers/dates and source metadata, not an independent event-by-event schedule reconciliation.

**Documentation versus assumptions:** configuration dates are admission boundaries, corroborated by observed dates and the schedule sources below; ordinary seasons use the documented normal 82-game structure. The strict complete-history policy is an implementation choice. All observations are recorded separately in `scope_audit.json`. Source references:

- [2015-16](https://pr.nba.com/nba-schedule-2015-16-season/)
- [2016-17](https://pr.nba.com/nba-schedule-2016-17-season/)
- [2017-18](https://pr.nba.com/nba-2017-18-game-broadcast-schedules/)
- [2018-19](https://pr.nba.com/2018-19-nba-schedule/)
- [2019-20 restart](https://pr.nba.com/seeding-games-awards/)
- [2019-20 historical game total](https://www.nba.com/news/power-rankings-notebook-week-12-2022-23)
- [2020-21](https://official.nba.com/nba-announces-structure-and-format-for-2020-21-season/)
- [2021-22](https://pr.nba.com/2021-22-nba-schedule-75th-anniversary-season/)
- [2022-23](https://pr.nba.com/2022-23-nba-regular-season-schedule-europe-middle-east-africa/)
- [2023-24](https://pr.nba.com/2023-24-nba-regular-season-schedule/)
- [2024-25](https://pr.nba.com/2024-25-nba-regular-season-schedule/)
- [2024 Cup dates](https://www.nba.com/news/nba-unveils-new-logo-and-game-dates-for-emirates-nba-cup-2024)

## 10. Regression check against 2023–24

All five regenerated tables match the protected Stage 1A/B originals exactly in values, column order, index and dtypes, and deterministic Parquet SHA-256: team games, canonical games, outcomes, team pregame features and game features. `regression_2023_24.json` records each comparison and hash. The baseline is tested before building other seasons. All 32 protected raw/artifact/evidence files retain their original hashes; old documents and manifests were not rewritten.

## 11. Multi-season leakage tests

**57 tests pass: all original 46 plus 11 Stage 1C tests.** The full suite ran with network sockets blocked. New checks cover opener resets, prior-season mutation (all next-season rows invariant), future-season mutation (all earlier rows invariant), shuffled combined inputs, exact equality of separate and combined feature generation, mislabeled seasons, invalid season dates, real five-table 2023–24 regression, holdout rejection before cache access, special-season scope, and quarantine/outcome-column exclusion. `multiseason_tests.txt` includes individual results. Two initial test-authoring errors were fixed (the opener assertion mistakenly included the nonmissing seven-day count, and a scope helper was supplied strings instead of parsed timestamps); no production rule was loosened.

## 12. Missingness by season

Missingness is expected and retained without dropping rows or imputing. Each admitted season has 30 missing team opener rates/rest values, 150 missing values per last-5 team statistic and 300 per last-10 statistic. Game affected counts count a game once if either team lacks the window. All 13 team and 32 game features, including individual home/away/difference fields, appear in `missingness_by_season.csv` (405 rows). Quarantined 2024–25 has no feature-missingness result; this is unavailable, not zero.

| Season | Team rate missing | Team rest missing | Team last-5 missing | Team last-10 missing | Game last-5 affected | Game last-10 affected |
| --- | --- | --- | --- | --- | --- | --- |
| 2015-16 | 30 | 30 | 150 | 300 | 78 | 157 |
| 2016-17 | 30 | 30 | 150 | 300 | 79 | 156 |
| 2017-18 | 30 | 30 | 150 | 300 | 80 | 155 |
| 2018-19 | 30 | 30 | 150 | 300 | 79 | 156 |
| 2019-20 | 30 | 30 | 150 | 300 | 77 | 153 |
| 2020-21 | 30 | 30 | 150 | 300 | 80 | 156 |
| 2021-22 | 30 | 30 | 150 | 300 | 78 | 157 |
| 2022-23 | 30 | 30 | 150 | 300 | 79 | 157 |
| 2023-24 | 30 | 30 | 150 | 300 | 81 | 156 |

## 13. Combined dataset schema

`data/processed/game_features_multiseason.parquet`: **10,749 × 42**, ten identity columns plus the unchanged 32 game features. Identity columns: season, season_type, game_id, game_date, home_team_id, home_team_name, home_team_abbreviation, away_team_id, away_team_name, away_team_abbreviation. Exact dtypes appear in `multiseason_build_manifest.json`. It contains no target-game points, W/L, box score or target.

`data/interim/game_outcomes_multiseason.parquet`: **10,749 × 5**, ordered as season, game_id, home_pts, away_pts, home_win. Keys agree exactly with the feature table; game IDs are globally unique. Both tables sort by season, date and game ID, with date removed from the outcome export after sorting.

Per-season audit tables are in `data/interim/seasons/`; admitted season features are in `data/processed/seasons/`. The root-level original 2023–24 files remain untouched. `team_identity_by_season.csv` records stable IDs and observed season-specific names/abbreviations. For 2024–25, canonical/interim tables are audit-only and must not be used as complete model histories.

## 14. Reproducibility evidence

From the active subproject, use the pinned `.venv`:

```sh
.venv/bin/python scripts/build_multi_season_games.py --start-season 2015-16 --end-season 2024-25 --allow-partial
.venv/bin/python scripts/build_season_games.py --season 2022-23
.venv/bin/python -m unittest discover -s tests -v
```

Default builds are cache-only; `--fetch` explicitly permits missing-source acquisition. Omit `--allow-partial` to fail closed on 2024–25. Two full rebuilds ran with `socket.socket` patched to raise on access. All per-season tables, combined tables, quality/missingness/identity CSVs and deterministic scope/retrieval summaries match their initial hashes. Raw cache hashes also match. Build timestamps intentionally vary and are excluded from deterministic-output comparison. `replay_verification.json` records hashes and replay results; `multiseason_build_manifest.json` records raw/code/output hashes, feature/build versions, requirement hash and installed versions. The environment is Python 3.10.8 with unchanged pinned requirements. Git ignore rules already exclude raw, interim and processed data.

## 15. Known limitations

The requested ten-season range is not fully admitted; 2024–25 is unavailable for development/evaluation until repaired through a reviewed provenance-preserving process. Present-day historical snapshots cannot certify intraday availability at the time of the original games; the existing Stage 1B calendar-date availability contract remains in force. Neutral-site, crowd and pandemic conditions are contextual limitations. Within-season pandemic gaps remain in rest features. Completeness checks use counts, dates and documented format plus structural integrity; they do not prove the absence of every possible upstream historical correction. No season is fabricated, and no values are silently corrected.

## 16. Recommended temporal development split

For the validated coverage, use **2015–16 through 2022–23 for training (9,519 games)** and **2023–24 for validation/development (1,230 games)**. The intended 2024–25 pre-holdout check is **blocked**, not silently replaced. Resolve and revalidate that season before treating the preferred split as complete; otherwise a separately approved redesign could move an earlier season into validation. Repeated model selection on any check set makes it development data, not an unbiased final test. **2025–26 remains an untouched final holdout** and was not accessed. This is a proposed split only; no model or metric was computed.

## 17. Stage 1C exit criteria

Pass for the nine-season analytical subset under the recorded partial-completion policy: multiple complete seasons, exact canonical/feature/outcome key correspondence, unchanged V1 definitions, explicit resets, passing leakage tests, exact 2023–24 regression, explicit special-season handling, separate outcomes, all 57 tests, two deterministic socket-blocked builds and no holdout access. The 1,225 structurally accepted 2024–25 audit games are **not admitted games** for these criteria. Full-range completion and the preferred 2024–25 evaluation checkpoint remain blocked. This report does not claim a complete 2015–16 through 2024–25 dataset.

## 18. Recommended Stage 2 scope

After review and separate approval: probabilistic baselines and a temporal evaluation framework, potentially constant home-win prior, chronological Elo, log loss, Brier score and calibration, with accuracy/ROC-AUC secondary. Resolve the missing pre-holdout check first or explicitly approve an alternative split. Stage 2 has not started.
