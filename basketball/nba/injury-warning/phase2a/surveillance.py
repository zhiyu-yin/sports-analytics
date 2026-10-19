"""Shared report extraction and actual executed-query receipts, including targeted transfers."""
from datetime import timedelta
import json,hashlib,time
from injury_warning.rules import utc
from .acquire import D,ROOT,manifest,read
from .report_parser import parse_report
FOLLOWUP_LABELS={'CLE':'ClevelandCavaliers','DEN':'DenverNuggets','ORL':'OrlandoMagic','PHI':'Philadelphia76ers','SAS':'SanAntonioSpurs','DET':'DetroitPistons','WAS':'WashingtonWizards','MIN':'MinnesotaTimberwolves','NYK':'NewYorkKnicks','MIL':'MilwaukeeBucks','IND':'IndianaPacers','BOS':'BostonCeltics','UTA':'UtahJazz','OKC':'OklahomaCityThunder','MEM':'MemphisGrizzlies','TOR':'TorontoRaptors'}
def refresh():
    start=time.monotonic();parser_hash=hashlib.sha256((D/'report_parser.py').read_bytes()).hexdigest();sm=manifest();req=json.loads((D/'request_catalog.json').read_text());old={r['source_id']:r for r in json.loads((D/'parsed_reports.json').read_text())} if (D/'parsed_reports.json').exists() else {};reports=[]
    for sid in sorted({r['source_id'] for r in req if r['kind']=='report'}):
        if old.get(sid,{}).get('parser_sha256')==parser_hash and old.get(sid,{}).get('report_parse_scope')=='sampled_plus_targeted_transfer_v1':reports.append(old[sid]);continue
        r=sm[sid];out=dict(source_id=sid,date=r['date'],retrieval_status=r['status'],report_parse_scope='sampled_plus_targeted_transfer_v1',parser_sha256=parser_hash)
        if r['status']=='obtained':
            try:
                p=parse_report(read(sid,sm));out.update(report_at=p['report_at'],B_available_at=(utc(p['report_at'])+timedelta(minutes=30)).isoformat(),sections=[s for s in p['sections'] if s['team'] in FOLLOWUP_LABELS.values()],observations=[o for o in p['observations'] if o['team'] in FOLLOWUP_LABELS.values()])
            except Exception as exc:out.update(error=str(exc),sections=[],observations=[])
        else:out.update(sections=[],observations=[])
        reports.append(out)
    (D/'parsed_reports.json').write_text(json.dumps(reports,indent=2)+'\n');queries=[]
    for f in sorted((ROOT/'data/raw/phase2a/searches').glob('*.json')):
        b=f.read_bytes();o=json.loads(b)
        for q in o['queries']:queries.append(dict(q,status=o['status'],retrieved_at=o['retrieved_at'],sha256=hashlib.sha256(b).hexdigest(),raw_file=str(f.relative_to(ROOT)),scope=q.get('scope','fixed_six_team_dated_search')))
    (D/'search_ledger.json').write_text(json.dumps(queries,indent=2)+'\n')
    # Outcome-only reason completion for verified actual nonappearances; no predictor changes.
    from .prepare import rows,write
    from injury_warning.longitudinal import canonical,absence_category
    from collections import defaultdict
    people={canonical(p['family_name']+', '+p['first_name']):p['player_id'] for p in rows('players')};lookup=defaultdict(list);inverse={v:k for k,v in FOLLOWUP_LABELS.items()}
    for rp in reports:
        for o in rp['observations']:
            pid=people.get(canonical(o['player_name_raw']))
            if pid and o['status']=='Out':lookup[(inverse[o['team']],pid,o['target_game_date'])].append((rp,o))
    pg=rows('player_games')
    for r in pg:
        if r['appeared']=='False' and not r['reason'] and r['roster_observed']=='True':
            hits=lookup.get((r['team'],r['player_id'],r['game_date']),[])
            if hits:
                rp,o=max(hits,key=lambda x:utc(x[0]['report_at']));r.update(reason=o['reason'],category=absence_category(o['reason']),reason_source=rp['source_id'],reason_locator=o['evidence_locator']+'; full-name snapshot for verified actual nonappearance, C only')
    write('player_games',pg)
    print('report sources',len(reports),'executed queries',len(queries),'seconds',round(time.monotonic()-start,2))
if __name__=='__main__':refresh()
