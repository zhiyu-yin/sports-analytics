# Phase 1D: linkage audit, targeted follow-up and positive-path validation

## Decision and registration

A bounded expansion of **development-data collection for prolonged injury-related absence onset** is supportable, with the same explicit B publication assumptions and event-by-event continuity review. The clinical-onset target remains insufficiently observable for general collection or model training. No model was trained; no protected holdout was opened; Boston membership and predictors are unchanged. This selected one-team pilot contains no qualifying positive runs and cannot establish prevalence, performance or population calibration. The selected external cases test the positive path only.

The separately versioned [alternative definition](../phase1d/registration/alternative_v1.json) and preserved-output hashes were committed as `facea5b` **before** retrieval/label generation. The full commit is in `registration/commit_receipt.json`; the SHA-256 is in `alternative_v1.sha256`. The registration's `results_generated: false` records its preregistration state and is deliberately immutable. All historical Phase 1B/1C outputs and reports pass their saved hashes.

The alternative is a new documented injury-attributed absence run starting in `(decision, decision + 14 elapsed days]`, subsequently reaching at least 10 consecutive applicable-team missed games. It predicts prolonged injury-related absence onset. It does not estimate the biological moment of injury. Its first missed-game anchor is an actual first-period-start minute interval from cached play-by-play; raw clock text is retained. IANA local-date timezone rules handle source clock labels (which sometimes say EST during daylight time). If unavailable, the code retains a whole documented game-date interval. A left-censored initial block keeps its true start lower bound and severity upper bound unknown; the first observed game is not invented as a new run onset. Clinical acute events in fixtures are bounded by actual game start/end, not assigned an exact injury second or scheduled tipoff.

## Root cause: the 118 rows

Phase 1C passed every same-player candidate envelope to a clinical-onset interval test. For six April 12 candidates, lower onset was unbounded and severity right-censored; that interval intersects every earlier January/February horizon. This explains the numerical propagation, but is **not evidence of a common clinical episode, an in-window new event or prolonged injury severity**. The old potential-link output must not be interpreted as a confirmed injury linkage.

Review found no demonstrated code error establishing that all six clinical events were unrelated to all earlier windows. It found an identification limitation plus an overly broad interpretation risk in same-player candidate linkage. The Phase 1D audit explicitly marks these links **unestablished possible relevance**, distinguishes clinical symptoms/new trauma/first injury miss/run boundaries, and preserves all 118 baseline clinical unknowns. It does not assign clinical negatives using intervening play or claim medical recovery. The alternative evaluates its own observed run anchor before allowing unknown severity to affect a window; a definitely later run cannot contaminate an earlier run-onset window. This is a separately registered estimand, not a silent clinical relabeling.

The final two observed absences are April 12 and April 14. Gamebooks attribute injury reasons, while the April 12 recap describes precautionary rest context and April 14 describes resting the starters. Neither account proves solely noninjury cause or a precise new clinical onset. Each run is right-censored; none has ten documented same-episode games. For the clinical target to qualify, an unobserved in-window new onset/recurrence would have to be linked to a qualifying same-injury future run. These unproved assertions preclude a positive; available records do not safely exclude them. Intervening appearances close separate missed-game runs only.

| player | baseline_rows | lagged_rows | clinical | final_run_anchor |
| --- | --- | --- | --- | --- |
| Jaylen Brown | 20 | 20 | unknown | April 12; outside every pilot horizon |
| Jayson Tatum | 22 | 21 | unknown | April 12; outside every pilot horizon |
| Derrick White | 22 | 21 | unknown | April 12; outside every pilot horizon |
| Al Horford | 18 | 18 | unknown | April 12; outside every pilot horizon |
| Jrue Holiday | 21 | 20 | unknown | April 12; outside every pilot horizon |
| Kristaps Porzingis | 15 | 15 | unknown | April 12; outside every pilot horizon |

Evidence review distinguishes the candidates:

- Brown: April 3 and April 5 recaps discuss the left-hand problem, including play while symptomatic. This directly illustrates why an appearance cannot establish recovery or a new onset lower bound. Earlier ankle/back listings cannot be merged into the hand issue by player identity.
- Tatum: April 7 describes a right-knee contusion. Earlier ankle absences are not a demonstrated common event; no source establishes the knee's initial symptom date.
- Horford: March 23/28 and April 9 document toe-related absences. Repeated site labels support reviewing continuity but do not date biological onset or prove uninterrupted severity.
- White: March 17 names a hand sprain; the final gamebook's generic injury/illness reason does not establish identity with it.
- Holiday: March 11 describes knee soreness; later patellar listings cannot alone identify a new onset versus ongoing symptoms.
- Porzingis: March 18 explicitly links a return to five missed hamstring games; April 9 describes subsequent workload management. This supports a clinical-history relationship but also separate absence runs. It does not back-date onset to a pilot horizon or produce ten consecutive misses.

