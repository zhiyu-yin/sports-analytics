# Stage 0B — Source validation and 2013-14 FT dataset freeze

Audit date: 2026-09-28. **Result: partial; candidate dataset frozen for review, not cleared for inferential Stage 1.** Official sources corroborate selected shoe heights/wingspans and season shooting counts. Direct official validation of barefoot height and early historical coverage remains inadequate. No exposure–outcome effect estimate, residualization, hypothesis test, confidence interval or scientific effect plot was calculated.

## 1. Objective

Validate the pinned Stage 0 sources, audit identities and measurements, and freeze a reproducible 2013-14 population and model protocol before examining any association. Deliverables are the local candidate Parquet, explicit exclusions, compact factual evidence, and [frozen protocol](stage0b_protocol.md). A candidate freeze does not imply that every archive measurement has been validated.

## 2. Why Stage 0 was partial

[Stage 0](stage0_data_audit.md) demonstrated FT feasibility using secondary combine and player-game archives, but did not authenticate their official historical lineage. Source descriptions were claims, not validation. Stage 0 report, evidence and existing raw records remain unchanged: all **107 protected files** match the pre-work SHA-256 snapshot in `stage0b_evidence/stage0_preservation_manifest.json`.

## 3. Anthropometric archive validation

The original combine CSV remains pinned to commit `3422f3003b6a37d7aabdec94d8d8bd7da1e71f04` in `ianstack/NBA-Draft-Combine-Analysis`. Numeric values were not corrected during this audit.

The predeclared sample has **27 players**, nine each from 2000–07, 2008–14 and 2015–22. Within each era, complete records were sorted by wingspan minus barefoot height, with ranks at approximately 2, 10, 20, 35, 50, 65, 80, 90 and 98 percent selected. No FT accuracy or shooting outcome entered selection. Names and archive fields remain in `anthro_sample_predeclared.csv`; `sample_protocol.json` records the declaration. Supplemental available sources are reported separately and never replace unavailable sampled players.

Official stats endpoints timed out. The historical official 2013 PDF URL returned HTTP 200 with a generic HTML page, not the requested measurements. Neither counts as validation. Old prospect URLs frequently returned pages without the requested factual fields.

## 4. Official spot-check results

The field-level ledger is [anthro_official_crosscheck.csv](stage0b_evidence/anthro_official_crosscheck.csv), with player, ID, year, field, both values, signed archive-minus-source difference, URL, timestamp, checksum and status.

| Evidence group | Players | Result |
|---|---:|---|
| Predeclared stratified sample | 27 | No successful same-year barefoot-height/wingspan pair; 131 unavailable field checks, 3 narrative discrepancies, 1 rounding-consistent weight |
| Supplemental NBA Rockets 2012 draft previews | 27 mapped players | All 27 shoe-height/wingspan pairs exact; weight exact; 20 standing-reach conflicts |
| Supplemental NBA 2022 combine narratives | 2 | Andrew Nembhard and Nikola Jovic: shoe height and wingspan exact, weights rounding-consistent |

**29 players therefore have both shoe height and wingspan corroborated directly on official NBA pages. Zero have a directly corroborated barefoot-height/wingspan pair.** Counting any agreeing field instead would yield 30 players, but that would overstate validation: Scottie Barnes contributes only a rounding-consistent weight. Overall there are 92 exact, 3 rounding-consistent, 23 conflicting and 162 unavailable field checks across 56 player-year records.

