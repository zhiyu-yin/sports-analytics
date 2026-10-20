# NBA injury-warning research: checkpoint through Phase 2D

The current observable target is **a new documented injury-attributed absence run starting within the next 14 elapsed days and subsequently reaching at least 10 consecutive missed applicable-team games**. Its anchor is the first injury-attributed missed game, using a documented timestamp interval. A positive requires supported common-episode attribution. An appearance ends a missed-game run; it does not establish medical recovery or bound clinical symptom onset.

This is a feasibility study of prolonged injury-related absence onset. It does not demonstrate predictive success or injury prevention. **No model has been trained and no protected holdout has been opened. Phase 3A has not started.**

## Completed phases and findings

- **Phase 1:** defined separate clinical-onset, medical-unavailability and missed-game questions, inventoried public sources, and assembled 25 review candidates. These are audit candidates, not an adjudicated training cohort. [Report](docs/phase1_report.md), [labeling specification](docs/labeling_specification.md), [review table](docs/audit_review.md).
- **Phase 1B:** completed a bounded Boston 2023–24 longitudinal pilot and six selected external case audits. Original publication times and positive historical availability remained unresolved. [Report](docs/phase1b_report.md), [timelines](docs/phase1b_timelines.md), [case reviews](docs/phase1b_case_audits.md), [registration](pilot/registration/design.json).
- **Phase 1C:** registered explicit publication assumptions and next-day-noon eligibility, plus an additional-calendar-day sensitivity analysis. The 392 candidates yielded 244 and 234 included assumption-based rows. Clinical-onset labels were respectively 0 positive / 110 negative / 134 unknown and 0 / 103 / 131. [Report](docs/phase1c_report.md), [amendment](phase1c/registration/amendment_v1.json).
- **Phase 1D:** audited all 118 consequential baseline clinical unknowns (233 records across both timing rules), collected destination-team follow-up, and validated the positive path with separate Randle/Ball integration fixtures. Nine Banton rows per timing rule were resolved on severity evidence; seven Stevens rows remained clinically uncertain. Clinical labels became 0 / 119 / 125 and 0 / 112 / 122. The separately registered observable run-onset endpoint gave 0 / 244 / 0 and 0 / 234 / 0. These conditional negatives do not prove absence of unreported injury. [Report and reproducible results](docs/phase1d_report.md), [alternative registration](phase1d/registration/alternative_v1.json), [summary](phase1d/summary.json), [row-level linkage audit](phase1d/tables/unknown_row_linkage_audit.csv).

- **Phase 2A/2B:** expanded to a fixed six-team development batch and audited source clocks, knowledge timing, transfers and qualifying injury subruns. Separate protocol and clock amendments precede the corresponding results. [Phase 2B report](docs/phase2b_report.md).
- **Phase 2C:** completed a second fixed six-team batch, preserving earlier outputs and auditing cumulative canonical events. [Report](docs/phase2c_report.md).
- **Phase 2D:** audited the existing cumulative events, then completed the registered remaining 17 teams in three fixed batches. The resulting **30-team 2023–24 development-period collection** covers 680 team-game exposures (340 physical indexing games), 549 roster players and 497 recently active players. Index decisions span January 1–February 18, 2024; workload history starts December 4, 2023; onset surveillance extends through March 3 and severity follow-up through return, decisive bound or regular-season censoring on April 14. [Report and full reproduction sequence](docs/phase2d_report.md), [registration](phase2d/registration/scope_v1.json), [results](phase2d/tables/scope_results.csv), [human review packet](phase2d/tables/human_review_packet.csv).

At next-day noon America/New_York, 7,108 included decisions have **115 positive / 6,560 negative / 433 unknown** outcomes. The additional-local-calendar-day sensitivity has 6,862 included decisions and **109 / 6,329 / 424** outcomes. There are 37 canonical confirmed events in 36 players; 32 events have eligible main-rule opportunities (31 under the sensitivity rule). These are descriptive, assumption-based labels, not predictive performance. Duplicate event records were reconciled; 170 seeded negative traces were reread against original sources. Independent human adjudication remains **zero**, and reviewer decisions remain blank. No model, preprocessing fit, tuning or evaluation of predictive success has occurred.

The clinical-onset outcome, >28-day public absence-span outcome and original medical-unavailability outcome remain separate. Clinical onset and continuity remain insufficiently observable for general biological injury prediction. Selected external fixtures are integration tests only: they are excluded from Boston cohort counts, prevalence estimates and future training/evaluation data. Independent human adjudication remains outstanding.

The Phase 1C amendment commit `dc6dc1e` and Phase 1D alternative-registration commit `facea5b` precede this checkpoint and are preserved without rewriting. The Phase 1D registration was committed before its alternative results were generated. Earlier registrations and output hashes remain preserved in the phase directories.

## Publication assumptions and limitations

Category **A** requires verified historical availability; none has been established. Category **B** explicitly assumes final game statistics/full recaps are available at game-end upper bound +6 hours, injury-report snapshots at nominal header +30 minutes, and qualifying timezone-aware article metadata +60 minutes where used. These are assumptions, not independently verified first-publication timestamps. Current historical records may have been revised.

