# Phase 1B: bounded longitudinal data pilot — completed feasibility results

**Decision: do not expand model-ready cohort collection under the present availability definition.** The public sources support a reproducible retrospective roster/participation panel, but this pilot does not establish the positive postgame availability evidence or original input-publication times required by the registered task. A specific alternative exposure definition is described below for review, without adopting it or generating its labels. No model was trained. Few or zero adjudicated events in this short pilot say nothing about attainable predictive performance.

## Registered team, period and evidence scope

Boston Celtics, **January 1 through February 18, 2024**, inclusive: seven continuous weeks, **23 regular-season games**. The first actual game was January 2 and the last February 14; All-Star games were not included. History is December 4–31, 2023 (**13 games**); follow-up is February 19–April 14, 2024 (**27 games**). History and follow-up do not create pilot prediction rows.

[Registration](../pilot/registration/design.json) and its SHA256 were saved before pilot outcomes were reviewed. Selection used the existing development-season schedule, accessible historical official gamebooks, and official roster-transaction announcements. The team/dates were never changed to enrich injuries. [Acquisition update](../pilot/registration/acquisition_update.json) records the public-source fallback and unchanged scope.

The existing 2023-24 LeagueGameLog snapshot was checksum-verified and filtered to team/date/game identity fields. Its raw scores were not exported or modeled. Existing code, frozen experiment executors, and protected 2024-25/later data were not used. Phase 1's original 25-case CSV and judgments remain preserved; new reviews are separate extensions. The pre-existing root README changes were left untouched.

## Data actually obtained

| Scope | Obtained material | Important limits |
| --- | --- | --- |
| Core pilot, history and follow-up | 63 official historical game pages; 63 official gamebook PDFs; 69 injury-report PDFs; 2 team trade releases; 1 retrospective May 11 roster/acquisition guide: **198 successful source snapshots** | Original public availability is unverified; later site navigation and unrelated seasons in HTML were not extracted. |
| Six selected case reviews | 74 additional unique public source snapshots, separate from pilot denominator | Outcome evidence only; no historical training-cutoff availability claimed. |
| Overall Phase 1B retrieval | **272 successful snapshots**, 58,485,060 source bytes; **3 actual HTTP 403 failures** | Raw content remains in ignored local data/raw/phase1b. Content hashes and actual request outcomes are retained. |
| Direct CDN boxscore/playbyplay source | Two boxscore and one play-by-play probes returned 403 | No access restriction was bypassed. Further same-endpoint game probes were not made. Public NBA game HTML was acquired as a distinct accessible source and contains structured historical game data. |

The raw-source mix is 124 gamebook PDFs, 76 historical game pages, 69 report PDFs, two releases and one roster guide. [Append-only retrieval/provenance ledger](../pilot/source_manifest.jsonl) records URLs, retrieval times, HTTP outcomes, final URLs, SHA256, content sizes, raw paths, server Last-Modified where supplied, and publication uncertainty. Last-Modified is not treated as original publication. [Source coverage](../pilot/tables/source_coverage.csv) also records the 83 planned CDN requests not attempted after the endpoint denial; these are not fabricated per-game failures. [Failure table](../pilot/tables/retrieval_failures.csv) lists actual failures and parsing failures, if any.

All 69 **sampled** report URLs were accessible and parsed. This does not establish an archive-wide retrieval rate: the URLs were bounded schedule-driven probes, not an enumeration of all historical reports. Reports contain **64 Celtics game-date sections**: **23 submitted sections** and **41 not-yet-submitted sections**. Ten documents do not cover Boston. Five documents contain both a submitted current-game section and an unsubmitted next-game section. The parser preserves both instead of incorrectly marking the entire team submitted/unsubmitted. At document level: 18 complete only, 36 unsubmitted only, 5 mixed, 10 not covered. No sampled report was missing and no final report parse failure remained.

The **101 Celtics status listings** map to stable IDs without ambiguity: 88 Out and 13 Available. Available listings are mostly pregame or game-specific; none establishes the registered postgame availability. The report header is a nominal document timestamp, not independently verified original public availability. Report filename hours are not silently treated as header timestamps. For example, filenames ending 06PM can contain a 6:30 PM report.

## Actual linked tables

