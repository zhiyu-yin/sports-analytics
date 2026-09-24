# Stage 0 — NBA game prediction data audit

Audit date: 2026-09-23 America/New_York (request timestamps are 2026-09-24 UTC).

## 1. Objective and decision

Design a reproducible dataset for **P(home team wins | information available before tip-off)**. This stage audits access, schemas, and temporal availability; it does not train a model, calculate prediction metrics, or build a full feature table. Chemistry remains paused.

**Finding:** live NBA retrieval failed in this environment. Upstream recorded samples were accessible and exposed schema and consistency risks; no live endpoint can yet be called reliable.

The preferred core is team game logs paired into one row per game, with schedule metadata for timing and venue. Advanced statistics are optional enrichment. An endpoint accepting a season parameter does not establish historical completeness. Local access findings and documentation claims are distinguished throughout.

## 2. Repository structure

Project root: `/Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/`.

```text
sports-analytics/
├── basketball/nba/
│   ├── game-prediction/
│   │   ├── docs/
│   │   │   ├── stage0_data_audit.md
│   │   │   └── stage0_evidence/  # actual small request evidence
│   │   ├── stage0_probe.py
│   │   ├── stage0_followup.py
│   │   ├── stage0_fixtures.py
│   │   └── stage0_inspect.py
│   └── chemistry/docs/
├── soccer/
├── shared/
├── README.md
└── .gitignore
```

Only evidence needed for this audit supplements the requested structure. Empty directories exist locally; Git does not retain empty directories. No notebooks, models, commits, or pushes were created. No unrelated project files were changed.

## 3. Local environment audit

Before creation, the parent `proj/` existed and `sports-analytics/` did not. The initial tool working directory was a different folder (`/Users/zhiyuyin/Documents/ChatGPT/New project`); all deliverables were deliberately placed at the requested path. No AGENTS.md was found at the checked home/Documents/requested-parent ancestry locations.

| Check | Observation |
|---|---|
| Python | 3.10.8, Clang 14.0.0 |
| Executable | `/opt/homebrew/opt/python@3.10/bin/python3.10` |
| pandas / numpy / nba_api / requests | All absent from this interpreter, checked with `importlib.util.find_spec` |
| Environment modifications | No package installation and no global environment changes |
| Probe tooling | Python standard library plus curl; direct calls to endpoints exposed by nba_api |
| Initial network check | Sandboxed curl could not resolve raw.githubusercontent.com (exit 6) |
| Network diagnosis | Approved network execution successfully retrieved GitHub sources; subsequent NBA access results are recorded separately |

