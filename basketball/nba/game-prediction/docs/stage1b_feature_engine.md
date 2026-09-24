# Stage 1B — Leakage-safe pregame feature engine

Definition version: **1.0.0**. Scope: cached 2023-24 NBA regular-season history only.

## 1. Objective and result

**Stage 1B passes.** The output has 1,230 game rows (one for every Stage 1A game), 32 numeric pregame feature columns, and 10 identity columns. The intermediate table has 2,460 team rows, 13 features and 10 identity fields. All 46 tests pass: 27 unchanged Stage 1A tests and 19 new Stage 1B tests. Target-game mutation, future append/mutation, team isolation, exact rolling windows, shuffle invariance and same-date rejection are covered explicitly.

The stage reused local Parquet files, with network sockets blocked during two complete feature builds. No NBA data was downloaded, no holdout outcomes inspected, no model trained, no Stage 2 implementation started, and no commits or pushes made. All Stage 1A source files, input tables and evidence remain unchanged.

## 2. Input dataset and provenance

Before implementation, all four Stage 1A Parquet checksums and the quality artifact hash were verified against `data/interim/build_manifest_2023_24.json`. Every production feature build repeats that check, checks requirements.txt against the pinned manifest, and verifies the fixed snapshot counts before writing any outputs.

Observed input: 2,460 team rows, 1,230 unique games, 30 teams, 82 games/team and zero anomalies/rejections. No repeated team/game-date was found. The three substantive inputs are:

- `data/interim/team_games_2023_24.parquet`: completed team histories and validated identities.
- `data/interim/games_2023_24.parquet`: canonical pairing and scores.
- `data/interim/game_outcomes_2023_24.parquet`: independently checked against canonical outcome columns; remains separate from features.

The zero-row anomaly table and Stage 1A quality JSON are also checked. No raw response is read by the feature engine. Input SHA-256 values, including the Stage 1A manifest itself, are recorded in [build_manifest.json](stage1b_evidence/build_manifest.json). A mismatch raises an error and stops the build; it never causes a download or a silent Stage 1A rebuild.

## 3. Prediction-time / availability contract

The [availability contract](stage1b_availability_contract.md) was written before implementation.

For target game G with source game_date T, eligible history is that team's completed regular-season games with **game_date strictly less than T**. This is a conservative calendar-date rule; the source does not supply tip-off timestamps. No same-day result is used, and GAME_ID never breaks a same-team/date tie. Such a tie raises `ValueError` and stops the build.

A target game's own scores, W/L, plus-minus and other box scores must not affect its features. Those scores enter history only for later dates. Team identity and the target's date/home designation are permitted join/schedule context. History resets at the beginning of this one regular season; there is no prior-season carryover. No values are imputed, backfilled or supplied from a later game.

Design assumption: completed games on earlier dates are available for this date-based historical exercise. This is not proof of original publication timestamps or freedom from retrospective score corrections.

## 4. Exact feature definitions

Let H be all eligible earlier games for the team, ordered by date. Let n=|H|, W the indicator of winning a historical game, PF its score and PA its opponent's score.

| Feature | Definition / units | Minimum history |
|---|---|---:|
| games_played_before | n; games | 0 |
| season_win_pct_before | sum(W in H)/n; fraction | 1 |
| win_pct_last_5, win_pct_last_10 | Mean W over the immediately previous 5/10 games; fraction | 5/10 |
| point_diff_avg_last_5, point_diff_avg_last_10 | Mean (PF−PA) over previous 5/10 games; points/game | 5/10 |
| pts_for_avg_last_5, pts_for_avg_last_10 | Mean PF over previous 5/10 games; points/game | 5/10 |
| pts_against_avg_last_5, pts_against_avg_last_10 | Mean PA over previous 5/10 games; points/game | 5/10 |
| rest_days | Calendar date difference from previous game minus 1; days | 1 |
| is_back_to_back | 1 iff rest_days=0, else 0; binary, opener 0 | 0 |
| games_last_7_days | Count in [T−7 days,T); games | 0 |

Opponent scores come from the correctly paired canonical home/away scores, reconciled against the team rows. Historical wins are derived from paired scores and checked against W/L. PLUS_MINUS and other box-score columns are not used for feature values. No efficiency, pace, Four Factors, Elo, player, lineup, injury, odds, travel, altitude or opponent-adjusted features were added.

[stage1b_feature_dictionary.csv](stage1b_feature_dictionary.csv) enumerates all 13 team feature names and all 32 game feature names: description, unit, window, minimum_history, source_columns, availability_rule and definition_version. Identity fields are documented separately below and must not automatically become numerical model inputs.

