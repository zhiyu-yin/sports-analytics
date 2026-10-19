"""Versioned Phase 1C operational rules, separate from preserved original endpoints."""
from datetime import datetime,date,time,timedelta,timezone
from zoneinfo import ZoneInfo
from injury_warning.rules import utc,future_window


def add_elapsed(value,days=0,hours=0,minutes=0):
    return (utc(value).astimezone(timezone.utc)+timedelta(days=days,hours=hours,minutes=minutes)).isoformat()


def decision(game_date,extra_day=0):
    return datetime.combine(date.fromisoformat(game_date)+timedelta(days=1+extra_day),time(12),tzinfo=ZoneInfo('America/New_York')).isoformat()


def ordering(end_upper,decision_at):
    return bool(end_upper and utc(end_upper)<utc(decision_at))


def in_window(t,lo,hi):
    return future_window(t,lo,hi)


def eligibility(*,appeared,member,time_ordered,covered,explicit_disqualifiers,verified=False):
    if not appeared:return 'not_in_population','no_positive_minutes'
    if not member:return 'unknown','membership_unresolved'
    if not time_ordered:return 'unknown','game_end_ordering_unresolved'
    if explicit_disqualifiers:return 'excluded',';'.join(explicit_disqualifiers)
    if not covered:return 'unknown','searched_source_coverage_insufficient' if not verified else 'verified_publication_coverage_insufficient'
    return 'included','no_known_disqualifying_report_under_registered_search'


def confirmed_run_bounds(rows,closed):
    """Rows cover every team game in an observed absence block, in date order.

    Never count noninjury/mixed absences as injury games. Bounds above a confirmed
    streak remain uncertain until resolution; a single diagnosis is not an episode link.
    """
    streak=best=0
    for r in rows:
        if r.get('appeared'):
            raise ValueError('Return belongs outside the absence block')
        if r['category']=='injury' and r.get('same_episode_supported',False):streak+=1;best=max(best,streak)
        else:streak=0
    upper=len(rows) if closed else None
    return best,upper


def public_outcomes(*,run_lower,run_upper,span_lower,span_upper,continuity_supported):
    primary='positive' if run_lower>=10 and continuity_supported else 'negative' if run_upper is not None and run_upper<10 else 'unknown'
    secondary='positive' if span_lower is not None and span_lower>28 and continuity_supported else 'negative' if span_upper is not None and span_upper<=28 else 'unknown'
    return primary,secondary


def row_outcome(decision_at,episodes,endpoint,*,surveillance,followup,transferred=False):
    uncertain=False;links=[];prevalent=[]
    for e in episodes:
        status=e[endpoint]
        if e.get('onset_upper') and utc(e['onset_upper'])<=utc(decision_at):
            ret=e.get('first_return_appearance')
            if not ret or ret>=utc(decision_at).date().isoformat():prevalent.append(e['episode_id'])
            continue
        if status=='negative':continue
        membership=in_window(decision_at,e.get('onset_lower'),e.get('onset_upper'))
        if membership is False:continue
        links.append(e['episode_id'])
        if status=='positive' and membership is True:return 'positive',links,prevalent
        uncertain=True
    if not surveillance or not followup or transferred or uncertain:return 'unknown',links,prevalent
    return 'negative',links,prevalent


def features(logs,decision_at,*,history_complete,baseline_complete):
    """Only completed and publication-eligible records; elapsed UTC windows, past-only baseline."""
    t=utc(decision_at).astimezone(timezone.utc)
    eligible=[g for g in logs if g.get('end_upper') and g.get('assumed_available_at') and
              t-timedelta(days=28)<utc(g['end_upper']).astimezone(timezone.utc)<=t and utc(g['assumed_available_at'])<=t]
    out={}
    for days in (7,14,28):
        vals=[g for g in eligible if t-timedelta(days=days)<utc(g['end_upper']).astimezone(timezone.utc)<=t]
        out[f'minutes_{days}d']=round(sum(g['minutes'] for g in vals),4) if history_complete else None
        out[f'appearances_{days}d']=sum(g['minutes']>0 for g in vals) if history_complete else None
    prev=[g for g in eligible if t-timedelta(days=14)<utc(g['end_upper']).astimezone(timezone.utc)<=t-timedelta(days=7)]
    out['minutes_prior_7d']=round(sum(g['minutes'] for g in prev),4) if history_complete else None
    out['workload_change_7d']=round(out['minutes_7d']-out['minutes_prior_7d'],4) if history_complete else None
    played=[g for g in eligible if g['minutes']>0]
    last=max(played,key=lambda g:utc(g['end_upper'])) if played else None
    out['rest_elapsed_days_since_appearance']=round((t-utc(last['end_upper']).astimezone(timezone.utc)).total_seconds()/86400,5) if last and history_complete else None
    lastteam=max(eligible,key=lambda g:utc(g['end_upper'])) if eligible else None
    out['rest_elapsed_days_since_team_game']=round((t-utc(lastteam['end_upper']).astimezone(timezone.utc)).total_seconds()/86400,5) if lastteam and history_complete else None
    prior_baseline=[g for g in played if last and utc(g['end_upper'])<utc(last['end_upper']) and utc(g['end_upper'])>t-timedelta(days=28)]
    out['baseline_prior_appearance_count']=len(prior_baseline)
    out['past_mean_minutes_per_appearance']=round(sum(g['minutes'] for g in prior_baseline)/len(prior_baseline),4) if prior_baseline and baseline_complete else None
    out['last_minutes_deviation']=round(last['minutes']-out['past_mean_minutes_per_appearance'],4) if last and out['past_mean_minutes_per_appearance'] is not None else None
    out['input_game_ids']=';'.join(g['game_id'] for g in eligible)
    out['max_input_assumed_available_at']=max((g['assumed_available_at'] for g in eligible),key=utc,default=None)
    return out
