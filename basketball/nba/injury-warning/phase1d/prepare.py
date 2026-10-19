"""Extract targeted evidence without writing historical artifacts."""
import json,csv,re,hashlib
from io import BytesIO
from datetime import timedelta
from phase1d.acquire import D,ROOT,manifest,read
from phase1d.report_parser import parse_report
from injury_warning.longitudinal import parse_game_page,minutes,canonical,absence_category,end_minute
from injury_warning.rules import utc

def write(name,rows):
    rows=list(rows);p=D/'tables';p.mkdir(exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r)) or ['row_id']
    with (p/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def rows(name,folder='phase1c'):
    with (ROOT/folder/'tables'/name).open() as f:return list(csv.DictReader(f))
def page(sid):
    b=read(sid)
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',b.decode(),re.S)[1])['props']['pageProps']
def game_bounds(game_id, game_date, clinical=False):
    """Minute-bounded actual period start; clinical event lies within played game.

    Reuse explicit source clock -> IANA-zone parser, retaining raw clock text.
    Scheduled start is never passed as an actual completion or onset time.
    """
    from phase1d.logic import day_bounds
    sid='page_'+game_id
    if manifest().get(sid,{}).get('status')!='obtained':
        lo,hi=day_bounds(game_date)
        return lo,hi,'documented_date_only; source_missing_actual_start_unresolved'
    _, actions=parse_game_page(read(sid))
    starts=[a for a in actions if a.get('actionType')=='period' and a.get('subType')=='start' and a.get('period')==1]
    if starts:
        lo,hi,raw=end_minute([dict(starts[0],subType='end')],game_date)
        if lo and hi:
            if clinical:
                _,end,_=end_minute(actions,game_date)
                if end:return lo,end,'actual_played_game_interval; '+raw
            else:return lo,hi,'actual_first_period_start_minute; '+raw
    lo,hi=day_bounds(game_date)
    return lo,hi,'documented_game_date_ET_whole_day_interval; actual_start_unresolved'

def prepare():
    from pypdf import PdfReader
    sources=manifest();logs=[];recaps=[];reports=[]
    for r in json.loads((D/'target_schedule.json').read_text()):
        pid,name,label={'transfer_Stevens':('1630205','Lamar Stevens','Grizzlies'),'transfer_Banton':('1630625','Dalano Banton','Trail Blazers'),'fixture_Randle':('203944','Julius Randle','Knicks'),'fixture_Ball':('1630163','LaMelo Ball','Hornets')}[r['role']]
        gid=r['game_id'];sid='page_'+gid;book='book_'+gid;rec=dict(r,player_id=pid,player_name=name,roster_observed=False,appeared=False,minutes='',reason='',category='unknown',page_source=sid,reason_source=book,coverage='unknown',evidence_category='C_outcome_only',historical_label_known_at='')
        if sources.get(sid,{}).get('status')=='obtained':
            p=page(sid);g,a=parse_game_page(read(sid));tm=next(t for t in [g['homeTeam'],g['awayTeam']] if t['teamTricode']==r['team']);pp=next((v for v in tm['players']+tm['inactives'] if str(v['personId'])==pid),None)
            rec['roster_observed']=bool(pp);rec['minutes']=minutes(pp.get('statistics',{}).get('minutes')) or 0 if pp else '';rec['appeared']=bool(pp and rec['minutes']>0);rec['reason']=pp.get('comment','') if pp else '';lo,hi,raw=end_minute(a,r['game_date']);rec.update(end_upper=hi or '',end_clock_raw=raw,stats_B_available_at=(utc(hi)+timedelta(hours=6)).isoformat() if hi else '',recap_present=bool(p.get('story',{}).get('content')))
            recaps.append(dict(game_id=gid,game_date=r['game_date'],role=r['role'],source_id=sid,story_date_raw=p.get('story',{}).get('date'),paragraphs=[dict(index=i,text=s) for i,s in enumerate(p.get('story',{}).get('content',[])) if any(w in str(s).lower() for w in ['randle','ball','stevens','banton','injur','ankle','shoulder'])]))
        if sources.get(book,{}).get('status')=='obtained':
            pdf=PdfReader(BytesIO(read(book)));text=pdf.pages[0].extract_text();m=re.search(r'Inactive:\s*'+re.escape(label)+r'\s*-\s*(.*?)(?=Inactive:|Points in the Paint:)',text,re.S|re.I)
            if m:
                hits=[reason.strip() for fam,reason in re.findall(r'([^(),]+)\s*\(([^)]+)\)',m[1].replace('\n',' ')) if canonical(fam.strip())==canonical(name.split()[-1])]
                if len(hits)==1:rec['reason']=hits[0]
            if not rec['reason'] and not rec['appeared']:
                layout=pdf.pages[0].extract_text(extraction_mode='layout');hits=[line for line in layout.splitlines() if canonical(name) in canonical(line) and ('DND -' in line or 'DNP -' in line)]
                if len(hits)==1:rec['reason']=re.search(r'DN[DP] -.*',hits[0])[0].strip()
            rec['coverage']='page_and_book' if rec['roster_observed'] else 'book_obtained_roster_unobserved'
        rec['category']='appearance' if rec['appeared'] else absence_category(rec['reason']);logs.append(rec)
    for sid,r in sources.items():
        if r['kind']!='report' or sid not in {v['source_id'] for v in json.loads((D/'request_catalog.json').read_text())}:continue
        for team,label in [('NYK','NewYorkKnicks'),('CHA','CharlotteHornets')]:
            rr=dict(source_id=sid,team=team,retrieval_status=r['status'])
            if r['status']=='obtained':
                try:rr.update(parse_report(read(sid),label));rr['B_available_at']=(utc(rr['report_at'])+timedelta(minutes=30)).isoformat()
                except Exception as exc:rr.update(state='parse_failure',error=str(exc),observations=[],sections=[])
            else:rr.update(state='missing',observations=[],sections=[])
            reports.append(rr)
    searches=[]
    for f in sorted((ROOT/'data/raw/phase1d/searches').glob('*.json')):
        b=f.read_bytes();o=json.loads(b)
        for q in o['queries']:searches.append(dict(q,retrieved_at=o['retrieved_at'],status='executed',sha256=hashlib.sha256(b).hexdigest(),raw_file=str(f.relative_to(ROOT)),coverage='bounded_dated_search; not exhaustive; results not predictors without direct review'))
    write('target_game_evidence',logs);(D/'parsed_reports.json').write_text(json.dumps(reports,indent=2)+'\n');(D/'search_ledger.json').write_text(json.dumps(searches,indent=2)+'\n')
    # Licensed narrative text remains local; tracked review locators are emitted by build.
    (ROOT/'data/raw/phase1d/recap_review.json').write_text(json.dumps(recaps,indent=2)+'\n')
    print('target game rows',len(logs),'reports',len(reports),'queries',len(searches))
if __name__=='__main__':prepare()
