# Stage 0C — Historical barefoot height / wingspan validation

2026-09-28. **Decision: PASS.** The 45-player predeclared historical sample has 45 direct official same-player, same-combine-year barefoot-height/wingspan pairs, all exact. Successful browser retrieval also enabled a separate census comparison of all historical records through 2013. The original analytical dataset, reference membership and Stage 0/0B evidence remain unchanged.

**Anthropometric provenance gate passed; Stage 1 inferential analysis may begin.** Prior shooting validation remains accepted. Stage 1 has not been run, and this report contains no scientific effect estimate.

## 1. Objective

Resolve the specific exposure-source gate left by Stage 0B: whether historical barefoot height and wingspan in the pinned combine archive are supported by official NBA records. The validation unit is a same-player, same-year pair; shoe height cannot satisfy barefoot-height validation. No residualization or exposure–outcome analysis belongs to this stage.

## 2. Why Stage 0B remained blocked

[Stage 0B](stage0b_source_validation.md) obtained official shoe-height/wingspan corroboration but no direct barefoot-height/wingspan pairs across the historical strata. Its NBA-authored 2013 PDF copy was independently corroborative but secondary-hosted. Command-line NBA API requests repeatedly timed out. Those results were insufficient for the frozen residual-wingspan exposure.

Stage 0C found a working retrieval route: **the live official NBA Stats page renders historical tables in the in-app browser**, even while command-line endpoint requests fail. This is new factual evidence, not a reinterpretation of prior timeouts or a change to the source gate. Prior reports and the protocol are preserved as dated records.

## 3. Validation sample design

Before Stage 0C source lookup, `release_rule_predeclared.json` and `validation_sample_predeclared.csv` froze **45 participants** from complete, plausible, positive-ID records through 2013. Sampling uses only year, barefoot height and wingspan.

Three eras: 2000–2004, 2005–2008, 2009–2013. Within each era, height strata are short (<75 inches), medium (75 to <80), and tall (>=80). These are physical-size groups, not validated playing-position assignments. Within each era/height cell, order by wingspan advantage, then year/name/ID for ties; select ranks approximately 0.10, 0.35, 0.50, 0.65 and 0.90. Relative-span strata are lower tail (<20th rank percentile), middle (20th–80th), and upper tail (>80th), defined **within era/height cell**. This yields 15 players per era and per height group; 9 lower-tail, 27 middle and 9 upper-tail players.

No FT data, accuracy or outcome association selected participants. Original unavailable cases could not be silently replaced. A deterministic reserve rule was frozen: at most one replacement per unavailable original, same era/height/relative stratum, ordered by SHA-256 of ID/year. **No replacements were needed or used.** The full reserve stays local in `data/interim/stage0c_replacement_pool_predeclared.csv`.

Rounding was declared before source inspection: absolute difference <=0.125 inch qualifies only when source precision supports quarter-inch or finer values. Coarser measurements are separately flagged and cannot manufacture qualifying precision. Exact comparisons have zero difference.

The predeclared release rule requires >=30 direct official pairs, >=95% exact/explainably rounded agreement, all three eras and all height/relative strata represented, no unresolved substantive/systematic discrepancy, clean reference membership and passing tests. The descriptive systematic-offset screen flags at least three same-sign nonzero differences within an era or height stratum when their median absolute magnitude exceeds 0.125 inch; obvious repeated unit/shoe-field errors also require review. No significance test is used.

## 4. Source hierarchy

The search followed the requested hierarchy: official NBA measurement tables, NBA-hosted sheets/PDFs, prospect measurements, team publications, then archived official URLs. Direct table access ultimately succeeded, so no secondary source was needed to satisfy the gate. The original pinned CSV remains a **secondary archive**, not retroactively relabeled official.

