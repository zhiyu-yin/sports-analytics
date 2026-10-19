# Phase 1C — observable Boston cohort: implementation and results

**The operational cohort and assumption-based feature pipeline now run. Broad expansion is not yet justified without improving episode onset and follow-up adjudication.** Verified historical publication remains unsupported; the useful deliverable is an explicitly assumption-based feasibility dataset, not a verified historical prediction cohort. No model was trained, no other team was added to the prediction population, and no protected holdout was opened.

## Version and amendment chronology

The user-authorized, development-data-informed [amendment v1](../phase1c/registration/amendment_v1.json) was saved and committed **before** revised labels were generated:

- Commit: `dc6dc1e3e450e038a47c509a437e31cff0753f7e`.
- Amendment SHA256: `6cc20062920630c6f3801b6e5900dcddc10598f4f891f86d01228ed1d62cb662`.
- The commit contains only the amendment, its SHA256, and the [historical-version hash manifest](../phase1c/registration/historical_version_hashes.json). It excludes the user's unrelated root README modifications.
- This is **not preregistration before development-data inspection**. Phase 1/1B findings motivated the authorized change. Their scientific documents, code, source ledger and result tables remain byte-identical; the test suite verifies those hashes.

Boston and the January 1–February 18, 2024 game-date period are unchanged: 19 roster members, 23 pilot games, 392 original candidates including transaction uncertainty. Only positive-minute appearances can enter the amended population. December 4–31 supplies history; Boston follow-up ends April 14. Neither new arrival appeared in the pilot, so no arrival received zero-filled prior-team workload features. Departed players' post-Boston severity follow-up remains unknown rather than counting the former team's games.

## Executed source process and confidence

The implementation reuses the 63 cached Boston game pages/gamebooks and existing report snapshots. Final structured statistics and the **full AP recap story** were checked for all relevant games; a video-recap excerpt alone is not treated as a complete narrative. The original 69 report snapshots were supplemented by 61 registered daily/late-evening probes. **58 new PDFs were obtained** (4,494,575 raw bytes); three returned HTTP 403: February 16, 19 and 20 at 11AM. A 403 establishes failed access, not proof that no historical report exists. No restriction was bypassed.

The combined parsed report set contains **130 probes**: 127 obtained/parsed documents and 3 unavailable. Document states are 53 complete, 15 mixed submitted/unsubmitted, 45 not-yet-submitted, 14 not covering Boston, and 3 not obtained. Target game dates and wrapped player reasons remain separate. A source can describe a game already completed; that listing is not automatically applicable to a later decision.

**61 dated official NBA/Celtics injury-news searches** were executed, one per calendar date January 1–March 1, with query text, retrieval time, result URLs and hashed local receipts preserved. Queries use `site:nba.com "Celtics" "Month day, 2024" injury`. Search-engine date matching is imperfect: returned results can be out of period or refer to other teams. Those links/snippets are not automatically used as eligibility evidence. Only directly reviewed source assertions can affect decisions. Searches document a bounded source-checking process, not an exhaustive historical news index or proof of no reports.

[New retrieval ledger](../phase1c/source_manifest.jsonl), [request catalog](../phase1c/request_catalog.json), [search ledger](../phase1c/search_ledger.json), [recap inventory](../phase1c/recap_inventory.json) and [daily coverage table](../phase1c/tables/daily_source_coverage.csv) retain provenance and gaps. Original search response text stays in the ignored local cache to avoid redistributing article bodies. Source IDs inherited from Phase 1B join its unchanged ledger. Recap dates without timezone stay as raw metadata; server modification time and present retrieval do not establish original publication.

| Category | Operational use | Result |
| --- | --- | --- |
| A: contemporaneously supported public availability | Requires defensible original/archived availability for material inputs; no B/C status used | 0 verified included rows and 0 verified feature rows |
| B: registered publication assumptions | Game final statistics and full recap at documented end upper bound +6 elapsed hours; report header +30 minutes; timezone-aware original article metadata +60 minutes only where directly supported | Actual assumption-based cohort and feature tables, clearly labeled B |
| C: retrospective evidence | Episode onset/continuity/severity review, source conflicts and baseline misclassification; forbidden for retroactive exclusion or verified predictors | 64 candidate envelopes reviewed; historical label-known times remain unverified |

