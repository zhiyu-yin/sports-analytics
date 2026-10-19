"""Offline Phase 1D audit and separately registered endpoint results."""
from collections import Counter,defaultdict
from datetime import date,timedelta
import json,hashlib,re
from phase1d.acquire import D,ROOT,read,manifest,schedule
from phase1d.prepare import rows,write,page,game_bounds
from phase1d.logic import day_bounds,label_events,absence_runs,applicable_schedule,membership
from phase1c.logic import decision,eligibility,in_window,row_outcome
from injury_warning.rules import utc
from injury_warning.longitudinal import absence_category

def truth(x):return x is True or x=='True'
def normalized(r):
    return dict(r,appeared=truth(r['appeared']),roster_observed=truth(r.get('roster_observed',True)))
def boston_logs(pid):
    return [dict(game_id=r['game_id'],game_date=r['game_date'],player_id=pid,appeared=truth(r['appeared']),category=r['absence_category'],reason=r['nonappearance_reason'],roster_observed=True,coverage='page_and_book',page_source=r['source_id'],reason_source=r['reason_source_id']) for r in rows('player_games.csv','pilot') if r['player_id']==pid]
def verify():
    p=D/'registration/alternative_v1.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==p.with_suffix('.sha256').read_text().strip()
    for path,h in json.loads((D/'registration/preserved_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path

def fixtures(target):
    reports=json.loads((D/'parsed_reports.json').read_text());searches=json.loads((D/'search_ledger.json').read_text());events=[];result=[];evidence=[]
    for pid,team,onset,first,last,cid,news in [('203944','NYK','2024-01-27','2024-01-29','2024-04-14','A02','d_randle_update'),('1630163','CHA','2023-11-26','2023-11-28','2024-01-10','A03','d_ball_return')]:
        logs=sorted([r for r in target if r['player_id']==pid],key=lambda r:r['game_date']);onsetrow=next(r for r in logs if r['game_date']==onset);firstrow=next(r for r in logs if r['game_date']==first)
        # Randle's already cached complete individual PDF assertions are retained.
        severity_rows=[r for r in rows('case_assertions.csv','pilot') if r['case_id']==cid and r['assertion']=='game_absence_attribution'] if cid=='A02' else [dict(value=r['reason'],source_id=r['reason_source'],evidence_locator='FINAL BOX page 1; '+r['game_date']) for r in logs if first<=r['game_date']<=last]
        expected=[r for r in schedule() if r['team']==team and first<=r['game_date']<=last]
        assert len(severity_rows)==len(expected)
        narrative=read(news).decode();assert ('Jan. 27' in narrative and 'shoulder' in narrative.lower()) if cid=='A02' else ('Nov. 26' in narrative and '20-game absence' in narrative)
        assert all('injury/illness' in r['value'].lower() for r in severity_rows)
        # This reviewed link is source-based, separate from matching diagnosis text.
        # Randle: ongoing Jan27 shoulder absence (article); Ball: Nov26 event to Jan12 return (article).
        adjudication=json.loads((D/'fixture_adjudications.json').read_text())[cid]
        assert adjudication['continuity_source']==news
        continuity=adjudication['common_episode_supported'] is True
        clinical_lo,clinical_hi,clinical_precision=game_bounds(onsetrow['game_id'],onset,True);run_lo,run_hi,run_precision=game_bounds(firstrow['game_id'],first)
        event=dict(event_id=cid+'_documented_event',player_id=pid,clinical_lower=clinical_lo,clinical_upper=clinical_hi,run_lower=run_lo,run_upper=run_hi,severity='positive' if len(severity_rows)>=10 and continuity else 'unknown',continuity_supported=continuity,confirmed_same_episode_games=len(severity_rows),clinical_onset_type='documented acute injury event or recurrence; not first lifetime biological symptom',anchor_game_id=firstrow['game_id'],anchor_precision=run_precision,clinical_precision=clinical_precision,onset_source='page_'+onsetrow['game_id'],onset_locator='story.content[2]',continuity_source=news,continuity_locator=adjudication['continuity_locator'],severity_source_ids=';'.join(r['source_id'] for r in severity_rows),first_miss=first,last_documented_miss=last,return_date='2024-01-12' if cid=='A03' else '',cohort_role='external_integration_fixture_only',historical_label_known_at='')
        events.append(event)
        for e in severity_rows:evidence.append(dict(e,case_id=cid))
        for r in logs:
            if r['game_date']>onset:continue
            for lag in (0,1):
                t=decision(r['game_date'],lag);day=utc(t).date().isoformat();available=[rp for rp in reports if rp['team']==team and rp.get('B_available_at') and utc(rp['B_available_at'])<=utc(t)]
                baseline=[rp for rp in available if any(s['target_game_date']==r['game_date'] and s['state']=='complete' for s in rp['sections'])]
                current=[rp for rp in available if rp['source_id'].startswith('report_'+day+'_') and rp['retrieval_status']=='obtained'];search=[q for q in searches if q['date']==day and q['team']==team]
                ready=bool(r.get('stats_B_available_at') and utc(r['stats_B_available_at'])<=utc(t));coverage=bool(baseline and current and search and ready and truth(r['recap_present']))
                disqual=[];disqual_sources=[]
                # Reviewed completed-game paragraphs, never the later severity article.
                if r['game_date']==onset and ready:disqual.append('new_injury_in_index_game');disqual_sources.append('page_'+r['game_id']+'#story.content[2]')
                relevant={}
                for rp in sorted(available,key=lambda x:utc(x['B_available_at'])):
                    for o in rp['observations']:
                        if o['player_name_raw'].split(',')[0] in {'Randle','Ball'} and o['target_game_date'] and o['target_game_date']>=day:relevant[o['target_game_date']]=(o,rp['source_id'])
                for o,sid in relevant.values():
                    if o['status']=='Out' and absence_category(o['reason'])=='injury':disqual.append('documented_ongoing_injury_out');disqual_sources.append(sid+'#'+o['evidence_locator'])
                state,reason=eligibility(appeared=r['appeared'],member=r['roster_observed'],time_ordered=bool(r.get('end_upper') and utc(r['end_upper'])<utc(t)),covered=coverage,explicit_disqualifiers=disqual)
                clinical,clinks=label_events(t,[event],'clinical');run,rlinks=label_events(t,[event],'run')
                result.append(dict(fixture_row_id=cid+'_'+r['game_id']+'_lag'+str(lag),case_id=cid,player_id=pid,index_game_id=r['game_id'],index_game_date=r['game_date'],extra_lag_days=lag,decision_at=t,eligibility_B=state,eligibility_reason=reason,index_minutes=r['minutes'],game_end_upper=r.get('end_upper',''),stats_B_available_at=r.get('stats_B_available_at',''),baseline_report_ids=';'.join(x['source_id'] for x in baseline),decision_report_ids=';'.join(x['source_id'] for x in current),dated_search_executed=bool(search),exclusion_source_ids=';'.join(disqual_sources),A_state='unknown' if r['appeared'] else 'not_in_population',clinical_event_relation=clinical,absence_run_relation=run,clinical_cohort_label=clinical if state=='included' else 'not_labelled_'+state,run_cohort_label=run if state=='included' else 'not_labelled_'+state,event_id=event['event_id'],scope='selected_event_integration_test; negative_relation_is_not_all_event_surveillance',historical_label_known_at='',outcome_evidence_in_eligibility=False,fixture_in_Boston_counts=False))
    write('fixture_events',events);write('fixture_severity_evidence',evidence);write('fixture_rows',result);return result

def build():
    verify();target=[normalized(r) for r in rows('target_game_evidence.csv','phase1d')];old=rows('row_outcomes.csv');cohort={r['row_id']:r for r in rows('cohort_all_candidates.csv')};episodes=rows('episode_candidates.csv');players={r['player_id'] for r in old};runs=[];transfer=[];byplayer={}
    for pid in players:
        logs=boston_logs(pid)
        if pid in {'1630205','1630625'}:
            departure='2024-02-07' if pid=='1630205' else '2024-02-08';dest=[r for r in target if r['player_id']==pid];logs=applicable_schedule(logs,dest,departure)
            for r in logs:transfer.append(dict(r,team=r.get('team','BOS'),actual_schedule=True,departure_date=departure))
        for g in logs:
            g['anchor_lower'],g['anchor_upper'],g['anchor_precision']=game_bounds(g['game_id'],g['game_date'])
        byplayer[pid]=logs;runs.extend(absence_runs(logs))
    write('absence_run_candidates',runs);write('transfer_applicable_game_sequence',transfer)
    # Independently review clinical event relevance. Absence envelopes are NOT asserted new events.
    review=[];narrative_refs={'1627759':'page_0022301105#story.content[9];page_0022301118#story.content[18]','1628369':'page_0022301134#story.content[5]','201143':'page_0022301023#story.content[6];page_0022301060#story.content[17]','1628401':'page_0022300980#story.content[3]','201950':'page_0022300938#story.content[10]','204001':'page_0022300920#story.content[13];page_0022300984#story.content[6];page_0022301148#story.content[16]'}
    for e in episodes:
        if not e['episode_id'].endswith('_20240412'):continue
        logs=byplayer[e['player_id']];same=[r for r in logs if r['category']=='injury' and r['game_date']<'2024-04-12'];review.append(dict(episode_id=e['episode_id'],player_id=e['player_id'],clinical_lower='',clinical_upper=e['onset_upper'],new_event_date='',clinical_symptom_onset='unobservable',first_observed_final_run='2024-04-12',final_run_games='0022301173;0022301186',final_run_observed_games=2,final_run_closed=False,common_episode_to_early_window='not_established; neither asserted unrelated nor asserted continuous',earlier_injury_absence_dates=';'.join(r['game_date'] for r in same),earlier_injury_reasons=';'.join(sorted({r['reason'] for r in same})),independent_continuity_sources=narrative_refs[e['player_id']],conflicting_context_sources='page_0022301173#story.content[5,6];page_0022301186#story.content[0,1]',clinical_severity='unknown; no supported >=10 same-episode run, final run right-censored',clinical_decision='unknown because clinical event/continuity ascertainment insufficient; candidate is a sensitivity witness, not evidence of a January injury',run_decision='final run begins April12; definitely outside every Jan/Feb decision horizon',recovery_inferred_from_appearance=False,lower_bound_inferred_from_appearance=False))
    write('season_end_event_review',review)
    audit=[];out=[];transferrows=[];runlinks=[]
    reviewed_at=json.loads((D/'adjudication_metadata.json').read_text())['retrospective_reviewed_at']
    for r in old:
        pid=r['player_id'];t=r['decision_at'];logs=byplayer[pid];pr=[e for e in runs if e['player_id']==pid];coverage=truth(r['onset_surveillance_B']);followup=truth(r['severity_schedule_followup_B'])
        if pid in {'1630205','1630625'}:
            # Require every destination roster and reason source, plus complete season schedule.
            dest=[x for x in target if x['player_id']==pid];followup=bool(dest) and all(x['roster_observed'] and x['coverage']=='page_and_book' for x in dest)
        alt,links=label_events(t,pr,'run',coverage=coverage,followup=followup)
        for e in pr:runlinks.append(dict(row_id=r['row_id'],event_id=e['event_id'],anchor_lower=e['run_lower'],anchor_upper=e['run_upper'],window_membership=membership(t,e['run_lower'],e['run_upper']),severity=e['severity'],continuity_supported=e['continuity_supported'],possible_run_upper=e['possible_run_upper'],reason=e['reason']))
        clinical=r['primary_ge10'];span=r['secondary_public_gt28']
        if pid in {'1630205','1630625'}:
            olde=[dict(e,onset_lower=e['onset_lower'] or None,onset_upper=e['onset_upper'] or None) for e in episodes if e['player_id']==pid]
            # Complete post-departure run upper bounds can resolve absence severity;
            # late right-censored candidates still cannot receive invented clinical bounds.
            dest_uncertain=any(e['severity']=='unknown' for e in pr)
            clinical=row_outcome(t,olde,'primary_ge10',surveillance=coverage,followup=followup,transferred=dest_uncertain)[0]
            span_unknown=any(not e['return_date'] or (date.fromisoformat(e['return_date'])-date.fromisoformat(e['anchor_date'])).days>28 for e in pr)
            span=row_outcome(t,olde,'secondary_public_gt28',surveillance=coverage,followup=followup,transferred=span_unknown)[0]
            transferrows.append(dict(row_id=r['row_id'],player_id=pid,extra_lag_days=r['extra_lag_days'],decision_at=t,original_clinical=r['primary_ge10'],clinical_after=clinical,public_span_after=span,run_onset_after=alt,destination_games=len(dest),destination_roster_complete=followup,unresolved_run_ids=';'.join(e['event_id'] for e in pr if e['severity']=='unknown'),reason='destination complete closed short runs resolve severity' if clinical=='negative' else 'late right-censored clinical candidate remains unresolved; destination schedule obtained',historical_label_known_at=''))
        out.append(dict(row_id=r['row_id'],player_id=pid,extra_lag_days=r['extra_lag_days'],decision_at=t,window_end=r['window_end'],clinical_before=r['primary_ge10'],clinical_after=clinical,public_span_before=r['secondary_public_gt28'],public_span_after=span,original_medical_gt28=r['original_medical_gt28'],absence_run_onset_ge10=alt,run_link_ids=';'.join(links),B_coverage=coverage,applicable_team_followup=followup,A_historical_verified=False,historical_label_known_at='',retrospective_evidence_category='C',retrospective_ascertainment_at=reviewed_at,historical_training_cutoff_usable=False,eligibility_source_row=r['row_id'],features_source_row=r['row_id'],prospective_inputs_unchanged=True))
        responsible=[e for e in episodes if e['episode_id'].endswith('_20240412') and e['episode_id'] in r['linked_potential_primary_episodes'].split(';')]
        for e in responsible:
            intervening=[g for g in logs if utc(t).date().isoformat()<=g['game_date']<'2024-04-12'];apps=[g for g in intervening if g['appeared']];blocks=[x for x in pr if utc(t).date().isoformat()<=x['anchor_date']<'2024-04-12']
            audit.append(dict(row_id=r['row_id'],player_id=pid,extra_lag_days=r['extra_lag_days'],decision_at=t,window_end=r['window_end'],responsible_candidate=e['episode_id'],clinical_onset_lower='',clinical_onset_upper=e['onset_upper'],onset_source=e['onset_source_id'],onset_locator=e['onset_evidence_locator'],clinical_event_link_status='not_established; conservative possible relevance only',intervening_appearance_ids=';'.join(g['game_id'] for g in apps),intervening_appearance_dates=';'.join(g['game_date'] for g in apps),intervening_appearance_count=len(apps),intervening_run_ids=';'.join(x['event_id'] for x in blocks),intervening_run_upper_bounds=';'.join(str(x['possible_run_upper']) for x in blocks),run_start_lower=game_bounds('0022301173','2024-04-12')[0],run_start_upper=game_bounds('0022301173','2024-04-12')[1],clinical_could_satisfy='not excluded by onset bounds; no demonstrated in-window new event or >=10 common-episode attribution; severity censored',clinical_final=clinical,clinical_reason='estimand ascertainment limitation, not a confirmed late-to-early event link; appearances do not bound onset or prove recovery',final_run_window_relation='definitely_outside',run_final=alt,run_reason='all potentially in-window run severities checked separately; April12 run cannot itself start in this window',historical_label_known_at=''))
    write('row_outcomes',out);write('row_run_links',runlinks);write('unknown_row_linkage_audit',audit);write('transfer_row_review',transferrows)
    boundary=[dict(r,departure_date='2024-02-07' if r['player_id']=='1630205' else '2024-02-08',counted_as_applicable_team_game=False,reason='transaction-day roster boundary unresolved; no appearance; adding this one possible game cannot create a >=10-game or >28-day run before next destination appearance') for r in rows('player_games.csv','pilot') if (r['player_id'],r['game_date']) in [('1630205','2024-02-07'),('1630625','2024-02-08')]]
    write('transfer_transaction_boundaries',boundary)
    fr=fixtures(target)
    counts=[]
    for lag in ('0','1'):
        rs=[r for r in out if r['extra_lag_days']==lag]
        for endpoint in ['clinical_before','clinical_after','public_span_before','public_span_after','original_medical_gt28','absence_run_onset_ge10']:counts.append(dict(extra_lag_days=lag,endpoint=endpoint,n=len(rs),**{s:sum(r[endpoint]==s for r in rs) for s in ['positive','negative','unknown']}))
    write('before_after_counts',counts)
    summary=dict(registration_commit='facea5b',readiness=dict(bounded_development_collection_for_run_onset=True,general_clinical_onset_collection=False,model_training=False,conditions='retain B assumptions, common-episode adjudication and separate clinical measurement'),cohort_counts=counts,baseline_118_audit_rows=sum(r['extra_lag_days']=='0' for r in audit),both_lags_audit_rows=len(audit),transfer_by_lag={str(l):dict(Counter(r['clinical_after'] for r in transferrows if r['extra_lag_days']==str(l))) for l in (0,1)},fixture_rows=len(fr),fixture_eligible_labels={k:dict(Counter(r[k] for r in fr)) for k in ['clinical_cohort_label','run_cohort_label']},new_receipts=len((D/'source_manifest.jsonl').read_text().splitlines()),historical_label_known_at_count=0,features_changed=0,independent_human_reviews=0)
    (D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));verify()
if __name__=='__main__':build()