The accepted source is [NBA Stats Draft Combine Anthropometrics](https://www.nba.com/stats/draft/combine-anthro?SeasonYear=2013-14). Historical season selectors such as 2013-14 identify the **2013 combine cohort**, not a later measurement of the same player. Accepted captures explicitly include separate “HEIGHT W/O SHOES,” “HEIGHT W/ SHOES” and “WINGSPAN” columns. Fields use feet/inches with quarter-inch increments. No generic roster height was substituted.

## 5. Official-source retrieval results

Command-line API probes for 2004, 2007 and 2013 timed out with no payload. The initial NBA Stats HTML retrieval did not contain the populated measurement table. The surviving Bulls 2004 page lacked its old factual table. The original 2013 PDF URL returned generic HTML; the old 2013 results URL and a Suns guide-location probe returned 404. Wayback index requests timed out. All are recorded as unsuccessful factual retrievals, not disagreements.

The browser successfully rendered **14 historical NBA tables (2000–2013)**, plus the 2019 table for the four discrepancy reviews. Read-only DOM extraction preserved the selected season, source URL, headers, original cell strings and UTC timestamp. Each raw capture is hashed and stored locally. Names are matched exactly after accent/punctuation/case normalization within the exact year, with uniqueness required; there were no unmatched historical table names and no fuzzy matching. The displayed table does not independently certify NBA IDs: archive IDs label the audited source rows, and the prior exact-ID analytical join policy remains unchanged.

One initial 2001 capture still displayed the preceding 2000 table while the season control had already changed. It was **rejected and retained as stale evidence**. The verified 2001 capture replaced it only in accepted inputs. Subsequent capture checks waited for the previous table to be replaced and rejected unchanged content. This matters because a selected year alone does not prove that an asynchronous table has refreshed.

All **45 preselected cases** have successful factual retrieval and `official_pair_found`. There are zero partial-only, barefoot-missing or unavailable primary-sample cases. This is 45 player-level retrieval successes across 14 unique historical pages, not 45 independent source systems. See `browser_capture_manifest.json` and the cross-check ledger.

## 6. Barefoot-height agreement

**45/45 primary-sample barefoot heights are exact**, with zero rounding cases, missing values or conflicts. Every source explicitly labels height without shoes. Archive and official values are stored separately; signed differences are archive minus official in inches. No value was corrected to improve agreement.

The broader historical comparison also found no barefoot-height mismatch. Missing values remain missing rather than being replaced by shoe heights.

## 7. Wingspan agreement

**45/45 primary-sample wingspans are exact**, with zero rounding cases, missing values or conflicts. All come from the same official year/row as the corresponding barefoot height. No later-year measurement validates an earlier record.

There is no directional discrepancy in historical core measurements: all observed numeric differences are zero. This supports archive transcription consistency with current official historical tables; it does not establish that the original physical measurements were free of measurement error.

## 8. Pair-level agreement

| Primary-sample metric | Result |
|---|---:|
| Preselected players | 45 |
| Successful official factual retrievals | 45 |
| Direct barefoot-height observations | 45 |
| Direct wingspan observations | 45 |
| Complete same-year pairs | **45** |
| Exact pairs | **45** |
| Rounding-consistent pairs | 0 |
| Conflicting pairs | 0 |
| Official-source-unavailable cases | 0 |
| Exact/rounding agreement | **100%** |

[anthro_barefoot_wingspan_crosscheck.csv](stage0c_evidence/anthro_barefoot_wingspan_crosscheck.csv) includes sampling strata, both original values, field/pair/availability statuses, URL, timestamp and raw checksum for every selected record.

A separate source-wide comparison covers **970 historical rows**, including **965 complete pairs**, all with exact core agreement. Five rows lack a complete pair. Five complete records have missing-ID placeholders, leaving the previously frozen **960** positive-ID reference participants. The census result supplements the original sample; it does not replace its denominator or introduce availability-driven replacements.

## 9. Agreement by era and body stratum

| Dimension | Stratum | Exact / complete pairs | Agreement |
|---|---|---:|---:|
| Era | 2000–2004 | 15 / 15 | 100% |
| Era | 2005–2008 | 15 / 15 | 100% |
| Era | 2009–2013 | 15 / 15 | 100% |
| Height | <75 inches | 15 / 15 | 100% |
| Height | 75 to <80 inches | 15 / 15 | 100% |
| Height | >=80 inches | 15 / 15 | 100% |
| Relative wingspan | Lower tail | 9 / 9 | 100% |
| Relative wingspan | Middle | 27 / 27 | 100% |
| Relative wingspan | Upper tail | 9 / 9 | 100% |

Relative-span ranks are conditional on era/height cell. `agreement_by_stratum.csv` also records retrieval, missingness and conflict counts. These are measurement agreement summaries, never grouped shooting outcomes.

## 10. Four discrepancy resolutions

The [official 2019 table](https://www.nba.com/stats/draft/combine-anthro?SeasonYear=2019-20) supports the **archive display string** for each flagged record:

| Player / ID | Field | Archive numeric | Archive display, inches | Official, inches | Resolution |
|---|---|---:|---:|---:|---|
| Daniel Gafford / 1629655 | Wingspan | 86.5 | 86.25 | 86.25 | official_display_confirmed |
| Eric Paschall / 1629672 | Wingspan | 87.75 | 83.75 | 83.75 | official_display_confirmed |
| P.J. Washington / 1629023 | Wingspan | 86.5 | 86.25 | 86.25 | official_display_confirmed |
| Naz Reid / 1629675 | Barefoot height | 80.25 | 80.75 | 80.75 | official_display_confirmed |

These are same-player 2019 combine observations, not later roster measurements. The evidence resolves which value is supported, but **no archive, old quarantine file, dataset or protocol was edited**. All four records remain outside the <=2013 reference and analytical cohort. Any later study including them must use an explicitly versioned corrected record rather than silently changing the original archive. The detailed ledger is `measurement_discrepancy_review.csv`.

## 11. 2013-14 candidate-population source coverage

This secondary audit was performed after the outcome-independent source comparison. The Parquet reader requested only **player_id, player_name_nba and season**. Measurement year was obtained from the independently reconstructed, unchanged reference rule; no shooting outcomes were read from the candidate file.

| Source coverage | Candidate players |
|---|---:|
| Direct official barefoot+wingspan corroboration | **311** |
| Official partial corroboration only | 0 |
| Archive-only measurement | **0** |
| Quarantined measurement | 0 |

`candidate_population_source_coverage.csv` contains identity, season, measurement year, source category and official URL. Coverage did not become an eligibility criterion. No player was removed, added or selected based on webpage survival. The candidate Parquet remains byte-for-byte unchanged at SHA-256 `4656da551e99fc7a8fc26d6f7847f956134a9da15ed47ccd13bbf0f982fbf735`.

## 12. Reference-population validation

The independently reconstructed rule is unchanged: latest complete, plausible, non-quarantined measurement through 2013, one record per positive archive ID. The result exactly equals all fields and membership of the Stage 0B reference file:

- **960 participants and 960 distinct positive IDs**.
- Years 2000–2013; zero post-2013 records.
- Zero missing/nonpositive-ID placeholders.
- Zero quarantined records.
- **960 direct official complete pairs**, all exact.
- Zero repeated IDs with multiple complete eligible records before 2014.

The copied local membership snapshot is `data/interim/stage0c_reference_membership.csv`. Its byte hash remains **`14537d9c1cec20b388fc2cf5c86d7ea9ec2e435117c62da499f2b2fa2820d85a`**, identical to Stage 0B. `reference_population_hash.json` also records a canonical-content hash. No residual column or fitted geometric transformation was produced.

Positive archive-ID uniqueness is the frozen operational membership rule, not independent biographical authentication of every ID. Stage 0C validates the associated measurement records; it does not resolve the 21 previously unresolved cross-source identity links or change their exclusion policy.

## 13. Repeated measurements

Every repeated complete positive-ID record in the archive was reviewed. The supplementary full-archive ledger has **28 IDs: 4 identical, 14 near-identical, 10 materially different** under the unchanged <=0.25-inch threshold for both core fields. Differences are signed latest minus earliest; material changes are review flags, not automatically errors.

None has multiple complete eligible records through 2013, so no observed historical participant requires a choice between two eligible complete measurements. The latest-complete rule is nevertheless tested using explicit incomplete/latest/future/duplicate fixtures. `repeated_measurement_review.csv` keeps later-year differences visible without allowing later records into the reference.

## 14. Internal consistency

In the 960-person reference, numeric versus display values agree exactly for **960 barefoot heights and 960 wingspans**. No core value violates the frozen broad plausibility bounds (height 60–96 inches; wingspan 60–108). No duplicate valid player/year key was found. Shorter-than-height wingspans are not treated as impossible.

Standing reach, which is not part of the frozen exposure or reference fields, has **957 exact numeric/display matches, two 0.05-inch differences, and one missing value**. Robb Dryden (2001) has numeric 110.2 versus display/official 110.25; Damone Thornton (2001) has 103.7 versus display/official 103.75. Both are explainable one-decimal-versus-quarter-inch representations and meet the declared 0.125-inch rounding tolerance. They are explicitly reviewed in `standing_reach_difference_review.csv`; no correction was applied. No available reference reach is at/below barefoot height or outside the audit range 80–132 inches.

One original reach string uses a leading fractional inch (`8' .25''`); the Stage 0C parser interprets it as 96.25 inches while preserving the source string. The old parser and prior evidence remain untouched.

`measurement_missingness_by_year.csv` reports height, wingspan and reach missingness for all 14 historical cohorts, including incomplete records excluded from the reference. `internal_consistency_summary.json` and local detailed ledgers distinguish strict numeric/display differences from substantively conflicting core measurements. These internal checks support quality control but do not replace direct official corroboration.

## 15. Provenance map

[source_provenance_map.json](stage0c_evidence/source_provenance_map.json) distinguishes the pinned secondary archive, direct official NBA browser tables, failed official endpoint/page/PDF attempts, and unsuccessful historical-archive lookups. Each source includes publisher/type, URL or pattern, years, fields, precision, method, UTC retrieval time and checksum where bytes exist. No search-result snippet, fan page, generic roster measurement or secondary copy counts as an official pair.

Full table captures and response bodies remain local under Git-ignored `data/raw/stage0c/`. The 1,047 mapped official observations (970 historical rows plus 77 from 2019), internal comparisons, full reserve and reference snapshot remain local under `data/interim/`. Docs contain the requested selected comparisons, identity/source-coverage ledger and compact evidence, not full source pages.

All **262 prior files** in the preservation manifest retain their SHA-256 hashes, including prior reports/protocol, both evidence directories, existing raw data and candidate/reference files. No existing subproject source file was edited; Stage 0C code is separate. The NBA Game Prediction project remains untouched. `build_manifest.json` records code, normalized-output, sample/rule, test and release-decision hashes. Offline reproduction and browser-capture details are in [Stage 0C reproduction notes](stage0c_reproduction.md).

## 16. Tests

**37 Stage 0C tests passed; zero failures, errors or skips.** See `test_run.txt` and `test_summary.json`. Earlier test suites were deliberately not executed because some load shooting outcomes; their prior results remain preserved.

Coverage includes same-player/same-year enforcement; rejection of later-year and shoe-height substitution; sampling without outcome access; within-stratum deterministic replacements; unavailable versus disagreement distinction; exact rounding boundary and coarse-precision rejection; preservation of conflicts without correction; all four quarantine rules; latest-complete selection; no post-2013 or placeholder IDs; duplicate rejection; projected candidate/anthropometric reads; source checksum and prior-file preservation; rejected stale capture; complete candidate coverage; and absence of residual output or scientific fitting/correlation calls.

The final validation importer projects only anthropometric/identity columns from the combine CSV and only three identity/season columns from the candidate Parquet. During initial setup, the generic CSV parser decoded the combine archive's full rows, including unused drill columns; the sample and comparisons accessed only anthropometric fields, and no drill outcome was used. The final importer and tests enforce projection. **No candidate FT/3P outcomes were loaded, no outcomes were used for scientific analysis, and no model was fit.** Hashing the frozen Parquet for preservation reads bytes without decoding outcome columns.

Static guards reject known scientific model/correlation imports and calls. They complement code review and restricted inputs; they are not a universal proof against every conceivable estimator. The pipeline contains no scientific estimator or residualization implementation. Arrow's sandbox CPU-cache-discovery warnings did not affect successful reads or checksums.

## 17. Release-gate decision

| Predeclared criterion | Result |
|---|---|
| >=30 direct official same-year core pairs | Pass: 45 / 45 selected |
| >=95% exact/rounding pair agreement | Pass: 100% exact |
| No unresolved systematic core discrepancy | Pass: all historical core differences zero |
| Substantive conflicts resolved or quarantined | Pass: four 2019 display values confirmed, outside temporal scope; minor reach differences explained |
| Cross-era/body-stratum coverage | Pass: all three eras and all height/relative groups |
| Reference membership frozen cleanly | Pass: unchanged 960 |
| All Stage 0C tests pass | Pass: 37 |
| No outcomes loaded for scientific analysis | Pass |
| No residual-wingspan model fitted | Pass |
| No exposure–outcome effect estimated | Pass |

Final classification: **PASS**, recorded in `release_gate_decision.json`. The threshold and sampling rules were not weakened after seeing agreement.

## 18. Remaining limitations

The official tables are a current NBA publication of historical measurements, not independently remeasured physiques or original signed paper forms. The archive and current NBA tables may share upstream lineage; exact agreement validates transcription and source support, not independent measurement reliability. Direct validation applies to the captured years and frozen population, not every later cohort. Four 2019 numeric errors demonstrate why later-year generalization requires separate review.

Browser access succeeded where command-line requests failed, so future automated retrieval remains fragile. Frozen raw captures make this audit reproducible offline; a future live refresh may change and must be versioned. Same-year unique-name mapping validates measurement attribution at the table level, not every stable ID. Combine participation, NBA selection and role selection remain substantive limitations for any future association. Source clearance does not remove those selection biases or establish causality.

## 19. Stage 1 readiness

**Anthropometric provenance gate passed; Stage 1 inferential analysis may begin.** This statement clears the source gate under the frozen design, assuming Stage 0B shooting validation remains accepted. It does not execute Stage 1 or change the original 311-player population, 960-person reference, outcome, exposure choice or model ladder.

No FT effect calculation, residual-wingspan fit, exposure–outcome regression, p-value, effect confidence interval or effect plot was produced. **Stage 1 was not run. Nothing was committed or pushed.**
