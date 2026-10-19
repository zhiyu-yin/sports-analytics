"""Fixed six-team development cohort. Eligibility/features never consume outcome review."""
from collections import defaultdict,Counter
from datetime import date,timedelta
import json,random,time,hashlib
from injury_warning.pilot_io import ROOT,now
from injury_warning.longitudinal import canonical,absence_category
from injury_warning.rules import utc
from phase1c.logic import decision,add_elapsed,eligibility,features
from phase1d.logic import absence_runs,label_events,membership
from phase1d.acquire import schedule
from .acquire import D,manifest,registration
from .prepare import rows,write,TEAM_LABELS
from .surveillance import FOLLOWUP_LABELS

def norm(r):return dict(r,appeared=r['appeared']=='True',roster_observed=r['roster_observed']=='True',minutes=float(r['minutes']) if r['minutes'] else None)
def sequences(pg,timing,spells,ss):
    by=defaultdict(list)
    for r in pg:
        if r['player_id']:by[r['player_id']].append(r)
    output={};coverage={};membership_rows=[]
    for pid,logs in by.items():
        ranges=[r for r in spells if r['player_id']==pid]
        if not ranges:
            for team in sorted({r['team'] for r in logs}):
                rr=[r for r in logs if r['team']==team];first=min(r['game_date'] for r in rr);last=max(r['game_date'] for r in rr);teamfirst=min(g['game_date'] for g in ss if g['team']==team and g['game_date']>='2023-12-04');ranges.append(dict(player_id=pid,team=team,start='2023-12-04' if first==teamfirst else first,end=last,date_basis='observed roster span; no extrapolation beyond last roster',source_id=';'.join(sorted({r['page_source'] for r in rr}))))
        lookup={(r['team'],r['game_id']):r for r in logs};seq=[];missing=[]
        for sp in sorted(ranges,key=lambda r:r['start']):
            membership_rows.append(sp)
            for g in ss:
                if g['team']!=sp['team'] or not sp['start']<=g['game_date']<=sp['end']:continue
                r=lookup.get((g['team'],g['game_id']))
                if not r:
                    missing.append(g['game_id']);r=dict(team=g['team'],player_id=pid,player_name=logs[0]['player_name'],game_id=g['game_id'],game_date=g['game_date'],appeared=False,minutes=None,roster_observed=False,reason='roster_not_observed_in_expected_spell',category='unknown',coverage='membership_gap',page_source='page_'+g['game_id'],reason_source='')
                else:r=dict(r)
                if r['reason']=='Trade Pending':r['category']='transaction'
                if r['game_id'] in timing:r.update({k:timing[r['game_id']][k] for k in ['anchor_lower','anchor_upper','anchor_precision']})
                previous=[v for v in ranges if v['end']<sp['start']]
                if previous and g['game_date']==min(z['game_date'] for z in ss if z['team']==sp['team'] and sp['start']<=z['game_date']<=sp['end']):r['membership_gap_before']=(date.fromisoformat(sp['start'])-date.fromisoformat(max(v['end'] for v in previous))).days>1
                seq.append(r)
        seq.sort(key=lambda r:(r['game_date'],r['game_id']))
        assert len({r['game_id'] for r in seq})==len(seq),('duplicate applicable player-game',pid)
        output[pid]=seq;coverage[pid]=dict(start=min(sp['start'] for sp in ranges),end=max(sp['end'] for sp in ranges),missing=missing,spells=ranges)
    write('membership_spells',membership_rows);return output,coverage