The [Rockets small-forward](https://www.nba.com/rockets/news/nba-draft-preview-part-iii-small-forwards), [center](https://www.nba.com/rockets/news/nba-draft-preview-part-i-centers) and [power-forward](https://www.nba.com/rockets/news/nba-draft-preview-part-ii-power-forwards) articles explicitly label combine measurements. All labeled rows with an exact normalized same-year name were compared. “Moe Harkless” was left unmapped rather than silently aliased. The 20 standing-reach disagreements are retained without choosing a preferred source; standing reach is not in the frozen table or selected exposure. Ayo Dosunmu's narrative wingspan/weight and Scottie Barnes's narrative wingspan differ, but the pages do not establish a comparable same-year combine measurement basis. These are comparison flags, not proven archive errors. Both records are outside the pre-2013 population/reference.

A separately pinned [secondary-host copy of the NBA-authored May 2013 combine sheet](https://www.thehrr.com/PDF/nba/mediacentral.nba.com_media_mediacentral_051713-2013-NBA-Draft-Combine-Anthropometric-Results.pdf) supplies useful independent corroboration: **63 players, 311 available field comparisons, all exact; 4 unavailable fields for Alex Len**. There are 62 complete barefoot-height/wingspan pairs. All five PDF pages were visually inspected. Explicit audit-only suffix/spelling mappings cover Otto Porter Jr., Glen Rice Jr. and Dennis Schroeder; these are not dataset ID bridges. See `anthro_secondary_crosscheck.csv` and `anthro_secondary_summary.json`. This is a checksum-pinned independent secondary cross-check, **not an authenticated official-host retrieval**. It strengthens 2013 coverage but cannot establish early-year provenance or full archive lineage.

## 5. Four discrepancy resolutions

| Player / ID | 2019 field | Archive numeric, inches | Display converted to inches | Resolution |
|---|---|---:|---:|---|
| Daniel Gafford / 1629655 | Wingspan | 86.5 | 86.25 | Unresolved; quarantine |
| Eric Paschall / 1629672 | Wingspan | 87.75 | 83.75 | Unresolved; quarantine |
| PJ Washington / 1629023 | Wingspan | 86.5 | 86.25 | Unresolved; quarantine |
| Naz Reid / 1629675 | Barefoot height | 80.25 | 80.75 | Unresolved; quarantine |

Individual official prospect-page attempts did not supply precise same-year measurements that distinguish the competing values. Washington's internally agreeing 2018 record does not resolve the 2019 disagreement. No value is guessed or preferred. All four **2019 records are quarantined** in code and tested; none can enter the <=2013 analysis or residual reference. Evidence: `measurement_discrepancy_review.csv`. Quarantine safely satisfies the discrepancy gate, while resolution remains open.

## 6. Shooting archive validation

The three original player-game partitions remain pinned to commit `a5f108b5b1f08074d78b9e8e901926a9ce4c06c5` in `NocturneBear/NBA-Data-2010-2024`.

The predeclared sample spans high, medium and low nonzero FT volume and guards/wings/bigs: Kevin Durant, Stephen Curry, Klay Thompson, Andre Iguodala, David West, Shaun Livingston, Anderson Varejao, Andrew Bogut, Draymond Green, JaVale McGee, Nemanja Nedovic and Ian Clark. Selection used volume, role and expected guide availability, never wingspan or FT accuracy. The sample is availability-driven, not a random league audit.

All 12 players' 2013-14 regular-season lines were independently checked in the [official 2016-17 Warriors media guide](https://ak-static-int.nba.com/wp-content/uploads/sites/3/2016/10/2016-17-Media-Guide-Warriors.pdf). All 12 relevant PDF pages were rendered and visually inspected to verify season and regular-season context. **60 exact comparisons** cover FTM, FTA, 3PM, 3PA and GP; **12 minutes comparisons** agree within half a minute, consistent with whole-minute publication. No conflicting count was found. Exact summed seconds are retained instead of replacing them with rounded minutes. Page-specific references are in `shooting_official_crosscheck.csv`. The official Durant MVP release separately supports 703 FTM / 805 FTA.

Aggregate check: Golden State's official season totals on PDF page 137 are FTM 1,303; FTA 1,731; 3PM 774; 3PA 2,037. All four exactly match archive sums. A full official league aggregate was not accessible; the team check must not be described as league-total validation.

Internal check: an independent second scan of all three raw partitions exactly reconstructs each of the **487 roster players'** four shooting counts, playing seconds and positive-minute GP. There are **31,378 unique player-game keys and 1,230 games**; no duplicated player-game key or zero-minute row with nonzero shooting counts was found. All reconstructed makes satisfy 0 <= makes <= attempts. Internal agreement checks construction integrity; it is not independent provenance validation. Taken together, the official player and team comparisons are sufficient factual support for this candidate season's counts, subject to the sample limitation.

## 7. Identity conflict review

All **21 conflicting-ID name links remain unresolved** after comparison of the source records; no independently established ID bridge supports remapping them. The review ledger preserves both IDs/names, normalized name, source evidence, status and notes at `data/interim/identity_crosswalk_review.csv`, with a review copy in the evidence directory. No fuzzy auto-match or normalized-name-only link enters the primary table.

Exact positive ID is stronger than a name collision. One unresolved crosswalk links combine ID 1626194 to shooting ID 201977 under “Marcus Thornton.” Shooting ID 201977 also has its own exact-ID 2009 combine record. That separate exact-ID record is retained; the unresolved 1626194 link is not used. Thus “exclude unresolved links” does not mean excluding a player who independently has a valid exact-ID record. Eight 2013-14 candidates lack such an independent match and are excluded with `unresolved_identity_conflict`.

The **36 Stage 0 exact-ID alias/name differences** remain documented in `exact_id_alias_audit.csv`; exact-ID joins are retained. Original names from both sources are stored in the final table.

## 8. Repeated-measurement policy

Use the latest complete, plausible, non-quarantined combine record through calendar year 2013. A newer incomplete record does not displace an older complete one. Same-year duplicates are rejected. Selection never depends on shooting performance.

Among 28 complete-measurement IDs repeated across the full archive, **4 are identical, 14 differ by at most 0.25 inch in both core measurements, and 10 differ materially** under the predeclared audit threshold. `repeated_measurements.csv` reports years and signed latest-minus-earliest height/wingspan differences. None has multiple complete pre-2013 records, so this rule creates no within-eligible-years selection ambiguity for this freeze. Later-year material changes require investigation before any expanded-season study.

## 9. 2013-14 eligibility rules

Require positive exact NBA ID, positive season minutes, valid nonnegative integer FTM/FTA and 3PM/3PA with makes <= attempts, and complete plausible barefoot height/wingspan in an eligible prior record. Plausibility bounds are 60–96 inches for height and 60–108 for wingspan; shorter-than-height wingspans are allowed. Plausibility is not a substitute for source validation. Reject quarantined records, unresolved name-only joins, and records available only after 2013.

There is **no FTA minimum**. Screening includes every 2013-14 archive roster ID, including zero-minute players. Every candidate appears exactly once in either the dataset or exclusion ledger. Players absent from the source entirely cannot be assessed. See the frozen protocol for timing, units, counts and identity rules.

## 10. Frozen dataset composition

| Accounting step | Players |
|---|---:|
| All archive roster IDs | 487 |
| Positive NBA minutes | 482 |
| Exact-ID match to any prior combine record, among positive-minute players | 313 |
| Eligible complete prior record / final candidate rows | **311** |
| Excluded positive-minute players | 171 |
| Excluded roster IDs including zero-minute players | 176 |

Local file: `data/processed/ft_2013_14_stage1_dataset.parquet`. It is Git-ignored and is not committed. Each player has one row, original source names, combine year/position, core measurements in inches, advantage and ratio, season counts, exact seconds/minutes, GP, join/source flags, validation status and likelihood eligibility. **Residual wingspan is not calculated.** Dataset metadata explicitly says “candidate frozen for review; NOT cleared for inference.”

Anthropometric ranges: barefoot height **67.75–85.25 inches**; wingspan **70.75–92.5 inches**; advantage **−1–10.25 inches**; ratio **0.987915–1.133117**. No shooting association accompanies these summaries. Dataset SHA-256 is `4656da551e99fc7a8fc26d6f7847f956134a9da15ed47ccd13bbf0f982fbf735`; the build refuses to silently replace a different frozen table.

## 11. Exclusion reasons

The complete local ledger is `data/interim/ft_2013_14_exclusions.csv`. Compact counts are in `ft_2013_14_exclusion_summary.csv`.

| Reason | Roster players |
|---|---:|
| No combine record | 163 |
| Unresolved identity conflict without independent exact match | 8 |
| Missing height | 2 |
| Missing wingspan | 1 |
| No positive minutes | 5 |

Counts overlap when a player fails multiple criteria; they are not intended to sum to 176. There are no invalid-count or post-season-only exclusions in this actual roster, although the pipeline tests those branches. The four 2019 quarantines have no effect on this temporally restricted population.

## 12. FT attempt distribution

Final population: **311 players; 42,587 total FTA; median 89**. Quantiles use linear interpolation between ordered observations: min 0, p10 5, p25 29.5, p50 89, p75 196, p90 338, max 805. **12 players have FTA=0; 203 have FTA>=50; 145 have FTA>=100.** These thresholds describe coverage and do not determine primary inclusion. The later accuracy likelihood has 299 informative players.

## 13. Position coverage

Original labels are preserved without collapsing: C 16; C-PF 8; PF 55; PF-C 17; PF-SF 16; PG 55; PG-SG 15; SF 40; SF-PF 14; SF-SG 15; SG 33; SG-PG 10; SG-SF 16; missing 1. See `position_coverage.csv` for shares.

Prepared, unapplied grouping: PG/SG -> guards, SF/PF -> forwards/wings, C -> bigs; hybrids retain their own labels. Model 2 uses original categories, with missing explicitly represented as “unknown”; any pooling policy must be amended before fitting and without looking at FT associations.

## 14. Primary exposure recommendation

**Residual wingspan remains the primary exposure**, chosen solely for geometry: subtraction fixes the height slope at one; division assumes proportional scaling. A linear residual permits empirical body-size scaling in an outcome-independent reference. Advantage and ratio are retained as sensitivity exposures. The audit does not establish that any exposure predicts shooting, and none was selected by an observed effect. Uncertain height provenance blocks all three, not only residualization.

## 15. Residual-wingspan reference-population decision

Choose option A with strict temporal restriction: **all 960 positive-ID, complete, plausible, non-quarantined combine participants through 2013**, one latest complete record per player, including players who never appeared in the NBA. Membership is frozen locally in `data/interim/residual_reference_pre2013.csv` and hashed. This remains a candidate reference until source validation passes.

Stage 1 would fit linear wingspan ~ intercept + barefoot height in this reference only, without FT information, then apply the transformation to the season panel. No fit has occurred. Restriction to eventual NBA players (option B) would add survival selection; including post-2013 cohorts could improve precision but weakens strict temporal interpretation and changes the reference. Neither is selected. NBA men's combine records define the league/sex scope. Repeated-record, plausibility and quarantine rules match the primary population. No silent reference change is allowed.

## 16. Primary outcome freeze

**FTM out of FTA in the 2013-14 regular season**, with future likelihood `FTM_i ~ Binomial(FTA_i, p_i)`. Do not model rounded FT%. Retain the 12 zero-attempt players in the audit table with `binomial_likelihood_eligible=false`; omit them from the future accuracy likelihood because n=0 supplies no accuracy information. No accuracy value is imputed.

## 17. Stage 1 model ladder

Design only, contingent on source release:

- Model 0: primary residual-wingspan exposure.
- Model 1: add barefoot height.
- Model 2: add original categorical combine position, including unknown.
- Model 3: add season-age/experience only after independent validation.

No season fixed effect is needed for one season. FTA enters the binomial denominator, not the primary predictor list merely to account for volume. Minutes, attempt thresholds and alternate exposures are later labeled sensitivities. No model was fitted.

Frozen interpretation: “This analysis estimates associations within NBA players with available combine measurements. It does not identify a causal effect of arm length on shooting, because combine participation, NBA selection, role assignment and other factors may jointly affect the observed sample.”

## 18. Selection-bias coverage

Of 482 positive-minute players, **311 (64.5%)** have usable prior measurements and **171 (35.5%)** do not under this policy. “Measured” here means eligible archive measurements, not fully authenticated historical provenance.

| Non-shooting characteristic | Measured | Unmeasured |
|---|---:|---:|
| Players | 311 | 171 |
| Median minutes | 1,338.77 | 971.02 |
| Mean minutes | 1,347.30 | 1,030.40 |
| Median games played | 63 | 55 |
| Mean games played | 55.32 | 49.18 |
| Players with any box-score position label | 241 | 115 |
| Share of player-games with a position label | 51.37% | 41.18% |

These are descriptive coverage comparisons only. Box-score position availability is sparse and is not equivalent to validated role. No shooting comparison or inferential test was conducted between groups. The largest limitation is selection into combine participation and then NBA survival/playing time: one-third of the observed league lacks usable measurements, and measured players have more playing time. Residualization cannot eliminate this selection.

## 19. Provenance

`source_manifest.json` preserves every retrieved source's URL, timestamp, response/transport status, local raw checksum/path and pinned archive revision where applicable. Its normalized-output checksum map covers the candidate Parquet, source comparison ledgers, identity and measurement review outputs, prepared season totals, exclusions and reference membership. Failed requests retain diagnostics with null payload checksums rather than invented data.

`build_manifest.json` records dataset/schema/hash, protocol hash, code hashes, reference hash, source-manifest hash, runtime dependency and Stage 0 preservation result. Raw/full source bodies, extracted PDF text and page renders remain local under Git-ignored data directories. Docs contain only compact factual comparisons, not full copyrighted pages. The independent mirrored PDF is explicitly secondary-hosted. HTTP status alone is never a factual match.

Reproduction instructions and dependencies are in the subproject README and `requirements-stage0b.txt`. Offline rebuilds verify raw source checksums. Re-running against changed sources requires an explicit versioned amendment instead of overwriting the candidate freeze. No commit or push was performed, and NBA Game Prediction V1 was untouched.

## 20. Tests

**33 passed, 0 failed, 0 errors, 0 skipped**: seven existing Stage 0 tests and 26 Stage 0B tests. Evidence is `test_run.txt` and `test_summary.json`.

Tests cover exact-ID priority, unresolved-link rejection, no name/fuzzy auto-match, latest complete prior measurements, incomplete latest records, future records, duplicate records, feet/inches/cm consistency, all four quarantines, integer/nonnegative/finite counts, makes <= attempts, FTA=0 retention and likelihood flag, multiple exclusion reasons, shorter-than-height wingspans, invalid IDs, one row per player, no future measurements, complete roster accounting, source/frozen checksums, preserved Stage 0 files, unique temporal reference, and official/internal shooting results.

An AST guard rejects scientific association/model imports and common correlation/regression/fit calls across pipeline modules and Stage 0B scripts. It is a guard against known APIs, not a mathematical proof against every possible hand-written estimator. Code inspection plus the executed construction steps establish that this run used only factual comparison, sums, ranges and descriptive distributions. Arrow emitted sandbox CPU-cache-discovery warnings, but serialization, readback and checksum tests passed.

## 21. Remaining limitations

Direct official checks are concentrated in 2012 and 2022 and do not supply the core barefoot-height field. The planned early-year sample remains unavailable. The secondary 2013 sheet is strong corroboration for that year but does not authenticate its hosting lineage or all historical years. Standing-reach disagreements show why source claims cannot be accepted wholesale. The four numeric/display discrepancies remain unresolved but safely quarantined outside this population. The 21 identity links are not resolved through independent ID bridges. Shooting spot-checks favor players covered by a Warriors guide and do not constitute a census of official league totals. Position, age and experience are not uniformly validated. These limitations preclude calling the candidate a high-confidence inferential release.

## 22. Stage 0B exit criteria

| Gate | Result |
|---|---|
| Meaningful official anthropometric evidence sufficient for core exposure | **Partial / release blocked**: 29 shoe-height/wingspan pairs, no direct barefoot-height pairs, early coverage absent |
| Four discrepancies resolved or safely quarantined | Pass: all four quarantined |
| Independent 2013-14 shooting factual validation | Pass within stated spot-check scope |
| Exact-ID join policy frozen | Pass |
| Unresolved identity links excluded | Pass; independent exact-ID records retain priority |
| Repeated-measurement rule frozen | Pass |
| Unique one-row-per-player table | Pass: 311 rows |
| Every screened exclusion has reasons | Pass: 176 roster exclusions |
| Primary exposure chosen without effects | Pass: residual wingspan |
| Outcome frozen as makes/attempts | Pass |
| Model ladder predeclared | Pass |
| No exposure–outcome effect estimated | Pass |

**Stage 0B does not strictly pass.** The reviewable candidate and protocol are frozen, but the historical anthropometric source gate remains closed.

## 23. Recommended Stage 1

**Do not start inferential Stage 1 yet.** First obtain authenticated official combine sheets or a documented official export supporting barefoot height and wingspan across the planned early/middle strata, and reconcile the relevant source-quality discrepancies. Record any additional validation or correction in a versioned audit amendment; preserve this candidate and its hashes. Once that gate is passed, use the predeclared reference, outcome and ladder without outcome-driven reselection. Age/experience remain conditional on independent validation. No effect direction is predicted by this report.
