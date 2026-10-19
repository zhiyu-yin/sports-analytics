#!/usr/bin/env python3
"""Validate curated audit records, then render a deterministic review table; never infer labels."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    with (ROOT/'audit/candidates.csv').open(newline='') as handle:
        records = list(csv.DictReader(handle))
    sources = {s['source_id']: s for s in json.loads((ROOT/'audit/sources.json').read_text())}
    ids = set()
    lines = ['# Selected injury label audit', '',
             'Purposive evidence sample, not a cohort, prevalence estimate, or model evaluation. Blank CSV values mean unknown. Labels are provisional reviewer judgments. Primary means documented >28 days; proxy means onset-to-return calendar gap only.', '',
             '| Case | Player / episode | Primary | Secondary | Proxy | Evidence / decision | Source |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for r in records:
        assert r['candidate_id'] not in ids
        ids.add(r['candidate_id'])
        assert r['mechanism'] in ('contact', 'non_contact', 'unknown')
        assert r['primary_label'] in ('positive', 'negative', 'unknown', 'excluded')
        assert r['secondary_label'] in ('positive', 'negative', 'unknown', 'excluded')
        assert r['medical_clearance_date'] == ''  # Not established in this audit.
        refs = r['source_ids'].split(';')
        assert all(s in sources for s in refs)
        links = ', '.join(f"[{s}]({sources[s]['url']})" for s in refs)
        lines.append(f"| {r['candidate_id']} | {r['player_name']} / {r['condition']} | {r['primary_label']} | {r['secondary_label']} | {r['return_gap_proxy_days'] or 'unknown'} | {r['adjudication_note']} | {links} |")
    (ROOT/'docs/audit_review.md').write_text('\n'.join(lines)+'\n')
    print(f'Validated and rendered {len(records)} selected candidate episodes')


if __name__ == '__main__':
    build()