Exact cached source/paragraph locators are in [season_end_event_review.csv](../phase1d/tables/season_end_event_review.csv). [unknown_row_linkage_audit.csv](../phase1d/tables/unknown_row_linkage_audit.csv) retains every baseline row and the rebuilt lagged rows: **118 + 115 = 233**. Each records responsible candidate, bounds, onset evidence, all intervening appearance IDs/dates, run IDs/upper bounds, feasibility, final labels and reasons. [row_run_links.csv](../phase1d/tables/row_run_links.csv) separately records every run-window relation and severity bound.

## Transfer follow-up

A new hashed ledger contains 193 obtained public sources: historical game records, final gamebooks, report snapshots and two continuity articles. Destination follow-up covers **31 Memphis games and 31 Portland games**, through April 14. Each has the target player observed on the roster and page/book evidence. The local development schedule supplies dates/IDs; score/outcome fields are not exported. Destination players never enter Boston population or predictor tables. Retrieval failures and missing attribution would remain unknown.

The applicable sequence switches from Boston at the registered transaction boundary, rather than counting Boston games after departure. A separate transaction-boundary table preserves Stevens's February 7 uncertain roster row. Including that single possible boundary game cannot turn the short block before his February 12 Memphis appearance into ten games or a >28-day span. No date-level membership certainty is invented.

Banton appeared in 30 of Portland's 31 games. His April 11 ankle absence is followed by an April 12 appearance: the public run is one game. All observed possible runs across his actual team sequence are closed below the severity thresholds. His nine baseline and nine lagged clinical/public-span unknowns become negatives on severity evidence, without requiring a new clinical onset bound.

Stevens has short closed mixed/medical blocks in February, March and early April, plus two injury-attributed misses on April 12/14 with no observed return. His seven rows per timing rule remain clinical/public-span unknowns. That final run's observed start is outside every relevant early horizon, so his alternative run-onset labels are negative. Mixed coaching/trade/not-with-team reasons are never counted as confirmed injury games.

[transfer_row_review.csv](../phase1d/tables/transfer_row_review.csv) gives every row decision; [transfer_applicable_game_sequence.csv](../phase1d/tables/transfer_applicable_game_sequence.csv) gives each actual applicable game and source. The clinical result resolves **9/16**, retaining **7/16** genuine uncertainties per timing rule.

## Before/after counts

All labels below refer only to prospectively included B-assumption Boston rows. The public >28-day outcome retains the original clinical-onset window and its separate first-injury-miss-to-return span definition. It is not merged into the alternative >=10-game run-onset endpoint. The original medical >28-day endpoint is also preserved separately.

| extra_lag_days | endpoint | n | positive | negative | unknown |
| --- | --- | --- | --- | --- | --- |
| 0 | clinical_before | 244 | 0 | 110 | 134 |
| 0 | clinical_after | 244 | 0 | 119 | 125 |
| 0 | public_span_before | 244 | 0 | 110 | 134 |
| 0 | public_span_after | 244 | 0 | 119 | 125 |
| 0 | original_medical_gt28 | 244 | 0 | 0 | 244 |
| 0 | absence_run_onset_ge10 | 244 | 0 | 244 | 0 |
| 1 | clinical_before | 234 | 0 | 103 | 131 |
| 1 | clinical_after | 234 | 0 | 112 | 122 |
| 1 | public_span_before | 234 | 0 | 103 | 131 |
| 1 | public_span_after | 234 | 0 | 112 | 122 |
| 1 | original_medical_gt28 | 234 | 0 | 0 | 234 |
| 1 | absence_run_onset_ge10 | 234 | 0 | 234 | 0 |

The alternative's all-negative result means no qualifying documented run under the bounded registered B search process and reviewed applicable-team follow-up. It is not proof of health, exhaustive public reporting or absence of unreported injury. April right censoring is preserved at event level; its run start lies outside these windows. Clinical unknowns are not optimized away.

## Real-case integration fixtures

These are deliberately selected, separate **event-specific integration fixtures**, not a prevalence sample or model evaluation. Every fixture joins an actual preceding game, positive minutes, membership, completion, B end+6h final-statistics/recap availability, a submitted baseline team report, an obtained decision-day snapshot with nominal header+30min, and an executed dated news query. A decision-day snapshot can have unsubmitted team information, exactly as in Phase 1C; this remains a limitation of that B definition. A remains unverified. Source articles/returns used for severity remain C-only.