## 5. Rolling/shift implementation

`features.py` validates distinct dates and reciprocal pairing, selects internal historical scores/win indicators, and processes each team separately. After a date sort within each team:

```python
prior = group[["_win", "_points_for", "_points_against", "_point_diff"]].shift(1)
season_rate = prior["_win"].expanding(min_periods=1).mean()
rolling_rate = prior["_win"].rolling(window=5, min_periods=5).mean()
```

The same shifted block feeds both 5/10-game windows. No unshifted statistic is exported. Local group indexes are reset before assignment, preventing cross-team alignment or shift leakage. Shuffled input produces identical sorted outputs. Output schemas are explicit allowlists rather than “drop a few known bad columns.”

[team_history_lineage.json](stage1b_evidence/team_history_lineage.json) records every team's ordered game IDs/dates. A target at position i uses only entries `[:i]`; its full-window last-n history is `[i-n:i]`. Together with input hashes and games_played_before this makes every history window traceable. Same-date guards ensure every listed predecessor has an earlier date.

## 6. Rest and schedule definitions

`rest_days=(T−previous_game_date).days−1`: January 1→January 3 gives 1; January 1→January 2 gives 0. The opener is missing. `is_back_to_back=0` at the opener means no observed prior game this season, not a measured offseason rest interval.

`games_last_7_days` includes a previous game exactly seven days before T and excludes the target date: **[T−7,T)**. A sorted-date left-boundary search counts eligible earlier rows; there is no inferred intraday ordering. Synthetic boundary tests verify both ends. The real dataset has 422 team rows marked back-to-back and no negative rest values. These are calendar-day gaps, not elapsed travel/recovery hours.

## 7. Team-level feature schema

`data/interim/team_pregame_features_2023_24.parquet`: 2,460 rows × 23 columns.

Identity fields: season, season_type, game_id, game_date, team_id, team_name, team_abbreviation, is_home, opponent_team_id, opponent_team_abbreviation. The remaining 13 columns are exactly the features in section 4.

There is no target-game pts, wl, plus_minus, point_diff, or box-score statistic. Rates and means are floating point; counts/rest/back-to-back use nullable integer types, is_home boolean, game IDs/names strings, and game_date retains date semantics at midnight. The exact persisted dtype for every field is in feature_quality.json and build_manifest.json.

## 8. Game-level feature schema

`data/processed/game_features_2023_24.parquet`: 1,230 rows × 42 columns.

Identity columns: season, season_type, game_id, game_date, home_team_id, home_team_name, home_team_abbreviation, away_team_id, away_team_name, away_team_abbreviation.

Each of the 13 team feature names has a `home_` and an `away_` copy (26 columns), joined by game_id with one-to-one validation. The six differences below bring the numeric total to 32. Every game identity matches the Stage 1A canonical table, with exactly one vector per side. There are no duplicated columns or IDs and no dropped early-season games.

**No home_pts, away_pts, home_win, target-game W/L, raw point difference or target box score appears here.** The untouched Stage 1A outcome table is y; the pregame table must be joined explicitly by game_id for later evaluation. No such model fit or training dataset was created in this stage.

## 9. Difference features

All differences use **home minus away**, with null propagation if either input is missing:

| Difference | Team feature subtracted |
|---|---|
| season_win_pct_diff | season_win_pct_before |
| win_pct_last_5_diff | win_pct_last_5 |
| win_pct_last_10_diff | win_pct_last_10 |
| point_diff_last_5_diff | point_diff_avg_last_5 |
| point_diff_last_10_diff | point_diff_avg_last_10 |
| rest_days_diff | rest_days |

Win-rate differences are fraction differences (0.10 = 10 percentage points), point-differential differences are points/game, and rest differences are calendar days. No other interactions were added.

## 10. Automated leakage tests

[leakage_tests.txt](stage1b_evidence/leakage_tests.txt) records **46 passing tests, zero failures/errors** with network sockets blocked. [test_run.json](stage1b_evidence/test_run.json) records counts and hashes of test sources/logs. Stage 1A's 27 tests still pass; all 19 feature tests pass.

- A: change target home/away scores, W/L and box values together; the target's team and game rows remain exactly equal, while later rows change as expected.
- B: append later games; every earlier team/game row remains exactly equal.
- C: mutate a future result; earlier rows remain exactly equal.
- D: each opener has zero prior games, missing rates/windows/rest, zero back-to-back and zero seven-day count.
- E: hand-check synthetic wins and differentials over exact 5/10-game windows, including the threshold rows and scored/conceded means.
- F: modify an unrelated team's history; the original teams' results remain unchanged.
- G: shuffle all input tables; output rows/values/dtypes remain exactly equal.
- H: create repeated same-team dates; an explicit error occurs instead of selecting a game-ID order.

