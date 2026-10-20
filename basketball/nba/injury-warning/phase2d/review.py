"""Locator-based source review inventory; accepted assertions are explicit input data."""
import json,re
from collections import defaultdict
from . import runtime as rt
from .runtime import ROOT,D,bd,SPEC,manifest,activity,write,rows
from injury_warning.longitudinal import parse_game_page,canonical
from phase2a.acquire import read
MED=r'injur|sprain|strain|sore|hurt|fractur|concuss|surg|tendin|pain|knee|ankle|hamstring|shoulder|illness|limp|MRI|locker.room|contusion|bruise|back.spasm|wrist|foot|elbow|groin|calf|quad|finger|Achilles|hip|disc'
def cards():
    from .names import without_suffix
    import os
    fixed=os.environ.get('PHASE2D_SUFFIX_FIX','1')=='1'
    prior=ROOT/'data/raw/phase2d'/('batch'+str(rt.BATCH))/'review_cards.json'
    old=json.loads(prior.read_text()) if prior.exists() else []
    existing={(c['game_id'],c['paragraph'],pid) for c in old for pid in c['players']}
    sm=manifest();selected={t['team'] for t in SPEC['batches'][rt.BATCH-1]};out=old if fixed else [];seen=set()
    for g in sorted(json.loads((bd()/'team_schedule.json').read_text()),key=lambda r:(r['game_date'],r['game_id'])):
        if g['game_date']>'2024-02-17':continue
        sid='page_'+g['game_id'];r=sm.get(sid,{})
        if r.get('status')!='obtained':continue
        b=read(sid,sm);p=json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',b.decode(),re.S)[1])['props']['pageProps'];team=next(t for t in [p['game']['homeTeam'],p['game']['awayTeam']] if t['teamTricode']==g['team']);people={str(v['personId']):v for v in team['players']+team['inactives']}
        for i,para in enumerate(p.get('story',{}).get('content',[])):
            if not re.search(MED,str(para),re.I):continue
            ids=[pid for pid,v in people.items() if (canonical(without_suffix(v['familyName'])) if fixed else re.sub(r'\b(jr|sr|ii|iii|iv)\b','',canonical(v['familyName'])).strip()) in canonical(str(para)) and len(v['familyName'])>2]
            if fixed:ids=[pid for pid in ids if (g['game_id'],i,pid) not in existing]
            if not ids:continue
            key=(g['game_id'],i,tuple(ids))
            if key in seen:continue
            seen.add(key);out.append(dict(card_id=len(out),game_id=g['game_id'],game_date=g['game_date'],team=g['team'],paragraph=i,text=para,players={pid:people[pid]['firstName']+' '+people[pid]['familyName'] for pid in ids}))
    path=ROOT/'data/raw/phase2d'/('batch'+str(rt.BATCH))/'review_cards.json';path.write_text(json.dumps(out,indent=2)+'\n');print('cards',len(out))
    for c in out:print(str(c['card_id'])+' '+c['game_date']+' '+json.dumps(c['players'])+' '+str(c['text']))
def apply():
    cardpath=ROOT/'data/raw/phase2d'/('batch'+str(rt.BATCH))/'review_cards.json';cards=json.loads(cardpath.read_text());mapping=json.loads((bd()/'recap_review_decisions.json').read_text());signals=[];ledger=[]
    # Previously reviewed original A/B paragraphs may be reused for actual
    # players across batches; their availability remains source-specific.
    known=[]
    for ph in ['phase2b','phase2c']:known+=json.loads((ROOT/ph/'recap_adjudications.json').read_text())
    available={r['game_id'] for r in rows('game_timing')};pids={r['player_id'] for r in rows('players')}
    signals=[s for s in known if s['player_id'] in pids and s['source_game_id'] in available]
    for c in cards:
        m=mapping.get(str(c['card_id']),{});accepted=[]
        for kind in ['history','acute']:
            for pid in m.get(kind,[]):
                assert pid in c['players'];accepted.append(pid);signals.append(dict(player_id=pid,source_game_id=c['game_id'],event_game_id=c['game_id'],paragraph=c['paragraph'],kind=kind,locator='story.content['+str(c['paragraph'])+']',review_note='Explicit same-agent medical assertion review; canonical player disambiguated; no retrospective C news used.'))
        ledger.append(dict(card_id=c['card_id'],source_id='page_'+c['game_id'],date=c['game_date'],locator='story.content['+str(c['paragraph'])+']',proposed_pids=';'.join(c['players']),accepted_pids=';'.join(accepted),decision='accept_explicit_assertion' if accepted else 'reject_no_specific_medical_assertion_opponent_or_nonmedical',reviewer='Codex same agent, not independent human',evidence='B final-recap assumption only'))
    signals=list({(s['player_id'],s['source_game_id'],s['paragraph'],s['kind']):s for s in signals}.values());(bd()/'recap_adjudications.json').write_text(json.dumps(signals,indent=2)+'\n');write('recap_review_decisions',ledger);print('signals',len(signals),'cards',len(cards))
if __name__=='__main__':
    import sys
    globals()[sys.argv[1]]()
