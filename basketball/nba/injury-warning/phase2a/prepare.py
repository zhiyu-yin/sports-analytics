"""Extract complete selected-team panels, report observations and recap review locators."""
from collections import defaultdict
from datetime import timedelta
from io import BytesIO
import csv,json,re,hashlib,time
from injury_warning.pilot_io import ROOT
from injury_warning.longitudinal import parse_game_page,minutes,end_minute,canonical,absence_category
from injury_warning.rules import utc
from phase1d.logic import day_bounds
from .acquire import D,manifest,read,registration
from .report_parser import parse_report
LABELS={'CLE':'Cavaliers','DEN':'Nuggets','ORL':'Magic','PHI':'76ers','SAS':'Spurs','DET':'Pistons'}
TEAM_LABELS={'CLE':'ClevelandCavaliers','DEN':'DenverNuggets','ORL':'OrlandoMagic','PHI':'Philadelphia76ers','SAS':'SanAntonioSpurs','DET':'DetroitPistons'}
def write(name,records,fields=None):
    records=list(records);out=D/'tables';out.mkdir(exist_ok=True);fields=fields or list(dict.fromkeys(k for r in records for k in r)) or ['row_id']
    with (out/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
def rows(name):
    with (D/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def page_data(sid,sm):
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',read(sid,sm).decode(),re.S)[1])['props']['pageProps']
def timing(gid,day,p):
    actions=p.get('playByPlay',{}).get('actions',[]);lo,hi,raw=end_minute(actions,day);starts=[a for a in actions if a.get('actionType')=='period' and a.get('subType')=='start' and a.get('period')==1];slo=shi=None;sr=''
    if starts:slo,shi,sr=end_minute([dict(starts[0],subType='end')],day)
    if not slo:slo,shi=day_bounds(day)
    return dict(game_id=gid,game_date=day,scheduled_start_utc=p['game'].get('gameTimeUTC'),end_upper=hi or '',end_clock_raw=raw,anchor_lower=slo,anchor_upper=shi,anchor_precision='actual_first_period_start_minute; '+sr if sr else 'documented_day_interval',B_available_at=(utc(hi)+timedelta(hours=6)).isoformat() if hi else '',recap_present=bool(p.get('story',{}).get('content')),source_id='page_'+gid)
def resolve_inactive_reason(pid,family,inactive_players,pdf_entries):
    candidates=[p for p in inactive_players if canonical(p['familyName'])==canonical(family)]
    hits=[reason.strip() for name,reason in pdf_entries if canonical(name.strip())==canonical(family)]
    return hits[0] if len(candidates)==1 and str(candidates[0]['personId'])==pid and len(hits)==1 else None

def prepare():
    from pypdf import PdfReader
    start=time.monotonic();sm=manifest();reg=registration();selected={x['team'] for x in reg['selected']};schedule=json.loads((D/'team_schedule.json').read_text());target=json.loads((D/'targeted_team_games.json').read_text()) if (D/'targeted_team_games.json').exists() else [];games=list({(r['team'],r['game_id']):r for r in schedule+target}.values());logs=[];timings={};recap_candidates=[];people={};pdfs={};pages={};local_recaps=[]
    wanted=defaultdict(set)
    for r in target:wanted[(r['team'],r['game_id'])].update(r['player_ids'])
    for g in sorted(games,key=lambda r:(r['game_date'],r['game_id'],r['team'])):
        gid=g['game_id'];sid='page_'+gid;book='book_'+gid;team=g['team'];day=g['game_date'];phase='history' if day<'2024-01-01' else 'index_period' if day<='2024-02-18' else 'followup'
        if sm.get(sid,{}).get('status')!='obtained':logs.append(dict(team=team,game_id=gid,game_date=day,player_id='',player_name='',appeared=False,minutes=None,roster_observed=False,category='unknown',reason='',coverage='missing_page',phase=phase,page_source=sid,reason_source=book));continue
        if gid not in pages:
            p=page_data(sid,sm);assert str(p['game']['gameId']).startswith('00223');pages[gid]=p;timings[gid]=timing(gid,day,p)
        p=pages[gid];t=next(t for t in [p['game']['homeTeam'],p['game']['awayTeam']] if t['teamTricode']==team)
        if gid not in pdfs and sm.get(book,{}).get('status')=='obtained':
            pdf=PdfReader(BytesIO(read(book,sm)));pdfs[gid]=(pdf.pages[0].extract_text(),pdf.pages[0].extract_text(extraction_mode='layout'))
        text,layout=pdfs.get(gid,('',''));label=LABELS.get(team) or {'ATL':'Hawks','BKN':'Nets','BOS':'Celtics','CHA':'Hornets','CHI':'Bulls','DAL':'Mavericks','GSW':'Warriors','HOU':'Rockets','IND':'Pacers','LAC':'Clippers','LAL':'Lakers','MEM':'Grizzlies','MIA':'Heat','MIL':'Bucks','MIN':'Timberwolves','NOP':'Pelicans','NYK':'Knicks','OKC':'Thunder','PHX':'Suns','POR':'Trail Blazers','SAC':'Kings','TOR':'Raptors','UTA':'Jazz','WAS':'Wizards'}.get(team)
        m=re.search(r'Inactive:\s*'+re.escape(label)+r'\s*-\s*(.*?)(?=Inactive:|Points in the Paint:)',text,re.S|re.I) if text else None
        inactive=re.findall(r'([^(),]+)\s*\(([^)]+)\)',m[1].replace('\n',' ')) if m else []
        for pp in {str(pp['personId']):pp for pp in t['players']+t['inactives']}.values():
            pid=str(pp['personId']);name=pp['firstName']+' '+pp['familyName'];is_selected=team in selected
            if not is_selected and pid not in wanted[(team,gid)]:continue
            mins=minutes(pp.get('statistics',{}).get('minutes')) or 0;played=mins>0;reason=pp.get('comment','');hits=[r.strip() for fam,r in inactive if canonical(fam.strip())==canonical(pp['familyName'])]
            inactive_ids={str(x['personId']) for x in t['inactives']}
            if not played:
                resolved=resolve_inactive_reason(pid,pp['familyName'],t['inactives'],inactive)
                if resolved:reason=resolved
            if not played and layout:
                matches=[line for line in layout.splitlines() if canonical(name) in canonical(line) and re.search(r'(?:DND|DNP|NWT) -',line)]
                if len(matches)==1:reason=re.search(r'(?:DND|DNP|NWT) -.*',matches[0])[0].strip()
            if not played and reason.lower()=='dnp':reason=''
            logs.append(dict(team=team,game_id=gid,game_date=day,player_id=pid,player_name=name,appeared=played,minutes=mins,minutes_source_raw=pp.get('statistics',{}).get('minutes',''),roster_observed=True,category='appearance' if played else absence_category(reason),reason=reason,coverage='page_and_book' if text else 'page_only',phase=phase,page_source=sid,reason_source=book if text else '',scope='sampled_team_inventory' if is_selected else 'targeted_cross_team_only'))
            people[pid]=dict(player_id=pid,player_name=name,first_name=pp['firstName'],family_name=pp['familyName'])
        if team in selected:
            roster={str(pp['personId']):pp for pp in t['players']+t['inactives']}
            for i,para in enumerate(p.get('story',{}).get('content',[])):
                # All injury-bearing paragraphs enter review; no automatic acute-event exclusion.
                if re.search(r'injur|sprain|strain|sore|hurt|fractur|concuss|surg|tendin|pain|knee|ankle|hamstring|shoulder|illness|return|missed|limp|MRI|locker room|bleed|contusion|bruise',str(para),re.I):
                    ids=[pid for pid,pp in roster.items() if canonical(pp['familyName']) in canonical(str(para)) and len(pp['familyName'])>3]
                    recap_candidates.append(dict(team=team,game_id=gid,game_date=day,paragraph=i,player_ids=';'.join(ids),source_id=sid,locator=f'story.content[{i}]',B_available_at=timings[gid]['B_available_at']))
                    local_recaps.append(dict(team=team,game_id=gid,game_date=day,paragraph=i,player_ids=ids,text=para))
    reports=[]
    ids={r['source_id'] for r in json.loads((D/'request_catalog.json').read_text()) if r['kind']=='report'}
    cached_reports={r['source_id']:r for r in json.loads((D/'parsed_reports.json').read_text())} if (D/'parsed_reports.json').exists() else {}
    for sid in sorted(ids):
        if sid in cached_reports:
            reports.append(cached_reports[sid]);continue
        r=sm[sid];out=dict(source_id=sid,retrieval_status=r['status'],date=r['date'])
        if r['status']=='obtained':
            try:
                parsed=parse_report(read(sid,sm));out.update(report_at=parsed['report_at'],B_available_at=(utc(parsed['report_at'])+timedelta(minutes=30)).isoformat(),sections=[v for v in parsed['sections'] if v['team'] in TEAM_LABELS.values()],observations=[v for v in parsed['observations'] if v['team'] in TEAM_LABELS.values()])
            except Exception as exc:out.update(error=str(exc),sections=[],observations=[])
        else:out.update(sections=[],observations=[])
        reports.append(out)
    searches=[]
    for f in sorted((CACHE_SEARCH:=ROOT/'data/raw/phase2a/searches').glob('*.json')):
        b=f.read_bytes();o=json.loads(b)
        for q in o['queries']:searches.append(dict(q,status=o['status'],retrieved_at=o['retrieved_at'],sha256=hashlib.sha256(b).hexdigest(),raw_file=str(f.relative_to(ROOT)),scope='dated_index_search_not_exhaustive; raw hits require original source review before B use'))
    # Full-name report evidence resolves duplicate-surname PDF entries only when
    # the actual roster confirms nonappearance and the report targets that exact game.
    fullnames={canonical(v['family_name']+', '+v['first_name']):pid for pid,v in people.items()}
    from .surveillance import FOLLOWUP_LABELS
    inverse={v:k for k,v in FOLLOWUP_LABELS.items()};reason_reports=defaultdict(list)
    for rp in reports:
        for o in rp['observations']:
            pid=fullnames.get(canonical(o['player_name_raw']));team=inverse[o['team']]
            if pid and o['status']=='Out':reason_reports[(team,pid,o['target_game_date'])].append((rp,o))
    for r in logs:
        if r['appeared'] or r['reason']:continue
        hits=reason_reports.get((r['team'],r['player_id'],r['game_date']),[])
        if hits:
            rp,o=max(hits,key=lambda v:utc(v[0]['report_at']));r['reason']=o['reason'];r['category']=absence_category(o['reason']);r['reason_source']=rp['source_id'];r['reason_locator']=o['evidence_locator']+'; full-name report for verified actual nonappearance, C outcome only'
    write('player_games',logs);write('players',people.values());write('game_timing',timings.values());write('recap_review_candidates',recap_candidates)
    (D/'parsed_reports.json').write_text(json.dumps(reports,indent=2)+'\n');(D/'search_ledger.json').write_text(json.dumps(searches,indent=2)+'\n');(ROOT/'data/raw/phase2a/recap_review.json').write_text(json.dumps(local_recaps,indent=2)+'\n')
    result=dict(team_game_records=len(games),player_game_records=len(logs),distinct_players=len(people),parsed_reports=len(reports),search_queries=len(searches),elapsed_seconds=round(time.monotonic()-start,2));(D/'parsing_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':
    prepare()
    from .surveillance import refresh
    refresh()
