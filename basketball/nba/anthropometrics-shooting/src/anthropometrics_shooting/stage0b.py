"""Eligibility and measurement selection only. No statistical association routines."""
import math
from .normalize import number,player_id
QUARANTINE={('1629655',2019),('1629672',2019),('1629675',2019),('1629023',2019)}
def positive_id(value):
    try:return player_id(value)
    except (ValueError,TypeError):return None

def complete(r):
    h=number(r.get('HEIGHT_WO_SHOES')); w=number(r.get('WINGSPAN'))
    return h is not None and w is not None and 60<=h<=96 and 60<=w<=108

def measurement_reasons(r):
    issues=[]; h=number(r.get('HEIGHT_WO_SHOES')); w=number(r.get('WINGSPAN'))
    if h is None:issues.append('missing_height')
    elif not 60<=h<=96:issues.append('implausible_height')
    if w is None:issues.append('missing_wingspan')
    elif not 60<=w<=108:issues.append('implausible_wingspan')
    if (str(r['PLAYER_ID']),int(r['SEASON'])) in QUARANTINE:issues.append('unresolved_measurement_conflict')
    return issues

def select_measurement(rows,cutoff=2013):
    prior=[r for r in rows if int(r['SEASON'])<=cutoff]
    good=[r for r in prior if not measurement_reasons(r)]
    if good:
        latest=max(int(r['SEASON']) for r in good)
        chosen=[r for r in good if int(r['SEASON'])==latest]
        if len(chosen)!=1: return None,['duplicate_measurement_record']
        return chosen[0],[]
    if not prior:return None,['post-season-only measurement'] if rows else ['no_combine_record']
    return None,sorted({reason for r in prior for reason in measurement_reasons(r)})

def valid_counts(m,a):
    return m is not None and a is not None and math.isfinite(m) and math.isfinite(a) and m>=0 and a>=0 and int(m)==m and int(a)==a and m<=a

def eligibility(nba,combine_rows,identity_conflict=False):
    reasons=[]
    pid=positive_id(nba.get('player_id'))
    exact=[r for r in combine_rows if positive_id(r.get('PLAYER_ID'))==pid] if pid else []
    if not pid:reasons.append('invalid_player_id')
    # Exact ID has priority even if another person's normalized name collides.
    measurement,why=select_measurement(exact)
    if not exact and identity_conflict: reasons.append('unresolved_identity_conflict')
    else: reasons+=why
    if nba.get('seconds',0)<=0:reasons.append('no_positive_minutes')
    if not valid_counts(nba.get('FTM'),nba.get('FTA')):reasons.append('invalid_ft_counts')
    if not valid_counts(nba.get('FG3M'),nba.get('FG3A')):reasons.append('invalid_3p_counts')
    return measurement,sorted(set(reasons))

def validate_frozen(rows):
    ids=[r['player_id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate frozen player_id')
    for r in rows:
        if r['combine_year']>2013:raise ValueError('Post-season measurement')
        if r['season']!='2013-14' or r['join_status']!='exact ID':raise ValueError('Invalid population')
        if not positive_id(r['player_id']):raise ValueError('Invalid ID')
        if not valid_counts(r['ftm'],r['fta']):raise ValueError('Invalid FT counts')
        if not valid_counts(r['fg3m'],r['fg3a']):raise ValueError('Invalid 3P counts')
        if not 60<=r['height_wo_shoes_inches']<=96 or not 60<=r['wingspan_inches']<=108:raise ValueError('Invalid measurements')
        if (str(r['player_id']),r['combine_year']) in QUARANTINE:raise ValueError('Quarantined measurement')
        if r['binomial_likelihood_eligible']!=(r['fta']>0):raise ValueError('Invalid likelihood flag')
        if r['minutes']<=0:raise ValueError('Nonpositive minutes')
    return True
