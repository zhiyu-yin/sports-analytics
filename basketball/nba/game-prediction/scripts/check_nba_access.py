"""Bounded Stage 1A access gate. No headers/proxies are overridden.

Default reruns show prior evidence without network access. --retry-live explicitly
requests a fresh check after an access change. Never fetches other seasons.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
import time
from uuid import uuid4

from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nba_game_prediction.sealed_access import install
install()
EVIDENCE = ROOT / 'docs' / 'stage1a_evidence'
RAW = ROOT / 'data' / 'raw' / '2023-24'


def write_new(path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retry-live', action='store_true')
    args = parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    previous = sorted(EVIDENCE.glob('*/attempt_*.json'))
    if previous and not args.retry_live:
        print('Prior evidence exists; no network request made. Use --retry-live only after an access change.')
        for path in previous:
            print(path.relative_to(ROOT), json.loads(path.read_text())['result'])
        return 0
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid4().hex[:8]
    run = EVIDENCE / run_id
    run.mkdir()
    write_new(run / 'environment.json', {
        'python': sys.version, 'executable': sys.executable,
        'platform': platform.platform(),
        'versions': {p: version(p) for p in ['nba_api','pandas','numpy','pyarrow','requests']},
        'headers': 'Maintained nba_api defaults; no custom headers or proxy supplied',
    })
    success = 0
    for attempt in (1, 2):
        endpoint = LeagueGameLog(
            season='2023-24', season_type_all_star='Regular Season',
            league_id='00', player_or_team_abbreviation='T',
            counter=0, direction='ASC', sorter='DATE',
            date_from_nullable='10/24/2023', date_to_nullable='10/25/2023',
            timeout=20, get_request=False,
        )
        record = {
            'attempt': attempt, 'endpoint': 'LeagueGameLog',
            'base_url': 'https://stats.nba.com/stats/leaguegamelog',
            'parameters': endpoint.parameters, 'season': '2023-24',
            'season_type': 'Regular Season',
            'retrieval_started_utc': datetime.now(timezone.utc).isoformat(),
            'nba_api_version': version('nba_api'), 'timeout_seconds': 20,
            'http_status': None, 'row_count': None, 'columns': None,
            'raw_sha256': None, 'raw_path': None,
        }
        start = time.monotonic()
        try:
            endpoint.get_request()
            record['result'] = 'response_received'
        except Exception as exc:
            record.update(result='request_failed', error_type=type(exc).__name__, error=str(exc))
        record['runtime_seconds'] = round(time.monotonic() - start, 3)
        record['retrieval_finished_utc'] = datetime.now(timezone.utc).isoformat()
        response = endpoint.nba_response
        if response is not None:
            # Preserve the source response before schema inspection or transformation.
            content = response.get_response().encode('utf-8')
            digest = hashlib.sha256(content).hexdigest()
            RAW.mkdir(parents=True, exist_ok=True)
            raw_path = RAW / (run_id + f'_attempt_{attempt}_' + digest + '.json')
            with raw_path.open('xb') as f:
                f.write(content)
            record.update(http_status=response._status_code, raw_sha256=digest,
                          raw_path=str(raw_path.relative_to(ROOT)), url=response.get_url())
            try:
                obj = json.loads(content)
                datasets = obj['resultSets']
                dataset = next(d for d in datasets if d['name'] == 'LeagueGameLog')
                record.update(row_count=len(dataset['rowSet']), columns=dataset['headers'])
                if response._status_code == 200 and record['row_count'] > 0:
                    record['result'] = 'nonempty_response_received'
                    success += 1
            except (ValueError, KeyError, TypeError, StopIteration) as exc:
                record.update(result='invalid_response', schema_error=str(exc))
        write_new(run / f'attempt_{attempt}.json', record)
        print(json.dumps(record), flush=True)
        if attempt == 1:
            time.sleep(3)
    if not success:
        print('BLOCKED: both maintained-client attempts failed; stop ingestion. No alternate data source used.')
        return 2
    print('Access evidence saved; full-season ingestion and validation still required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
