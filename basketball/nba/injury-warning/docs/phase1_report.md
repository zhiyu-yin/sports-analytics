# Phase 1 feasibility report

Audit performed October 18, 2026 (America/New_York; retrieval receipts use UTC). Recommendation: **continue data feasibility and adjudication; do not start modeling.** The evidence supports a research workflow and real event leads, but not yet a complete point-in-time cohort or generalizable prediction claims.

## Repository and tooling inventory

No AGENTS.md was found within the repository or in checked parent locations. The root README had pre-existing user modifications; it was left untouched. Existing experiments and raw/processed datasets were not changed.

| Existing asset | Inspection and suitability |
| --- | --- |
| game-prediction/README.md and docs/v1_reproduction.md | Frozen V1; documented 2015-16 to 2025-26 team-game study. Existing temporal access guards and frozen executor restrictions must remain intact. |
| game-prediction/src/nba_game_prediction/ingest.py | LeagueGameLog retrieval, response hashing, immutable cache validation and explicit network gates are useful design patterns. Defaults are team records, not player logs. Not imported because imports and builders belong to frozen experiments. |
| game-prediction/src/nba_game_prediction/policy.py | Training 2015-16 to 2022-23; development 2023-24; 2024-25 and later protected. Directory names were inventoried without opening protected data. |
| game-prediction/data/raw/2023-24/leaguegamelog_full_*.manifest.json | Inspected metadata only: official LeagueGameLog, PlayerOrTeam=T, 2,460 team rows, GAME_ID/TEAM_ID/GAME_DATE. Suitable schedule lead; exact game-end time and player availability absent. Raw outcome payload not decoded. |
| game-prediction/data/{interim,processed} | Existing team schedules/features by season; listed directories only. Do not rerun frozen builders. |
| anthropometrics-shooting/src/anthropometrics_shooting/{shooting,combine}.py | Stable PLAYER_ID normalization patterns exist. Combine/season aggregates are not a longitudinal player-game availability cohort. |
| anthropometrics-shooting/data | Raw archive manifests and season-level free-throw panels are present; one GitHub archive metadata manifest inspected. No panel or raw payload decoded for this task. |
| shared/ | Placeholder; no reusable injury pipeline established. |
| New module runtime | Python 3.10.8 standard library. No environment installation or modification needed. System pdftotext unavailable; web PDF text extraction used for manual evidence review. |

No verified injury-episode table, timestamped complete player-game cohort, player-to-injury source identifier crosswalk, or historical injury-availability series was obtained from existing assets. This is an inspection result, not a claim that every local raw payload was searched. Those payloads were intentionally not opened.

## Sources actually verified and obtained

| Source | Actually obtained | Coverage / timestamp / retrieval limitations |
| --- | --- | --- |
| Official January 4, 2024 18:30 ET injury PDF | 82,383 raw bytes, HTTP 200, SHA256 receipt; eight-page text reviewed via browser extraction | Snapshot for January 4-5; not a season archive. Rest, illness, suspension and personal-reason listings support exclusions. Report header time is not independently verified first public availability. |
| Official January 28, 2024 12:30 ET injury PDF | 74,375 raw bytes, HTTP 200, SHA256 receipt; five-page text reviewed via browser extraction | Snapshot for January 28-29; some next-day teams not submitted. Injury/Illness prefix requires reading the actual reason. A single listing cannot establish onset, continuous absence or severity. |
| Nine selected news/game-recap/biography URLs | Manually reviewed facts and URLs retained in sources.json and candidates.csv; article bodies not archived | Event leads within 2023-24, including a November 2023 onset. News update times, missing original timezone and retrospective reports limit historical availability claims. The mutable Bane bio was used only for its 2023-24 injury section. |
| Official 2023-24 injury-report index URL | Redirect behavior checked | Redirects to 2025-26 index. No protected-season report or outcome extracted; no claim of complete historical coverage. |
| NBA terms page | Usage provisions reviewed; link retained | Local personal, noncommercial downloads may be retained under the stated provision; no redistribution or commercial reuse license established. Raw PDFs stay in ignored local data/raw. Article bodies are metadata-only. |

