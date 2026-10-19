"""Source-linked membership repairs and exhaustive impact-prioritized gap ledger."""
import json
from collections import Counter,defaultdict
from .io import D,rows,write
from injury_warning.pilot_io import ROOT

def repair():
    original=json.loads((ROOT/'phase2a/membership_review_ranges.json').read_text());sp=[dict(r) for r in original];changes=[]
    for r in sp:
        if (r['player_id'],r['team']) in [('1628995','UTA'),('1627788','IND')]:
            old=r['end'];sid='p2b_knox_waiver' if r['team']=='UTA' else 'p2b_korkmaz_waiver'
            r.update(end='2024-02-08',date_basis='Official Feb9 waiver timestamp precedes that evening actual team game; last potentially applicable game date Feb8, intraday Feb8 onboarding remains unresolved',source_id=sid+';p2_trade_tracker')
            changes.append(dict(player_id=r['player_id'],team=r['team'],field='end',old_value=old,new_value=r['end'],reason=r['date_basis'],source_id=sid))
    # A 10-day contract is not a continuous January-to-April membership spell.
    # End is conservative last observed game; nominal Jan27 expiry is evidence,
    # not a fabricated assertion about the exact termination timestamp.
    for start,end,basis,sid in [('2024-01-18','2024-01-26','Jan18 10-day signing; Jan26 last observed roster; nominal expiry Jan27, exact termination not independently timestamped','p2b_nance_10day'),('2024-02-19','2024-04-14','Feb19 official two-way signing plus observed roster through season end','p2b_nance_2way')]:
        sp.append(dict(player_id='1631250',team='CLE',start=start,end=end,date_basis=basis,source_id=sid,historical_availability='C; membership not historical B eligibility exclusion'))
    changes.append(dict(player_id='1631250',team='CLE',field='spells',old_value='2024-01-20..2024-04-14 observed span',new_value='2024-01-18..2024-01-26;2024-02-19..2024-04-14',reason='separate short contract and two-way; preserve interval between observed end and re-signing as unverified NBA membership; no zero fill',source_id='p2b_nance_10day;p2b_nance_2way'))
    (D/'membership_review_ranges.json').write_text(json.dumps(sp,indent=2)+'\n');write('membership_repairs',changes)
    import csv
    def baseline(name):
        with (ROOT/'phase2a/tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
    oo=baseline('row_outcomes');ff=baseline('features_B');unknown=Counter(r['player_id'] for r in oo if r['absence_run_onset_ge10']=='unknown');missing=Counter(r['player_id'] for r in ff if r['history_complete']=='False');people={r['player_id']:r['player_name'] for r in rows('players')};ledger=[]
    affected={pid:{r['row_id'] for r in oo if r['player_id']==pid and r['absence_run_onset_ge10']=='unknown'}|{r['row_id'] for r in ff if r['player_id']==pid and r['history_complete']=='False'} for pid in set(unknown)|set(missing)}
    for pid in sorted(set(unknown)|set(missing),key=lambda p:(-len(affected[p]),p)):
        ranges=[r for r in sp if r['player_id']==pid]
        repair_rows=[r for r in changes if r['player_id']==pid]
        ledger.append(dict(player_id=pid,player_name=people[pid],baseline_unknown_rows_both_lags=unknown[pid],baseline_missing_history_rows_both_lags=missing[pid],priority_distinct_rows=len(affected[pid]),reviewed_spells=json.dumps(ranges,sort_keys=True),source_ids=';'.join(sorted({r['source_id'] for r in ranges})),repair_applied=bool(repair_rows),remaining_assertion='Exact contract termination/intraday onboarding and/or complete NBA membership in onset and follow-up still required. Actual schedules enumerated; missing roster never zero/injury. See row_missingness and unresolved_games.',review='Reviewed existing trade sources, observed roster, actual schedules; targeted dated sources for high-impact transitions, waivers and short contracts. Failed House waiver URL retained; no date inferred. Beverley/McDermott Feb8 one-game gaps independently bounded by next appearance.'))
    write('membership_gap_ledger',ledger)
if __name__=='__main__':repair()