Both local-noon timing rules retain the registered source-coverage checks. The bounded report probes, dated news searches and expected game records do not constitute an exhaustive historical archive; an obtained decision-day report may still contain unsubmitted team information. Missing source coverage, mixed attribution, unresolved transfers and incomplete follow-up remain uncertainty conditions. No absence is automatically an injury, and no later appearance proves health. Workload covers observed NBA team history, not all basketball activity.

Category **C** contains retrospective outcome evidence. It does not enter historical predictors or retroactively alter prospective eligibility. `historical_label_known_at` remains blank; retrospective ascertainment dates are stored separately and do not establish historical training-cutoff usability. The zero-positive Boston result and selected-case positives support pipeline checks, not predictive performance. The 30-team collection is complete for this bounded development window. It does not estimate a league-wide annual injury rate. Repeated decisions are correlated, events are concentrated, and source gaps, membership uncertainty and unresolved common-episode attribution limit inference. No protected holdout has been opened and no model has been trained.

## Reproduction and raw-cache requirements

From the repository root, use Python 3.10+ for rules, builds and tests. PDF extraction additionally needs the pinned [requirements](requirements-phase1b.txt) in an existing suitable environment:

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
python3 -m unittest discover -s basketball/nba/injury-warning/tests -v

# Phase 1D extraction and offline rebuild, with the required caches present:
python3 -m phase1d.prepare
python3 -m phase1d.build
python3 -m phase1d.render
```

The frozen Phase 2D scientific snapshot passes **112 tests**. The tests include endpoint counterexamples, real-case integration, transfer schedules, evidence separation and preserved-output hashes. They do not establish medical completeness. Earlier phase reports document their acquisition/build commands; do not rebuild historical outputs in place merely to reproduce Phase 1D.

Exact offline reconstruction requires local ignored caches under `data/raw/evidence`, `data/raw/phase1b`, `data/raw/phase1c` and `data/raw/phase1d`, including the hashed original search receipts. It also requires the existing 2023–24 development schedule cache named in [schedule provenance](pilot/schedule_provenance.json). Only permitted historical schedule dates/IDs are used; no protected-season outcome is opened. Source manifests, request catalogs, registrations, short evidence locators and reviewable derived tables are versioned; raw PDFs, full article bodies and search response bodies are not distributed.

Optional targeted acquisition reuses existing receipts:

```sh
python3 -m phase1d.acquire
```

A fresh download or search can differ from the saved historical snapshot. Acquisition does not reproduce the web-search service: executed queries and receipt hashes are retained in the search ledgers, while response bodies remain local. Rebuilding requires the original matching caches; it must not silently replace them or fabricate coverage. The offline test suite is available without installing PDF dependencies; source-hash checks use local caches where present.

## Artifacts

- [Phase 1D table dictionary](phase1d/table_dictionary.json), [fixture decisions](phase1d/tables/fixture_rows.csv), [transfer reviews](phase1d/tables/transfer_row_review.csv).
- [Phase 1C table dictionary](phase1c/table_dictionary.json), [traced timelines](docs/phase1c_timelines.md).
- [Pilot table dictionary](pilot/table_dictionary.json), [human review queue](pilot/tables/user_review_queue.csv).
- [Source register](audit/sources.json), [retrieval receipts](audit/retrieval_receipts.json), [schemas](schemas/injury_episode.schema.json), [deferred modeling plan](docs/modeling_plan.md).

## Phase 2D checkpoint reproduction

The current README is a mutable status index. Historical preservation manifests include its earlier bytes; those manifests and registrations have not been rewritten. To run the complete frozen integrity suite or rebuild historical outputs, use the scientific snapshot **`1d6fd5c9d9e52edffa96cc6488037b504c7ab95e`** in a separate checkout. Running its preservation checks against this updated status README intentionally detects documentation drift.

```sh
# From repository root; creates an isolated historical checkout without changing branches.
git archive 1d6fd5c9d9e52edffa96cc6488037b504c7ab95e | tar -x -C /path/to/existing-empty-reproduction-directory
cd /path/to/existing-empty-reproduction-directory
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
python3 -m unittest discover -s basketball/nba/injury-warning/tests -q
```

Full cache-dependent checks require the original local caches at the manifest-relative locations, including `data/raw/phase2a`, `data/raw/phase2b`, `data/raw/phase2c`, `data/raw/phase2d`, prior-phase evidence, original search receipts, review-card inputs and the development schedule cache. The root README is also checked against the pre-existing local user version; an exported checkout needs those same local bytes for that workspace-preservation assertion. See the [Phase 2D report](docs/phase2d_report.md#reproduction) for the ordered extraction/build/review commands and PDF dependencies. Run rebuilds in an isolated copy with matching caches: acquisition may contact the network and current responses cannot substitute silently for historical evidence. Do not rerun registrations, fabricate receipts or overwrite frozen results to obtain passing hashes.

Versioned artifacts contain code, registrations, technical reports, short evidence locators, source/hash metadata and reviewable derived tables. Raw PDFs, full article/search response bodies, credentials, environments and local caches remain excluded. Separate protocol/amendment commits retain their original chronology. **Phase 3A has not started.**
