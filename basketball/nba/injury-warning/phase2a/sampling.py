"""Fixed sample from stable IDs; no injury or fixture information enters selection."""
from pathlib import Path
import json,random,hashlib
from injury_warning.pilot_io import ROOT
D=ROOT/'phase2a';SEED=20240218

def draw(frame):
    ordered=sorted(frame,key=lambda r:int(r['team_id']))
    return sorted(random.Random(SEED).sample(ordered,6),key=lambda r:int(r['team_id']))

def register():
    base=ROOT.parent/'game-prediction/data/raw/2023-24';p=base/'leaguegamelog_full_20260924T020737Z_45ca3b50.manifest.json';m=json.loads(p.read_text());body=(base/m['raw_file']).read_bytes();assert hashlib.sha256(body).hexdigest()==m['sha256']
    rs=json.loads(body)['resultSets'][0];raw=[dict(zip(rs['headers'],r)) for r in rs['rowSet']]
    teams={str(r['TEAM_ID']):dict(team_id=str(r['TEAM_ID']),team=r['TEAM_ABBREVIATION'],name=r['TEAM_NAME']) for r in raw}
    frame=sorted([r for k,r in teams.items() if k!='1610612738'],key=lambda r:int(r['team_id']));assert len(frame)==29
    reg=dict(version='phase2a_fixed_six_v1',seed=SEED,sorting_rule='ascending numeric stable NBA TEAM_ID; selected output also sorted',sampling_implementation='random.Random(20240218).sample(ordered_frame, 6); CPython standard library',sampling_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),frame=frame,selected=draw(frame),game_dates=['2024-01-01','2024-02-18'],history_start='2023-12-04',onset_extension_end='2024-03-03',followup_end='2024-04-14',season='2023-24 regular season only',scope='development-only; Boston separately reported; no models/holdouts',endpoint_registration='phase1d/registration/alternative_v1.json',publication_rules='unchanged Phase1C A/B/C assumptions, operational exclusions and both noon timings',familiarity='Researcher has prior knowledge of historical NBA events and has inspected Boston, Randle/NYK, Ball/CHA, Embiid/PHI, Curry/GSW, Sengun/HOU, and Stevens/MEM and Banton/POR transfer followup. Existing fixture/source familiarity is not blindness. Selection uses IDs and seed only; no redraw.',source_process='Every selected-team regular-season game Dec4-Apr14: public game page with roster/stats/full recap plus final PDF gamebook. Daily 11AM report probes Jan1-Mar3 and game-day late snapshots for baseline submission; dated official NBA/team injury-news searches. Targeted cross-team prior workload and transfer followup. Shared sources reused by source_id; failures retained.',negative_review='All potential positives and unresolved >=10-possible runs; seeded minimum five negative decision rows per team per timing where available; same-agent review never independent',historical_label_known_at='unknown unless original availability independently verified; C ascertainment separate',results_reviewed_before_registration=False)
    p=D/'registration/sample_v1.json';p.write_text(json.dumps(reg,indent=2)+'\n');p.with_suffix('.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'\n');print(json.dumps(reg['selected'],indent=2))
if __name__=='__main__':register()