For inclusion under B, the code checks final game/recap completeness and assumed publication before the decision, a submitted Boston baseline section for the indexing game, an acquired report on the decision date by the cutoff, and the executed dated news search. Not-yet-submitted or not-covered sections are retained as gaps; they do not establish health. The decision-date report requirement is a conservative implementation of adequate coverage. This is a multi-channel **bounded searched-source definition**, not medically confirmed availability or exhaustive public knowledge.

For retrospective negative labels, all expected Boston games/recaps and daily report probes in the full 14-day window are checked, dated searches are recorded, adequate remaining team-game follow-up is required, and potentially qualifying unresolved episodes make the row unknown. Isolated unavailable reports on no-game dates can be supplemented by the dated search and complete scheduled-game record under B. The February 16 failure still blocks the extra-lag **eligibility** analysis because it lacks the required acquired decision-date report. These different eligibility-versus-outcome coverage roles are explicit rather than silently interchangeable.

## Recomputed cohort funnel

Decision time is noon America/New_York on the calendar day after the documented game date. The sensitivity moves it one additional local calendar day later. Exact end seconds are unnecessary: all 23 game-end upper bounds precede both noon rules. Fourteen-day outcome horizons are **elapsed UTC time**, not 14 local date boundaries.

| Funnel / result | Next-day noon | Noon one additional day later |
| --- | ---: | ---: |
| Original candidates | 392 | 392 |
| No positive minutes: outside amended population | 146 | 146 |
| Positive-minute appearances rechecked | 246 | 246 |
| Excluded under B | 2 | 2 |
| Eligibility unknown under B | 0 | 10 |
| Operationally included under B | **244** | **234** |
| Verified A included | **0** | **0** |
| Included with known B symptom/history flag | 43 | 52 |
| Included without a known B symptom flag | 201 | 182 |

The exclusions are Porzingis's January 25 ankle sprain during the Miami game and February 14 ankle sprain during the Brooklyn game. The directly reviewed recap paragraph is retained for each. February 14's statement that he could have returned does not undo the registered exclusion for a documented new injury in the indexing game. These are B exclusions after the assumed recap-publication bound, not A-verified exclusions. Ordinary symptoms, prior injury management, and probable/questionable listings do not automatically exclude a positive-minute player.

For the additional-day rule, 10 February 14 appearances become unknown because the February 16 morning report could not be obtained; Porzingis remains excluded. All decisions, sources eligible by cutoff, risk states, windows, features and event membership were rebuilt. **182 rows included in both analyses have changed feature input-game sets**, because another game completed or an older game left the trailing/baseline history. This is not just shifting a timestamp column.

Machine outputs: [all candidate decisions](../phase1c/tables/cohort_all_candidates.csv), [included rows](../phase1c/tables/operational_included.csv), and the **392-pair [lag comparison](../phase1c/tables/lag_sensitivity_comparison.csv)**. Appearance is a population criterion, not proof the player finished uninjured. No later return or retrospective diagnosis changes an earlier inclusion decision.

## Episode review and three separate outcomes

All **28 original injury-attributed absence leads map once to 19 reviewed candidate envelopes**. Those are not 19 confirmed new injuries. Across the available history/follow-up, 64 injury-bearing absence/event candidates are retained to evaluate possible outcomes. Same diagnosis, adjacent dates or matching body side alone do not establish clinical identity. The table preserves explicit site/side evidence, onset bounds, first observed Boston absence, first actual injury-missed game where established, return, run/span bounds, source IDs, locators, clinical continuity uncertainty and reviewer identity.

An absence block is a conservative candidate envelope. A closed block containing fewer than 10 team games proves no episode inside that block can produce a >=10-game run within it; this does not require claiming every absence belongs to one injury. Mixed reasons cannot count as confirmed injury games. A positive requires an explicitly supported common episode and at least 10 consecutive attributed games. A return ends the public missed-game run, but never implies medical clearance.

