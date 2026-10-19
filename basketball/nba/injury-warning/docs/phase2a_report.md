# Phase 2A: fixed six-team development expansion

## Scope and registration

The complete fixed batch is CLE, DEN, DET, ORL, PHI and SAS. The sampling frame contains 29 non-Boston teams sorted by numeric stable NBA team ID; `random.Random(20240218).sample(frame, 6)` selects six, with no outcome-dependent selection or redraw. The full frame, code fingerprint, dates and familiarity disclosure are in [sample_v1.json](../phase2a/registration/sample_v1.json). Commit **d2a8c3030951ede574ddf279c39d789a2d8340a3** preceded selected-team outcome review; its SHA-256 is `2344541f05c12d22587a1c7d50ab95fa4c5b9152fdd2072556a7e8c7bb32b286`. Earlier amendments and the Phase 1D checkpoint pass their preserved hashes. Prior familiarity, particularly PHI/Embiid and Boston/transfer cases, is explicitly acknowledged. Randle/Ball were not sampled; no selected fixture rows were imported.

Index game dates remain January 1–February 18, 2024. The panel contains 132 selected-team game exposures, 117 distinct physical games, 122 distinct roster-inventory players and 108 players with a positive-minute candidate appearance. There are 1452 appearance-defined candidates per timing rule. Shared files are acquired once; a player-game-lag decision and an absence event each have one canonical ID. Different lag analyses are never pooled as independent observations.

The target remains **prolonged injury-related absence onset**: a new documented injury-attributed run starts in `(decision, decision + 14 elapsed days]` and subsequently reaches >=10 consecutive applicable-team missed games, with supported common-episode attribution. Decisions are next-day noon America/New_York, plus an independently rebuilt additional-calendar-day noon sensitivity. It is not biological injury-onset prediction or demonstrated prevention. Clinical-onset and medical-severity analyses through Phase 1D remain separate. **No model, imputation, scaling or feature selection was fitted; no protected holdout was opened.**

## Team and pooled results

All six teams were completed irrespective of event count. Roster inventory includes nonappearing players and the transaction-only DET/House contract record; no unobserved zero-minute game is fabricated for that intraday roster spell. Eligibility is applied to appearances. `qualifying_events_broad_onset_period` means confirmed starts during Jan1–Mar3 (the collected onset extension); all four confirmed events in that interval also start within Jan1–Feb18. It does not include older December/prevalent runs. Zero confirmed events is not proof that unresolved runs are negative.

| team | extra_lag_days | games | roster_players | candidate_appearances | included | excluded | eligibility_unknown | positive | negative | outcome_unknown | qualifying_events_broad_onset_period | events_with_eligible_prediction | missing_history |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLE | 0 | 21 | 19 | 215 | 214 | 1 | 0 | 0 | 212 | 2 | 0 | 0 | 2 |
| DEN | 0 | 21 | 18 | 229 | 229 | 0 | 0 | 0 | 226 | 3 | 0 | 0 | 0 |
| DET | 0 | 22 | 29 | 239 | 237 | 2 | 0 | 2 | 185 | 50 | 1 | 1 | 7 |
| ORL | 0 | 23 | 18 | 271 | 250 | 6 | 15 | 1 | 246 | 3 | 1 | 1 | 0 |
| PHI | 0 | 22 | 21 | 239 | 236 | 3 | 0 | 6 | 172 | 58 | 2 | 2 | 1 |
| SAS | 0 | 23 | 19 | 259 | 259 | 0 | 0 | 0 | 244 | 15 | 0 | 0 | 3 |
| CLE | 1 | 21 | 19 | 215 | 205 | 2 | 8 | 0 | 203 | 2 | 0 | 0 | 2 |
| DEN | 1 | 21 | 18 | 229 | 220 | 0 | 9 | 0 | 219 | 1 | 0 | 0 | 0 |
| DET | 1 | 22 | 29 | 239 | 224 | 2 | 13 | 3 | 171 | 50 | 1 | 1 | 4 |
| ORL | 1 | 23 | 18 | 271 | 237 | 4 | 30 | 1 | 234 | 2 | 1 | 1 | 0 |
| PHI | 1 | 22 | 21 | 239 | 227 | 4 | 8 | 6 | 165 | 56 | 2 | 2 | 3 |
| SAS | 1 | 23 | 19 | 259 | 246 | 1 | 12 | 0 | 232 | 14 | 0 | 0 | 4 |

