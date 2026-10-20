"""Read-only cumulative audit of versioned inputs; no historical enrichment."""
import csv,json,hashlib
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
from injury_warning.pilot_io import ROOT
from phase2c.pipeline import manifest,read
D=ROOT/'phase2d';A=D/'stage1'
def rows(phase,name):
    with (ROOT/phase/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def write(path,rr):
    rr=list(rr);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rr for k in r)) or ['id']);w.writeheader();w.writerows(rr)
def utc(t):return datetime.fromisoformat(t).timestamp()
def lead_bin(lo,hi):
    for l,h,n in [(0,3,'>0-3d'),(3,7,'>3-7d'),(7,14,'>7-14d')]:
        if lo>l and hi<=h:return n
    return 'boundary_uncertain'
def group(r):
    # Mutually exclusive B hierarchy; A verification unresolved is retained as
    # an overlapping flag rather than swallowing every assumed-B observation.
    if r.get('group_B')=='knowledge_timing_unresolved':return 'unresolved_timing'
    if r.get('acute_known_B')=='True':return 'same_acute_event_disclosed'
    if r.get('recent_known_symptoms_28d_B')=='True':return 'recent_symptoms_or_injury_evidence'
    if r.get('ever_known_injury_history_B')=='True':return 'prior_acquired_history_without_recent_evidence'
    return 'no_signal_found_under_bounded_search'