The public >28-day endpoint uses **first injury-attributed missed-game date to first return date, end-exclusive**. A positive censored lower bound requires a documented later injury-related missed game, supported continuity and a span strictly >28 days. The passage of time alone never supplies a lower bound. Left-censored injury history or prior-team episodes have unknown first missed game and severity upper bounds; first observed Boston absence is not silently substituted as the true episode start. No offseason is added.

Two new in-game ankle events have directly documented onset dates represented as whole-day intervals. Other candidates retain unknown onset lower bounds and a latest-possible bound from the first observed injury absence. That bound is **not an invented onset at the first missed game**. Definite in-window membership requires the entire onset interval inside `(decision_at, decision_at+14 elapsed days]`. Previously known onset cannot become a future event. Retrospective prevalent flags remain separate from prospective exclusion.

| Included-row labels | Next-day noon | Additional-day noon |
| --- | ---: | ---: |
| Primary >=10 games: positive | 0 | 0 |
| Primary >=10 games: negative | **110** | **103** |
| Primary >=10 games: unknown | **134** | **131** |
| Public-record >28-day span: positive | 0 | 0 |
| Public-record >28-day span: negative | **110** | **103** |
| Public-record >28-day span: unknown | **134** | **131** |
| Original medical >28-day row outcome: unknown | 244 | 234 |
| Defensible historical label_known_at | 0 | 0 |

The two public outcomes happen to have identical counts in this pilot; they have separate functions/columns and independently tested thresholds. **Confirmed qualifying new events: zero for each public endpoint.** This does not assert zero injuries, zero unreported injuries or zero potentially qualifying unresolved events. It is not evidence about model performance. The original medical endpoint remains distinct: two directly bounded short episodes have negative medical-severity judgments at the episode level, but a full medical row-outcome surveillance basis was not established.

Negative means **no qualifying documented event under this registered searched-source process and sufficient follow-up**, not absence of all injuries. The main analysis's 134 unknown labels consist of 118 rows exposed to unresolved season-end candidates among the six main rotation players, and 16 rows for departed Stevens/Banton with uncollected post-trade severity follow-up. The late candidates have unbounded earlier onset and right-censored injury/rest mixtures. Their possible onset cannot be narrowed using later appearances as proof of health. They therefore remain potentially relevant under conservative bounds, even though their first recorded absence is much later than the pilot.

That is a major remaining measurement limitation. April 12's recap describes nagging ailments and an effective rest night, while gamebooks give injury reasons; April 14's recap says the starting lineup rested. These narratives do not justify declaring a solely noninjury cause or inventing a new onset date. Both sources are recorded in the [remaining review queue](../phase1c/tables/remaining_review_queue.csv). Its nine candidates include six such season-end conflicts and three left-censored history/prior-team candidates. The latter do not create new arrival observations or zero-filled features.

Detailed outputs: [episode candidates](../phase1c/tables/episode_candidates.csv), [game-level episode evidence](../phase1c/tables/episode_game_evidence.csv), [original-lead mapping](../phase1c/tables/original_lead_mapping.csv), [row-event links](../phase1c/tables/row_event_links.csv), [independent row outcomes](../phase1c/tables/row_outcomes.csv) and [window coverage](../phase1c/tables/window_source_coverage.csv). Retrospective ascertainment dates are recorded, but historical label_known_at stays blank with explicit uncertainty. No retrospective outcome label is represented as available at an earlier training cutoff. Review was performed by Codex, the same agent as earlier phases; independent human adjudications remain zero.

## Features, timing sensitivity and data quality

[Assumption-based feature rows](../phase1c/tables/features_assumption_B.csv) contain 244 baseline and 234 sensitivity rows. The [verified feature table](../phase1c/tables/features_verified_A.csv) has the declared schema and zero rows. [No-known-symptom](../phase1c/tables/features_B_no_known_symptoms.csv) and [symptom-informed](../phase1c/tables/features_B_symptom_informed.csv) subsets are separate; absence of a symptom flag is not a clinical symptom-free guarantee.

