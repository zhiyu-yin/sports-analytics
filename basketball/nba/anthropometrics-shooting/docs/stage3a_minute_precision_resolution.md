# Stage 3A — Minute Precision Resolution

Dated 2026-09-28. **UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE.** Stage 3 Part A remains BLOCKED; Part B remains DISABLED.

## 1. Objective

Distinguish source disagreement from minute representation or aggregation effects using official NBA game evidence only. No wingspan/shooting association, model, residual, correlation, posterior, or effect plot was calculated or examined.

## 2. Why Stage 3 was blocked

The permanent Stage 3 gate failed four predeclared sample MIN comparisons and 170 full-census MIN comparisons against the frozen decimal-display tolerance of 0.05 minute (implemented with numerical epsilon 0.050001). The original records, protocol, report, and all other preexisting project artifacts are hash-protected and unchanged. No tolerance has been widened. The original protocol's separate integer-display rule is not applied to decimal-formatted values such as `2851.0`.

## 3. Evidence hierarchy

Retrieved official NBA historical player traditional box-score logs for every season/player in the frozen sample, plus all archive-discovered zero-minute players in the three validation seasons. These pages display MM:SS, finer than season totals shown to one decimal minute. Captures retain URL, UTC retrieval time, filters, headers, row cells, game links, and SHA256 manifests. All 53 logs contain complete recorded-appearance sets: official season GP equals log count and archive recorded count. Season identity is checked in filters, dates and event URLs.

