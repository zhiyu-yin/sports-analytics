# Stage 1A — Historical game ingestion

Audit: 2026-09-23 America/New_York; requests on 2026-09-24 UTC.

## 1. Objective and status

**Exit criterion A is satisfied for the cached 2023-24 regular-season snapshot:** the maintained NBA client retrieved 2,460 team-game rows; the pipeline accepted 1,230 unique games, with no rejected games or validation warnings. Thirty teams each have 82 games. A locked environment, raw cache, normalized team table, canonical game table, separate outcomes, explicit anomaly handling, 27 passing offline tests, and deterministic offline rebuilds are present.

This is an identity/outcome dataset, not a prediction feature table. No rolling statistics, rest indicators, Four Factors, Elo, model-ready differences, models or evaluation metrics were created. Only 2023-24 outcomes were retrieved. Stage 0 recordings were not used as ingestion data. No 2025-26 holdout outcomes were inspected. No commit or push was performed.

## 2. Environment and dependencies

Project: `/Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/`.
Active subproject: `basketball/nba/game-prediction/`.

Created `.venv/` inside the active subproject, using the existing Homebrew Python 3.10.8. The other checked standard installation was Python 3.10.1; no newer interpreter was found in the checked Homebrew/Python-framework locations. Python 3.10 is supported by the installed nba_api release. No global Python packages were changed. Package installation succeeded, and `pip check` reported no broken requirements.