Boston is the previously inspected pilot and remains separate. The combined table is development accounting only. Physical games are deduplicated; different teams' roster appearances are distinct player observations. Distinct players are computed from stable IDs rather than added team counts.

| scope | extra_lag_days | team_game_exposures | distinct_physical_games | recently_active_players | candidate_appearances | included | excluded | eligibility_unknown | positive | negative | outcome_unknown | confirmed_qualifying_events | events_with_eligible_prediction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| new_fixed_six | 0 | 132 | 117 | 108 | 1452 | 1425 | 12 | 15 | 9 | 1285 | 131 | 4 | 4 |
| Boston_previously_inspected | 0 | 23 | 23 | 16 | 246 | 244 | 2 | 0 | 0 | 244 | 0 | 0 | 0 |
| combined_development_not_validation | 0 | 155 | 138 | 124 | 1698 | 1669 | 14 | 15 | 9 | 1529 | 131 | 4 | 4 |
| new_fixed_six | 1 | 132 | 117 | 108 | 1452 | 1359 | 13 | 80 | 10 | 1224 | 125 | 4 | 4 |
| Boston_previously_inspected | 1 | 23 | 23 | 16 | 246 | 234 | 2 | 10 | 0 | 234 | 0 | 0 | 0 |
| combined_development_not_validation | 1 | 155 | 138 | 124 | 1698 | 1593 | 15 | 90 | 10 | 1458 | 125 | 4 | 4 |

Core joins: [cohort](../phase2a/tables/cohort_all_roster_candidates.csv), [row outcomes](../phase2a/tables/row_outcomes.csv), [B features](../phase2a/tables/features_B.csv), [event links](../phase2a/tables/row_event_links.csv), [membership spells](../phase2a/tables/membership_spells.csv), [source receipts](../phase2a/source_manifest.jsonl), [table dictionary](../phase2a/table_dictionary.json).

The sampled main analysis has 9 positive, 1285 negative and 131 unknown labels among 1425 included rows, alongside 15 eligibility-unknown candidates. The sensitivity has 10 / 1224 / 125 among 1359, with 80 eligibility unknowns. Unknowns remain in the tables and denominators. No annual injury-rate or league-wide generalization is estimated. Multiple positive rows preceding one event are not independent events.

## Event adjudication and disclosure timing

Stage A identifies nonappearance envelopes from complete applicable-team sequences. Stage B reviews injury reasons, episode identity, first injury miss, actual minute-bounded game start, returns, mixed reasons, roster changes and censoring. Every positive and every unresolved potentially qualifying/censored envelope has a [detailed review](../phase2a/tables/detailed_event_reviews.csv); [event_game_evidence.csv](../phase2a/tables/event_game_evidence.csv) supplies each game/source. Short closed complete blocks can fail severity without a clinical identity assertion. Unknown, G League, coaching, rest, illness and suspension entries are never silently counted as injury games. No separate short runs are added together.

Four confirmed new absence events are retained: Gary Harris (Jan5; 14 actual injury-attributed misses), Melton (Jan15; 18), Livers (Jan24 after moving DET to WAS; at least the 15 explicitly linked misses through Feb25), Embiid (Feb1; 29). These counts are extracted from the full acquired sequences and explicit independent narratives, not assigned from name recognition. Gary/Kevon Harris surname ambiguity is resolved by full-name game-target reports and actual inactive identity; Mobley family names are similarly guarded. The Melton, Harris and Livers continuity assertions have dated secondary/official source receipts, and Embiid uses directly reviewed NBA/AP recap locators. Later mixed causes or season/roster censoring do not undo an already demonstrated ten-game streak; they also do not establish medical recovery.

