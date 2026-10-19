#!/usr/bin/env python3
"""Build linked pilot tables offline from hashed public evidence. No model fitting."""
from collections import defaultdict,Counter
from datetime import date,timedelta
from io import BytesIO
import csv,json,re
from injury_warning.pilot_io import ROOT,manifest,read_source
from injury_warning.longitudinal import (parse_game_page,canonical,resolve_name,minutes,
    absence_category,end_minute,later_noon,point_status,report_player_state)
from injury_warning.rules import utc

OUT=ROOT/'pilot/tables'


def write(name,rows,fields=None):
    rows=list(rows)
    if fields is None:fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def inactive_reasons(body,players):
    from pypdf import PdfReader
    reader=PdfReader(BytesIO(body));text=reader.pages[0].extract_text()
    m=re.search(r'Inactive:\s*Celtics\s*-\s*(.*?)(?=Inactive:|Points in the Paint:)',text,re.S|re.I)
    result={}
    if m:
        for family,reason in re.findall(r'([^(),]+)\s*\(([^)]+)\)',m[1].replace('\n',' ')):
            pid=resolve_name(family.strip(),players)
            if pid:result[pid]=reason.strip()
    return result,text


def build():
    sources=manifest();design=json.loads((ROOT/'pilot/registration/design.json').read_text())
    with (OUT/'team_schedule.csv').open() as f:schedule=list(csv.DictReader(f))
    gameobjects={};players={};listing=defaultdict(dict);ends={};parse_failures=[]
    for sg in schedule:
        sid='page_'+sg['game_id'];rec=sources.get(sid)
        if not rec or rec['status']!='obtained':continue
        try:
            g,actions=parse_game_page(read_source(sid))
            team=next(g[k] for k in ('homeTeam','awayTeam') if str(g[k]['teamId'])==design['team_id'])
            gameobjects[sg['game_id']]=(g,team)
            for p in team['players']+team['inactives']:
                pid=str(p['personId']);players[pid]=dict(player_id=pid,player_name=p['firstName']+' '+p['familyName'],first_name=p['firstName'],family_name=p['familyName'],identity_source_id=sid,evidence_locator='__NEXT_DATA__.props.pageProps.game team players/inactives personId='+pid)
                listing[pid][sg['game_id']]=p
            lo,hi,description=end_minute(actions,sg['game_date']);ends[sg['game_id']]=(lo,hi,description)
        except Exception as exc:parse_failures.append(dict(source_id=sid,state='parse_failure',error=str(exc)))
    pilot_games=[g for g in schedule if g['phase']=='pilot']
    pilot_ids={pid for pid,logs in listing.items() if any(g['game_id'] in logs for g in pilot_games)}
    people=[players[pid] for pid in sorted(pilot_ids)]
    write('players',people)
    # Explicit transaction-day uncertainty; no name-only identity join.
    changes={'1630205':('departure','2024-02-07','tillman_trade'),'1630625':('departure','2024-02-08','springer_trade'),
             '1630214':('arrival','2024-02-07','tillman_trade'),'1630531':('arrival','2024-02-08','springer_trade')}
    rosters=[];transactions=[]
    for p in people:
        pid=p['player_id'];seen=sorted(g['game_date'] for g in schedule if g['game_id'] in listing[pid]);chg=changes.get(pid)
        rr=dict(player_id=pid,team_id=design['team_id'],first_observed_roster_date=seen[0],last_observed_roster_date=seen[-1],entry_lower_date='',entry_upper_date=seen[0],exit_lower_date='',exit_upper_date='',entry_left_censored=True,exit_right_censored=True,contract_type='two_way' if pid in {'1631120','1641809','1629674'} else 'standard',membership_uncertainty='Roster listing verified, but effective membership on transaction days and unobserved intergame membership remain uncertain.',source_id=';'.join(sorted({'page_'+g['game_id'] for g in schedule if g['game_id'] in listing[pid] and g['game_date'] in {seen[0],seen[-1]}})),evidence_locator='team players + inactives; first/last observed roster date is not a signing/waiver date')
        if chg:
            direction,day,sid=chg;nxt=(date.fromisoformat(day)+timedelta(days=1)).isoformat()
            if direction=='arrival':rr.update(entry_lower_date=day,entry_upper_date=nxt,entry_left_censored=False)
            else:rr.update(exit_lower_date=day,exit_upper_date=nxt,exit_right_censored=False)
            transactions.append(dict(player_id=pid,transaction=direction,event_date=day,event_time_precision='day_only; press-release metadata does not establish exact effective time',source_id=sid,evidence_locator='official Celtics trade announcement'))
        rr['corroborating_roster_source_id']='roster_notes_may11'
        rr['corroborating_roster_locator']='May 11 notes page 2 historical roster and acquisition summary; retrospective identity/transaction check, not a historical predictor'
        rosters.append(rr)
    write('roster_membership',rosters);write('transactions',transactions)
    appearances=[];game_times=[];book_checks=[]
    for sg in schedule:
        gid=sg['game_id']
        if gid not in gameobjects:continue
        g,team=gameobjects[gid];sid='page_'+gid
        inactives={str(p['personId']) for p in team['inactives']};reasons={};booktext=''
        if sources.get('book_'+gid,{}).get('status')=='obtained':
            try:reasons,booktext=inactive_reasons(read_source('book_'+gid),list(players.values()))
            except Exception as exc:parse_failures.append(dict(source_id='book_'+gid,state='parse_failure',error=str(exc)))
        total=0
        for pid,logs in listing.items():
            if pid not in pilot_ids or gid not in logs:continue
            p=logs[gid];m=minutes(p.get('statistics',{}).get('minutes'));comment=p.get('comment','');reason=comment or reasons.get(pid,'')
            appeared=m is not None and m>0;total+=m or 0
            appearances.append(dict(game_id=gid,game_date=sg['game_date'],phase=sg['phase'],player_id=pid,player_name=players[pid]['player_name'],appeared=appeared,minutes=m if m is not None else 0,minutes_precision='seconds' if m is not None else 'not_played',minutes_source_raw=p.get('statistics',{}).get('minutes',''),minutes_normalization='carried_60seconds' if p.get('statistics',{}).get('minutes','').endswith(':60') else 'none',inactive=pid in inactives,nonappearance_reason=reason if not appeared else '',absence_category=absence_category(reason) if not appeared else 'appeared_not_health_verified',source_id=sid,reason_source_id='book_'+gid if pid in reasons else sid,evidence_locator='team.players/inactives personId='+pid+'; gamebook FINAL BOX page 1 inactive list',input_publication_at='',input_publication_precision='unverified_original_availability'))
        lo,hi,description=ends[gid]
        game_times.append(dict(game_id=gid,game_date=sg['game_date'],phase=sg['phase'],scheduled_start_utc=g['gameTimeUTC'],game_end_lower=lo or '',game_end_upper_exclusive=hi or '',game_end_precision='documented_minute' if lo else 'unknown',end_description=description,source_id=sid,evidence_locator='playByPlay.actions final period/end description',original_publication_at='',original_publication_precision='unknown'))
        # Independent official PDF consistency check: team minutes, player names, inactive list.
        book_checks.append(dict(game_id=gid,source_id='book_'+gid,structured_source_id=sid,minutes_total=round(total,3),expected_minutes=240+25*max(0,int(g['period'])-4),minute_sum_ok=abs(total-(240+25*max(0,int(g['period'])-4)))<0.05,inactive_reasons_mapped=len(reasons),pdf_available=bool(booktext),evidence_locator='FINAL BOX page 1 and __NEXT_DATA__.game'))
    write('player_games',appearances);write('game_timing',game_times);write('gamebook_checks',book_checks)
    reports=json.loads((ROOT/'pilot/parsed_reports.json').read_text());observations=[];reportcoverage=[]
    for rp in reports:
        reportcoverage.append(dict(source_id=rp['source_id'],report_at=rp.get('report_at',''),state=rp['state'],listed_bos_players=len(rp['observations']),retrieval_status=rp['retrieval_status'],publication_at='',publication_precision='document_header_time_only; original_public_availability_unverified',error=rp.get('error','')))
        for o in rp['observations']:
            pid=resolve_name(o['player_name_raw'],people)
            observations.append(dict(observation_id=f"{rp['source_id']}_{pid or canonical(o['player_name_raw'])}",source_id=rp['source_id'],player_id=pid or '',player_name_raw=o['player_name_raw'],report_at=o['report_at'],target_game_date=o.get('target_game_date',''),status=o['status'],reason=o['reason'],category=absence_category(o['reason']),publication_at='',publication_verified=False,evidence_locator=o['evidence_locator'],identity_uncertainty='' if pid else 'unmapped_or_ambiguous'))
    write('status_observations',observations,fields=['observation_id','source_id','player_id','player_name_raw','report_at','target_game_date','status','reason','category','publication_at','publication_verified','evidence_locator','identity_uncertainty'])
    write('report_coverage',reportcoverage)
    # Snapshot lookup retains absent listing separately from missing or unsubmitted team report.
    snapshotgrid=[]
    for rp in reports:
        sections=rp.get('sections') or [dict(target_game_date='',state=rp['state'])]
        for section in sections:
            listed={o['player_id'] for o in observations if o['source_id']==rp['source_id'] and o['target_game_date']==section['target_game_date']}
            for p in people:
                target_games=[g['game_id'] for g in schedule if g['game_date']==section['target_game_date']]
                member_state=('member_in_target_game_listing' if any(gid in listing[p['player_id']] for gid in target_games) else 'not_in_target_game_listing' if target_games else 'target_game_not_collected')
                if p['player_id'] in changes and changes[p['player_id']][1]==section['target_game_date']:member_state='uncertain_transaction_day'
                snapshotgrid.append(dict(source_id=rp['source_id'],target_game_date=section['target_game_date'],player_id=p['player_id'],state=report_player_state(section['state'],p['player_id'] in listed),report_at=rp.get('report_at',''),membership_at_report=member_state+'; retrospective_coverage_only_not_health_evidence',evidence_locator='PDF team/game-date section; status_observations join'))
    write('report_player_coverage',snapshotgrid)
    history=defaultdict(list)
    for row in appearances:
        if row['phase']=='history':history[row['player_id']].append(row['minutes'])
    groups={pid:('no_preperiod_history' if not history[pid] else 'high_24plus' if sum(history[pid])/len(history[pid])>=24 else 'rotation_10to24' if sum(history[pid])/len(history[pid])>=10 else 'depth_under10') for pid in pilot_ids}
    predictions=[];workloads=[]
    for sg in pilot_games:
        gid=sg['game_id'];lo,hi,desc=ends.get(gid,(None,None,''));noon=later_noon(sg['game_date'])
        for p in people:
            pid=p['player_id']
            # Each game roster explicitly lists both active and inactive members. Future
            # listings never infer membership on an earlier pilot game.
            change=changes.get(pid)
            transaction_day=bool(change and change[1]==sg['game_date'])
            inferred_arrival=bool(transaction_day and change[0]=='arrival' and gid not in listing[pid])
            if gid not in listing[pid] and not inferred_arrival:continue
            membership='uncertain_transaction_day' if transaction_day else 'member_verified_in_game_roster'
            game_row=next((x for x in appearances if x['game_id']==gid and x['player_id']==pid),dict(appeared=False,absence_category='roster_listing_absent_membership_uncertain'))
            # Only observations after this game's conservative end bound can describe
            # postgame availability. Pregame availability is not carried across a game.
            available_obs=[o for o in observations if o['player_id']==pid and hi and utc(hi)<=utc(o['report_at'])<=utc(noon)]
            ob=max(available_obs,key=lambda o:utc(o['report_at'])) if available_obs else None
            strict,why=point_status(ob,noon)
            nominal,nomwhy=point_status(ob,noon,require_verified_publication=False)
            predid=gid+'_'+pid
            predictions.append(dict(prediction_id=predid,game_id=gid,game_date=sg['game_date'],player_id=pid,player_name=p['player_name'],roster_membership=membership,roster_source_id=('page_'+gid if gid in listing[pid] else change[2]),immediate_prediction_at='',immediate_eligibility='unknown',immediate_blocker='game_end_only_minute_precision; input_publication_unverified',later_prediction_at=noon,later_eligibility=strict,later_eligibility_reason=why,later_evidence_id=ob['observation_id'] if ob else '',nominal_header_sensitivity_eligibility=nominal,nominal_header_sensitivity_reason=nomwhy,appeared_in_completed_game=game_row['appeared'],appearance_only_alternative='observed_appearance_not_health_eligible' if game_row['appeared'] else 'not_in_appearance_only_subset',preperiod_playing_time_group=groups[pid],observed_game_absence_category=game_row['absence_category'],primary_label='unknown',secondary_label='unknown',onset_surveillance_complete=False,severity_followup_complete=False,label_known_at_primary='',label_known_at_secondary='',label_known_at_precision='unverified',label_blocker='full_14day_onset_surveillance_not_established; episode_severity_unresolved',evidence_locator='roster __NEXT_DATA__.game; status_observations join; no future appearance used'))
            for days in (7,14,28):
                vals=[a['minutes'] for a in appearances if a['player_id']==pid and (date.fromisoformat(sg['game_date'])-timedelta(days=days))<date.fromisoformat(a['game_date'])<=date.fromisoformat(sg['game_date'])]
                workloads.append(dict(prediction_id=predid,player_id=pid,window_days=days,retrospective_calendar_minutes=round(sum(vals),3),retrospective_calendar_appearances=sum(v>0 for v in vals),point_in_time_feature_eligible=False,blocker='calendar_date_window_only; original_stat_publication_unknown; not_a_model_feature',source_ids=';'.join('page_'+a['game_id'] for a in appearances if a['player_id']==pid and (date.fromisoformat(sg['game_date'])-timedelta(days=days))<date.fromisoformat(a['game_date'])<=date.fromisoformat(sg['game_date']))))
    write('prediction_timestamps',predictions);write('workload_feasibility',workloads)
    # Injury-attributed absences are episode leads, not automatically merged episodes.
    episodes=[]
    for a in appearances:
        if a['phase']=='pilot' and a['absence_category']=='injury':
            episodes.append(dict(episode_id='lead_'+a['game_id']+'_'+a['player_id'],record_type='unadjudicated_episode_lead',player_id=a['player_id'],observed_absence_date=a['game_date'],reason=a['nonappearance_reason'],onset_lower='',onset_upper='',first_injury_missed_game='',medical_clearance='',first_return='',episode_relation='unresolved',primary_label='unknown',secondary_label='unknown',label_known_at='',source_ids=a['source_id']+';'+a['reason_source_id'],evidence_locator=a['evidence_locator'],adjudicator='Codex automated extraction; no independent human review',uncertainty='A game absence is verified; new onset, continuity and episode grouping unverified.'))
    write('injury_episodes',episodes,fields=['episode_id','record_type','player_id','observed_absence_date','reason','onset_lower','onset_upper','first_injury_missed_game','medical_clearance','first_return','episode_relation','primary_label','secondary_label','label_known_at','source_ids','evidence_locator','adjudicator','uncertainty'])
    cohortcoverage=[]
    for group in sorted(set(groups.values())):
        rows=[r for r in predictions if r['preperiod_playing_time_group']==group]
        cohortcoverage.append(dict(grouping='preperiod_playing_time',group=group,players=len({r['player_id'] for r in rows}),candidate_rows=len(rows),immediate_available=0,later_available=sum(r['later_eligibility']=='available' for r in rows),later_unavailable=sum(r['later_eligibility']=='unavailable' for r in rows),later_unknown=sum(r['later_eligibility']=='unknown' for r in rows),appeared_rows=sum(r['appeared_in_completed_game'] for r in rows),nominal_header_available=sum(r['nominal_header_sensitivity_eligibility']=='available' for r in rows)))
    for category in sorted({r['observed_game_absence_category'] for r in predictions}):
        rows=[r for r in predictions if r['observed_game_absence_category']==category]
        cohortcoverage.append(dict(grouping='retrospective_completed_game_category',group=category,players=len({r['player_id'] for r in rows}),candidate_rows=len(rows),immediate_available=0,later_available=sum(r['later_eligibility']=='available' for r in rows),later_unavailable=sum(r['later_eligibility']=='unavailable' for r in rows),later_unknown=sum(r['later_eligibility']=='unknown' for r in rows),appeared_rows=sum(r['appeared_in_completed_game'] for r in rows),nominal_header_available=sum(r['nominal_header_sensitivity_eligibility']=='available' for r in rows)))
    write('eligibility_coverage',cohortcoverage)
    catalog=json.loads((ROOT/'pilot/request_catalog.json').read_text())
    pilot_source_ids={r['source_id'] for r in catalog}
    source_coverage=[]
    for r in catalog:
        receipt=sources.get(r['source_id'])
        source_coverage.append(dict(source_id=r['source_id'],kind=r['kind'],url=r['url'],requested_date=r['date'],state=receipt['status'] if receipt else 'not_attempted_after_same_endpoint_403',retrieved_at=receipt.get('retrieved_at','') if receipt else '',publication_at='',publication_precision='original_unverified',evidence_locator='source_manifest.jsonl receipt; registered request catalog'))
    write('source_coverage',source_coverage)
    failures=[dict(source_id=sid,kind=r['kind'],url=r['url'],state=r['status'],http_status=r.get('http_status',''),error=r.get('error',''),retrieved_at=r['retrieved_at']) for sid,r in sources.items() if r['status']!='obtained']+parse_failures
    write('retrieval_failures',failures)
    summary=dict(team='Boston Celtics',prediction_start=design['prediction_start'],prediction_end=design['prediction_end'],players=len(people),games=len(pilot_games),history_games=sum(g['phase']=='history' for g in schedule),followup_games=sum(g['phase']=='followup' for g in schedule),candidate_player_games=len(predictions),roster_membership_counts=dict(Counter(r['roster_membership'] for r in predictions)),immediate=dict(Counter(r['immediate_eligibility'] for r in predictions)),later_noon=dict(Counter(r['later_eligibility'] for r in predictions)),nominal_header_sensitivity=dict(Counter(r['nominal_header_sensitivity_eligibility'] for r in predictions)),appearance_only_rows=sum(r['appeared_in_completed_game'] for r in predictions),report_coverage=dict(Counter(r['state'] for r in reports)),status_observations=len(observations),unmapped_observations=sum(not r['player_id'] for r in observations),unresolved_episode_leads=len(episodes),adjudicated_new_pilot_events=0,original_publication_verified_rows=0,game_end_minute_available=sum(bool(ends.get(g['game_id'],(None,))[0]) for g in pilot_games),raw_sources=dict(Counter(r['status'] for r in sources.values())),pilot_raw_sources=dict(Counter(r['status'] for sid,r in sources.items() if sid in pilot_source_ids)),report_section_coverage=dict(Counter(s['state'] for r in reports for s in r.get('sections',[]))),primary_label_counts=dict(Counter(r['primary_label'] for r in predictions)),secondary_label_counts=dict(Counter(r['secondary_label'] for r in predictions)),gamebook_consistency_failures=sum(not r['minute_sum_ok'] for r in book_checks))
    (ROOT/'pilot/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':build()
