#!/usr/bin/env python3
"""Retrieve only reviewed manifest URLs; immutable local cache and failure receipts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def fetch(source, output):
    if source.get('cache_policy') != 'local_personal_noncommercial_pdf':
        raise ValueError('Source is metadata-only; caching has not been cleared')
    url = source['url']
    # No URL synthesis, mutable season index, arbitrary URL or protected-season endpoint.
    allowed = {
        'https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-01-04_06PM.pdf',
        'https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-01-28_12PM.pdf',
    }
    if url not in allowed:
        raise ValueError('URL outside reviewed development evidence allowlist')
    output.mkdir(parents=True, exist_ok=True)
    receipt = {'source_id': source['source_id'], 'url': url,
               'retrieval_started_at': datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            body = response.read(5_000_001)
            receipt.update(final_url=response.url, http_status=response.status,
                           content_type=response.headers.get('Content-Type'))
        if receipt['final_url'] != url or not body.startswith(b'%PDF-') or len(body) > 5_000_000:
            raise ValueError('Redirect, oversized body or non-PDF response')
        digest = hashlib.sha256(body).hexdigest()
        path = output / (digest + '.pdf')
        if path.exists() and path.read_bytes() != body:
            raise ValueError('Cache collision')
        path.write_bytes(body)
        receipt.update(sha256=digest, bytes=len(body), raw_file=path.name, status='obtained')
    except Exception as exc:
        receipt.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    receipt['retrieval_finished_at'] = datetime.now(timezone.utc).isoformat()
    token = receipt['retrieval_started_at'].replace(':', '').replace('+', '_')
    (output / (source['source_id'] + '_' + token + '.json')).write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fetch', action='store_true', help='Explicitly permit network retrieval')
    p.add_argument('--output', type=Path, default=ROOT/'data/raw/evidence')
    args = p.parse_args()
    sources = json.loads((ROOT/'audit/sources.json').read_text())
    selected = [s for s in sources if s['cache_policy'] == 'local_personal_noncommercial_pdf']
    if not args.fetch:
        print(json.dumps({'mode': 'offline', 'reviewed_urls': [s['url'] for s in selected]}, indent=2))
    else:
        results = [fetch(s, args.output) for s in selected]
        print(json.dumps(results, indent=2))
        raise SystemExit(any(r['status'] != 'obtained' for r in results))
