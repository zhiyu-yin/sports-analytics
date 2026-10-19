"""Readable selected decision traces, separate from all retained machine records."""
from .acquire import D,ROOT
from .prepare import rows

def render_timelines():
    co=rows('cohort_all_roster_candidates');out={r['row_id']:r for r in rows('row_outcomes')};fs={r['row_id']:r for r in rows('features_B')};events=rows('events');members=rows('event_game_evidence')
    examples=[('203914','2024-01-02','Gary Harris: decision lag crosses acute disclosure'),('1630587','2024-01-12','Isaiah Livers: DET index, WAS absence event'),('1629001','2024-01-10','Melton: known back symptoms, separate prolonged run'),('203954','2024-01-25','Embiid: knee history before later Jan30 trauma'),('203954','2024-01-16','Embiid: first miss outside these 14-day windows'),('1631124','2024-01-01','Strawther: uncertain common-episode attribution'),('1630191','2024-01-28','Stewart: injury/coaching/suspension mixture'),('1628386','2024-01-11','Allen: complete negative sequence')]
    # Use observed stable player name/ID if the human-selected display key differs.
    straw=next(r['player_id'] for r in co if 'Strawther' in r['player_name']);examples=[(straw if title.startswith('Strawther') else pid,day,title) for pid,day,title in examples]
    text=['# Phase 2A selected evidence timelines','All source availability below is category B unless marked retrospective C. No label is claimed historically training-ready. Same-agent review is not independent human adjudication.']
    for pid,day,title in examples:
        rr=[r for r in co if r['player_id']==pid and r['index_game_date']==day];text+=['\n## '+title]
        if not rr:text+=['No matching index row; see complete machine tables.'];continue
        for c in rr:
            o=out.get(c['row_id']);f=fs.get(c['row_id']);text += [f"\n**{c['row_id']}** — {c['player_name']}, {c['team']}, index {day}; {c['index_minutes']} minutes. Decision `{c['decision_at']}`; horizon ends `{c['window_end']}`. B eligibility **{c['B_state']}**: {c['B_reason']}.",f"Final game end upper `{c['game_end_upper']}`; final stats/recap assumed available `{c['stats_recap_B_available_at']}`. Baseline: `{c['baseline_report_ids']}`. Decision snapshots: `{c['decision_report_ids']}`. Exclusion evidence: `{c['B_exclusion_source_ids']}`."]
            if not o:continue
            text += [f"Outcome **{o['absence_run_onset_ge10']}**; B group **{o['group_B']}**, A timing **{o['group_A']}**. Onset surveillance `{o['onset_surveillance_B']}`, severity follow-up `{o['severity_followup_B']}`. Label known-at remains blank."]
            if f:text += [f"Past NBA history complete `{f['history_complete']}`; input teams `{f['input_teams']}`; max input availability `{f['max_input_assumed_available_at']}`. 28-day minutes `{f['minutes_28d']}`. Exact input IDs: `{f['input_game_ids']}`."]
            ee=[e for e in events if e['player_id']==pid and (e['event_id'] in o['event_ids'].split(';') or c['decision_at'][:10]<=e['anchor_date']<=c['window_end'][:10])]
            if not ee:ee=[e for e in events if e['player_id']==pid and e['severity']=='positive'][:1]
            for e in ee:
                gg=[g for g in members if g['event_id']==e['event_id']];text += [f"C event `{e['event_id']}`: first observed anchor `{e['run_lower']}`–`{e['run_upper']}`, actual team {e['anchor_team']}, severity **{e['severity']}**. Confirmed same-episode lower bound {e['confirmed_same_episode_games']}; possible upper `{e['possible_run_upper']}`; mixed categories `{e['mixed_categories']}`. Return `{e['return_date']}` ends the run without asserting recovery.",f"Continuity sources: `{e.get('continuity_source_ids','')}`; `{e.get('continuity_locator','')}`. Review: {e.get('continuity_review_note',e['reason'])}","First ten observed game checks: "+'; '.join(f"{g['game_date']} {g['team']} {g['game_id']} [{g['category']}; {g['reason_source']}]" for g in gg[:10])+'.']
    text+=['\n## Covington: unresolved event with no eligible preceding January decision','The Jan2 first miss is retained in inventory. The Jan6 named final-box row explicitly records illness; the later calendar-year knee summary does not settle this mixed attribution at the initial anchor. It is not counted as a confirmed qualifying event or silently attached to a nonexistent January preceding appearance. See `episode_adjudications.json` and the event review table.','\nAll 19 positive decision rows, 60 reproducibly sampled negative decisions and representative unresolved decisions have full joins in `phase2a/traced_cases.json`. The two timing rules are sensitivity analyses, not independent replications.']
    (ROOT/'docs/phase2a_timelines.md').write_text('\n\n'.join(text)+'\n')
if __name__=='__main__':render_timelines()
