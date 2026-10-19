"""Execute the registered observable-cohort amendment; never modify Phase 1B outputs."""
from collections import Counter,defaultdict
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import csv,json,hashlib,re
from injury_warning.pilot_io import ROOT,now
from injury_warning.longitudinal import resolve_name,absence_category,canonical
from injury_warning.rules import utc
from .sources import CROOT,manifest,read
from .logic import decision,ordering,add_elapsed,eligibility,row_outcome,features
from .episode_review import review,rows

OUT=CROOT/'tables'


def write(name,records,fields=None):
    records=list(records);OUT.mkdir(exist_ok=True)
    fields=fields or list(dict.fromkeys(k for r in records for k in r))
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)


def build():
    p=CROOT/'registration/amendment_v1.json'
    if hashlib.sha256(p.read_bytes()).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Amendment changed')
    people=rows('players.csv');pg=rows('player_games.csv');old=rows('prediction_timestamps.csv');schedule=rows('team_schedule.csv');times={r['game_id']:r for r in rows('game_timing.csv')}
    byplayer=defaultdict(list)
    for r in pg:byplayer[r['player_id']].append(r)
    pgmap={(r['game_id'],r['player_id']):r for r in pg}
    sm=manifest();reports=json.loads((CROOT/'parsed_reports.json').read_text());searches={s['date']:s for s in json.loads((CROOT/'search_ledger.json').read_text())};recaps={r['game_id']:r for r in json.loads((CROOT/'recap_inventory.json').read_text())}
    episodes,members,events=review();write('episode_candidates',episodes);write('episode_game_evidence',members)
    (CROOT/'explicit_in_game_events.json').write_text(json.dumps(events,indent=2)+'\n')
    # Link all 28 original leads to reviewed candidate envelopes, preserving their old IDs.
    mapping=[]
    for lead in rows('injury_episodes.csv'):
        matches=[m for m in members if m['game_id'] in lead['episode_id'] and m['player_id']==lead['player_id']]
        if len(matches)!=1:raise ValueError('Lead mapping unresolved: '+lead['episode_id'])
        mapping.append(dict(original_lead_id=lead['episode_id'],episode_candidate_id=matches[0]['episode_id'],player_id=lead['player_id'],mapping_basis='same observed game/ID assertion; not inferred clinical newness'))
    write('original_lead_mapping',mapping)
    observations=[]
    for rp in reports:
        for o in rp['observations']:
            pid=resolve_name(o['player_name_raw'],people)
            if not pid:raise ValueError('Unmapped Boston status name')
            observations.append(dict(observation_id=rp['source_id']+'_'+pid+'_'+str(o['target_game_date']),source_id=rp['source_id'],player_id=pid,report_at=o['report_at'],target_game_date=o['target_game_date'],status=o['status'],reason=o['reason'],category=absence_category(o['reason']),B_available_at=rp['assumed_available_at'],A_verified_publication_at='',evidence_category='B_publication_lag_assumed; C_in_verified_analysis',evidence_locator=o['evidence_locator']))
    write('status_observations',observations)
    # Capture source checking once per calendar day, not fabricated per-player receipts.
    days={}
    d=date(2024,1,1)
    while d<=date(2024,3,1):
        key=d.isoformat();daily=[r for r in reports if r['source_id']=='report_'+key+'_11AM'];expected=[g for g in schedule if g['game_date']==key]
        complete=all('page_'+g['game_id'] in sm and recaps[g['game_id']]['recap_present'] for g in expected)
        report_attempted=bool(daily);searched=key in searches;reportstate=daily[0]['state'] if daily else 'not_probed'
        # Registered process allows isolated report gaps only with completed game
        # records/recaps and the separately executed daily news search. Explicitly B.
        covered=report_attempted and searched and complete
        days[key]=dict(date=key,daily_report_source_id='report_'+key+'_11AM',report_state=reportstate,news_search_id='search_'+key if searched else '',news_search_executed=searched,expected_Boston_games=len(expected),complete_game_records_and_recaps=complete,B_process_covered=covered,A_process_covered=False,limitation='bounded searched-source surveillance; not exhaustive public knowledge; absence alone is not health evidence',alternative_for_report_gap='dated_news_search_plus_all_expected_game_records' if reportstate in {'missing_report','not_yet_submitted','team_not_covered'} else '')
        d+=timedelta(days=1)
    write('daily_source_coverage',days.values())
    logs=defaultdict(list)
    for r in pg:
        tm=times[r['game_id']]
        logs[r['player_id']].append(dict(game_id=r['game_id'],game_date=r['game_date'],minutes=float(r['minutes']),end_upper=tm['game_end_upper_exclusive'] or None,assumed_available_at=add_elapsed(tm['game_end_upper_exclusive'],hours=6) if tm['game_end_upper_exclusive'] else None,source_id=r['source_id'],mutable_final_statistics=True,source_minutes_raw=r['minutes_source_raw'],source_normalization=r['minutes_normalization']))
    cohort=[];outcomes=[];feature_rows=[];verified_feature_rows=[];windowcoverage=[];eventlinks=[]
    departures={'1630205':'2024-02-07','1630625':'2024-02-08'}
    for lag in (0,1):
        for origin in old:
            pid=origin['player_id'];gid=origin['game_id'];g=pgmap.get((gid,pid));appeared=bool(g and g['appeared']=='True');t=decision(origin['game_date'],lag);end=add_elapsed(t,days=14);day=utc(t).date().isoformat();tm=times[gid]
            date_ambiguous=utc(tm['scheduled_start_utc']).astimezone(ZoneInfo('America/New_York')).date().isoformat()!=origin['game_date']
            proof=ordering(tm['game_end_upper_exclusive'],t) and not date_ambiguous
            recap=recaps[gid];assumed_stats=add_elapsed(tm['game_end_upper_exclusive'],hours=6) if tm['game_end_upper_exclusive'] else None
            stats_ready=bool(assumed_stats and utc(assumed_stats)<=utc(t))
            baseline=[r for r in reports if r.get('assumed_available_at') and utc(r['assumed_available_at'])<=utc(t) and any(s['target_game_date']==origin['game_date'] and s['state']=='complete' for s in r.get('sections',[]))]
            day_report=[r for r in reports if r.get('assumed_available_at') and utc(r['assumed_available_at'])<=utc(t) and r['source_id'].startswith('report_'+day+'_') and r['retrieval_status']=='obtained']
            search=searches.get(day);covered=bool(stats_ready and recap['recap_present'] and baseline and day_report and search)
            disqual=[];evidence=[]
            for e in events:
                if e['source_id']=='page_'+gid and pid==e['player_id'] and stats_ready:disqual.append('new_injury_in_index_game');evidence.append(e['source_id']+'#story.content['+str(e['paragraph'])+']')
            relevant=[o for o in observations if o['player_id']==pid and utc(o['B_available_at'])<=utc(t) and o['target_game_date'] and o['target_game_date']>=day]
            # Latest snapshot for each not-yet-completed target game; an earlier Out
            # is superseded by a later Available, even at the same nominal time.
            latest={}
            for o in sorted(relevant,key=lambda o:(utc(o['report_at']),o['source_id'])):latest[o['target_game_date']]=o
            for o in latest.values():
                if o['status']=='Out' and o['category']=='injury':disqual.append('documented_ongoing_injury_out');evidence.append(o['observation_id'])
                if o['status']=='Out' and o['category'] in {'suspension','personal'}:disqual.append('documented_noninjury_unavailability');evidence.append(o['observation_id'])
            departed=pid in departures and day>departures[pid]
            if departed:disqual.append('documented_roster_departure');evidence.append('tillman_trade' if pid=='1630205' else 'springer_trade')
            state,why=eligibility(appeared=appeared,member=origin['roster_membership']=='member_verified_in_game_roster',time_ordered=proof,covered=covered,explicit_disqualifiers=disqual)
            a_state,a_why=eligibility(appeared=appeared,member=origin['roster_membership']=='member_verified_in_game_roster',time_ordered=proof,covered=False,explicit_disqualifiers=[],verified=True)
            symptoms=[o for o in observations if o['player_id']==pid and utc(o['B_available_at'])<=utc(t) and utc(o['B_available_at'])>=utc(add_elapsed(t,days=-7)) and o['category']=='injury']
            rid=origin['prediction_id']+'_lag'+str(lag)
            cr=dict(row_id=rid,index_game_id=gid,index_game_date=origin['game_date'],player_id=pid,player_name=origin['player_name'],extra_lag_days=lag,decision_at=t,window_end=end,appeared=appeared,index_minutes=float(g['minutes']) if g else None,game_end_ordering=proof,game_end_upper=tm['game_end_upper_exclusive'],game_date_convention='official_team_game_date; scheduled_ET_date_crosscheck; UTC_calendar_date_not_substituted',game_date_ambiguity=date_ambiguous,roster_membership=origin['roster_membership'],B_state=state,B_reason=why,A_state=a_state,A_reason=a_why,prospective_exclusion_evidence_ids=';'.join(evidence),B_symptom_informed=bool(symptoms),B_symptom_source_ids=';'.join(sorted({o['source_id'] for o in symptoms})),A_symptoms_known=False,B_baseline_report_checked=bool(baseline),B_decision_day_report_checked=bool(day_report),recap_reviewed=recap['recap_present'],news_search_id=search['search_id'] if search else '',evidence_category='B_assumption_based; NOT_verified',stats_assumed_available_at=assumed_stats,source_ids=';'.join(['page_'+gid]+[r['source_id'] for r in baseline]+[r['source_id'] for r in day_report]),retrospective_information_used_for_exclusion=False)
            cohort.append(cr)
            if state!='included':continue
            # Full 14-day process coverage, with both partial boundary dates retained.
            daykeys=[];d=utc(t).date()
            while d<=utc(end).date():daykeys.append(d.isoformat());d+=timedelta(days=1)
            surveillance=all(days.get(k,{}).get('B_process_covered',False) for k in daykeys)
            for k in daykeys:windowcoverage.append(dict(row_id=rid,date=k,coverage_id=k,B_process_covered=days.get(k,{}).get('B_process_covered',False),partial_boundary_date=k in {day,utc(end).date().isoformat()},confidence='B_registered_search_not_complete_public_archive'))
            futuregames=[sg for sg in schedule if sg['game_date']>utc(end).date().isoformat() and sg['game_date']<='2024-04-14']
            enough=len(futuregames)>=10
            transferred=pid in departures
            eps=[e for e in episodes if e['player_id']==pid]
            p_label,p_links,p_prev=row_outcome(t,eps,'primary_ge10',surveillance=surveillance,followup=enough,transferred=transferred)
            s_label,s_links,s_prev=row_outcome(t,eps,'secondary_public_gt28',surveillance=surveillance,followup=enough,transferred=transferred)
            outcomes.append(dict(row_id=rid,player_id=pid,extra_lag_days=lag,decision_at=t,window_end=end,primary_ge10=p_label,secondary_public_gt28=s_label,original_medical_gt28='unknown',onset_surveillance_B=surveillance,severity_schedule_followup_B=enough,post_window_team_games=len(futuregames),transferred_followup_unknown=transferred,linked_potential_primary_episodes=';'.join(p_links),linked_potential_secondary_episodes=';'.join(s_links),retrospective_prevalent_episode_ids=';'.join(sorted(set(p_prev+s_prev))),possible_baseline_misclassification=bool(p_prev or s_prev),eligibility_retroactively_changed=False,retrospective_ascertainment_at=now(),historical_label_known_at='',label_known_at_precision='unverified_historical_availability',evidence_confidence='B_surveillance_with_C_retrospective_episode_review',negative_interpretation='no_qualifying_documented_event_under_registered_search; not_absence_of_all_unreported_injury'))
            for e in eps:
                from .logic import in_window
                eventlinks.append(dict(row_id=rid,episode_id=e['episode_id'],onset_membership=in_window(t,e.get('onset_lower'),e.get('onset_upper')),episode_primary=e['primary_ge10'],episode_secondary=e['secondary_public_gt28'],prevalent_retrospective=bool(e.get('onset_upper') and utc(e['onset_upper'])<=utc(t)),exclusion_changed=False))
            history_complete=utc(add_elapsed(t,days=-28)).date().isoformat()>='2023-12-04'
            # Neither new arrival appeared in pilot: no prior-team history is silently zero-filled.
            if pid in {'1630214','1630531'}:history_complete=False
            f=features(logs[pid],t,history_complete=history_complete,baseline_complete=history_complete)
            previous_index=[l for l in logs[pid] if l['game_date']<origin['game_date']]
            prevteam=max(previous_index,key=lambda x:x['game_date']) if previous_index else None
            f.update(row_id=rid,player_id=pid,extra_lag_days=lag,decision_at=t,evidence_category='B_publication_lag_assumed',verified_point_in_time=False,history_complete_28d=history_complete,history_scope='NBA_Boston_team_minutes_only; G_League_not_obtained',history_start='2023-12-04',baseline_definition='prior_28elapsed_days_appearances_excluding_most_recent; never_full_season',index_game_back_to_back=bool(prevteam and (date.fromisoformat(origin['game_date'])-date.fromisoformat(prevteam['game_date'])).days==1),symptom_informed=bool(symptoms),retrospective_diagnoses_used=False)
            prior_team_eligible=[l for l in logs[pid] if l['end_upper'] and l['assumed_available_at'] and utc(l['assumed_available_at'])<=utc(t)]
            prior_team_eligible.sort(key=lambda l:utc(l['end_upper']))
            f['latest_team_game_back_to_back']=bool(len(prior_team_eligible)>=2 and (date.fromisoformat(prior_team_eligible[-1]['game_date'])-date.fromisoformat(prior_team_eligible[-2]['game_date'])).days==1)
            f['input_normalization_flags']=';'.join(sorted({l['source_normalization'] for l in prior_team_eligible if l['source_normalization']!='none'}))
            f['mutable_final_statistics']=True
            feature_rows.append(f)
    write('cohort_all_candidates',cohort);write('operational_included',[r for r in cohort if r['B_state']=='included']);write('row_outcomes',outcomes);write('features_assumption_B',feature_rows)
    write('features_B_no_known_symptoms',[r for r in feature_rows if not r['symptom_informed']])
    write('features_B_symptom_informed',[r for r in feature_rows if r['symptom_informed']])
    write('features_verified_A',[],fields=['row_id','player_id','decision_at','evidence_category','verified_point_in_time'])
    write('window_source_coverage',windowcoverage);write('row_event_links',eventlinks)
    summary={}
    for lag in (0,1):
        cs=[r for r in cohort if r['extra_lag_days']==lag];os=[r for r in outcomes if r['extra_lag_days']==lag]
        summary['lag'+str(lag)]=dict(candidates=len(cs),positive_minute_appearances=sum(r['appeared'] for r in cs),B_states=dict(Counter(r['B_state'] for r in cs)),A_states=dict(Counter(r['A_state'] for r in cs)),primary_ge10=dict(Counter(r['primary_ge10'] for r in os)),secondary_public_gt28=dict(Counter(r['secondary_public_gt28'] for r in os)),original_medical_gt28=dict(Counter(r['original_medical_gt28'] for r in os)),symptom_informed_included=sum(r['B_symptom_informed'] for r in cs if r['B_state']=='included'),features_B=sum(r['extra_lag_days']==lag for r in feature_rows),features_A=0,historically_available_labels=0)
    summary.update(original_leads=28,reviewed_pilot_candidates=len({m['episode_candidate_id'] for m in mapping}),all_reviewed_absence_candidates=len(episodes),distinct_confirmed_qualifying_new_events_primary=sum(e['primary_ge10']=='positive' for e in episodes),distinct_confirmed_qualifying_new_events_public_span=sum(e['secondary_public_gt28']=='positive' for e in episodes),A_verified_rows=0,B_assumptions='stats/recap end_upper+6h; reports header+30min; no archived publication proof',amendment_commit='dc6dc1e3e450e038a47c509a437e31cff0753f7e',historical_files_modified=False)
    (CROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':build()
