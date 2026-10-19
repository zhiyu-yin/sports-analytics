#!/usr/bin/env python3
"""Parse PDF report geometry; keep not-submitted, no-team and parse failure distinct."""
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
import json,re
from injury_warning.pilot_io import ROOT,manifest,read_source


def parse_report(body):
    import pdfplumber
    observations=[];teams=set();not_submitted=set();team='';pending=None;target_date=None;sections={}
    with pdfplumber.open(BytesIO(body)) as pdf:
        first=pdf.pages[0].extract_text()
        m=re.search(r'Injury\s*Report:\s*(\d\d/\d\d/\d\d)\s*(\d{1,2}:\d\d)\s*([AP]M)',first)
        if not m:raise ValueError('Report header missing')
        report_at=datetime.strptime(' '.join(m.groups()),'%m/%d/%y %I:%M %p').replace(tzinfo=ZoneInfo('America/New_York')).isoformat()
        for i,page in enumerate(pdf.pages):
            lines={}
            for w in page.extract_words(x_tolerance=2,y_tolerance=2):
                key=round(w['top']/2)*2;lines.setdefault(key,[]).append(w)
            page_rows=[];reason_lines=[]
            for top,words in sorted(lines.items()):
                words.sort(key=lambda w:w['x0'])
                cols={c:' '.join(w['text'] for w in words if lo<=w['x0']<hi) for c,lo,hi in [('team',260,420),('player',420,580),('status',580,660),('reason',660,1200)]}
                text=' '.join(w['text'] for w in words)
                if top<80 or 'CurrentStatus' in text or 'Current Status' in text:continue
                date_words=' '.join(w['text'] for w in words if w['x0']<115)
                dm=re.search(r'\d\d/\d\d/\d{4}',date_words)
                if dm:target_date=datetime.strptime(dm[0],'%m/%d/%Y').date().isoformat()
                if cols['team']:
                    candidate=cols['team'].replace(' ','')
                    if not any(ch.isdigit() for ch in candidate) and len(candidate)>5:
                        team=candidate;teams.add(team);sections.setdefault((team,target_date),'complete')
                if 'NOTYETSUBMITTED' in text.replace(' ',''):
                    not_submitted.add(team);sections[(team,target_date)]='not_yet_submitted'
                if cols['player'] and ',' in cols['player'] and cols['status'] in {'Out','Available','Probable','Questionable','Doubtful'}:
                    pending=dict(team=team,target_game_date=target_date,player_name_raw=cols['player'],status=cols['status'],reason='',report_at=report_at,publication_verified=False,evidence_locator=f'PDF page {i+1}, y={top}, player {cols["player"]}')
                    page_rows.append((top,pending));observations.append(pending)
                if cols['reason'] and 'NOTYETSUBMITTED' not in cols['reason'].replace(' ',''):
                    reason_lines.append((top,cols['reason']))
            # Wrapped reason cells are vertically centered beside player names. Assign
            # to the nearest player row, including lines slightly ABOVE the name.
            for top,text in reason_lines:
                if page_rows:
                    y,row=min(page_rows,key=lambda pair:abs(pair[0]-top))
                    if abs(y-top)<=18:row['reason']=(row['reason']+' '+text).strip()
    bos='BostonCeltics'
    own=[dict(target_game_date=d,state=state) for (team,d),state in sections.items() if team==bos]
    states={s['state'] for s in own}
    state='team_not_covered' if not own else 'mixed_complete_and_unsubmitted' if len(states)>1 else next(iter(states))
    return dict(report_at=report_at,state=state,sections=own,observations=[o for o in observations if o['team']==bos],all_team_count=len(teams))



if __name__=='__main__':
    output=[]
    for sid,r in manifest().items():
        if r['kind']!='report':continue
        record=dict(source_id=sid,retrieval_status=r['status'])
        if r['status']!='obtained':record.update(state='missing_report',observations=[])
        else:
            try:record.update(parse_report(read_source(sid)))
            except Exception as exc:record.update(state='parse_failure',error=f'{type(exc).__name__}: {exc}',observations=[])
        output.append(record)
    (ROOT/'pilot/parsed_reports.json').write_text(json.dumps(output,indent=2)+'\n')
    from collections import Counter
    print(dict(Counter(r['state'] for r in output)))
    print('BOS observations',sum(len(r['observations']) for r in output))