All CSVs use empty cells for unknown/not applicable, with precision and reason columns. Source IDs join the retrieval ledger; `local_2023_24_schedule` joins [schedule provenance](../pilot/schedule_provenance.json); `phase1:` references join the [original source register](../audit/sources.json). [Table dictionary](../pilot/table_dictionary.json) lists every saved table's row count and columns.

| Table | Contents |
| --- | --- |
| [players](../pilot/tables/players.csv) / [roster_membership](../pilot/tables/roster_membership.csv) | 19 stable NBA IDs, observed roster intervals, contract category, left/right censoring and transaction uncertainty. |
| [transactions](../pilot/tables/transactions.csv) | Tillman/Stevens February 7 and Springer/Banton February 8 movements with official-source references. |
| [team_schedule](../pilot/tables/team_schedule.csv) / [game_timing](../pilot/tables/game_timing.csv) | 63 linked games; phase tags; scheduled start distinct from documented game-end interval. |
| [player_games](../pilot/tables/player_games.csv) | **1,068 player-game records** across history/pilot/follow-up, including appearances, minutes, bench DNPs, inactive/two-way entries and documented reasons. |
| [status_observations](../pilot/tables/status_observations.csv) | 101 timestamped listings, reason, target game date, nominal report time, publication uncertainty and PDF locator. |
| [report_coverage](../pilot/tables/report_coverage.csv) / [report_player_coverage](../pilot/tables/report_player_coverage.csv) | Missing source, not submitted, no team coverage, player listing and absence from submitted report kept distinct. A missing listing never means healthy. |
| [injury_episodes](../pilot/tables/injury_episodes.csv) | **28 unadjudicated injury-attributed game-absence leads**, with source links. They are not 28 distinct new injuries and are not automatically merged into episodes. |
| [prediction_timestamps](../pilot/tables/prediction_timestamps.csv) | 392 candidate rows, precise timing blockers, membership uncertainty, evidence IDs, separate immediate/later/nominal-header decisions and unknown outcome labels. |
| [workload_feasibility](../pilot/tables/workload_feasibility.csv) | Retrospective 7/14/28 calendar-date minutes and appearances; explicitly ineligible as point-in-time model features because original publication and exact timestamp windows are unverified. |
| [eligibility_coverage](../pilot/tables/eligibility_coverage.csv) / [missingness](../pilot/tables/missingness.csv) | Descriptive coverage by past playing time and completed-game status; no predictive comparisons. |
| [case_audits](../pilot/tables/case_audits.csv), [assertions](../pilot/tables/case_assertions.csv), [case games](../pilot/tables/case_game_evidence.csv) | Six detailed outcome reviews, assertion-level provenance and per-game absence evidence, separate from cohort. |
| [user_review_queue](../pilot/tables/user_review_queue.csv) | All 25 original records, six detailed-review priorities, blank user decisions, reviewer identities and unresolved questions. |

The roster covers players who never appeared, bench players, three two-way players during the pilot, arrivals and departures. Each game supplies an explicit active/inactive listing; no player was selected using later injury status. The May roster guide corroborates identities and acquisition dates retrospectively. It is not a timestamped historical transaction feed, and unseen contracts entirely between games cannot be conclusively excluded from that guide alone. Intergame membership and exact effective transaction times remain explicit uncertainties.

There are **391 directly listed game-roster rows**. On February 7, the game listing still includes Lamar Stevens, while the trade release announces Tillman's acquisition. Rather than force one source to win, both transaction-day possibilities are retained: **392 candidate rows, comprising 390 certain game-roster memberships and 2 uncertain transaction-day memberships**. The additional Tillman row is a roster uncertainty lead, not an invented appearance or a verified eligible observation. Candidate membership bounds are therefore 390–392. The roster interval table does not equate first/last observed listing with signing/waiver date.

## Operational timing and eligibility results

| Measure | Immediate postgame task | Separately registered next-day noon ET analysis |
| --- | ---: | ---: |
| Candidate player-game rows | 392 | 392 |
| Explicitly available/eligible | **0** | **0** |
| Point-in-time established unavailable | 0 | 0 |
| Point-in-time noninjury exclusions | 0 | 0 |
| Unknown eligibility | **392** | **392** |
| Complete onset surveillance and resolved outcome labels | 0 | 0 |

