#!/usr/bin/env python3
"""Render completed results and table dictionary from saved pilot tables, offline."""
import csv,json
from collections import Counter
from injury_warning.pilot_io import ROOT,manifest


def read(name):
    with (ROOT/'pilot/tables'/name).open() as f:return list(csv.DictReader(f))


def render():
    summary=json.loads((ROOT/'pilot/summary.json').read_text());casesummary=json.loads((ROOT/'pilot/case_audit_summary.json').read_text())
    sources=manifest();preds=read('prediction_timestamps.csv');games=read('player_games.csv');cases=read('case_audits.csv')
    timeline=['# Sample player timelines','',
        'Selected dates from the registered pilot. Observed participation and absence reasons are retrospective facts; they do not establish postgame health or original input publication. All primary and next-noon eligibility decisions remain unknown. No future appearance is used to backfill eligibility.','',
        '| Date | Player | Observed game participation | Game roster membership | Next-noon eligibility | Evidence |',
        '| --- | --- | --- | --- | --- | --- |']
    wanted={'Jayson Tatum','Al Horford','Jordan Walsh','JD Davison','Drew Peterson','Xavier Tillman','Lamar Stevens'}
    days={'2024-01-02','2024-01-05','2024-01-08','2024-01-17','2024-02-07','2024-02-09','2024-02-14'}
    indexed={(r['game_id'],r['player_id']):r for r in games}
    for r in preds:
        if r['player_name'] not in wanted or r['game_date'] not in days:continue
        g=indexed.get((r['game_id'],r['player_id']))
        observation=(g['minutes']+' minutes' if g['appeared']=='True' else g['nonappearance_reason'] or 'unresolved nonappearance') if g else 'not in game listing; transaction membership unresolved'
        sid=r['roster_source_id'];url=sources[sid]['url']
        timeline.append(f"| {r['game_date']} | {r['player_name']} | {observation} | {r['roster_membership']} | {r['later_eligibility']} | [{sid}]({url}) |")
    (ROOT/'docs/phase1b_timelines.md').write_text('\n'.join(timeline)+'\n')
    lines=['# Six detailed case audits','',
        'Separate purposive reviews, excluded from the pilot cohort denominator. Reviewer: Codex, the same agent as Phase 1. Independent human reviews: zero. Missing fields and unknown labels have not been forced to completion. Original evidence publication times and full medical clearances remain unverified.','',
        '| Case | Player / stable NBA ID | Onset interval (date precision) | First injury missed game | Return appearance | Primary >28 days | Secondary >=10 games | Appearance-gap proxy |',
        '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in cases:
        lines.append(f"| {r['case_id']} | {r['player_name']} / {r['player_id']} | {r['onset_lower_date'] or 'not applicable'} | {r['first_injury_missed_game'] or 'not applicable'} | {r['first_return_appearance_date'] or 'not established'} | {r['primary_label']} | {r['secondary_label']} ({r['injury_game_run_count'] or 'not applicable'}) | {r['onset_to_return_proxy_days'] or 'not observed/applicable'} |")
    lines+=['','For the five injury cases, the primary outcome is resolved in 2/5 (40%); an onset-to-return appearance gap is observed in 3/5 (60%); the secondary outcome is resolved in 5/5. These are adjudicability proportions in a selected sample, not injury prevalence. A rest exclusion is reported separately.','',
            '## Continuity, evidence and unresolved assertions','']
    assertions=read('case_assertions.csv')
    for r in cases:
        lines += [f"### {r['case_id']}: {r['player_name']}",'',r['continuity_and_identity_evidence'],'',
                  f"Evidence: [assertion-level ledger](../pilot/tables/case_assertions.csv), [game-level evidence](../pilot/tables/case_game_evidence.csv). Stable ID sources: {r['identity_source_ids']}. First-public-report time and historical label_known_at remain unknown. Medical clearance remains unknown. Follow-up: {r['followup_censoring']}.",'']
    lines+=['[Full machine-readable reviews](../pilot/tables/case_audits.csv) · [User review queue for all 25 original records](../pilot/tables/user_review_queue.csv) · [Raw-source retrieval/provenance ledger](../pilot/source_manifest.jsonl) · [Original Phase 1 source register](../audit/sources.json)']
    (ROOT/'docs/phase1b_case_audits.md').write_text('\n'.join(lines)+'\n')
    dictionary={}
    for p in sorted((ROOT/'pilot/tables').glob('*.csv')):
        with p.open() as f:
            reader=csv.DictReader(f);rows=list(reader)
        dictionary[p.name]=dict(rows=len(rows),columns=reader.fieldnames,missing_value='Empty CSV cell means unknown or not applicable; consult reason/precision columns.',provenance='source_id / source_ids joins pilot/source_manifest.jsonl; phase1: IDs join audit/sources.json; local_2023_24_schedule joins pilot/schedule_provenance.json. Derived prediction_id joins prediction_timestamps.csv.')
    (ROOT/'pilot/table_dictionary.json').write_text(json.dumps(dictionary,indent=2)+'\n')
    # Original-publication precision is deliberately distinct from source document time.
    quality=[dict(measure='candidate_immediate_timestamp_missing_exact_end',numerator=len(preds),denominator=len(preds)),dict(measure='candidate_original_input_publication_unverified',numerator=len(preds),denominator=len(preds)),dict(measure='primary_label_unknown',numerator=len(preds),denominator=len(preds)),dict(measure='secondary_label_unknown',numerator=len(preds),denominator=len(preds)),dict(measure='candidate_roster_membership_uncertain',numerator=sum(r['roster_membership'].startswith('uncertain') for r in preds),denominator=len(preds)),dict(measure='mapped_status_player_ids',numerator=summary['status_observations']-summary['unmapped_observations'],denominator=summary['status_observations'])]
    with (ROOT/'pilot/tables/missingness.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['measure','numerator','denominator']);w.writeheader();w.writerows(quality)
    print('Rendered timelines, six-case review, missingness and machine table dictionary')


if __name__=='__main__':render()
