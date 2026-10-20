"""Resumable fixed-batch state; completed review activity, never event-count stopping."""
import json,csv
from collections import Counter
from injury_warning.pilot_io import now
from . import runtime as rt
from .runtime import D,SPEC,bd,rows,write

def checkpoint():
    co=rows('cohort_all_roster_candidates');oo=rows('row_outcomes');ff=rows('features_B');ee=[e for e in rows('events') if e['severity']=='positive' and e['candidate_broad_onset_period']=='True'];ng=rows('negative_original_source_audit');assert len(ng)==len(SPEC['batches'][rt.BATCH-1])*10
    assert all(r['all_original_PID_and_book_name_checks_passed']=='True' for r in ng)
    out=[]
    for lag in ['0','1']:
        cr=[r for r in co if r['extra_lag_days']==lag];rr=[r for r in oo if r['extra_lag_days']==lag];features=[r for r in ff if r['extra_lag_days']==lag];out.append(dict(batch=rt.BATCH,extra_lag_days=lag,games=len({r['index_game_id'] for r in cr}),team_games=len({(r['team'],r['index_game_id']) for r in cr}),players=len({r['player_id'] for r in cr}),candidate_appearances=sum(r['appeared']=='True' for r in cr),included=sum(r['B_state']=='included' for r in cr),excluded=sum(r['B_state']=='excluded' for r in cr),eligibility_unknown=sum(r['B_state']=='unknown' for r in cr),positive=sum(r['absence_run_onset_ge10']=='positive' for r in rr),negative=sum(r['absence_run_onset_ge10']=='negative' for r in rr),outcome_unknown=sum(r['absence_run_onset_ge10']=='unknown' for r in rr),distinct_events=len(ee),event_players=len({e['player_id'] for e in ee}),events_with_eligible_prediction=len({eid for r in rr if r['absence_run_onset_ge10']=='positive' for eid in r['event_ids'].split(';') if eid}),missing_workload=sum(r['history_complete']=='False' for r in features),surveillance_gap=sum(r['onset_surveillance_B']=='False' for r in rr),followup_gap=sum(r['severity_followup_B']=='False' for r in rr),A_verified=0,B_feature_rows=len(features)))
    write('batch_results',out)
    state=dict(batch=rt.BATCH,saved_at=now(),completed_teams=[t['team'] for b in SPEC['batches'][:rt.BATCH] for t in b],pending_teams=[t['team'] for b in SPEC['batches'][rt.BATCH:] for t in b],batch_teams=[t['team'] for t in SPEC['batches'][rt.BATCH-1]],state='completed_same_agent_review_pending_human',negative_original_source_reviews=len(ng),independent_human_reviews=0,request_usage_at_checkpoint=json.loads((D/'actual_usage.json').read_text()),results=out)
    (bd()/'checkpoint.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state))
if __name__=='__main__':checkpoint()
