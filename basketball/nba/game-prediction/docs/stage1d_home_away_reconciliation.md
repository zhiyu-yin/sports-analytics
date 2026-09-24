# Stage 1D — 2024–25 home/away reconciliation

## 1. Objective

Resolve five home/away anomalies with independent authoritative evidence, preserve the original NBA LeagueGameLog source, and admit 2024–25 only after full validation. **Stage 1D passes:** all five mappings are supported by explicit official schedule fields; the rebuilt season has 1,230 canonical games and feature rows. The combined dataset has 11,979 games across 2015–16 through 2024–25. Feature definition version remains 1.0.0. No model, Elo, metric, tuning, commit or push was performed. No 2025–26 data source was requested or used.

## 2. Why 2024–25 was quarantined

The immutable LeagueGameLog snapshot contains two `@` rows for each of five games. Stage 1A correctly rejects these under `not_one_home_and_one_away`. Stage 1C retained 1,225 structurally accepted games for audit but excluded the entire season from features to avoid incomplete histories. All original Stage 1C evidence, anomalies and per-season tables remain unchanged. Stage 1D adds a separate reviewed layer; no MATCHUP string was edited, even in the reconciled team table.

## 3. The five anomalous games

| Game ID | Date | Raw labels (unchanged) | Designated home | Designated away | Venue / city | Neutral |
| --- | --- | --- | --- | --- | --- | --- |
| 0022400147 | 2024-11-02 | MIA @ WAS; WAS @ MIA | WAS | MIA | Arena CDMX / Mexico City | True |
| 0022400621 | 2025-01-23 | SAS @ IND; IND @ SAS | IND | SAS | Accor Arena / Paris | True |
| 0022400633 | 2025-01-25 | IND @ SAS; SAS @ IND | SAS | IND | Accor Arena / Paris | True |
| 0022401229 | 2024-12-14 | ATL @ MIL; MIL @ ATL | MIL | ATL | T-Mobile Arena / Las Vegas | True |
| 0022401230 | 2024-12-14 | HOU @ OKC; OKC @ HOU | OKC | HOU | T-Mobile Arena / Las Vegas | True |

Each row's reason is `not_one_home_and_one_away`; each confidence is `authoritative`. Team IDs and original row order are explicitly recorded in [the reviewable CSV](stage1d_home_away_reconciliation.csv), also stored under `stage1d_evidence/home_away_reconciliation.csv` and `data/interim/home_away_reconciliation_2024_25.parquet`. Original order is retained for traceability only, never used to select home.

## 4. Independent sources used