Additional tests cover calendar boundaries, rest examples, difference directions, output allowlists/dictionary coverage, ignored plus-minus/box scores, mismatched identities/outcomes, incomplete pairs, duplicate columns and corrupt input bytes. Mutation tests operate on synthetic in-memory fixtures; no Stage 1A file is modified. They do not bypass the production file-hash gate.

## 11. Real-data sanity checks

I reviewed the following exact source histories and their arithmetic. [manual_checks.json](stage1b_evidence/manual_checks.json) stores all prior games for each example, exact window IDs, points, wins, date boundaries and expected feature values. In addition, an independent implementation based on Python list slices, sums and calendar arithmetic checked **31,980 scalar values (2,460×13)**; all matched the exported table. It does not reuse the shift/rolling implementation.


### Season Opener: LAL, 2023-10-24 (0022300061)

No prior games: games_played_before=0, rates/rolling/rest missing, back-to-back=0, seven-day count=0. No later game supplies a value.

### Sixth Game: LAL, 2023-11-04 (0022300134)

The prior ten games (or all available if fewer) are shown below. The last five rows are the last-5 window. Full season-to-date history is in the JSON evidence.

| Date | Game ID | Opponent | Points for–against | Win |
|---|---|---|---|---:|
| 2023-10-24 | 0022300061 | DEN | 107–119 | 0 |
| 2023-10-26 | 0022300076 | PHX | 100–95 | 1 |
| 2023-10-29 | 0022300100 | SAC | 127–132 | 0 |
| 2023-10-30 | 0022300111 | ORL | 106–103 | 1 |
| 2023-11-01 | 0022300127 | LAC | 130–125 | 1 |

Last-5 win rate: 3 / 5 = 0.6; mean point differential: (-12 + 5 + -5 + 3 + 5) / 5 = -0.8.

Last-10: missing: only 5 prior games, requires 10.

Rest: `(2023-11-04 - 2023-11-01).days - 1 = 2`. Seven-day history contains exactly 3 games: `0022300100`, `0022300111`, `0022300127`.

### Eleventh Game: LAL, 2023-11-14 (0022300026)

The prior ten games (or all available if fewer) are shown below. The last five rows are the last-5 window. Full season-to-date history is in the JSON evidence.

| Date | Game ID | Opponent | Points for–against | Win |
|---|---|---|---|---:|
| 2023-10-24 | 0022300061 | DEN | 107–119 | 0 |
| 2023-10-26 | 0022300076 | PHX | 100–95 | 1 |
| 2023-10-29 | 0022300100 | SAC | 127–132 | 0 |
| 2023-10-30 | 0022300111 | ORL | 106–103 | 1 |
| 2023-11-01 | 0022300127 | LAC | 130–125 | 1 |
| 2023-11-04 | 0022300134 | ORL | 101–120 | 0 |
| 2023-11-06 | 0022300150 | MIA | 107–108 | 0 |
| 2023-11-08 | 0022300163 | HOU | 94–128 | 0 |
| 2023-11-10 | 0022300015 | PHX | 122–119 | 1 |
| 2023-11-12 | 0022300187 | POR | 116–110 | 1 |

Last-5 win rate: 2 / 5 = 0.4; mean point differential: (-19 + -1 + -34 + 3 + 6) / 5 = -9.0.

Last-10 win rate: 5 / 10 = 0.5; mean point differential: (-12 + 5 + -5 + 3 + 5 + -19 + -1 + -34 + 3 + 6) / 10 = -4.9.

Rest: `(2023-11-14 - 2023-11-12).days - 1 = 1`. Seven-day history contains exactly 3 games: `0022300163`, `0022300015`, `0022300187`.

### Back To Back: LAL, 2023-11-15 (0022300198)

The prior ten games (or all available if fewer) are shown below. The last five rows are the last-5 window. Full season-to-date history is in the JSON evidence.

