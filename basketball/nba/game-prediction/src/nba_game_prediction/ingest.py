"""Acquire one season once; preserve response text and validate cache provenance."""
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import time
from uuid import uuid4
from .seasons import get_scope

SEASON = '2023-24'
SEASON_TYPE = 'Regular Season'
PARAMETERS = {
    'Counter': 0, 'Direction': 'ASC', 'LeagueID': '00', 'PlayerOrTeam': 'T',
    'Season': SEASON, 'SeasonType': SEASON_TYPE, 'Sorter': 'DATE',
    'DateFrom': '', 'DateTo': '',
}
REQUIRED = {
    'SEASON_ID', 'TEAM_ID', 'TEAM_NAME', 'TEAM_ABBREVIATION',
    'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'PTS',
}


def extract_table(body):
    obj = json.loads(body)
    sets = obj['resultSets']
    table = next(s for s in sets if s['name'] == 'LeagueGameLog')
    columns, rows = table['headers'], table['rowSet']
    if len(columns) != len(set(columns)) or not REQUIRED.issubset(columns):
        raise ValueError('Missing/duplicate required source columns')
    if not rows or any(len(row) != len(columns) for row in rows):
        raise ValueError('Empty response or malformed source row widths')
    return columns, rows


def parameters_for(season):
    from .sealed_access import require_seasons
    require_seasons([season], 'raw outcomes')
    get_scope(season)
    return dict(PARAMETERS, Season=season)


def read_cache(raw_dir, *, season=SEASON):
    """No silent repair or network fallback when an existing cache is corrupt."""
    expected_parameters = parameters_for(season)
    manifests = sorted(Path(raw_dir).glob('leaguegamelog_full_*.manifest.json'))
    valid = []
    for path in manifests:
        meta = json.loads(path.read_text())
        if meta['parameters'] != expected_parameters:
            raise ValueError(f'Unexpected full-season cache parameters: {path}')
        if meta['endpoint'] != 'LeagueGameLog' or meta['http_status'] != 200:
            raise ValueError(f'Unexpected cache endpoint/status: {path}')
        body_path = path.parent / meta['raw_file']
        if body_path.parent.resolve() != path.parent.resolve():
            raise ValueError('Raw cache path escapes its directory')
        body = body_path.read_bytes()
        if sha256(body).hexdigest() != meta['sha256']:
            raise ValueError(f'Raw cache checksum mismatch: {body_path}')
        columns, rows = extract_table(body)
        if meta['row_count'] != len(rows) or meta['columns'] != columns:
            raise ValueError('Cached row count/schema mismatch')
        valid.append((body, meta))
    if not valid:
        return None
    if len({m['sha256'] for _, m in valid}) != 1:
        raise ValueError('Conflicting full-season snapshots; explicitly reconcile before use')
    return valid[0]


def retrieve(raw_dir, *, allow_network=False, season=SEASON):
    from .sealed_access import require_seasons
    require_seasons([season], 'raw outcomes')
    get_scope(season)  # Before cache/network.
    cached = read_cache(raw_dir, season=season)
    if cached:
        return (*cached, True)
    if not allow_network:
        raise FileNotFoundError('No valid full-season cache. Explicit --fetch is required.')
    from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    token = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid4().hex[:8]
    client = LeagueGameLog(
        counter=0, direction='ASC', league_id='00', player_or_team_abbreviation='T',
        season=season, season_type_all_star=SEASON_TYPE, sorter='DATE',
        date_from_nullable='', date_to_nullable='', timeout=30, get_request=False,
    )
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    error = None
    try:
        client.get_request()
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    meta = {
        'source': 'NBA Stats via maintained nba_api client', 'endpoint': 'LeagueGameLog',
        'parameters': client.parameters, 'season': season, 'season_type': SEASON_TYPE,
        'retrieval_started_utc': started,
        'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
        'runtime_seconds': round(time.monotonic() - clock, 3),
        'nba_api_version': version('nba_api'), 'http_status': None,
        'error': error, 'row_count': None, 'columns': None,
    }
    response = client.nba_response
    if response is not None:
        # Original response text exposed by nba_api, UTF-8 encoded; not reserialized.
        body = response.get_response().encode('utf-8')
        digest = sha256(body).hexdigest()
        filename = f'leaguegamelog_full_{token}_{digest}.json'
        with (raw_dir / filename).open('xb') as f:
            f.write(body)
        meta.update(raw_file=filename, sha256=digest, http_status=response._status_code,
                    url=response.get_url(), raw_bytes=len(body))
        try:
            columns, rows = extract_table(body)
            meta.update(columns=columns, row_count=len(rows))
        except Exception as exc:
            meta['error'] = {'type': type(exc).__name__, 'message': str(exc)}
    valid = meta['error'] is None and meta['http_status'] == 200 and meta['row_count']
    suffix = '.manifest.json' if valid else '.failure.json'
    with (raw_dir / f'leaguegamelog_full_{token}{suffix}').open('x') as f:
        json.dump(meta, f, indent=2)
        f.write('\n')
    if not valid:
        raise RuntimeError(f'NBA retrieval failed; evidence saved in {raw_dir}; stop ingestion')
    return body, meta, False
