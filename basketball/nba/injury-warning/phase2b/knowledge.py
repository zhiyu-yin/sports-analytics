"""B-only memory is cumulative; status is game-specific and expires explicitly."""
from injury_warning.rules import utc
from phase1c.logic import add_elapsed
COMPLETIONS={}
def knowledge(t,pid,observations,signals):
    oo=[o for o in observations if o['player_id']==pid and utc(o['B_available_at'])<=utc(t)]
    ss=[s for s in signals if s['player_id']==pid and utc(s['B_available_at'])<=utc(t)]
    inj=[o for o in oo if o['category']=='injury'];cut=utc(add_elapsed(t,days=-28))
    recent=[o for o in inj if utc(o['B_available_at'])>=cut]+[s for s in ss if utc(s['B_available_at'])>=cut]
    latest={}
    for o in sorted(oo,key=lambda o:(utc(o['B_available_at']),o['observation_id'])):
        latest[(o['team'],o['target_game_date'])]=o
    current=[];expired=[]
    # t is the registered Eastern noon; use its local calendar date, not UTC date.
    for key,o in latest.items():
        end=COMPLETIONS.get(key)
        if (end and utc(end)<=utc(t)) or (not end and o['target_game_date'] and o['target_game_date']<t[:10]):expired.append(o)
        elif o['target_game_date']:current.append(o)
    ids=[o['observation_id'] for o in inj]+[s['signal_id'] for s in ss]
    history=bool(ids);acute=[s for s in ss if s['kind']=='acute']
    return dict(ever_known_injury_history_B=history,recent_known_symptoms_28d_B=bool(recent),current_status_observation_ids=';'.join(o['observation_id'] for o in current),expired_status_observation_ids=';'.join(o['observation_id'] for o in expired),explicit_superseding_available_ids=';'.join(o['observation_id'] for o in current if o['status']=='Available'),any_prior_acute_disclosure_B=bool(acute),acute_known_B=False,same_event_disclosure_evaluated=False,symptoms_history_known_B=history,signal_ids=';'.join(ids),group_B='symptom_or_history_known' if history else 'no_signal_found_under_searched_process',group_A='knowledge_timing_unresolved',A_verified=False)
def positive_event_knowledge(t,pid,observations,signals,events):
    k=knowledge(t,pid,observations,signals)
    related={gid for e in events for gid in e.get('acute_event_game_ids','').split(';') if gid}
    same=[s for s in signals if s['player_id']==pid and s['kind']=='acute' and s['event_game_id'] in related and utc(s['B_available_at'])<=utc(t)]
    k.update(acute_known_B=bool(same),same_event_disclosure_evaluated=True,group_B='acute_already_disclosed' if same else k['group_B'],signal_relation_to_future_run='same acute event; retrospective C linkage of prior B disclosure' if same else 'prior history only; episode identity not inferred' if k['ever_known_injury_history_B'] else 'no signal in acquired B history')
    return k
