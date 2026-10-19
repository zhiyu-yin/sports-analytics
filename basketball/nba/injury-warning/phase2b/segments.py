"""Maximal injury-only segments; reviewed common identity and original anchor are separate."""
import json
from .io import D,write
SEGMENTS=[]
def maximal_segments(block):
    out=[];part=[]
    for g in block+[{}]:
        valid=(g.get('category')=='injury' and g.get('roster_observed') is True and g.get('coverage')=='page_and_book' )
        if valid:
            if g.get('membership_gap_before') and part:out.append(part);part=[]
            part.append(g)
        else:
            if part:out.append(part)
            part=[]
    return out

def adjudicate_segments(e,block,manual=None):
    reviews=json.loads((D/'segment_reviews.json').read_text()) if (D/'segment_reviews.json').exists() else {}
    candidates=maximal_segments(block);r=reviews.get(e['player_id']+'_'+e['anchor_date'],{})
    if e.get('return_date') and not e.get('left_censored_start') and not e.get('contract_gap_in_run'):
        # Missing reason/roster can leave attribution unknown, but not the number
        # of games in a complete applicable-team schedule closed by appearance.
        upper=len(block);e['schedule_upper_bound']=upper
        if upper<10:e.update(possible_run_upper=upper,severity='negative',reason='complete closed applicable schedule bounds total misses below ten')
    best=0;anchor_ok=False
    for i,part in enumerate(candidates):
        existing=bool(manual and manual.get('common_episode_supported') and part[0]['game_date']<=manual['supported_through'])
        count=sum(g['game_date']<=manual['supported_through'] for g in part) if existing else 0
        reviewed=bool(r.get('common_episode_supported') and r.get('segment_start')==part[0]['game_date'])
        review_count=sum(g['game_date']<=r.get('supported_through',part[-1]['game_date']) for g in part)
        supported=(existing and count>=10) or (reviewed and review_count>=10)
        anchor=bool(supported and (existing or r.get('original_anchor_supported')))
        if supported:best=max(best,count if existing else review_count);anchor_ok|=anchor
        SEGMENTS.append(dict(event_id=e['event_id'],segment_number=i+1,player_id=e['player_id'],player_name=e['player_name'],envelope_anchor_date=e['anchor_date'],segment_start=part[0]['game_date'],segment_end=part[-1]['game_date'],consecutive_injury_games=len(part),threshold_met=len(part)>=10,common_episode_supported=supported,original_anchor_supported=anchor,segment_game_ids=';'.join(g['game_id'] for g in part),source_ids=';'.join(sorted({g['page_source'] for g in part}|{g['reason_source'] for g in part})),continuity_source_ids=manual.get('source_ids','') if existing else r.get('source_ids',''),review_note=manual.get('note','') if existing else r.get('note','Complete individual injury segment; common identity beyond repeated diagnosis and its relation to the preserved envelope anchor not established from acquired total evidence. Not automatically positive.'),evidence_role='C_only'))
    e['longest_injury_only_segment']=max([len(p) for p in candidates] or [0]);e['qualifying_segment_established']=best>=10;e['anchor_identity_uncertain']=bool(best>=10 and not anchor_ok)
    if best>=10 and anchor_ok:
        e.update(severity='positive',continuity_supported=True,confirmed_same_episode_games=max(best,e['confirmed_same_episode_games']))
        if r:e.update(continuity_source_ids=r['source_ids'],continuity_review_note=r['note'],continuity_locator=r['locator'])
    elif best>=10:e.update(severity='unknown',continuity_supported=False)

def flush():write('injury_segments',SEGMENTS)
