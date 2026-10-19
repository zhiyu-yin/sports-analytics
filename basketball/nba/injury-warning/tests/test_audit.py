import csv
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuditIntegrity(unittest.TestCase):
    def test_references_and_proxy_arithmetic(self):
        from datetime import date
        sources = {s['source_id'] for s in json.loads((ROOT/'audit/sources.json').read_text())}
        with (ROOT/'audit/candidates.csv').open(newline='') as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(20 <= len(rows) <= 30)
        self.assertEqual(len({r['candidate_id'] for r in rows}), len(rows))
        for r in rows:
            self.assertTrue(set(r['source_ids'].split(';')) <= sources)
            if r['return_gap_proxy_days']:
                self.assertEqual((date.fromisoformat(r['first_return_appearance_date']) -
                                  date.fromisoformat(r['onset_lower_date'])).days,
                                 int(r['return_gap_proxy_days']))
            self.assertFalse(r['medical_clearance_date'])

    def test_raw_cache_if_present(self):
        for s in json.loads((ROOT/'audit/sources.json').read_text()):
            if s.get('raw_sha256'):
                p = ROOT/'data/raw/evidence'/(s['raw_sha256']+'.pdf')
                if p.exists():
                    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), s['raw_sha256'])