Features use completed game-end upper bounds and B-publication bounds in `(decision-k elapsed days, decision]`, for k=7/14/28. They include NBA minutes/appearances, nonoverlapping prior-seven-day minutes, seven-day workload change, elapsed rest since last observed appearance/team game, indexing-game and latest-game back-to-back flags, and a prior-28-day personal mean excluding the most recent appearance plus its deviation. Empty history is not imputed to zero. An additional Boston game can enter the lagged decision's inputs only if its completion and assumed publication precede that decision.

Feature provenance retains input game IDs and latest assumed input time. No future absence, future return, retrospective diagnosis, full-season baseline or model preprocessing is used. History is NBA/Boston workload, not total basketball workload; G League workload was not obtained. All included players have the cached 28-day Boston history window; the arrivals never enter the appearance-defined population. A first prior-appearance baseline can still be missing and remains missing.

Cached final statistics are mutable historical measurements, not verified original vintages. The prior source's `33:60` minute value and the three-second team-total discrepancy remain flagged in [source-quality issues](../phase1c/tables/source_quality_issues.csv). The March minute carry is outside pilot feature windows; the history discrepancy can affect a small past workload value and is not silently corrected. Raw recap dates without timezone and source corrections cannot become verified publication times merely because a noon or extra-day lag is applied.

Six fully traced index-player examples, with both lag rules where applicable, are available in [readable timelines](phase1c_timelines.md) and [linked JSON traces](../phase1c/traced_timelines.json). They include both excluded Porzingis events, a Tatum row whose feature inputs change after another game, Pritchard's process-defined negative, Kornet's uncertain-onset short run and Walsh's extra-day source gap. Each trace joins actual input sources, eligibility, endpoint judgments and feature provenance.

## Reproduce and validate

New Phase 1C files are separate from all historical outputs. From the repository root:

```sh
export PYTHONPATH=basketball/nba/injury-warning/src
python3 basketball/nba/injury-warning/scripts/acquire_phase1c.py
# Optional explicit retrieval of missing request-catalog sources; prior receipts are reused:
python3 basketball/nba/injury-warning/scripts/acquire_phase1c.py --fetch
# Use the existing pinned PDF dependencies / bundled interpreter for the parser:
python3 basketball/nba/injury-warning/scripts/parse_phase1c_sources.py
python3 basketball/nba/injury-warning/scripts/build_phase1c.py
python3 basketball/nba/injury-warning/scripts/render_phase1c.py
python3 -m unittest discover -s basketball/nba/injury-warning/tests -v
```

The saved news queries were executed through the available web search tool, not an invented shell/API endpoint. Their cached receipts and compact query ledger support the offline coverage rebuild; repeating a mutable search need not return identical results. Parsing reuses the existing PDF parser without modifying it. Raw acquisition is ignored/local; the source ledgers, compact metadata, tables and [table dictionary](../phase1c/table_dictionary.json) remain reviewable. Exact offline reconstruction requires the hashed original and new raw caches. The command sequence never invokes model executors or a holdout opener.

**45 tests pass**: all 32 earlier tests plus 13 new tests covering bounded end before noon, elapsed horizons/DST, in-game versus future onset, prospective exclusion versus retrospective prevalence, uncertain onset boundaries, interrupted ten-game runs, strict >28-day proxy bounds, left censoring, unknown surveillance, transfer follow-up, incomplete history, genuinely rebuilt lag inputs, source-time limits, preserved historical hashes and one-to-one lead mapping. They verify implementation and evidence consistency, not medical truth or archive completeness.

## Recommendation

The amendment successfully turns an all-unknown availability pilot into an operational **B-assumption cohort** with linked features, conditional outcomes and explicit A/C separation. The ingestion and sensitivity pipeline is reusable. It is **not yet ready for unqualified broad development-cohort expansion**, chiefly because 134/244 baseline outcomes remain unknown, historical label availability is unsupported, and late mixed injury/rest episodes have onset bounds too broad to resolve many early rows.

The smallest next step is to adjudicate the six consequential season-end candidates and document episode-specific onset/continuation evidence, plus a defensible approach to post-transfer follow-up. If the evidence remains insufficient, keep those outcomes unknown and reconsider whether the source-defined task can support a useful development cohort before collecting more teams. Do not relax onset rules or relabel season-end rest to obtain negatives. No model or holdout action is warranted at this stage.
