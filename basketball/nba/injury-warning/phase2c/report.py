"""Canonical batch/cumulative summaries, source traces and pending human review."""
from collections import Counter,defaultdict
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
from .pipeline import D,ROOT,rows,write,manifest,registration,schedule,verify

def historical(phase,name):
    with (ROOT/phase/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def truth(x):return x is True or x=='True'
def normalize_boston():
    co=historical('phase1c','cohort_all_candidates');oo={r['row_id']:r for r in historical('phase1d','row_outcomes')};ff={r['row_id']:r for r in historical('phase1c','features_assumption_B')}
    out=[]
    for r in co:
        o=oo.get(r['row_id'],{});f=ff.get(r['row_id'],{})
        out.append(dict(r,team='BOS',absence_run_onset_ge10=o.get('absence_run_onset_ge10',''),event_ids='',group_B='legacy_knowledge_fields_not_retrospectively_reclassified',history_complete=f.get('history_complete_28d',''),onset_surveillance_B=o.get('B_coverage',''),severity_followup_B=o.get('applicable_team_followup',''),scope='Boston_prior'))
    return out

def report():
    verify();sm=manifest();sources={sid:dict(url=r.get('url',''),sha256=r.get('sha256',''),status=r['status']) for sid,r in sm.items()};newco=rows('cohort_all_roster_candidates');newo={r['row_id']:r for r in rows('row_outcomes')};newf={r['row_id']:r for r in rows('features_B')}
    oldco=historical('phase2b','cohort_all_roster_candidates');oldo={r['row_id']:r for r in historical('phase2b','row_outcomes')};oldf={r['row_id']:r for r in historical('phase2b','features_B')}
    def merge(co,out,feat,scope):return [dict(r,**{k:v for k,v in out.get(r['row_id'],{}).items() if k not in {'team','player_id','extra_lag_days','decision_at','window_end'}},history_complete=feat.get(r['row_id'],{}).get('history_complete',''),scope=scope) for r in co]
    groups={'new_six_phase2c':merge(newco,newo,newf,'new_six_phase2c'),'first_six_audited_phase2b':merge(oldco,oldo,oldf,'first_six_audited_phase2b'),'Boston_prior':normalize_boston()}
    union={};duplicates=[]
    for scope,rr in groups.items():
        for r in rr:
            key=r['index_game_id']+'_'+r['player_id']+'_lag'+r['extra_lag_days']
            if key in union:
                old=union[key];duplicates.append(dict(canonical_decision_id=key,scope1=old['scope'],scope2=scope,state1=old['B_state'],state2=r['B_state']))
                # Same-game transfers may duplicate an inactive inventory entry;
                # only a verified positive-minute appearance is a prediction row.
                if truth(r['appeared']) and not truth(old['appeared']):union[key]=r
                elif truth(r['appeared']) and truth(old['appeared']):assert old['B_state']==r['B_state'] and old.get('absence_run_onset_ge10')==r.get('absence_run_onset_ge10'),key
            else:union[key]=r
    groups['combined_development']=list(union.values());write('canonical_decision_duplicates',duplicates)
    events=rows('events');old_events=historical('phase2b','events');event_union={};eventdups=[]
    for scope,ee in [('new_six_phase2c',events),('first_six_audited_phase2b',old_events)]:
        for e in ee:
            key=e['player_id']+'_'+e['anchor_game_id'];e=dict(e,canonical_event_id=key,scope=scope)
            if key in event_union:
                prev=event_union[key];eventdups.append(dict(canonical_event_id=key,scope1=prev['scope'],scope2=scope,severity1=prev['severity'],severity2=e['severity']))
                if e['severity']=='positive' and prev['severity']!='positive':event_union[key]=e
            else:event_union[key]=e
    write('canonical_event_duplicates',eventdups);write('canonical_events',event_union.values())
    tables=[];teamtables=[];knowledge=[];concentration=[];ranges=[]
    event_by_scope={'new_six_phase2c':events,'first_six_audited_phase2b':old_events,'Boston_prior':[],'combined_development':list(event_union.values())}
    for scope,rr in groups.items():
        for lag in ['0','1']:
            cr=[r for r in rr if r['extra_lag_days']==lag];inc=[r for r in cr if r['B_state']=='included'];ee=[e for e in event_by_scope[scope] if e['severity']=='positive' and truth(e['candidate_broad_onset_period'])];eligible_ids={eid for r in inc if r.get('absence_run_onset_ge10')=='positive' for eid in r['event_ids'].split(';') if eid}
            inventory={r['player_id'] for r in cr}
            additional=[r for r in rows('contract_only_inventory') if r['team'] in {x['team'] for x in cr}] if scope in {'new_six_phase2c','combined_development'} and (D/'tables/contract_only_inventory.csv').exists() else []
            row=dict(scope=scope,extra_lag_days=lag,distinct_membership_inventory_players=len(inventory|{r['player_id'] for r in additional}),contract_only_unobserved_players=len({r['player_id'] for r in additional}-inventory),team_game_exposures=len({(r['team'],r['index_game_id']) for r in cr}),distinct_physical_games=len({r['index_game_id'] for r in cr}),distinct_roster_players=len({r['player_id'] for r in cr}),distinct_recently_active_players=len({r['player_id'] for r in cr if truth(r['appeared'])}),candidate_appearances=sum(truth(r['appeared']) for r in cr),included=len(inc),excluded=sum(r['B_state']=='excluded' for r in cr),eligibility_unknown=sum(r['B_state']=='unknown' for r in cr),positive=sum(r.get('absence_run_onset_ge10')=='positive' for r in inc),negative=sum(r.get('absence_run_onset_ge10')=='negative' for r in inc),outcome_unknown=sum(r.get('absence_run_onset_ge10')=='unknown' for r in inc),distinct_qualifying_events=len(ee),distinct_event_players=len({e['player_id'] for e in ee}),events_with_eligible_preceding_prediction=len(eligible_ids),B_feature_rows=len(inc),A_verified_rows=0,A_original_publication_unresolved_rows=len(inc),missing_workload=sum(r.get('history_complete')=='False' for r in inc),onset_surveillance_gaps=sum(r.get('onset_surveillance_B')=='False' for r in inc),severity_followup_gaps=sum(r.get('severity_followup_B')=='False' for r in inc))
            assert row['positive']+row['negative']+row['outcome_unknown']==row['included'];tables.append(row)
            ranges.append(dict(scope=scope,extra_lag_days=lag,included=row['included'],positive=row['positive'],unknown=row['outcome_unknown'],lower_if_unknown_negative=row['positive']/row['included'] if row['included'] else None,upper_if_unknown_positive=(row['positive']+row['outcome_unknown'])/row['included'] if row['included'] else None,interpretation='worst-case identification range conditional on included rows; not confidence interval, estimated injury rate or annual incidence'))
            for g in ['acute_already_disclosed','symptom_or_history_known','no_signal_found_under_searched_process','knowledge_timing_unresolved']:
                pos=[r for r in inc if r.get('absence_run_onset_ge10')=='positive' and (r.get('group_B')==g if g!='knowledge_timing_unresolved' else r.get('group_A')==g)]
                knowledge.append(dict(scope=scope,extra_lag_days=lag,knowledge_group=g,positive_rows=len(pos),distinct_events=len({eid for r in pos for eid in r['event_ids'].split(';') if eid}),evidence_category='A' if g=='knowledge_timing_unresolved' else 'B',note='A unresolved overlaps B strata; B signal absence is bounded search only'))
            for team in sorted({r['team'] for r in cr}):
                tr=[r for r in cr if r['team']==team];tt=[r for r in tr if r['B_state']=='included'];teamtables.append(dict(scope=scope,team=team,extra_lag_days=lag,games=len({r['index_game_id'] for r in tr}),players=len({r['player_id'] for r in tr}),appearances=sum(truth(r['appeared']) for r in tr),included=len(tt),excluded=sum(r['B_state']=='excluded' for r in tr),eligibility_unknown=sum(r['B_state']=='unknown' for r in tr),**{label:sum(r.get('absence_run_onset_ge10')==label for r in tt) for label in ['positive','negative','unknown']},missing_workload=sum(r.get('history_complete')=='False' for r in tt)))
            for e in ee:
                pos=[r for r in inc if r.get('absence_run_onset_ge10')=='positive' and e['event_id'] in r['event_ids'].split(';')]
                concentration.append(dict(scope=scope,extra_lag_days=lag,event_id=e['event_id'],canonical_event_id=e['player_id']+'_'+e['anchor_game_id'],player_id=e['player_id'],player_name=e['player_name'],anchor_team=e['anchor_team'],sampled_origin_team=e['sampled_origin_team'],anchor_date=e['anchor_date'],positive_rows=len(pos),eligible_decision_ids=';'.join(r['row_id'] for r in pos),knowledge_groups=';'.join(sorted({r['group_B'] for r in pos})),not_independent_events_per_row=True))
    write('scope_results',tables);write('scope_team_results',teamtables);write('positive_knowledge_groups',knowledge);write('missing_label_identification_ranges',ranges);write('positive_rows_per_event',concentration)
    # Concentration measures use events, not repeated positive decisions.
    ec=[]
    for scope in event_by_scope:
        ee=[e for e in event_by_scope[scope] if e['severity']=='positive' and truth(e['candidate_broad_onset_period'])]
        for dimension,key in [('team','sampled_origin_team'),('player','player_id')]:
            for value,n in sorted(Counter(e[key] for e in ee).items()):ec.append(dict(scope=scope,dimension=dimension,value=value,events=n,event_fraction=n/len(ee) if ee else None))
    write('event_concentration',ec)
    prepare_review(groups['new_six_phase2c'],events,sources)
    quality_and_cost(sm,groups)
    summary=dict(registration_commit=json.loads((D/'registration/commit_receipt.json').read_text())['sampling_commit'],frozen_checkpoint=json.loads((D/'registration/collection_v1.json').read_text())['checkpoint_commit'],selected=[r['team'] for r in registration()['selected']],scope_results=tables,identification_ranges=ranges,canonical_duplicate_decisions=len(duplicates),canonical_duplicate_events=len(eventdups),independent_human_reviews=0,models_trained=0,protected_holdouts_opened=False,all_prior_hashes_verified=True)
    (D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');render(summary)

def urls(ids,sources):return ';'.join(dict.fromkeys(sources.get(s.split('#')[0].strip(),{}).get('url','') for s in ids.split(';') if s.strip()))
def prepare_review(co,events,sources):
    evidence=rows('event_game_evidence');segments=rows('injury_segments');oo={r['row_id']:r for r in rows('row_outcomes')};ff={r['row_id']:r for r in rows('features_B')};cc={r['row_id']:r for r in co};packet=[];traces=[]
    links=rows('row_event_links');uncert=Counter(r['event_id'] for r in links if r['severity']=='unknown' and r['window_membership']!='False')
    positive=[e for e in events if e['severity']=='positive' and truth(e['candidate_broad_onset_period'])];unknown=sorted([e for e in events if e['severity']=='unknown'],key=lambda e:(-uncert[e['event_id']],-int(e['observed_games']),e['event_id']))[:10]
    for role,ee in [('confirmed_positive_event',positive),('consequential_unresolved_event',unknown)]:
        for e in ee:
            games=[g for g in evidence if g['event_id']==e['event_id']];first=games[:10];ids=e.get('continuity_source_ids','')+';'+(';'.join(g['reason_source']+';'+g['page_source'] for g in first));sg=[r for r in segments if r['event_id']==e['event_id']]
            packet.append(dict(review_id=e['event_id'],role=role,player_id=e['player_id'],player_name=e['player_name'],anchor_date=e['anchor_date'],current_label=e['severity'],short_assertion=e.get('continuity_review_note') or 'Individual reasons and segment lengths reviewed; identity/anchor or membership/followup remains unresolved. See attached evidence.',consequential_candidate_rows=uncert[e['event_id']],source_urls=urls(ids,sources),exact_locators=e.get('continuity_locator','')+'; FINAL BOX: inactive/active nonappearance reasons; individual game IDs in event_game_evidence',evidence_table='event_game_evidence.csv;injury_segments.csv',accept_amend_reject='',amended_value='',reviewer_name='',review_date='',review_notes='',human_review_completed=False))
            traces.append(dict(review_id=e['event_id'],event=e,games=games,segments=sg,preceding_positive_rows=[r for r in co if r.get('absence_run_onset_ge10')=='positive' and e['event_id'] in r['event_ids'].split(';')],sources={k.strip():sources.get(k.strip()) for k in ids.split(';') if k.strip()}))
    for r in rows('negative_sample_review'):
        o=oo[r['row_id']];ids=r['window_source_ids']+';'+cc[r['row_id']].get('baseline_report_ids','')+';'+cc[r['row_id']].get('decision_report_ids','');packet.append(dict(review_id=r['row_id'],role='seeded_negative_row',player_id=r['player_id'],player_name=cc[r['row_id']]['player_name'],anchor_date='',current_label='negative',short_assertion='Actual applicable-team schedule, bounded source surveillance and finite candidate severity checked. Negative is conditional on registered search; not proof of health.',consequential_candidate_rows=1,source_urls=urls(ids,sources),exact_locators='FINAL BOX; story.content; source IDs/window game IDs in negative_sample_review; reports header and target game/player rows',evidence_table='negative_sample_review.csv; negative_original_source_audit.csv; row_event_links.csv',accept_amend_reject='',amended_value='',reviewer_name='',review_date='',review_notes='',human_review_completed=False))
        traces.append(dict(review_id=r['row_id'],cohort=cc[r['row_id']],outcome=o,features=ff[r['row_id']],negative_review=r,sources={k:sources.get(k) for k in ids.split(';')}))
    write('human_review_packet',packet);(D/'traced_cases.json').write_text(json.dumps(traces,indent=2)+'\n')
    text='# Phase 2C pending human review\n\nNo independent human review has occurred. Each row in `tables/human_review_packet.csv` has direct source URLs, short assertions, locators, and blank accept/amend/reject, amended-value, reviewer and notes fields. Review every confirmed broad-period positive event, ten consequential unknowns, and all60 seeded negatives (five per team per lag). Detailed joins are in `traced_cases.json`; repeated decisions are not independent events.\n\n'
    for p in packet[:len(positive)+len(unknown)]:text+='- **'+p['review_id']+'** ('+p['role']+'): '+p['short_assertion']+' Locators: '+p['exact_locators']+'\n'
    (D/'human_review_packet.md').write_text(text)

def quality_and_cost(sm,groups):
    # Compare the separately retained draft from the new adapter bug, not Phase2B.
    prior=D/'quality/source_binding_before';imp=[];before=[]
    for name,key in [('cohort_all_roster_candidates','row_id'),('row_outcomes','row_id'),('features_B','row_id'),('game_timing','game_id')]:
        with (prior/(name+'.csv')).open() as f:aa={r[key]:r for r in csv.DictReader(f)}
        bb={r[key]:r for r in rows(name)}
        for rid in sorted(set(aa)|set(bb)):
            a=aa.get(rid,{});b=bb.get(rid,{});changed=[k for k in set(a)&set(b) if a[k]!=b[k]]
            if not a or not b:changed=['row_presence']
            if changed:imp.append(dict(table=name,row_key=rid,changed_fields=';'.join(sorted(changed)),old_values=json.dumps({k:a.get(k) for k in changed},sort_keys=True),new_values=json.dumps({k:b.get(k) for k in changed},sort_keys=True),reason='New batch cache binding fixed; explicit immutable prior ledgers, prior receipt precedence, source-SHA-aware parsed-report invalidation',support='quality/source_binding_before/;source_binding_manifest_impact.csv'))
    write('source_binding_row_impact',imp)
    with (prior/'team_results.csv').open() as f:tt=list(csv.DictReader(f))
    for lag in ['0','1']:
        for version,rr in [('draft_before_cache_binding_fix',tt),('after_cache_binding_fix',rows('team_results'))]:
            q=[r for r in rr if r['extra_lag_days']==lag];before.append(dict(version=version,extra_lag_days=lag,**{k:sum(int(r[k]) for r in q) for k in ['included','excluded','eligibility_unknown','positive','negative','outcome_unknown','missing_history']}))
    write('source_binding_before_after',before)
    # Unresolved events and expected player-games remain explicit.
    from phase2b.build import sequences,norm
    from .pipeline import bindings
    with bindings():seq,cov=sequences([norm(r) for r in rows('player_games')],{r['game_id']:r for r in rows('game_timing')},json.loads((D/'membership_review_ranges.json').read_text()),schedule())
    gaps=[]
    for pid,gg in seq.items():
        for g in gg:
            if not g['roster_observed'] or g['category']=='unknown':gaps.append(dict(player_id=pid,player_name=g['player_name'],team=g['team'],game_id=g['game_id'],date=g['game_date'],roster_observed=g['roster_observed'],category=g['category'],reason=g['reason'],source_ids=g['page_source']+';'+g['reason_source'],resolution='unresolved; never zero-filled or inferred injury'))
    write('unresolved_player_games',gaps)
    boundaries=[]
    for r in rows('player_games'):
        if r['player_id'] not in cov:continue
        matching=[x for x in cov[r['player_id']]['spells'] if x['team']==r['team'] and x['start']<=r['game_date']<=x['end']]
        if not matching:boundaries.append(dict(player_id=r['player_id'],team=r['team'],game_id=r['game_id'],date=r['game_date'],raw_roster_observed=r['roster_observed'],appeared=r['appeared'],raw_minutes=r['minutes'],source_ids=r['page_source']+';'+r['reason_source'],decision='Raw roster retained; outside conservative reviewed spell. Transaction-day/short-contract membership uncertain, never filled with zero or injury.',positive_appearance_outside_spell=truth(r['appeared'])))
    write('membership_boundary_conflicts',boundaries)
    # Exhaustive potential-event review ledger, including out-of-window/censored
    # cases. The human packet is a compact subset; this ledger is not.
    er=[];links=defaultdict(list)
    for x in rows('row_event_links'):
        if x['window_membership']!='False':links[x['event_id']].append(x['row_id'])
    for e in rows('events'):
        if e['severity']=='negative':continue
        er.append(dict(event_id=e['event_id'],player_id=e['player_id'],player_name=e['player_name'],anchor_date=e['anchor_date'],registered_anchor_attribution=e['anchor_attribution'],severity=e['severity'],observed_games=e['observed_games'],maximal_medical_segment=e['longest_injury_only_segment'],mixed_categories=e['mixed_categories'],roster_gap_count=e['roster_gap_count'],contract_gap=e['contract_gap_in_run'],original_anchor_uncertainty=e['anchor_identity_uncertain'],candidate_decision_rows=len(set(links[e['event_id']])),common_identity_review=e.get('continuity_review_note',''),remaining_assertion='' if e['severity']=='positive' else 'No supported ten-game common episode at preserved anchor, or unverified membership/source/return bound. Recorded individual reasons/segments retained; no combining short segments or inferring injury from absence.',source_ids=e['source_ids'],continuity_source_ids=e.get('continuity_source_ids',''),evidence_locator=e.get('continuity_locator','')+'; FINAL BOX; injury_segments; event_game_evidence',review_type='same-agent sequence/source review, not independent human'))
    write('event_review_ledger',er)
    missing=[]
    for r in groups['new_six_phase2c']:
        causes=[]
        if r['B_state']=='unknown':causes.append('eligibility_report_submission_or_source_gap')
        if r.get('absence_run_onset_ge10')=='unknown':
            if r.get('onset_surveillance_B')=='False':causes.append('membership_or_bounded_onset_surveillance_gap')
            if r.get('severity_followup_B')=='False':causes.append('incomplete_actual_team_severity_followup')
            causes.append('unresolved_event_identity_attribution_anchor_or_bound')
        if r.get('history_complete')=='False':causes.append('unobserved_prior_NBA_membership_or_game_history')
        for cause in causes:missing.append(dict(row_id=r['row_id'],team=r['team'],player_id=r['player_id'],extra_lag_days=r['extra_lag_days'],cause=cause,nonexclusive=True,evidence='row_outcomes;row_event_links;membership_spells;daily_coverage;unresolved_player_games'))
    write('row_missingness',missing)
    write('missingness_by_cause',[dict(extra_lag_days=lag,cause=cause,rows=n,nonexclusive=True) for (lag,cause),n in sorted(Counter((r['extra_lag_days'],r['cause']) for r in missing).items())])
    own=list(map(json.loads,(D/'source_manifest.jsonl').read_text().splitlines()));requests=json.loads((D/'request_catalog.json').read_text());current_selected={r['source_id'] for r in requests};query=rows('daily_coverage');search=json.loads((D/'search_ledger.json').read_text());raw_search=list((ROOT/'data/raw/phase2c/searches').glob('*.json'));news_rejections=[dict(source_id=r['source_id'],requested_date=r.get('date'),reason='Same title is an unrelated 2022 release; rejected for2024 membership',url=r.get('url')) for r in own if r['url'].endswith('/knicks-waive-taj-gibson')]
    write('source_applicability_rejections',news_rejections)
    duplicate_receipts=[]
    from phase1d.acquire import manifest as base
    old=base()
    for r in map(json.loads,(ROOT/'phase2a/source_manifest.jsonl').read_text().splitlines()):old[r['source_id']]=r
    for r in own:
        if r['source_id'] in old:duplicate_receipts.append(dict(source_id=r['source_id'],prior_status=old[r['source_id']]['status'],redundant_request_status=r['status'],retained_source_sha256=old[r['source_id']].get('sha256',''),duplicate_sha256=r.get('sha256',''),used_in_corrected_pipeline=False,reason='Retained redundant request receipt from diagnosed new batch adapter bug; original success/failure takes precedence. No alternate host/proxy/access bypass.'))
    write('duplicate_request_receipts',duplicate_receipts)
    cp=dict(actual_new_http_requests=len(own),actual_http_status=dict(Counter(r['status'] for r in own)),new_request_bytes=sum(r.get('bytes',0) for r in own),source_catalog_unique=len(current_selected),catalog_prior_cache_reused=len(current_selected&set(old)),catalog_without_new_attempt=len(current_selected-{r['source_id'] for r in own}),intrabatch_duplicate_url_attempts=len(own)-len({r['url'] for r in own}),redundant_http_requests_from_adapter_bug=len(duplicate_receipts),actual_new_search_queries=sum(len(json.loads(p.read_text())['queries']) for p in raw_search if p.name!='reused_target.json'),new_search_call_receipts=len([p for p in raw_search if p.name!='reused_target.json']),reused_executed_target_queries=sum(1 for q in search if q.get('scope')=='reused_executed_targeted_query'),manual_supplemental_search_effort='Additional targeted interactive contract/continuity lookups performed; not instrumented as fixed dated searches; no invented elapsed review time',agent_adjudication=dict(recap_cards=285,prior_team_cards=8,negative_rows=len(rows('negative_sample_review')),independent_human_reviews=0),current_pipeline_parsing=json.loads((D/'parsing_summary.json').read_text()),clock_audit=json.loads((D/'clock_summary.json').read_text()))
    (D/'cost_and_quality.json').write_text(json.dumps(cp,indent=2)+'\n')
    # A single fixed proposed extension; metadata cost estimate, no extra collection.
    remaining={g['team'] for g in schedule()}-{'BOS','CLE','DEN','DET','ORL','PHI','SAS'}-{r['team'] for r in registration()['selected']};games={g['game_id'] for g in schedule() if g['team'] in remaining and '2023-12-04'<=g['game_date']<='2024-04-14'};missing=[kind+'_'+gid for gid in games for kind in ['page','book'] if kind+'_'+gid not in sm]
    (D/'next_scope_cost_estimate.json').write_text(json.dumps(dict(proposed_prediction_teams=sorted(remaining),team_count=len(remaining),index_dates=['2024-01-01','2024-02-18'],scope='All remaining17 teams as one fixed development collection phase; no event-count stopping; separate future preregistration required',uncached_core_game_page_book_requests=len(missing),additional_daily_dated_queries_upper=len(remaining)*63,estimated_new_core_raw_bytes_range=[len(missing)*150000,len(missing)*700000],targeted_transfer_requests='Additional bounded actual-member requests; most source games already cached, exact ledger established before acquisition',estimated_agent_review_hours=[15,30],estimated_independent_human_adjudication_hours=[8,16],estimates_not_measured_work=True,not_collected=True),indent=2)+'\n')

def render(s):
    cols=['scope','extra_lag_days','candidate_appearances','included','excluded','eligibility_unknown','positive','negative','outcome_unknown','distinct_qualifying_events','events_with_eligible_preceding_prediction','missing_workload']
    table='\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(str(r[c]) for c in cols)+' |' for r in s['scope_results']])
    cost=json.loads((D/'cost_and_quality.json').read_text());nextcost=json.loads((D/'next_scope_cost_estimate.json').read_text())
    doc=f'''# Phase 2C second fixed development batch

Completed six teams: ATL, DAL, NYK, SAC, OKC, MEM. Sampling commit `{s['registration_commit']}`; frozen Phase2B checkpoint `{s['frozen_checkpoint']}`. Seed20240219,23-team numeric-ID frame, no redraw. Prior transfer/fixture familiarity is disclosed in the registration; this is development collection, not unseen validation. No model, preprocessing fit, tuning, protected holdout or annual-rate inference.

## Frozen target and evidence

New documented injury-related absence-run onset in the next14 elapsed days, eventually >=10 consecutive actual applicable-team injury misses with reviewed common identity. Next-day noon ET and one additional calendar-day noon sensitivity; 28-day workload/history windows, cumulative acquired history versus recent evidence and expiring game-specific status remain Phase2B rules. Qualifying maximal medical segments survive later coaching/assignment/noninjury/censoring, which do not count toward ten. Ambiguous original anchors stay ambiguous. Clinical onset and recovery are not inferred from appearances.

All game/roster/recap extraction reuses Phase2A functions; clocks, knowledge, sequence/event logic and cohort build reuse Phase2B functions through isolated runtime bindings. No copied parallel event implementation. Code hashes and original protocol/amendment commits are in `registration/collection_v1.json`. The adapter changes paths, team scope, review seed and metadata only. The old hardcoded DET contract-only inventory entry is filtered from this new six-team export. An unanswered human-review packet does not imply review occurred. Contract-only transaction entries without game rosters are separately inventoried; they create no fabricated appearance or zero-minute game.

Publication A means independently verified original historical availability; none established. B assumes final stats/full recaps end-upper+6h and report nominal header+30min. New medical/return narratives and contract adjudication are C only. They do not enter features or prospective eligibility. Same-event linkage describes positive-event knowledge strata only. No searched signal is proof of being symptom-free. Cumulative history is bounded by acquired channels, not a lifetime medical record; a recent report of remote injury history does not date the original symptoms. Historical label-known-at remains blank.

## Results by versioned cohort and timing

{table}

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

Actual new HTTP requests: {cost['actual_new_http_requests']}; statuses {cost['actual_http_status']}; response bytes {cost['new_request_bytes']}. Redundant requests caused by the adapter bug: {cost['redundant_http_requests_from_adapter_bug']}. New executed dated search queries: {cost['actual_new_search_queries']} across {cost['new_search_call_receipts']} saved call receipts; reused executed targeted queries:{cost['reused_executed_target_queries']}. More detailed counts are in `cost_and_quality.json`. The retained-source cache reused {cost['catalog_prior_cache_reused']} catalog entries; duplicate-URL attempts within this new ledger: {cost['intrabatch_duplicate_url_attempts']} . Additional interactive continuity/contract lookups were performed but not fully time-instrumented; no fabricated human/agent review duration is reported.

Recommendation: preregister one fixed collection phase covering the remaining17 development teams over the same indexing dates, rather than start a fitted baseline now. Metadata-only estimate: {nextcost['uncached_core_game_page_book_requests']} uncached core page/book requests, up to {nextcost['additional_daily_dated_queries_upper']} dated daily queries, plus explicit bounded transfer supplements; estimated agent review15–30 hours and independent human adjudication8–16 hours. These are prospective budgets, not measured completed work. No further teams were collected here.

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
'''
    (ROOT/'docs/phase2c_report.md').write_text(doc);(D/'README.md').write_text('# Phase 2C fixed second development batch\n\nCompleted ATL, DAL, NYK, SAC, OKC, MEM under frozen Phase2B rules. No models or holdouts. See [report and commands](../docs/phase2c_report.md), [scope tables](tables/scope_results.csv), [pending human review](human_review_packet.md), [registration](registration/collection_v1.json) and [sampling receipt](registration/commit_receipt.json).\n')
if __name__=='__main__':report()