For **all 23 games**, official final-period descriptions recover a documented **end-minute interval**, not exact seconds. The code does not substitute scheduled start or game duration for completion. Consequently all 392 immediate prediction rows lack the exact game-end timestamp, and every row also lacks verified original publication of required inputs. Both blockers are retained. The registered later rule is noon America/New_York on the following calendar day, which is after the game-end upper bound; it changes the timing question but does not solve publication or positive-availability evidence.

Pregame Available cannot be carried through a game to prove the player finished uninjured. A report issued after a game can still refer to that completed game; its target-game date must be checked before interpreting it as current status. Even a nominal-header sensitivity that relaxes independent publication verification produces **zero available rows** after these safeguards. Source health/availability is not backfilled using later appearances.

The retrospective completed-game panel has **246 appearances, 28 injury-attributed absences, 2 rest absences, 1 illness absence, 59 assignment/two-way nonappearances, 53 coaching DNPs, and 2 unresolved nonappearances** among the 391 listed rows. These are descriptions of the completed game, not 28 verified postgame unavailable rows. The extra transaction-only row has unknown participation. Outcomes for **all 392 candidate rows remain unknown separately for both definitions**: onset surveillance over the entire following 14 days is not established, and severity follow-up is not fully adjudicated. Twenty-seven follow-up gamebooks alone do not establish continuous onset surveillance between games.

### Descriptive selection/coverage audit

Playing-time groups use only the preceding December 4–31 Boston game records; new arrivals have no Boston preperiod history. This grouping itself is retrospective source analysis, not a claim that publication times are verified.

| Preperiod group | Players | Candidate rows | Observed appearances | Available rows |
| --- | ---: | ---: | ---: | ---: |
| >=24 minutes per listed team game | 4 | 92 | 85 | 0 |
| 10 to <24 minutes | 5 | 115 | 91 | 0 |
| <10 minutes | 8 | 176 | 70 | 0 |
| No Boston preperiod history | 2 | 9 | 0 | 0 |

Strict inclusion retains no usable availability cohort in any group. An appearance-only substitute would retain 246/392 (62.8%) raw candidate rows, preferentially selecting regular rotation players while dropping many depth/two-way players and both newly acquired inactive players. These 246 appearances have **not** passed a healthy-at-noon rule. [Sample timelines](phase1b_timelines.md) show stars, bench/two-way players, a rest absence and the transaction-day conflict alongside the explicit unknown decisions.

## Six case reviews and remaining uncertainty

[Readable case reviews](phase1b_case_audits.md) and the machine evidence ledgers document the following provisional judgments:

| Case | Stable NBA ID | Primary >28 days | Secondary >=10 consecutive games | Onset-to-return proxy |
| --- | --- | --- | --- | --- |
| Joel Embiid, left knee | 203954 | Unknown | Positive, 29-game reported run reconciled to schedule | 63 days |
| Julius Randle, shoulder | 203944 | Positive | Positive, 36 individually injury-attributed games | Unknown; no regular-season return |
| LaMelo Ball, November ankle episode | 1630163 | Unknown | Positive, 20-game reported run reconciled to schedule | 47 days |
| Stephen Curry, March ankle | 201939 | Negative | Negative, 3 individually verified injury-related missed games | 9 days |
| Al Horford, January 5 rest | 201143 | Excluded | Excluded | Not an injury proxy |
| Alperen Sengun, March knee/ankle | 1630578 | Unknown | Positive, 18 individually injury-attributed games | Unknown; season-end censored |

The five injury cases have formal primary outcomes resolved in **2/5 (40%)**, an observed onset-to-return appearance gap in **3/5 (60%)**, and secondary outcomes resolved in **5/5**. These proportions describe selected-case adjudicability, not prevalence. All five have a verified first injury-related missed team game. No full medical clearance or original historical label-availability time was established. Randle's ongoing sidelining narrative supports continuous injury unavailability; game-by-game out reasons alone are not promoted to proof of medical unavailability on every intervening day. Sengun's season-end censoring does not automatically erase a sufficiently long observed missed-game run or create a primary negative. No offseason was counted as evidence of ongoing injury.

The same Codex agent performed both rounds. **Independent human adjudications: zero.** The six reviews retain unknown assertions; they are not six fully medically adjudicated episodes. All 25 original records have a review-queue entry. User review should accept/amend/reject the source assertions and outcome judgments individually; the remaining 19 are still pending detailed evidence collection. Historical label_known_at fields remain empty with unverified precision, so none of these labels is represented as ready for an earlier training cutoff.

