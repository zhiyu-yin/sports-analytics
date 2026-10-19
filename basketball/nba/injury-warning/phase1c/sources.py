"""Phase 1C acquisition ledger; original Phase 1B ledger remains byte-identical."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date,timedelta
import csv,hashlib,json,re,urllib.request,urllib.error
from pathlib import Path
from injury_warning.pilot_io import ROOT,manifest as old_manifest,read_source as old_read,now

CROOT=ROOT/'phase1c'
CACHE=ROOT/'data/raw/phase1c'
LEDGER=CROOT/'source_manifest.jsonl'


def manifest():
    out=old_manifest()
    if LEDGER.exists():out.update({r['source_id']:r for r in map(json.loads,LEDGER.read_text().splitlines())})
    return out


def read(sid):
    if sid in old_manifest():return old_read(sid)
    r=manifest()[sid]
    if r['status']!='obtained':return None
    p=ROOT/r['raw_file'];b=p.read_bytes()
    if not p.resolve().is_relative_to(CACHE.resolve()) or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Cache provenance failure')
    return b


def request(r):
    if not '2024-01-01'<=r['date']<='2024-04-14':raise ValueError('Outside registered development follow-up')
    if r['kind']=='report':
        if not re.fullmatch(r'https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-\d\d-\d\d_\d\d[AP]M.pdf',r['url']):raise ValueError('Unsupported report')
    elif r['kind']=='news':
        if not (r['url'].startswith('https://www.nba.com/celtics/news/') or r['url'].startswith('https://www.nba.com/news/')):raise ValueError('Unsupported news host')
    else:raise ValueError('Unsupported source kind')
    receipt=dict(r,retrieved_at=now(),publication_at=None,publication_precision='unverified_original_availability',evidence_category='C_until_registered_B_assumption_applied')
    try:
        with urllib.request.urlopen(urllib.request.Request(r['url'],headers={'User-Agent':'NBAInjuryFeasibilityResearch/0.1'}),timeout=18) as response:
            body=response.read(12_000_001);receipt.update(http_status=response.status,final_url=response.url,server_last_modified=response.headers.get('Last-Modified'))
        if receipt['final_url']!=r['url'] or len(body)>12_000_000:raise ValueError('Redirect or oversized response')
        if r['kind']=='report' and not body.startswith(b'%PDF-'):raise ValueError('Non-PDF report')
        digest=hashlib.sha256(body).hexdigest();CACHE.mkdir(parents=True,exist_ok=True);p=CACHE/(digest+('.pdf' if r['kind']=='report' else '.html'));p.write_bytes(body)
        receipt.update(status='obtained',sha256=digest,bytes=len(body),raw_file=str(p.relative_to(ROOT)))
    except urllib.error.HTTPError as exc:receipt.update(status='http_not_found' if exc.code==404 else 'access_denied' if exc.code in (401,403) else 'http_error',http_status=exc.code,error=str(exc))
    except Exception as exc:receipt.update(status='retrieval_failed',error=f'{type(exc).__name__}: {exc}')
    return receipt


def catalog():
    result=[]
    with (ROOT/'pilot/tables/team_schedule.csv').open() as f:games=list(csv.DictReader(f))
    for g in games:
        if g['phase']=='pilot':
            d=g['game_date'];result.append(dict(source_id='report_'+d+'_11PM',kind='report',date=d,url=f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{d}_11PM.pdf'))
    # Dense daily report probes are a registered surveillance channel, not a claim of archive completeness.
    d=date(2024,1,1)
    while d<=date(2024,3,1):
        day=d.isoformat();result.append(dict(source_id='report_'+day+'_11AM',kind='report',date=day,url=f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{day}_11AM.pdf'));d+=timedelta(days=1)
    extra=CROOT/'reviewed_news_requests.json'
    if extra.exists():result.extend(json.loads(extra.read_text()))
    (CROOT/'request_catalog.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def acquire(fetch=False):
    from collections import Counter
    old=manifest();todo=[r for r in catalog() if r['source_id'] not in old]
    if fetch:
        with ThreadPoolExecutor(max_workers=3) as pool,LEDGER.open('a') as f:
            for r in pool.map(request,todo):f.write(json.dumps(r,sort_keys=True)+'\n');f.flush()
    return dict(pending=len(todo),new_ledger_status=dict(Counter(r['status'] for r in map(json.loads,LEDGER.read_text().splitlines()))) if LEDGER.exists() else {})
