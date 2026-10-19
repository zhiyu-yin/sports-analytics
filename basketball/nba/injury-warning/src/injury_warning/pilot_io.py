"""Bounded development-source retrieval. No protected experiment imports."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT/'data/raw/phase1b'
MANIFEST = ROOT/'pilot/source_manifest.jsonl'


def now():
    return datetime.now(timezone.utc).isoformat()


def validate_request(r):
    if r['kind'] in {'boxscore','playbyplay'}:
        expected = f"https://cdn.nba.com/static/json/liveData/{r['kind']}/{r['kind']}_{r['game_id']}.json"
        if r['url'] != expected or not r['game_id'].startswith('00223'):
            raise ValueError('Non-development game or unexpected live-data URL')
    elif r['kind'] == 'report':
        if not re.fullmatch(r'https://ak-static.cms.nba.com/referee/injury/Injury-Report_202[34]-\d\d-\d\d_\d\d[AP]M.pdf',r['url']):
            raise ValueError('Unexpected injury report URL')
    elif r['kind'] == 'gamebook':
        if not re.fullmatch(r'https://statsdmz.nba.com/pdfs/202[34]\d{4}/202[34]\d{4}_[A-Z]{6}_book.pdf',r['url']):
            raise ValueError('Unexpected gamebook URL')
    elif r['kind'] == 'team_notes':
        if r['url']!='https://cdn.nba.com/teams/uploads/sites/1610612739/2024/05/240511-boscle-notes.pdf':
            raise ValueError('Unreviewed historical team notes')
    elif r['kind'] == 'game_page':
        if not re.fullmatch(r'https://www.nba.com/game/[a-z]{3}-vs-[a-z]{3}-00223\d{5}/box-score',r['url']):
            raise ValueError('Unexpected historical game page')
    elif r['kind'] == 'team_release':
        if not r['url'].startswith('https://www.nba.com/celtics/news/'):
            raise ValueError('Unreviewed release URL')
    else:
        raise ValueError('Unsupported source kind')
    if not '2023-10-01' <= r['date'] <= '2024-06-30':
        raise ValueError('Outside development evidence bounds')


def retrieve_one(r):
    validate_request(r)
    record = dict(r, retrieved_at=now(), publication_at=None,
                  publication_precision='unverified_original_availability',
                  status='retrieval_failed', error=None, evidence_locator='raw response')
    try:
        request = urllib.request.Request(r['url'],headers={'User-Agent':'NBAInjuryFeasibilityResearch/0.1'})
        with urllib.request.urlopen(request,timeout=18) as response:
            body=response.read(12_000_001)
            record.update(http_status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type'),
                          server_last_modified=response.headers.get('Last-Modified'))
        if record['final_url'] != r['url']:
            raise ValueError('Unexpected redirect; not following into other-season data')
        if len(body)>12_000_000:
            raise ValueError('Response too large')
        if r['kind'] in ('report','gamebook','team_notes') and not body.startswith(b'%PDF-'):
            raise ValueError('Not PDF')
        if r['kind'] in ('boxscore','playbyplay'):
            obj=json.loads(body)
            if str(obj.get('game',{}).get('gameId')) != r['game_id']:
                raise ValueError('Wrong game')
        digest=hashlib.sha256(body).hexdigest()
        CACHE.mkdir(parents=True,exist_ok=True)
        ext='.pdf' if r['kind'] in ('report','gamebook','team_notes') else '.json' if r['kind'] in ('boxscore','playbyplay') else '.html'
        target=CACHE/(digest+ext)
        if target.exists() and target.read_bytes()!=body:
            raise ValueError('Hash collision')
        target.write_bytes(body)
        record.update(status='obtained',sha256=digest,bytes=len(body),raw_file=str(target.relative_to(ROOT)))
    except urllib.error.HTTPError as e:
        record.update(http_status=e.code,error=str(e),status='http_not_found' if e.code==404 else 'access_denied' if e.code in (401,403) else 'http_error')
    except Exception as e:
        record.update(error=f'{type(e).__name__}: {e}')
    record['retrieval_finished_at']=now()
    return record


def manifest():
    if not MANIFEST.exists():return {}
    return {r['source_id']:r for r in map(json.loads,MANIFEST.read_text().splitlines())}


def retrieve(requests,fetch=False):
    old=manifest()
    pending=[r for r in requests if r['source_id'] not in old]
    for r in requests:validate_request(r)
    if not fetch:return {'requested':len(requests),'already_attempted':len(requests)-len(pending),'pending':len(pending)}
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool, MANIFEST.open('a') as f:
        for result in pool.map(retrieve_one,pending):
            f.write(json.dumps(result,sort_keys=True)+'\n');f.flush()
    from collections import Counter
    return dict(Counter(r['status'] for r in manifest().values()))


def read_source(source_id):
    record=manifest()[source_id]
    if record['status']!='obtained':return None
    p=ROOT/record['raw_file']
    if not p.resolve().is_relative_to(CACHE.resolve()):raise ValueError('Cache path escape')
    b=p.read_bytes()
    if hashlib.sha256(b).hexdigest()!=record['sha256']:raise ValueError('Raw cache changed')
    return b