The inspected upstream [pyproject.toml](https://github.com/swar/nba_api/blob/master/pyproject.toml) declared nba_api 1.11.4, Python >=3.10, numpy >=1.26 on Python 3.10, pandas >=2.1, and requests >=2.32.3,<3.0. Python compatibility is plausible; package installation/import behavior was not tested. Stage 1 should use an isolated environment with a recorded dependency lock.

## 4. Data sources investigated

NBA Stats is the upstream service; nba_api is its community-maintained Python client, **not an independent data source or a service availability guarantee**. Public access does not imply unrestricted redistribution. Review the source's terms before distributing raw datasets.

The [NBA Stats FAQ](https://www-ng.nba.com/stats/help/faq) states base-stat coverage from 1946-47 and advanced-stat coverage from 1996-97. These are site-wide claims, not verified endpoint-by-endpoint completeness guarantees. Modern seasons are the practical initial target.

| Source / endpoint | Grain and useful fields | Coverage evidence | Current test / scale judgment | Leakage concern |
|---|---|---|---|---|
| [LeagueGameLog](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguegamelog.md) | One team-game with PlayerOrTeam=T; IDs, date, MATCHUP, WL, PTS, shooting, rebounds, turnovers, PLUS_MINUS | Season/date filters documented; two-day 2023-24 probe | See request ledger; best core candidate if access restored; one season request can return both teams | All target-game box-score values are outcomes, not pre-game features |
| [LeagueGameFinder](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/leaguegamefinder.py) | Team-game when PlayerOrTeam=T; IDs, date, matchup, scores and box score | Recorded January 2021 response inspected; no full-season coverage established | GitHub fixture accessible; live endpoint not called; date slicing needs completeness checks | Outcome filters and same-game box scores can leak; two recorded consistency conflicts |
| [TeamGameLog](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/teamgamelog.py) | One team-game for a selected team; Game_ID, GAME_DATE, MATCHUP, WL, PTS, W/L/W_PCT | Season/date filters; Denver opening-range probe | See ledger; 30 team requests per season less efficient than league logs | Cumulative records may include current game; normalize field casing |
| [ScheduleLeagueV2](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/scheduleleaguev2.py) | One game in SeasonGames, plus separate SeasonWeeks; home/away IDs, UTC/EST times, status, score, postponedStatus, isNeutral | Season parameter documented; earliest complete season not verified | Documentation inspected, not directly tested; season batching attractive | Retrospective schedule changes, scores, wins/losses, leaders, seeds |
| [ScoreboardV3](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/scoreboardv3.py) / historical ScoreboardV2 | Daily games plus team line scores; identifiers, status, teams, scores | Date parameter; V2 tested on 2023-10-24 | See ledger; daily pulls cost more than season logs | Retrospective standings, season leaders, final scores |
| [LeagueDashTeamStats](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/leaguedashteamstats.py), MeasureType=Advanced | One team aggregate over requested dates; expected OFF_RATING, DEF_RATING, NET_RATING, PACE, TS_PCT, EFG_PCT, rebound/turnover rates | Site claims advanced data since 1996-97; two-day probe attempted | See ledger; snapshot per prediction date would be costly; prefer prior game-level inputs | DateTo must precede target; full-season aggregates contain future games |
| Same endpoint, MeasureType=Four Factors | One team/date-window aggregate; expected EFG_PCT, FTA_RATE, TM_TOV_PCT, OREB_PCT and opponent equivalents | Two-day probe attempted; precise field availability unverified | See ledger; optional enrichment | Target-game contributions and ambiguous denominator definitions |
| [BoxScoreAdvancedV3](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/boxscoreadvancedv3.md) | Team-game and player-game tables; offensiveRating, defensiveRating, possessions, pace, effectiveFieldGoalPercentage | Documentation inspected; per-version historical coverage unverified | No live call; one recorded response inspected; one request per game is more expensive | Prior completed games only; estimates and official ratings differ |
| [BoxScoreFourFactorsV3](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/boxscorefourfactorsv3.md) | Team/player game; effectiveFieldGoalPercentage, freeThrowAttemptRate, teamTurnoverPercentage, offensiveReboundPercentage, opponent counterparts | Documentation inspected; coverage unverified | No live call; one recorded response inspected; docs contain mixed legacy uppercase and V3 camelCase examples, so do not hard-code from prose | Target game forbidden; schema and formula validation required |
| [LeagueDashLineups](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashlineups.md) | One player group/team/date-window aggregate; GROUP_ID, GROUP_NAME, TEAM_ID, MIN, GP and statistics | Season/date and GroupQuantity filters; exact earliest season unverified | Docs only; high cardinality, sparse minutes; defer with chemistry | Actual target-game lineup/minutes known after tip-off; full-season lineup ratings leak |
| [LiveData boxscore](https://github.com/swar/nba_api/blob/master/docs/nba_api/live/endpoints/boxscore.md) on cdn.nba.com | One game object with explicit homeTeam/awayTeam, players and statistics | One historical 2023 game requested; no archive guarantee | See ledger; useful cross-check, per-game cost | Starter/played/injury annotations from final box score are retrospective |
| LiveData play-by-play; [PlayByPlayV3](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/playbyplayv3.py) | One game event/action, period, clock, team/player, score | One historical CDN game requested; Stats V3 not tested | See ledger; event volume and correction complexity make this unnecessary for Stage 1 | Target-game events are prohibited inputs; corrected event timestamps are not publication history |

Current [nba_api release notes](https://github.com/swar/nba_api/releases) document header fixes, restoration of TeamGameLog, and important endpoint changes: PlayByPlayV2 is deprecated; ScoreboardV2 has empty line scores for 2025-26 and should be replaced by V3. BoxScoreSummaryV2 has a post-2025-04-10 availability warning. Consequently older examples are not a reliable current implementation guide.

No stable documented requests-per-second allowance was verified. Use conservative serial requests, persistent caching, explicit timeout, bounded exponential backoff for transient failures, and stop on persistent access denial. Never equate HTTP 200 with complete valid data. No proxy rotation or anti-bot bypass is proposed.

## 5. Actual API/sample tests

See `stage0_evidence/manifest.json` for exact URLs, UTC timestamps, curl exit codes, response status, elapsed time, response bytes and SHA-256 checksums where a body exists. `stage0_probe.py` records raw returned bodies rather than constructing synthetic API samples. Requests use 18-second timeouts and one-second spacing; no bulk historical download. Direct HTTP probing does not establish that the Python wrapper itself works.

| Probe | HTTP / curl exit | Seconds | Result |
|---|---|---:|---|
| leaguegamelog_2023_opening | 000 / 28 | 18.02 | Timeout; zero response bytes |
| teamgamelog_den_2023_opening | 000 / 28 | 18.04 | Timeout; zero response bytes |
| teamstats_advanced | 000 / 28 | 18.04 | Timeout; zero response bytes |
| teamstats_four_factors | 000 / 28 | 18.03 | Timeout; zero response bytes |
| scoreboard_2023_opening | 000 / 28 | 18.02 | Timeout; zero response bytes |
| live_boxscore_0022300061 | 403 / 0 | 0.07 | Access Denied HTML; not NBA data |
| live_playbyplay_0022300061 | 403 / 0 | 0.09 | Access Denied HTML; not NBA data |
| leaguegamelog_current_headers | 000 / 28 | 25.02 | Timeout; zero response bytes |

**Live retrieval did not work.** Six Stats requests (five initial probes plus one current-header retry) timed out; two CDN requests returned access-denied HTML. No HTTP 429 was observed, so rate limiting was not diagnosed. The final retry used the maintained Chrome 145-style headers and a 25-second timeout, also without success. These outcomes do not prove global failure or nonexistent historical data. ScoreboardV3 was documentation-reviewed but not called; do not mistake its predecessor's failed probe for a V3 test.

**Recorded-source fallback:** Four small response bodies were retrieved from upstream nba_api VCR test cassettes hosted on GitHub: Lakers January 2024 TeamGameLog; January 2021 league team-game results from LeagueGameFinder; and one game's AdvancedV3 and FourFactorsV3 responses. These are upstream recordings, not freshly queried NBA data and not independently verified immutable historical snapshots. See [fixture provenance](stage0_evidence/fixture_provenance.json) for exact URLs, original request parameters, retrieval times and content hashes. Only response bodies were retained, with no replay of recorded request cookies. GitHub was accessible in these tests; NBA endpoint reliability remains unestablished.

`stage0_fixtures.py` retrieves these narrowly selected fixtures and rejects unrecognized encodings. `stage0_inspect.py` performs offline schema and join checks. `stage0_followup.py` records the final header diagnostic. No final-holdout fixture was fetched. Re-running network scripts can overwrite evidence; preserve this audit snapshot before rerunning. Sources on master can change, so compare the recorded hashes.


## 6. Available fields and sample schemas

### Observed recorded samples (not live API success)

[inspection_summary.json](stage0_evidence/inspection_summary.json) contains full observed column lists, JSON-native types, per-column null counts, example rows, team statistics and failed checks. No pandas dtype inference was performed.

| Recorded response | Observed size / coverage | Missingness and identifiers |
|---|---|---|
| TeamGameLog | 15 Lakers team-game rows, January 2024, requested season 2023-24 | Zero JSON null cells across 27 columns; Team_ID=1610612747; string Game_ID and human-readable date |
| LeagueGameFinder | 444 team-game rows / 222 games, 30 teams, 2021-01-01–2021-01-31; SEASON_ID=22020 | Zero JSON null cells across 28 columns; no duplicate (GAME_ID, TEAM_ID); date string YYYY-MM-DD |
| BoxScoreAdvancedV3 | Game 0022200552, two team objects plus nested players | No null team statistics; home 1610612739 CLE, away 1610612741 CHI; response metadata recorded 2026-02-20 |
| BoxScoreFourFactorsV3 | Same game, two team objects plus nested players | No null team statistics; response metadata recorded 2026-02-22 |

TeamGameLog's observed columns:

```text
Team_ID Game_ID GAME_DATE MATCHUP WL W L W_PCT MIN FGM FGA FG_PCT
FG3M FG3A FG3_PCT FTM FTA FT_PCT OREB DREB REB AST STL BLK TOV PF PTS
```

Example: game `0022300669`, `JAN 30, 2024`, `LAL @ ATL`, PTS=122, WL=L, cumulative W=24, L=25. The previous row is January 29, W=24, L=24: the January 30 loss is already included. **The returned cumulative record is post-game and unsafe as that game's pre-game record.** Rows arrive newest first and must be sorted before shifting.

LeagueGameFinder's observed columns:

```text
SEASON_ID TEAM_ID TEAM_ABBREVIATION TEAM_NAME GAME_ID GAME_DATE MATCHUP WL
MIN PTS FGM FGA FG_PCT FG3M FG3A FG3_PCT FTM FTA FT_PCT OREB DREB REB
AST STL BLK TOV PF PLUS_MINUS
```

Example pair: `0022000311`, 2021-01-31: Minnesota (1610612750), `MIN vs. CLE`, 109 points, W; Cleveland (1610612739), `CLE @ MIN`, 104 points, L. Thus the game appears twice in team-level data; pair by game ID and identify home via MATCHUP. All 222 recorded games have two distinct teams, exactly one home/away row, reciprocal abbreviations and matching dates. **Structural joins succeed, but two games fail score/plus-minus consistency**:

- `0022000291`: NYK 102, CLE 81, but PLUS_MINUS is +18/-18 instead of +21/-21.
- `0022000106`: POR 108, CHI 111, but POR PLUS_MINUS is +1 instead of -3.

Do not silently repair these upstream recordings or assume that production responses share the problem. Preserve the conflict, quarantine questionable fields/rows, and reconcile with an independent authoritative box score before inclusion. PLUS_MINUS is not a safe shortcut for final score difference even apart from leakage. The fixture sample establishes pairing mechanics, not January completeness.

Observed types: IDs for teams and box-score counts are JSON integers; game/season IDs and dates are strings; percentages and LeagueGameFinder PLUS_MINUS are floats. MIN includes values such as 239 and 241; do not assume every regulation team total is exactly 240 in source data. Percentages require interpretation, not dtype alone.

The AdvancedV3 home team has offensiveRating=134.3, defensiveRating=122.9, pace=98.26, possessions=108.0, effectiveFieldGoalPercentage=0.609; minutes is the string `265:00`. **Suspicious estimated fields** include estimatedOffensiveRating=671.3 and estimatedPace=19.65. These need reconciliation; do not mix estimated and non-estimated ratings or use the suspicious values as trusted features.

FourFactorsV3 home statistics contain effectiveFieldGoalPercentage=0.609, freeThrowAttemptRate=0.489, teamTurnoverPercentage=0.093, offensiveReboundPercentage=0.269 and opponent counterparts. AdvancedV3 turnoverRatio=9.3 while FourFactors teamTurnoverPercentage=0.093: the schema mixes percentage-point and fractional scales across fields. Validate units explicitly. All are **post-game summaries**; future features may use only prior completed games. Full observed team-stat field lists are preserved in inspection_summary.json.


The documented LeagueGameLog column list (not a successfully observed schema unless the ledger says otherwise) is:

```text
SEASON_ID TEAM_ID TEAM_ABBREVIATION TEAM_NAME GAME_ID GAME_DATE MATCHUP WL
MIN FGM FGA FG_PCT FG3M FG3A FG3_PCT FTM FTA FT_PCT OREB DREB REB
AST STL BLK TOV PF PTS PLUS_MINUS VIDEO_AVAILABLE
```

Expected normalization: game and season identifiers to strings; TEAM_ID to integer or consistently normalized string; GAME_DATE to date; counts to nullable integers; percentages to nullable floating point. Game IDs must retain leading zeros. Missingness and inferred pandas dtypes for failed requests are **unknown**, not zero or validated. A raw JSON null check also does not detect every sentinel or semantically missing value.

In league team logs, the expected pattern is two team records per completed game: `AAA vs. BBB` for designated home and `BBB @ AAA` for away. Pair by GAME_ID, not date/name; require two distinct team IDs and exactly one of each side. Cross-check explicit schedule home/away IDs, shared date, reciprocal opponent identity, scores and complementary W/L. Reject duplicate `(game_id, team_id)` rows and incomplete pairs rather than silently dropping one. TeamGameLog for a single team alone cannot establish league-level pairing. The recorded LeagueGameFinder sample validates structural pairing, but the two score conflicts above remain unresolved and live-source validation is still required.

## 7. Recommended canonical game table (design only)

| Category | Column | Type / rule |
|---|---|---|
| Identity | game_id | String primary key; retain leading zeros |
| Identity | league_id, season, season_type | Strings; explicit regular-season scope |
| Identity | game_date | NBA schedule-local date; do not derive blindly from UTC date |
| Timing | scheduled_tipoff_utc, actual_tipoff_utc | UTC timestamps, actual may be missing; distinguish scheduled from actual |
| Timing | prediction_cutoff_utc | Fixed operational prediction timestamp strictly before tip-off |
| Identity | home_team_id, home_team_name | Stable identifier; name is descriptive |
| Identity | away_team_id, away_team_name | Different stable identifier; name is descriptive |
| Context | is_neutral, game_status | Venue/status metadata; status for eligibility, not a predictor |
| Provenance | source, retrieved_at_utc, raw_sha256, schema_version | Traceability; do not feed into a model |
| Feature provenance | feature_asof_utc / maximum_input_available_at | Must be <= prediction cutoff and strictly before game start |
| Future features | home_*_pregame, away_*_pregame, selected differences | Nullable numeric values, explicit window/sample count |
| Target | home_win | Nullable boolean; 1 iff final home score exceeds final away score; only for completed eligible games |

Keep final home/away points in a separate outcome/staging table for target derivation and checks. If retained alongside features, explicitly denylist them from the model matrix. Do not interpret a scheduled game's zero score as a loss. Overtime games have a valid final binary outcome; canceled/postponed/unplayed games do not. Neutral-site designated home is not ordinary home-court advantage.

## 8. Leakage Rules

**For game G at time T, every feature must be computable using information available strictly before game G begins.** Use a reproducible prediction cutoff before T, not an arbitrary retrospective snapshot.

Unsafe inputs include points, FG%, turnovers, end-of-game plus-minus, final pace/ratings, or any event from the target game; full-season aggregates containing future games; unshifted rolling statistics; retrospective standings that include the target game; future injuries, confirmed participation, actual starting lineups, or minutes learned after the cutoff; and random train/test splits mixing future and past games.

Conceptual rolling pattern, after sorting within each team by time:

```python
# Concept only; not implemented during Stage 0.
historical_value.shift(1).rolling(window=window, min_periods=min_history).mean()
```

Apply shift **within each team**, preserving index alignment; a global shift can transfer another team's data. Require source games to have finished and their data to be available before the cutoff. If only dates are trusted, use games from strictly earlier local dates rather than assuming an order for same-day events. A chronological game ID sort alone is insufficient. Deliberately define season resets, offseason carryover, warmup windows and minimum histories; never backfill early-season features from future games.

DateFrom/DateTo are typically day filters, not point-in-time publication controls. Inclusive DateTo equal to the target date is unsafe. LastNGames retrieved today is not a historical rolling window. Aggregate percentages from prior numerators and denominators where appropriate, not an unexplained mean of daily percentages. A historical game's corrected final box score may differ from what was published immediately after that game; current endpoints generally do not prove revision-time availability. Disclose that limitation and preserve future snapshots.

Fit imputers, scaling, feature selection, calibration and model parameters using training data only. Hyperparameters may be selected with temporally later validation, never final test outcomes. Fit the naive home prior on training only. Elo updates, later, occur after each completed game. Identifiers are join keys rather than automatically legitimate numeric predictors. Keep both team rows for the same game in the same temporal partition.

## 9. Temporal evaluation design

Provisional target, **not a finalized claim of retrieved coverage**:

| Window | Role |
|---|---|
| 2014-15 through 2023-24 | Candidate training pool; expanding season-based internal validation within this pool |
| 2024-25 | Development/validation for model choice, features and calibration design |
| 2025-26 | Reserved final out-of-time holdout |

The NBA's [2025-26 schedule announcement](https://pr.nba.com/2025-26-nba-regular-season-schedule/) scheduled the regular-season end for April 12, 2026. This precedes this audit, but a scheduled end does not establish complete API data. **2024-25 and 2025-26 row-level completeness were not verified.** No holdout outcomes were intentionally fetched or examined in this audit. Before finalizing splits, Stage 1 must verify season coverage with metadata/counts and a declared scope, with final-test outcomes isolated from development analysis. Do not silently replace a missing holdout with a previously tuned season.

Start with regular-season games only. Explicitly handle NBA Cup games that count in regular-season records and exclude the Cup championship; exclude preseason, All-Star, play-in and playoffs until separately scoped. Bubble/neutral games and shortened seasons require flags and season-specific expected counts; do not assume 1,230 every year. Dates must be actual played dates for temporal ordering, while pre-game schedule features must use the schedule known then.

Temporal splitting estimates deployment into a future season and prevents future team strength and preprocessing information flowing backward. After selection, a fixed recipe can be refit on training plus validation before a single final evaluation. During sequential holdout prediction, previously completed holdout games may update predeclared rolling state/Elo, but cannot drive tuning or opportunistic refitting. Freeze that policy before opening outcomes. Reserve reporting by season and uncertainty estimates clustered by date/season as appropriate.

## 10. Candidate feature families

Future candidates only: training-derived home prior; pre-game Elo; shifted recent/season win percentage and point differential; offensive/defensive efficiency and pace; eFG%, turnover rate, offensive rebound rate and free-throw attempt rate; rest days, back-to-back and recent schedule density; designated home/neutral venue context. Use symmetric home/away values and optionally their differences.

Specify Four Factors denominators explicitly: eFG%=(FGM+0.5*FG3M)/FGA; ORB%=OREB/(OREB+opponent DREB); FT attempt rate=FTA/FGA if matching that chosen convention. Turnover-rate and possession formulas vary; match the selected source's definition and label estimates. Zero denominators require missingness rules. Rest days should have a documented calendar/timezone definition (e.g. intervening local dates), while hours since previous final is a different feature. Player availability/injuries need timestamped archives before inclusion. No feature values were calculated here.

## 11. Planned baseline/model progression

1. Baseline 0: training-derived constant home-win prior / naive probability baseline.
2. Baseline 1: chronological Elo.
3. Baseline 2: logistic regression with leakage-safe rolling team features.
4. Baseline 3: gradient boosting, only after simpler baselines are validated.
5. Later: timestamped injuries/player availability, player strength and lineup features.
6. Separate later benchmark: our probability versus timestamp-matched market implied probability, with bookmaker margin handled explicitly.

Market odds are excluded from the initial basketball-information model. Chemistry stays paused. None of these models was implemented or trained.

## 12. Evaluation metrics

Primary metrics: **log loss**, **Brier score**, and **calibration**. Log loss penalizes confident wrong probabilities strongly; Brier score is mean squared probability error. Lower is better for both. Calibration asks whether forecast probabilities match observed frequencies: among many home teams given roughly 70% probability, about 70% should win. Use reliability plots with bin counts and uncertainty, not an unsupported claim from tiny bins.

Secondary metrics: accuracy at a predeclared threshold and ROC-AUC for ranking. Accuracy discards probability quality; AUC does not establish calibration. Report comparisons against the same-period naive baseline, with season/sample counts. No metrics were computed in Stage 0.

## 13. Known API/data risks

- Access is environment-dependent; timeout is not proof of global outage, endpoint removal, rate limiting, or absent historical games.
- Documentation can be stale; release changes and inconsistent Four Factors examples require schema checks on real responses.
- Single-game success cannot prove season completeness or production reliability.
- Revisions, schedule changes, date/timezone ambiguity and unarchived injury publication times limit strict historical as-of claims.
- Team names/abbreviations change; preserve stable IDs and explicit season identity.
- Both sides of team logs, nullable results, canceled games and duplicate requests need assertions before pairing.
- Per-game box scores and play-by-play are more expensive than season-level game logs; advanced aggregate endpoints are not a substitute for historical point-in-time data.
- Store raw data locally by default; review redistribution terms before publishing samples or datasets.

## 14. Open questions / acceptance gates

Can NBA Stats be accessed consistently from the intended runtime with current client headers? Which recent seasons are complete for league game logs and schedule UTC times? How far back do CDN archives remain accessible? Can known-before-tip-off injury/schedule snapshots ever be obtained? What cutoff (e.g. a fixed offset before scheduled tip-off) should define the deployed prediction product? How should neutral games, season resets, shortened seasons and delayed games be treated? These are unresolved decisions, not fabricated completeness findings.

## 15. Recommended Stage 1 scope

Build a small, reproducible ingestion and validation layer **before any model**:

1. Resolve access using the current maintained client in an isolated environment; if still unavailable, document the block and evaluate a licensed, versioned alternative with known provenance rather than adding brittle bypasses.
2. Fetch one development season only (2023-24), cache raw responses with parameters/timestamps/checksums, and validate date bounds, eligibility, counts and missingness.
3. Normalize team logs; enforce unique `(game_id, team_id)`, exactly two teams and one designated home per game; reconcile schedule and scores; construct the canonical identity/target table.
4. Verify timing semantics, one-to-one joins and actual historical coverage. Finalize temporal split metadata while reserving holdout outcomes.
5. Specify and test feature-availability contracts: adding future games or changing the target-game box score must not change that game's pre-game features. Then implement only a small set of shifted team features in the subsequent agreed scope.

Exit criteria: deterministic cached re-run, source/schema manifest, reconciled game counts, clear rejects/missingness, validated join and timestamp invariants, and a documented holdout policy. Training remains a later stage.
