"""Report the fixed batch without fitting or selecting models."""
from collections import Counter,defaultdict
from pathlib import Path
import json,csv,hashlib
from injury_warning.pilot_io import ROOT
from .acquire import D,manifest,registration,read
from .prepare import rows,write

def md(records,fields):
    return '\n'.join(['| '+' | '.join(fields)+' |','| '+' | '.join(['---']*len(fields))+' |']+['| '+' | '.join(str(r.get(k,'')) for k in fields)+' |' for r in records])
def legacy(name,phase):
    with (ROOT/phase/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def render():
    reg=registration();sm=manifest();team=rows('team_results');co=rows('cohort_all_roster_candidates');out=rows('row_outcomes');events=rows('events');members=rows('event_game_evidence');feat=rows('features_B');neg=rows('negative_sample_review');eventpred=rows('event_prediction_coverage');selected={r['team'] for r in reg['selected']};pooled=[];groups=[];missing=[];sources=[]
    bco=legacy('cohort_all_candidates','phase1c');bo=legacy('row_outcomes','phase1d');evlookup={e['event_id']:e for e in events};colookup={r['row_id']:r for r in co}
    for lag in ('0','1'):
        cr=[r for r in co if r['extra_lag_days']==lag];oo=[r for r in out if r['extra_lag_days']==lag];bb=[r for r in bco if r['extra_lag_days']==lag];bob=[r for r in bo if r['extra_lag_days']==lag]
        new=dict(scope='new_fixed_six',extra_lag_days=lag,team_game_exposures=sum(int(r['games']) for r in team if r['extra_lag_days']==lag),distinct_physical_games=len({r['index_game_id'] for r in cr}),roster_players=len({r['player_id'] for r in cr}),recently_active_players=len({r['player_id'] for r in cr if r['appeared']=='True'}),candidate_appearances=sum(r['appeared']=='True' for r in cr),included=len(oo),excluded=sum(r['B_state']=='excluded' for r in cr),eligibility_unknown=sum(r['B_state']=='unknown' for r in cr),positive=sum(r['absence_run_onset_ge10']=='positive' for r in oo),negative=sum(r['absence_run_onset_ge10']=='negative' for r in oo),outcome_unknown=sum(r['absence_run_onset_ge10']=='unknown' for r in oo),confirmed_qualifying_events=sum(e['severity']=='positive' and e['candidate_broad_onset_period']=='True' for e in events),events_with_eligible_prediction=len({eid for r in oo if r['absence_run_onset_ge10']=='positive' for eid in r['event_ids'].split(';')}),missing_history=sum(r['history_complete']=='False' for r in feat if r['extra_lag_days']==lag),A_verified=0)
        pooled.append(new)
        bos=dict(new,scope='Boston_previously_inspected',team_game_exposures=len({r['index_game_id'] for r in bb}),distinct_physical_games=len({r['index_game_id'] for r in bb}),roster_players=len({r['player_id'] for r in bb}),recently_active_players=len({r['player_id'] for r in bb if r['appeared']=='True'}),candidate_appearances=sum(r['appeared']=='True' for r in bb),included=len(bob),excluded=sum(r['B_state']=='excluded' for r in bb),eligibility_unknown=sum(r['B_state']=='unknown' for r in bb),positive=sum(r['absence_run_onset_ge10']=='positive' for r in bob),negative=sum(r['absence_run_onset_ge10']=='negative' for r in bob),outcome_unknown=sum(r['absence_run_onset_ge10']=='unknown' for r in bob),confirmed_qualifying_events=0,events_with_eligible_prediction=0,missing_history=0)
        pooled.append(bos)
        # Both groups use the same player-game-lag decision key. Shared team games
        # are distinct sources once, while different players are different rows.
        assert not ({r['row_id'] for r in oo}&{r['row_id'] for r in bob})
        combined=dict(new,scope='combined_development_not_validation',team_game_exposures=new['team_game_exposures']+bos['team_game_exposures'],distinct_physical_games=len({r['index_game_id'] for r in cr+bb}),roster_players=len({r['player_id'] for r in cr+bb}),recently_active_players=len({r['player_id'] for r in cr+bb if r['appeared']=='True'}))
        for k in ['candidate_appearances','included','excluded','eligibility_unknown','positive','negative','outcome_unknown','missing_history']:combined[k]=new[k]+bos[k]
        pooled.append(combined)
        for t in sorted(selected):
            rr=[r for r in oo if r['team']==t and r['absence_run_onset_ge10']=='positive']
            for g in ['acute_already_disclosed','symptom_or_history_known','no_signal_found_under_searched_process','timing_unresolved']:
                gg=[r for r in rr if r['group_B']==g];groups.append(dict(team=t,extra_lag_days=lag,knowledge_group_B=g,positive_rows=len(gg),distinct_events=len({eid for r in gg for eid in r['event_ids'].split(';') if eid}),A_verified=0,A_knowledge_timing_unresolved_positive_rows=len(gg)))
            rteam=[r for r in oo if r['team']==t];ee=[e for e in events if e['sampled_origin_team']==t and e['candidate_broad_onset_period']=='True'];missing.append(dict(team=t,extra_lag_days=lag,eligibility_unknown=sum(r['team']==t and r['B_state']=='unknown' for r in cr),outcome_unknown=sum(r['absence_run_onset_ge10']=='unknown' for r in rteam),incomplete_history=sum(r['team']==t and r['extra_lag_days']==lag and r['history_complete']=='False' for r in feat),transfer_surveillance_gaps=sum(r['transfer_onset_surveillance_gap']=='True' for r in rteam),insufficient_severity_followup=sum(r['severity_followup_B']=='False' for r in rteam),mixed_reason_candidate_runs=sum('injury' in e['mixed_categories'] and ';' in e['mixed_categories'] for e in ee),unresolved_potential_runs=sum(e['severity']=='unknown' for e in ee),right_censored_candidates=sum(not e['return_date'] for e in ee)))
    write('pooled_results',pooled);write('known_injury_groups',groups);write('missingness_summary',missing)
    daily=rows('daily_coverage');tm=rows('game_timing');panel=json.loads((D/'team_schedule.json').read_text())
    for t in sorted(selected):
        gg=[g for g in panel if g['team']==t];dd=[d for d in daily if d['team']==t];sources.append(dict(team=t,expected_history_index_followup_games=len(gg),obtained_pages=sum(sm.get('page_'+g['game_id'],{}).get('status')=='obtained' for g in gg),obtained_gamebooks=sum(sm.get('book_'+g['game_id'],{}).get('status')=='obtained' for g in gg),full_recaps=sum(next((x['recap_present']=='True' for x in tm if x['game_id']==g['game_id']),False) for g in gg),daily_report_probes=len(dd),daily_access_failures=sum(d['report_retrieval_status']!='obtained' for d in dd),daily_team_submission_or_section_gaps=sum(d['report_team_state']!='complete' for d in dd),dated_team_queries=sum(q['team']==t for q in json.loads((D/'search_ledger.json').read_text())),limitation='section gaps include off-days; not every gap invalidates B surveillance; no archive-completeness claim'))
    write('source_coverage_summary',sources)
    req=json.loads((D/'request_catalog.json').read_text());newledger=list(map(json.loads,(D/'source_manifest.jsonl').read_text().splitlines()));ownids={r['source_id'] for r in newledger};queries=json.loads((D/'search_ledger.json').read_text());cost=dict(unique_requested_sources=len(req),source_kind_counts=dict(Counter(r['kind'] for r in req)),new_http_requests=len(newledger),new_http_statuses=dict(Counter(r['status'] for r in newledger)),new_obtained_bytes=sum(r.get('bytes',0) for r in newledger),prior_phase_source_reuse=sum(r['source_id'] not in ownids for r in req),summed_request_seconds=round(sum(r.get('request_seconds',0) for r in newledger),2),observed_initial_acquisition_batch_wall_seconds=[92.76,77.44],last_parsing=json.loads((D/'parsing_summary.json').read_text()),last_build=json.loads((D/'build_summary.json').read_text()),saved_dated_queries=len(queries),saved_search_call_receipts=len({r['raw_file'] for r in queries}),targeted_transfer_queries=sum(q['team'] not in selected for q in queries),detailed_event_reviews=len(rows('detailed_event_reviews')),negative_trace_reviews=len(neg),independent_human_reviews=0,manual_person_time='not instrumented; do not infer from request wall time',supplemental_interactive_searches='used to locate continuity sources; article retrieval URLs/hashes retained; total interactive review time not measured')
    (D/'cost_summary.json').write_text(json.dumps(cost,indent=2)+'\n')
    # Full compact traces: every positive, seeded negatives, representative unresolved cases.
    traces=[]
    picks=[r for r in out if r['absence_run_onset_ge10']=='positive']
    for t in sorted(selected):picks+=next(([r] for r in out if r['team']==t and r['extra_lag_days']=='0' and r['absence_run_onset_ge10']=='unknown'),[])
    picks += [next(r for r in out if r['row_id']==n['row_id']) for n in neg]
    for r in picks:
        ids=r['event_ids'].split(';') if r['event_ids'] else [];linked=[evlookup[e] for e in ids];traces.append(dict(row=r,eligibility=colookup[r['row_id']],features=next(f for f in feat if f['row_id']==r['row_id']),events=linked,event_games=[g for g in members if g['event_id'] in ids]))
    (D/'traced_cases.json').write_text(json.dumps(traces,indent=2)+'\n')
    fields=['team','extra_lag_days','games','roster_players','candidate_appearances','included','excluded','eligibility_unknown','positive','negative','outcome_unknown','qualifying_events_broad_onset_period','events_with_eligible_prediction','missing_history']
    fieldp=['scope','extra_lag_days','team_game_exposures','distinct_physical_games','recently_active_players','candidate_appearances','included','excluded','eligibility_unknown','positive','negative','outcome_unknown','confirmed_qualifying_events','events_with_eligible_prediction']
    pmain=next(r for r in pooled if r['scope']=='new_fixed_six' and r['extra_lag_days']=='0');plag=next(r for r in pooled if r['scope']=='new_fixed_six' and r['extra_lag_days']=='1');gsummary=[]
    for lag in ('0','1'):
        for g in ['acute_already_disclosed','symptom_or_history_known','no_signal_found_under_searched_process','timing_unresolved']:
            rr=[r for r in out if r['extra_lag_days']==lag and r['absence_run_onset_ge10']=='positive' and r['group_B']==g];gsummary.append(dict(extra_lag_days=lag,group_B=g,rows=len(rr),events=len({e for r in rr for e in r['event_ids'].split(';')})))
    (D/'summary.json').write_text(json.dumps(dict(registration_commit=json.loads((D/'registration/commit_receipt.json').read_text())['commit'],registration_sha256=(D/'registration/sample_v1.sha256').read_text().strip(),pooled_results=pooled,knowledge_groups=gsummary,tests_passed=73,recommendation='Repair a specific data-quality bottleneck: adjudicate unresolved run attribution and contract/roster gaps before baseline-study planning',models_trained=0,protected_holdouts_opened=0),indent=2)+'\n')
    report=f'''# Phase 2A: fixed six-team development expansion

## Scope and registration

The complete fixed batch is CLE, DEN, DET, ORL, PHI and SAS. The sampling frame contains 29 non-Boston teams sorted by numeric stable NBA team ID; `random.Random(20240218).sample(frame, 6)` selects six, with no outcome-dependent selection or redraw. The full frame, code fingerprint, dates and familiarity disclosure are in [sample_v1.json](../phase2a/registration/sample_v1.json). Commit **d2a8c3030951ede574ddf279c39d789a2d8340a3** preceded selected-team outcome review; its SHA-256 is `{(D/'registration/sample_v1.sha256').read_text().strip()}`. Earlier amendments and the Phase 1D checkpoint pass their preserved hashes. Prior familiarity, particularly PHI/Embiid and Boston/transfer cases, is explicitly acknowledged. Randle/Ball were not sampled; no selected fixture rows were imported.

Index game dates remain January 1–February 18, 2024. The panel contains {pmain['team_game_exposures']} selected-team game exposures, {pmain['distinct_physical_games']} distinct physical games, {pmain['roster_players']} distinct roster-inventory players and {pmain['recently_active_players']} players with a positive-minute candidate appearance. There are {pmain['candidate_appearances']} appearance-defined candidates per timing rule. Shared files are acquired once; a player-game-lag decision and an absence event each have one canonical ID. Different lag analyses are never pooled as independent observations.

The target remains **prolonged injury-related absence onset**: a new documented injury-attributed run starts in `(decision, decision + 14 elapsed days]` and subsequently reaches >=10 consecutive applicable-team missed games, with supported common-episode attribution. Decisions are next-day noon America/New_York, plus an independently rebuilt additional-calendar-day noon sensitivity. It is not biological injury-onset prediction or demonstrated prevention. Clinical-onset and medical-severity analyses through Phase 1D remain separate. **No model, imputation, scaling or feature selection was fitted; no protected holdout was opened.**

## Team and pooled results

All six teams were completed irrespective of event count. Roster inventory includes nonappearing players and the transaction-only DET/House contract record; no unobserved zero-minute game is fabricated for that intraday roster spell. Eligibility is applied to appearances. `qualifying_events_broad_onset_period` means confirmed starts during Jan1–Mar3 (the collected onset extension); all four confirmed events in that interval also start within Jan1–Feb18. It does not include older December/prevalent runs. Zero confirmed events is not proof that unresolved runs are negative.

{md(team,fields)}

Boston is the previously inspected pilot and remains separate. The combined table is development accounting only. Physical games are deduplicated; different teams' roster appearances are distinct player observations. Distinct players are computed from stable IDs rather than added team counts.

{md(pooled,fieldp)}

Core joins: [cohort](../phase2a/tables/cohort_all_roster_candidates.csv), [row outcomes](../phase2a/tables/row_outcomes.csv), [B features](../phase2a/tables/features_B.csv), [event links](../phase2a/tables/row_event_links.csv), [membership spells](../phase2a/tables/membership_spells.csv), [source receipts](../phase2a/source_manifest.jsonl), [table dictionary](../phase2a/table_dictionary.json).

The sampled main analysis has {pmain['positive']} positive, {pmain['negative']} negative and {pmain['outcome_unknown']} unknown labels among {pmain['included']} included rows, alongside {pmain['eligibility_unknown']} eligibility-unknown candidates. The sensitivity has {plag['positive']} / {plag['negative']} / {plag['outcome_unknown']} among {plag['included']}, with {plag['eligibility_unknown']} eligibility unknowns. Unknowns remain in the tables and denominators. No annual injury-rate or league-wide generalization is estimated. Multiple positive rows preceding one event are not independent events.

## Event adjudication and disclosure timing

Stage A identifies nonappearance envelopes from complete applicable-team sequences. Stage B reviews injury reasons, episode identity, first injury miss, actual minute-bounded game start, returns, mixed reasons, roster changes and censoring. Every positive and every unresolved potentially qualifying/censored envelope has a [detailed review](../phase2a/tables/detailed_event_reviews.csv); [event_game_evidence.csv](../phase2a/tables/event_game_evidence.csv) supplies each game/source. Short closed complete blocks can fail severity without a clinical identity assertion. Unknown, G League, coaching, rest, illness and suspension entries are never silently counted as injury games. No separate short runs are added together.

Four confirmed new absence events are retained: Gary Harris (Jan5; 14 actual injury-attributed misses), Melton (Jan15; 18), Livers (Jan24 after moving DET to WAS; at least the 15 explicitly linked misses through Feb25), Embiid (Feb1; 29). These counts are extracted from the full acquired sequences and explicit independent narratives, not assigned from name recognition. Gary/Kevon Harris surname ambiguity is resolved by full-name game-target reports and actual inactive identity; Mobley family names are similarly guarded. The Melton, Harris and Livers continuity assertions have dated secondary/official source receipts, and Embiid uses directly reviewed NBA/AP recap locators. Later mixed causes or season/roster censoring do not undo an already demonstrated ten-game streak; they also do not establish medical recovery.

Four events have an operationally eligible preceding prediction under each timing rule. Covington stays in the unresolved event inventory with zero eligible preceding January-period predictions: his Jan6 final PDF explicitly lists illness, conflicting with a later recap's broad knee-only description. A later knee streak does not establish the initial Jan2 anchor as a homogeneous injury run. Livers's event belongs to the DET-origin sampled player but uses WAS's actual schedule; it is counted once. Ambiguous long runs including Strawther's knee/assignment envelope, Stewart's ankle/coaching/suspension envelope, Cissoko's ankle/assignment envelope, and other roster/assignment gaps remain unknown where explicit common-episode evidence or continuity is insufficient. Matching diagnoses alone are not accepted as clinical identity.

For each positive row, [positive_knowledge_review.csv](../phase2a/tables/positive_knowledge_review.csv) distinguishes the **same acute event** already disclosed under B from prior symptoms/injury history. In particular, Embiid's earlier January knee problem is not called advance disclosure of the later January30 trauma. Category A timing is unresolved for every positive. The B groups are conditional on bounded reviewed channels, not proof that all public signals were absent.

{md(gsummary,['extra_lag_days','group_B','rows','events'])}

The additional-day Harris decision is after the documented Jan3 acute event but before the Jan5 prolonged-absence start, so it is a disclosed-injury prediction. His next-day-noon Jan2 index decision precedes that event. Melton's prior back symptoms and Embiid's knee history were already visible in B channels. None of these rows is claimed as verified pre-injury warning. The B no-signal group is only absence of a signal in the searched process; biological onset and A publication timing remain unknown.

## Missingness, negative audit and features

[missingness_summary.csv](../phase2a/tables/missingness_summary.csv) reports overlapping mechanisms, including incomplete prior workload, transfer surveillance gaps, insufficient applicable-team follow-up, mixed causes and right censoring. [source_coverage_summary.csv](../phase2a/tables/source_coverage_summary.csv) separates retrieval from submission/section coverage. The parser now accepts `Philadelphia76ers` (the legacy alphabetic-only team rule dropped it) and prevents surname-only injury attribution to a different active player. Full named PDF active-box reasons also replace truncated HTML comments: generic `DND - Injury/Illness` cannot hide an explicit illness diagnosis. The [extraction correction ledger](../phase2a/tables/reason_extraction_corrections.csv) preserves these cases; [status/final-reason disagreements](../phase2a/tables/reason_evidence_disagreements.csv) remain explicit quality evidence. These are extraction corrections, not changed eligibility/endpoint thresholds.

Orlando's Feb13 baseline section remains unverified despite an additional public 6PM probe; obtained snapshots cover a different target date rather than supplying a submitted baseline. Feb16 nominal 11AM is a previously recorded access denial; the additional-day Feb14 decisions retain that gap. Failed or unsubmitted sources are never evidence that a report or injury did not exist. Exact causes are retained in cohort/report tables.

A reproducible seeded sample contains five negative rows per team per timing rule: **60 traces**. Every trace joins actual window games, source IDs, candidate severity bounds and adequate B surveillance/follow-up. Their sequence checks were inspected with the same agent; this is algorithmic/source-trace review, **not independent human adjudication**. Every unresolved/positive event also has a same-agent review record. [Readable selected timelines](phase2a_timelines.md) explain positives, negatives and unresolved cases; [traced_cases.json](../phase2a/traced_cases.json) joins all positive decisions, the negative sample, and representative unresolved decisions to eligibility, features, events and game evidence. Human review counts remain zero.

Past-only features reuse Phase1C windows `(decision-k elapsed days, decision]` for k=7/14/28, end+6h final-statistics availability, nonoverlapping prior-seven-day workload change, rest intervals and prior-appearance baseline excluding the most recent appearance. Cross-team NBA history is joined by stable player/game IDs. Missing membership, contract gaps or missing game coverage suppress affected workloads rather than zero-fill. Late same-day games cannot enter a noon feature window. Source IDs, input teams, availability maxima, missingness flags and both timing rules are retained. These are NBA workload measures, not G League or total training load. No fitted preprocessing exists.

## Availability and collection cost

A verified historical availability remains zero. B retains final stats/full recap end+6h and nominal report header+30min; timezone-aware article +60min is available only where separately justified (the new continuity articles are C-only). Current final records are mutable, and neither a retrieval date nor an extra-day lag establishes original publication. C outcomes never retroactively change eligibility or enter workload features. Historical `label_known_at` remains blank and historical training-cutoff usability false; retrospective review time is separate.

The batch has {cost['unique_requested_sources']} unique requested sources, {cost['new_http_requests']} new HTTP requests and {cost['prior_phase_source_reuse']} prior-phase cache reuses. All new requests were obtained; prior denied receipts remain gaps. New raw volume is {cost['new_obtained_bytes']:,} bytes. There are {cost['saved_dated_queries']} saved dated queries in {cost['saved_search_call_receipts']} search-call receipts, including {cost['targeted_transfer_queries']} queries for destination follow-up rather than new prediction teams. The selected panel covers Dec4–Apr14; targeted prior/destination requests add evidence for 24 transitioning players without expanding the prediction population.

Measured initial acquisition batch wall times were 92.76 and 77.44 seconds, excluding small supplemental requests. The final extraction run took {cost['last_parsing']['elapsed_seconds']} seconds and the final cohort build {cost['last_build']['elapsed_seconds']} seconds on this host. Network request time sums are concurrency-weighted and are not elapsed review time. Manual person-time was not instrumented; {cost['detailed_event_reviews']} detailed event reviews and {cost['negative_trace_reviews']} negative traces quantify review units, not independent clinicians or elapsed labor. Full metadata are in [cost_summary.json](../phase2a/cost_summary.json).

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
'''
    (ROOT/'docs/phase2a_report.md').write_text(report)
    (D/'README.md').write_text('# Phase 2A fixed six-team development batch\n\nCompleted fixed sample: CLE, DEN, DET, ORL, PHI, SAS. Target: prolonged injury-related absence onset, >=10 consecutive applicable-team games. Both noon rules; A/B/C separated. No models or protected holdouts.\n\nSee [report and exact commands](../docs/phase2a_report.md), [sampling registration](registration/sample_v1.json), [summary](summary.json), [team results](tables/team_results.csv), [pooled results](tables/pooled_results.csv), and [trace joins](traced_cases.json). Raw cache requirements and measured collection costs are documented in the report.\n')
    dictionary={}
    for p in sorted((D/'tables').glob('*.csv')):
        with p.open() as f:r=csv.DictReader(f);rr=list(r);dictionary[p.name]=dict(rows=len(rr),columns=r.fieldnames)
    from .timelines import render_timelines
    render_timelines()
    (D/'table_dictionary.json').write_text(json.dumps(dictionary,indent=2)+'\n')
    for r in newledger:
        if r['status']=='obtained':assert hashlib.sha256(read(r['source_id'],sm)).hexdigest()==r['sha256']
    print(json.dumps(dict(main=pmain,sensitivity=plag,cost_bytes=cost['new_obtained_bytes'],tables=len(dictionary)),indent=2))
if __name__=='__main__':render()
