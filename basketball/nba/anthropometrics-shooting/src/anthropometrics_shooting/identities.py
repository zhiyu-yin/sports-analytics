from collections import defaultdict
from .normalize import name_key

def classify(measured,players):
    """Players must be one row per identity. Names never override conflicting IDs."""
    ids=defaultdict(list); names=defaultdict(list)
    for p in players:
        if p.get('player_id'): ids[p['player_id']].append(p)
        if name_key(p.get('player_name')): names[name_key(p['player_name'])].append(p)
    output=[]
    for r in measured:
        pid=r.get('player_id'); matches=ids.get(pid,[]) if pid else []
        status='unmatched'; target=None
        if len(matches)==1: status='exact ID'; target=matches[0]['player_id']
        elif len(matches)>1: status='ambiguous'
        else:
            candidates=names.get(name_key(r.get('player_name')),[])
            if len(candidates)>1: status='ambiguous'
            elif len(candidates)==1:
                if pid and candidates[0].get('player_id') and pid!=candidates[0]['player_id']:
                    status='manually reviewable'
                else: status='exact normalized name'; target=candidates[0].get('player_id')
        output.append(dict(r,join_status=status,matched_player_id=target))
    return output
