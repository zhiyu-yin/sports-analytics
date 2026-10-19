"""Deterministic field-level impact, missingness and source-linked audit report."""
from collections import Counter,defaultdict
from pathlib import Path
import csv,json,hashlib,subprocess
from injury_warning.pilot_io import ROOT
from .io import D,rows,write

def oldrows(name):
    with (ROOT/'phase2a/tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def equivalent(k,a,b):
    if a==b:return True
    if (k.endswith('_at') or k.endswith('_upper') or k.endswith('_lower')) and a and b:
        try:
            from injury_warning.rules import utc
            return utc(a)==utc(b)
        except ValueError:pass
    return False

def report():
    impacts=[];changes=[]
    keys={'game_timing':'game_id','cohort_all_roster_candidates':'row_id','row_outcomes':'row_id','features_B':'row_id','events':'event_id','event_prediction_coverage':None}
    for name,key in keys.items():
        old=oldrows(name);new=rows(name)
        def ident(r):return r[key] if key else r['event_id']+'_lag'+r['extra_lag_days']
        aa={ident(r):r for r in old};bb={ident(r):r for r in new};counts=Counter()
        for rid in sorted(set(aa)|set(bb)):
            a=aa.get(rid,{});b=bb.get(rid,{})
            fields=[k for k in set(a)&set(b) if not equivalent(k,a[k],b[k])]
            if name in {'cohort_all_roster_candidates','row_outcomes','events'}:fields+=list(set(b)-set(a))
            if not a or not b:fields=['__row_presence__']
            if not fields:continue
            reason='B history retained cumulatively; recent window/status expiry and event-specific disclosure separated'
            sources=b.get('signal_ids') or a.get('signal_ids') or b.get('source_ids') or a.get('source_ids','')
            if name=='event_prediction_coverage':reason='Recomputed qualifying-event severity and eligible preceding prediction coverage from reviewed segments/membership';sources=b.get('event_id',a.get('event_id',''))+'; injury_segments; event_game_evidence'
            if name=='events':reason='Systematic maximal injury-segment/common identity review; preserve original anchor; conservative finite schedule upper bound; source-linked membership repair';sources=b.get('continuity_source_ids') or b.get('source_ids') or a.get('source_ids','')
            if name=='row_outcomes' and 'absence_run_onset_ge10' in fields:reason='Reviewed qualifying injury-only segment inside longer mixed envelope; original first injury anchor preserved';sources=b.get('event_ids','')+'; see injury_segments and segment_reviews.json'
            if name=='features_B':reason='Recomputed from source-backed actual membership and audited clock inputs; no zero fill';sources='membership_repairs; input_game_ids in old/new values'
            if name=='game_timing':reason='Audited page Eastern wall-clock with official schedule/book; interval/precision retained';sources='page_'+rid+';book_'+rid
            common=dict(table=name,row_key=rid,extra_lag_days=b.get('extra_lag_days',a.get('extra_lag_days','')),changed_fields=';'.join(sorted(fields)),old_value=json.dumps((a if fields==['__row_presence__'] else {k:a.get(k) for k in sorted(fields)}) if a else None,sort_keys=True),new_value=json.dumps((b if fields==['__row_presence__'] else {k:b.get(k) for k in sorted(fields)}) if b else None,sort_keys=True),reason=reason,supporting_source_or_rule=sources+'; registration/amendment_v1.json; clock_source_clarification_v1.json; schedule_bound_clarification_v1.json')
            changes.append(common);counts[b.get('extra_lag_days',a.get('extra_lag_days',''))]+=1
        for lag in ['0','1','']:
            impacts.append(dict(table=name,extra_lag_days=lag,old_rows=sum(r.get('extra_lag_days','')==lag for r in old),new_rows=sum(r.get('extra_lag_days','')==lag for r in new),changed_existing_or_presence_rows=counts[lag]))
    write('changed_rows',changes);write('table_impact_summary',impacts)
    comparisons=[]
    for lag in ['0','1']:
        for version,load in [('before_phase2a',oldrows),('after_phase2b',rows)]:
            co=[r for r in load('cohort_all_roster_candidates') if r['extra_lag_days']==lag];out=[r for r in load('row_outcomes') if r['extra_lag_days']==lag];ev=[r for r in load('event_prediction_coverage') if r['extra_lag_days']==lag and r['broad_onset_period']=='True' and r['severity']=='positive'];ff=[r for r in load('features_B') if r['extra_lag_days']==lag]
            row=dict(scope='fixed_six_only',version=version,extra_lag_days=lag,appearances=sum(r['appeared']=='True' for r in co),included=sum(r['B_state']=='included' for r in co),excluded=sum(r['B_state']=='excluded' for r in co),eligibility_unknown=sum(r['B_state']=='unknown' for r in co),positive=sum(r['absence_run_onset_ge10']=='positive' for r in out),negative=sum(r['absence_run_onset_ge10']=='negative' for r in out),outcome_unknown=sum(r['absence_run_onset_ge10']=='unknown' for r in out),qualifying_events=len(ev),events_with_eligible_prediction=sum(r['has_eligible_preceding_prediction']=='True' for r in ev),eligible_positive_decisions=sum(r['absence_run_onset_ge10']=='positive' for r in out),missing_history=sum(r['history_complete']=='False' for r in ff),changed_feature_rows=sum(c['table']=='features_B' and c['extra_lag_days']==lag for c in changes) if version=='after_phase2b' else 0)
            for g in ['acute_already_disclosed','symptom_or_history_known','no_signal_found_under_searched_process']:row[g]=sum(r['absence_run_onset_ge10']=='positive' and r['group_B']==g for r in out)
            comparisons.append(row)
    write('before_after',comparisons)
    groups=[]
    for version,load in [('before_phase2a',oldrows),('after_phase2b',rows)]:
        for lag in ['0','1']:
            rr=[r for r in load('row_outcomes') if r['extra_lag_days']==lag]
            for group in sorted({r['group_B'] for r in rr}):
                gg=[r for r in rr if r['group_B']==group]
                groups.append(dict(version=version,extra_lag_days=lag,group_B=group,included_rows=len(gg),positive_rows=sum(r['absence_run_onset_ge10']=='positive' for r in gg),negative_rows=sum(r['absence_run_onset_ge10']=='negative' for r in gg),unknown_rows=sum(r['absence_run_onset_ge10']=='unknown' for r in gg)))
    write('knowledge_groups_before_after',groups)
    causes=[];causecounts=[]
    for version,load in [('before_phase2a',oldrows),('after_phase2b',rows)]:
        co=load('cohort_all_roster_candidates');out=load('row_outcomes');ff=load('features_B');links=defaultdict(list)
        for r in load('row_event_links'):
            if r['severity']=='unknown' and r['window_membership']!='False':links[r['row_id']].append(r['event_id'])
        for r in co:
            if r['B_state']=='unknown':causes.append(dict(version=version,row_id=r['row_id'],extra_lag_days=r['extra_lag_days'],cause='eligibility_source_or_submission_gap',detail=r['B_reason'],source_ids=r['decision_report_ids']+';'+r['baseline_report_ids']))
        for r in out:
            if r['absence_run_onset_ge10']!='unknown':continue
            if links[r['row_id']]:causes.append(dict(version=version,row_id=r['row_id'],extra_lag_days=r['extra_lag_days'],cause='event_attribution_severity_or_anchor_unresolved',detail=';'.join(links[r['row_id']]),source_ids='row_event_links; events; injury_segments'))
            if r['onset_surveillance_B']=='False':causes.append(dict(version=version,row_id=r['row_id'],extra_lag_days=r['extra_lag_days'],cause='actual_membership_or_bounded_surveillance_gap',detail=r['unknown_reason'],source_ids='membership_spells; daily_coverage; membership_gap_ledger'))
            if r['severity_followup_B']=='False':causes.append(dict(version=version,row_id=r['row_id'],extra_lag_days=r['extra_lag_days'],cause='incomplete_actual_team_severity_followup',detail=r['applicable_games_after_horizon'],source_ids='player_games; membership_spells'))
        for r in ff:
            if r['history_complete']=='False':causes.append(dict(version=version,row_id=r['row_id'],extra_lag_days=r['extra_lag_days'],cause='workload_history_unobserved_membership_or_game',detail=r['missing_history_reason'],source_ids='membership_spells; membership_repairs; input_game_ids'))
    write('row_missingness',causes)
    for (version,lag,cause),n in sorted(Counter((r['version'],r['extra_lag_days'],r['cause']) for r in causes).items()):causecounts.append(dict(version=version,extra_lag_days=lag,cause=cause,rows=n,nonexclusive=True))
    write('missingness_by_cause',causecounts)
    long=[]
    by=defaultdict(list)
    for r in rows('injury_segments'):by[r['event_id']].append(r)
    for e in rows('events'):
        if int(e['observed_games'])<10:continue
        parts=by[e['event_id']]
        long.append(dict(event_id=e['event_id'],player_id=e['player_id'],player_name=e['player_name'],anchor_date=e['anchor_date'],envelope_games=e['observed_games'],maximal_injury_segment_lengths=';'.join(r['consecutive_injury_games'] for r in parts),threshold_segments=sum(r['threshold_met']=='True' for r in parts),common_identity_supported_segments=sum(r['common_episode_supported']=='True' for r in parts),original_anchor_identity_uncertain=e['anchor_identity_uncertain'],severity=e['severity'],source_ids=e['source_ids'],review='; '.join(dict.fromkeys(r['review_note'] for r in parts)) or 'No complete injury-only segment; unknown reasons, noninjury reasons and membership gaps cannot supply injury attribution. Missing assertion: >=10 consecutive medically attributed games and common episode at original anchor.',remaining_assertion='' if e['severity']=='positive' else 'Common identity connecting >=10 consecutive individual injury misses to preserved original anchor and/or complete membership/followup not established; exact conflicting/unknown game reasons retained.'))
    write('long_envelope_audit',long)
    # Every unresolved expected player-game, rather than a selected list of names.
    from .build import sequences,norm
    from phase1d.acquire import schedule
    seq,cov=sequences([norm(r) for r in rows('player_games')],{r['game_id']:r for r in rows('game_timing')},json.loads((D/'membership_review_ranges.json').read_text()),schedule())
    gaps=[]
    for pid,gg in seq.items():
        for g in gg:
            if not g['roster_observed'] or g['category']=='unknown':gaps.append(dict(player_id=pid,player_name=g['player_name'],team=g['team'],game_id=g['game_id'],game_date=g['game_date'],roster_observed=g['roster_observed'],category=g['category'],reason=g['reason'],source_id=g['page_source']+';'+g['reason_source'],resolution='unresolved; missing roster/reason never treated as zero workload or injury'))
    write('unresolved_games',gaps)
    # Source-complete per-case traces, including all changed labels and named hypotheses.
    co={r['row_id']:r for r in rows('cohort_all_roster_candidates')};oo={r['row_id']:r for r in rows('row_outcomes')};ee={r['event_id']:r for r in rows('events')};feat={r['row_id']:r for r in rows('features_B')}
    named={r['row_id'] for r in co.values() if (r['player_id'],r['index_game_date']) in [('1630191','2024-01-28'),('203914','2024-01-02'),('1628386','2024-01-11')]}
    changedlabels={c['row_key'] for c in changes if c['table']=='row_outcomes' and 'absence_run_onset_ge10' in c['changed_fields']}
    traces=[]
    for rid in sorted(named|changedlabels):
        o=oo.get(rid,{});events=[ee[x] for x in o.get('event_ids','').split(';') if x in ee];traces.append(dict(row_id=rid,cohort=co[rid],before_outcome=next((r for r in oldrows('row_outcomes') if r['row_id']==rid),None),after_outcome=o,features=feat.get(rid),events=events,segments=[r for r in rows('injury_segments') if r['event_id'] in {e['event_id'] for e in events}]))
    (D/'traced_cases.json').write_text(json.dumps(traces,indent=2)+'\n')
    hashes=json.loads((D/'registration/preserved_hashes.json').read_text())
    for n,h in hashes.items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    summary=dict(before_after=comparisons,changed_rows_by_table=dict(Counter(r['table'] for r in changes)),missingness_nonexclusive=causecounts,all_prior_files_verified=len(hashes),root_README_sha256=hashlib.sha256(Path('README.md').read_bytes()).hexdigest(),models_trained=0,protected_holdouts_opened=False,amendment_commits=['acac9e4','59a0b38','7e4c6b8'],clock=json.loads((D/'clock_summary.json').read_text()),legacy=json.loads((D/'legacy_rebuild_summary.json').read_text()))
    (D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');render(summary)

def render(s):
    def md(rr):
        fields=['version','extra_lag_days','included','excluded','eligibility_unknown','positive','negative','outcome_unknown','qualifying_events','events_with_eligible_prediction','missing_history','changed_feature_rows']
        return '\n'.join(['| '+' | '.join(fields)+' |','| '+' | '.join(['---']*len(fields))+' |']+['| '+' | '.join(str(r[k]) for k in fields)+' |' for r in rr])
    doc='''# Phase 2B targeted data-quality audit

Target: a new documented injury-attributed absence run starts in the next 14 elapsed days and eventually has >=10 consecutive actual applicable-team missed games with supported common identity. This is an observable absence target, not biological onset or predictive success. Fixed six teams/dates only; no model trained; no protected holdout opened. Same-agent review is not independent human adjudication.

## Findings

- **Unsupported clock concern:** 708 acquired game pages and 708 official books audited, including Boston and fixtures. Page period timestamps are Eastern wall clocks; `gameTimeUTC` is scheduled UTC, while `gameEt` has a misleading Z and is never interpreted as UTC. All 704 extracted book starts and 708 ends match venue-local conversions within 0–1 minute. Book clocks lack zone suffixes; arena location supplies the independently interpretable comparison, including Paris and non-DST Phoenix. Four book starts were not extracted by the bounded locator; their scheduled UTC and full end checks remain available. Page/source-specific minute bounds are retained, not exact second timestamps. Literal fixed EST after March10 would introduce an error; raw evidence refuted that initial hypothesis. Separate source clarification was committed before outcome regeneration.
- **Named clocks unchanged:** Embiid Feb1 first-period start 22:16 Eastern, scheduled 22:00, book 20:15 Mountain; Harris Jan2 final end 00:39 Eastern on Jan3, upper 00:40, book 21:39 Pacific; Allen Paris Jan11 final end 16:42 Eastern, upper 16:43, book 22:42 CET. First-period and final-period fields are distinct; calendar rollover is explicit. No established timing correction, anchor shift or workload change results. All absence anchors and both lags were rebuilt from audited timing. Boston numeric workloads and Phase1D labels/fixtures were independently rebuilt in `boston_fixture_rebuild`, outside six-team counts.
- **Confirmed knowledge semantics defect / missing methodological rule:** Phase2A did use all eligible past evidence, but dropped injury reports after seven days and recaps after 28. Stewart Jan28 falls across report expiry, so history was falsely described as no signal. Amendment separates cumulative acquired B history, 28-day recent evidence, game-specific latest status, explicit supersession, and status expiry after target-game completion. Omission never resolves history. History completeness is bounded by acquired channels, not lifetime history. Generic/negative rows no longer carry an event-specific acute flag; only retrospectively linked positive-event strata may use that flag. C linkage is descriptive, never an eligibility or predictor input. Clinical recovery is never inferred from appearance.
- **Confirmed subrun omission:** Strawther has 13 consecutive injury-attributed games Jan5–Jan31, followed by coaching/assignment/coaching before Feb9 NBA appearance. Official contemporaneous reports, full gamebooks, and reviewed return/clearance context establish one right-knee episode. Subsequent noninjury reasons cannot undo this segment. Cissoko has ten Jan10–Jan26 individual ankle-attributed games, with serial ongoing-absence updates and contemporaneous reports supporting common identity; later assignments are not added. His Jan7 report/assignment disagreement remains in the quality ledger; Jan10 remains the registered first final-game injury attribution, not clinical onset. He has no preceding January-period positive-minute prediction. Covington has a later 41-game knee-attributed segment with a supported qualifying subset, but Jan6 illness prevents establishing identity with the original Jan2 anchor: event remains unknown, anchor unchanged. Stewart's Jan31 envelope contains medical segments of four and three games, interrupted by coaching and followed by suspension, so it cannot supply ten. Every maximal segment is in `injury_segments.csv`; matching diagnosis alone does not certify any other segment.
- **Membership audit:** priority is determined from baseline affected-row counts in `membership_gap_ledger.csv`. Official Feb9 waiver timestamps remove speculative post-waiver Utah/Indiana games for Knox/Korkmaz. Nance's ten-day and later two-way contracts replace an unsupported continuous roster span; exact gap remains unverified, without zero fill. Diakite's Jan1 signing is confirmed but earlier NBA workload remains unverified; Morris's Feb29 waiver/Mar18 return confirms a real contract gap. Beverley/McDermott one-game trade envelopes have a finite actual-schedule upper bound, even when onboarding roster is missing; this does not by itself establish negative surveillance. The failed House waiver URL is retained and no date is inferred. All unresolved expected game reasons/roster entries are preserved in `unresolved_games.csv`, and every unresolved row has nonexclusive causes in `row_missingness.csv`.

## Before/after (six-team cohort only)

'''+md(s['before_after'])+'''

Six confirmed broad-period qualifying events now include Harris, Melton, Livers, Embiid, Strawther and Cissoko; five have eligible preceding predictions. Strawther adds two main and one extra-day positive decisions; all were formerly unknown. These are descriptive adjudication changes, not improved predictions. Inclusion, negative counts and numeric workload features are unchanged. Existing-positive knowledge strata can change because history now persists under the amendment; `before_after.csv` gives each group. Missingness causes are nonexclusive, and unchanged unknowns must not be interpreted as complete surveillance.

## Trace and source audit

`changed_rows.csv` stores every changed existing field or removed/added row, old/new values, reason and source/rule joins for timing, eligibility/knowledge, outcomes, features, events and event prediction coverage. Newly introduced knowledge fields are in the complete candidate/outcome tables. `traced_cases.json` includes all changed labels and both lags of the three named row hypotheses. Each event joins to all individual games, source IDs and common-identity review; historical label-known-at stays blank. `table_impact_summary.csv`, `missingness_by_cause.csv`, `all_acquired_game_clock_audit.csv`, `legacy_clock_impact.csv` and the separate Boston/fixture rebuild provide unchanged-result evidence.

Sources are identified by SHA-256 in Phase2A/earlier manifests or `source_manifest.json`; locators in segment reviews refer to original public sources. Targeted source bodies are ignored local raw cache only. The complete long-envelope inventory, segment lengths, source IDs and missing assertions are in `long_envelope_audit.csv`. No full article or search body is included in reviewable derived tables. Review evidence includes [Denver Jan29](https://www.nba.com/nuggets/news/nuggets-and-bucks-play-in-battle-of-two-title-contenders), [Denver Feb4 assignment](https://www.nba.com/nuggets/news/nuggets-play-trail-blazers-for-second-time-in-three-days), [Strawther return reporting](https://gazette.com/2024/02/09/julian-strawther-is-back-from-injury-but-michael-malone-says-nuggets-plan-to-stick-with-jamal-murray-led-second-unit/), [Cissoko dated updates](https://www.foxsports.com/nba/sidy-cissoko-2-player?p=4), [Utah waiver](https://www.nba.com/jazz/news/utah-jazz-waive-kevin-knox-ii), [Indiana waiver](https://www.nba.com/pacers/news/indiana-pacers-waive-furkan-korkmaz), [Nance short contract](https://gleague.nba.com/news/cavaliers-sign-pete-nance-to-10-day-contract), [Nance two-way](https://www.nba.com/cavaliers/news/releases-pete-nance-two-way-240219), [Diakite signing](https://www.nba.com/spurs/news/spurs-sign-mamadi-diakite-to-two-way-contract), [Morris contract](https://www.nba.com/news/cleveland-cavaliers-marcus-morris-10-day-contract), and [Stewart suspension](https://www.nba.com/news/pistons-isaiah-stewart-suspension). Only dated 2023–24 evidence enters review; unrelated current site navigation/search hits are not cohort data.

## Registration chronology and reproduction

Development amendment `acac9e4`; source-clock clarification `59a0b38`; finite-schedule-bound clarification `7e4c6b8`. Each is a separate commit before Phase2B result regeneration. JSON and SHA files are in `registration/`. Earlier protocol commits and Phase2A tables are preserved byte-for-byte by `preserved_hashes.json`. Root README remains unchanged and unstaged.

From repository root:

```sh
export PYTHONPATH=basketball/nba/injury-warning/src:basketball/nba/injury-warning
python3 -m phase2b.io
python3 -m phase2b.acquire
# Use a Python with pypdf; no terminal TeX or other new dependency needed.
/Users/zhiyuyin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m phase2b.clocks
python3 -m phase2b.membership
python3 -m phase2b.build
python3 -m phase2b.legacy_audit
python3 -m phase2b.report
python3 -m unittest discover -s basketball/nba/injury-warning/tests -q
```

Acquisition is resumable; it does not retry recorded failures or bypass denied endpoints. Offline reproduction requires all checksummed raw files named in Phase2A/earlier source manifests and the Phase2B manifest; cache files stay in ignored `data/raw`. Source availability is not guaranteed by the public site. Public B assumptions remain final stats/recaps end-upper+6h and report header+30min; no verified first historical publication is established. Targeted new narratives/contracts are C only. No trained model, calibration, discrimination, clinical forecast, causal claim or generalization estimate is warranted.

Next expansion: freeze these rules and evidence templates, then preregister a further seeded, disjoint development-team batch with the same dates and a fixed acquisition budget. Do not redraw for events; require early contract-boundary review and independent adjudication where possible before considering model training. No new expansion has been started here.
'''
    (ROOT/'docs/phase2b_report.md').write_text(doc)
    (D/'README.md').write_text('# Phase 2B targeted audit\n\nFixed Phase2A six teams and dates; versioned repair, no training/holdout. See [report](../docs/phase2b_report.md), [before/after](tables/before_after.csv), [changed rows](tables/changed_rows.csv), [clock audit](tables/all_acquired_game_clock_audit.csv), [segments](tables/injury_segments.csv), [registration](registration/amendment_v1.json). Raw-cache and exact reproduction requirements are in the report.\n')
if __name__=='__main__':report()
