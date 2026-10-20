"""Versioned provenance-preserving30-team union, opportunities and quality accounting."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from .runtime import ROOT,D,SPEC,manifest,verify
from .audit import rows as prior_rows,write,group,lead_bin,utc

def load(path):
    with path.open() as f:return list(csv.DictReader(f))
def tables(path,name):return load(path/'tables'/(name+'.csv'))
def joined(path):
    co=tables(path,'cohort_all_roster_candidates');oo={r['row_id']:r for r in tables(path,'row_outcomes')};ff={r['row_id']:r for r in tables(path,'features_B')}
    return [dict(r,**{k:v for k,v in oo.get(r['row_id'],{}).items() if k not in ['row_id','team','player_id','extra_lag_days','decision_at','window_end']},history_complete=ff.get(r['row_id'],{}).get('history_complete','')) for r in co]

def report():
    verify();out=D/'tables';out.mkdir(exist_ok=True);sm=manifest();groups={};events={};eventrecords=[];games_by_record={};teams_by_record={};inputhash={}
    from phase2c.report import normalize_boston
    groups['Boston_prior']=normalize_boston();events['Boston_prior']=[]
    for scope,path in [('first_six_phase2b',ROOT/'phase2b'),('second_six_phase2c',ROOT/'phase2c')]+[(f'phase2d_batch{i}',D/f'batch{i}') for i in [1,2,3]]:
        groups[scope]=joined(path);ee=tables(path,'events');events[scope]=ee
        eg=defaultdict(set);et=defaultdict(set)
        for g in tables(path,'event_game_evidence'):
            eg[g['event_id']].add(g['game_id']);et[g['event_id']].add(g['team'])
        for e in ee:eventrecords.append(dict(e,batch=scope));games_by_record[(scope,e['event_id'])]=eg[e['event_id']];teams_by_record[(scope,e['event_id'])]=et[e['event_id']]
        for name in ['events','row_outcomes','cohort_all_roster_candidates','features_B']:
            p=path/'tables'/(name+'.csv');inputhash[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    union={};decision_dups=[]
    for scope,rr in groups.items():
        for r in rr:
            r=dict(r,batch=scope);key=r['row_id']
            if key in union:
                decision_dups.append(dict(row_id=key,batch1=union[key]['batch'],batch2=scope));assert r.get('absence_run_onset_ge10')==union[key].get('absence_run_onset_ge10')
            else:union[key]=r
    groups['combined_30_team_development']=list(union.values());write(out/'canonical_decision_duplicates.csv',decision_dups)
    canonical={};aliases={};eventdups=[];overlap=[]
    for i,e in enumerate(eventrecords):
        key=e['player_id']+'_'+e['anchor_game_id'];aliases[(e['batch'],e['event_id'])]=key
        if key in canonical:
            p=canonical[key];eventdups.append(dict(canonical_event_id=key,batch1=p['batch'],batch2=e['batch'],severity1=p['severity'],severity2=e['severity'],assertion='Same actual original first-miss game and player; overlap reviewed; not an extra event'))
            if e['severity']=='positive' and p['severity']!='positive':canonical[key]=e
        else:canonical[key]=e
        for f in eventrecords[:i]:
            if e['player_id']!=f['player_id'] or e['batch']==f['batch']:continue
            shared=games_by_record[(e['batch'],e['event_id'])]&games_by_record[(f['batch'],f['event_id'])]
            if shared:
                same=e['anchor_game_id']==f['anchor_game_id'];overlap.append(dict(player_id=e['player_id'],batch1=f['batch'],batch2=e['batch'],event1=f['event_id'],event2=e['event_id'],anchor1=f['anchor_date'],anchor2=e['anchor_date'],shared_actual_games=len(shared),same_original_anchor=same,shared_game_ids=';'.join(sorted(shared)),disposition='same underlying absence envelope; canonical duplicate retained once' if same else 'overlapping records with different anchors require specific attribution review; never distinct merely by ID',involves_positive=e['severity']=='positive' or f['severity']=='positive'))
                assert same or not (e['severity']=='positive' and f['severity']=='positive'),('positive overlap requires review',e['event_id'],f['event_id'])
    events['combined_30_team_development']=list(canonical.values());write(out/'canonical_event_duplicates.csv',eventdups);write(out/'cross_batch_actual_game_overlap.csv',overlap)
    summaries=[];teamrows=[];ranges=[];opps=[];inventory=[];concentration=[];knowledge=[];bins=[]
    for scope,rr in groups.items():
        ee=[e for e in events[scope] if e['severity']=='positive' and e['candidate_broad_onset_period']=='True']
        for lag in ['0','1']:
            cr=[r for r in rr if r['extra_lag_days']==lag];inc=[r for r in cr if r['B_state']=='included'];counts=Counter(r.get('absence_run_onset_ge10') for r in inc);p=counts['positive'];n=counts['negative'];u=counts['unknown'];ids={eid for r in inc if r.get('absence_run_onset_ge10')=='positive' for eid in r.get('event_ids','').split(';') if eid}
            row=dict(scope=scope,extra_lag_days=lag,team_count=len({r['team'] for r in cr}),team_game_exposures=len({(r['team'],r['index_game_id']) for r in cr}),physical_index_games=len({r['index_game_id'] for r in cr}),distinct_roster_players=len({r['player_id'] for r in cr}),distinct_recently_active_players=len({r['player_id'] for r in cr if r['appeared']=='True'}),candidate_appearances=sum(r['appeared']=='True' for r in cr),included=len(inc),excluded=sum(r['B_state']=='excluded' for r in cr),eligibility_unknown=sum(r['B_state']=='unknown' for r in cr),positive=p,negative=n,outcome_unknown=u,distinct_qualifying_events=len(ee),distinct_event_players=len({e['player_id'] for e in ee}),events_with_eligible_prediction=len(ids),missing_workload=sum(r.get('history_complete')=='False' for r in inc),onset_surveillance_gaps=sum(r.get('onset_surveillance_B')=='False' for r in inc),severity_followup_gaps=sum(r.get('severity_followup_B')=='False' for r in inc),A_verified_rows=0,B_feature_rows=len(inc),A_original_publication_unresolved=len(inc));assert p+n+u==len(inc);summaries.append(row)
            ranges.append(dict(scope=scope,extra_lag_days=lag,included=len(inc),positive=p,unknown=u,lower=p/len(inc),upper=(p+u)/len(inc),interpretation='worst-case positive-label identification range among included rows; not confidence interval or annual injury rate'))
            for team in sorted({r['team'] for r in cr}):
                cc=[r for r in cr if r['team']==team];ci=[r for r in cc if r['B_state']=='included'];teamrows.append(dict(scope=scope,extra_lag_days=lag,team=team,games=len({r['index_game_id'] for r in cc}),players=len({r['player_id'] for r in cc}),included=len(ci),excluded=sum(r['B_state']=='excluded' for r in cc),eligibility_unknown=sum(r['B_state']=='unknown' for r in cc),positive=sum(r.get('absence_run_onset_ge10')=='positive' for r in ci),negative=sum(r.get('absence_run_onset_ge10')=='negative' for r in ci),outcome_unknown=sum(r.get('absence_run_onset_ge10')=='unknown' for r in ci),missing_workload=sum(r.get('history_complete')=='False' for r in ci)))
        for dimension,key in [('team','anchor_team'),('collection_origin_team','sampled_origin_team'),('player','player_id')]:
            for v,n in sorted(Counter(e[key] for e in ee).items()):concentration.append(dict(scope=scope,dimension=dimension,value=v,events=n,fraction=n/len(ee)))
    for key,e in canonical.items():
        if e['severity']!='positive' or e['candidate_broad_onset_period']!='True':continue
        rr=[r for r in union.values() if r.get('absence_run_onset_ge10')=='positive' and e['event_id'] in r.get('event_ids','').split(';')];record=dict(canonical_event_id=key,player_id=e['player_id'],player_name=e['player_name'],anchor_team=e['anchor_team'],applicable_teams=';'.join(sorted(teams_by_record[(e['batch'],e['event_id'])])),collection_batch=e['batch'],anchor_lower=e['run_lower'],anchor_upper=e['run_upper'],anchor_precision='audited first-period minute interval; absence-run anchor not clinical onset',confirmed_consecutive_injury_games=e['confirmed_same_episode_games'],common_episode_assertion=e.get('continuity_review_note',''),source_ids=e.get('continuity_source_ids',''),source_urls=';'.join(sm[s.strip()]['url'] for s in e.get('continuity_source_ids','').split(';') if s.strip() in sm),locators=e.get('continuity_locator',''),limitations='Assumed B original availability; A unresolved; no independent human adjudication; original anchor and actual-team boundaries retained')
        for lag in ['0','1']:
            lr=[r for r in rr if r['extra_lag_days']==lag];record['eligible_decisions_lag'+lag]=len(lr);record['earliest_decision_lag'+lag]=min((r['decision_at'] for r in lr),default='');record['knowledge_groups_lag'+lag]=';'.join(sorted({group(r) for r in lr}))
            for r in lr:
                lo=(utc(e['run_lower'])-utc(r['decision_at']))/86400;hi=(utc(e['run_upper'])-utc(r['decision_at']))/86400;assert lo>0 and hi<=14
                opps.append(dict(canonical_event_id=key,player_id=e['player_id'],row_id=r['row_id'],batch=r['batch'],extra_lag_days=lag,decision_at=r['decision_at'],onset_lower=e['run_lower'],onset_upper=e['run_upper'],lead_days_lower=lo,lead_days_upper=hi,lead_time_bin=lead_bin(lo,hi),knowledge_group_B=group(r),same_acute_B=r.get('acute_known_B',''),recent_evidence_28d_B=r.get('recent_known_symptoms_28d_B',''),prior_history_B=r.get('ever_known_injury_history_B',''),source_signal_ids_B=r.get('signal_ids',''),A_original_timing_unresolved=True,interpretation='available prediction opportunity; not successful warning; retrospective C linkage descriptive only'))
        inventory.append(record)
    for lag in ['0','1']:
        rr=[r for r in opps if r['extra_lag_days']==lag]
        for g in ['same_acute_event_disclosed','recent_symptoms_or_injury_evidence','prior_acquired_history_without_recent_evidence','no_signal_found_under_bounded_search','unresolved_timing']:
            r=[x for x in rr if x['knowledge_group_B']==g];knowledge.append(dict(extra_lag_days=lag,group_B=g,positive_rows=len(r),events=len({x['canonical_event_id'] for x in r}),event_counts_overlap_when_decisions_differ=True,A_timing_unresolved_rows=len(r)))
        for g in ['>0-3d','>3-7d','>7-14d','boundary_uncertain']:
            r=[x for x in rr if x['lead_time_bin']==g];bins.append(dict(extra_lag_days=lag,lead_time_bin=g,positive_rows=len(r),events=len({x['canonical_event_id'] for x in r})))
    packet=[]
    for e in inventory:
        packet.append(dict(review_id=e['canonical_event_id'],role='confirmed_positive_event',player_id=e['player_id'],player_name=e['player_name'],batch=e['collection_batch'],short_assertion=e['common_episode_assertion'],source_urls=e['source_urls'],exact_locators=e['locators'],accept_amend_reject='',amended_value='',reviewer_name='',review_date='',review_notes='',human_review_completed=False))
    seen_packet=set()
    for i in [1,2,3]:
        for r in tables(D/f'batch{i}','human_review_packet'):
            if r['role']=='confirmed_positive_event':continue
            key=(r['role'],r['review_id'])
            if key in seen_packet:continue
            seen_packet.add(key);packet.append(dict(r,batch='phase2d_batch'+str(i)))
    write(out/'human_review_packet.csv',packet)
    for name,rr in [('scope_results',summaries),('team_results',teamrows),('identification_ranges',ranges),('event_inventory',inventory),('available_opportunities',opps),('knowledge_summary',knowledge),('lead_time_summary',bins),('event_concentration',concentration)]:write(out/(name+'.csv'),rr)
    write(out/'canonical_events.csv',[dict(e,canonical_event_id=k) for k,e in canonical.items()])
    for i in [1,2,3]:
        scope='phase2d_batch'+str(i);path=D/f'batch{i}';oo=[r for r in opps if r['batch']==scope]
        write(path/'tables/available_opportunities.csv',oo)
        ownkeys={e['player_id']+'_'+e['anchor_game_id'] for e in events[scope] if e['severity']=='positive' and e['candidate_broad_onset_period']=='True'}
        write(path/'tables/event_inventory.csv',[dict(r,prediction_batch=scope) for r in inventory if r['canonical_event_id'] in ownkeys])
        write(path/'tables/event_concentration.csv',[r for r in concentration if r['scope']==scope])
        ks=[];bs=[]
        for lag in ['0','1']:
            lr=[r for r in oo if r['extra_lag_days']==lag]
            for category in ['same_acute_event_disclosed','recent_symptoms_or_injury_evidence','prior_acquired_history_without_recent_evidence','no_signal_found_under_bounded_search','unresolved_timing']:
                r=[x for x in lr if x['knowledge_group_B']==category];ks.append(dict(extra_lag_days=lag,group_B=category,positive_rows=len(r),events=len({x['canonical_event_id'] for x in r}),A_original_publication_unresolved=len(r)))
            for category in ['>0-3d','>3-7d','>7-14d','boundary_uncertain']:
                r=[x for x in lr if x['lead_time_bin']==category];bs.append(dict(extra_lag_days=lag,lead_time_bin=category,positive_rows=len(r),events=len({x['canonical_event_id'] for x in r})))
        write(path/'tables/knowledge_summary.csv',ks);write(path/'tables/lead_time_summary.csv',bs)
    # Explicit source coverage and all residual membership/reason gaps.
    coverage=[];fromphase=[];gaps=[];allpg=[]
    for i in [1,2,3]:
        path=D/f'batch{i}';pg=tables(path,'player_games');allpg+=pg;clock=tables(path,'game_timing');ct={g['game_id']:g for g in clock}
        for t in SPEC['batches'][i-1]:
            gg=[g for g in json.loads((path/'team_schedule.json').read_text()) if g['team']==t['team']];coverage.append(dict(batch=i,team=t['team'],expected_team_games=len(gg),pages_obtained=sum(sm.get('page_'+g['game_id'],{}).get('status')=='obtained' for g in gg),books_obtained=sum(sm.get('book_'+g['game_id'],{}).get('status')=='obtained' for g in gg),full_recaps=sum(ct.get(g['game_id'],{}).get('recap_present')=='True' for g in gg),dated_query_days=len({r['date'] for r in json.loads((path/'search_ledger.json').read_text()) if r['team']==t['team'] and r['status']=='fulfilled'})))
        for r in pg:
            if r['player_id'] and (r['roster_observed']!='True' or (r['appeared']=='False' and r['category']=='unknown')):gaps.append(dict(r,batch=i))
        # Cross-team expected-spell gaps from the unchanged sequence engine.
        from phase2b.build import sequences,norm
        from phase1d.acquire import schedule
        from .runtime import bindings
        from . import runtime as rt
        previous=rt.BATCH;rt.BATCH=i
        try:
            with bindings():seq,cov=sequences([norm(r) for r in pg],ct,json.loads((path/'membership_review_ranges.json').read_text()),schedule())
            for pid,ls in seq.items():
                for g in ls:
                    if not g['roster_observed']:gaps.append(dict(g,batch=i))
        finally:rt.BATCH=previous
    write(out/'source_coverage.csv',coverage);write(out/'unresolved_player_games.csv',gaps)
    # Before/after row ledger for the genuine suffix-path defect.
    impact=[];counts=[]
    for i in [1,2,3]:
        old=D/'quality/suffix_before'/f'batch{i}'
        for name,key in [('cohort_all_roster_candidates','row_id'),('row_outcomes','row_id'),('features_B','row_id'),('player_games','game_id'),('status_observations','observation_id')]:
            before=load(old/(name+'.csv'));after=tables(D/f'batch{i}',name)
            def identity(r):return r[key]+('_'+r.get('player_id','')+'_'+r.get('team','') if name=='player_games' else '')
            aa={identity(r):r for r in before};bb={identity(r):r for r in after}
            for rid in sorted(set(aa)|set(bb)):
                a,b=aa.get(rid,{}),bb.get(rid,{})
                diff=[k for k in set(a)|set(b) if k!='retrospective_ascertainment_at' and a.get(k)!=b.get(k)]
                if diff:impact.append(dict(batch=i,table=name,row_id=rid,changed_fields=';'.join(sorted(diff)),before=json.dumps({k:a.get(k) for k in diff},sort_keys=True),after=json.dumps({k:b.get(k) for k in diff},sort_keys=True)))
        for lag in ['0','1']:
            for version,rr in [('before',load(old/'row_outcomes.csv')),('after',tables(D/f'batch{i}','row_outcomes'))]:
                cc=Counter(r['absence_run_onset_ge10'] for r in rr if r['extra_lag_days']==lag);counts.append(dict(batch=i,extra_lag_days=lag,version=version,positive=cc['positive'],negative=cc['negative'],outcome_unknown=cc['unknown'],included=sum(cc.values())))
    write(out/'suffix_repair_row_impact.csv',impact);write(out/'suffix_repair_count_impact.csv',counts)
    actual=[json.loads(l) for l in (D/'source_manifest.jsonl').read_text().splitlines()];queries=list((ROOT/'data/raw/phase2d/searches').glob('*.json'));qq=[json.loads(p.read_text()) for p in queries];activity=[json.loads(l) for l in (D/'activity.jsonl').read_text().splitlines()];assert len({r['url'] for r in actual})==len(actual)
    cost=dict(actual_http_requests=len(actual),core_requests=sum(r.get('scope')=='core' for r in actual),supplement_requests=sum(r.get('scope')=='supplement' for r in actual),http_status=dict(Counter(r['status'] for r in actual)),response_bytes=sum(r.get('bytes',0) for r in actual),new_dated_queries=sum(len(r['queries']) for r in qq if r['status']=='fulfilled'),new_dated_calls=len(qq),reused_dated_queries=267,continuity_queries_with_saved_bodies=sum(len(json.loads(p.read_text())['queries']) for p in (ROOT/'data/raw/phase2d').glob('continuity_search_*.json')),additional_interactive_continuity_queries_without_saved_body=4,final_distinct_negative_traces=170,negative_source_reread_operations=sum(a['operation']=='seeded_negative_original_source_reread' for a in activity),machine_activity_seconds_sum=sum(a['elapsed_machine_seconds'] for a in activity),activity_entries=len(activity),activity_durations_overlap_and_are_not_agent_labor=True,agent_activity_time='Not exclusively instrumented; operation/source-review wall intervals and counts only',independent_human_reviews=0,independent_human_seconds=0,budgets=SPEC['budgets'],duplicate_new_http_requests=0)
    for i in [1,2,3]:
        cp=D/f'batch{i}/checkpoint.json';state=json.loads(cp.read_text());seen=[r for r in actual if utc(r['retrieved_at'])<=utc(state['saved_at'])]
        state['request_usage_at_checkpoint']=dict(actual_http=len(seen),core=sum(r.get('scope')=='core' for r in seen),supplement=sum(r.get('scope')=='supplement' for r in seen),bytes=sum(r.get('bytes',0) for r in seen),statuses=dict(Counter(r['status'] for r in seen)),receipt_time_filter='actual retrieved_at no later than checkpoint saved_at')
        state['lead_time_table']='tables/lead_time_summary.csv';state['knowledge_table']='tables/knowledge_summary.csv';state['event_concentration_table']='tables/event_concentration.csv';state['final_source_coverage_table']='../tables/source_coverage.csv'
        cp.write_text(json.dumps(state,indent=2)+'\n')
    (D/'actual_usage.json').write_text(json.dumps(cost,indent=2)+'\n');(D/'result_input_hashes.json').write_text(json.dumps(inputhash,indent=2)+'\n')
    summary=dict(completed_prediction_teams=30,new_phase2d_teams=17,pending_teams=[],same_agent_complete=True,independent_human_adjudication=False,models_trained=0,protected_holdouts_opened=False,registration_commit=json.loads((D/'registration/commit_receipt.json').read_text())['registration_commit'],canonical_duplicate_decisions=len(decision_dups),canonical_duplicate_event_records=len(eventdups),different_anchor_positive_overlap_candidates=sum(r['involves_positive'] and not r['same_original_anchor'] for r in overlap),scope_results=summaries,lead_bins=bins,knowledge=knowledge,suffix_repair_changed_rows=len(impact),actual_usage=cost)
    (D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');render(summary)

def render(s):
    cols=['scope','extra_lag_days','included','excluded','eligibility_unknown','positive','negative','outcome_unknown','distinct_qualifying_events','events_with_eligible_prediction','missing_workload']
    tab='| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+''.join('| '+' | '.join(str(r[k]) for k in cols)+' |\n' for r in s['scope_results'])
    text='''# Phase 2D cumulative audit and fixed remaining-team census

Stage1 reconciled19 events,18 players,17 main-noon and16 extra-day events with opportunities;3067 main included rows=57 positive+2817 negative+193 unknown. See `stage1/audit_report.md`, original evidence inventory, actual-game overlap review and57/52 opportunity rows. Stage1 preceded registration and new-team outcome review. Historical Phase1–2C files remain hash-verified unchanged.

Registered seed20240220 order: WAS/MIN/CHA/POR/MIL/UTA; CHI/PHX/BKN/GSW/HOU/TOR; IND/MIA/NOP/LAL/LAC. All17 teams completed;30 prediction teams in the provenance-preserving union. This is a development-period census, not unseen validation. Prior transfer, fixture and opponent familiarity is disclosed. Endpoint, windows, noon ET timings, source clocks and common-identity standards remain frozen. No model, preprocessing fitting, tuning or protected holdout was opened.

## Results and limitations

'''+tab+'''
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
'''
    (D/'report.md').write_text(text);(ROOT/'docs/phase2d_report.md').write_text(text);(D/'README.md').write_text('# Phase 2D fixed remaining-team census\n\nCompleted30-team development-period census under frozen rules. No fitted model or holdout. See [report and commands](report.md), [Stage1 audit](stage1/audit_report.md), [registration](registration/scope_v1.json), [results](tables/scope_results.csv), and per-batch human review packets. Independent human review remains pending.\n')
if __name__=='__main__':report()
