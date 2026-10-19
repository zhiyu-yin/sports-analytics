"""Review public absence blocks; do not assert clinical identity from similar diagnoses."""
from collections import defaultdict
from datetime import date,datetime,time,timedelta
import csv,json,re
from zoneinfo import ZoneInfo
from injury_warning.pilot_io import ROOT,read_source,manifest
from .logic import public_outcomes,confirmed_run_bounds


def rows(name):
    with (ROOT/'pilot/tables'/name).open() as f:return list(csv.DictReader(f))


def review():
    games=rows('player_games.csv');groups=defaultdict(list)
    for g in games:groups[g['player_id']].append(g)
    # Directly reviewed NBA/AP recap assertions. Injury during indexed game is
    # disqualifying under B only after end+6h, not a prospectively verified A source.
    events=[dict(event_id='new_ankle_20240125_204001',player_id='204001',onset_date='2024-01-25',source_id='page_0022300630',paragraph=3,site='ankle',side='left',note='New ankle sprain during the completed Miami game; explicit recap assertion.'),
            dict(event_id='new_ankle_20240214_204001',player_id='204001',onset_date='2024-02-14',source_id='page_0022300780',paragraph=7,site='ankle',side='unknown',note='Ankle sprain during completed Brooklyn game; player reported second-half availability. New in-game injury still disqualifies this indexing row.')]
    episodes=[];members=[]
    for pid,logs in groups.items():
        logs.sort(key=lambda r:(r['game_date'],r['game_id']));block=[]
        def flush(return_row):
            nonlocal block
            injury=[r for r in block if r['absence_category']=='injury']
            if not injury:block=[];return
            first=injury[0];last=injury[-1];d=first['game_date'];left_censored=(block[0]['game_id']==logs[0]['game_id']);ret=return_row['game_date'] if return_row else None
            after_first=[r for r in block if r['game_date']>=d]
            # A public absence block is only a candidate envelope. Multiple symptoms,
            # nonspecific Injury/Illness, assignment, rest or unknown rows remain mixed.
            reasons={r['nonappearance_reason'] for r in injury};sole=all(r['absence_category']=='injury' for r in after_first)
            explicit=next((e for e in events if pid==e['player_id'] and e['onset_date']<=d and (date.fromisoformat(d)-date.fromisoformat(e['onset_date'])).days<=3),None)
            clinical_supported=bool(explicit and sole and all('Left Ankle' in r['nonappearance_reason'] for r in injury))
            lower,upper=confirmed_run_bounds([dict(category=r['absence_category'],appeared=False,same_episode_supported=clinical_supported) for r in after_first],bool(ret))
            if left_censored:upper=None
            span_upper=(date.fromisoformat(ret)-date.fromisoformat(d)).days if ret and not left_censored else None
            span_lower=(date.fromisoformat(last['game_date'])-date.fromisoformat(d)).days if clinical_supported else None
            prim,sec=public_outcomes(run_lower=lower,run_upper=upper,span_lower=span_lower,span_upper=span_upper,continuity_supported=clinical_supported)
            eid='bos_block_'+pid+'_'+d.replace('-','')
            lo=hi=None
            if explicit:
                lo=explicit['onset_date']+'T00:00:00-05:00';hi=explicit['onset_date']+'T23:59:59.999999-05:00'
            else:hi=d+'T23:59:59.999999'+('-04:00' if d>='2024-03-10' else '-05:00')
            # Censor at a transfer or collection end; never continue another team's schedule.
            censor='none' if ret else 'loss_of_followup_or_season_end'
            sourceids=sorted({r['source_id'] for r in after_first}|{r['reason_source_id'] for r in after_first}|({return_row['source_id']} if return_row else set())|({explicit['source_id']} if explicit else set()))
            ep=dict(episode_id=eid,player_id=pid,player_name=first['player_name'],record_type='reviewed_absence_block_candidate',first_injury_missed_game='' if left_censored else d,first_observed_Boston_injury_missed_game=d,left_censored_start=left_censored,last_documented_injury_missed_game=last['game_date'],first_return_appearance=ret or '',onset_lower=lo,onset_upper=hi,onset_source_id=explicit['source_id'] if explicit else first['reason_source_id'],onset_evidence_locator='story.content['+str(explicit['paragraph'])+']' if explicit else 'first observed injury absence bounds latest possible onset only',continuity_evidence_locator='page_0022300670 story.content[13] explicitly links two-game ankle absence to return' if clinical_supported else 'clinical continuity unresolved; complete game sequence supplies conservative severity upper bounds',onset_precision='whole_day_interval' if lo else 'lower_unknown_upper_bound_only_not_first_miss_as_onset',injury_reasons=';'.join(sorted(reasons)),body_site=';'.join(sorted({r.split('Injury/Illness -',1)[-1].split(';')[0].strip() for r in reasons if 'Injury/Illness -' in r})) or 'unknown',body_side='left' if all('Left' in x for x in reasons) else 'right' if all('Right' in x for x in reasons) else 'unknown_or_mixed',clinical_episode_identity='explicit_event_link_and_uninterrupted_attribution' if clinical_supported else 'unresolved_candidate_envelope_not_a_new_injury_count',continuity_supported=clinical_supported,confirmed_same_episode_run_lower=lower,possible_game_run_upper=upper,public_span_lower_days=span_lower,public_span_upper_days=span_upper,public_span_proxy_days=span_upper if sole else None,primary_ge10=prim,secondary_public_gt28=sec,original_medical_gt28='negative' if explicit and span_upper is not None and (date.fromisoformat(ret)-date.fromisoformat(explicit['onset_date'])).days<=28 else 'unknown',censoring='left_censored_history_or_prior_team; '+censor if left_censored else censor,source_ids=';'.join(sourceids),evidence_category='C_retrospective_outcome_review',historical_label_known_at='',historical_label_time_precision='unknown',reviewer='Codex same agent; not independent human adjudication',review_note='Complete team-game sequence bounds potential severity. A closed block shorter than 10 games / 29 days bounds every candidate within it, even if onset or clinical grouping is unresolved. Mixed or censored long blocks stay unknown. No healthy status inferred from a later return.')
            episodes.append(ep)
            for r in injury:members.append(dict(episode_id=eid,player_id=pid,game_id=r['game_id'],game_date=r['game_date'],source_id=r['source_id'],reason_source_id=r['reason_source_id'],reason=r['nonappearance_reason'],phase=r['phase'],evidence_locator=r['evidence_locator']))
            block=[]
        for r in logs:
            if r['appeared']=='True':flush(r)
            else:block.append(r)
        flush(None)
    # Explicit February 14 event had no documented consecutive injury absence before
    # first later appearance: keep it separately, not merged into unrelated diagnoses.
    e=events[1];logs=sorted(groups[e['player_id']],key=lambda r:r['game_date']);ret=next(r for r in logs if r['game_date']>e['onset_date'] and r['appeared']=='True')
    episodes.append(dict(episode_id=e['event_id'],player_id=e['player_id'],player_name='Kristaps Porzingis',record_type='documented_in_game_event_without_injury_missed_run',first_injury_missed_game='',first_observed_Boston_injury_missed_game='',left_censored_start=False,last_documented_injury_missed_game='',first_return_appearance=ret['game_date'],onset_lower=e['onset_date']+'T00:00:00-05:00',onset_upper=e['onset_date']+'T23:59:59.999999-05:00',onset_source_id=e['source_id'],onset_evidence_locator='story.content[7]',continuity_evidence_locator='explicit game event; no injury-missed run recorded before next appearance',onset_precision='whole_day_interval',injury_reasons='sprained ankle during game',body_side='unknown',body_site='ankle',clinical_episode_identity='explicit_in_game_event',continuity_supported=True,confirmed_same_episode_run_lower=0,possible_game_run_upper=0,public_span_lower_days=0,public_span_upper_days=0,public_span_proxy_days=None,primary_ge10='negative',secondary_public_gt28='negative',original_medical_gt28='negative',censoring='none',source_ids=e['source_id']+';'+ret['source_id'],evidence_category='C_retrospective_outcome_review',historical_label_known_at='',historical_label_time_precision='unknown',reviewer='Codex same agent; not independent human adjudication',review_note='No recorded injury-attributed missed game before next appearance; no first-missed-game span invented.'))
    return episodes,members,events
