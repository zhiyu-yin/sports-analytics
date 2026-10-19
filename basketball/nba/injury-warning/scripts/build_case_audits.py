#!/usr/bin/env python3
"""Six source-linked case reviews; preserves original 25 records and pilot denominators."""
from collections import Counter
from datetime import date
from io import BytesIO
import csv,json,re
from injury_warning.pilot_io import ROOT,manifest,read_source,now
from injury_warning.longitudinal import parse_game_page,canonical,absence_category,minutes


def write(name,rows):
    with (ROOT/'pilot/tables'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));w.writeheader();w.writerows(rows)


def build():
    from pypdf import PdfReader
    cases=json.loads((ROOT/'pilot/case_audit_selection.json').read_text());games=json.loads((ROOT/'pilot/case_team_games.json').read_text());sources=manifest();rows=[];assertions=[];game_evidence=[]
    teamlabels={'PHI':'76ers','NYK':'Knicks','CHA':'Hornets','GSW':'Warriors','BOS':'Celtics','HOU':'Rockets'}
    original_sources={'A01':'embiid_return','A02':'randle_update','A03':'ball_return','A04':'curry_return','A22':'report_jan04','A09':'sengun_game'}
    for c in cases:
        cg=sorted([g for g in games if g['case_id']==c['case_id']],key=lambda g:g['game_date']);people={};id_sources=[]
        for g in cg:
            sid='page_'+g['game_id']
            if sources.get(sid,{}).get('status')!='obtained':continue
            game,_=parse_game_page(read_source(sid));team=next(game[k] for k in ('homeTeam','awayTeam') if game[k]['teamTricode']==c['team'])
            for p in team['players']+team['inactives']:
                if canonical(p['firstName']+' '+p['familyName'])==canonical(c['name']):people[str(p['personId'])]=p;id_sources.append(sid)
        if len(people)!=1:raise ValueError('Unresolved player identity: '+c['name'])
        pid=next(iter(people));p=people[pid];surname=p['familyName'];checks=[];actual_return=False
        for g in cg:
            gid=g['game_id'];sid='book_'+gid;reason='';appearance=None;pdf_checked=False
            if sources.get(sid,{}).get('status')=='obtained':
                text=PdfReader(BytesIO(read_source(sid))).pages[0].extract_text()
                m=re.search(r'Inactive:\s*'+teamlabels[c['team']]+r'\s*-\s*(.*?)(?=Inactive:|Points in the Paint:)',text,re.S|re.I)
                if m:
                    entries=re.findall(r'([^(),]+)\s*\(([^)]+)\)',m[1].replace('\n',' '))
                    hits=[reason.strip() for family,reason in entries if canonical(family.strip())==canonical(surname)]
                    if len(hits)==1:reason=hits[0]
                if not reason:
                    layout=PdfReader(BytesIO(read_source(sid))).pages[0].extract_text(extraction_mode='layout')
                    matches=[line for line in layout.splitlines() if canonical(c['name']) in canonical(line) and ('DND -' in line or 'DNP -' in line)]
                    if len(matches)==1:reason=re.search(r'DN[DP] -.*',matches[0])[0].strip()
                pdf_checked=True
            page='page_'+gid
            if sources.get(page,{}).get('status')=='obtained':
                game,_=parse_game_page(read_source(page));team=next(game[k] for k in ('homeTeam','awayTeam') if game[k]['teamTricode']==c['team'])
                entry=next((p for p in team['players'] if str(p['personId'])==pid),None)
                appearance=bool(entry and (minutes(entry['statistics']['minutes']) or 0)>0)
                if g['game_date']==c['return_date']:actual_return=appearance
            if c['first_missed']<=g['game_date']<=c['last_missed']:
                category=absence_category(reason)
                checks.append(dict(case_id=c['case_id'],player_id=pid,game_id=gid,game_date=g['game_date'],pdf_checked=pdf_checked,reason=reason,category=category,source_id=sid if pdf_checked else '',evidence_locator='FINAL BOX page 1; Inactive: '+teamlabels[c['team']],original_publication_at='',publication_precision='unverified'))
            game_evidence.append(dict(case_id=c['case_id'],player_id=pid,game_id=gid,game_date=g['game_date'],appearance_verified=appearance,source_id=page if appearance is not None else '',reason=reason,reason_source_id=sid if pdf_checked else '',evidence_locator='__NEXT_DATA__.game team players/inactives; FINAL BOX page 1'))
        injury_run=sum(x['category']=='injury' for x in checks);complete_run=bool(checks) and all(x['category']=='injury' for x in checks)
        # Existing explicit retrospective aggregate sources remain outcome-only.
        aggregate=29 if c['case_id']=='A01' else 20 if c['case_id']=='A03' else None
        secondary='excluded' if c['case_id']=='A22' else ('positive' if aggregate and aggregate>=10 else 'positive' if complete_run and injury_run>=10 else 'negative' if complete_run and actual_return and injury_run<10 else 'unknown')
        primary='positive' if c['case_id']=='A02' else 'negative' if c['case_id']=='A04' and actual_return else 'excluded' if c['case_id']=='A22' else 'unknown'
        proxy=(date.fromisoformat(c['return_date'])-date.fromisoformat(c['onset'])).days if c['onset'] and actual_return else None
        first=next((x for x in checks if x['game_date']==c['first_missed']),None)
        first_verified=bool(first and first['category']=='injury')
        note={
            'A01':'Same left-knee meniscus episode linked by source injury/return narrative and first missed-game reason. 29-game aggregate verified against team schedule. No full medical clearance or continuous medical-unavailability interval obtained; pre-existing knee symptoms also leave new injury versus continuation unresolved.',
            'A02':'Dislocated shoulder narrative documents continued sidelining into April. All team games in the injury-absence run individually checked, including DND rows outside the inactive list. No return appearance through regular-season end; censor there, never extend through offseason.',
            'A03':'November ankle event and January return linked by narrative. Twenty-game aggregate agrees with schedule. Prior same-ankle surgery makes recurrence history relevant; do not merge with the later January setback. Continuous medical unavailability remains unverified.',
            'A04':'March right-ankle event, three individually injury-attributed missed games, and March 16 return establish short upper bound. Clearance for on-court activity is not full competition clearance.',
            'A22':'January 4 report was a rest listing; January 5 gamebook confirms actual rest nonappearance. January 6 appearance is a return from rest, not an injury return or medical clearance.',
            'A09':'March 10 onset and subsequent individually documented injury-related absences reviewed through April 14. No return/clearance observed; season-end censoring. Repeated game-day out listings support a game-absence run, not every intervening day of medical unavailability.'}[c['case_id']]
        row=dict(case_id=c['case_id'],player_id=pid,player_name=c['name'],cohort_role='external_selected_case; excluded_from_pilot_denominator',onset_lower_date=c['onset'],onset_upper_date=c['onset'],onset_precision='day_interval_timezone_unverified' if c['onset'] else 'not_applicable',first_injury_missed_game=c['first_missed'] if first_verified else '',first_injury_missed_game_verified=first_verified,noninjury_absence_date=c['first_missed'] if c['case_id']=='A22' else '',first_public_report_at='',earliest_reviewed_evidence_source='phase1:'+original_sources[c['case_id']],medical_clearance_at='',activity_clearance_date='2024-03-12' if c['case_id']=='A04' else '',first_return_appearance_date=c['return_date'] if actual_return and c['case_id']!='A22' else '',noninjury_return_date=c['return_date'] if actual_return and c['case_id']=='A22' else '',last_observed_injury_absence=checks[-1]['game_date'] if complete_run else '',injury_game_run_count=aggregate if aggregate else injury_run if complete_run else '',expected_team_games_in_run=len(checks),individually_injury_verified_games=injury_run,primary_label=primary,secondary_label=secondary,onset_to_return_proxy_days=proxy if proxy is not None else '',proxy_definition='onset_date_to_first_return_date; not_medical_clearance' if proxy is not None else 'not_observed_or_not_applicable',label_known_at_primary='',label_known_at_secondary='',label_known_at_precision='original_evidence_availability_unverified; unavailable_for_historical_training',followup_censoring='season_end_no_return; no_offseason_extension' if c['case_id'] in {'A02','A09'} else 'closed_by_appearance' if actual_return else 'unknown',mechanism='unknown',episode_relation='possible_recurrence_or_continuation' if c['case_id'] in {'A01','A03','A04'} else 'documented_event_link; clinical_newness_unverified' if c['case_id']!='A22' else 'not_applicable_noninjury',continuity_and_identity_evidence=note,identity_source_ids=';'.join(sorted(set(id_sources))),reviewer='Codex source review (same agent as Phase 1); not independent human adjudication',reviewed_at=now(),unresolved_assertions='first_public_report; full_medical_clearance; original_publication_time'+('; continuous_medical_unavailability' if primary=='unknown' else ''))
        rows.append(row)
        for assertion,value,sid,locator in [
            ('stable_player_id',pid,id_sources[0],'__NEXT_DATA__.game team personId and name'),
            ('first_missed_game_reason',first['reason'] if first else '',first['source_id'] if first else '','FINAL BOX page 1 inactive list'),
            ('onset_date',c['onset'],'phase1:'+original_sources[c['case_id']],'injury/return narrative; day precision'),
            ('return_appearance',row['first_return_appearance_date'],next(('page_'+g['game_id'] for g in cg if g['game_date']==c['return_date']),''),'__NEXT_DATA__.game player minutes'),
            ('outcome_continuity_review',note,'phase1:'+original_sources[c['case_id']],'review in continuity_and_identity_evidence; claims not silently promoted to historical predictors')]:
            assertions.append(dict(case_id=c['case_id'],assertion=assertion,value=value,source_id=sid,evidence_locator=locator,original_publication_at='',publication_precision='unverified',evidence_role='retrospective_outcome_only',reviewer='Codex; no independent human review'))
        for check in checks:assertions.append(dict(case_id=c['case_id'],assertion='game_absence_attribution',value=check['reason'],source_id=check['source_id'],evidence_locator=check['evidence_locator']+'; game_date='+check['game_date'],original_publication_at='',publication_precision='unverified',evidence_role='retrospective_outcome_only',reviewer='Codex PDF extraction and consistency review'))
    write('case_audits.csv',rows);write('case_assertions.csv',assertions);write('case_game_evidence.csv',game_evidence)
    with (ROOT/'audit/candidates.csv').open() as f:original=list(csv.DictReader(f))
    queue=[];reviewed={r['case_id']:r for r in rows}
    for c in original:
        update=reviewed.get(c['candidate_id']);queue.append(dict(case_id=c['candidate_id'],player_name=c['player_name'],priority='high' if update else 'pending',independent_human_review='not_done',prior_reviewer=c['adjudicator'],phase1b_reviewer='Codex same agent; not independent' if update else 'not_reviewed_in_detail',review_task='Verify source assertions, primary medical-unavailability evidence, episode identity, publication precision; accept/amend/reject each label.' if update else 'Map stable ID and resolve onset, attribution, continuity and follow-up.',linked_table='case_audits.csv' if update else '../../audit/candidates.csv',user_decision='',user_notes=''))
    write('user_review_queue.csv',queue)
    injury=[r for r in rows if r['primary_label']!='excluded']
    summary=dict(selected_reviews=len(rows),injury_reviews=len(injury),independent_human_reviews=0,primary_resolved=sum(r['primary_label'] in {'positive','negative'} for r in injury),primary_resolved_fraction=sum(r['primary_label'] in {'positive','negative'} for r in injury)/len(injury),appearance_proxy_observed=sum(r['onset_to_return_proxy_days']!='' for r in injury),appearance_proxy_fraction=sum(r['onset_to_return_proxy_days']!='' for r in injury)/len(injury),secondary_resolved=sum(r['secondary_label'] in {'positive','negative'} for r in injury),primary_labels=dict(Counter(r['primary_label'] for r in rows)),secondary_labels=dict(Counter(r['secondary_label'] for r in rows)),full_medical_clearance_known=0,original_label_availability_verified=0)
    (ROOT/'pilot/case_audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':build()