Four events have an operationally eligible preceding prediction under each timing rule. Covington stays in the unresolved event inventory with zero eligible preceding January-period predictions: his Jan6 final PDF explicitly lists illness, conflicting with a later recap's broad knee-only description. A later knee streak does not establish the initial Jan2 anchor as a homogeneous injury run. Livers's event belongs to the DET-origin sampled player but uses WAS's actual schedule; it is counted once. Ambiguous long runs including Strawther's knee/assignment envelope, Stewart's ankle/coaching/suspension envelope, Cissoko's ankle/assignment envelope, and other roster/assignment gaps remain unknown where explicit common-episode evidence or continuity is insufficient. Matching diagnoses alone are not accepted as clinical identity.

For each positive row, [positive_knowledge_review.csv](../phase2a/tables/positive_knowledge_review.csv) distinguishes the **same acute event** already disclosed under B from prior symptoms/injury history. In particular, Embiid's earlier January knee problem is not called advance disclosure of the later January30 trauma. Category A timing is unresolved for every positive. The B groups are conditional on bounded reviewed channels, not proof that all public signals were absent.

| extra_lag_days | group_B | rows | events |
| --- | --- | --- | --- |
| 0 | acute_already_disclosed | 0 | 0 |
| 0 | symptom_or_history_known | 6 | 2 |
| 0 | no_signal_found_under_searched_process | 3 | 2 |
| 0 | timing_unresolved | 0 | 0 |
| 1 | acute_already_disclosed | 1 | 1 |
| 1 | symptom_or_history_known | 6 | 2 |
| 1 | no_signal_found_under_searched_process | 3 | 1 |
| 1 | timing_unresolved | 0 | 0 |

The additional-day Harris decision is after the documented Jan3 acute event but before the Jan5 prolonged-absence start, so it is a disclosed-injury prediction. His next-day-noon Jan2 index decision precedes that event. Melton's prior back symptoms and Embiid's knee history were already visible in B channels. None of these rows is claimed as verified pre-injury warning. The B no-signal group is only absence of a signal in the searched process; biological onset and A publication timing remain unknown.

## Missingness, negative audit and features

[missingness_summary.csv](../phase2a/tables/missingness_summary.csv) reports overlapping mechanisms, including incomplete prior workload, transfer surveillance gaps, insufficient applicable-team follow-up, mixed causes and right censoring. [source_coverage_summary.csv](../phase2a/tables/source_coverage_summary.csv) separates retrieval from submission/section coverage. The parser now accepts `Philadelphia76ers` (the legacy alphabetic-only team rule dropped it) and prevents surname-only injury attribution to a different active player. Full named PDF active-box reasons also replace truncated HTML comments: generic `DND - Injury/Illness` cannot hide an explicit illness diagnosis. The [extraction correction ledger](../phase2a/tables/reason_extraction_corrections.csv) preserves these cases; [status/final-reason disagreements](../phase2a/tables/reason_evidence_disagreements.csv) remain explicit quality evidence. These are extraction corrections, not changed eligibility/endpoint thresholds.

Orlando's Feb13 baseline section remains unverified despite an additional public 6PM probe; obtained snapshots cover a different target date rather than supplying a submitted baseline. Feb16 nominal 11AM is a previously recorded access denial; the additional-day Feb14 decisions retain that gap. Failed or unsubmitted sources are never evidence that a report or injury did not exist. Exact causes are retained in cohort/report tables.

A reproducible seeded sample contains five negative rows per team per timing rule: **60 traces**. Every trace joins actual window games, source IDs, candidate severity bounds and adequate B surveillance/follow-up. Their sequence checks were inspected with the same agent; this is algorithmic/source-trace review, **not independent human adjudication**. Every unresolved/positive event also has a same-agent review record. [Readable selected timelines](phase2a_timelines.md) explain positives, negatives and unresolved cases; [traced_cases.json](../phase2a/traced_cases.json) joins all positive decisions, the negative sample, and representative unresolved decisions to eligibility, features, events and game evidence. Human review counts remain zero.

