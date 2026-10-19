"""Audit explicit source clock semantics across all acquired development game pages."""
from datetime import datetime,timedelta,timezone,date
from collections import Counter
from zoneinfo import ZoneInfo
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import re,json
from phase2a.prepare import page_data
from phase1d.acquire import schedule
from .io import D,manifest,read,rows,write
OFFSETS={'UTC':0,'GMT':0,'EST':-5,'EDT':-4,'CST':-6,'CDT':-5,'MST':-7,'MDT':-6,'PST':-8,'PDT':-7}
def parse_clock(raw,day,scheduled=None,source_zone=None):
    m=re.search(r'\((\d{1,2}:\d\d\s*[AP]M)\s+(UTC|GMT|EST|EDT|CST|CDT|MST|MDT|PST|PDT)\)',raw)
    if not m:return None,None,'unknown_timezone_or_format'
    clock=datetime.strptime(m[1],'%I:%M %p').time();z=timezone(timedelta(hours=OFFSETS[m[2]]))
    base=datetime.combine(date.fromisoformat(day),clock,ZoneInfo(source_zone) if source_zone else z)
    if scheduled:
        s=datetime.fromisoformat(scheduled.replace('Z','+00:00'))
        # Scheduled start establishes the calendar day; end must follow that start.
        base=min([base+timedelta(days=x) for x in [-1,0,1]],key=lambda x:abs((x-s).total_seconds()))
    elif base.hour<6:base+=timedelta(days=1)
    return base.isoformat(),(base+timedelta(minutes=1)).isoformat(),('verified_NBA_Eastern_wall_clock_stale_EST_label' if source_zone else 'explicit_'+m[2]+'_fixed_offset')+'; nearest_scheduled_UTC_date; minute_interval'
def endpoints(p,day):
    a=p.get('playByPlay',{}).get('actions',[])
    starts=[x for x in a if x.get('actionType')=='period' and x.get('subType')=='start' and x.get('period')==1]
    ends=[x for x in a if x.get('actionType')=='period' and x.get('subType')=='end']
    st=starts[0].get('description','') if starts else '';en=max(ends,key=lambda x:(x.get('period',0),x.get('actionNumber',0))).get('description','') if ends else ''
    sched=p['game'].get('gameTimeUTC')
    def parse(raw):return parse_clock(raw,day,sched,'America/New_York' if re.search(r' (EST|EDT)\)',raw) else None)
    return st,en,parse(st),parse(en)
def book_clocks(item):
    from pypdf import PdfReader
    gid,entry=item
    try:
        from injury_warning.pilot_io import ROOT
        import hashlib
        b=(ROOT/entry['raw_file']).read_bytes();assert hashlib.sha256(b).hexdigest()==entry['sha256']
        p=PdfReader(BytesIO(b));first=p.pages[0].extract_text();duration=re.search(r'Game Duration:\s*(\d+:\d+)',first)
        start=end=''
        for i in range(8,min(len(p.pages),12)):
            m=re.search(r'Start of Period \(([^)]+)\)',p.pages[i].extract_text())
            if m:start=m[1];break
        for i in range(len(p.pages)-1,7,-1):
            m=re.findall(r'End of Period \(([^)]+)\)',p.pages[i].extract_text())
            if m:end=m[-1];break
        return gid,dict(book_start_raw=start,book_end_raw=end,book_duration=duration[1] if duration else '',book_timezone='unlabeled venue-local clock; comparison uses venue metadata, not input to parser',book_locator='first/last play-by-play Start/End of Period; FINAL BOX Game Duration')
    except Exception as e:return gid,dict(book_error=str(e))
def audit():
    sm=manifest();ss={g['game_id']:g for g in schedule()};data=[];tasks=[]
    for sid,v in sorted(sm.items()):
        if not sid.startswith('page_') or v['status']!='obtained':continue
        try:p=page_data(sid,sm)
        except (KeyError,TypeError,ValueError):continue
        gid=str(p['game']['gameId']);g=ss.get(gid)
        if not g:continue
        day=g['game_date'];st,en,s,e=endpoints(p,day);arena=p['game'].get('arena',{})
        data.append(dict(game_id=gid,game_date=day,source_id=sid,source_sha256=v['sha256'],scheduled_start_utc=p['game'].get('gameTimeUTC'),gameEt_raw_not_UTC=p['game'].get('gameEt'),venue=arena.get('arenaName'),city=arena.get('arenaCity'),venue_timezone=arena.get('arenaTimezone'),start_raw=st,end_raw=en,start_lower=s[0],start_upper=s[1],end_lower=e[0],end_upper=e[1],start_rule=s[2],end_rule=e[2],precision='one minute; source timestamp not clinical onset',scheduled_delay_minutes=(datetime.fromisoformat(s[0])-datetime.fromisoformat(p['game']['gameTimeUTC'].replace('Z','+00:00'))).total_seconds()/60 if s[0] else None))
        if sm.get('book_'+gid,{}).get('status')=='obtained':tasks.append((gid,sm['book_'+gid]))
    with ProcessPoolExecutor(max_workers=6) as pool:books=dict(pool.map(book_clocks,tasks))
    for r in data:
        r.update(books.get(r['game_id'],{}))
        zones={'Eastern':'America/New_York','Central':'America/Chicago','Mountain':'America/Denver','Pacific':'America/Los_Angeles'}
        zone='America/Phoenix' if r['city']=='Phoenix' else 'Europe/Paris' if r['city']=='Paris' else zones.get(r['venue_timezone'])
        r['book_conversion_rule']='Venue IANA timezone; Paris independently located by arena/city; Phoenix no DST. Compare only, never attach venue zone to page Eastern text.'
        for kind in ['start','end']:
            raw=r.get('book_'+kind+'_raw');value=r[kind+'_lower']
            if not (raw and value and zone):continue
            a=datetime.fromisoformat(value);z=ZoneInfo(zone);b=datetime.combine(a.astimezone(z).date(),datetime.strptime(raw,'%I:%M %p').time(),z)
            r['book_'+kind+'_converted_utc']=b.astimezone(timezone.utc).isoformat()
            r['page_minus_book_'+kind+'_minutes']=(a-b).total_seconds()/60
            assert abs(r['page_minus_book_'+kind+'_minutes'])<=2,(r['game_id'],kind)
        r['interpretation']='Page Eastern seasonal wall-clock supported by UTC schedule and venue-local book. Start/end distinct. Book can precede page by one minute; source-specific minute interval retained.' 
    write('all_acquired_game_clock_audit',data)
    (D/'clock_summary.json').write_text(json.dumps(dict(acquired_game_pages=len(data),book_checks=len(books),formats=dict(Counter(r['start_rule'] for r in data)),unresolved=sum(not r['start_lower'] or not r['end_upper'] for r in data)),indent=2)+'\n')
    lookup={r['game_id']:r for r in data};new=[]
    for old in rows('game_timing'):
        r=lookup[old['game_id']];out=dict(old)
        if r['start_lower']:out.update(anchor_lower=r['start_lower'],anchor_upper=r['start_upper'])
        else:out.update(anchor_lower='',anchor_upper='',anchor_precision='unknown timezone; no point anchor')
        out['end_upper']=r['end_upper'] or '';out['B_available_at']=(datetime.fromisoformat(r['end_upper'])+timedelta(hours=6)).isoformat() if r['end_upper'] else ''
        new.append(out)
    write('game_timing',new)
if __name__=='__main__':audit()
