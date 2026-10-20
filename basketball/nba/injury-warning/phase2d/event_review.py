"""Outcome-only original narrative retrieval and exhaustive unresolved ledger."""
import json,re
from . import runtime as rt
from .runtime import D,ROOT,bd,rows,write,manifest,activity
from phase2a.acquire import read
from injury_warning.longitudinal import canonical
from .review import MED

def inspect():
    sm=manifest();pg=rows('player_games');out=[]
    for e in rows('events'):
        if e['severity']=='negative' or e['candidate_broad_onset_period']!='True':continue
        print('\nEVENT',e['player_id'],e['player_name'],e['anchor_date'],'longest medical',e['longest_injury_only_segment'],'return',e['return_date'])
        own=[g for g in pg if g['player_id']==e['player_id'] and g['game_date']>=e['anchor_date']];name=e['player_name'].split()[-1];name=re.sub(r'^(Jr\.|Sr\.|II|III|IV)$','',name) or e['player_name'].split()[-2]
        chosen=set();snippets=[]
        for g in own:
            sid=g['page_source']
            if sid in chosen:continue
            chosen.add(sid)
            if sm.get(sid,{}).get('status')!='obtained':continue
            raw=read(sid,sm).decode();m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',raw,re.S)
            if not m:continue
            p=json.loads(m[1])['props']['pageProps']
            for i,t in enumerate(p.get('story',{}).get('content',[])):
                if canonical(name) in canonical(str(t)) and re.search(MED,str(t),re.I):snippets.append(dict(source_id=sid,date=g['game_date'],paragraph=i,text=t))
        # Full source cards stay ignored. Show medical-bearing contexts first,
        # including return, explicit cumulative missed counts and treatment.
        core=[s for s in snippets if re.search(r'miss|return|surg|strain|sprain|sore|injur|fract|re.evaluat|tendin|ruled|week',str(s['text']),re.I)]
        for s in core[:6]+core[-3:]:print(s['source_id'],s['date'],'p'+str(s['paragraph']),s['text'])
        out.append(dict(event=e,narrative_candidates=snippets))
    (ROOT/'data/raw/phase2d'/('batch'+str(rt.BATCH))/'event_narrative_cards.json').write_text(json.dumps(out,indent=2)+'\n')
def inherit():
    pgids={r['player_id'] for r in rows('player_games')};out={}
    for ph in ['phase2b','phase2c']:
        for k,v in json.loads((ROOT/ph/'episode_adjudications.json').read_text()).items():
            if k.split('_')[0] in pgids:out[k]=v
    path=bd()/'new_episode_reviews.json'
    if path.exists():out.update(json.loads(path.read_text()))
    (bd()/'episode_adjudications.json').write_text(json.dumps(out,indent=2)+'\n')
    limits=json.loads((bd()/'identity_limitations.json').read_text()) if (bd()/'identity_limitations.json').exists() else {}
    ledger=[]
    for e in rows('events'):
        if e['severity']=='negative':continue
        gg=[g for g in rows('event_game_evidence') if g['event_id']==e['event_id']]
        ledger.append(dict(event_id=e['event_id'],player_id=e['player_id'],player_name=e['player_name'],anchor_date=e['anchor_date'],maximal_injury_only_games=e['longest_injury_only_segment'],review='Original individual game sequence, maximal segments, roster bounds and available narratives inspected. Existing C continuity data reused only for same player/anchor. Matching diagnosis alone insufficient; absent linkage remains unknown.',common_episode_review_key=e['player_id']+'_'+e['anchor_date'] if e['player_id']+'_'+e['anchor_date'] in out else '',source_ids=e['source_ids'],specific_identity_limitation=limits.get(e['player_id']+'_'+e['anchor_date'],''),original_anchor_retained=True,independent_human_review=False))
    write('event_review_ledger',ledger);print('reused/new common episode assertions',len(out),'nonnegative reviews',len(ledger))
if __name__=='__main__':
    import sys
    globals()[sys.argv[1]]()
