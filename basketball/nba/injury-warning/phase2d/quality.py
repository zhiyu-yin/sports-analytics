"""Source assertions, immutable historical aliases and final evidence checks."""
import json,csv,hashlib
from collections import Counter
from .runtime import D,ROOT,manifest,verify
from .audit import write,utc
from .names import name_key
from injury_warning.longitudinal import canonical
from phase2a.acquire import read

def load(path):
    with path.open() as f:return list(csv.DictReader(f))
def check():
    verify();sm=manifest();required={'d_brown_surgery':['left wrist','surgery'],'d_sharpe_surgery':['worsening','core muscle'],'d_ball_shutdown':['2024','right ankle'],'d_patrick_surgery':['subsequent imaging','stress reaction'],'d_simmons_surgery':['pinched nerve','2024'],'d_eason_coach':['benign growth','pre-existing'],'d_vanderbilt':['mid-foot sprain','Feb. 1'],'d_wood':['left knee','arthroscopic'],'d_daniels':['meniscectomy','four weeks'],'d_daniels_progress':['Feb. 9','knee'],'d_castleton':['right wrist fracture'],'d_lavine_distinct':['ankle','responding well to treatment']};checks=[]
    for sid,fragments in required.items():
        source=sm[sid];assert source['status']=='obtained';body=read(sid,sm).decode();assert all(f.lower() in body.lower() for f in fragments),sid
        checks.append(dict(source_id=sid,sha256=source['sha256'],url=source['url'],required_assertion_fragments=';'.join(fragments),all_fragments_present=True,role='C only, not predictor/eligibility evidence'))
    write(D/'tables/continuity_source_checks.csv',checks)
    aliases=[]
    for ph in ['phase2b','phase2c']:
        people=load(ROOT/ph/'tables/players.csv');old={canonical(p['family_name']+', '+p['first_name']):p['player_id'] for p in people};new={name_key(p['family_name']+', '+p['first_name']):p['player_id'] for p in people};tm={r['game_id']:r for r in load(ROOT/ph/'tables/game_timing.csv')}
        for rp in json.loads((ROOT/ph/'parsed_reports.json').read_text()):
            for o in rp['observations']:
                if canonical(o['player_name_raw']) in old or name_key(o['player_name_raw']) not in new:continue
                aliases.append(dict(batch=ph,source_id=rp['source_id'],player_id=new[name_key(o['player_name_raw'])],raw_name=o['player_name_raw'],target_game_date=o['target_game_date'],B_available_at=rp['B_available_at'],reason=o['reason'],effect='Existing Phase2C Jemison assignment snapshot: noninjury, target game already completed before availability and before future noon decisions. Does not alter medical history, prospective eligibility, labels or workload; historical expired-status metadata left versioned unchanged.'))
    assert len(aliases)==1 and aliases[0]['raw_name']=='Jemison, Trey' and aliases[0]['reason']=='G League - Two-Way'
    t=next(r for r in load(ROOT/'phase2c/tables/game_timing.csv') if r['game_date']=='2024-02-14' and r['game_id']=='0022300783');assert utc(t['end_upper'])<utc(aliases[0]['B_available_at'])
    write(D/'tables/historical_suffix_alias_audit.csv',aliases)
    # Explicit per-event diagnostic summaries; reason changes never collapse
    # merely because all rows share broad injury/illness category.
    diagnostics=[];contracts=[]
    for i in [1,2,3]:
        p=D/f'batch{i}';evidence=load(p/'tables/event_game_evidence.csv');limits=json.loads((p/'identity_limitations.json').read_text()) if (p/'identity_limitations.json').exists() else {}
        for e in load(p/'tables/events.csv'):
            if e['severity']=='negative' or e['candidate_broad_onset_period']!='True':continue
            gg=[g for g in evidence if g['event_id']==e['event_id']]
            if e['severity']=='positive':
                assert e['continuity_supported']=='True' and int(e['confirmed_same_episode_games'])>=10 and int(e['longest_injury_only_segment'])>=int(e['confirmed_same_episode_games'])
                for sid in e['continuity_source_ids'].split(';'):
                    assert sm[sid.strip()]['status']=='obtained';read(sid.strip(),sm)
            diagnostics.append(dict(batch=i,event_id=e['event_id'],player_id=e['player_id'],player_name=e['player_name'],original_anchor_date=e['anchor_date'],severity=e['severity'],confirmed_same_episode_games=e['confirmed_same_episode_games'],maximal_injury_only_segment=e['longest_injury_only_segment'],individual_reason_counts=json.dumps(dict(Counter(g['reason'] for g in gg)),sort_keys=True),specific_identity_limitation=limits.get(e['player_id']+'_'+e['anchor_date'],''),common_episode_assertion=e.get('continuity_review_note',''),source_ids=e.get('continuity_source_ids','') or e['source_ids'],evidence_table='batch'+str(i)+'/tables/event_game_evidence.csv',independent_human_review=False))
    write(D/'tables/all_new_potential_event_reviews.csv',diagnostics)
    contracts=load(ROOT/'phase2c/tables/contract_only_inventory.csv')
    for r in load(ROOT/'phase2b/tables/roster_inventory.csv'):
        if r['role'].startswith('transaction_only'):contracts.append(dict(team=r['team'],player_id=r['player_id'],player_name=r['player_name'],transaction_date=r['membership_date'],basis=r['role'],source_id=r['source_id'],historical_availability='C'))
    write(D/'tables/contract_only_inventory.csv',contracts)
    summary=dict(continuity_sources_verified=len(checks),potential_new_events_reviewed=len(diagnostics),historical_unmatched_suffix_snapshots=len(aliases),historic_predictor_label_workload_changes=0,independent_human_reviews=0)
    (D/'quality_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':check()
