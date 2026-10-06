# Stage 0 — Anthropometrics × Shooting Data Availability Audit

Audit date: September 28, 2026. **Decision: strict Stage 0 has not yet passed. Archive-based FT feasibility is demonstrated; official historical-source validation remains open.** All numerical findings below concern availability, data quality or joins, never an association between wingspan and shooting.

Evidence labels: **Observed** = retrieved and inspected data; **Documentation** = published interface or source statement; **Assumption** = a provisional design choice; **Future** = work not executed. Secondary archives are labeled explicitly; they are not live NBA responses.

## 1. Objective

Establish which measurements and shooting counts can be obtained, their grain and history, how identities join, what coverage is lost, and which outcomes deserve Stage 1. No final statistical models, hypothesis tests, correlations or scientific effect claims. This independent subproject makes no changes to frozen NBA Game Prediction V1.

## 2. Research question

Is relative wingspan associated with shooting performance in NBA players after accounting for body size, position/role, shot type and other relevant context? This is an **associational** question. NBA selection and role allocation preclude a simple causal interpretation.

## 3. Anthropometric sources

**Preferred primary source:** [NBA combine anthropometrics](https://www.nba.com/stats/draft/combine-anthro), through `draftcombineplayeranthro` or `draftcombinestats`. [nba_api's endpoint documentation](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/draftcombineplayeranthro.md) identifies the interface; nba_api is a client, not an independent measurement source. Request `LeagueID=00`, `SeasonYear=YYYY` (four digits).

**Observed:** corrected combine probes for 2000, 2009, 2013, 2022, 2025 and 2026 all timed out with no response bytes. Initial exploratory requests using YYYY-YY were also unsuccessful and are preserved, but are not valid coverage tests. `draftcombinestats` initial tests also used the season-label form; its live coverage remains unvalidated. Endpoint failure is not evidence of zero measured players. All request parameters, timestamps, errors and raw hashes where bytes exist are in the evidence logs.

**Observed secondary fallback:** [ianstack's combine archive](https://github.com/ianstack/NBA-Draft-Combine-Analysis), pinned to the revision recorded in `archive_sources.json`. Its `nba_draft_data.csv` contains 1,552 rows spanning 2000–2022. The publisher describes collection through py_ball from NBA Stats. That upstream provenance is a publisher claim, not independently established for every row. Numeric checks and real ID joins validate its utility for a feasibility audit, but do not certify it as a definitive measurement source.

**Official corroboration:** the [Andrew Nembhard](https://www.nba.com/draft/2022/prospects/andrew-nembhard) and [Nikola Jovic](https://www.nba.com/draft/2022/prospects/nikola-jovic) prospect pages were retrieved successfully. Their shoe-height and wingspan values agree with the archive: respectively 76.5/77.75 inches and 83/84.25 inches. Rounded weights also agree. These two spot checks do not validate barefoot height or all historical records.

The [official AWS Combine Data Hub](https://combine.nba.com/) and its public application bundle were retrieved. It uses an embedded dashboard interface; no downloadable measurement table, identifier mapping or historical range was validated. Its existence is not evidence of complete historical coverage. Prefer the Stats interfaces for reproducible tabular acquisition if access recovers.

## 4. Combine coverage

**Observed archive:** 23 combine years, 1,552 records, 1,517 distinct positive IDs plus five records with a missing-ID placeholder (`-1`). There are **1,508 complete, positive, plausible height/wingspan rows representing 1,480 distinct measured entities**: 1,475 positive IDs plus five separately named missing-ID records. Distinct entities here are an audit identity approximation, not an official player census.

Twenty-eight complete-measurement IDs occur in two years; no duplicate player/year keys were found. Retain all source measurements. The prototype uses the earliest complete record on or before the NBA season; Stage 1 must explicitly decide how to handle repeated measurements.

| Combine year | Records | Complete height + wingspan rows | Missing pair rate | IDs observed in NBA after combine* |
|---|---:|---:|---:|---:|
| 2000 | 65 | 65 | 0.0% | 5 |
| 2001 | 78 | 78 | 0.0% | 20 |
| 2002 | 82 | 82 | 0.0% | 16 |
| 2003 | 78 | 78 | 0.0% | 27 |
| 2004 | 81 | 79 | 2.5% | 23 |
| 2005 | 81 | 80 | 1.2% | 32 |
| 2006 | 76 | 76 | 0.0% | 23 |
| 2007 | 77 | 76 | 1.3% | 30 |
| 2008 | 76 | 76 | 0.0% | 22 |
| 2009 | 46 | 46 | 0.0% | 40 |
| 2010 | 52 | 52 | 0.0% | 41 |
| 2011 | 54 | 54 | 0.0% | 42 |
| 2012 | 61 | 61 | 0.0% | 54 |
| 2013 | 63 | 62 | 1.6% | 52 |
| 2014 | 56 | 56 | 0.0% | 45 |
| 2015 | 58 | 58 | 0.0% | 44 |
| 2016 | 56 | 56 | 0.0% | 50 |
| 2017 | 64 | 63 | 1.6% | 57 |
| 2018 | 69 | 69 | 0.0% | 57 |
| 2019 | 77 | 70 | 9.1% | 64 |
| 2020 | 45 | 45 | 0.0% | 41 |
| 2021 | 74 | 65 | 12.2% | 56 |
| 2022 | 83 | 61 | 26.5% | 49 |

*The last column searches only the retrieved **2010-11–2023-24** positive-minute box scores, by exact ID. It is a lower bound on NBA participation, not the number who ever reached the NBA. Old cohorts are left-truncated; recent cohorts have limited follow-up. Conflicting IDs remain unresolved. Missing-pair rates are within combine records, not within NBA rosters. No observed combine data before 2000 or after 2022 were retrieved. This does not establish that those years lack data.

## 5. Available anthropometric fields

The archive actually contains `SEASON`, `PLAYER_ID`, first/last/full name, `POSITION`, barefoot and shoe height, wingspan, standing reach, weight, hand length and hand width. Full original headers are in `combine_schema.json`. CSV values are text that parse into numeric inches (linear measurements) and pounds (weight); height, span and reach also have feet/inches display columns. Official anthro documentation additionally lists `TEMP_PLAYER_ID`; never use that as a stable NBA join key. Archive year is a calendar combine year.

| Field | Missing archive rows |
|---|---:|
| HEIGHT_WO_SHOES | 44 / 1,552 (2.8%) |
| HEIGHT_W_SHOES | 347 / 1,552 (22.4%) |
| WINGSPAN | 43 / 1,552 (2.8%) |
| WEIGHT | 46 / 1,552 (3.0%) |
| STANDING_REACH | 45 / 1,552 (2.9%) |
| HAND_LENGTH | 780 / 1,552 (50.3%) |
| HAND_WIDTH | 780 / 1,552 (50.3%) |

Use barefoot height consistently for candidate exposures. Do not substitute shoe height when barefoot height is missing without an explicit later sensitivity design. Position is a combine-time prospect label, often PG/SG/SF/PF/C or hybrids, not a current role measure.

## 6. Shooting sources

**Preferred:** `leaguedashplayerstats`, `PerMode=Totals`, regular season, provides documented player IDs, FTM/FTA/FT_PCT, FG3M/FG3A/FG3_PCT, FGM/FGA/FG_PCT, MIN, GP and AGE. Derive 2PM = FGM − FG3M and 2PA = FGA − FG3A; do not treat them as independently observed fields. [Endpoint documentation](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashplayerstats.md).

**Observed fallback:** three pinned partitions from [NocturneBear's public NBA box-score archive](https://github.com/NocturneBear/NBA-Data-2010-2024). They contain 424,478 player-game rows, including 73,069 rows without positive minutes, covering 2010-11–2023-24. Fields include `personId`, `personName`, season/date/game, minutes and integer makes/attempts. NBA-shaped field names alone do not prove source lineage. Raw responses and checksums are local; only summary evidence is published here.

No full joined analytical dataset was saved. Player-season aggregates were calculated in memory for feasibility counts, and only a 12-row joined prototype and local identity review tables were written.

## 7. Basic shooting coverage

**Documentation:** NBA describes base statistics extending to the league's early history in its [Stats FAQ](https://www.nba.com/stats/help/faq). Availability of every modern field across that history must be tested separately.

**Live tests:** `leaguedashplayerstats` for 2000-01, 2012-13, 2013-14, 2022-23 and 2025-26 all timed out. No live row count or missingness estimate is available.

**Observed archive:** 14 NBA seasons; 1,708 distinct players with positive minutes. Player-games can be aggregated to player-season and career-within-window grains. Career totals here are not lifetime totals. All three partitions are needed because each contains rows from multiple seasons. `match_rate_summary.csv` records season date bounds and observed game counts (990 in 2011-12, 1,059 in 2019-20, 1,080 in 2020-21, 1,229 in 2012-13 and 1,230 otherwise). These are observed counts, not proof against an independently verified schedule. Raw-row count and schema are in `shooting_schema.json`.

## 8. Catch-and-shoot coverage

`leaguedashptstats`, `PlayerOrTeam=Player`, `PtMeasureType=CatchShoot`, `PerMode=Totals` is the candidate interface. Tests covered 2000-01, 2012-13, 2013-14, 2022-23 and 2025-26: **all failed by timeout**, so observed sample rows, matched players and attempt volume are **unknown**, not zero.

Candidate count fields are `CATCH_SHOOT_FG3M` and `CATCH_SHOOT_FG3A`; actual returned headers and integer totals must be verified before use. The [generic nba_api page](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashptstats.md) shows a Team/SpeedDistance sample, which does not validate a Player/CatchShoot schema.

**Documentation:** [NBA's tracking announcement](https://pr.nba.com/nba-stats-llc-partnership/) places league-wide tracking deployment in 2013-14. Treat that as a plausible historical boundary to test, not proof that every current dashboard returns complete data from that season. Context history is potentially much shorter than basic box-score history.

## 9. Pull-up coverage and other context

`PtMeasureType=PullUpShot` was tested over the same five seasons and also timed out. Candidate fields are `PULL_UP_FG3M` and `PULL_UP_FG3A`; no live schema/count volume is validated. Both tracking outcomes are naturally player-season/shot-type summaries, potentially with team splits that must be checked.

| Candidate endpoint | Intended information / documented fields | Tested range | Observed result |
|---|---|---|---|
| `playerdashptshots` | Shot type, closest defender (including 10+ feet variants), dribbles, touch-time buckets; FG3M/FG3A and FGM/FGA | 2012-13, 2013-14, 2025-26 | All timeouts; rows unknown |
| `leaguedashplayershotlocations` | Player-season zone totals, including corner, above-break and midrange; nested zone headers | 2012-13, 2013-14, 2025-26 | All timeouts; rows unknown |
| `shotchartdetail` | PLAYER_ID, GAME_ID, GAME_EVENT_ID, LOC_X/LOC_Y, SHOT_DISTANCE, SHOT_ZONE_BASIC, SHOT_MADE_FLAG, SHOT_ATTEMPTED_FLAG | 2012-13, 2013-14, 2025-26 | All timeouts; rows unknown |

Player dashboard/event probes used Stephen Curry (`201939`), `TeamID=0`; shot charts requested `ContextMeasure=FGA` so a future successful response should include attempts, not only makes. Documented distance units/coordinate conventions still require source validation before physical interpretation. Shot charts do not establish historical defender, dribble or touch-time fields at event grain; marginal dashboards cannot be joined together as if they were joint shot-level context. No empty historical JSON response was observed—there was no successful JSON response. Live timeout fragility affects all these candidates.

## 10. Player identity / join strategy

Prefer positive NBA `PLAYER_ID` ↔ box-score `personId`. Preserve source IDs and names. Never match `-1` placeholders. `commonallplayers` was probed for 2025-26 with `IsOnlyCurrentSeason=0`, but timed out, so no independent NBA-ever denominator was obtained.

Join classes are exact ID, exact normalized name, manually reviewable, ambiguous and unmatched. Unicode accent and punctuation folding preserves suffixes. Name collisions are ambiguous; a unique normalized name with conflicting positive IDs is **manually reviewable**, never automatically accepted. No fuzzy matching. Current archive joins yield 21 such conflicting-ID cases, including Joe Ingles, Omer Yurtseven and Carsen Edwards; these are excluded pending documented crosswalk review. Name equality does not prove identity (e.g., Justin Jackson and Marcus Thornton).

There are 36 name differences even among exact-ID joins, including Enes Kanter/Enes Freedom, Edrice Adebayo/Bam Adebayo and missing suffixes. They are retained as exact-ID joins and logged locally for review; the audit has not independently certified every alias. Preserve accents, suffixes, punctuation and original names alongside normalized keys. A measurement record without observed NBA minutes may represent a non-NBA prospect or a career outside the retrieved window.

## 11. Small join prototype

`data/interim/join_prototype.csv` contains 12 real players, alphabetically selected among exact-ID matches in 2013-14. It includes player ID/name, combine year, barefoot height, wingspan, advantage, ratio, combine position, NBA season, FT/3P makes and attempts, and join status. Rebuild with `python3 scripts/audit_joinability.py`.

Schema-check example: player ID `201166`, combine year 2007, NBA season 2013-14, height 70 inches, wingspan 76 inches, advantage 6 inches, ratio 1.085714, FTM/FTA 83/95 and 3PM/3PA 96/248. This is a join illustration, not a scientific result. The prototype and identity review CSVs are Git-ignored; no bulk player payload is placed in docs.

## 12. Match rates

| Audit quantity | Observed value |
|---|---:|
| Combine rows | 1,552 |
| Complete measurement rows | 1,508 |
| Unique measured entities | 1,480 |
| NBA positive-minute players in archive | 1,708 |
| Exact-ID measured-player matches | 866 |
| Exact normalized-name matches | 0 |
| Manually reviewable conflicting IDs | 21 |
| Ambiguous joins | 0 |
| Unmatched measured entities | 593 |

The **measured-to-observed-NBA fraction is 866/1,480 = 58.5%**. It is not an identity-linkage success rate among players known to have reached the NBA. That desired denominator is unknown until an independent NBA-ever roster/crosswalk is available. A narrower 2013 combine cohort has 52/62 measured players observed by exact ID (83.9%), still a cohort participation fraction, not a validated linkage recall.

Reverse coverage is the fraction of NBA players in each season with an exact-ID complete measurement **on or before** that season:

| NBA season | NBA players | Measured players | Reverse coverage | Matched FT attempts |
|---|---:|---:|---:|---:|
| 2010-11 | 452 | 265 | 58.6% | 37576 |
| 2011-12 | 478 | 281 | 58.8% | 28788 |
| 2012-13 | 469 | 293 | 62.5% | 37372 |
| 2013-14 | 482 | 311 | 64.5% | 42587 |
| 2014-15 | 492 | 320 | 65.0% | 40830 |
| 2015-16 | 476 | 318 | 66.8% | 41364 |
| 2016-17 | 486 | 327 | 67.3% | 41291 |
| 2017-18 | 540 | 335 | 62.0% | 37001 |
| 2018-19 | 530 | 336 | 63.4% | 39204 |
| 2019-20 | 529 | 334 | 63.1% | 33636 |
| 2020-21 | 540 | 335 | 62.0% | 31190 |
| 2021-22 | 605 | 353 | 58.3% | 34287 |
| 2022-23 | 539 | 328 | 60.9% | 36672 |
| 2023-24 | 572 | 292 | 51.0% | 29882 |

This reverse quantity answers sample coverage. Its complement includes skipped/missing measurements, archive cutoff, identity problems and historical truncation—not solely combine nonparticipation. Coverage falls in 2023-24 partly because the combine archive stops in 2022.

## 13. Data quality findings

**Observed:** 44 missing barefoot heights, 43 missing spans, 44 incomplete pairs; 347 missing shoe heights. Five nonpositive ID placeholders are treated as missing, not merged. Twenty-eight repeated measured IDs across years; no duplicate player/year keys. Seventeen valid spans below height are retained. Review bounds are 60–96 inches for height and 60–108 for wingspan; none of the complete numeric pairs violated these broad bounds. These thresholds are prompts for review, not biological exclusion rules.

Four numeric/display discrepancies remain unresolved: wingspan for IDs 1629655, 1629672 and 1629023, and height for 1629675. The audit prototype uses numeric columns without silently correcting them; Stage 1 must reconcile these four pairs against original measurements. Feet/inches parsing accepts both double quotes and NBA double-apostrophe suffixes, rejects malformed strings and inches ≥12, and supports explicit cm-to-inch conversion. Original numeric and display values remain in raw data.

Across 424,478 box-score rows: no duplicate game/player keys, conflicting duplicates, makes > attempts, negative/noninteger counts or percentage disagreements above 0.00051 were detected. Positive-minute rows are used for player-season sums; DNP/zero-minute rows are not games played. Zero-attempt accuracy is missing, not zero. Percentages are recomputed from summed counts, never averaged. Player-season keys are unique by construction. Season labels and adjacent-year suffixes are checked. Full schedule/team totals reconciliation remains outstanding.

Box-score position is missing in 184,829 of 351,409 positive-minute rows (52.6%); the remaining labels look like lineup positions, not stable season roles. Therefore **combine position is easiest now**, while `commonplayerinfo` / `commonteamroster` are documented future sources to test for roster position. No modern role classification is currently validated. `data_quality_summary.json` and unit tests cover these checks.

## 14. Selection Bias Risks

### A. Combine participation bias

The measured sample is not random. Prospects may skip the combine or individual measurements. The archive cannot attribute a particular absence to skipping rather than missing ingestion, so do not label individual stars as nonparticipants without independent evidence. Missingness varies by year (26.5% incomplete pairs among 2022 archive records) and field.

### B. NBA survival / selection bias

Among players who reach or remain in the NBA, shorter-armed players may need stronger shooting or other compensating skills. Conditioning on NBA selection can therefore create a negative observed association even without a mechanically harmful effect of wingspan. This is a risk mechanism, not a finding in these data.

### C. Role selection

Longer players may be selected into interior/defensive roles with different shot opportunities. Combine position only approximates later role; it can change with age and team context.

### D. Shot-volume selection

Low-attempt percentages are noisy. Selecting high-volume shooters can itself change the target population. Report attempt-volume distributions and sensitivity thresholds rather than silently excluding low-volume players.

### E. Era effects

Shooting strategy, perimeter roles and measurement/tracking practices change over time. The sample mixes eras and has truncated follow-up. The 2023-24 reverse coverage drop also reflects archive age. No causal correction is attempted here.

## 15. Confounders and contextual variables

| Variable | Availability now | Limitation / next source |
|---|---|---|
| Height | Observed barefoot combine measure | Missing pairs and display disagreements |
| Position / role | Observed combine position | Time-invariant proxy; box-score position incomplete |
| Age | Potentially available | AGE documented in league player stats; no successful response |
| NBA experience | Potentially available | Career/roster/bio endpoints; cannot infer true experience from left-truncated archive |
| Season / era | Observed | Explicit NBA season |
| Shot volume | Observed FT/2P/3P counts | Could reflect selection or mediation as well as confounding |
| Minutes / games | Observed player-games | Positive-minute aggregation; reconcile with official season totals |
| Offensive role | Not currently available | No validated classification; combine position is insufficient |
| Shot type | Basic FT/2P/3P derivable | C&S/pull-up pending |
| Shot distance / location | Potentially available | Shot charts / zone dashboard pending |
| Defender distance | Potentially available | Player tracking buckets pending |
| Dribble count / touch time | Potentially available | Player tracking buckets pending |

This is a list of candidate adjustment/context variables, not a claim that every item is a pre-exposure causal confounder. Weight and hand dimensions are available for subsets but are not substitutes for missing role/context.

## 16. Simpson's paradox risk

A pooled negative relationship could shrink or disappear within guards, wings and bigs because the groups differ in size and shooting roles. That is an illustrative possibility, not an observed direction. Future EDA should compare pooled displays, position/role-stratified displays and adjusted regression. Avoid concluding from a pooled percentage scatterplot.

## 17. Candidate exposure definitions

Preserve all three; **no final exposure is selected at Stage 0**. Use barefoot height and wingspan in inches from the same combine record:

- Wingspan advantage = wingspan − height (inches).
- Wingspan ratio = wingspan / height (dimensionless).
- Residual wingspan = observed wingspan − expected wingspan from a later regression `wingspan = a + b × height + error`.

Residual wingspan is the preferred candidate to evaluate in Stage 1 because subtraction fixes the height slope to exactly 1, whereas residualization estimates it. This is a design preference, not a fitted or validated result. The ratio imposes its own scaling relationship and is not automatically height-independent. Future residualization must define its reference population, functional form and handling of repeated combines; if predictive validation is used, estimate that transformation inside training folds. No residual regression was fitted here. Advantage and ratio appear in the small schema prototype only.

## 18. Candidate outcome definitions

**First candidate:** free-throw makes out of attempts (`FTM`, `FTA`), standardized shot conditions and large observed volume. **Second/third candidates:** C&S three-point makes/attempts and pull-up three-point makes/attempts, pending source validation. Secondary outcomes: overall 3P, corner 3P, above-break 3P and midrange. Only overall FT/3P and basic 2P counts are currently observed in this audit. Do not use overall FG% as the primary outcome because location and role mix dominate its interpretation.

## 19. Statistical modeling implications — design only

80% could mean 4/5 or 400/500; these contain very different information. Prefer a later count likelihood `Makes_i ~ Binomial(Attempts_i, p_i)` rather than ordinary least squares on percentages alone. Zero-attempt rows carry no accuracy information. Consider overdispersion and clustering later.

Future model ladder: Model 0 descriptive relationship with relative wingspan; Model 1 adds height; Model 2 position/role; Model 3 age, experience and season; Model 4 volume/minutes; Model 5 validated shot context. Binomial/logistic formulations are preferred for count outcomes. Repeated player-seasons may require hierarchical player and season effects. Attempt denominators already influence precision; adding volume as a predictor changes the estimand and deserves a separate justification. None of this ladder was implemented or run.

## 20. FT-focused feasibility

**Observed secondary archives:** 866 exactly matched measured players, 4,428 player-seasons after measurement, **511,680 FT attempts** over 14 seasons. There are 2,738 player-seasons with ≥50 attempts and 1,833 with ≥100; these are exploratory volume summaries, not proposed eligibility requirements. Reverse coverage varies from 51.0% to 67.3%.

A useful narrower first panel is **2013-14**: 311 matched players, 42,587 FT attempts, 203 players with ≥50 attempts and 145 with ≥100. **FT is feasible in the archived sample and is the recommended first Stage 1 outcome**, conditional on resolving provenance and flagged IDs/measurements. This establishes neither representativeness nor scientific power for a particular effect size.

## 21. C&S / pull-up feasibility

Both remain **unverified**, with no observed attempt volume or matched-player count. The 2013-14 tracking deployment boundary is shorter than box-score history and does not certify endpoint coverage. Do not force either into V1. Before inclusion, retrieve valid totals from an early tracking season and a recent season, audit empty responses versus failures, verify integer counts, compare tracking game coverage with basic GP and quantify joins separately. Per-game rounded fields must not be multiplied back into pseudo-counts.

## 22. Recommended Stage 1 dataset

After the outstanding validation gates, start with a **2013-14 regular-season FT player panel** joined to the earliest complete prior combine, then consider a repeated player-season extension. Preserve original measurement source/year, stable ID, name, barefoot height, span, all exposure candidates, FTM/FTA, minutes, GP, position and season. Add age/experience only after actual retrieval. Keep missingness and unmatched records in audit tables. Carry a flag for each disputed measurement and identity; do not silently correct or exclude them.

Use official NBA responses when obtainable. If proceeding with archives, explicitly accept the secondary-source limitation and independently reconcile representative season totals and measurement samples first. Do not treat the current 14-season feasibility aggregation as an approved final analytical dataset.

## 23. Known limitations and reproducibility

Official legacy endpoints produced no usable responses from this host. Therefore live schema, completeness and reliability are unverified. Raw secondary archives are pinned by commit and SHA-256; local manifests record URL, parameters, source, timestamp and checksum. Early curl probes did not capture HTTP status and have transport/error evidence instead; later official page probes include status. No status code has been inferred for a timed-out request.

The archive shooting lineage is not independently established; sample aggregation counts are observed but not a complete official census. ID conflicts, 36 aliases, four numeric/display differences, skipped combines, missing measurements, old/new cohort truncation and incomplete role labels remain. Tracking coverage is unknown. Initial `Result_Data.csv` inspection revealed an unrelated prediction table; it was not used in this audit. Cached inspection bytes remain local only.

Evidence files: `anthropometric_sources.json`, `shooting_sources.json`, `combine_schema.json`, `shooting_schema.json`, `join_audit.json`, `coverage_by_year.csv`, `match_rate_summary.csv`, `data_quality_summary.json`, plus endpoint/documentation/provenance logs. Raw payload → immutable local cache → normalized audit records → later analytical table is the workflow. The umbrella `.gitignore` already excludes raw/interim/processed data. No dependency/environment change was made to Game Prediction V1.

Run the commands in the project README to reproduce. Checksums are verified before reading archive CSVs. The narrative report is a dated snapshot and must be refreshed if new evidence changes. Tests use synthetic cases only for validator behavior; all reported empirical counts above come from real retrieved archive data.

## 24. Stage 0 exit criteria

| Criterion | Status | Evidence / remaining gate |
|---|---|---|
| Reliable anthropometric source validated | **Partial** | Primary interface documented; secondary extract checked and two official spot checks; full source reconciliation pending |
| Meaningful height + wingspan sample | Met for archive | 1,480 distinct measured entities |
| Basic FT/3P count joins | Met for archive | 866 exact-ID matches; local real prototype |
| Explicit auditable join strategy | Met | Five classes, no fuzzy joins, review files |
| Historical coverage quantified | Met for retrieved archives | 23 combine years, 14 shooting seasons; no claim beyond those windows |
| Selection bias documented | Met | Dedicated five-part risks section |
| Viable first outcome | Met conditionally | FT counts; Stage 1 needs source validation |
| No premature effect claim | Met | No inferential model or direction reported |

**Overall: not a strict pass yet.** The remaining blocker is source reliability validation, not lack of a plausible FT sample. Next steps are official historical retrieval or stronger independent reconciliation of the archived source, review of flagged measurement/identity discrepancies, and separate tracking feasibility verification. A failed network probe must never be rewritten as successful validation.
