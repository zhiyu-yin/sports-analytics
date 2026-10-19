"""Point-in-time conservative longitudinal normalization for the registered pilot."""
from datetime import datetime,timedelta,date,time
from zoneinfo import ZoneInfo
import json,re,unicodedata
from .rules import utc


def canonical(name):
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower())


def resolve_name(name,players):
    """Never choose the first duplicate name. Returns None for missing or ambiguous."""
    key=canonical(name)
    matches={str(p['player_id']) for p in players if key in {canonical(p['player_name']),canonical(p['family_name']+', '+p['first_name']),canonical(p['family_name'])}}
    return next(iter(matches)) if len(matches)==1 else None


def parse_game_page(body):
    m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',body.decode(),re.S)
    if not m:raise ValueError('Missing historical game JSON')
    p=json.loads(m[1])['props']['pageProps']
    if not str(p['game']['gameId']).startswith('00223'):raise ValueError('Non-development game')
    return p['game'],p.get('playByPlay',{}).get('actions',[])


def minutes(value):
    if value in ('',None):return None
    m=re.fullmatch(r'(\d+):(\d\d)',value)
    if not m or int(m[2])>60:raise ValueError('Malformed minutes')
    return round(int(m[1])+int(m[2])/60,6)


def absence_category(reason):
    text=reason.lower().strip()
    if not text:return 'unknown'
    medical=text.split('injury/illness',1)[-1].strip(' -')
    if 'illness' in medical or 'respiratory' in medical:return 'illness'
    if text=='rest' or text.endswith(' - rest'):return 'rest'
    if 'suspension' in text:return 'suspension'
    if 'personal' in text:return 'personal'
    if 'coach' in text:return 'coaching'
    if 'g league' in text or 'gleague' in text:return 'assignment'
    if 'injury/illness' in text or 'concussion' in text:return 'injury'
    return 'unknown'


def member_on(day,entry_lower,entry_upper,exit_lower=None,exit_upper=None):
    """Date-level entry inclusive, exit exclusive. Uncertain transaction day stays unknown."""
    if day < entry_lower or (exit_upper and day>=exit_upper):return 'not_member'
    if day < entry_upper or (exit_lower and day>=exit_lower):return 'unknown'
    return 'member'


def end_minute(actions,game_date):
    ends=[a for a in actions if a.get('actionType')=='period' and a.get('subType')=='end']
    if not ends:return None,None,''
    last=max(ends,key=lambda a:(a['period'],a.get('actionNumber',0)))
    m=re.search(r'\((\d{1,2}:\d\d\s*[AP]M)\s+(EST|EDT|CST|CDT|MST|MDT|PST|PDT)\)',last.get('description',''))
    if not m:return None,None,last.get('description','')
    zones={'EST':'America/New_York','EDT':'America/New_York','CST':'America/Chicago','CDT':'America/Chicago','MST':'America/Denver','MDT':'America/Denver','PST':'America/Los_Angeles','PDT':'America/Los_Angeles'}
    clock=datetime.strptime(m[1].replace(' ','') ,'%I:%M%p').time()
    dt=datetime.combine(date.fromisoformat(game_date),clock,tzinfo=ZoneInfo(zones[m[2]]))
    # Midnight event clocks can lie on next date; afternoon/evening regular-season starts.
    if dt.hour<6:dt+=timedelta(days=1)
    return dt.isoformat(),(dt+timedelta(minutes=1)).isoformat(),last['description']


def later_noon(game_date):
    return datetime.combine(date.fromisoformat(game_date)+timedelta(days=1),time(12),tzinfo=ZoneInfo('America/New_York')).isoformat()


def point_status(observation,decision_at,*,require_verified_publication=True):
    if not observation:return 'unknown','no_postgame_positive_availability_evidence'
    if observation['report_at'] is None or utc(observation['report_at'])>utc(decision_at):return 'unknown','future_or_undated_observation'
    if observation.get('target_game_date') and observation['target_game_date'] < utc(decision_at).astimezone(ZoneInfo('America/New_York')).date().isoformat():
        return 'unknown','listing_for_already_completed_game'
    if require_verified_publication and observation.get('publication_verified') is not True:return 'unknown','original_public_availability_unverified'
    value=observation['status'].lower()
    category=absence_category(observation.get('reason',''))
    if category in {'rest','illness','suspension','personal','coaching','assignment'}:return 'excluded_noninjury','documented_'+category
    if value=='out' and category=='injury':return 'unavailable','documented_injury_out'
    if value=='available':return 'available','explicit_available_listing'
    return 'unknown','status_not_explicit_available_or_injury_out'


def report_player_state(report_state,listed):
    if report_state!='complete':return report_state
    return 'listed' if listed else 'absent_from_complete_report'
