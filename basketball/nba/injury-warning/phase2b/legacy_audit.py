"""Rebuild Boston and external integration fixtures in separate output directories."""
import csv,json,shutil
from datetime import datetime
from injury_warning.pilot_io import ROOT
from injury_warning.rules import utc
from phase1c.logic import add_elapsed,features
from phase1d.logic import day_bounds
from .io import D,rows,write

def audit():
    tm={r['game_id']:r for r in rows('all_acquired_game_clock_audit')}
    def load(phase,name):
        with (ROOT/phase/'tables'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
    scope=[]
    for phase,name,field in [('pilot','game_timing','game_end_upper_exclusive'),('phase1d','target_game_evidence','end_upper')]:
        for r in load(phase,name):
            new=tm[r['game_id']]['end_upper'];assert utc(new)==utc(r[field])
            scope.append(dict(scope='Boston' if phase=='pilot' else 'targeted_transfers_and_external_fixtures',game_id=r['game_id'],old_end_upper=r[field],new_end_upper=new,timing_changed=False,source_id='page_'+r['game_id'],book_source_id='book_'+r['game_id'],rule='708-game official-source audit; source timezone and date unchanged'))
    write('legacy_clock_impact',scope)
    # Independently recompute all numeric Boston workload features using audited clocks.
    pg=load('pilot','player_games');old=load('phase1c','features_assumption_B');rebuilt=[]
    for r in old:
        logs=[dict(game_id=g['game_id'],game_date=g['game_date'],minutes=float(g['minutes']),end_upper=tm[g['game_id']]['end_upper'],assumed_available_at=add_elapsed(tm[g['game_id']]['end_upper'],hours=6)) for g in pg if g['player_id']==r['player_id']]
        f=features(logs,r['decision_at'],history_complete=r['history_complete_28d']=='True',baseline_complete=r['history_complete_28d']=='True')
        for k,v in f.items():
            if k not in r:continue
            expected='' if v is None else str(v)
            if isinstance(v,float) and r[k]:assert abs(v-float(r[k]))<1e-7,(r['row_id'],k)
            else:assert expected==r[k],(r['row_id'],k,expected,r[k])
        rebuilt.append(dict(r,clock_audit_recomputed=True))
    write('boston_features_recomputed',rebuilt)
    import phase1d.build as legacy
    out=D/'boston_fixture_rebuild';out.mkdir(exist_ok=True);(out/'tables').mkdir(exist_ok=True)
    for name in ['parsed_reports.json','search_ledger.json','fixture_adjudications.json','adjudication_metadata.json','source_manifest.jsonl']:shutil.copyfile(ROOT/'phase1d'/name,out/name)
    shutil.copytree(ROOT/'phase1d/registration',out/'registration',dirs_exist_ok=True)
    def bounds(gid,day,clinical=False):
        r=tm[gid]
        return r['start_lower'],r['end_upper'] if clinical else r['start_upper'],'audited actual played game interval' if clinical else 'audited first period start minute'
    def output(name,records):
        rr=list(records);fields=list(dict.fromkeys(k for r in rr for k in r)) or ['row_id']
        with (out/'tables'/(name+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr)
    legacy.D=out;legacy.write=output;legacy.game_bounds=bounds;legacy.build()
    for name,key in [('row_outcomes','row_id'),('fixture_rows','fixture_row_id')]:
        with (out/'tables'/(name+'.csv')).open() as f:new={r[key]:r for r in csv.DictReader(f)}
        old=load('phase1d',name)
        for r in old:
            for k,v in r.items():assert new[r[key]][k]==v,(name,r[key],k)
    (D/'legacy_rebuild_summary.json').write_text(json.dumps(dict(clock_records=len(scope),boston_feature_rows_recomputed=len(rebuilt),boston_labels_identical=True,fixture_labels_and_eligibility_identical=True,fixtures_in_cohort_counts=False),indent=2)+'\n')
if __name__=='__main__':audit()
