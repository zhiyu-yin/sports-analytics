"""Actual dated-query receipts, independently resumable from the HTTP catalog."""
import json,hashlib
from datetime import date,timedelta
from .runtime import D,ROOT,SPEC,bd

def ledger():
    records=[]
    for phase in ['phase2a','phase2c','phase2d']:
        for p in sorted((ROOT/'data/raw'/phase/'searches').glob('*.json')):
            b=p.read_bytes();o=json.loads(b)
            if o.get('status')!='fulfilled':continue
            for q in o['queries']:records.append(dict(q,status='fulfilled',retrieved_at=o['retrieved_at'],sha256=hashlib.sha256(b).hexdigest(),raw_file=str(p.relative_to(ROOT)),scope=q.get('scope','fixed_team_dated_search')))
    return records

def plan():
    seen={(r['team'],r['date']) for r in ledger()};todo=[]
    for t in SPEC['ordered_teams']:
        day=date(2024,1,1)
        while day<=date(2024,3,3):
            ds=day.isoformat()
            if (t['team'],ds) not in seen:todo.append(dict(team=t['team'],date=ds,q='site:nba.com "'+t['name']+'" "'+day.strftime('%B %-d, %Y')+'" injury status recap',scope='fixed_remaining17_daily_dated_search'))
            day+=timedelta(days=1)
    (D/'search_plan.json').write_text(json.dumps(todo,indent=2)+'\n');print('new',len(todo),'reused',1071-len(todo))
if __name__=='__main__':plan()