def audit():
    sm=manifest();inventory=[];opps=[];identity=[];allrecords=[];hashes={}
    for phase in ['phase2b','phase2c']:
        ee=rows(phase,'events');gg=rows(phase,'event_game_evidence');pg=rows(phase,'player_games');oo=rows(phase,'row_outcomes');co={r['row_id']:r for r in rows(phase,'cohort_all_roster_candidates')}
        for n in ['events','event_game_evidence','row_outcomes','cohort_all_roster_candidates','features_B']:
            p=ROOT/phase/'tables'/(n+'.csv');hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        for e in ee:allrecords.append((phase,e,{g['game_id'] for g in gg if g['event_id']==e['event_id']}))
        for e in ee:
            if e['severity']!='positive' or e['candidate_broad_onset_period']!='True':continue
            games=[g for g in gg if g['event_id']==e['event_id']];pids={g['player_id'] for g in games};assert pids=={e['player_id']}
            count=int(e['confirmed_same_episode_games']);assert count>=10 and e['continuity_supported']=='True'
            longest=streak=0
            for g in games:
                assert g['appeared']=='False'
                streak=streak+1 if g['category']=='injury' and g['coverage']=='page_and_book' and g['roster_observed']=='True' else 0;longest=max(longest,streak)
            assert longest>=count,(e['event_id'],count,longest)
            for sid in e['continuity_source_ids'].split(';'):
                sid=sid.strip();assert sid in sm and sm[sid]['status']=='obtained',sid
                read(sid,sm)
            pp=[o for o in oo if o['absence_run_onset_ge10']=='positive' and e['event_id'] in o['event_ids'].split(';')]
            for o in pp:
                assert co[o['row_id']]['B_state']=='included'
                lo=(utc(e['run_lower'])-utc(o['decision_at']))/86400;hi=(utc(e['run_upper'])-utc(o['decision_at']))/86400
                assert lo>0 and hi<=14
                opps.append(dict(batch=phase,canonical_event_id=e['player_id']+'_'+e['anchor_game_id'],event_id=e['event_id'],player_id=e['player_id'],player_name=e['player_name'],row_id=o['row_id'],extra_lag_days=o['extra_lag_days'],decision_at=o['decision_at'],onset_lower=e['run_lower'],onset_upper=e['run_upper'],lead_days_lower=lo,lead_days_upper=hi,opportunity_bin=lead_bin(lo,hi),knowledge_group_B=group(o),same_acute_event_disclosed_B=o['acute_known_B'],recent_evidence_28d_B=o['recent_known_symptoms_28d_B'],prior_acquired_history_B=o['ever_known_injury_history_B'],source_signal_ids_B=o['signal_ids'],A_original_timing_unresolved=o['A_verified']!='True',interpretation='available prediction opportunity, not a successful warning; C linkage descriptive only'))
            inv=dict(canonical_event_id=e['player_id']+'_'+e['anchor_game_id'],event_id=e['event_id'],player_id=e['player_id'],player_name=e['player_name'],batch=phase,applicable_teams=';'.join(sorted({g['team'] for g in games})),anchor_game_id=e['anchor_game_id'],anchor_lower=e['run_lower'],anchor_upper=e['run_upper'],anchor_precision='audited actual first-period start minute interval; absence-run anchor, not clinical onset',confirmed_consecutive_injury_games=count,observed_maximal_medical_segment=longest,common_episode_assertion=e['continuity_review_note'],source_ids=e['continuity_source_ids'],source_urls=';'.join(sm[s.strip()]['url'] for s in e['continuity_source_ids'].split(';')),locators=e['continuity_locator'],limitations='B historical publication assumed, A unresolved; no independent human adjudication; '+e['censoring']+'; '+('Original clinical trauma context disagreement retained. ' if e['player_id'] in {'1629630','203957'} else '')+('Later noninjury entries do not add injury games. ' if e['player_id'] in {'1631321','1631124'} else ''))
            for lag in ['0','1']:
                p=[o for o in pp if o['extra_lag_days']==lag];inv['eligible_decisions_lag'+lag]=len(p);inv['earliest_decision_lag'+lag]=min((o['decision_at'] for o in p),default='');inv['knowledge_groups_lag'+lag]=';'.join(sorted({group(o) for o in p}))
            inventory.append(inv)
    # Inspect same-player records by actual game overlap, not just IDs. The
    # distinct Rose episodes must be separated by an observed NBA appearance.
    for i,(ph,e,ga) in enumerate(allrecords):
        for ph2,f,gb in allrecords[i+1:]:
            if e['player_id']!=f['player_id']:continue
            overlap=ga&gb
            if ph!=ph2 and (overlap or e['anchor_game_id']==f['anchor_game_id']):
                identity.append(dict(player_id=e['player_id'],record1=e['event_id'],record2=f['event_id'],batch1=ph,batch2=ph2,shared_games=len(overlap),same_episode=True,basis='Actual same-player overlapping nonappearance game evidence; common anchor and actual-team chronology inspected',severity1=e['severity'],severity2=f['severity']))
    rose=[e for e in inventory if e['player_id']=='201565'];assert len(rose)==2
    appearances=[r for r in rows('phase2c','player_games') if r['player_id']=='201565' and r['appeared']=='True' and '2024-02-02'<=r['game_date']<'2024-03-01'];assert appearances
    identity.append(dict(player_id='201565',record1=rose[0]['event_id'],record2=rose[1]['event_id'],batch1='phase2c',batch2='phase2c',shared_games=0,same_episode=False,basis='Distinct hamstring and later back run separated by '+str(len(appearances))+' actual NBA appearances; diagnosis alone not used',severity1='positive',severity2='positive'))
    assert len(inventory)==19 and len({e['canonical_event_id'] for e in inventory})==19
    assert sum(e['eligible_decisions_lag0']>0 for e in inventory)==17
    assert sum(e['eligible_decisions_lag1']>0 for e in inventory)==16
    scope=rows('phase2c','scope_results');main=next(r for r in scope if r['scope']=='combined_development' and r['extra_lag_days']=='0');assert [int(main[k]) for k in ['included','positive','negative','outcome_unknown']]==[3067,57,2817,193]
    assert Counter(o['extra_lag_days'] for o in opps)=={'0':57,'1':52}
    write(A/'event_inventory.csv',inventory);write(A/'available_opportunities.csv',opps);write(A/'cross_batch_identity_review.csv',identity);write(A/'count_reconciliation.csv',scope)
    summary=[]
    for lag in ['0','1']:
        oo=[o for o in opps if o['extra_lag_days']==lag]
        for dimension in ['opportunity_bin','knowledge_group_B']:
            for k,n in sorted(Counter(o[dimension] for o in oo).items()):summary.append(dict(extra_lag_days=lag,dimension=dimension,value=k,rows=n,distinct_events=len({o['canonical_event_id'] for o in oo if o[dimension]==k}),event_counts_overlap_when_decisions_differ=True))
    write(A/'lead_and_knowledge_summary.csv',summary)
    (A/'input_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    result=dict(events=19,event_players=18,events_with_main_opportunities=17,events_with_extra_day_opportunities=16,positive_main_rows=57,positive_extra_day_rows=52,counts_reconciled=True,historical_outputs_modified=False,material_unresolved_defect=False,independent_human_adjudication=False)
    (A/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (A/'audit_report.md').write_text('''# Phase 2D Stage 1 cumulative audit

The versioned 19 events (18 players),17 with main-noon and16 with extra-day eligible opportunities reconcile. Included main decisions reconcile to3067 =57 positive +2817 negative +193 unknown. No historical labels or sources were enriched. Event inventory includes confirmed actual injury-game streaks, original anchor precision, C common-episode assertions, direct links and exact locators. Same-player cross-batch overlap was inspected using actual game sets; duplicate transfer-followup records are not additional events. The two Rose episodes are separated by actual appearances. Existing canonical union is retained.

`available_opportunities.csv` records all57/52 eligible positive decisions with lower/upper elapsed lead days. Bins require the complete timestamp interval within >0–3,>3–7,>7–14 days, otherwise boundary-uncertain. These are available prediction opportunities, not successful warnings or model detection. Each event's earliest decision and counts are in `event_inventory.csv`.

Mutually exclusive B hierarchy: unresolved B timing, same-event acute disclosure, recent acquired injury/symptom evidence within28 days, older acquired injury history only, no signal under bounded search. Recent evidence includes injury reports and recap symptoms/history, not proven biological symptom onset. Overlapping source flags remain available. All original-publication A timings remain unresolved and are reported separately rather than swallowing the entire assumption-B summary. Event counts by group overlap when different decisions for the same event fall in different groups. Retrospective C linkage is descriptive only, never prospective eligibility/features. Absence of a searched signal does not establish health.

Common-episode support and all individual medical streaks meet frozen rules; source-context differences (Morant game versus training trauma, Exum return wording), short contracts, censoring and A/B assumptions remain explicit limitations. No material unresolved defect preventing Stage2 acquisition/labeling was identified. No independent human adjudication occurred, and no model or holdout was opened. Proceed to fixed registration before new remaining-team outcome review.
''')
    print(json.dumps(result));print(json.dumps(summary))
if __name__=='__main__':audit()