The [official Christmas game box score](https://www.nba.com/game/ind-vs-phi-0021601203/box-score) separately confirms appearance/DNP/DND treatment. Historical and recent CDN box-score probes returned 403; the historical stats endpoint timed out. Direct HTTP page retrieval returned 403, but browser rendering succeeded. These failures are documented, not counted as validation. The [NBA glossary](https://www.nba.com/stats/help/glossary) provides no rounding mechanism in its MIN definition. No third-party minute explanation is used.

**Finest successfully obtained precision is displayed whole seconds, not guaranteed underlying exact clock time.** No subsecond field or authoritative aggregation algorithm was obtained.

## 4. Audit sample

Frozen at `2026-09-28T22:19:00.054708+00:00`, SHA256 `6819d4c95b872d96bf96fabeb327685f767017fcd1de49602c0274ec81c6bf70`, before the first game capture. Select two lowest SHA256(`stage3a-minute-only-v1|season|player_id`) in each season × within-season season-minute rank tertile × original MIN gate status, then add all four original failed cases. One late low-minute mismatch stratum contains only one candidate, retained without replacement.

The frozen sample has **39 player-seasons: 18 within-tolerance and 21 mismatches, including 17 additional mismatches**. It spans 2010–11, 2016–17, 2023–24 and low/medium/high totals. Sampling used only identity, season, MIN and original MIN-match status. No FTM, FTA, FT%, wingspan, residual wingspan, or association informed selection. Fourteen additional player-seasons were selected solely because their archive contained recorded 0:00; they are separately labeled, not added to the frozen sample.

See `stage3a_evidence/minute_audit_sample_predeclared.csv` and `sample_freeze.json`.

## 5. Game-level reconstruction

The comparison retains distinct routes A–F:

- A: no independent raw archive season MIN field exists; explicitly unavailable.
- B: integer-second sum parsed from archive game displays, including recorded 0:00.
- C: raw official season decimal MIN, separately converted to seconds.
- D: sum of official game MM:SS displays, including recorded 0:00. These are not relabeled unrounded clocks.
- E: official season GP.
- F: independently counted official recorded game appearances.

Across **53 player-seasons / 2,861 recorded appearances**, B = D exactly, every matched raw game MIN string agrees, all dates agree, every game ID is regular-season, and E = F = archive recorded GP. No recorded game is unmatched on either side. The frozen sample itself contributes 2,308 appearances. The union comparison retains 3,559 rows, including 698 archive empty-minute rows absent from the official appearance-only logs. Their official status remains **missing**, not inferred 0:00 or independently verified DNP. No missing minute is imputed.

`official_game_minute_crosscheck.csv` has row-level raw and parsed values, statuses, dates, IDs and provenance; `minute_reconstruction_by_player_season.csv` preserves A–F.

## 6. Four original discrepancy cases

| Season | Player | GP | B = D seconds | B = D minutes | C raw MIN | B − C seconds |
| --- | --- | --- | --- | --- | --- | --- |
| 2010-11 | DeMar DeRozan | 82 | 171064.0 | 2851.0666666666666 | 2851.0 | 4.0 |
| 2010-11 | Wesley Matthews | 82 | 165508.0 | 2758.4666666666667 | 2758.4 | 4.0 |
| 2010-11 | Trevor Ariza | 75 | 155994.0 | 2599.9 | 2599.8 | 6.0 |
| 2016-17 | Seth Curry | 70 | 121744.0 | 2029.0666666666666 | 2029.0 | 4.0 |

All 309 games in the four original cases reconcile exactly at official displayed whole-second precision. Thus each +4/+4/+6/+4 second season difference is reproduced **within NBA's own public representations**: summing NBA game MM:SS yields the archive total, not NBA's season decimal. This excludes archive-only time conversion and missing games as explanations in these cases. It does **not** establish whether hidden fractional-second rounding, truncation, revisions, or another internal aggregation detail generated the season values.

Candidate checks (computed for all 53, with per-player results in `candidate_rounding_explanations.csv`):

| Explanation | Four-case result | Interpretation |
| --- | --- | --- |
| Round season sum to whole minute | Compatible for DeRozan and Curry; not Matthews or Ariza | Not a common mechanism; official raw season values are decimal displays |
| Round whole-second sum to one decimal minute | Predicts 2851.1, 2758.5, 2599.9, 2029.1; all differ from C | Rejected for these four |
| Exact displayed-second aggregation then decimal display rounding | Same calculation as preceding row | Rejected for these four |
| Truncate whole-second sum to one decimal | Compatible for three; fails Ariza | Not a common mechanism |
| Round each displayed game to one decimal then sum | 2851.6, 2758.8, 2600.3, 2029.6; all fail | Rejected for these four |
| Round each displayed game to whole minutes then sum | 2852, 2761, 2602, 2031; all fail | Rejected for these four |
| Sum unobserved fractional-second values, round games and season separately | Mathematically compatible with all four | Not demonstrated: interval feasibility is not observed clock evidence |
| Archive MM.SS conversion error | Archive and official game sums agree; parser checks pass | Not supported |
| Source revision/stat correction | No matching-game discrepancy or dated revision evidence found | Cannot exclude an internal product revision from displays alone |
| Genuine materially different playing time/missing games | Zero game differences and identical complete appearance sets | Not observed in the audited sample |

For the fractional-second hypothesis, intersect the possible nearest-second game-sum interval D ± GP/2 seconds with the possible nearest-tenth season interval C ± 3 seconds. The intervals overlap for all four. This is an explicitly hypothetical rounding model, not an acceptance threshold and not proof that NBA uses it.

## 7. Broader mismatch sample

All 39 frozen player-seasons reconcile game by game, covering all 18 within-tolerance controls and all 21 mismatches. The 14 zero-minute supplements also reconcile. The audit therefore does not merely explain away four cherry-picked cases. It is still a sample of minute records, not all official game logs for the full 1,510-player-season census. No extrapolation of whole-second equality to unqueried players is claimed.

## 8. Decimal / MM:SS conversion audit

`12:04` = 724 seconds = 12 + 4/60 minutes, not 12.04. `12:28` = 748 seconds = 12 + 28/60, not 12.28. Decimal `12.4` minutes means 744 seconds and is a different representation. A Decimal parser preserves exact seconds and distinguishes empty values from zero. One hundred deterministic SHA256-selected nonempty archive rows pass independent component arithmetic and match the original Stage 3 parser; their identities and calculations are retained.

There are **186 noncanonical M:60 archive rows** in the three seasons; eight occur in the official audit and both sources show the identical M:60 string. Treating M:60 as (M+1) minutes preserves the displayed seconds, as the prior Stage 3 parser already did. These are logged explicitly; they are not silently dropped or interpreted as M.60 minutes. Such displays suggest a formatting boundary, but do not alone prove how fractional seconds were aggregated.

## 9. Zero-minute appearances

All **15** archive 0:00 candidates in the three validation seasons are present as official recorded game-log appearances: 3 early, 4 middle, 8 late. Every official 0:00 in the 53 retrieved logs is included below. This is an archive-directed zero audit, not an independent league-wide official log census.

| Season | Player | Date | Official FTM | Official FTA |
| --- | --- | --- | --- | --- |
| 2010-11 | Hamed Haddadi | 2011-03-06 | 0 | 0 |
| 2010-11 | James Anderson | 2011-02-23 | 0 | 0 |
| 2010-11 | Jason Collins | 2010-12-01 | 0 | 0 |
| 2016-17 | Rakeem Christmas | 2017-04-10 | 1 | 2 |
| 2016-17 | Boban Marjanovic | 2017-01-08 | 0 | 0 |
| 2016-17 | Shawn Long | 2017-03-09 | 0 | 0 |
| 2016-17 | Pierre Jackson | 2017-01-19 | 0 | 0 |
| 2023-24 | Bol Bol | 2023-11-08 | 0 | 0 |
| 2023-24 | Isaiah Jackson | 2024-03-13 | 0 | 0 |
| 2023-24 | Isaiah Jackson | 2024-04-07 | 0 | 0 |
| 2023-24 | Trayce Jackson-Davis | 2023-11-01 | 0 | 0 |
| 2023-24 | Bismack Biyombo | 2023-11-03 | 0 | 0 |
| 2023-24 | Justin Holiday | 2023-11-22 | 0 | 0 |
| 2023-24 | Cody Zeller | 2023-12-26 | 0 | 0 |
| 2023-24 | Seth Curry | 2023-11-22 | 0 | 0 |

Christmas on 2017-04-10 (game 0021601203) is explicitly **0:00, 1 FTM / 2 FTA**, in both the official log and box score. His official GP is 29; counting only positive-time game rows gives 28. Including the zero record yields 21/29 season FTM/FTA, versus 20/27 if improperly dropped. No shooting count has been changed in Stage 3A. A displayed zero is a recorded appearance, not evidence of no participation or a DNP.

The full Christmas box score independently classifies 26 player rows, including five DNP/DND rows; all match the archive's appearance versus empty-minute treatment. At season level, positive-minute eligibility agrees for **all 1,510** official/archive season pairs, including all 170 mismatches. Therefore retain positive-minute **season eligibility**, aggregate all recorded appearances including 0:00, and keep missing/DNP separate. This validates the earlier aggregation correction without altering the failed gate.

## 10. Quantization pattern

Sign is archive game-second sum minus official displayed season minutes × 60. Frequencies for every requested integer-second bin:

| Seconds | Frequency |
| --- | --- |
| -8 | 0 |
| -7 | 0 |
| -6 | 0 |
| -5 | 4 |
| -4 | 9 |
| -3 | 0 |
| -2 | 0 |
| -1 | 0 |
| 0 | 0 |
| 1 | 0 |
| 2 | 0 |
| 3 | 0 |
| 4 | 88 |
| 5 | 43 |
| 6 | 14 |
| 7 | 8 |
| 8 | 4 |

For all 170 mismatches: mean **4.017647 s**, median **4 s**, sample SD **2.591460 s** (population SD 2.583826), min **−5 s**, max **+8 s**, median absolute **4 s**, maximum absolute **8 s**. All values are exactly on an integer-second grid using Decimal source arithmetic; binary floating-point differences were not rounded into a manufactured grid.

There are **157 positive versus 13 negative** differences. The failed subset is **not symmetric**. Its selection is conditional on exceeding the old gate, so this is not an unbiased characterization of all rounding errors. Discreteness and small size do not demonstrate a benign mechanism or justify a threshold based on the observed maximum.

## 11. Whether playing-time records materially disagree

No material archive-versus-official disagreement is observed at the available game-display resolution. All audited recorded appearances and time strings match. The discrepancy is located between official game displays and official season displays, but its exact numerical mechanism remains unresolved. Lack of subsecond records limits the inference: the public integer-second display cannot establish the underlying real elapsed time. This is insufficient precision evidence, not a demonstrated material source conflict and not proof of a resolved rounding rule.

## 12. Primary-count versus MIN distinction

All **7,550** prior full-census player comparisons for FTM, FTA, 3PM, 3PA and GP remain exact; all **450** team count/GP comparisons remain exact. Prior artifacts and raw archives are unchanged. The scientific response would be FTM out of FTA. MIN is neither that response, a primary predictor, nor the definition of wingspan exposure; it affects positive-season eligibility and descriptive selection coverage. This distinction supports studying representation separately, but does not waive the frozen validation gate.

## 13. Proposed protocol amendment

**No operative amendment is recommended.** Exact language of the dated decision:

> No amendment to the Stage 3 source-validation protocol is recommended on the current Stage 3A evidence. Retain the original failed Part A gate and its frozen MIN tolerance unchanged. Stage 3 Part B remains disabled. Reconsider a representation-based MIN rule only after official evidence demonstrates the aggregation/display mechanism and explains the asymmetric season differences while preserving exact FTM, FTA, 3PM, 3PA, and GP reconciliation and positive/zero/DNP classification.

The required `protocol_amendment_proposal.md` records this deferral and A–F evaluation. It does not implement an amendment or create a numeric tolerance.

## 14. Amendment decision

**UNRESOLVED — INSUFFICIENT PRECISION EVIDENCE.** Criteria A, D and F are supported. C is supported at recorded display/classification precision, with the explicit DNP coverage limitation. B is partial: complete games and MM:SS match, but the aggregation mechanism is not demonstrated. E is partial: small/discrete values and no missing audited games, but a strongly asymmetric pattern. Since the complete evidentiary rule is not met, no amendment is recommended.

## 15. Whether Stage 3 Part A can be rerun

A diagnostic rerun under the unchanged original protocol is possible but would retain the same failure. A rerun cannot be used to mark the old record PASS or release Part B. Further official finer-resolution records or authoritative aggregation documentation, followed by review of a separately dated supported amendment, are needed before considering a new gate decision. **Stage 3 Part B remains disabled.**

## 16. Reproducibility

From the subproject directory, the existing pinned Stage 3 Python environment is sufficient; no new packages were installed:

```sh
.venv/bin/python scripts/stage3a_audit.py
.venv/bin/python scripts/stage3a_report.py
.venv/bin/python scripts/verify_stage3a.py
```

`stage3a_prepare.py` is a one-time freeze and refuses to overwrite the sample. `stage3a_archive_projection.py` reconstructs the minute-only audit projection plus FTM/FTA needed for the explicitly requested zero-count audit; neither reads an exposure/outcome panel. Public browser capture is recorded in `official_dom_capture_workflow.js`; immutable raw captures support offline reconstruction without requiring live network access. Source archive SHA256 values, all prior artifact hashes, sample hash, raw official capture hashes, generated artifact hashes, environment and test results are retained. `build_manifest.json` is written after verification and does not hash itself. The report and manifests deliberately distinguish successful software tests from the unresolved factual gate.

Tests cover exact MM:SS/decimal conversion, M:60 carry, no MM.SS confusion, 100 parser rows, game uniqueness and regular-season scope, complete appearance sets and GP, zero/DNP separation, unchanged FTM/FTA, deterministic outcome-free selection, no new tolerance, disabled Part B, and unchanged prior failure artifacts. Consult `test_run.txt` and `test_summary.json` for executed results.

## 17. Remaining limitations

Official game displays are whole seconds; their conversion into mathematical seconds is exact, but their representation of true playing time may already be rounded. Endpoint failures leave hidden precision unavailable. Simple final rounding and tested per-game rounding routes do not explain all four originals. Source revisions and internal display calculations are not distinguished by the retrieved evidence. Full official game logs were obtained for the frozen sample and zero supplements, not the entire league census. Appearance-only logs omit DNP rows; explicit DNP/DND corroboration is limited to the full Christmas box score. No association evidence was used to choose, amend, or interpret a validation threshold. No commit or push was performed.