| Date | Game ID | Opponent | Points for–against | Win |
|---|---|---|---|---:|
| 2023-10-26 | 0022300076 | PHX | 100–95 | 1 |
| 2023-10-29 | 0022300100 | SAC | 127–132 | 0 |
| 2023-10-30 | 0022300111 | ORL | 106–103 | 1 |
| 2023-11-01 | 0022300127 | LAC | 130–125 | 1 |
| 2023-11-04 | 0022300134 | ORL | 101–120 | 0 |
| 2023-11-06 | 0022300150 | MIA | 107–108 | 0 |
| 2023-11-08 | 0022300163 | HOU | 94–128 | 0 |
| 2023-11-10 | 0022300015 | PHX | 122–119 | 1 |
| 2023-11-12 | 0022300187 | POR | 116–110 | 1 |
| 2023-11-14 | 0022300026 | MEM | 134–107 | 1 |

Last-5 win rate: 3 / 5 = 0.6; mean point differential: (-1 + -34 + 3 + 6 + 27) / 5 = 0.2.

Last-10 win rate: 6 / 10 = 0.6; mean point differential: (5 + -5 + 3 + 5 + -19 + -1 + -34 + 3 + 6 + 27) / 10 = -1.0.

Rest: `(2023-11-15 - 2023-11-14).days - 1 = 0`. Seven-day history contains exactly 4 games: `0022300163`, `0022300015`, `0022300187`, `0022300026`.

### Dense Recent Schedule: ATL, 2023-11-28 (0022300055)

The prior ten games (or all available if fewer) are shown below. The last five rows are the last-5 window. Full season-to-date history is in the JSON evidence.

| Date | Game ID | Opponent | Points for–against | Win |
|---|---|---|---|---:|
| 2023-11-06 | 0022300155 | OKC | 117–126 | 0 |
| 2023-11-09 | 0022300172 | ORL | 120–119 | 1 |
| 2023-11-11 | 0022300175 | MIA | 109–117 | 0 |
| 2023-11-14 | 0022300018 | DET | 126–120 | 1 |
| 2023-11-15 | 0022300193 | NYK | 114–116 | 0 |
| 2023-11-17 | 0022300029 | PHI | 116–126 | 0 |
| 2023-11-21 | 0022300039 | IND | 152–157 | 0 |
| 2023-11-22 | 0022300227 | BKN | 147–145 | 1 |
| 2023-11-25 | 0022300241 | WAS | 136–108 | 1 |
| 2023-11-26 | 0022300246 | BOS | 103–113 | 0 |

Last-5 win rate: 2 / 5 = 0.4; mean point differential: (-10 + -5 + 2 + 28 + -10) / 5 = 1.0.

Last-10 win rate: 4 / 10 = 0.4; mean point differential: (-9 + 1 + -8 + 6 + -2 + -10 + -5 + 2 + 28 + -10) / 10 = -0.7.

Rest: `(2023-11-28 - 2023-11-26).days - 1 = 1`. Seven-day history contains exactly 4 games: `0022300039`, `0022300227`, `0022300241`, `0022300246`.


These histories also show that GAME_ID ordering is not chronological: the Lakers' November 14 ID `0022300026` comes after November 12 ID `0022300187` in time. The date sort handles this correctly; it is not a data anomaly.

## 12. Missingness

Missing values are the intended warmup behavior; there is no imputation or early-game removal.

| Feature | Team rows missing | Home rows missing | Away rows missing |
|---|---:|---:|---:|
| games_played_before | 0 | 0 | 0 |
| season_win_pct_before | 30 | 15 | 15 |
| win_pct_last_5 | 150 | 75 | 75 |
| win_pct_last_10 | 300 | 148 | 152 |
| point_diff_avg_last_5 | 150 | 75 | 75 |
| point_diff_avg_last_10 | 300 | 148 | 152 |
| pts_for_avg_last_5 | 150 | 75 | 75 |
| pts_for_avg_last_10 | 300 | 148 | 152 |
| pts_against_avg_last_5 | 150 | 75 | 75 |
| pts_against_avg_last_10 | 300 | 148 | 152 |
| rest_days | 30 | 15 | 15 |
| is_back_to_back | 0 | 0 | 0 |
| games_last_7_days | 0 | 0 | 0 |


- Last-5: 150 team rows (30×5), affecting 81 games with at least one missing side.
- Last-10: 300 team rows (30×10), affecting 156 games with at least one missing side.
- Rest/season win percentage: 30 team rows (one opener per team), affecting 15 games.
- Counts and back-to-back indicators: no missing values.

Difference-feature missingness:

- `season_win_pct_diff`: 15 game rows missing.
- `win_pct_last_5_diff`: 81 game rows missing.
- `win_pct_last_10_diff`: 156 game rows missing.
- `point_diff_last_5_diff`: 81 game rows missing.
- `point_diff_last_10_diff`: 156 game rows missing.
- `rest_days_diff`: 15 game rows missing.