def build_events(seq,manual):
    events=[];members=[];reviews=[]
    for pid,logs in seq.items():
        for e in absence_runs(logs):
            block=[g for g in logs if g['game_id'] in e['game_ids'].split(';')];inj=[g for g in block if g['category']=='injury'];return_row=next((g for g in logs if g['game_id']==e['return_game_id']),{});gap=any(g.get('membership_gap_before') for g in block) or return_row.get('membership_gap_before',False)
            if gap:e['possible_run_upper']=None;e['severity']='unknown'
            e['contract_gap_in_run']=bool(gap);oldid=e['event_id'];e['event_id']='nba2324_'+oldid;e['player_name']=logs[0]['player_name'];e['anchor_team']=next(g['team'] for g in block if g['game_id']==e['anchor_game_id']);selected={v['team'] for v in registration()['selected']};own=[g for g in logs if g['team'] in selected and g['game_date']<=e['anchor_date']];e['sampled_origin_team']=max(own,key=lambda g:g['game_date'])['team'] if own else next((g['team'] for g in logs if g['team'] in selected),e['anchor_team']);e['source_phase']='phase2a_systematic_cohort';e['historical_label_known_at']='';e['clinical_onset_not_estimated']=True
            # Stage B: explicit source-linked adjudication; no name/case-specific positive assignment.
            review=manual.get(pid+'_'+e['anchor_date'])
            if review:
                e.update(continuity_supported=review['common_episode_supported'],continuity_source_ids=review['source_ids'],continuity_locator=review['locator'],continuity_review_note=review['note'],acute_event_game_ids=';'.join(review.get('acute_event_game_ids',[])))
                streak=best=0
                for g in block:
                    if g['category']=='injury' and g['roster_observed'] and g['coverage']=='page_and_book' and g['game_date']<=review['supported_through']:streak+=1;best=max(best,streak)
                    else:streak=0
                e['confirmed_same_episode_games']=best if e['continuity_supported'] else 0
                if e['continuity_supported'] and best>=10:e['severity']='positive'
            if e['severity']=='unknown':
                e['continuity_source_ids']=e.get('continuity_source_ids','');e['continuity_review_note']=e.get('continuity_review_note','Complete sequence reviewed. Unknown/mixed nonappearance or censoring; no explicit common-episode narrative sufficient for >=10 confirmed consecutive games. Same diagnosis alone not accepted.')
            e['censoring']='closed_by_appearance_not_recovery' if e['return_date'] else 'last_applicable_roster_or_regular_season_end';e['last_observed_absence_date']=block[-1]['game_date'];
            if e['severity']=='positive':e['reason']='at_least_10_individually_medical_games_with_reviewed_common_episode_narrative'
            e['candidate_broad_onset_period']='2024-01-01'<=e['anchor_date']<='2024-03-03';e['onset_in_index_game_dates']='2024-01-01'<=e['anchor_date']<='2024-02-18';e['mixed_categories']=';'.join(sorted({g['category'] for g in block}));e['roster_gap_count']=sum(not g['roster_observed'] for g in block)
            events.append(e)
            for n,g in enumerate(block):members.append(dict(event_id=e['event_id'],sequence_number=n+1,player_id=pid,team=g['team'],game_id=g['game_id'],game_date=g['game_date'],appeared=g['appeared'],category=g['category'],reason=g['reason'],roster_observed=g['roster_observed'],coverage=g['coverage'],page_source=g['page_source'],reason_source=g['reason_source'],evidence_role='C_outcome_only'))
            if e['severity']!='negative':reviews.append(dict(event_id=e['event_id'],player_id=pid,player_name=e['player_name'],anchor_date=e['anchor_date'],anchor_team=e['anchor_team'],observed_games=e['observed_games'],severity=e['severity'],common_episode_supported=e['continuity_supported'],mixed_categories=e['mixed_categories'],roster_gap_count=e['roster_gap_count'],first_return=e['return_date'],source_ids=e['source_ids'],continuity_source_ids=e.get('continuity_source_ids',''),review_note=e.get('continuity_review_note',''),reviewer='Codex same agent; source sequence and attribution review, not independent human',evidence_role='C',historical_label_known_at=''))
    write('events',events);write('event_game_evidence',members);write('detailed_event_reviews',reviews);return events