The [PyPI package metadata](https://pypi.org/project/nba_api/) was checked; the normal installation selected nba_api 1.11.4. Exact installed versions, including transitive dependencies, are locked in [requirements.txt](../requirements.txt):

```text
certifi==2026.7.22
charset-normalizer==3.5.1
idna==3.20
nba_api==1.11.4
numpy==2.2.6
pandas==2.3.3
pyarrow==25.0.1
python-dateutil==2.9.0.post0
pytz==2026.3.post1
requests==2.34.2
six==1.17.0
tzdata==2026.4
urllib3==2.8.0
```

No pytest dependency was needed: the suite uses Python's unittest. Dependency pins describe the tested Python 3.10/macOS environment; they are not a guarantee that every platform has compatible wheels.

## 3. Data source actually used

**Observed:** NBA Stats, accessed through `nba_api.stats.endpoints.leaguegamelog.LeagueGameLog`. The maintained client was invoked normally: no custom headers, proxy settings, browser imitation or bypass. Its own default request headers were used unchanged. Neither Kaggle nor an alternate archive was involved.

LeagueGameLog was selected because it returned both team rows for every game in a single season-level call. There was no need to try TeamGameLogs or LeagueGameFinder after the successful access test. The success does not establish why Stage 0 curl probes failed, nor future service reliability.

## 4. Exact endpoint and parameters

Endpoint: `https://stats.nba.com/stats/leaguegamelog`.
Full-season request:

```json
{
  "Counter": 0,
  "Direction": "ASC",
  "LeagueID": "00",
  "PlayerOrTeam": "T",
  "Season": "2023-24",
  "SeasonType": "Regular Season",
  "Sorter": "DATE",
  "DateFrom": "",
  "DateTo": ""
}
```

The initial minimal checks used the same parameters except `DateFrom="10/24/2023"`, `DateTo="10/25/2023"`. The probe timeout was 20 seconds, with one repeat after three seconds. The full-season timeout was 30 seconds. Only one full-season retrieval was necessary; all subsequent full builds used the cache.

## 5. Access results and evidence

| Request | HTTP | Team rows | Runtime | Observation |
|---|---:|---:|---:|---|
| Opening dates, attempt 1 | 200 | 28 | 0.770 s | Nonempty, 29-column LeagueGameLog |
| Identical opening dates, attempt 2 | 200 | 28 | 0.053 s | Identical raw response SHA-256 |
| Full 2023-24 regular season | 200 | 2,460 | 0.163 s | 1,230 distinct game IDs |

The initial probe SHA-256 was `6bec114238869079558a014a83a32657125c3926f50011b979f0889689371c2c` on both attempts. The full-season snapshot contains 390,337 UTF-8 bytes with SHA-256:

```text
8a3bc942e72e06ae88efd28c17a44918de0b484b22d85aea342eb739632ad4de
```

Full-season retrieval started `2026-09-24T02:07:37.016336+00:00` and finished `2026-09-24T02:07:37.179423+00:00`.

Evidence: [full-season provenance](stage1a_evidence/full_season_provenance.json), [quality results](stage1a_evidence/data_quality_2023_24.json), [offline tests](stage1a_evidence/offline_tests.txt), and [replay verification](stage1a_evidence/replay_verification.json). The timestamped directory under `stage1a_evidence/` contains both probe manifests and the environment snapshot. HTTP success, returned columns/counts and runtimes are measured observations, not documentation claims.

## 6. Raw caching design and commands

```text
data/
├── raw/2023-24/             # original source response text + immutable retrieval manifests
├── interim/                # four Parquet tables, quality JSON, build manifest
└── processed/              # intentionally empty; no feature/model artifacts
```

The client-exposed response text is encoded as UTF-8 and saved before transformation. It is not a JSON reserialization or a wire-level compressed packet capture. Cache filenames include retrieval time, a unique suffix and content checksum; exclusive creation prevents overwriting existing raw responses. The matching manifest records endpoint, parameters, UTC times, season/type, row count, columns, HTTP status, runtime, nba_api version and SHA-256. This is application-level immutability, not an operating-system write-protection mechanism.

On every build, the loader verifies full-season parameters, endpoint/status, SHA-256, columns and row count. Invalid caches fail loudly; they are not silently repaired with a new request. Conflicting full-season snapshots require explicit reconciliation. The small opening-date probe files cannot be mistaken for a full-season cache. Failure evidence is retained separately if a future fetch fails. No automatic retry loop exists in season ingestion.

Run from the active subproject:

```bash
# Recreate the tested environment if needed:
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# Default: strictly local, verified full-season cache required.
.venv/bin/python scripts/build_2023_24_games.py

# Permit one download only when no valid full-season cache exists.
.venv/bin/python scripts/build_2023_24_games.py --fetch

# Offline unit tests:
.venv/bin/python -m unittest discover -s tests -v
```

Even `--fetch` reuses a valid cache. `scripts/check_nba_access.py` is the separate bounded diagnostic used before ingestion; default reruns display existing evidence without a request. Its explicit `--retry-live` option is intended only for a later access diagnosis, not routine rebuilding.

`.gitignore` excludes `.venv/`, raw, interim and processed data. Small summary evidence remains reviewable under docs. Nothing was staged. Raw and transformed data remain local.

## 7. Observed raw schema

The 29 returned columns were:

```text
SEASON_ID TEAM_ID TEAM_ABBREVIATION TEAM_NAME GAME_ID GAME_DATE MATCHUP WL MIN
FGM FGA FG_PCT FG3M FG3A FG3_PCT FTM FTA FT_PCT OREB DREB REB AST STL BLK
TOV PF PTS PLUS_MINUS VIDEO_AVAILABLE
```

GAME_ID and SEASON_ID arrive as strings; TEAM_ID and box-score counts are numeric; GAME_DATE is a `YYYY-MM-DD` string; MATCHUP uses `vs.` or `@`; WL is W/L. Keep leading zeros. Source percentages, MIN and VIDEO_AVAILABLE stay in the raw cache; they are not predictors or required normalized count fields. Observed MIN ranged from 240 to 290, consistent with summed team minutes including overtime, but it is not used to infer exact timing.

There is one raw null: Boston's FT_PCT for game `0022301148`, 2024-04-09, with FTM=0 and FTA=0. The percentage is undefined with zero attempts; it is neither filled with zero nor used as a rejection criterion. Every other raw column has zero null cells. Per-column counts are retained in the quality JSON.

## 8. Normalization rules

`normalize.py` lowercases the selected source fields, adds fixed season/type labels, and preserves `source_season_id` for scope validation and `source_row` for traceability. Game IDs remain strings; malformed IDs are rejected rather than silently zero-padded. Dates must exactly parse as YYYY-MM-DD and are stored as timezone-naive midnight `datetime64[ns]`, representing the source's game date, **not tip-off time**.

Normalized accepted team-game columns:

```text
season season_type source_season_id game_id game_date team_id team_name
team_abbreviation matchup is_home opponent_team_abbreviation wl
pts fgm fga fg3m fg3a ftm fta oreb dreb reb ast stl blk tov pf plus_minus source_row
```

Counts/team IDs use nullable Int64, plus_minus Float64, is_home boolean and text fields string. Required invalid numbers are rejected; optional absent counts stay null and generate explicit warnings. No ratios or predictive features are calculated. The saved team-game table contains only accepted games; all rejected rows remain in immutable raw data and in anomaly observed-values payloads. Thus no failed game disappears silently.

## 9. Home/away parsing

An exact parser accepts `AAA vs. BBB` as designated home and `AAA @ BBB` as away. It verifies that AAA matches TEAM_ABBREVIATION and that the opponent differs. Row order is never used. Every accepted pair must have two different team IDs, one home, one away and reciprocal abbreviations. IDs/abbreviations are checked against nba_api's local static team registry; that registry is not a request for current game outcomes.

Two actual examples:

| Game ID | Date | Home | Away | Score | home_win |
|---|---|---|---|---|---|
| 0022300061 | 2023-10-24 | DEN (1610612743) | LAL (1610612747) | 119–107 | true |
| 0022300062 | 2023-10-24 | GSW (1610612744) | PHX (1610612756) | 104–108 | false |

Designated home does not prove ordinary home-court advantage for neutral-site tournament games; that is a later context issue.

## 10. Validation and rejection rules

Every game is assigned to accepted or rejected, with a conservation assertion. A game can have multiple anomaly reasons. No duplicate is silently deduplicated, no score is corrected automatically, and no missing opponent is synthesized.

| Rule / reason family | Action |
|---|---|
| invalid_game_id, invalid_game_date, invalid_team_id, missing_team_name, missing_team_abbreviation, invalid_matchup | Reject entire game; preserve raw row and reason |
| not_completed_or_invalid_wl | Reject missing/non-W/L result; source completion is inferred from completed-game logs plus valid W/L and scores |
| invalid_pts / invalid basic count | Reject negative, nonfinite, fractional, boolean or nonnumeric count values |
| out_of_scope_season_id | Require source SEASON_ID=22023 |
| out_of_scope_game_type_or_season | Require regular-season 2023-24 ID family 00223 plus ten-digit ID validation |
| out_of_scope_date | Require date within 2023-10-24 through 2024-04-14 |
| cup_championship_date_requires_reconciliation | Reject any December 9 row for explicit review; that date was the non-regular-season final |
| unknown_or_inconsistent_team_identity / inconsistent_team_mapping | Reject unknown IDs, mismatched ID/abbreviation or inconsistent names/abbreviations for an ID |
| duplicate_team_game | Reject every row for an affected game, even if the duplicate is identical |
| not_exactly_two_rows / not_two_distinct_teams | Reject incomplete or overfull pairs and repeated team identity |
| not_one_home_and_one_away / nonreciprocal_opponents | Reject invalid pairing |
| game_date_mismatch_or_missing | Reject inconsistent or missing dates between sides |
| noncomplementary_wl / tied_final_score / score_wl_mismatch | Reject inconsistent final outcome |
| points_do_not_match_scoring_components | Require PTS = 2×FGM + FG3M + FTM when components exist |
| invalid_box_score_counts | Require made≤attempted, FG3M≤FGM and FG3A≤FGA |
| rebound_total_mismatch | Require REB=OREB+DREB when present |
| missing_optional_* / invalid_plus_minus | Explicit warning; retain valid identities/outcomes and missing/suspicious raw values |
| plus_minus_score_mismatch | Explicit warning; compare both sides against score differential; never overwrite it or derive target from it |

The plus-minus policy intentionally treats it as nonauthoritative: a game with internally consistent scores/WL may remain accepted with a warning. All other structural, scope or score failures reject the full game. The full raw response is available for reconciliation; anomalies contain game_id, severity, reason and original observed rows as JSON.

## 11. Data quality results and scope checks

| Check | Observed result |
|---|---|
| Retrieved team-game rows | 2,460 |
| Unique game IDs | 1,230 |
| Accepted team-game rows / games | 2,460 / 1,230 |
| Rejected games / anomalous games / anomaly rows | 0 / 0 / 0 |
| Date range | 2023-10-24–2024-04-14 |
| Teams | 30 |
| Games per team | 82 for each team |
| Duplicate (game_id, team_id) rows | 0 extra; 0 involved |
| Rows per game | Exactly 2 for all 1,230 games |
| Home / away rows | 1,230 / 1,230 |
| Reciprocal opponents / dates / complementary W/L | All pass |
| Final score arithmetic and W/L consistency | All pass |
| PLUS_MINUS score-difference discrepancies | 0 |
| Raw missing values | One FT_PCT null, described above |
| Accepted normalized missing values | Zero in every output column |

**Observed scope evidence:** every source SEASON_ID is 22023; every GAME_ID starts with 00223; all dates fall within the regular-season interval. There are no December 9 championship-date rows, no February 18 All-Star-date rows and no rows outside the regular-season window. Prefix/date/season checks found no preseason, play-in, playoffs, All-Star or other non-regular-season records.

**Documentation context:** the [NBA schedule announcement](https://pr.nba.com/2023-24-nba-regular-season-schedule/) gives October 24–April 14 as the season window, followed by play-in and playoffs. The [NBA tournament schedule announcement](https://pr.nba.com/nba-announces-group-play-schedule-for-inaugural-in-season-tournament/) states that tournament games other than the championship count in regular-season standings and that each team plays 82 regular-season games. Therefore legitimate group/quarterfinal/semifinal games remain included.

**Interpretation:** the observed dates, identifiers, 30 teams and 82 games per team support completeness and consistency with the requested scope. 1,230 was not hard-coded as an acceptance rule. These checks are not an independent reconciliation of every game against a second source. The regular-season ID convention and date window are explicit scope assumptions enforced for this one season, not a generic all-season classifier.

## 12. Anomalies and rejected games

`data/interim/game_anomalies_2023_24.parquet` exists with zero rows and a stable four-column string schema:

```text
game_id severity reason observed_values_json
```

No accepted/rejected score anomaly was found in this live 2023-24 snapshot. The one null raw FT_PCT is documented missingness outside the normalized count schema, not a game anomaly. Stage 0's discrepancies were in different recorded samples and are not assumed to exist here.

Synthetic offline tests deliberately trigger malformed matchups/dates/IDs, duplicate/incomplete pairs, reciprocal-identity failures, same-team pairs, missing/noncomplementary outcomes, ties, score arithmetic errors, invalid counts, out-of-scope records and optional plus-minus conflicts. All 27 tests pass. These fixtures are clearly synthetic test cases, never ingestion data.

## 13. Canonical and separate outcome schemas

`data/interim/games_2023_24.parquet` has exactly one row per accepted completed game:

| Fields | Dtype |
|---|---|
| season, season_type, game_id | string |
| game_date | datetime64[ns], date semantics only |
| home_team_id, away_team_id | Int64 |
| home_team_name, away_team_name | string |
| home_team_abbreviation, away_team_abbreviation | string |
| home_pts, away_pts | Int64 |
| home_win | boolean |

`home_win` is true only when final home_pts>away_pts; ties/missing results never produce labels. Scores and outcome appear here for a reviewable canonical history, **not as inputs to a future model**.

`data/interim/game_outcomes_2023_24.parquet` separately contains only game_id, home_pts, away_pts and home_win. The separate table matches those columns of the canonical table exactly after Parquet readback. Future X must be a separate pre-game table joined to y by game_id; X does not exist yet.

## 14. Files created or updated

All new files are under the active subproject except umbrella README and .gitignore updates:

```text
.venv/
requirements.txt
src/nba_game_prediction/{__init__,ingest,normalize,validate}.py
scripts/check_nba_access.py
scripts/build_2023_24_games.py
tests/test_ingestion.py
data/raw/2023-24/             # two probe bodies, one full response + full manifest
data/interim/team_games_2023_24.parquet
data/interim/games_2023_24.parquet
data/interim/game_outcomes_2023_24.parquet
data/interim/game_anomalies_2023_24.parquet
data/interim/data_quality_2023_24.json
data/interim/build_manifest_2023_24.json
data/processed/              # empty
docs/stage1a_ingestion.md
docs/stage1a_evidence/        # probes, provenance, quality, tests, replay hashes
```

The build manifest records raw provenance, source/build script/requirements hashes and output hashes. Two offline rebuilds with `requests.Session.request` blocked produced byte-identical Parquet, quality and manifest files under the pinned environment. Raw checksums were verified, and outcomes were compared after Parquet readback. Reproducibility across different pandas/pyarrow versions is not asserted.

## 15. Known limitations

- NBA access worked today but has no reliability guarantee; persistent future failure must stop retrieval rather than trigger evasive access methods or an unapproved data-source switch.
- GAME_DATE is not an exact tip-off timestamp; this table cannot by itself support intraday pre-game availability claims.
- LeagueGameLog lacks an explicit game-status field. Completed status is inferred from the historical game-log endpoint, valid final scores and complementary W/L.
- Internal checks and per-team counts do not independently prove every source score or opponent is correct. No full external schedule reconciliation was performed.
- Current historical data may include later corrections; retrieval time records the snapshot, not the original publication time.
- Neutral-site designation is not venue advantage. No injury, lineup or market data has been introduced.
- Fixed 2023-24 dates, season IDs and static team identities deliberately constrain this pipeline; expansion needs a new scope audit.
- Optional fields with future warnings would require review before feature use. Never treat a successful run alone as data-quality approval.
- Raw cache immutability is enforced by the ingestion code; manual edits remain possible and are detected by checksums.

## 16. Stage 1A exit criteria

**A — satisfied for this snapshot.** Actual live data was preserved with provenance before transformation; accepted team/game/outcome tables are validated and conserved; anomalies have an explicit policy/table; all 27 offline tests pass; cache-only reruns were deterministic with network blocked; scope and missingness checks are documented. This conclusion is based on observed data and validation, not merely on code execution.

**B — not applicable today.** The maintained client succeeded, so an access blocker was not the final outcome.

## 17. Recommended Stage 1B scope (not started)

After reviewing this ingestion snapshot, define a precise prediction cutoff and feature-availability contract. Then build a separate pre-game feature table using a small set of shifted team-history inputs, with tests proving that target-game/future outcomes cannot change a game's features. Decide season warmup and neutral-site handling explicitly. Keep y separate, reserve the holdout, and do not begin model training until those leakage checks are complete. No Stage 1B implementation was performed here.
