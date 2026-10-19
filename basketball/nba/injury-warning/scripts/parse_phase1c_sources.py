#!/usr/bin/env python3
"""Read original caches without modifying them; parse the Phase 1C source union."""
import sys,json,importlib.util,csv,re,hashlib
from pathlib import Path
from datetime import timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from phase1c.sources import ROOT,CROOT,manifest,read
from injury_warning.rules import utc
spec=importlib.util.spec_from_file_location('legacy_report_parser',ROOT/'scripts/parse_pilot_reports.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def main():
    out=[]
    for sid,r in manifest().items():
        if r['kind']!='report':continue
        rec=dict(source_id=sid,retrieval_status=r['status'],url=r['url'])
        if r['status']!='obtained':rec.update(state='missing_report',observations=[],sections=[])
        else:
            try:
                rec.update(m.parse_report(read(sid)));rec['assumed_available_at']=(utc(rec['report_at'])+timedelta(minutes=30)).isoformat()
            except Exception as exc:rec.update(state='parse_failure',observations=[],sections=[],error=str(exc))
        out.append(rec)
    (CROOT/'parsed_reports.json').write_text(json.dumps(out,indent=2)+'\n')
    # Keep search response bodies local; retain reproducible query/result URL metadata for review.
    saved=json.loads((CROOT/'search_ledger.json').read_text()) if (CROOT/'search_ledger.json').exists() else []
    searches=list(saved);rawdir=ROOT/'data/raw/phase1c/searches';rawdir.mkdir(parents=True,exist_ok=True)
    for p in sorted((CROOT/'searches').glob('batch_*.json')):
        o=json.loads(p.read_text());urls=list(dict.fromkeys(re.findall(r'https://[^\s)]+',o['result'])))
        digest=hashlib.sha256(p.read_bytes()).hexdigest();dest=rawdir/(digest+'.json');dest.write_bytes(p.read_bytes())
        for q in o['queries']:searches.append(dict(search_id='search_'+q['date'],date=q['date'],query=q['q'],retrieved_at=o['retrieved_at'],status='executed',coverage='bounded_index_search_not_exhaustive',result_urls=urls,result_date_scope='not guaranteed; unrelated dates and other teams are ineligible without direct review',raw_file=str(dest.relative_to(ROOT)),sha256=digest))
    searches=list({r['search_id']:r for r in searches}.values())
    (CROOT/'search_ledger.json').write_text(json.dumps(searches,indent=2)+'\n')
    from collections import Counter
    print('Report states:',dict(Counter(r['state'] for r in out)),'Daily search queries:',len(searches))


if __name__=='__main__':main()
