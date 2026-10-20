"""Render actual opportunity, fold and missingness counts directly in report."""
from collections import Counter
from .study import ROOT,D,read


def table(rows, fields):
    rows=list(rows)
    def clean(x):return str(x).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(fields)+' |','| '+' | '.join('---' for _ in fields)+' |']+['| '+' | '.join(clean(r.get(k,'')) for k in fields)+' |' for r in rows])+'\n'


def render(result,review):
    rr,events,all_events,summary,folds,ev,knowledge,missing,disclosure=result
    bins=read(ROOT/'phase2d/tables/lead_time_summary.csv')
    teams=[]
    opp=read(D/'tables/opportunities.csv');byid={r['row_id']:r for r in rr}
    for lag in ('0','1'):
        for team in sorted({r['team'] for r in rr}):
            oo=[o for o in opp if o['extra_lag_days']==lag and byid[o['row_id']]['team']==team]
            teams.append(dict(lag=lag,team=team,positive_decisions=len(oo),players=len({o['player_id'] for o in oo}),events=len({o['canonical_event_id'] for o in oo})))
    from .study import write
    write(D/'tables/team_opportunities.csv',teams)
    player_counts=[]
    for lag in ('0','1'):
        for pid in sorted({e['player_id'] for e in events}):
            ee=[e for e in events if e['player_id']==pid]
            oo=[o for o in opp if o['player_id']==pid and o['extra_lag_days']==lag]
            player_counts.append(dict(lag=lag,player_id=pid,player=ee[0]['player_name'],qualifying_runs=len(ee),
                                      events_with_opportunities=len({o['canonical_event_id'] for o in oo}),positive_decisions=len(oo)))
    write(D/'tables/player_opportunities.csv',player_counts)
    order=[]
    for lag in ('0','1'):
        sub=[r for r in disclosure if r['lag']==lag]
        order.append(dict(lag=lag,events_with_supported_pre_disclosure_opportunity=sum(r['supported_order'] for r in sub),events_with_linked_disclosure=sum(bool(r['first_acquired_same_acute_B_at']) for r in sub),ordering_unverified=sum(not r['first_acquired_same_acute_B_at'] for r in sub)))
    selection=read(D/'tables/selection_missingness.csv')
    text='''# Phase 3A preparation and post-inspection baseline protocol

All30 teams remain the bounded 2023–24 development cohort. No new data collection, retrieval, fitting, preprocessing fitting, threshold tuning or protected-period access occurred. Independent human review is pending. Original files and registrations remain unchanged; no assertion correction was made and the before/after correction ledger is empty. The README documentation checkpoint is explicitly versioned separately from the scientific-result snapshot.

## Snapshot and count reconciliation

`../phase3a/snapshot_manifest.json` hashes every tracked historical module artifact, code, source receipt/provenance, historical batch registration and the preparation adapter. Scientific result commit: `1d6fd5c9d9e52edffa96cc6488037b504c7ab95e`; documentation checkpoint: `b5932dff33752d9f2cdffda42ebdf1da48523b6e`. The union is read through existing adapters without re-running historical builds. Canonical decisions are unique by row ID and by player/time/timing rule, including transfers. Stable player+first-miss game keys reconcile canonical runs; historical actual-game overlap tables and115 duplicate event-record ledger entries remain hashed. No different-anchor overlapping confirmed positives were found in the frozen audit.37 qualifying runs involve36 players. Rose has two separated absence runs; this does **not** establish clinically independent injuries. Both stay in the same player fold.

'''
    text+=table(summary,['lag','included','positive','negative','unknown','qualifying_runs','run_players','eligible_events','lower','upper'])
    text+='''
Ranges are worst-case positive-label frequency identification ranges among included decisions, not confidence intervals, annual incidence, PR-AUC bounds or calibration bounds. The population includes repeated correlated decisions; unknown labels are not negatives.

## Actual observation opportunities

These are eligible observation opportunities, not model detections or successful warnings. Full anchor interval must lie in (decision,decision+14 elapsed days]. Earliest is the earliest included positive decision, not biological injury onset. A blank earliest means no eligible opportunity. All37 events and both timing rules follow; per-event counts also give player counts because IDs are canonical across transfers. Different runs for the same player are separate rows but not independent persons.

'''
    text+=table(ev,['lag','event','player','team','opportunities','earliest','earliest_lead_lower','earliest_lead_upper','>0-3d','>3-7d','>7-14d','boundary_uncertain'])
    text+='\nCounts aggregated by player (related runs remain grouped):\n\n'+table(player_counts,['lag','player_id','player','qualifying_runs','events_with_opportunities','positive_decisions'])
    text+='\nLead bins (row counts and distinct events; event totals overlap across bins):\n\n'+table(bins,['extra_lag_days','lead_time_bin','positive_rows','events'])
    text+='\nCounts by prediction team (transfer events may occur across teams, so event totals across teams can overlap):\n\n'+table(teams,['lag','team','positive_decisions','players','events'])
    text+='\nMutually exclusive positive-row knowledge hierarchy under B timing; overlapping raw source flags remain in `tables/opportunities.csv`:\n\n'+table(knowledge,['lag','group','rows','events'])
    text+='''
Different decisions for one event may fall in different knowledge groups; event counts across groups overlap. A original-publication timing is unverified for all rows. C links prior acute disclosures to eventual runs for description only, never prediction. No searched signal means no signal found within the bounded source process, not biologically symptom-free.

Supported ordering before an acquired linked acute disclosure (B assumed availability only):

'''+table(order,['lag','events_with_supported_pre_disclosure_opportunity','events_with_linked_disclosure','ordering_unverified'])
    text+='''
Unlinked disclosures cannot be ordered merely because the same-event flag is false. `tables/disclosure_ordering.csv` retains timestamps and unresolved ordering. No verified A pre-injury warning is established.

Already-disclosed-acute sensitivity (outcome-conditioned C linkage; not a deployable eligibility filter):

'''+table(summary,['lag','acute_excluded','sensitivity_denominator','sensitivity_positive','sensitivity_events'])
    text+='''
## Review preparation

'''+f"Prepared {review['cases']} shuffled conclusion-blinded cases: all37 currently qualifying runs, {review['consequential_unknown']} consequential unresolved runs and30 seeded negative decisions, one/team (seed20240221). Unknown cases are every canonical unknown run linked to an included unknown decision with possible/true onset-window membership, not merely the earlier top-ten queues. Their exact selection and original conclusions are in the separate answer key. First-pass packet contains raw factual game timelines, reasons, direct URLs, source hashes, short capped excerpts, locators and blank structured reviewer fields. Public narratives and selection may reveal case type, so this is conclusion-blinded rather than perfectly blinded. {review['missing_source_urls']} unresolved source URLs; {review['narrative_without_exact_paragraph']} narrative references lack exact paragraph locators and are explicitly marked for source inspection. No invented locators or excerpts. Factual game rows still identify exact game/player entries. Case facts use the original batch-selected receipt hashes, not a silent replacement by the latest/global cache; `review/source_version_audit.csv` preserves the comparison. Global receipts only supply otherwise unavailable retrospective C supplements. Independent human reviews: **0**.\n"
    text+='''
Distribute only `review/first_pass/` to a separate human; retain `review/answer_key.csv`, this report and historical judgments separately until first-pass completion. Review attribution, continuity, original anchor, consecutive medical games, competing reasons, censoring and transfers. No need to wait to complete preparation, but final labels, event opportunity claims and later model interpretation depend on review. No human conclusions are invented.

## Feature availability and fixed comparison

Age/DOB is unavailable in the existing feature tables. M1 is explicitly an exposure/known-injury alternative, not an age-adjusted risk model. M0 is constant training known-label event-row fraction; M1 uses recent acquired28-day evidence, cumulative acquired history and prior28-day mean minutes per appearance excluding latest; M2 adds only7-day minus prior7-day minutes and index-game back-to-back indicator. No player/team IDs, C acute links or outcome fields are predictors. Full formulas, L2 C=0.1 settings, missing indicators, training-only imputation/scaling, weights and metric/alert definitions are fixed in `protocol/study_protocol.md` and `protocol/config.json`.

'''+table(missing,['lag','feature','rows','missing','min','max'])
    text+='''
Incomplete history makes exposure/rest features missing rather than zero. Boston legacy injury-memory fields are missing, not falsely equated to modern fields. Missing features stay in paired evaluation with training-only imputation and fixed indicators. The decision-to-last-appearance interval was rejected after inspection because it mainly encodes the noon decision convention; the back-to-back indicator is the fixed rest alternative. No imputer/scaler has been fitted. Actual workload latest-input and acquired-signal identity/timing checks found no future B inputs; this verifies assumption-based clocks, not original A publication. Predictor allowlist rejects extra columns. Detailed selection by team, player, exposure band and acquired risk is in `tables/selection_missingness.csv`; summaries by exposure/risk follow.

'''+table([r for r in selection if r['dimension'] in ('exposure_band','risk_information')],['lag','dimension','value','rows','players','positive','negative','unknown','any_missing_predictor'])
    text+='''
## Deterministic grouped feasibility

Five player folds use SHA256 with fixed prefix/seed, modulo5, without label stratification or redraw. All transfer spells/episodes stay together. Counts below are actual train/test labels and events before any fitting. Memphis sensitivity removes every row of a player with any included MEM decision, including transfer rows; original folds remain fixed. Team/calendar dependence remains. These are planning counts, not validation results or a pristine holdout.

'''+table(folds,['lag','sensitivity','fold','role','rows','players','positive_players','positive_events','positive','negative','unknown'])
    text+='''
Recommended next step: independent human adjudication and resolution/logging of consequential uncertainty, **not an immediate exploratory fit**. Fold counts support only bounded internal-study planning; sparse positive players/events, Memphis concentration (7/37 runs), missing labels, one narrow season and assumed clocks preclude confirmatory claims. If reviewed labels remain usable, separately authorize the fixed player-grouped exploratory comparison. Call it exploratory internal validation, not prospective/temporal generalization. A later separately authorized2024-10-22–2024-12-31 evaluation period (onset through2025-01-14, severity through2025-04-13) is a candidate only and was not accessed. Historical label maturity at training cutoffs remains unverified; assumptions must be distinguished from verified availability before any temporal study.

The protocol fixes AP/PR-AUC with prevalence reference, Brier/calibration, paired identical-row M2-M1 differences, player-bootstrap uncertainty, unknown-label selection/ranges and training-only nested threshold selection. Alerts merge within7 days of the first alert, match each canonical run once within14 days, and keep unresolved/redundant alerts separate. Denominator is observed eligible decisions, never invented player-weeks. Row weights remain1; no event reweighting then probability-calibration claim.

## Commands and freeze

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
python3 -m phase3a.study --prepare  # deterministic preparation; never fits
python3 -m phase3a.study            # default: verify snapshot/config and show dry-run status
python3 -m unittest discover -s basketball/nba/injury-warning/tests -p test_phase3a.py -v
# --execute-fit is intentionally refused in this phase, even if supplied.
```

See `protocol/study_protocol.md` for exact definitions and `commit_receipt.json` for protocol commit/hash after freeze. Historical tests are run on their scientific snapshot because preservation manifests deliberately freeze the old module README. The Phase1D preservation list additionally hashes three ignored local bytecode files: exact offline reproduction requires these original bytes and PYTHONDONTWRITEBYTECODE=1, plus the checksummed 2023–24 schedule cache and pre-existing local root README. These machine-cache dependencies are a historical portability limitation, not files to distribute or silently remove from registrations. Raw cache requirements remain those of Phase2D; no full bodies or PDFs are redistributed. This protocol was designed after outcome inspection and is not pre-data preregistration. Pending human review has not been represented as complete.
'''
    (D/'report.md').write_text(text)
    (D/'README.md').write_text('# Phase 3A preparation only\n\nSee [report](report.md), [post-inspection protocol](protocol/study_protocol.md), [dry-run configuration](protocol/config.json), [snapshot](snapshot_manifest.json), and [conclusion-blinded first-pass packet](review/first_pass/README.md). The answer key is deliberately separate. No fitting or independent human adjudication has occurred.\n')
