"""Pure functions: unknown evidence stays unknown; no source access here."""
from datetime import datetime, timedelta


def utc(value):
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('Timezone-aware timestamps required')
    return value


def future_window(prediction_at, onset_lower, onset_upper):
    """Tri-state membership in (t, t+14d]; bounds are inclusive."""
    t = utc(prediction_at)
    if onset_lower is None or onset_upper is None:
        return None
    lo, hi = utc(onset_lower), utc(onset_upper)
    if lo > hi:
        raise ValueError('Reversed onset bounds')
    if hi <= t or lo > t + timedelta(days=14):
        return False
    if lo > t and hi <= t + timedelta(days=14):
        return True
    return None


def severity(*, injury_related, excluded_reason=False, days_lower=None,
             days_upper=None, consecutive_games_lower=None,
             consecutive_games_upper=None):
    """Bounds must cover continuously evidenced injury unavailability, not projections."""
    for lo, hi in [(days_lower, days_upper),
                   (consecutive_games_lower, consecutive_games_upper)]:
        if (lo is not None and lo < 0) or (hi is not None and hi < 0):
            raise ValueError('Negative duration')
        if lo is not None and hi is not None and lo > hi:
            raise ValueError('Reversed severity bounds')
    if excluded_reason:
        return {'primary': 'excluded', 'secondary': 'excluded'}
    if injury_related is not True:
        return {'primary': 'unknown', 'secondary': 'unknown'}
    primary = ('positive' if days_lower is not None and days_lower > 28 else
               'negative' if days_upper is not None and days_upper <= 28 else 'unknown')
    secondary = ('positive' if consecutive_games_lower is not None and consecutive_games_lower >= 10 else
                 'negative' if consecutive_games_upper is not None and consecutive_games_upper < 10 else 'unknown')
    return {'primary': primary, 'secondary': secondary}


def risk_eligible(prediction_at, game_ended_at, status, status_known_at, season_type):
    if season_type != 'Regular Season' or status != 'available' or status_known_at is None:
        return False
    return utc(game_ended_at) <= utc(prediction_at) and utc(status_known_at) <= utc(prediction_at)


def group_reports(reports):
    """Only adjudicated episode IDs merge. Diagnosis/name proximity never merges reports."""
    grouped = {}
    for r in reports:
        if not r.get('episode_id') or not r.get('player_id'):
            raise ValueError('Adjudicated episode ID and stable player ID required')
        key = (r['player_id'], r['episode_id'])
        grouped.setdefault(key, []).append(r)
    return grouped


FEATURES = frozenset({'age', 'position', 'nba_experience', 'prior_injury_count',
    'minutes_7d', 'minutes_14d', 'minutes_28d', 'appearances_7d', 'appearances_14d',
    'appearances_28d', 'workload_change', 'consecutive_appearances', 'back_to_back',
    'rest_days', 'past_baseline_deviation', 'public_symptoms'})


def validate_features(features, prediction_at, *, symptom_informed=False):
    """Each feature carries the latest public time of every input and baseline observation."""
    t = utc(prediction_at)
    for name, record in features.items():
        if name not in FEATURES or (name == 'public_symptoms' and not symptom_informed):
            raise ValueError('Forbidden feature: ' + name)
        if record.get('evidence_role') != 'predictor':
            raise ValueError('Retrospective outcome evidence cannot be a predictor')
        if utc(record['max_input_known_at']) > t:
            raise ValueError('Future feature input')


def training_row_allowed(*, prediction_at, window_end, label_known_at, cutoff,
                         episode_id, evaluation_episode_ids=()):
    if label_known_at is None:
        return False
    t, end, known, cut = map(utc, [prediction_at, window_end, label_known_at, cutoff])
    if end != t + timedelta(days=14):
        raise ValueError('Incorrect horizon')
    return t < cut and end < cut and known <= cut and episode_id not in evaluation_episode_ids


def cohort_label(*, eligible, event_results, complete_onset_surveillance):
    """event_results contains (window membership, outcome severity) for each candidate."""
    if not eligible:
        return 'excluded'
    if any(w is True and s == 'positive' for w, s in event_results):
        return 'positive'
    if not complete_onset_surveillance or any(w is None or (w is True and s == 'unknown')
                                            for w, s in event_results):
        return 'unknown'
    return 'negative'


def normalize_status(value, reason):
    """Conservative snapshot normalization. Not-listed is never assumed healthy."""
    reason = reason.strip().lower()
    if reason in {'rest', 'league suspension', 'personal reasons'} or 'illness' == reason:
        return 'excluded_noninjury'
    if value.strip().lower() == 'available':
        return 'available'
    if value.strip().lower() == 'out':
        return 'unavailable'
    return 'unknown'


def workload(logs, prediction_at, days):
    """Closed trailing (t-days,t] window; actual game-end AND publication must be known."""
    if days not in (7, 14, 28):
        raise ValueError('Unsupported window')
    t = utc(prediction_at)
    valid = [g for g in logs if utc(g['known_at']) <= t and
             t-timedelta(days=days) < utc(g['game_ended_at']) <= t]
    keys = [g['game_id'] for g in valid]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate player-game logs')
    if any(g['minutes'] < 0 for g in valid):
        raise ValueError('Negative minutes')
    return {'minutes': sum(g['minutes'] for g in valid), 'appearances': len(valid)}


def onset_day_interval(day, timezone_name):
    """Expand a supported local event date, preserving whole-day timing uncertainty."""
    from datetime import date, time
    from zoneinfo import ZoneInfo
    d = date.fromisoformat(day)
    zone = ZoneInfo(timezone_name)
    lo = datetime.combine(d, time.min, tzinfo=zone)
    hi = datetime.combine(d + timedelta(days=1), time.min, tzinfo=zone) - timedelta(microseconds=1)
    return lo.isoformat(), hi.isoformat()


def active_calendar_days(start, end, active_start, active_end, *, continuity_confirmed):
    """Date-only continuous unavailability; refuse unsupported offseason extension.

    Boundaries are local dates in an already adjudicated common timezone.
    active_end is exclusive; evidence across multiple active intervals needs adjudication.
    """
    from datetime import date
    start, end, a, b = map(date.fromisoformat, [start, end, active_start, active_end])
    if end < start or b < a:
        raise ValueError('Reversed dates')
    if not continuity_confirmed or start < a or end > b:
        return None
    return (end - start).days
