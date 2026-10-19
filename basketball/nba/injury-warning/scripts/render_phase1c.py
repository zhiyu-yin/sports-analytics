#!/usr/bin/env python3
"""Render actual Phase 1C results, sensitivity comparisons, trace records and review queue."""
import sys,csv,json,hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from phase1c.sources import CROOT,ROOT,manifest
from phase1c.build import write


def rows(name):
    with (CROOT/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))


def main():
    c=rows('cohort_all_candidates');out={r['row_id']:r for r in rows('row_outcomes')};feats={r['row_id']:r for r in rows('features_assumption_B')};eps=rows('episode_candidates');sm=manifest()
    bykey={r['row_id']:r for r in c};comparisons=[]
    for r in c:
        if r['extra_lag_days']!='0':continue
        other=bykey[r['row_id'][:-1]+'1'];a=out.get(r['row_id'],{});b=out.get(other['row_id'],{});fa=feats.get(r['row_id'],{});fb=feats.get(other['row_id'],{})
        comparisons.append(dict(index_game_id=r['index_game_id'],index_game_date=r['index_game_date'],player_id=r['player_id'],base_decision_at=r['decision_at'],extra_day_decision_at=other['decision_at'],base_window_end=r['window_end'],extra_day_window_end=other['window_end'],base_B_state=r['B_state'],extra_day_B_state=other['B_state'],base_primary=a.get('primary_ge10','not_labeled_not_included'),extra_day_primary=b.get('primary_ge10','not_labeled_not_included'),base_secondary=a.get('secondary_public_gt28','not_labeled_not_included'),extra_day_secondary=b.get('secondary_public_gt28','not_labeled_not_included'),base_minutes_7d=fa.get('minutes_7d',''),extra_day_minutes_7d=fb.get('minutes_7d',''),base_input_game_ids=fa.get('input_game_ids',''),extra_day_input_game_ids=fb.get('input_game_ids',''),B_eligibility_changed=r['B_state']!=other['B_state']))
    write('lag_sensitivity_comparison',comparisons)
    reviewed=[]
    for e in eps:
        if e['primary_ge10']=='unknown' or e['secondary_public_gt28']=='unknown':
            late='2024-04-12'==e['first_injury_missed_game']
            reviewed.append(dict(episode_id=e['episode_id'],player_id=e['player_id'],player_name=e['player_name'],reviewer='Codex same agent; independent human review not performed',question='Recover episode start before cached history or before Boston arrival; no pre-join schedule is silently counted.' if e['left_censored_start']=='True' else 'Resolve onset lower bound and season-end mixed injury/rest attribution; do not infer onset from last appearance or rest-only cause from prose alone.',evidence_ids=e['source_ids'],conflicting_recap_source_id='page_0022301173' if late else '',conflicting_recap_locator='story.content[5]: recap describes nagging ailments and an effective rest night; gamebook lists injury reasons' if late else '',latest_recap_source_id='page_0022301186' if late else '',latest_recap_locator='story.content[0]: season finale rested entire starting lineup' if late else '',decision='',notes='',evidence_category='C_retrospective_conflict'))
    write('remaining_review_queue',reviewed)
    quality=[]
    with (ROOT/'pilot/tables/player_games.csv').open() as f:
        for r in csv.DictReader(f):
            if r['minutes_normalization']!='none':quality.append(dict(source_id=r['source_id'],player_id=r['player_id'],game_date=r['game_date'],issue='source minute carry',raw_value=r['minutes_source_raw'],normalized_value=r['minutes'],used_in_pilot_feature_windows=False))
    with (ROOT/'pilot/tables/gamebook_checks.csv').open() as f:
        for r in csv.DictReader(f):
            if r['minute_sum_ok']=='False':quality.append(dict(source_id=r['structured_source_id'],player_id='',game_date='',issue='team minutes differ from expected total',raw_value=r['minutes_total'],normalized_value='not silently corrected; expected '+r['expected_minutes'],used_in_pilot_feature_windows=True))
    write('source_quality_issues',quality)
    chosen={('204001','2024-01-25'),('204001','2024-02-14'),('1628369','2024-01-05'),('1630202','2024-01-02'),('1628436','2024-01-27'),('1641775','2024-02-14')}
    traces=[]
    text=['# Traced Phase 1C timelines','',
          'All included states below are category B under the registered publication assumptions. A verified eligibility remains unknown for every appearance. Evidence available only retrospectively cannot change the earlier inclusion decision.','']
    for r in c:
        if (r['player_id'],r['index_game_date']) not in chosen:continue
        a=out.get(r['row_id']);f=feats.get(r['row_id']);sourceids=r['source_ids'].split(';')
        receipts=[{k:sm[s].get(k) for k in ('source_id','url','retrieved_at','publication_at','publication_precision','sha256')} for s in sourceids if s in sm]
        traces.append(dict(cohort=r,outcome=a,features=f,checked_sources=receipts,related_episode_ids=[e['episode_id'] for e in eps if e['player_id']==r['player_id']]))
        text += [f"## {r['player_name']} — index {r['index_game_date']}, extra lag {r['extra_lag_days']} day(s)",'',
            f"Observed index minutes: {r['index_minutes']}. Decision: {r['decision_at']}; future window ends {r['window_end']}. B state: **{r['B_state']}** ({r['B_reason']}). Verified A state: {r['A_state']}.",'',
            f"Source: [{sourceids[0]}]({sm[sourceids[0]]['url']}); all checked reports and query ID are retained in the linked trace JSON. Prospective exclusion assertions: {r['prospective_exclusion_evidence_ids'] or 'none found under the registered search'}.",'']
        if a:text += [f"Public >=10-game outcome: {a['primary_ge10']}; public >28-day span: {a['secondary_public_gt28']}; original medical outcome: {a['original_medical_gt28']}. Retrospective prevalent flags: {a['retrospective_prevalent_episode_ids'] or 'none'}. Historical label_known_at remains unknown.",'']
        if f:text += [f"Assumed features: 7/14/28-day minutes = {f['minutes_7d']} / {f['minutes_14d']} / {f['minutes_28d']}. Input games: {f['input_game_ids']}. Maximum assumed input-availability time: {f['max_input_assumed_available_at']}. These are NBA-only retrospective measurements under B, not verified historical vintages.",'']
    (CROOT/'traced_timelines.json').write_text(json.dumps(traces,indent=2)+'\n')
    (ROOT/'docs/phase1c_timelines.md').write_text('\n'.join(text)+'\n')
    dictionary={}
    for p in sorted((CROOT/'tables').glob('*.csv')):
        with p.open() as f:reader=csv.DictReader(f);data=list(reader)
        dictionary[p.name]=dict(rows=len(data),columns=reader.fieldnames,missing='empty means unknown or not applicable; never a zero substitute')
    (CROOT/'table_dictionary.json').write_text(json.dumps(dictionary,indent=2)+'\n')
    summary=json.loads((CROOT/'summary.json').read_text())
    summary['sensitivity_changed_eligibility']=sum(r['B_eligibility_changed'] for r in comparisons)
    summary['sensitivity_changed_feature_inputs_among_both_included']=sum(r['base_B_state']==r['extra_day_B_state']=='included' and r['base_input_game_ids']!=r['extra_day_input_game_ids'] for r in comparisons)
    summary['remaining_review_candidates']=len(reviewed)
    (CROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Search tool returns may contain long licensed text: only query/link metadata is reviewable.
    # Original receipts are now hashed and stored in the ignored local cache by parser.
    for p in (CROOT/'searches').glob('batch_*.json'):p.unlink()
    print('Rendered sensitivity comparison, six traced cases, review queue, source-quality flags and table dictionary')


if __name__=='__main__':main()
