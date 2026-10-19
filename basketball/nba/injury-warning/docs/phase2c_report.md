# Phase 2C second fixed development batch

Completed six teams: ATL, DAL, NYK, SAC, OKC, MEM. Sampling commit `f0cb5342fe7c812342fa0f1ae5f499fc3eef1ed5`; frozen Phase2B checkpoint `e2267f0592bdb806f85a6a8be0f8b0f38373f711`. Seed20240219,23-team numeric-ID frame, no redraw. Prior transfer/fixture familiarity is disclosed in the registration; this is development collection, not unseen validation. No model, preprocessing fit, tuning, protected holdout or annual-rate inference.

## Frozen target and evidence

New documented injury-related absence-run onset in the next14 elapsed days, eventually >=10 consecutive actual applicable-team injury misses with reviewed common identity. Next-day noon ET and one additional calendar-day noon sensitivity; 28-day workload/history windows, cumulative acquired history versus recent evidence and expiring game-specific status remain Phase2B rules. Qualifying maximal medical segments survive later coaching/assignment/noninjury/censoring, which do not count toward ten. Ambiguous original anchors stay ambiguous. Clinical onset and recovery are not inferred from appearances.

All game/roster/recap extraction reuses Phase2A functions; clocks, knowledge, sequence/event logic and cohort build reuse Phase2B functions through isolated runtime bindings. No copied parallel event implementation. Code hashes and original protocol/amendment commits are in `registration/collection_v1.json`. The adapter changes paths, team scope, review seed and metadata only. The old hardcoded DET contract-only inventory entry is filtered from this new six-team export. An unanswered human-review packet does not imply review occurred. Contract-only transaction entries without game rosters are separately inventoried; they create no fabricated appearance or zero-minute game.

Publication A means independently verified original historical availability; none established. B assumes final stats/full recaps end-upper+6h and report nominal header+30min. New medical/return narratives and contract adjudication are C only. They do not enter features or prospective eligibility. Same-event linkage describes positive-event knowledge strata only. No searched signal is proof of being symptom-free. Cumulative history is bounded by acquired channels, not a lifetime medical record; a recent report of remote injury history does not date the original symptoms. Historical label-known-at remains blank.

## Results by versioned cohort and timing

| scope | extra_lag_days | candidate_appearances | included | excluded | eligibility_unknown | positive | negative | outcome_unknown | distinct_qualifying_events | events_with_eligible_preceding_prediction | missing_workload |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| new_six_phase2c | 0 | 1454 | 1398 | 14 | 42 | 46 | 1288 | 64 | 13 | 12 | 43 |
| new_six_phase2c | 1 | 1454 | 1341 | 27 | 86 | 41 | 1235 | 65 | 13 | 11 | 41 |
| first_six_audited_phase2b | 0 | 1452 | 1425 | 12 | 15 | 11 | 1285 | 129 | 6 | 5 | 13 |
| first_six_audited_phase2b | 1 | 1452 | 1359 | 13 | 80 | 11 | 1224 | 124 | 6 | 5 | 13 |
| Boston_prior | 0 | 246 | 244 | 2 | 0 | 0 | 244 | 0 | 0 | 0 | 0 |
| Boston_prior | 1 | 246 | 234 | 2 | 10 | 0 | 234 | 0 | 0 | 0 | 0 |
| combined_development | 0 | 3152 | 3067 | 28 | 57 | 57 | 2817 | 193 | 19 | 17 | 56 |
| combined_development | 1 | 3152 | 2934 | 42 | 176 | 52 | 2693 | 189 | 19 | 16 | 54 |

`scope_results.csv` distinguishes observed game-roster players from full membership inventory (including contract-only players with no game roster) and additionally reports physical games, team-game exposures, distinct roster/recently-active players, A/B rows, surveillance and follow-up gaps. `scope_team_results.csv` gives all teams; `positive_rows_per_event.csv` gives every event's eligible decisions. `positive_knowledge_groups.csv` separates B acute/history/no-searched-signal strata from overlapping A timing-unresolved counts. Boston is its separately preserved historical cohort; legacy knowledge fields are not silently reclassified. Fixtures contribute no cohort rows. Combined results union canonical player/game/lag decisions and player/first-miss-game event IDs; shared raw games and cross-batch transferred players are counted once. Historical first-six labels are the frozen Phase2B version, not silently enriched with new sources.

Repeated positive rows share events. Event concentration by team and player is in `event_concentration.csv` (MEM contributes7/13 new events and7/19 combined events; Rose contributes two events); do not treat row count as independent sample size. `missing_label_identification_ranges.csv` reports positive/included through (positive+unknown)/included conditional on inclusion. These are worst-case identification ranges, not confidence intervals or injury-rate estimates.

## Source and event review

Complete registered indexing period Jan1–Feb18, history from Dec4, onset-window extension through Mar3 and regular-season follow-up through Apr14. All six teams were completed, regardless of missingness/event counts. Targeted actual-team schedules and dated membership sources address trades, waivers and short contracts. Unverified periods and missing roster/reason entries remain unknown, never zero workload or injury. Exact failures and a wrong-year same-title Taj Gibson release are retained; the 2022 release was rejected for2024 inference.