Sources: [January 4 PDF](https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-01-04_06PM.pdf), [January 28 PDF](https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-01-28_12PM.pdf), [historical index tested](https://official.nba.com/nba-injury-report-2023-24-season/), [terms](https://www.nba.com/termsofuse). All selected article links appear in [the review table](audit_review.md).

The first standard-shell download attempts failed at sandbox DNS resolution; their failure receipts remain local. The permitted network retry downloaded both exact, previously reviewed URLs. Source metadata distinguishes raw PDF receipts from manually captured web evidence. Current retrieval does not recreate what a page looked like in 2024. Broad automated scraping, historical archive completeness, a player-game endpoint, tracking coverage and travel data were not verified, and no such API is claimed to exist here.

## Selected audit results

25 real candidate records: 21 injury/status leads and four noninjury exclusion controls. This sample deliberately mixes strong evidence and unresolved leads; it is not 25 fully adjudicated injury episodes.

| Provisional outcome | Primary >28 days | Secondary >=10 consecutive team games |
| --- | ---: | ---: |
| Positive | 2 | 3 |
| Negative | 1 | 1 |
| Unknown | 18 | 17 |
| Excluded | 4 | 4 |

The human-readable [review](audit_review.md) links every case to evidence. [CSV](../audit/candidates.csv) retains distinct onset, report, missed-game, clearance, return and uncertainty columns. Unknown values remain blank. The return-gap proxy is explicitly separate from primary labels. Forecast recovery alone never determines a positive. None of these records supplies a validated historical prediction timestamp.

Important unresolved issues: exact first-public times, stable player IDs, onset intervals, recurrence versus continuation, per-game attribution, continuous medical unavailability, end-of-season follow-up, and population availability. All medical clearance fields and all mechanisms remain unknown. Independent human adjudication has not occurred. Positive labels are provisional evidence judgments, not a claim that medical records were obtained.

## Implemented deliverables

Three JSON Schema designs cover injury episodes, player prediction timestamps, and source provenance. Audit CSV is an intentionally partial staging format, not a complete production episode-table instance. Pure Python rules implement tri-state horizon membership, separate severity outcomes, conservative status normalization, explicit episode grouping, point-in-time workload, predictor role/time checks, label-maturity and episode-purging guards. The review builder validates identifiers, source references and controlled values before rendering. The retriever permits only the two reviewed development PDFs, validates response type and exact final URL, hashes raw bytes, and records errors without inventing data. No training or holdout-opening code is provided.

All 21 focused tests passed. They exercise calendar-day and DST boundaries, offseason-extension refusal, strict horizon start, inclusive 14-day end, uncertain intervals, timezone requirements, strict >28 versus >=10 boundaries, missing evidence, censoring, episode grouping, availability, workload publication timing, forbidden future/outcome predictors, and split/label-maturity checks. These tests validate software invariants, not clinical label accuracy or completeness of source surveillance.

## Smallest practical next phase

1. Build a coverage manifest for a bounded development pilot, initially one team over 6-8 regular-season weeks in 2023-24. Enumerate expected reports from its verified schedule and measure observed report snapshots, publication precision and missingness. Do not silently reduce the cohort to injured or frequently reported players.
2. Map NBA player IDs, independently review the 25 candidate records, and collect game-level injury reasons and follow-up for ambiguous cases. Reconcile recurrent episodes and preserve disagreements. Review per-case details directly in the CSV; no change to the research question is required to do this.
3. Acquire or validate player-game minutes and game-end/publication timestamps for **all** pilot roster members, including never-injured players. Build eligible/unknown/excluded counts and separate onset-surveillance from severity-follow-up completeness. Quantify label and availability coverage before expanding seasons.
4. Proceed to cohort construction only if point-in-time coverage and adjudication are credible. Select and preregister event-count/precision requirements after the pilot; no arbitrary success threshold or predictive power is assumed. Only then freeze chronological validation and fit simple baselines.

No user decision is needed to finish the independent Phase 1 work. Genuine blockers are missing historical coverage and adjudication evidence, not model complexity. Future account access, costs, changed outcomes, or protected holdout access require user authorization. Human review is needed before treating the candidate judgments as final labels; it does not block the independent coverage pilot.