def knowledge(t,pid,observations,signals):
    past=[o for o in observations if o['player_id']==pid and utc(o['B_available_at'])<=utc(t) and utc(o['B_available_at'])>=utc(add_elapsed(t,days=-7)) and o['category']=='injury']
    sig=[s for s in signals if s['player_id']==pid and utc(s['B_available_at'])<=utc(t) and utc(s['B_available_at'])>=utc(add_elapsed(t,days=-28))]
    acute=any(s['kind']=='acute' for s in sig);symptom=bool(past or any(s['kind'] in {'symptom','history'} for s in sig))
    return dict(acute_known_B=acute,symptoms_history_known_B=symptom,signal_ids=';'.join([o['observation_id'] for o in past]+[s['signal_id'] for s in sig]),group_B='acute_already_disclosed' if acute else 'symptom_or_history_known' if symptom else 'no_signal_found_under_searched_process',group_A='knowledge_timing_unresolved',A_verified=False)

def positive_event_knowledge(t,pid,observations,signals,events):
    k=knowledge(t,pid,observations,signals)
    related_ids={gid for e in events for gid in e.get('acute_event_game_ids','').split(';') if gid}
    same=[s for s in signals if s['player_id']==pid and s['kind']=='acute' and s['event_game_id'] in related_ids and utc(s['B_available_at'])<=utc(t)]
    prior_acute=k['acute_known_B'];k['any_prior_acute_disclosure_B']=prior_acute;k['acute_known_B']=bool(same)
    k['symptoms_history_known_B']=bool(k['symptoms_history_known_B'] or (prior_acute and not same))
    k['group_B']='acute_already_disclosed' if same else 'symptom_or_history_known' if k['symptoms_history_known_B'] else 'no_signal_found_under_searched_process'
    k['signal_relation_to_future_run']='same documented acute event' if same else 'prior symptoms or injury history; identity with later trauma not assumed' if k['symptoms_history_known_B'] else 'no signal found in bounded reviewed channels'
    return k