The primary evidence for **each** game is the [NBA official ScheduleLeagueV2 response for 2024–25](https://stats.nba.com/stats/scheduleleaguev2?LeagueID=00&Season=2024-25), retrieved through the maintained nba_api client with explicit parameters `LeagueID=00`, `Season=2024-25`. This is a separate official schedule representation from LeagueGameLog's MATCHUP field, not an independent organization. We inspected the actual returned objects, not search snippets: `gameId`, `gameCode`, `gameDateEst`, `homeTeam.teamId`, `homeTeam.teamTricode`, `awayTeam.teamId`, `awayTeam.teamTricode`, `arenaName`, `arenaCity`, `isNeutral` and event labels.

Retrieval completion: **2026-09-24T16:41:04.821997+00:00**. Timestamp is the UTC filesystem completion time of the initial successful JSON extraction. Source metadata and exact parameters are saved in `source_manifest.json`; its checksum is explicitly for parsed JSON serialization, not wire bytes. Only selected factual evidence is retained, with no full news article or player data. Context storage excludes schedule scores, records and standings.

The five official NBA.com game pages were opened first, but their text views omitted explicit home/away fields. A direct HTML request returned 403; no bypass was attempted. The schedule endpoint returned the required explicit fields. The NBA-hosted [Paris report](https://www.nba.com/news/victor-wembanyama-returns-to-france-spurs-pacers-nba-paris-games-2025) independently corroborates Indiana as designated home on January 23 and San Antonio on January 25. No conflicting explicit designation was found among inspected official evidence. The known LeagueGameLog discrepancy remains preserved and documented.

## 5. Game-by-game reconciliation

For every game in section 3, the official schedule object with the exact game ID supplies the designated sides, date and venue. The evidence keys are:

| Game ID | Official schedule gameCode | Home ID | Away ID |
| --- | --- | --- | --- |
| 0022400147 | 20241102/MIAWAS | 1610612764 | 1610612748 |
| 0022400621 | 20250123/SASIND | 1610612754 | 1610612759 |
| 0022400633 | 20250125/INDSAS | 1610612759 | 1610612754 |
| 0022401229 | 20241214/ATLMIL | 1610612749 | 1610612737 |
| 0022401230 | 20241214/HOUOKC | 1610612760 | 1610612745 |

The reasons for all five changes are identical: the raw pair lacks a designated home, whereas the official schedule explicitly names one. Source URL and timestamp are attached to every CSV row. No score, winner, list position, abbreviation ordering or game-ID arithmetic determines a designation. NBA game-page references for manual navigation:

- [Miami / Washington, November 2](https://www.nba.com/game/mia-vs-was-0022400147)
- [San Antonio / Indiana, January 23](https://www.nba.com/game/sas-vs-ind-0022400621)
- [Indiana / San Antonio, January 25](https://www.nba.com/game/ind-vs-sas-0022400633)
- [Atlanta / Milwaukee, December 14](https://www.nba.com/game/atl-vs-mil-0022401229)
- [Houston / Oklahoma City, December 14](https://www.nba.com/game/hou-vs-okc-0022401230)

These navigation links are not used as evidence merely from their URL team order; the structured schedule fields above are the designation authority.

## 6. Designated home versus physical home

The target remains **P(designated home team wins)**. All five games have explicit NBA home/away identities despite neutral venues. Arena CDMX, Accor Arena and T-Mobile Arena are not either participating team's ordinary home arena. Official `isNeutral=true`, venue and city fields establish that classification; the malformed matchup labels do not. Crowd support, travel advantage or a player's national affiliation do not change the target designation.

## 7. Neutral-site findings and root-cause limits

All five reconciled games are neutral-site: one Mexico City game, two Paris games and two Cup semifinals. The full 2024–25 official schedule contains 1,230 regular-season game IDs and exactly these five with `isNeutral=true`. `data/interim/game_context_2024_25.parquet` preserves all 1,230 schedule neutrality/venue records separately from features.

The previously audited 2019–20 bubble supplies **88 additional known neutral games** (22 teams × 8 / 2). Thus at least **93 admitted historical games are known neutral** from this stage's schedule evidence plus the prior bubble audit. This is a lower bound, not a complete cross-season inventory. Earlier international and Cup games have not all been individually audited for context. Quality rows use missing, not zero, for unaudited historical seasons; 2019–20's 88 is explicitly a bubble-only lower bound.

**Observed pattern:** all five malformed pairs coincide exactly with 2024–25 official neutral-site games. **Inference only:** LeagueGameLog may encode both teams as away for neutral games in this snapshot. The provider's underlying cause is unverified; this is not promoted into a generic parser rule, nor assumed to apply identically to other seasons.

Do not add neutrality to V1 features now. Recommend a separately versioned Stage 2/3 extension only after historical venue/neutral coverage is audited consistently and pregame availability is established. Otherwise the model would have reliable labels for 2024–25 but incomplete historical coverage. Unknown must never be treated as ordinary home court.

## 8. Reconciliation-layer implementation

New `src/nba_game_prediction/reconciliation.py` loads checksummed evidence and compares mapping/context fields to the saved official factual extracts. Only rows marked `authoritative` can apply. It validates season, game date, both raw team IDs and original MATCHUP strings, approved team IDs/abbreviations, uniqueness and provenance. Normal validation runs before application; a mapping must target a game whose only rejection is the reviewed home/away anomaly. Additional errors remain fatal.

`apply_reconciliation` copies the normalized frame and modifies **only `is_home`** for explicit approved IDs. It does not alter `matchup`, `_observed`, scores, W/L, opponent abbreviations or any other source value. Original text and source-row references remain available. All validation runs again afterward. Unknown anomalous games receive no fallback. Unresolved/conflicted rows fail closed. The unchanged parser and normalization have no reconciliation logic.

New `src/nba_game_prediction/stage1d.py` and `scripts/build_reconciled_multiseason.py` run the offline build. Stage 1D 2024–25 canonical/team/outcome/feature/anomaly tables are written to `data/interim/reconciled/`; this avoids replacing Stage 1C audit files. Its game feature table is additionally published at `data/processed/seasons/game_features_2024_25.parquet`. The reconciliation table and applied-game ledger make the external designation explicit. No Stage 1A/B validation or numerical feature rule changed.

## 9. Rebuilt 2024–25 validation results

Observed: 2,460 accepted team rows, **1,230 accepted games**, 30 teams, exactly 82 games per team, five reconciled games, zero rejected games, zero warnings. Date range: 2024-10-22 through 2025-04-13. Every game has two distinct teams, one designated home, one away, reciprocal opponents, matching dates, complementary W/L, valid scores, scoring arithmetic and rebound consistency. The existing plus-minus warning policy remains unchanged. The expected count was checked through the complete per-team scope audit, not forced into the output.

See `stage1d_evidence/reconciliation_validation.json` for results, applied IDs and full scope audit. Raw scores/WL and all raw cache manifests are unchanged.

## 10. 2024–25 feature-generation result

Created **2,460 × 23 team pregame** and **1,230 × 42 game feature** tables, using unchanged V1 definitions, explicit season resets and strict earlier-date history. No game is dropped. Each team's `games_played_before` runs from 0 through 81. Independent slice-based checks compare rolling five-game points and wins across every team history, including games following reconciliation. Neutrality is context only. No target outcome columns enter features. Warmup missingness remains unfilled and is reported in `stage1d_evidence/missingness_by_season.csv`.

## 11. Multi-season rebuild result

The count is derived by summing validated season counts: **11,979 games**, covering all ten seasons from 2015–16 through 2024–25. Outputs:

- `data/processed/game_features_multiseason.parquet`: 11,979 × 42.
- `data/interim/game_outcomes_multiseason.parquet`: 11,979 × 5.

Combined IDs are unique; feature/outcome keys match exactly; chronology sorts by season and date. The prior Stage 1C combined tables are preserved as `data/interim/stage1c_game_features_multiseason.parquet` and `data/interim/stage1c_game_outcomes_multiseason.parquet`. Historical Stage 1C evidence remains a record of that earlier quarantined build.

| Season | Accepted games | Reconciled | Rejected | Feature rows | Known neutral count |
| --- | --- | --- | --- | --- | --- |
| 2015-16 | 1230 | 0 | 0 | 1230 | not audited |
| 2016-17 | 1230 | 0 | 0 | 1230 | not audited |
| 2017-18 | 1230 | 0 | 0 | 1230 | not audited |
| 2018-19 | 1230 | 0 | 0 | 1230 | not audited |
| 2019-20 | 1059 | 0 | 0 | 1059 | 88 (bubble lower bound) |
| 2020-21 | 1080 | 0 | 0 | 1080 | not audited |
| 2021-22 | 1230 | 0 | 0 | 1230 | not audited |
| 2022-23 | 1230 | 0 | 0 | 1230 | not audited |
| 2023-24 | 1230 | 0 | 0 | 1230 | not audited |
| 2024-25 | 1230 | 5 | 0 | 1230 | 5 |

## 12. Regression checks and reproducibility

All **45 earlier-season comparisons** pass exact values/dtypes: team games, canonical games, outcomes, team features and game features for each of nine seasons. Earlier per-season files were not rewritten and keep their SHA-256. Earlier combined slices match their saved Stage 1C snapshots. The five 2023–24 outputs still match protected Stage 1A/B values, dtypes and deterministic Parquet hashes exactly. All 94 files in the Stage 1D before-snapshot remain unchanged, including all original raw caches, Stage 1C evidence and per-season artifacts; the older 32-file Stage 1C protection gate also passes.

Run from the active subproject:

```sh
.venv/bin/python scripts/build_reconciled_multiseason.py
.venv/bin/python -m unittest discover -s tests -v
```

Use this Stage 1D entry point for the current reconciled dataset. Legacy Stage 1C commands intentionally do not apply external mappings and would reproduce the older quarantine result. The Stage 1D script has no network option. Two complete rebuilds with `socket.socket` blocked produced identical build manifests and output hashes. Evidence: `replay_verification.json`, `build_manifest.json`, `regression_pre_2024_25.json` and `regression_2023_24.json`. The manifest records code, raw, requirement and reconciliation-input checksums; pinned dependencies are unchanged.

## 13. Tests

Final suite: **71 tests passed** (57 existing plus 14 new). Tests cover raw/input immutability, explicit-only mapping, exact authoritative sides, reciprocal/full-season validation, preserved scores/WL/MATCHUP, restored rolling histories, earlier-feature invariance under later reconciliation, earlier-season regression, unresolved/conflicted rejection, separate neutrality metadata, invalid date/raw-label evidence, duplicate evidence and unrelated validation failures.

The existing Stage 1C historical quarantine test retains all assertions, but reads its preserved Stage 1C combined snapshot rather than the newly admitted current combined output. This is a versioned fixture-path update, not removal of a quarantine rule. Actual final results and socket-blocked execution are in `stage1d_tests.txt` and `test_run.json`.

## 14. Remaining limitations

The schedule is an authoritative independent representation, but shares the NBA publisher with LeagueGameLog. Retrieval is retrospective and does not certify publication timestamps on original game days. Current snapshot mapping does not establish a universal neutral-game MATCHUP convention. Earlier neutrality coverage is incomplete. The underlying raw source discrepancy remains intact and requires this explicit layer on every reconciled rebuild. Checksums detect accidental modification; they are not an operating-system write lock or a digital signature from the NBA. Historical source accuracy beyond checked identities/structure retains prior-stage limitations.

## 15. Final 2024–25 admission decision

**Admit 2024–25** for the existing date-based V1 dataset contract. All five designations are authoritative, all 1,230 games pass structural validation, and all 82 games per team enter feature history. It is suitable as the proposed out-of-time pre-holdout test once Stage 2 is separately approved. This is a data-quality admission, not a model-performance claim.

## 16. Recommended Stage 2 temporal split

- Training: 2015–16 through 2022–23 — 9,519 games.
- Validation/development: 2023–24 — 1,230 games.
- Out-of-time pre-holdout test: 2024–25 — 1,230 games.
- Final holdout: 2025–26 — untouched; no count or outcome inspected.

No fitting, metrics or tuning occurred. If the pre-holdout test is repeatedly used for model selection, it becomes development evidence; the final holdout must remain reserved.

## 17. Stage 1D exit criteria

Pass requires the authoritative five-game mapping, unchanged raw/evidence, a separate explicit layer, all 1,230 games validated with complete feature histories, unchanged earlier seasons, all old/new tests passing, no outcomes in features, untouched holdout and a full offline replay. Final evidence confirms these gates. No Stage 2 work has started.
