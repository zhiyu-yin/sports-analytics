# Phase 2D cumulative audit and fixed remaining-team census

Stage1 reconciled19 events,18 players,17 main-noon and16 extra-day events with opportunities;3067 main included rows=57 positive+2817 negative+193 unknown. See `stage1/audit_report.md`, original evidence inventory, actual-game overlap review and57/52 opportunity rows. Stage1 preceded registration and new-team outcome review. Historical Phase1–2C files remain hash-verified unchanged.

Registered seed20240220 order: WAS/MIN/CHA/POR/MIL/UTA; CHI/PHX/BKN/GSW/HOU/TOR; IND/MIA/NOP/LAL/LAC. All17 teams completed;30 prediction teams in the provenance-preserving union. This is a development-period census, not unseen validation. Prior transfer, fixture and opponent familiarity is disclosed. Endpoint, windows, noon ET timings, source clocks and common-identity standards remain frozen. No model, preprocessing fitting, tuning or protected holdout was opened.

## Results and limitations

| scope | extra_lag_days | included | excluded | eligibility_unknown | positive | negative | outcome_unknown | distinct_qualifying_events | events_with_eligible_prediction | missing_workload |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Boston_prior | 0 | 244 | 2 | 0 | 0 | 244 | 0 | 0 | 0 | 0 |
| Boston_prior | 1 | 234 | 2 | 10 | 0 | 234 | 0 | 0 | 0 | 0 |
| first_six_phase2b | 0 | 1425 | 12 | 15 | 11 | 1285 | 129 | 6 | 5 | 13 |
| first_six_phase2b | 1 | 1359 | 13 | 80 | 11 | 1224 | 124 | 6 | 5 | 13 |
| second_six_phase2c | 0 | 1398 | 14 | 42 | 46 | 1288 | 64 | 13 | 12 | 43 |
| second_six_phase2c | 1 | 1341 | 27 | 86 | 41 | 1235 | 65 | 13 | 11 | 41 |
| phase2d_batch1 | 0 | 1485 | 6 | 45 | 17 | 1327 | 141 | 5 | 4 | 20 |
| phase2d_batch1 | 1 | 1484 | 16 | 36 | 17 | 1330 | 137 | 5 | 4 | 23 |
| phase2d_batch2 | 0 | 1380 | 18 | 11 | 16 | 1291 | 73 | 8 | 6 | 34 |
| phase2d_batch2 | 1 | 1319 | 23 | 67 | 15 | 1230 | 74 | 8 | 6 | 30 |
| phase2d_batch3 | 0 | 1176 | 15 | 30 | 25 | 1125 | 26 | 6 | 5 | 21 |
| phase2d_batch3 | 1 | 1125 | 20 | 76 | 25 | 1076 | 24 | 6 | 5 | 18 |
| combined_30_team_development | 0 | 7108 | 67 | 143 | 115 | 6560 | 433 | 37 | 32 | 131 |
| combined_30_team_development | 1 | 6862 | 101 | 355 | 109 | 6329 | 424 | 37 | 31 | 125 |

`tables/scope_results.csv` and `team_results.csv` retain Boston, audited first six, second six, each fixed new batch and the30-team union. Distinct physical games differ from team-game exposures. Player IDs are deduplicated. Contract-only entries without game rosters remain a separate inventory, never fabricated appearances. Canonical event IDs are supported by actual overlapping game evidence in `cross_batch_actual_game_overlap.csv`; transfer-followup duplicates are counted once. Historical label rows are not enriched by newly reviewed sources. Source-version differences are explicit in `canonical_event_duplicates.csv`.

`event_inventory.csv` gives each qualifying anchor interval, confirmed actual consecutive medical games, common-episode assertion and locator, source URLs, earliest eligible opportunity and counts under both timing rules. `available_opportunities.csv` retains lower/upper elapsed lead days. Bins require the complete interval within >0–3,>3–7,>7–14 days; otherwise boundary-uncertain. These are available prediction opportunities, not successful warnings or detections. Repeated decisions share events and are not independent samples.

Knowledge hierarchy is mutually exclusive under assumption B: unresolved B timing, same acute event disclosed, recent acquired injury/symptom evidence within28 days, older acquired history only, no signal found under bounded search. Overlapping flags/source IDs remain. Recent evidence is not a claim of biological recent symptom onset. All A original-publication timings remain unresolved separately. Different decisions for one event can occupy different groups, so event counts across groups overlap. C linkage describes eventual-event relations only; C does not enter predictors or prospective eligibility. No searched signal is proof of being symptom-free.

`identification_ranges.csv` shows positive/included through(positive+unknown)/included. These are worst-case positive-label identification ranges, not confidence intervals or injury-rate/annual-incidence estimates. Missing workload, incomplete actual-team attribution and surveillance gaps remain explicit; no zero fill. Later coaching, assignment, rest and unknown entries do not count toward ten and cannot erase an established qualifying segment. Original ambiguous anchors are never shifted to create positives.

## Source efficiency, new defect and review

