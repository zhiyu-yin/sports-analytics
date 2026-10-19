"""Separate clinical-event and observable absence-run onset targets."""
from datetime import datetime,date,time,timedelta
from zoneinfo import ZoneInfo
from injury_warning.rules import utc
from phase1c.logic import in_window,add_elapsed

def day_bounds(day):
    d=date.fromisoformat(day);z=ZoneInfo('America/New_York')
    return datetime.combine(d,time.min,z).isoformat(),(datetime.combine(d+timedelta(days=1),time.min,z)-timedelta(microseconds=1)).isoformat()

def membership(t,lo,hi):
    # A single finite bound can prove exclusion; it cannot prove inclusion.
    if hi and utc(hi)<=utc(t):return False
    if lo and utc(lo)>utc(add_elapsed(t,days=14)):return False
    return in_window(t,lo,hi)

def label_events(t,events,anchor,*,coverage=True,followup=True):
    """No clinical bounds are derived from appearances. Explicit evidence supplies them.

    Unknown severity cannot affect a window if its *selected endpoint* anchor is
    definitely outside. A demonstrated event positive does not need negative surveillance.
    """
    links=[];uncertain=False
    for e in events:
        relation=membership(t,e.get(anchor+'_lower') or None,e.get(anchor+'_upper') or None)
        if relation is False or e['severity']=='negative':continue
        links.append(e['event_id'])
        if relation is True and e['severity']=='positive' and e.get('continuity_supported') is True:return 'positive',links
        uncertain=True
    return ('unknown' if uncertain or not coverage or not followup else 'negative'),links

def absence_runs(logs):
    """Complete applicable-team game sequence. Never infer injury from nonappearance."""
    result=[];block=[];ordered=sorted(logs,key=lambda r:(r['game_date'],r['game_id']))
    def flush(ret):
        nonlocal block
        inj=[r for r in block if r['category']=='injury']
        ambiguous=[r for r in block if r['category']=='unknown']
        if not inj and not ambiguous:block=[];return
        first=min(inj+ambiguous,key=lambda r:(r['game_date'],r['game_id']));tail=[r for r in block if r['game_date']>=first['game_date']]
        lo,hi=first.get('anchor_lower'),first.get('anchor_upper')
        if not lo or not hi:lo,hi=day_bounds(first['game_date'])
        complete=all(r.get('roster_observed',True) and r.get('coverage','page_and_book')=='page_and_book' for r in tail)
        left_censored=bool(ordered and first['game_id']==ordered[0]['game_id'])
        if left_censored:lo=None
        upper=len(tail) if ret and complete and not left_censored else None
        result.append(dict(event_id='run_'+first['player_id']+'_'+first['game_id'],player_id=first['player_id'],run_lower=lo,run_upper=hi,anchor_game_id=first['game_id'],anchor_date=first['game_date'],anchor_attribution=first['category'],left_censored_start=left_censored,anchor_precision='first_observed_game_only; true_start_left_censored' if left_censored else first.get('anchor_precision','documented_game_date_ET_whole_day_interval; actual_start_not_asserted'),clinical_lower=None,clinical_upper=hi,severity='negative' if upper is not None and upper<10 else 'unknown',continuity_supported=False,confirmed_same_episode_games=0,possible_run_upper=upper,observed_games=len(tail),return_game_id=ret['game_id'] if ret else '',return_date=ret['game_date'] if ret else '',mixed_reasons=any(r['category']!='injury' for r in tail),game_ids=';'.join(r['game_id'] for r in tail),source_ids=';'.join(sorted({r['reason_source'] for r in tail}|{r['page_source'] for r in tail})),reason='closed complete run bounds severity below 10' if upper is not None and upper<10 else 'censored, mixed, incomplete or common episode attribution unresolved'))
        block=[]
    for r in ordered:
        if r['appeared'] is True:flush(r)
        else:block.append(r)
    flush(None);return result

def applicable_schedule(boston,destination,departure):
    return sorted([r for r in boston if r['game_date']<departure]+[r for r in destination if r['game_date']>=departure],key=lambda r:(r['game_date'],r['game_id']))