Randle's January 27 game recap records an acute shoulder event. Thirty-six injury-attributed Knicks games from January 29 to April 14 reconcile with the complete schedule and cached individual PDF assertions. The separately reviewed continuity article links the absence to that event. Ball's November 26 game recap records the ankle event; twenty consecutive Charlotte missed games have individual game/page/PDF evidence, consistent with the separately reviewed return narrative and the January 12 appearance. The generic December 8 medical DND row gets clinical identity from that independent narrative, not from a generic diagnosis string. Ball's prior surgery is retained as history; this is a documented new traumatic event/recurrence test, not a claim about first lifetime symptoms.

The common-episode review and actual number of injury-attributed games enter the generic endpoint function. Player names, case IDs and prior positive labels do not determine its result. Removing supported common-episode attribution prevents a positive. The event bounds and 56 game-evidence rows are in [fixture_events.csv](../phase1d/tables/fixture_events.csv) and [fixture_severity_evidence.csv](../phase1d/tables/fixture_severity_evidence.csv).

Examples: Randle January 25 and Ball November 22 index games are eligible and positive for both endpoints under both noon rules. Ball November 12's next-noon decision includes the November 26 trauma but ends before the November 28 first miss: clinical positive, run-onset negative. Randle January 13 similarly separates the January 27 event from the January 29 run. Earlier Randle January 1 and Ball November 10 decisions put these selected events outside their horizons. The actual injury games are excluded under the B completed-game recap assumption. Ball November 18 lacks a submitted baseline snapshot in the reviewed set and stays eligibility-unknown under both lags; no label is forced.

There are **24 fixture decision rows**: 18 included, 4 excluded and 2 eligibility-unknown. Among the included selected-event tests, clinical membership/severity gives 14 positives and 4 negatives; run onset gives 10 positives and 8 negatives. An event-specific negative here does not assert that all other possible events were surveilled. It is not exported as a cohort negative or training example. All 24 rows explicitly remain outside Boston counts and future datasets.

Full decisions, publication assumptions, exclusions and event joins are in [fixture_rows.csv](../phase1d/tables/fixture_rows.csv). Actual game-interval bounds preserve temporal precision; synthetic interval tests additionally cover unresolved onset straddling boundaries.

## Availability, reproducibility and validation

Category A verified historical availability remains zero. Category B retains both Phase 1C noon rules and all publication assumptions; no retrospective destination appearance, diagnosis or return changes Boston eligibility or features. Category C adjudicates outcomes only. `historical_label_known_at` stays blank in all outcome/fixture rows. Retrospective ascertainment is separately dated in `adjudication_metadata.json` and the cohort outcome table, with historical training-cutoff usability false. No independent human adjudication has occurred.

From the repository root, use the same PDF dependencies pinned in `requirements-phase1b.txt`:

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
# Optional online targeted acquisition; reuses hashed prior caches and does not retry recorded failures:
python3 -m phase1d.acquire
# PDF extraction requires the existing pypdf/pdfplumber environment:
python3 -m phase1d.prepare
python3 -m phase1d.build
python3 -m phase1d.render
python3 -m unittest discover -s basketball/nba/injury-warning/tests -v
```

The bundled interpreter used for PDF extraction was `/Users/zhiyuyin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`. Pure rule/build/test commands also pass with system Python 3.10. Offline reproduction requires the hashed Phase 1B/1C/1D raw caches and the original 2023-24 schedule cache. The new acquisition module touches only explicitly selected historical games/reports/articles. No game-prediction executor or holdout loader is imported.

The 25 dated fixture queries were actually executed through web search; `search_ledger.json` preserves query/date/hash receipts. Search response bodies and full narratives remain in ignored local caches, not redistributed in tracked results. Mutable search results may differ on rerun; the bounded original query protocol and saved receipts reproduce this analysis, not an exhaustive archive. The original search queries are declarative in that ledger and can be re-executed through a search tool if available. Parsing/building does not pretend to rerun them.

**59 tests pass**, including all 45 historical tests and 14 new definition-derived tests for unrelated later events, early injury with continued play, return/run separation, clinical/run disagreement, unknown boundary intervals, common-episode attribution, mixed/censored runs, actual transfer schedules/gaps, real positive fixtures, exclusions and evidence separation. Every saved historical file and every new obtained-source hash is checked. These validate the implementation and recorded evidence, not medical completeness.

The next bounded collection should use the registered observable run endpoint, retain clinical labels as a separate measurement study, and require common-episode adjudication before accepting new positives. General biological injury forecasting and historical-cutoff model training remain unsupported by these sources.