The immutable global index preserves all receipt versions and verifies raw hashes. Earliest usable success is stable; a previous failure does not suppress a legitimate later success. Denied URLs with no valid success are not automatically retried. The dry run removed590 duplicate catalog entries:1520 cached usable sources,106 needing full-scope report parsing,3 prior failed/invalid sources,125 genuinely new core requests. Core and supplement budgets are separate. `actual_usage.json` reports137 actual HTTP requests (125 core+12 supplements;136 obtained,1 denied),804 new dated queries across201 saved calls,267 reused dated queries and22 continuity queries (18 with saved bodies,4 additional interactive queries retained in chat only). Response bytes:40,949,351. No new HTTP URL was requested twice; no fees/accounts or restriction bypass.950 source game pages and950 official books were clock-audited with no unresolved endpoints, reusing hash-matched prior clock evidence. Additional search hits from other seasons were not cohort evidence.

A genuine name-suffix adapter defect was discovered: page “Jimmy Butler III” versus report “Butler, Jimmy”, and suffix stripping after punctuation removal missed recap proposals. Corrected keys remove suffixes before canonicalization and retain full first/family identity; surname-only matches never become report identity. Ambiguous opponent/surname proposals remain manually rejected. New suffix proposals were explicitly reread. `quality/suffix_before/` preserves counterfactual Phase2D outputs, and `suffix_repair_row_impact.csv` plus count ledger isolate the repair; volatile retrospective review timestamps are excluded from semantic change counts. Included/positive/negative/unknown totals did not change; name-linked observations, reasons and knowledge fields did. The nested runtime binding was also hardened to restore inner overrides before outer bindings; this affects context cleanup, not research labels. Historical files remain unchanged; no thresholds or evidence rules changed. The semantic repair ledger contains442 changed rows:33 player-game reasons,30 status observations,225 cohort metadata rows and154 outcome knowledge rows; no workload feature or outcome-label changes. A historical alias audit found one prior Phase2C Jemison assignment snapshot, already expired before availability; it has no medical-history, eligibility, label or workload effect and remains unchanged. Focused regression tests cover identity and all count reconciliation. An initial parse started before the final HTTP receipt existed and failed closed; its failed operation and successful restart are recorded, with no fabricated outputs.

Every nonnegative candidate has an event-review ledger. Important retained unknowns include Whitehead right-foot maintenance followed by left-shin stress reaction, LaVine ankle versus later foot surgery (coach says ankle no longer limiting), Okogie one hip plus nine abdominal games, Herro knee resolution followed by foot tendinitis, Love coaching/unknown interruptions, and uncertain contracts/original anchors. Same diagnosis alone is insufficient. Primary narratives are checked against individual game evidence; narrative total missed counts do not overwrite nonmedical records.

The cumulative `tables/human_review_packet.csv` and per-batch packets include all confirmed positives, consequential unknowns and five seeded negative traces per team per timing (170 original-source rereads in the final samples; earlier pre-fix reread operations are separately logged). Direct URLs, factual assertions and locators are included; accept/amend/reject/reviewer fields are blank. Same-agent review is not independent human adjudication. Activity logs measure elapsed machine operations and source review counts; durations can overlap and are not cognitive labor or human hours. No retrospective labor estimate is invented.

## Next research phase

Recommend one bounded Phase3A: independent adjudication of all confirmed events and consequential unknowns, followed by preregistration of a very limited baseline study plan. Plan a small fixed workload/rest feature set, player/event grouping, time-respecting availability and labels, and explicit missing-label analyses before any fit. The broader event distribution supports planning, but does not establish model feasibility or predictive success. Event concentration, one season and short indexing period, assumed original publication, unknown labels, historical batch differences and absent independent adjudication still limit inference. Do not treat thousands of repeated rows or an arbitrary events-per-variable threshold as sufficient evidence. No further collection or fitting was started.

## Reproduction

Use existing checksummed ignored raw caches from all historical manifests and Phase2D, raw search receipts and recap review-card inputs. Raw PDFs, full article bodies, search responses, environments and credentials remain ignored. Root README user changes remain untouched. Registration is immutable; do not rerun/redraw it. Rebuilding historical batches is not required and would silently change provenance.

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
# Python below must contain pypdf/pdfplumber; bundled runtime can be used.
python3 -m phase2d.audit
python3 -m phase2d.sources
python3 -m phase2d.runtime acquire
# Actual dated-search receipts are required inputs, not fabricated success rows.
for batch in 1 2 3; do
  python3 -m phase2d.runtime initialize "$batch"
  python3 -m phase2d.membership target "$batch"
  python3 -m phase2d.runtime prepare "$batch"
  python3 -m phase2d.runtime clocks "$batch"
  python3 -m phase2d.review cards "$batch"
  python3 -m phase2d.review apply "$batch"
  python3 -m phase2d.event_review inherit "$batch"
  python3 -m phase2d.runtime build "$batch"
  python3 -m phase2d.runtime audit_negatives "$batch"
  python3 -m phase2d.runtime packet "$batch"
  python3 -m phase2d.checkpoint save "$batch"
done
python3 -m phase2d.report
python3 -m phase2d.quality
python3 -m unittest discover -s basketball/nba/injury-warning/tests -q
```

Source-index dry-run outputs were committed before network acquisition. Re-running its report is a deterministic rebuild of historical receipts. Acquisition is resumable by canonical URL, including own successes/failures; no automatic denied-endpoint retry. C-only supplements are enumerated in `supplement_requests.json` and use their own quota. Saved manual source assertions and raw review cards are auditable inputs. Parse and result hashes protect historical outputs and source provenance.