## Quality checks, tests and reproducibility

The PDF report parser uses actual page coordinates and preserves team/game-date sections across page breaks. Wrapped reason cells can start above the player name, and NBA gamebooks can put injury DND rows in the active box instead of the inactive list; both cases are handled. A report/gamebook page was rendered and visually checked against extraction. Exact raw byte hashes are checked before offline reads.

Two source-quality issues remain visible rather than silently corrected away. One follow-up JSON minute value is `33:60`; its arithmetic carry to 34:00 is recorded explicitly with the original value. One history game's structured player-minute sum is 240.05 against the expected 240, a three-second residual at the tolerance boundary. [Gamebook checks](../pilot/tables/gamebook_checks.csv) retain that flag. No model feature uses these retrospective values. The report parser has zero final unmapped Boston status names and zero final parse failures in the sampled PDFs.

**32 relevant tests passed**: the existing 21 plus 11 new tests for roster entry/exit uncertainty, duplicate names, injury-versus-illness/rest attribution, missing versus absent report listings, source publication and target-game scope, end-minute uncertainty, explicit minute normalization, registration integrity, full listed-member coverage with transaction exceptions, source links, and accurate reviewer labeling. The earlier future-onset, threshold, censoring, offseason and leakage tests continue to pass. Tests verify software invariants and ledger consistency; they cannot establish medical truth, archive completeness or original public availability.

From the repository root, use Python 3.10+ for acquisition and tests. PDF parsing uses `requirements-phase1b.txt` in an isolated environment; the implementation run used the bundled Python with pypdf 6.10.0 and pdfplumber 0.11.9. No existing project environment was changed.

```sh
export PYTHONPATH=basketball/nba/injury-warning/src
python3 basketball/nba/injury-warning/scripts/acquire_pilot.py
# Explicit network acquisition; existing source receipts/cache are reused:
python3 basketball/nba/injury-warning/scripts/acquire_pilot.py --fetch
python3 basketball/nba/injury-warning/scripts/acquire_case_audits.py --fetch
# Use the interpreter with the pinned PDF dependencies for these commands:
python3 basketball/nba/injury-warning/scripts/parse_pilot_reports.py
python3 basketball/nba/injury-warning/scripts/build_case_audits.py
python3 basketball/nba/injury-warning/scripts/build_pilot.py
python3 basketball/nba/injury-warning/scripts/render_pilot_results.py
python3 -m unittest discover -s basketball/nba/injury-warning/tests -v
```

An exact offline rebuild requires the ignored hashed raw cache and the existing checksum-matched 2023-24 schedule snapshot. The tracked tables, source receipts, request catalogs, registration and dictionary support review without redistributing raw NBA material. Re-fetching mutable public pages need not recover identical historical bytes. Retrieval failures remain logged; the scripts do not silently fall back to invented rows or change pilot scope.

## Recommendation and precisely separated alternative

**Revise the operational availability requirement before any broader modeling-oriented expansion, or stop the original task if that requirement is essential.** The immediate postgame positive-availability task is not supported by this pilot's source/timestamp evidence. Simply downloading more teams under the same source assumptions would multiply unknown rows. A targeted test of a timestamped historical public status/news archive could still be worthwhile, but archive completeness and contemporaneous publication must first be demonstrated.

A concrete alternative for user review is an **appearance-defined next-noon exposure cohort**: take players with >0 observed minutes in the completed regular-season game, assign the decision time as next-day noon ET, remove players with an explicitly reported in-game new injury or injury-unavailable status known by that noon, and retain an `availability_unverified` flag for everyone else. Inputs still require publication evidence by noon, prior ongoing injuries cannot silently become new onsets, and any incomplete 14-day onset surveillance remains unknown. The 246 appearance rows here are only an upper bound before that evidence-based exclusion step; alternative outcome labels were not generated.

This changes the population from positively known available players to recently active players without a known disqualifying report. It assumes unreported postgame problems can remain in the risk set, selects by playing opportunity, and excludes nonplaying bench/two-way players. It therefore changes the operational estimand and requires explicit adoption rather than silently replacing the original research question. A fixed-noon timing rule by itself is insufficient. No evidence in this pilot establishes either predictive success or failure, and no predictive result would establish preventability.