Every confirmed positive and potentially qualifying unknown envelope has individual game evidence, maximal-segment output and a common-identity assertion or missing assertion. First injury anchors stay registered. Morant's game-versus-training trauma discrepancy does not change his Jan7 first-miss anchor; no unsupported indexed-game acute flag is invented. Exum's first actual Feb28 return is taken from full stats despite a Mar1 recap repeating first-return wording. Rose's later back run is separate from the earlier hamstring run; a reviewed qualifying back subset is not undone by later groin/censoring context. Existing Randle selected-fixture source familiarity is disclosed and no fixture row is added.

The same agent reviewed285 source-locator medical candidates plus eight prior-team December candidates. Opponent names, duplicate surnames, missing Jr. suffixes, figurative language, missed shots and noninjury absences are explicitly distinguished in `recap_candidate_adjudication.csv`; manually accepted PID/paragraph assertions are reproducible in `review_recaps.py`. All60 seeded negative traces were also reread from original canonical-ID game pages and official FINAL BOX PDFs through a separate source-read path; `negative_original_source_audit.csv` records source IDs and finite candidate bounds. This is same-agent verification, not independent adjudication. All60 traces are included (five/team/lag), along with every new confirmed broad-period positive and ten consequential unknowns, in `human_review_packet.md`, `tables/human_review_packet.csv` and `traced_cases.json`. Accept/amend/reject and reviewer fields are blank; independent human reviews completed:0.

## New adapter bug, isolated correction and limits

A genuine new path-binding bug made Phase2A's historical manifest follow the rebound output directory, hiding prior cache entries. This caused redundant public requests and an incomplete all-cache clock audit; it did not change research rules. Correction reads immutable historical ledgers explicitly, retains the first recorded success/failure, and invalidates parsed reports by raw-source SHA/status. Earlier results remain byte-for-byte unchanged. The pre-fix draft is preserved in `quality/source_binding_before/`; `source_binding_manifest_impact.csv`, `source_binding_row_impact.csv` and `source_binding_before_after.csv` report the exact source/row/count effects. Redundant receipts are retained in `duplicate_request_receipts.csv` and charged to acquisition effort, never represented as cache reuse. A prior denied receipt takes precedence over an accidental redundant later response; no alternative proxy or access bypass was used.

The corrected all-cache audit covers889 game pages and889 official books with no unresolved clock format; the draft covered678 pages with one missing period-clock payload. A single timing-input row changed after restoring its original cached page, while cohort labels and workload features were unchanged. The source-specific EST display-label interpretation is checked against scheduled UTC and venue-local official gamebook clocks, including date rollover and DST, with raw clocks/rules/precision in `all_acquired_game_clock_audit.csv`. Digit-containing team names and duplicate/suffixed surnames reuse the repaired parser; generic injury labels remain explicit and do not alone prove common identity. Source disagreements, contract gaps and consequential uncertainty are not removed to improve the results.

## Measured acquisition and proposed next step

Actual new HTTP requests: 1041; statuses {'obtained': 1035, 'failed': 6}; response bytes 321132389. Redundant requests caused by the adapter bug: 650. New executed dated search queries: 557 across 140 saved call receipts; reused executed targeted queries:138. More detailed counts are in `cost_and_quality.json`. The retained-source cache reused 1044 catalog entries; duplicate-URL attempts within this new ledger: 1 . Additional interactive continuity/contract lookups were performed but not fully time-instrumented; no fabricated human/agent review duration is reported.

Recommendation: preregister one fixed collection phase covering the remaining17 development teams over the same indexing dates, rather than start a fitted baseline now. Metadata-only estimate: 122 uncached core page/book requests, up to 1071 dated daily queries, plus explicit bounded transfer supplements; estimated agent review15–30 hours and independent human adjudication8–16 hours. These are prospective budgets, not measured completed work. No further teams were collected here.

The number and concentration of independent episodes, one season, unknown labels/contract gaps, assumed historical publication and absent independent adjudication still limit conclusions. No arbitrary events-per-variable threshold is used. A later baseline plan would require a small predefined feature set, time-respecting labels and independent event review; thousands of correlated decisions do not supply that justification alone.

## Reproduction

From repository root, with existing checksummed raw caches and a Python containing pypdf/pdfplumber:

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
python3 -m phase2c.targets
python3 -m phase2c.pipeline acquire
python3 -m phase2c.review_sources
/Users/zhiyuyin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m phase2c.pipeline prepare
/Users/zhiyuyin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m phase2c.pipeline clocks
python3 -m phase2c.review_recaps
python3 -m phase2c.pipeline candidates
python3 -m phase2c.adjudications
python3 -m phase2c.pipeline build
/Users/zhiyuyin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m phase2c.audit_negatives
python3 -m phase2c.report
python3 -m unittest discover -s basketball/nba/injury-warning/tests -q
```

Search receipts are immutable input records; rerunning collection does not fabricate or silently re-execute missing queries. The manual candidate inventory and prior-team medical assertions are regenerated from cached recaps. Raw requirements: all cache files referenced by Phase1–2B manifests and Phase2C `source_manifest.jsonl`, plus the actual saved dated-search response receipts under ignored `data/raw/phase2c/searches`. Acquisition is resumable; recorded failures are not retried or bypassed. Search ledgers are receipts of actual executed/reused queries, not generated success assertions. Source-ID/date assertions and manual review locators are versioned data, never inferred clinical ground truth. Raw PDFs, article bodies, search bodies, environments and credentials remain ignored. Root README user changes remain untouched and unstaged. Sampling is already registered and must not be rerun/redrawn; reuse the saved specification.
