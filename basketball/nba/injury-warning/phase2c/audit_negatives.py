"""Independent source-read path for the60 seeded negative traces (same agent)."""
from io import BytesIO
from collections import Counter
from .pipeline import rows,write,manifest,read
from injury_warning.longitudinal import parse_game_page,canonical

def audit():
    from pypdf import PdfReader
    sm=manifest();pages={};books={};people={r['player_id']:r for r in rows('players')};checks=[];ev={r['event_id']:r for r in rows('events')}
    for r in rows('negative_sample_review'):
        assertions=[]
        for gid in r['window_game_ids'].split(';'):
            if not gid:continue
            if gid not in pages:pages[gid]=parse_game_page(read('page_'+gid,sm))[0]
            if gid not in books:books[gid]=PdfReader(BytesIO(read('book_'+gid,sm))).pages[0].extract_text()
            pp=pages[gid];team=next(t for t in [pp['homeTeam'],pp['awayTeam']] if any(str(p['personId'])==r['player_id'] for p in t['players']+t['inactives']))
            person=next(p for p in team['players']+team['inactives'] if str(p['personId'])==r['player_id'])
            # Book inactive lists may use surname only. The page's canonical PID
            # disambiguates identity; no reason is reassigned from surname alone.
            assert canonical(person['familyName']).replace('jr','') in canonical(books[gid]).replace('jr',''),(gid,r['player_id'])
            assertions.append(dict(game_id=gid,actual_team=team['teamTricode'],pid_on_original_page=True,book_name_present=True,book_source='book_'+gid,page_source='page_'+gid))
        ee=[ev[x] for x in r['event_ids'].split(';') if x]
        assert all(e['severity']=='negative' and e['possible_run_upper'] and int(e['possible_run_upper'])<10 for e in ee),r['row_id']
        checks.append(dict(row_id=r['row_id'],team=r['team'],player_id=r['player_id'],player_name=people[r['player_id']]['player_name'],extra_lag_days=r['extra_lag_days'],source_games_reopened=len(assertions),all_original_PID_and_book_name_checks_passed=True,in_horizon_candidate_upper_bounds=';'.join(e['possible_run_upper'] for e in ee),source_ids=';'.join(a['page_source']+';'+a['book_source'] for a in assertions),exact_locators='Original __NEXT_DATA__.game home/away players+inactives canonical personId; official FINAL BOX p1 active/inactive name; row_event_links exact temporal memberships',review='Original source reread and candidate bounds reviewed. Conditional negative under bounded process; not evidence of complete public archive or symptom-free status.',reviewer='Codex same agent; not independent human',independent_human_review=False))
    write('negative_original_source_audit',checks)
    print('Source-reread rows',len(checks),'distinct original games/books',len(books))
    for r in checks:print(r['team'],r['extra_lag_days'],r['player_name'],r['row_id'],'source_games',r['source_games_reopened'],'candidate_upper',r['in_horizon_candidate_upper_bounds'] or 'none')
if __name__=='__main__':audit()
