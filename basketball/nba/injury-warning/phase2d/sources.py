"""Immutable receipt index and canonical-URL request planning; no endpoint retry."""
import json,hashlib,re
from pathlib import Path
from collections import defaultdict,Counter
from urllib.parse import urlsplit,urlunsplit
from injury_warning.pilot_io import ROOT
from phase1d.acquire import schedule
from .audit import D,write

def canonical_url(url):
    p=urlsplit(url);return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip('/'),p.query,''))
def historical_receipts():
    out=[]
    for phase in ['pilot','phase1c','phase1d','phase2a','phase2b','phase2b/boston_fixture_rebuild','phase2c']:
        for suffix in ['jsonl','json']:
            p=ROOT/phase/('source_manifest.'+suffix)
            if not p.exists():continue
            rr=[json.loads(l) for l in p.read_text().splitlines()] if suffix=='jsonl' else json.loads(p.read_text())
            if isinstance(rr,dict):rr=list(rr.values())
            out.extend(dict(r,receipt_ledger=str(p.relative_to(ROOT)),receipt_line=i+1) for i,r in enumerate(rr))
    return out
def choose_usable(receipts):
    valid=sorted([r for r in receipts if r['usable']],key=lambda r:(r.get('retrieved_at',''),r['receipt_id']))
    return valid[0] if valid else None

def build_index():
    receipts=historical_receipts();hashed={};records=[];byurl=defaultdict(list);byid=defaultdict(list)
    for r in receipts:
        r=dict(r,canonical_url=canonical_url(r['url']));r['receipt_id']=hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest();r['usable']=False
        if r['status']=='obtained' and r.get('raw_file'):
            p=ROOT/r['raw_file']
            if p not in hashed:hashed[p]=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
            r['usable']=hashed[p]==r.get('sha256')
        records.append(r);byurl[r['canonical_url']].append(r);byid[r['source_id']].append(r)
    index=[]
    for url,rr in sorted(byurl.items()):
        valid=sorted([r for r in rr if r['usable']],key=lambda r:(r.get('retrieved_at',''),r['receipt_id']))
        # Earliest hash-verified success is stable. A prior failed receipt does
        # not suppress a later legitimate obtained version. All receipts remain.
        chosen=choose_usable(rr)
        index.append(dict(canonical_url=url,source_ids=';'.join(sorted({r['source_id'] for r in rr})),receipt_ids=';'.join(r['receipt_id'] for r in rr),receipt_count=len(rr),versions=';'.join(sorted({r.get('sha256','') for r in valid})),selected_receipt_id=chosen['receipt_id'] if chosen else '',selected_source_id=chosen['source_id'] if chosen else '',raw_file=chosen['raw_file'] if chosen else '',sha256=chosen['sha256'] if chosen else '',state='cached_usable' if chosen else 'previously_failed_or_invalid',failed_before_valid_success=bool(chosen and any(not r['usable'] and r.get('retrieved_at','')<chosen.get('retrieved_at','') for r in rr))))
    (D/'global_receipts.json').write_text(json.dumps(records,indent=2)+'\n');write(D/'global_source_index.csv',index)
    return records,index

def catalog(teams):
    req=[];games=[g for g in schedule() if g['team'] in teams and '2023-12-04'<=g['game_date']<='2024-04-14']
    for g in games:
        a,b=g['matchup'].split(' @ ') if ' @ ' in g['matchup'] else g['matchup'].split(' vs. ')[::-1];day=g['game_date'];ds=day.replace('-','');gid=g['game_id']
        for kind,url in [('page',f'https://www.nba.com/game/{a.lower()}-vs-{b.lower()}-{gid}/box-score'),('book',f'https://statsdmz.nba.com/pdfs/{ds}/{ds}_{a}{b}_book.pdf')]:req.append(dict(source_id=kind+'_'+gid,date=day,kind=kind,url=url,scope='core'))
    from datetime import date,timedelta
    day=date(2024,1,1)
    while day<=date(2024,3,3):
        for hour in ['11AM']+(['11PM'] if day<=date(2024,2,18) else []):
            ds=day.isoformat();req.append(dict(source_id='report_'+ds+'_'+hour,date=ds,kind='report',url=f'https://ak-static.cms.nba.com/referee/injury/Injury-Report_{ds}_{hour}.pdf',scope='core'))
        day+=timedelta(days=1)
    return req,games

def plan(teams):
    receipts,index=build_index();byurl={r['canonical_url']:r for r in index};raw,games=catalog(teams);unique={canonical_url(r['url']):r for r in raw};plan=[]
    for url,r in unique.items():
        old=byurl.get(url);state=old['state'] if old else 'genuinely_new_request';plan.append(dict(r,canonical_url=url,state=state,selected_receipt_id=old['selected_receipt_id'] if old else '',requires_new_scope_reparse=state=='cached_usable' and r['kind']=='report'))
    write(D/'dry_run_request_plan.csv',plan)
    result=dict(raw_catalog_entries=len(raw),deduplicated_catalog_entries=len(unique),duplicate_requests_removed=len(raw)-len(unique),states=dict(Counter(r['state'] for r in plan)),cached_needing_scope_reparse=sum(r['requires_new_scope_reparse'] for r in plan),global_receipts=len(receipts),prior_failure_with_valid_success=sum(r['failed_before_valid_success'] for r in index),policy='Use earliest hash-verified success for canonical URL, retain all historical receipts and hashes. Failure never overrides legitimate later success. Previously denied/failed URLs with no valid success are not automatically retried. New data is C until registered B availability. No modification of historical batch source selection.')
    (D/'dry_run_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result
if __name__=='__main__':
    spec=json.loads((D/'registration/scope_v1.json').read_text());plan([t['team'] for t in spec['remaining_sorted']])