Home/away missing counts need not be equal because teams reach their fifth/tenth prior game on different dates and venues. Warmup treatment for future training remains a review decision; none was selected silently.

## 13. Output counts and observed anomalies

2,460 unique team-game rows and 1,230 unique game rows, covering exactly the Stage 1A accepted IDs. Thirty teams each retain all 82 games. No same-date ambiguity, negative rest, identity mismatch, duplicate feature column, or unexpected feature discrepancy was found. All expected missing values have known warmup causes.

This does not independently recertify NBA source accuracy: Stage 1A's date/status/source limitations still apply. No Stage 0/1A ingestion was rerun.

## 14. Reproducibility and artifacts

Run from `basketball/nba/game-prediction/`, using the existing pinned `.venv`:

```bash
.venv/bin/python scripts/build_2023_24_features.py
.venv/bin/python scripts/audit_2023_24_features.py
.venv/bin/python -m unittest discover -s tests -v
```

The feature build has no download option or source API import. It validates local provenance first. Two full builds with socket creation blocked produced identical SHA-256 values for both Parquet files, the dictionary, quality JSON and lineage JSON. [replay_verification.json](stage1b_evidence/replay_verification.json) records the two build timestamps and audit-script hash. Build-manifest timestamps intentionally differ; the deterministic comparison excludes that timestamp and compares actual artifact/input/code hashes.

`build_manifest.json` records build UTC timestamp, definition version, all input hashes, source-code hashes, row counts, output schemas, output SHA-256, contract hash and pandas/NumPy/PyArrow versions. Reproducibility is asserted under the pinned environment, not across library versions.

New files:

```text
src/nba_game_prediction/features.py
src/nba_game_prediction/schedule.py
src/nba_game_prediction/feature_io.py
scripts/build_2023_24_features.py
scripts/audit_2023_24_features.py
tests/test_features.py
data/interim/team_pregame_features_2023_24.parquet
data/processed/game_features_2023_24.parquet
docs/stage1b_availability_contract.md
docs/stage1b_feature_dictionary.csv
docs/stage1b_feature_engine.md
docs/stage1b_evidence/{feature_quality,manual_checks,build_manifest}.json
docs/stage1b_evidence/{team_history_lineage,replay_verification,test_run}.json
docs/stage1b_evidence/leakage_tests.txt
```

Existing raw/interim/processed ignore rules already cover generated data. No dependency changes were necessary. Stage 1A evidence was not overwritten.

## 15. Known limitations and assumptions

- Earlier dates are the temporal eligibility rule; exact tip-off, game-completion and data-publication times are unavailable.
- Historical snapshots may contain later corrections. Hashing preserves this snapshot, not the original as-of publication history.
- Rest/density refer to counted regular-season games. The non-counting Cup championship, preseason and playoffs are absent; Lakers/Pacers December rest can therefore differ from physical all-competition rest. This is an explicit scope limitation of these V1 schedule features, not silently added outside data.
- Rest cannot represent travel, altitude or actual hours between games. Neutral-site games still have designated home/away identities.
- Same-day doubleheaders fail the build rather than receive an inferred order.
- Features start fresh at each team's 2023-24 opener; no offseason priors or imputation are supplied. Count windows have full-history requirements.
- Teams not sharing opponents should remain isolated; an opponent's historical score legitimately contributes to a team's own historical points against. The engine is not opponent adjusted.
- Structural validation consults the complete input for consistency, but feature values use earlier history only. Mutating malformed future identities can appropriately stop a build; the invariance tests concern valid completed-game mutations.

## 16. Stage 1B exit criteria

All requested criteria pass: every Stage 1A game has one feature row; all team-history values use strictly earlier dates; target and future invariants pass; team isolation and hand-checkable windows pass; missingness is explicit; target columns are absent; complete builds work offline; and all Stage 1A/1B tests pass. Real worked examples and the independent full-table comparison agree with the outputs.

The conclusion is limited to the defined V1 contract and snapshot. No model performance claim is made.

## 17. Recommended Stage 2 scope — not started

After reviewing Stage 1B, agree on a chronological development/evaluation split and an explicit warmup policy. The next proposed scope is a training-derived constant home-win probability, chronological Elo, and probability-evaluation infrastructure (log loss, Brier score and calibration). Fit priors/parameters only on training history and keep the final holdout reserved. With this single development season, any within-season evaluation must remain clearly labeled development work. Exact Stage 2 scope requires the next review; no baseline, metric calculation or model training was implemented here.