Past-only features reuse Phase1C windows `(decision-k elapsed days, decision]` for k=7/14/28, end+6h final-statistics availability, nonoverlapping prior-seven-day workload change, rest intervals and prior-appearance baseline excluding the most recent appearance. Cross-team NBA history is joined by stable player/game IDs. Missing membership, contract gaps or missing game coverage suppress affected workloads rather than zero-fill. Late same-day games cannot enter a noon feature window. Source IDs, input teams, availability maxima, missingness flags and both timing rules are retained. These are NBA workload measures, not G League or total training load. No fitted preprocessing exists.

## Availability and collection cost

A verified historical availability remains zero. B retains final stats/full recap end+6h and nominal report header+30min; timezone-aware article +60min is available only where separately justified (the new continuity articles are C-only). Current final records are mutable, and neither a retrieval date nor an extra-day lag establishes original publication. C outcomes never retroactively change eligibility or enter workload features. Historical `label_known_at` remains blank and historical training-cutoff usability false; retrospective review time is separate.

The batch has 1388 unique requested sources, 1082 new HTTP requests and 306 prior-phase cache reuses. All new requests were obtained; prior denied receipts remain gaps. New raw volume is 337,579,297 bytes. There are 554 saved dated queries in 139 search-call receipts, including 176 queries for destination follow-up rather than new prediction teams. The selected panel covers Dec4–Apr14; targeted prior/destination requests add evidence for 24 transitioning players without expanding the prediction population.

Measured initial acquisition batch wall times were 92.76 and 77.44 seconds, excluding small supplemental requests. The final extraction run took 112.06 seconds and the final cohort build 9.58 seconds on this host. Network request time sums are concurrency-weighted and are not elapsed review time. Manual person-time was not instrumented; 82 detailed event reviews and 60 negative traces quantify review units, not independent clinicians or elapsed labor. Full metadata are in [cost_summary.json](../phase2a/cost_summary.json).

## Reproduce and validate

Run from the repository root. Do not rerun sampling or redraw teams after outcomes. The committed registration is an immutable input.

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
# Optional online acquisition, resumable and deduplicated by source_id:
python3 -m phase2a.target_transfers
python3 -m phase2a.acquire
# Existing pinned PDF environment required for prepare/surveillance:
python3 -m phase2a.prepare
python3 -m phase2a.repair_active_reasons
python3 -m phase2a.build
python3 -m phase2a.render
python3 -m unittest discover -s basketball/nba/injury-warning/tests -v
```

The bundled PDF interpreter used was `/Users/zhiyuyin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`, with existing pinned pypdf/pdfplumber dependencies. Pure build/rule tests also run with system Python3.10. Offline reconstruction requires the hashed Phase1B/1C/1D/2A raw caches and the original permitted 2023–24 schedule cache referenced by Phase1B provenance. Saved search receipts reproduce the original bounded process; acquisition does not silently manufacture or rerun web searches. Query strings are saved for explicit search-service reruns. Raw PDFs, full article/recap bodies, search responses and extraction caches stay ignored/local; review tables retain short factual assertions and locators.

**73 tests pass** (59 historical plus 14 focused expansion checks): fixed sampling, unchanged prior checkpoint, IDs/deduplication, cross-team workloads and actual transfer event paths, digit/team and surname parsing, missing-history handling, actual positive/negative/unknown paths, shared-event identity, event-aware knowledge groups, negative sample coverage, and outcome/predictor separation. Cache hashes are checked where present; this run verified every newly obtained raw source. No protected-season loader or model executor is imported.

**Recommendation: repair a specific data-quality bottleneck before baseline-study planning.** Complete source-linked common-episode adjudication for unresolved long medical/assignment envelopes and verify short-contract/waiver membership gaps. Acquisition and past-only feature generation scale to this fixed batch, but four events with eligible decisions, unresolved outcomes, assumption-only publication and repeated rows per event do not yet justify model training. Do not collect until a desired positive count is reached or loosen the endpoint.