def build():
    started=time.monotonic();reg=registration();sm=manifest();pg=[norm(r) for r in rows('player_games')];timing={r['game_id']:r for r in rows('game_timing')};people={r['player_id']:r for r in rows('players')};selected={r['team'] for r in reg['selected']};ss=schedule();spells=json.loads((D/'membership_review_ranges.json').read_text());seq,cov=sequences(pg,timing,spells,ss)
    manual=json.loads((D/'episode_adjudications.json').read_text()) if (D/'episode_adjudications.json').exists() else {};events=build_events(seq,manual);eby=defaultdict(list)
    for e in events:eby[e['player_id']].append(e)
    rawsignals=json.loads((D/'recap_adjudications.json').read_text()) if (D/'recap_adjudications.json').exists() else [];signals=[]
    for i,s in enumerate(rawsignals):signals.append(dict(s,signal_id='recap_signal_'+str(i),B_available_at=timing[s['source_game_id']]['B_available_at'],source_id='page_'+s['source_game_id'],evidence_category='B_final_recap_end_plus_6h'))
    write('recap_signals_B',signals)
    reports=json.loads((D/'parsed_reports.json').read_text());queries={(q['team'],q['date']):q for q in json.loads((D/'search_ledger.json').read_text()) if q['status']=='fulfilled'};labels=FOLLOWUP_LABELS;observations=[]
    namemap={canonical(p['family_name']+', '+p['first_name']):pid for pid,p in people.items()};inverse={v:k for k,v in labels.items()}
    for rp in reports:
        for o in rp['observations']:
            pid=namemap.get(canonical(o['player_name_raw']))
            if not pid:continue
            observations.append(dict(o,team=inverse[o['team']],player_id=pid,category=absence_category(o['reason']),source_id=rp['source_id'],observation_id=rp['source_id']+'_'+pid+'_'+str(o['target_game_date']),B_available_at=rp['B_available_at'],A_verified_publication_at=''))
    write('status_observations',observations)
    disagreements=[]
    for g in pg:
        if g['appeared'] or not g['player_id']:continue
        oo=[o for o in observations if o['player_id']==g['player_id'] and o['team']==g['team'] and o['target_game_date']==g['game_date'] and o['status']=='Out']
        if not oo:continue
        o=max(oo,key=lambda o:utc(o['B_available_at']))
        if o['category']!=g['category'] and ('injury' in {o['category'],g['category']}):disagreements.append(dict(player_id=g['player_id'],game_id=g['game_id'],game_date=g['game_date'],team=g['team'],report_reason=o['reason'],report_category=o['category'],report_source=o['source_id'],final_reason=g['reason'],final_category=g['category'],final_reason_source=g['reason_source'],review='status-to-final reason disagreement; not silently resolved or used to infer health',evidence_role='C_quality_review_only'))
    write('reason_evidence_disagreements',disagreements)
    # Precompute bounded daily source surveillance; failed/unsubmitted reports are explicit states.
    daily={};dailyrows=[];report_map={r['source_id']:r for r in reports}
    d=date(2024,1,1)
    while d<=date(2024,3,3):
        day=d.isoformat()
        for team in labels:
            rp=report_map.get('report_'+day+'_11AM');section=[s for s in rp.get('sections',[]) if s['team']==labels[team]] if rp else [];states=';'.join(sorted({s['state'] for s in section})) or 'team_not_covered' if rp and rp['retrieval_status']=='obtained' else 'missing_or_denied';expected=[g for g in ss if g['team']==team and g['game_date']==day];complete=all(g['game_id'] in timing and timing[g['game_id']]['recap_present']=='True' and sm.get('book_'+g['game_id'],{}).get('status')=='obtained' for g in expected);searched=(team,day) in queries
            row=dict(team=team,date=day,report_source_id='report_'+day+'_11AM',report_retrieval_status=rp['retrieval_status'] if rp else 'not_probed',report_team_state=states,dated_search_executed=searched,expected_team_games=len(expected),complete_game_records_and_recaps=complete,B_process_covered=bool(rp and searched and complete),A_process_covered=False);daily[(team,day)]=row;dailyrows.append(row)
        d+=timedelta(days=1)
    write('daily_coverage',dailyrows)
    # Feature inputs contain only final game workload and registered availability bounds.
    workloads={}
    for pid,logs in seq.items():workloads[pid]=[dict(game_id=g['game_id'],game_date=g['game_date'],team=g['team'],minutes=g['minutes'],end_upper=timing.get(g['game_id'],{}).get('end_upper'),assumed_available_at=timing.get(g['game_id'],{}).get('B_available_at')) for g in logs if g['minutes'] is not None]
    cohort=[];outcomes=[];features_rows=[];links=[];known=[];seen=set();inventory=[]
    own=[r for r in pg if r['team'] in selected and '2024-01-01'<=r['game_date']<='2024-02-18']
    for team in sorted(selected):
        for pid in sorted({r['player_id'] for r in own if r['team']==team and r['player_id']}):
            rr=[r for r in own if r['team']==team and r['player_id']==pid];inventory.append(dict(team=team,player_id=pid,player_name=people[pid]['player_name'],roster_game_records=len(rr),period_appearances=sum(r['appeared'] for r in rr),first_roster_game=min(r['game_date'] for r in rr),last_roster_game=max(r['game_date'] for r in rr),role='all_roster_inventory; appearance population applied separately'))
    if not any(r['team']=='DET' and r['player_id']=='1627863' for r in inventory):inventory.append(dict(team='DET',player_id='1627863',player_name='Danuel House Jr.',roster_game_records=0,period_appearances=0,first_roster_game='',last_roster_game='',role='transaction_only_contract_inventory; no game roster or appearance inferred',membership_date='2024-02-08',source_id='p2_trade_tracker'))
    write('roster_inventory',inventory)
    for r in own:
        if not r['player_id']:continue
        pid=r['player_id'];team=r['team'];gid=r['game_id'];tm=timing[gid]
        for lag in (0,1):
            rid=gid+'_'+pid+'_lag'+str(lag)
            assert rid not in seen,('duplicate decision',rid);seen.add(rid);t=decision(r['game_date'],lag);end=add_elapsed(t,days=14);day=utc(t).date().isoformat();available=[rp for rp in reports if rp.get('B_available_at') and utc(rp['B_available_at'])<=utc(t)]
            baseline=[rp for rp in available if any(s['team']==labels[team] and s['target_game_date']==r['game_date'] and s['state']=='complete' for s in rp['sections'])];dayreports=[rp for rp in available if rp['source_id'].startswith('report_'+day+'_') and rp['retrieval_status']=='obtained'];ready=bool(tm['B_available_at'] and utc(tm['B_available_at'])<=utc(t));covered=bool(baseline and dayreports and ready and tm['recap_present']=='True' and (team,day) in queries)
            dis=[];dis_sources=[]
            for s in signals:
                if s['player_id']==pid and s['kind']=='acute' and s['event_game_id']==gid and utc(s['B_available_at'])<=utc(t):dis.append('new_injury_in_index_game');dis_sources.append(s['signal_id'])
            latest={}
            for o in sorted(observations,key=lambda x:(utc(x['B_available_at']),x['source_id'])):
                if o['player_id']==pid and utc(o['B_available_at'])<=utc(t) and o['target_game_date'] and o['target_game_date']>=day:latest[o['target_game_date']]=o
            for o in latest.values():
                if o['status']=='Out' and o['category']=='injury':dis.append('documented_ongoing_injury_out');dis_sources.append(o['observation_id'])
                elif o['status']=='Out' and (o['category'] in {'suspension','personal'} or o['reason'] in {'Trade Pending','Not With Team'}):dis.append('documented_noninjury_unavailability');dis_sources.append(o['observation_id'])
            state,reason=eligibility(appeared=r['appeared'],member=r['roster_observed'],time_ordered=bool(tm['end_upper'] and utc(tm['end_upper'])<utc(t)),covered=covered,explicit_disqualifiers=sorted(set(dis)))
            kn=knowledge(t,pid,observations,signals)
            cr=dict(row_id=rid,team=team,player_id=pid,player_name=r['player_name'],index_game_id=gid,index_game_date=r['game_date'],extra_lag_days=lag,decision_at=t,window_end=end,index_minutes=r['minutes'],appeared=r['appeared'],B_state=state,B_reason=reason,B_exclusion_source_ids=';'.join(dis_sources),baseline_report_ids=';'.join(x['source_id'] for x in baseline),decision_report_ids=';'.join(x['source_id'] for x in dayreports),game_end_upper=tm['end_upper'],stats_recap_B_available_at=tm['B_available_at'],A_state='unknown' if r['appeared'] else 'not_in_population',prospective_uses_retrospective_outcome_evidence=False,**kn);cohort.append(cr)
            if state!='included':continue
            cp=cov[pid];windowdays=[];dd=utc(t).date()
            while dd<=utc(end).date():windowdays.append(dd.isoformat());dd+=timedelta(days=1)
            # Only the actual applicable-team sequence may supply negative surveillance.
            relevant=[g for g in seq[pid] if day<=g['game_date']<=utc(end).date().isoformat()];teams_in_window={g['team'] for g in relevant}|{team};source_ok=all(bool(active:={sp['team'] for sp in cp['spells'] if sp['start']<=ds<=sp['end']}) and all(daily.get((tt,ds),{}).get('B_process_covered',False) for tt in active) for ds in windowdays)
            # Destination channels were not registered as whole-team news/report panels;
            # require complete actual-game pages/books and preserve coverage uncertainty
            # where a transfer occurs before the end of the onset horizon.
            transfer_window=any(tt not in selected for tt in teams_in_window);surveillance=bool(source_ok and cp['end']>=utc(end).date().isoformat() and all(g['roster_observed'] and g['coverage']=='page_and_book' for g in relevant))
            after=[g for g in seq[pid] if g['game_date']>utc(end).date().isoformat()];followup=len(after)>=10 and all(g['roster_observed'] and g['coverage']=='page_and_book' for g in after[:10])
            outcome,ids=label_events(t,eby[pid],'run',coverage=surveillance,followup=followup)
            potential_ids=list(ids)
            if outcome=='positive':ids=[e['event_id'] for e in eby[pid] if e['severity']=='positive' and e['continuity_supported'] and membership(t,e['run_lower'],e['run_upper']) is True]
            if outcome=='positive':kn=positive_event_knowledge(t,pid,observations,signals,[e for e in eby[pid] if e['event_id'] in ids])
            for e in eby[pid]:
                relation=membership(t,e['run_lower'],e['run_upper']);links.append(dict(row_id=rid,event_id=e['event_id'],window_membership=relation,severity=e['severity'],anchor_lower=e['run_lower'],anchor_upper=e['run_upper'],common_episode_supported=e['continuity_supported']))
            outcomes.append(dict(row_id=rid,team=team,player_id=pid,extra_lag_days=lag,decision_at=t,window_end=end,absence_run_onset_ge10=outcome,event_ids=';'.join(ids),potential_event_ids=';'.join(potential_ids),onset_surveillance_B=surveillance,severity_followup_B=followup,cross_team_onset_window=transfer_window,transfer_onset_surveillance_gap=bool(transfer_window and not source_ok),applicable_games_after_horizon=len(after),unknown_reason='unresolved run/attribution, roster/source gap or insufficient applicable-team followup' if outcome=='unknown' else '',historical_label_known_at='',retrospective_ascertainment_at=json.loads((D/'review_metadata.json').read_text())['retrospective_reviewed_at'],historical_training_cutoff_usable=False,evidence_category='B_surveillance; C_outcome_adjudication',**kn))
            if outcome=='positive':known.append(dict(row_id=rid,team=team,player_id=pid,event_ids=';'.join(ids),extra_lag_days=lag,decision_at=t,**kn))
            start28=utc(add_elapsed(t,days=-28)).date().isoformat();prior=[g for g in seq[pid] if start28<=g['game_date']<=day and (g['game_id'] not in timing or not timing[g['game_id']].get('scheduled_start_utc') or utc(timing[g['game_id']]['scheduled_start_utc'])<=utc(t))];history=bool(cp['start']<=start28 and all(g['minutes'] is not None and g['game_id'] in timing and timing[g['game_id']]['end_upper'] for g in prior))
            # Contract/roster gaps between observed spells cannot be zero-filled.
            relevant_sp=[sp for sp in cp['spells'] if sp['start']<=day and sp['end']>=start28];relevant_sp.sort(key=lambda s:s['start'])
            for a,b in zip(relevant_sp,relevant_sp[1:]):
                if (date.fromisoformat(b['start'])-date.fromisoformat(a['end'])).days>1:history=False
            f=features(workloads[pid],t,history_complete=history,baseline_complete=history);features_rows.append(dict(row_id=rid,team=team,player_id=pid,extra_lag_days=lag,decision_at=t,history_complete=history,missing_history_reason='' if history else 'unobserved prior NBA membership/game or contract gap; no zero fill',input_teams=';'.join(sorted({g['team'] for g in prior if g['game_id'] in f['input_game_ids'].split(';')})),index_back_to_back=any((date.fromisoformat(r['game_date'])-date.fromisoformat(g['game_date'])).days==1 for g in seq[pid] if g['game_date']<r['game_date']),feature_evidence_category='B_final_stats_end_plus_6h',**f))
    write('cohort_all_roster_candidates',cohort);write('row_outcomes',outcomes);write('features_B',features_rows);write('row_event_links',links);write('positive_knowledge_review',known,fields=list(known[0]) if known else ['row_id','team','player_id','event_ids','extra_lag_days','group_B']);write('features_A',[],fields=['row_id','A_verified_publication_at'])
    event_eligible=[]
    for e in events:
        eligible=[o for o in outcomes if o['absence_run_onset_ge10']=='positive' and e['event_id'] in o['event_ids'].split(';')]
        for lag in (0,1):event_eligible.append(dict(event_id=e['event_id'],player_id=e['player_id'],anchor_team=e['anchor_team'],sampled_origin_team=e['sampled_origin_team'],anchor_date=e['anchor_date'],extra_lag_days=lag,severity=e['severity'],broad_onset_period=e['candidate_broad_onset_period'],onset_in_index_dates=e['onset_in_index_game_dates'],eligible_positive_rows=sum(o['extra_lag_days']==lag for o in eligible),has_eligible_preceding_prediction=any(o['extra_lag_days']==lag for o in eligible),event_known_groups_B=';'.join(sorted({o['group_B'] for o in eligible if o['extra_lag_days']==lag}))))
    write('event_prediction_coverage',event_eligible)
    summary=[]
    for lag in (0,1):
        for team in sorted(selected):
            cr=[r for r in cohort if r['team']==team and r['extra_lag_days']==lag];oo=[r for r in outcomes if r['team']==team and r['extra_lag_days']==lag];ff=[r for r in features_rows if r['team']==team and r['extra_lag_days']==lag];ev=[r for r in event_eligible if r['sampled_origin_team']==team and r['extra_lag_days']==lag and r['severity']=='positive' and r['broad_onset_period']]
            summary.append(dict(scope='sampled_six',team=team,extra_lag_days=lag,games=len({r['index_game_id'] for r in cr}),roster_players=len({r['player_id'] for r in inventory if r['team']==team}),candidate_appearances=sum(r['appeared'] for r in cr),included=sum(r['B_state']=='included' for r in cr),excluded=sum(r['B_state']=='excluded' for r in cr),eligibility_unknown=sum(r['B_state']=='unknown' for r in cr),positive=sum(r['absence_run_onset_ge10']=='positive' for r in oo),negative=sum(r['absence_run_onset_ge10']=='negative' for r in oo),outcome_unknown=sum(r['absence_run_onset_ge10']=='unknown' for r in oo),qualifying_events_broad_onset_period=len(ev),affected_event_players=len({r['player_id'] for r in ev}),events_with_eligible_prediction=sum(r['has_eligible_preceding_prediction'] for r in ev),missing_history=sum(not r['history_complete'] for r in ff),A_verified_rows=0,B_feature_rows=len(ff),acute_known_positive_rows=sum(r['absence_run_onset_ge10']=='positive' and r['group_B']=='acute_already_disclosed' for r in oo),symptom_known_positive_rows=sum(r['absence_run_onset_ge10']=='positive' and r['group_B']=='symptom_or_history_known' for r in oo),no_signal_positive_rows=sum(r['absence_run_onset_ge10']=='positive' and r['group_B']=='no_signal_found_under_searched_process' for r in oo),A_positive_knowledge_unresolved=sum(r['absence_run_onset_ge10']=='positive' for r in oo),transfer_surveillance_gaps=sum(r['transfer_onset_surveillance_gap'] for r in oo)))
    write('team_results',summary)
    # Reproducible review sample drawn only after the fixed full batch, not used to select teams.
    negative=[]
    rng=random.Random(20240218)
    for lag in (0,1):
        for team in sorted(selected):
            pool=sorted([o for o in outcomes if o['team']==team and o['extra_lag_days']==lag and o['absence_run_onset_ge10']=='negative'],key=lambda r:r['row_id'])
            for o in rng.sample(pool,min(5,len(pool))):
                ev=[e for e in eby[o['player_id']] if membership(o['decision_at'],e['run_lower'],e['run_upper']) is not False];games=[g for g in seq[o['player_id']] if utc(o['decision_at']).date().isoformat()<=g['game_date']<=utc(o['window_end']).date().isoformat()];negative.append(dict(row_id=o['row_id'],team=team,player_id=o['player_id'],extra_lag_days=lag,decision_at=o['decision_at'],window_end=o['window_end'],event_ids=';'.join(e['event_id'] for e in ev),event_severities=';'.join(e['severity'] for e in ev),possible_upper_bounds=';'.join(str(e['possible_run_upper']) for e in ev),window_game_ids=';'.join(g['game_id'] for g in games),window_source_ids=';'.join(g['page_source']+';'+g['reason_source'] for g in games),source_sequence_check=all(g['coverage']=='page_and_book' and g['roster_observed'] for g in games),review='complete applicable sequence; all intersecting candidate severities below 10, searched-source surveillance and followup verified',reviewer='Codex same agent; algorithmic trace plus source review, not independent human',seed=20240218))
    write('negative_sample_review',negative)
    (D/'build_summary.json').write_text(json.dumps(dict(cohort_roster_decision_rows=len(cohort),outcome_rows=len(outcomes),events=len(events),detailed_reviews=len([e for e in events if e['severity']!='negative']),negative_review_rows=len(negative),elapsed_seconds=round(time.monotonic()-started,2)),indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':build()
